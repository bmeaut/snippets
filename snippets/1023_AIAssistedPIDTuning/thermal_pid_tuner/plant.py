"""
plant.py
--------
Thermal plant model as a first-order-plus-dead-time (FOPDT) transfer function.

Transfer function (deviation form):
            K * e^(-theta * s)
  G(s) = ─────────────────────
                tau * s + 1

Dead time is approximated with a 2nd-order Padé expansion.
Absolute temperature:  T(t) = T_amb + G(s) * u(t)
"""

import numpy as np
import control


class ThermalPlant:
    """
    First-order thermal plant with dead time.

    Parameters
    ----------
    K     : float  Steady-state gain  [°C / % heater power]
    tau   : float  Time constant       [s]
    theta : float  Dead time           [s]
    T_amb : float  Ambient temperature [°C]
    """

    def __init__(self, K: float = 1.5, tau: float = 200.0,
                 theta: float = 20.0, T_amb: float = 20.0) -> None:
        self.K = K
        self.tau = tau
        self.theta = theta
        self.T_amb = T_amb

    # ------------------------------------------------------------------
    def transfer_function(self) -> control.TransferFunction:
        """
        Build and return the full transfer function G(s), with the dead
        time represented by a 2nd-order Padé approximation.

        Returns
        -------
        control.TransferFunction
        """
        # --- First-order lag:  K / (tau*s + 1) ---
        lag = control.TransferFunction([self.K], [self.tau, 1.0])

        # --- 2nd-order Padé approximation for e^(-theta*s) ---
        num_pade, den_pade = control.pade(self.theta, n=2)
        pade_tf = control.TransferFunction(num_pade, den_pade)

        # --- Series combination: G(s) = lag * pade ---
        G = control.series(lag, pade_tf)
        return G

    # ------------------------------------------------------------------
    def step_response(self, u_step: float = 100.0,
                      t_end: float = 800.0,
                      dt: float = 0.5):
        """
        Simulate the open-loop step response: heater jumps from 0 to
        *u_step* at t = 0.

        Parameters
        ----------
        u_step : float  Heater power step size  [%]  (clamped to [0, 100])
        t_end  : float  Simulation end time      [s]
        dt     : float  Time step                [s]

        Returns
        -------
        t : np.ndarray  Time vector  [s]
        T : np.ndarray  Absolute temperature  [°C]
        """
        # Clamp heater command
        u_step = float(np.clip(u_step, 0.0, 100.0))

        # Build time vector
        t = np.arange(0.0, t_end + dt, dt)

        # Step input signal (deviation from 0 %)
        u = np.full_like(t, u_step)

        # Get transfer function
        G = self.transfer_function()

        # Simulate forced response
        t_out, y_out = control.forced_response(G, T=t, U=u)

        # Convert to absolute temperature; keep only real part (Padé is real)
        T = self.T_amb + np.real(y_out)

        return t_out, T
