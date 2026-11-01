"""Pitch estimators. Depends on NumPy only (must not import imu_sim, imu_metrics, imu_plots).

Tier 1: accel_tilt, gyro_integrate, complementary_filter.
Tier 2: kalman_noise_matrices, KalmanResult, kalman_pitch.

Units: s, rad, rad/s, m/s^2. No angle wrapping, no ground-truth inputs.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np


def accel_tilt(accel):
    """Return (roll, pitch) in rad from specific force of shape (N, 3)."""
    a = np.asarray(accel, dtype=np.float64)
    if a.ndim != 2 or a.shape[1] != 3:
        raise ValueError("accel must be 2-D with 3 columns")
    fx, fy, fz = a[:, 0], a[:, 1], a[:, 2]
    roll = np.arctan2(fy, fz)
    pitch = np.arctan2(-fx, np.sqrt(fy * fy + fz * fz))
    return roll, pitch


def _check_series(t, *series):
    t = np.asarray(t, dtype=np.float64)
    arrs = [np.asarray(s, dtype=np.float64) for s in series]
    if t.ndim != 1 or any(a.ndim != 1 for a in arrs):
        raise ValueError("inputs must be 1-D")
    if any(a.shape != t.shape for a in arrs):
        raise ValueError("input lengths do not match")
    if t.shape[0] < 1:
        raise ValueError("N must be >= 1")
    if t.shape[0] > 1 and not np.all(np.diff(t) > 0):
        raise ValueError("t must be strictly increasing")
    return (t, *arrs)


def gyro_integrate(t, gyro_rate, initial_angle=0.0):
    """Backward rectangle integration using the current sample's rate."""
    t, rate = _check_series(t, gyro_rate)
    inc = np.empty(t.shape[0], dtype=np.float64)
    inc[0] = float(initial_angle)
    inc[1:] = rate[1:] * np.diff(t)
    return np.cumsum(inc)


def complementary_filter(t, gyro_rate, accel_angle, tau=0.2, initial_angle=None):
    """First-order complementary filter (Tier 1 spec section 5.3)."""
    if not tau > 0:
        raise ValueError("tau must be > 0")
    t, rate, acc = _check_series(t, gyro_rate, accel_angle)
    n = t.shape[0]
    out = np.empty(n, dtype=np.float64)
    out[0] = acc[0] if initial_angle is None else float(initial_angle)
    tau = float(tau)
    prev = float(out[0])
    tl = t.tolist()
    rl = rate.tolist()
    al = acc.tolist()
    for k in range(1, n):
        dt = tl[k] - tl[k - 1]
        alpha = tau / (tau + dt)
        prev = alpha * (prev + rl[k] * dt) + (1.0 - alpha) * al[k]
        out[k] = prev
    return out


# --------------------------------------------------------------------------- #
# Tier 2: linear Kalman filter, state [pitch angle, gyro bias (y axis)]
# --------------------------------------------------------------------------- #

def kalman_noise_matrices(dt, gyro_noise_std, accel_noise_std, bias_rw_std, gravity=9.81):
    """Return (Q, R): Q is (2, 2) float64, R is a float in rad^2 (spec section 5.1)."""
    if not dt > 0:
        raise ValueError("dt must be > 0")
    if not gyro_noise_std > 0:
        raise ValueError("gyro_noise_std must be > 0")
    if not accel_noise_std > 0:
        raise ValueError("accel_noise_std must be > 0")
    if not bias_rw_std >= 0:
        raise ValueError("bias_rw_std must be >= 0")
    if not gravity > 0:
        raise ValueError("gravity must be > 0")
    Q = np.zeros((2, 2), dtype=np.float64)
    Q[0, 0] = gyro_noise_std ** 2 * dt ** 2
    Q[1, 1] = bias_rw_std ** 2 * dt
    R = float((accel_noise_std / gravity) ** 2)
    return Q, R


@dataclass(frozen=True)
class KalmanResult:
    angle: np.ndarray  # (N,) rad, posterior
    bias: np.ndarray   # (N,) rad/s, posterior
    cov: np.ndarray    # (N, 2, 2) posterior covariance


def _check_initial_cov(initial_cov):
    P0 = np.asarray(initial_cov, dtype=np.float64)
    if P0.shape != (2, 2):
        raise ValueError("initial_cov must have shape (2, 2)")
    if not np.all(np.isfinite(P0)):
        raise ValueError("initial_cov must be finite")
    if not np.allclose(P0, P0.T, rtol=0.0, atol=1e-12):
        raise ValueError("initial_cov must be symmetric")
    eig = np.linalg.eigvalsh(0.5 * (P0 + P0.T))
    # strictly negative eigenvalue -> error; tiny round-off relative to the scale is tolerated
    if eig[0] < -1e-12 * max(float(np.max(np.abs(eig))), np.finfo(np.float64).tiny):
        raise ValueError("initial_cov must be positive semi-definite")
    return P0


def kalman_pitch(
    t,
    gyro_rate,
    accel_angle,
    gyro_noise_std=0.005,
    accel_noise_std=0.05,
    bias_rw_std=1e-4,
    gravity=9.81,
    initial_angle=None,
    initial_bias=0.0,
    initial_cov=None,
):
    """Linear Kalman filter for pitch with gyro-bias state (spec section 5.3).

    The prediction step uses the trapezoidal rate (gyro_rate[k-1] + gyro_rate[k]) / 2.
    The noise parameters are sensor specifications and must be supplied by the caller.
    """
    t, rate, acc = _check_series(t, gyro_rate, accel_angle)
    # validates the noise parameters (dt is a placeholder here) and gives R
    _, R = kalman_noise_matrices(1.0, gyro_noise_std, accel_noise_std, bias_rw_std, gravity)
    if initial_cov is None:
        P0 = np.diag([R, 0.02 ** 2]).astype(np.float64)
    else:
        P0 = _check_initial_cov(initial_cov)

    n = t.shape[0]
    angle = np.empty(n, dtype=np.float64)
    bias = np.empty(n, dtype=np.float64)
    cov_flat = np.empty((n, 4), dtype=np.float64)

    x0 = float(acc[0]) if initial_angle is None else float(initial_angle)
    x1 = float(initial_bias)
    p00, p01, p10, p11 = float(P0[0, 0]), float(P0[0, 1]), float(P0[1, 0]), float(P0[1, 1])
    angle[0] = x0
    bias[0] = x1
    cov_flat[0] = (p00, p01, p10, p11)

    gs = float(gyro_noise_std)
    bs = float(bias_rw_std)
    tl = t.tolist()
    rl = rate.tolist()
    al = acc.tolist()
    a_ang = [0.0] * n
    a_bias = [0.0] * n
    a_cov = [None] * n

    for k in range(1, n):
        dt = tl[k] - tl[k - 1]
        wbar = (rl[k - 1] + rl[k]) / 2.0
        q00 = gs ** 2 * dt ** 2
        q11 = bs ** 2 * dt

        # prediction
        xm0 = x0 + (wbar - x1) * dt
        xm1 = x1
        # P- = F P F^T + Q with F = [[1, -dt], [0, 1]]
        f01 = p01 - dt * p11
        m00 = (p00 - dt * p10) - dt * f01 + q00
        m01 = f01
        m10 = p10 - dt * p11
        m11 = p11 + q11

        # update with H = [1, 0]
        S = m00 + R
        k0 = m00 / S
        k1 = m10 / S
        y = al[k] - xm0
        x0 = xm0 + k0 * y
        x1 = xm1 + k1 * y
        p00 = m00 - S * (k0 * k0)
        p01 = m01 - S * (k0 * k1)
        p10 = m10 - S * (k1 * k0)
        p11 = m11 - S * (k1 * k1)

        a_ang[k] = x0
        a_bias[k] = x1
        a_cov[k] = (p00, p01, p10, p11)

    if n > 1:
        angle[1:] = a_ang[1:]
        bias[1:] = a_bias[1:]
        cov_flat[1:] = np.asarray(a_cov[1:], dtype=np.float64)
    cov = cov_flat.reshape(n, 2, 2)
    return KalmanResult(angle=angle, bias=bias, cov=cov)


# --------------------------------------------------------------------------- #
# Tier 3: roll + pitch estimators (Euler kinematics, yaw == 0)
# --------------------------------------------------------------------------- #

def _check_motion_inputs(t, gyro, accel):
    t = np.asarray(t, dtype=np.float64)
    g = np.asarray(gyro, dtype=np.float64)
    a = np.asarray(accel, dtype=np.float64)
    if t.ndim != 1:
        raise ValueError("t must have shape (N,)")
    if g.ndim != 2 or g.shape[1] != 3 or a.ndim != 2 or a.shape[1] != 3:
        raise ValueError("gyro and accel must have shape (N, 3)")
    if g.shape[0] != t.shape[0] or a.shape[0] != t.shape[0]:
        raise ValueError("t, gyro and accel must have the same length")
    if t.shape[0] < 1:
        raise ValueError("N must be >= 1")
    if t.shape[0] > 1 and not np.all(np.diff(t) > 0):
        raise ValueError("t must be strictly increasing")
    return t, g, a


def _euler_step_rates(phi, theta, wx, wy, wz, dt):
    """Section 6.1: Euler rates at the midpoint angles. Returns (r, p, phi_mid)."""
    sp = math.sin(phi)
    cp = math.cos(phi)
    r1 = wx + math.tan(theta) * (sp * wy + cp * wz)
    p1 = cp * wy - sp * wz
    phim = phi + 0.5 * dt * r1
    thm = theta + 0.5 * dt * p1
    spm = math.sin(phim)
    cpm = math.cos(phim)
    r = wx + math.tan(thm) * (spm * wy + cpm * wz)
    p = cpm * wy - spm * wz
    return r, p, phim


def complementary_roll_pitch(
    t,
    gyro,
    accel,
    tau=0.2,
    gyro_bias=(0.0, 0.0, 0.0),
    initial_roll=None,
    initial_pitch=None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Roll/pitch complementary filter with trapezoidal rate and midpoint Euler mapping."""
    if not tau > 0:
        raise ValueError("tau must be > 0")
    t, g, a = _check_motion_inputs(t, gyro, accel)
    b = np.asarray(gyro_bias, dtype=np.float64)
    if b.shape != (3,):
        raise ValueError("gyro_bias must have shape (3,)")
    n = t.shape[0]
    roll_acc, pitch_acc = accel_tilt(a)
    roll = np.empty(n, dtype=np.float64)
    pitch = np.empty(n, dtype=np.float64)
    roll[0] = roll_acc[0] if initial_roll is None else float(initial_roll)
    pitch[0] = pitch_acc[0] if initial_pitch is None else float(initial_pitch)
    if n == 1:
        return roll, pitch

    gbar = (g[:-1] + g[1:]) / 2.0 - b
    wxl, wyl, wzl = gbar[:, 0].tolist(), gbar[:, 1].tolist(), gbar[:, 2].tolist()
    dtl = np.diff(t).tolist()
    ral = roll_acc.tolist()
    pal = pitch_acc.tolist()
    tau = float(tau)
    phi = float(roll[0])
    th = float(pitch[0])
    for k in range(1, n):
        dt = dtl[k - 1]
        r, p, _ = _euler_step_rates(phi, th, wxl[k - 1], wyl[k - 1], wzl[k - 1], dt)
        alpha = tau / (tau + dt)
        phi = alpha * (phi + r * dt) + (1.0 - alpha) * ral[k]
        th = alpha * (th + p * dt) + (1.0 - alpha) * pal[k]
        roll[k] = phi
        pitch[k] = th
    return roll, pitch


@dataclass(frozen=True)
class StationaryEstimate:
    gyro_bias: np.ndarray      # (3,) rad/s
    gyro_noise_std: float      # rad/s
    accel_noise_std: float     # m/s^2
    gravity: float             # m/s^2
    n_samples: int


def estimate_stationary(t, gyro, accel, t_start, t_end) -> StationaryEstimate:
    """Estimate gyro bias, noise levels and local gravity from a stationary window."""
    t = np.asarray(t, dtype=np.float64)
    g = np.asarray(gyro, dtype=np.float64)
    a = np.asarray(accel, dtype=np.float64)
    if t.ndim != 1:
        raise ValueError("t must have shape (N,)")
    if g.ndim != 2 or g.shape[1] != 3 or a.ndim != 2 or a.shape[1] != 3:
        raise ValueError("gyro and accel must have shape (N, 3)")
    if g.shape[0] != t.shape[0] or a.shape[0] != t.shape[0]:
        raise ValueError("t, gyro and accel must have the same length")
    if not t_start < t_end:
        raise ValueError("t_start must be < t_end")
    m = (t >= t_start) & (t <= t_end)
    n = int(np.count_nonzero(m))
    if n < 10:
        raise ValueError("fewer than 10 samples in the window")
    gw = g[m]
    aw = a[m]
    return StationaryEstimate(
        gyro_bias=np.mean(gw, axis=0),
        gyro_noise_std=float(np.sqrt(np.mean(np.var(gw, axis=0, ddof=1)))),
        accel_noise_std=float(np.sqrt(np.mean(np.var(aw, axis=0, ddof=1)))),
        gravity=float(np.mean(np.sqrt(np.sum(aw * aw, axis=1)))),
        n_samples=n,
    )


@dataclass(frozen=True)
class RollPitchKalmanResult:
    roll: np.ndarray        # (N,) rad
    pitch: np.ndarray       # (N,) rad
    bias_x: np.ndarray      # (N,) rad/s
    bias_y: np.ndarray      # (N,) rad/s
    cov_roll: np.ndarray    # (N, 2, 2)
    cov_pitch: np.ndarray   # (N, 2, 2)
    gated: np.ndarray       # (N,) bool


def kalman_roll_pitch(
    t,
    gyro,
    accel,
    gyro_noise_std=0.005,
    accel_noise_std=0.05,
    bias_rw_std=1e-4,
    gravity=9.81,
    gyro_bias_z=0.0,
    initial_bias=(0.0, 0.0),
    gate_threshold=None,
    gate_hold=0.2,
    gate_r_scale=1e4,
    initial_roll=None,
    initial_pitch=None,
) -> RollPitchKalmanResult:
    """Two decoupled 2-state Kalman filters (roll/b_x and pitch/b_y); see Tier 3 spec section 6.4."""
    t, g, a = _check_motion_inputs(t, gyro, accel)
    _, R0 = kalman_noise_matrices(1.0, gyro_noise_std, accel_noise_std, bias_rw_std, gravity)
    if gate_threshold is not None and not gate_threshold > 0:
        raise ValueError("gate_threshold must be > 0 or None")
    if not gate_hold >= 0:
        raise ValueError("gate_hold must be >= 0")
    if not gate_r_scale >= 1:
        raise ValueError("gate_r_scale must be >= 1")
    ib = np.asarray(initial_bias, dtype=np.float64)
    if ib.shape != (2,):
        raise ValueError("initial_bias must have length 2")

    n = t.shape[0]
    roll_acc, pitch_acc = accel_tilt(a)
    tl = t.tolist()

    # gate: any trigger within the last gate_hold seconds (inclusive), including the current sample
    gated = np.zeros(n, dtype=bool)
    if gate_threshold is not None:
        trig = np.abs(np.sqrt(np.sum(a * a, axis=1)) - gravity) > gate_threshold
        trl = trig.tolist()
        last = None
        gl = [False] * n
        for k in range(n):
            if trl[k]:
                last = tl[k]
            if last is not None and last >= tl[k] - gate_hold:
                gl[k] = True
        gated = np.array(gl, dtype=bool)

    roll = np.empty(n, dtype=np.float64)
    pitch = np.empty(n, dtype=np.float64)
    bias_x = np.empty(n, dtype=np.float64)
    bias_y = np.empty(n, dtype=np.float64)
    cov_roll = np.empty((n, 2, 2), dtype=np.float64)
    cov_pitch = np.empty((n, 2, 2), dtype=np.float64)

    phi = float(roll_acc[0]) if initial_roll is None else float(initial_roll)
    th = float(pitch_acc[0]) if initial_pitch is None else float(initial_pitch)
    bx = float(ib[0])
    by = float(ib[1])
    c0 = math.cos(th)
    # symmetric 2x2 covariances stored as (p00, p01, p11)
    a00, a01, a11 = R0 / (c0 * c0), 0.0, 0.02 ** 2     # roll filter
    b00, b01, b11 = R0, 0.0, 0.02 ** 2                 # pitch filter

    o_roll = [phi] * n
    o_pitch = [th] * n
    o_bx = [bx] * n
    o_by = [by] * n
    o_cr = [(a00, a01, a11)] * n
    o_cp = [(b00, b01, b11)] * n

    if n > 1:
        gbar = (g[:-1] + g[1:]) / 2.0
        wxl = gbar[:, 0].tolist()
        wyl = gbar[:, 1].tolist()
        wzl = gbar[:, 2].tolist()
        dtl = np.diff(t).tolist()
        ral = roll_acc.tolist()
        pal = pitch_acc.tolist()
        gl = gated.tolist()
        gs2 = float(gyro_noise_std) ** 2
        bs2 = float(bias_rw_std) ** 2
        gbz = float(gyro_bias_z)
        scale = float(gate_r_scale)
        for k in range(1, n):
            dt = dtl[k - 1]
            wx = wxl[k - 1] - bx
            wy = wyl[k - 1] - by
            wz = wzl[k - 1] - gbz
            r, p, phim = _euler_step_rates(phi, th, wx, wy, wz, dt)
            cth = math.cos(th)
            c2 = cth * cth
            s = scale if gl[k] else 1.0
            q11 = bs2 * dt

            # roll filter, state [phi, b_x], F = [[1, -dt], [0, 1]]
            f = -dt
            xm0 = phi + r * dt
            m00 = a00 + 2.0 * f * a01 + f * f * a11 + gs2 * dt * dt / c2
            m01 = a01 + f * a11
            m11 = a11 + q11
            S = m00 + s * R0 / c2
            k0 = m00 / S
            k1 = m01 / S
            y = ral[k] - xm0
            phi_new = xm0 + k0 * y
            bx_new = bx + k1 * y
            a00 = m00 - S * (k0 * k0)
            a01 = m01 - S * (k0 * k1)
            a11 = m11 - S * (k1 * k1)

            # pitch filter, state [theta, b_y], F = [[1, -cos(phi_mid) dt], [0, 1]]
            f = -math.cos(phim) * dt
            xm0 = th + p * dt
            m00 = b00 + 2.0 * f * b01 + f * f * b11 + gs2 * dt * dt
            m01 = b01 + f * b11
            m11 = b11 + q11
            S = m00 + s * R0
            k0 = m00 / S
            k1 = m01 / S
            y = pal[k] - xm0
            th_new = xm0 + k0 * y
            by_new = by + k1 * y
            b00 = m00 - S * (k0 * k0)
            b01 = m01 - S * (k0 * k1)
            b11 = m11 - S * (k1 * k1)

            phi, th, bx, by = phi_new, th_new, bx_new, by_new
            o_roll[k] = phi
            o_pitch[k] = th
            o_bx[k] = bx
            o_by[k] = by
            o_cr[k] = (a00, a01, a11)
            o_cp[k] = (b00, b01, b11)

    roll[:] = o_roll
    pitch[:] = o_pitch
    bias_x[:] = o_bx
    bias_y[:] = o_by
    for cov, rows in ((cov_roll, o_cr), (cov_pitch, o_cp)):
        arr = np.asarray(rows, dtype=np.float64).reshape(n, 3)
        cov[:, 0, 0] = arr[:, 0]
        cov[:, 0, 1] = arr[:, 1]
        cov[:, 1, 0] = arr[:, 1]
        cov[:, 1, 1] = arr[:, 2]
    return RollPitchKalmanResult(
        roll=roll, pitch=pitch, bias_x=bias_x, bias_y=bias_y,
        cov_roll=cov_roll, cov_pitch=cov_pitch, gated=gated,
    )
