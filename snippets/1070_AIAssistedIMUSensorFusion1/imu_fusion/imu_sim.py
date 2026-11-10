"""IMU simulation (pitch-only rotation, known ground truth).

Tier 1 + Tier 2 (gyro bias random walk and bias step on the y axis).
Units: s, rad, rad/s, m/s^2. Body frame: Android / phyphox convention.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, NamedTuple, Optional

import numpy as np

GRAVITY: float = 9.81

_PITCH_LIMIT = math.pi / 3


@dataclass(frozen=True)
class SimulatedIMU:
    t: np.ndarray               # (N,) s
    gyro: np.ndarray            # (N, 3) rad/s
    accel: np.ndarray           # (N, 3) m/s^2
    roll_true: np.ndarray       # (N,) rad
    pitch_true: np.ndarray      # (N,) rad
    gyro_bias: np.ndarray       # (3,) rad/s, initial bias b0
    fs: float                   # Hz
    gyro_bias_true: np.ndarray  # (N, 3) rad/s, bias actually applied at each sample


def default_pitch_trajectory(t):
    """pitch(t) = 0.5 sin(2 pi 0.1 t) + 0.2 sin(2 pi 0.5 t) and its exact derivative."""
    t = np.asarray(t, dtype=np.float64)
    w1 = 2.0 * np.pi * 0.1
    w2 = 2.0 * np.pi * 0.5
    pitch = 0.5 * np.sin(w1 * t) + 0.2 * np.sin(w2 * t)
    rate = 0.5 * w1 * np.cos(w1 * t) + 0.2 * w2 * np.cos(w2 * t)
    return pitch, rate


def constant_pitch_trajectory(angle: float) -> Callable:
    """Trajectory with pitch == angle and pitch_rate == 0."""
    angle = float(angle)

    def traj(t):
        t = np.asarray(t, dtype=np.float64)
        return np.full(t.shape, angle, dtype=np.float64), np.zeros(t.shape, dtype=np.float64)

    return traj


def _parse_bias_step(bias_step):
    """Return (t_step, delta) as floats, or None. Raises ValueError if malformed."""
    if bias_step is None:
        return None
    try:
        arr = np.asarray(bias_step, dtype=np.float64)
    except (TypeError, ValueError):
        raise ValueError("bias_step must be a length-2 sequence of finite floats") from None
    if arr.shape != (2,) or not np.all(np.isfinite(arr)):
        raise ValueError("bias_step must be a length-2 sequence of finite floats")
    return float(arr[0]), float(arr[1])


def simulate_pitch_imu(
    duration: float = 60.0,
    fs: float = 100.0,
    trajectory: Callable | None = None,
    gyro_bias=(0.01, 0.01, 0.01),
    gyro_noise_std: float = 0.005,
    accel_noise_std: float = 0.05,
    seed: int | None = None,
    gyro_bias_rw_std: float = 0.0,
    bias_step: tuple[float, float] | None = None,
) -> SimulatedIMU:
    if not duration > 0:
        raise ValueError("duration must be > 0")
    if not fs > 0:
        raise ValueError("fs must be > 0")
    n = int(round(duration * fs))
    if n < 2:
        raise ValueError("N must be >= 2")
    if gyro_noise_std < 0 or accel_noise_std < 0:
        raise ValueError("noise standard deviations must be >= 0")
    bias = np.array(gyro_bias, dtype=np.float64)
    if bias.shape != (3,):
        raise ValueError("gyro_bias must have shape (3,)")
    if not gyro_bias_rw_std >= 0:
        raise ValueError("gyro_bias_rw_std must be >= 0")
    step = _parse_bias_step(bias_step)

    if trajectory is None:
        trajectory = default_pitch_trajectory

    t = np.arange(n, dtype=np.float64) / fs
    pitch, pitch_rate = trajectory(t)
    pitch = np.array(pitch, dtype=np.float64)
    pitch_rate = np.array(pitch_rate, dtype=np.float64)
    if pitch.shape != (n,) or pitch_rate.shape != (n,):
        raise ValueError("trajectory must return two arrays of shape (N,)")
    if np.any(np.abs(pitch) > _PITCH_LIMIT + 1e-9):
        raise ValueError("trajectory pitch exceeds pi/3 + 1e-9 rad")

    # Random draws: Tier 1 draws first (unchanged order), random-walk draws afterwards.
    rng = np.random.default_rng(seed)
    gyro_noise = rng.standard_normal((n, 3)) * gyro_noise_std
    accel_noise = rng.standard_normal((n, 3)) * accel_noise_std

    # Time-varying bias (section 4.2 of the Tier 2 spec).
    bias_true = np.empty((n, 3), dtype=np.float64)
    bias_true[:] = bias
    if gyro_bias_rw_std > 0:
        w = rng.standard_normal((n - 1, 3))
        inc = gyro_bias_rw_std * np.sqrt(np.diff(t))[:, None] * w
        rw = np.zeros((n, 3), dtype=np.float64)
        rw[1:] = np.cumsum(inc, axis=0)
        bias_true += rw
    if step is not None:
        t_step, delta = step
        bias_true[t >= t_step, 1] += delta

    gyro = np.empty((n, 3), dtype=np.float64)
    gyro[:, 0] = bias_true[:, 0]
    gyro[:, 1] = pitch_rate + bias_true[:, 1]
    gyro[:, 2] = bias_true[:, 2]
    gyro += gyro_noise

    accel = np.empty((n, 3), dtype=np.float64)
    accel[:, 0] = -GRAVITY * np.sin(pitch)
    accel[:, 1] = 0.0
    accel[:, 2] = GRAVITY * np.cos(pitch)
    accel += accel_noise

    return SimulatedIMU(
        t=t,
        gyro=gyro,
        accel=accel,
        roll_true=np.zeros(n, dtype=np.float64),
        pitch_true=pitch,
        gyro_bias=bias.copy(),
        fs=float(fs),
        gyro_bias_true=bias_true,
    )


# --------------------------------------------------------------------------- #
# Tier 3: roll + pitch simulation with linear-acceleration and vibration segments
# --------------------------------------------------------------------------- #

class LinearAccelSegment(NamedTuple):
    t_start: float    # s
    duration: float   # s
    peak: float       # m/s^2
    azimuth: float    # rad


class VibrationSegment(NamedTuple):
    t_start: float    # s
    duration: float   # s
    accel_amp: float  # m/s^2
    freq: float       # Hz
    gyro_amp: float   # rad/s


DEFAULT_LINEAR_ACCEL_SEGMENTS = (
    LinearAccelSegment(30.0, 2.0, 3.0, 0.0),
    LinearAccelSegment(60.0, 2.0, 3.0, math.pi / 2),
)
DEFAULT_VIBRATION_SEGMENTS = (VibrationSegment(90.0, 5.0, 2.0, 15.0, 0.05),)

_REST_END = 5.0


def default_roll_pitch_trajectory(t):
    """Rest until t = 5 s, then product-of-sines roll and pitch; returns (roll, pitch, roll_rate, pitch_rate)."""
    t = np.asarray(t, dtype=np.float64)
    tau = np.maximum(t - _REST_END, 0.0)   # all four outputs are exactly 0 for t < 5
    a1, b1 = 2.0 * np.pi * 0.05, 2.0 * np.pi * 0.17
    a2, b2 = 2.0 * np.pi * 0.04, 2.0 * np.pi * 0.23
    roll = 0.6 * np.sin(a1 * tau) * np.sin(b1 * tau)
    pitch = 0.7 * np.sin(a2 * tau) * np.sin(b2 * tau)
    roll_rate = 0.6 * (a1 * np.cos(a1 * tau) * np.sin(b1 * tau) + b1 * np.sin(a1 * tau) * np.cos(b1 * tau))
    pitch_rate = 0.7 * (a2 * np.cos(a2 * tau) * np.sin(b2 * tau) + b2 * np.sin(a2 * tau) * np.cos(b2 * tau))
    return roll, pitch, roll_rate, pitch_rate


def constant_roll_pitch_trajectory(roll: float, pitch: float) -> Callable:
    """Trajectory with constant roll and pitch and zero rates."""
    roll = float(roll)
    pitch = float(pitch)

    def traj(t):
        t = np.asarray(t, dtype=np.float64)
        return (np.full(t.shape, roll, dtype=np.float64), np.full(t.shape, pitch, dtype=np.float64),
                np.zeros(t.shape, dtype=np.float64), np.zeros(t.shape, dtype=np.float64))

    return traj


@dataclass(frozen=True)
class SimulatedRollPitchIMU:
    t: np.ndarray               # (N,) s
    gyro: np.ndarray            # (N, 3) rad/s
    accel: np.ndarray           # (N, 3) m/s^2
    roll_true: np.ndarray       # (N,) rad
    pitch_true: np.ndarray      # (N,) rad
    gyro_bias: np.ndarray       # (3,) rad/s
    fs: float                   # Hz
    disturbed_true: np.ndarray  # (N,) bool


def _parse_segments(segments, n_fields):
    """Return a list of tuples of floats; raise ValueError for malformed segments."""
    out = []
    try:
        iterator = iter(segments)
    except TypeError:
        raise ValueError("segments must be a sequence of segments") from None
    for seg in iterator:
        try:
            vals = tuple(float(v) for v in seg)
        except (TypeError, ValueError):
            raise ValueError("malformed segment") from None
        if len(vals) != n_fields:
            raise ValueError("segment must have %d fields" % n_fields)
        if not all(math.isfinite(v) for v in vals):
            raise ValueError("segment values must be finite")
        out.append(vals)
    return out


def simulate_roll_pitch_imu(
    duration: float = 120.0,
    fs: float = 100.0,
    trajectory: Optional[Callable] = None,
    gyro_bias=(0.01, 0.01, 0.01),
    gyro_noise_std: float = 0.005,
    accel_noise_std: float = 0.05,
    seed: Optional[int] = None,
    linear_accel_segments=(),
    vibration_segments=(),
) -> SimulatedRollPitchIMU:
    if not duration > 0:
        raise ValueError("duration must be > 0")
    if not fs > 0:
        raise ValueError("fs must be > 0")
    n = int(round(duration * fs))
    if n < 2:
        raise ValueError("N must be >= 2")
    if gyro_noise_std < 0 or accel_noise_std < 0:
        raise ValueError("noise standard deviations must be >= 0")
    bias = np.array(gyro_bias, dtype=np.float64)
    if bias.shape != (3,):
        raise ValueError("gyro_bias must have shape (3,)")

    lin = _parse_segments(linear_accel_segments, 4)
    vib = _parse_segments(vibration_segments, 5)
    for (_t0, dur, peak, _az) in lin:
        if not dur > 0:
            raise ValueError("segment duration must be > 0")
        if peak < 0:
            raise ValueError("peak must be >= 0")
    for (_t0, dur, a_amp, freq, g_amp) in vib:
        if not dur > 0:
            raise ValueError("segment duration must be > 0")
        if a_amp < 0 or g_amp < 0:
            raise ValueError("accel_amp and gyro_amp must be >= 0")
        if not (freq > 0 and freq < fs / 2.0):
            raise ValueError("freq must satisfy 0 < freq < fs/2")

    if trajectory is None:
        trajectory = default_roll_pitch_trajectory

    t = np.arange(n, dtype=np.float64) / fs
    out = trajectory(t)
    if len(out) != 4:
        raise ValueError("trajectory must return (roll, pitch, roll_rate, pitch_rate)")
    phi, theta, phi_dot, theta_dot = (np.array(o, dtype=np.float64) for o in out)
    if any(a.shape != (n,) for a in (phi, theta, phi_dot, theta_dot)):
        raise ValueError("trajectory must return four arrays of shape (N,)")
    if np.any(np.abs(phi) > _PITCH_LIMIT + 1e-9) or np.any(np.abs(theta) > _PITCH_LIMIT + 1e-9):
        raise ValueError("trajectory angle exceeds pi/3 + 1e-9 rad")

    rng = np.random.default_rng(seed)
    gyro_noise = rng.standard_normal((n, 3)) * gyro_noise_std
    accel_noise = rng.standard_normal((n, 3)) * accel_noise_std

    sp, cp = np.sin(phi), np.cos(phi)
    st, ct = np.sin(theta), np.cos(theta)

    gyro = np.empty((n, 3), dtype=np.float64)
    gyro[:, 0] = phi_dot
    gyro[:, 1] = cp * theta_dot
    gyro[:, 2] = -sp * theta_dot
    gyro += bias

    accel = np.empty((n, 3), dtype=np.float64)
    accel[:, 0] = -GRAVITY * st
    accel[:, 1] = GRAVITY * sp * ct
    accel[:, 2] = GRAVITY * cp * ct

    disturbed = np.zeros(n, dtype=bool)

    # world-frame linear acceleration (horizontal), rotated into the body frame by R^T
    ax_w = np.zeros(n, dtype=np.float64)
    ay_w = np.zeros(n, dtype=np.float64)
    for (t0, dur, peak, az) in lin:
        m = (t >= t0) & (t <= t0 + dur)
        s = peak * np.sin(np.pi * (t[m] - t0) / dur)
        ax_w[m] += s * np.cos(az)
        ay_w[m] += s * np.sin(az)
        disturbed |= m
    accel[:, 0] += ct * ax_w
    accel[:, 1] += st * sp * ax_w + cp * ay_w
    accel[:, 2] += st * cp * ax_w - sp * ay_w

    # vibration: sensor-level artefact, does not change the true angles
    phases = (0.0, 2.0 * math.pi / 3.0, 4.0 * math.pi / 3.0)
    for (t0, dur, a_amp, freq, g_amp) in vib:
        m = (t >= t0) & (t <= t0 + dur)
        for i in range(3):
            arg = 2.0 * np.pi * freq * (t[m] - t0) + phases[i]
            accel[m, i] += a_amp * np.sin(arg)
            gyro[m, i] += g_amp * np.sin(arg)
        disturbed |= m

    gyro += gyro_noise
    accel += accel_noise

    return SimulatedRollPitchIMU(
        t=t,
        gyro=gyro,
        accel=accel,
        roll_true=phi,
        pitch_true=theta,
        gyro_bias=bias.copy(),
        fs=float(fs),
        disturbed_true=disturbed,
    )
