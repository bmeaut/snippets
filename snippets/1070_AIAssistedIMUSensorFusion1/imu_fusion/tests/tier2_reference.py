"""Independent reference computations written from tier2_spec.md (section 5).

Nothing here imports the modules under test.
"""
import numpy as np


def ref_noise_matrices(dt, gyro_noise_std, accel_noise_std, bias_rw_std, gravity=9.81):
    """Spec 5.1."""
    Q = np.array([[gyro_noise_std ** 2 * dt ** 2, 0.0], [0.0, bias_rw_std ** 2 * dt]])
    R = (accel_noise_std / gravity) ** 2
    return Q, R


def ref_kalman_pitch(t, gyro_rate, accel_angle, gyro_noise_std=0.005, accel_noise_std=0.05,
                     bias_rw_std=1e-4, gravity=9.81, initial_angle=None, initial_bias=0.0,
                     initial_cov=None):
    """Spec 5.3, transcribed line by line with explicit 2x2 matrix algebra."""
    n = len(t)
    R = (accel_noise_std / gravity) ** 2
    angle = np.empty(n)
    bias = np.empty(n)
    cov = np.empty((n, 2, 2))
    angle[0] = accel_angle[0] if initial_angle is None else initial_angle
    bias[0] = initial_bias
    cov[0] = np.diag([R, 0.02 ** 2]) if initial_cov is None else np.asarray(initial_cov, dtype=float)
    for k in range(1, n):
        dt = t[k] - t[k - 1]
        w_bar = 0.5 * (gyro_rate[k - 1] + gyro_rate[k])
        Q = ref_noise_matrices(dt, gyro_noise_std, accel_noise_std, bias_rw_std, gravity)[0]
        F = np.array([[1.0, -dt], [0.0, 1.0]])
        x_prior = np.array([angle[k - 1] + (w_bar - bias[k - 1]) * dt, bias[k - 1]])
        P = F @ cov[k - 1] @ F.T + Q
        S = P[0, 0] + R
        K = P[:, 0] / S
        y = accel_angle[k] - x_prior[0]
        x = x_prior + K * y
        angle[k], bias[k] = x
        cov[k] = P - S * np.outer(K, K)
    return angle, bias, cov
