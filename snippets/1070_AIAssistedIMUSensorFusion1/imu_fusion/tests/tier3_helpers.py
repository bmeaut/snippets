"""Scenario runners and fixture builders for the Tier 3 tests (tier3_spec.md sections 10, 11).

Results are cached per (scenario, seed). Tests must treat the returned arrays as read-only.
Python 3.9-valid syntax.
"""
import functools
import io
import zipfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

KEYS = ("accel", "CF", "KF", "KF-gated")
S6_SEEDS = tuple(range(5))
S7_SEEDS = tuple(range(5))

# Spec 11.1 "Definitions" (explicit interval lists from the spec)
SEGMENT_ENDS = (32.0, 62.0, 95.0)
RECOVERY_WINDOWS = ((32.0, 60.0, False), (62.0, 90.0, False), (95.0, 150.0, True))  # (lo, hi, hi_inclusive)
QUIET_INTERVALS = ((20.0, 30.0, False), (47.0, 60.0, False), (77.0, 90.0, False), (110.0, 150.0, True))


def interval_mask(t, intervals):
    mask = np.zeros(t.shape, dtype=bool)
    for lo, hi, hi_inclusive in intervals:
        mask |= (t >= lo) & ((t <= hi) if hi_inclusive else (t < hi))
    return mask


def run_estimators(t, gyro, accel, rest_window):
    """Spec 10 'Estimator configuration'. Returns dict key -> (roll, pitch), plus the extras."""
    import imu_filters as F

    est = F.estimate_stationary(t, gyro, accel, rest_window[0], rest_window[1])
    accel_rp = F.accel_tilt(accel)
    cf = F.complementary_roll_pitch(t, gyro, accel, tau=0.2, gyro_bias=est.gyro_bias)
    kw = dict(gyro_noise_std=est.gyro_noise_std, accel_noise_std=est.accel_noise_std,
              gravity=est.gravity, gyro_bias_z=est.gyro_bias[2],
              initial_bias=(est.gyro_bias[0], est.gyro_bias[1]))
    kf = F.kalman_roll_pitch(t, gyro, accel, **kw)
    kfg = F.kalman_roll_pitch(t, gyro, accel, gate_threshold=0.2, **kw)
    return SimpleNamespace(
        est=est,
        angles={"accel": (accel_rp[0], accel_rp[1]), "CF": cf,
                "KF": (kf.roll, kf.pitch), "KF-gated": (kfg.roll, kfg.pitch)},
        kf=kf, kfg=kfg)


@functools.lru_cache(maxsize=None)
def sim_run(scenario, seed):
    """S6 or S7 with seed; the estimators of spec 10 with the simulated rest window (0, 4.5)."""
    import imu_sim

    if scenario == "S6":
        sim = imu_sim.simulate_roll_pitch_imu(seed=seed)
    elif scenario == "S7":
        sim = imu_sim.simulate_roll_pitch_imu(
            duration=150.0, seed=seed,
            linear_accel_segments=imu_sim.DEFAULT_LINEAR_ACCEL_SEGMENTS,
            vibration_segments=imu_sim.DEFAULT_VIBRATION_SEGMENTS)
    else:
        raise KeyError(scenario)
    out = run_estimators(sim.t, sim.gyro, sim.accel, (0.0, 4.5))
    out.sim = sim
    out.t = sim.t
    out.truth = (sim.roll_true, sim.pitch_true)
    return out


# ------------------------------------------------------------------ real recordings
REAL_FILES = {"A": DATA_DIR / "phone_tilts.zip", "B": DATA_DIR / "phone_disturbances.zip"}


@functools.lru_cache(maxsize=None)
def real_run(name):
    """Loads recording A or B, resamples to 100 Hz, runs the estimators with the real rest window.

    Fails (does not skip) if the file is missing.
    """
    import imu_io

    path = REAL_FILES[name]
    if not path.exists():
        pytest.fail("Real recording %s is missing: the owner must place it at %s" % (name, path),
                    pytrace=False)
    rec = imu_io.load_phyphox_zip(str(path))
    t, gyro, accel = imu_io.resample_common(rec.accel_t, rec.accel, rec.gyro_t, rec.gyro, fs=100.0)
    out = run_estimators(t, gyro, accel, (t[0] + 1.0, t[0] + 7.0))
    out.rec, out.t, out.gyro, out.accel = rec, t, gyro, accel
    return out


# ------------------------------------------------------------------ synthetic phyphox zips
ACCEL_HEADER = "Time (s),X (m/s^2),Y (m/s^2),Z (m/s^2)"
GYRO_HEADER = "Time (s),X (rad/s),Y (rad/s),Z (rad/s)"


def csv_text(header, rows, newline="\n", trailing="", bom=False):
    """rows: list of 4-item sequences of already formatted strings."""
    lines = [header] + [",".join(r) for r in rows]
    text = newline.join(lines) + newline + trailing
    return ("﻿" if bom else "") + text


def write_zip(path, members):
    """members: dict name -> str or bytes. Returns the path as str."""
    with zipfile.ZipFile(str(path), "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in members.items():
            zf.writestr(name, content if isinstance(content, bytes) else content.encode("utf-8"))
    return str(path)


def fmt_rows(arr):
    """Format an (n, 4) float array as exponent-notation strings (uppercase E)."""
    return [["%.9E" % v for v in row] for row in arr]
