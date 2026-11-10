"""Independent reference computations written from the formulas in tier1_spec.md.

Nothing here imports the modules under test.
"""
import numpy as np

G = 9.81  # spec 2.3 (literal on purpose; not taken from imu_sim)


def true_pitch_and_rate(t):
    """Spec 4.3 default trajectory."""
    w1 = 2 * np.pi * 0.1
    w2 = 2 * np.pi * 0.5
    pitch = 0.5 * np.sin(w1 * t) + 0.2 * np.sin(w2 * t)
    rate = 0.5 * w1 * np.cos(w1 * t) + 0.2 * w2 * np.cos(w2 * t)
    return pitch, rate


def ref_accel_tilt(f):
    """Spec 2.4 tilt formulas."""
    f = np.asarray(f, dtype=float)
    roll = np.arctan2(f[:, 1], f[:, 2])
    pitch = np.arctan2(-f[:, 0], np.sqrt(f[:, 1] ** 2 + f[:, 2] ** 2))
    return roll, pitch


def ref_gyro_integrate(t, rate, initial_angle=0.0):
    """Spec 5.2 recurrence (backward rectangle, current sample)."""
    out = np.empty(len(t))
    out[0] = initial_angle
    for k in range(1, len(t)):
        out[k] = out[k - 1] + rate[k] * (t[k] - t[k - 1])
    return out


def ref_complementary(t, rate, accel_angle, tau=0.2, initial_angle=None):
    """Spec 5.3 recurrence."""
    out = np.empty(len(t))
    out[0] = accel_angle[0] if initial_angle is None else initial_angle
    for k in range(1, len(t)):
        dt = t[k] - t[k - 1]
        alpha = tau / (tau + dt)
        out[k] = alpha * (out[k - 1] + rate[k] * dt) + (1 - alpha) * accel_angle[k]
    return out
