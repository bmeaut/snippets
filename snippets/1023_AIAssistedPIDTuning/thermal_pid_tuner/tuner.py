"""
tuner.py
--------
Automatic PID tuning methods.

Functions
---------
ziegler_nichols_tune(plant)
    Ziegler-Nichols ultimate gain method -- uses the plant's frequency
    response (gain margin / phase-crossover frequency) to derive Ku and Tu,
    then applies the classic ZN rules.

cohen_coon_tune(plant)
    Cohen-Coon method -- uses the plant's FOPDT parameters (K, tau, theta)
    directly to compute PID gains. Includes an automatic robustness check:
    if the Pade-approximated closed loop is unstable (a known artifact of
    pure-derivative terms interacting with Pade RHP zeros), the gains are
    scaled down iteratively until the closed loop is stable with adequate
    gain margin.
"""

import numpy as np
import control


# ======================================================================
# Ziegler-Nichols Ultimate Gain Method
# ======================================================================

def ziegler_nichols_tune(plant) -> dict:
    """
    Compute Ziegler-Nichols PID gains for *plant*.

    Parameters
    ----------
    plant : ThermalPlant
        An instance of ThermalPlant (or any object with a
        ``transfer_function()`` method returning a SISO LTI system).

    Returns
    -------
    dict with keys:
        Ku  - ultimate (critical) gain          [float]
        Tu  - ultimate period                   [float, seconds]
        Kp  - proportional gain                 [float]
        Ki  - integral gain                     [float]
        Kd  - derivative gain                   [float]
    """
    # ------------------------------------------------------------------
    # 1. Obtain plant transfer function and compute stability margins
    # ------------------------------------------------------------------
    Gp = plant.transfer_function()

    # control.margin returns (gm, pm, w_p, w_g)
    #   gm  - gain margin (linear, not dB)
    #   pm  - phase margin (degrees)
    #   w_p - phase-crossover frequency, where angle(G) = -180  [rad/s]
    #   w_g - gain-crossover frequency, where |G| = 1           [rad/s]
    gm, pm, w_p, w_g = control.margin(Gp)

    # ------------------------------------------------------------------
    # 2. Guard: infinite or NaN gain margin -> fallback defaults
    # ------------------------------------------------------------------
    if gm is None or not np.isfinite(gm) or np.isnan(gm):
        print("Gain margin infinite; using default Ku=5, Tu=200 for tuning.")
        Ku = 5.0
        Tu = 200.0
    else:
        Ku = float(gm)
        Tu = float(2.0 * np.pi / w_p)

    # ------------------------------------------------------------------
    # 3. Ziegler-Nichols PID rules
    # ------------------------------------------------------------------
    Kp = 0.6  * Ku
    Ki = 2.0  * Kp / Tu
    Kd = Kp   * Tu / 8.0

    return {
        "Ku": Ku,
        "Tu": Tu,
        "Kp": float(Kp),
        "Ki": float(Ki),
        "Kd": float(Kd),
    }


# ======================================================================
# Cohen-Coon Method
# ======================================================================

def cohen_coon_tune(plant) -> dict:
    """
    Compute Cohen-Coon PID gains for *plant* using its FOPDT parameters.

    The Cohen-Coon method works directly from the plant's steady-state
    gain (K), time constant (tau), and dead time (theta), making it
    independent of frequency-response calculations. It typically produces
    lower overshoot than Ziegler-Nichols for FOPDT processes.

    Formulas (ideal PID form)
    -------------------------
        r    = theta / tau
        Kc   = (1/K) * (1.35 * (tau/theta) + 0.27)
        tauI = tau * (32 + 6r) / (13 + 8r)
        tauD = tau * 4 / (11 + 2r)

    Converting to standard gains:
        Kp = Kc
        Ki = Kc / tauI
        Kd = Kc * tauD

    Robustness note
    ---------------
    When the plant dead time is approximated by a Pade expansion (as in
    this project), the resulting RHP zeros can interact with a large Kd
    and destabilise the closed loop -- even though the Cohen-Coon formulas
    are mathematically correct for the true FOPDT plant.  This function
    therefore performs a closed-loop stability check after computing the
    raw gains and, if necessary, scales all three gains down by a common
    factor f until the system is stable with an adequate gain margin.
    The scaling preserves the ratio Kp:Ki:Kd (i.e. tauI and tauD are
    unchanged), so the closed-loop character remains Cohen-Coon in nature.

    Parameters
    ----------
    plant : ThermalPlant
        Must expose ``plant.K``, ``plant.tau``, and ``plant.theta``.

    Returns
    -------
    dict with keys:
        Kp        - proportional gain        [float]
        Ki        - integral gain            [float]
        Kd        - derivative gain          [float]
        Kc        - raw Cohen-Coon controller gain (before any detuning)
        tauI      - integral time constant   [float, seconds]
        tauD      - derivative time constant [float, seconds]
        detune_f  - detuning factor applied  [float]  (1.0 = no detuning)
    """
    from controller import PIDController

    K_plant = float(plant.K)
    tau     = float(plant.tau)
    theta   = float(plant.theta)

    # ------------------------------------------------------------------
    # Edge-case guard: avoid division by zero if theta is negligibly small
    # ------------------------------------------------------------------
    if theta < 1e-9:
        print("Warning: dead time theta ~= 0; Cohen-Coon requires theta > 0. "
              "Returning conservative defaults.")
        return {"Kp": 1.0, "Ki": 0.01, "Kd": 0.0,
                "Kc": 1.0, "tauI": 100.0, "tauD": 0.0, "detune_f": 1.0}

    # ------------------------------------------------------------------
    # Cohen-Coon PID formulas (ideal form)
    # ------------------------------------------------------------------
    r    = theta / tau

    Kc   = (1.0 / K_plant) * (1.35 * (tau / theta) + 0.27)
    tauI = tau * (32.0 + 6.0 * r) / (13.0 + 8.0 * r)
    tauD = tau * 4.0 / (11.0 + 2.0 * r)

    Kp_raw = float(Kc)
    Ki_raw = float(Kc / tauI)
    Kd_raw = float(Kc * tauD)

    # ------------------------------------------------------------------
    # Robustness check: verify closed-loop stability with Pade plant.
    # If unstable, binary-search for the largest detuning factor f in
    # (0, 1] that yields a stable closed loop, then apply a 15 % safety
    # margin (f_use = f_boundary * 0.85).
    # ------------------------------------------------------------------
    Gp = plant.transfer_function()

    def _is_stable(f: float) -> bool:
        pid = PIDController(Kp_raw * f, Ki_raw * f, Kd_raw * f)
        Gc  = pid.transfer_function()
        G_cl = control.feedback(control.series(Gc, Gp), 1, sign=-1)
        poles = control.poles(G_cl)
        return all(p.real <= 0 for p in poles)

    if _is_stable(1.0):
        # Raw CC gains are stable -- use them directly
        detune_f = 1.0
    else:
        # Binary search for stability boundary
        print("Cohen-Coon: raw gains unstable with Pade plant model; "
              "applying automatic detuning to restore stability.")
        lo_f, hi_f = 0.0, 1.0
        for _ in range(60):           # 60 iterations -> precision ~1e-18
            mid = (lo_f + hi_f) / 2.0
            if _is_stable(mid):
                lo_f = mid
            else:
                hi_f = mid
        # Apply 15 % safety margin below the stability boundary
        detune_f = lo_f * 0.85

    Kp = Kp_raw * detune_f
    Ki = Ki_raw * detune_f
    Kd = Kd_raw * detune_f

    return {
        "Kp":      float(Kp),
        "Ki":      float(Ki),
        "Kd":      float(Kd),
        "Kc":      float(Kc),
        "tauI":    float(tauI),
        "tauD":    float(tauD),
        "detune_f": float(detune_f),
    }
