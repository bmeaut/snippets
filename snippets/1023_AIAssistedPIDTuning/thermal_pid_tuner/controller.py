"""
controller.py
-------------
Ideal PID controller as a Laplace-domain transfer function.

          Ki
Gc(s) = Kp + ── + Kd·s   =   (Kd·s² + Kp·s + Ki) / s
          s

No derivative filter and no anti-windup — pure ideal PID.
"""

import control


class PIDController:
    """
    Ideal PID controller.

    Parameters
    ----------
    Kp : float  Proportional gain  (default 1.0)
    Ki : float  Integral gain      (default 0.0)
    Kd : float  Derivative gain    (default 0.0)
    """

    def __init__(self, Kp: float = 1.0, Ki: float = 0.0, Kd: float = 0.0) -> None:
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

    def transfer_function(self) -> control.TransferFunction:
        """
        Return the ideal PID transfer function:

            Gc(s) = (Kd·s² + Kp·s + Ki) / s

        Returns
        -------
        control.TransferFunction
        """
        numerator   = [self.Kd, self.Kp, self.Ki]   # Kd·s² + Kp·s + Ki
        denominator = [1.0, 0.0]                      # s
        return control.TransferFunction(numerator, denominator)
