# Phase 3.5: Cohen‑Coon Auto‑Tuning & Comparison with Ziegler‑Nichols

## Objective
Implement a second automatic tuning method — Cohen‑Coon — directly from the plant’s FOPDT parameters, then compare the closed‑loop performance of Ziegler‑Nichols and Cohen‑Coon on the same plot, with a printed metric comparison table.

---

## 1. Extend `tuner.py` with Cohen‑Coon

Add a new public function to the existing `tuner.py` module:

    def cohen_coon_tune(plant):
        ...

### 1.1 Plant Parameter Access
Our `ThermalPlant` stores `K`, `tau`, `theta`. These should be accessed via the plant instance, e.g. `plant.K`, `plant.tau`, `plant.theta`. If these aren't already instance attributes, add them to `plant.py` by setting them in `__init__`:

    self.K = K
    self.tau = tau
    self.theta = theta

(This is a minimal, non‑breaking change — the plant should still work exactly as before.)

### 1.2 Cohen‑Coon PID Formulas (Ideal Form)
Given `Kp_plant = plant.K`, `tau = plant.tau`, `theta = plant.theta`:

    r = theta / tau

    Kc = (1.0 / Kp_plant) * (1.35 * (tau / theta) + 0.27)
    tauI = tau * ( (32.0 + 6.0 * r) / (13.0 + 8.0 * r) )
    tauD = tau * ( 4.0 / (11.0 + 2.0 * r) )

Then for an ideal PID: `Gc(s) = Kc (1 + 1/(tauI s) + tauD s)`, which is equivalent to:

    Kp = Kc
    Ki = Kc / tauI
    Kd = Kc * tauD

### 1.3 Return Value
Return a dictionary containing `Kp`, `Ki`, `Kd` (floats), along with the intermediate values `Kc`, `tauI`, `tauD` for diagnostic prints.

    return {
        'Kp': Kp,
        'Ki': Ki,
        'Kd': Kd,
        'Kc': Kc,
        'tauI': tauI,
        'tauD': tauD
    }

### 1.4 Edge Cases
If `theta` is zero or very small (not our case), return sensible defaults to avoid division by zero. For our plant (θ=20), this is fine.

---

## 2. Comparison Script: `compare_tuning.py`

Create a new script `compare_tuning.py` that runs both tuners and compares their closed‑loop responses.

### 2.1 Imports

    import numpy as np
    import matplotlib.pyplot as plt
    import control
    from plant import ThermalPlant
    from controller import PIDController
    from tuner import ziegler_nichols_tune, cohen_coon_tune
    from utils import overshoot, rise_time, settling_time

### 2.2 Parameters

    SETPOINT = 60.0
    T_AMBIENT = 20.0
    T_SIM = 800.0

### 2.3 Tune with Both Methods

    plant = ThermalPlant()
    zn = ziegler_nichols_tune(plant)
    cc = cohen_coon_tune(plant)

Print the gains for both:

    print("Ziegler-Nichols PID: Kp=..., Ki=..., Kd=...")
    print("Cohen-Coon PID:     Kp=..., Ki=..., Kd=...")

### 2.4 Build Closed‑Loop Systems and Simulate
Write a small helper function to avoid code duplication:

    def simulate_closed_loop(Kp, Ki, Kd):
        pid = PIDController(Kp, Ki, Kd)
        Gp = plant.transfer_function()
        Gc = pid.transfer_function()
        G_ol = Gc * Gp
        G_cl = control.feedback(G_ol, 1, sign=-1)
        t, y_dev = control.step_response(G_cl, T=T_SIM)
        T_abs = T_AMBIENT + (SETPOINT - T_AMBIENT) * y_dev
        return t, T_abs

Then:

    t_zn, T_zn = simulate_closed_loop(zn['Kp'], zn['Ki'], zn['Kd'])
    t_cc, T_cc = simulate_closed_loop(cc['Kp'], cc['Ki'], cc['Kd'])

### 2.5 Plot Both Responses

- Figure size (10, 6).
- Plot `t_zn`, `T_zn` with label "Ziegler‑Nichols".
- Plot `t_cc`, `T_cc` with label "Cohen‑Coon".
- Add dashed horizontal line at 60 °C, label "Setpoint".
- Grid, axis labels, title "ZN vs Cohen‑Coon Tuning Comparison".
- Legend.
- Save to `plots/tuning_comparison.png`.

### 2.6 Compute and Print Metrics Table

For each method, compute overshoot, rise time, and settling time. Print a formatted table:

    Metric          Ziegler‑Nichols    Cohen‑Coon
    --------------------------------------------------
    Overshoot (%)   X.XX              Y.YY
    Rise time (s)   X.XX              Y.YY
    Settling time (s) X.XX            Y.YY

All numbers formatted to two decimal places.

### 2.7 Run
The script must be executable with `python compare_tuning.py`.

---

## 3. Acceptance Criteria

- `python compare_tuning.py` runs without errors.
- The terminal output clearly shows both sets of gains and the metrics comparison table.
- The plot displays two distinct response curves (different rise times and overshoots).
- Cohen‑Coon typically yields lower overshoot than ZN for this plant (though both are acceptable).
- All rise times and settling times ≤ 800 s.
- Plot saved to `plots/tuning_comparison.png`.
- Existing `python auto_tune.py` still works after the `tuner.py` extension.