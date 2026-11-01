"""Independent reference computations written from tier3_spec.md.

Nothing here imports the modules under test. Python 3.9-valid syntax.
"""
import math

import numpy as np

G = 9.81  # T1 spec 2.3 (literal on purpose)


# ------------------------------------------------------------------ kinematics (spec 2.2)
def euler_rates(phi, theta, w):
    """E(phi, theta; w) -> (phi_dot, theta_dot) for scalars."""
    r = w[0] + math.tan(theta) * (math.sin(phi) * w[1] + math.cos(phi) * w[2])
    p = math.cos(phi) * w[1] - math.sin(phi) * w[2]
    return r, p


def rotation_body_to_world(phi, theta):
    cp, sp, ct, st = math.cos(phi), math.sin(phi), math.cos(theta), math.sin(theta)
    return np.array([[ct, st * sp, st * cp],
                     [0.0, cp, -sp],
                     [-st, ct * sp, ct * cp]])


def gravity_term(roll, pitch):
    """GRAVITY * (-sin(theta), sin(phi)cos(theta), cos(phi)cos(theta)), vectorized -> (N, 3)."""
    return G * np.column_stack([-np.sin(pitch), np.sin(roll) * np.cos(pitch),
                                np.cos(roll) * np.cos(pitch)])


def body_rates(roll, roll_rate, pitch_rate):
    """(phi_dot, cos(phi) theta_dot, -sin(phi) theta_dot) -> (N, 3)."""
    return np.column_stack([roll_rate, np.cos(roll) * pitch_rate, -np.sin(roll) * pitch_rate])


# ------------------------------------------------------------------ trajectory (spec 5.1)
def ref_default_trajectory(t):
    t = np.asarray(t, dtype=float)
    tau = t - 5.0
    a1, b1 = 2 * np.pi * 0.05, 2 * np.pi * 0.17
    a2, b2 = 2 * np.pi * 0.04, 2 * np.pi * 0.23
    on = t >= 5.0
    roll = 0.6 * np.sin(a1 * tau) * np.sin(b1 * tau)
    roll_rate = 0.6 * (a1 * np.cos(a1 * tau) * np.sin(b1 * tau) + b1 * np.sin(a1 * tau) * np.cos(b1 * tau))
    pitch = 0.7 * np.sin(a2 * tau) * np.sin(b2 * tau)
    pitch_rate = 0.7 * (a2 * np.cos(a2 * tau) * np.sin(b2 * tau) + b2 * np.sin(a2 * tau) * np.cos(b2 * tau))
    z = np.zeros_like(t)
    return (np.where(on, roll, z), np.where(on, pitch, z),
            np.where(on, roll_rate, z), np.where(on, pitch_rate, z))


# ------------------------------------------------------------------ disturbances (spec 5.2, 5.4)
def ref_linear_accel_body(t, roll, pitch, segments):
    """R^T * sum(a_w) using the explicit matrix R of spec 2.2, per sample -> (N, 3)."""
    out = np.zeros((len(t), 3))
    for (t0, dur, peak, az) in segments:
        for k in range(len(t)):
            if t0 <= t[k] <= t0 + dur:
                mag = peak * math.sin(math.pi * (t[k] - t0) / dur)
                a_w = np.array([mag * math.cos(az), mag * math.sin(az), 0.0])
                out[k] += rotation_body_to_world(roll[k], pitch[k]).T @ a_w
    return out


def ref_linear_accel_closed_form(t, roll, pitch, segments):
    """The closed form written out in spec 5.4: (c_th ax, s_th s_ph ax + c_ph ay, s_th c_ph ax - s_ph ay)."""
    t = np.asarray(t, dtype=float)
    ax = np.zeros_like(t)
    ay = np.zeros_like(t)
    for (t0, dur, peak, az) in segments:
        inside = (t >= t0) & (t <= t0 + dur)
        mag = np.where(inside, peak * np.sin(np.pi * (t - t0) / dur), 0.0)
        ax = ax + mag * np.cos(az)
        ay = ay + mag * np.sin(az)
    cth, sth, cph, sph = np.cos(pitch), np.sin(pitch), np.cos(roll), np.sin(roll)
    return np.column_stack([cth * ax, sth * sph * ax + cph * ay, sth * cph * ax - sph * ay])


def ref_vibration(t, segments):
    """Returns (accel_add, gyro_add), each (N, 3), per spec 5.2."""
    t = np.asarray(t, dtype=float)
    acc = np.zeros((len(t), 3))
    gyr = np.zeros((len(t), 3))
    phases = (0.0, 2 * np.pi / 3, 4 * np.pi / 3)
    for (t0, dur, accel_amp, freq, gyro_amp) in segments:
        inside = (t >= t0) & (t <= t0 + dur)
        for i, p in enumerate(phases):
            s = np.sin(2 * np.pi * freq * (t - t0) + p)
            acc[:, i] += np.where(inside, accel_amp * s, 0.0)
            gyr[:, i] += np.where(inside, gyro_amp * s, 0.0)
    return acc, gyr


# ------------------------------------------------------------------ filters
def ref_accel_tilt(f):
    f = np.asarray(f, dtype=float)
    return (np.arctan2(f[:, 1], f[:, 2]),
            np.arctan2(-f[:, 0], np.sqrt(f[:, 1] ** 2 + f[:, 2] ** 2)))


def ref_cf_roll_pitch(t, gyro, accel, tau=0.2, gyro_bias=(0.0, 0.0, 0.0),
                      initial_roll=None, initial_pitch=None):
    """Spec 6.2 line by line."""
    n = len(t)
    roll_acc, pitch_acc = ref_accel_tilt(accel)
    roll = np.empty(n)
    pitch = np.empty(n)
    roll[0] = roll_acc[0] if initial_roll is None else initial_roll
    pitch[0] = pitch_acc[0] if initial_pitch is None else initial_pitch
    b = np.asarray(gyro_bias, dtype=float)
    for k in range(1, n):
        dt = t[k] - t[k - 1]
        w = 0.5 * (gyro[k - 1] + gyro[k]) - b
        php, thp = roll[k - 1], pitch[k - 1]
        r1, p1 = euler_rates(php, thp, w)
        phm, thm = php + 0.5 * dt * r1, thp + 0.5 * dt * p1
        r, p = euler_rates(phm, thm, w)
        alpha = tau / (tau + dt)
        roll[k] = alpha * (php + r * dt) + (1 - alpha) * roll_acc[k]
        pitch[k] = alpha * (thp + p * dt) + (1 - alpha) * pitch_acc[k]
    return roll, pitch


def ref_gate(t, accel, gravity, threshold, hold):
    """Spec 6.4 gate, written as the literal O(N^2) definition."""
    n = len(t)
    if threshold is None:
        return np.zeros(n, dtype=bool)
    norm = np.sqrt((np.asarray(accel, dtype=float) ** 2).sum(axis=1))
    trig = np.abs(norm - gravity) > threshold
    gated = np.zeros(n, dtype=bool)
    for k in range(n):
        for j in range(k + 1):
            if trig[j] and t[j] >= t[k] - hold:
                gated[k] = True
                break
    return gated


def ref_kf_roll_pitch(t, gyro, accel, gyro_noise_std=0.005, accel_noise_std=0.05, bias_rw_std=1e-4,
                      gravity=9.81, gyro_bias_z=0.0, initial_bias=(0.0, 0.0), gate_threshold=None,
                      gate_hold=0.2, gate_r_scale=1e4, initial_roll=None, initial_pitch=None):
    """Spec 6.4 recurrence with explicit 2x2 matrix algebra. Returns a dict of arrays."""
    n = len(t)
    R0 = (accel_noise_std / gravity) ** 2
    roll_acc, pitch_acc = ref_accel_tilt(accel)
    gated = ref_gate(t, accel, gravity, gate_threshold, gate_hold)
    roll, pitch = np.empty(n), np.empty(n)
    bx, by = np.empty(n), np.empty(n)
    cov_r, cov_p = np.empty((n, 2, 2)), np.empty((n, 2, 2))
    roll[0] = roll_acc[0] if initial_roll is None else initial_roll
    pitch[0] = pitch_acc[0] if initial_pitch is None else initial_pitch
    bx[0], by[0] = initial_bias
    cov_r[0] = np.diag([R0 / math.cos(pitch[0]) ** 2, 0.02 ** 2])
    cov_p[0] = np.diag([R0, 0.02 ** 2])
    for k in range(1, n):
        dt = t[k] - t[k - 1]
        gbar = 0.5 * (gyro[k - 1] + gyro[k])
        w = (gbar[0] - bx[k - 1], gbar[1] - by[k - 1], gbar[2] - gyro_bias_z)
        php, thp = roll[k - 1], pitch[k - 1]
        r1, p1 = euler_rates(php, thp, w)
        phm, thm = php + 0.5 * dt * r1, thp + 0.5 * dt * p1
        r, p = euler_rates(phm, thm, w)
        c2 = math.cos(thp) ** 2
        s = gate_r_scale if gated[k] else 1.0
        # roll channel
        x_r = np.array([php + r * dt, bx[k - 1]])
        F_r = np.array([[1.0, -dt], [0.0, 1.0]])
        Q_r = np.diag([gyro_noise_std ** 2 * dt ** 2 / c2, bias_rw_std ** 2 * dt])
        R_r = s * R0 / c2
        P = F_r @ cov_r[k - 1] @ F_r.T + Q_r
        S = P[0, 0] + R_r
        K = P[:, 0] / S
        x = x_r + K * (roll_acc[k] - x_r[0])
        roll[k], bx[k] = x
        cov_r[k] = P - S * np.outer(K, K)
        # pitch channel
        x_p = np.array([thp + p * dt, by[k - 1]])
        F_p = np.array([[1.0, -math.cos(phm) * dt], [0.0, 1.0]])
        Q_p = np.diag([gyro_noise_std ** 2 * dt ** 2, bias_rw_std ** 2 * dt])
        R_p = s * R0
        P = F_p @ cov_p[k - 1] @ F_p.T + Q_p
        S = P[0, 0] + R_p
        K = P[:, 0] / S
        x = x_p + K * (pitch_acc[k] - x_p[0])
        pitch[k], by[k] = x
        cov_p[k] = P - S * np.outer(K, K)
    return dict(roll=roll, pitch=pitch, bias_x=bx, bias_y=by, cov_roll=cov_r, cov_pitch=cov_p,
                gated=gated)


def ref_stationary(t, gyro, accel, t_start, t_end):
    """Spec 6.3 definitions."""
    m = (t >= t_start) & (t <= t_end)
    g, a = gyro[m], accel[m]
    return dict(
        gyro_bias=g.mean(axis=0),
        gyro_noise_std=math.sqrt(np.mean(g.var(axis=0, ddof=1))),
        accel_noise_std=math.sqrt(np.mean(a.var(axis=0, ddof=1))),
        gravity=float(np.mean(np.sqrt((a ** 2).sum(axis=1)))),
        n_samples=int(m.sum()),
    )
