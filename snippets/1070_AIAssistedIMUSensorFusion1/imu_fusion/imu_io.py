"""phyphox loading and resampling (Tier 3).

Reads the phyphox iOS "CSV (Comma, decimal point)" export. Depends on NumPy and the
standard library only (must not import imu_sim, imu_filters or imu_plots).
"""
from __future__ import annotations

import os
import re
import zipfile
from dataclasses import dataclass
from typing import Tuple

import numpy as np

_ACCEL_HEADER = ["Time (s)", "X (m/s^2)", "Y (m/s^2)", "Z (m/s^2)"]
_GYRO_HEADER = ["Time (s)", "X (rad/s)", "Y (rad/s)", "Z (rad/s)"]
_NUMBER = re.compile(r"[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?\Z")


@dataclass(frozen=True)
class PhyphoxRecording:
    accel_t: np.ndarray   # (Na,) s
    accel: np.ndarray     # (Na, 3) m/s^2
    gyro_t: np.ndarray    # (Ng,) s
    gyro: np.ndarray      # (Ng, 3) rad/s
    source: str


def _unquote(field):
    field = field.strip()
    if len(field) >= 2 and field[0] == '"' and field[-1] == '"':
        field = field[1:-1]
    return field


def _parse_csv(raw, expected_header, name):
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("%s is not valid UTF-8" % name) from None
    lines = text.split("\n")
    header = [_unquote(f) for f in lines[0].rstrip("\r").split(",")]
    if header != expected_header:
        raise ValueError("%s: unexpected header %r" % (name, header))
    rows = []
    for number, line in enumerate(lines[1:], start=2):
        line = line.rstrip("\r")
        if line.strip() == "":
            continue
        fields = line.split(",")
        if len(fields) != 4:
            raise ValueError("%s line %d: expected 4 fields, got %d" % (name, number, len(fields)))
        row = []
        for f in fields:
            f = _unquote(f).strip()
            if not _NUMBER.match(f):
                raise ValueError("%s line %d: non-numeric value %r" % (name, number, f))
            v = float(f)
            if not np.isfinite(v):
                raise ValueError("%s line %d: non-finite value" % (name, number))
            row.append(v)
        rows.append(row)
    if len(rows) < 2:
        raise ValueError("%s: fewer than 2 data rows" % name)
    arr = np.array(rows, dtype=np.float64)
    if not np.all(np.diff(arr[:, 0]) > 0):
        raise ValueError("%s: time must be strictly increasing" % name)
    return arr[:, 0].copy(), arr[:, 1:4].copy()


def load_phyphox_zip(path) -> PhyphoxRecording:
    """Load Accelerometer.csv and Gyroscope.csv from a phyphox zip export (values unchanged)."""
    path = os.fspath(path)
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    if not zipfile.is_zipfile(path):
        raise ValueError("not a zip file: %s" % path)
    try:
        with zipfile.ZipFile(path) as zf:
            members = set(zf.namelist())
            for required in ("Accelerometer.csv", "Gyroscope.csv"):
                if required not in members:
                    raise ValueError("zip is missing the member %s" % required)
            raw_a = zf.read("Accelerometer.csv")
            raw_g = zf.read("Gyroscope.csv")
    except zipfile.BadZipFile:
        raise ValueError("not a valid zip file: %s" % path) from None
    accel_t, accel = _parse_csv(raw_a, _ACCEL_HEADER, "Accelerometer.csv")
    gyro_t, gyro = _parse_csv(raw_g, _GYRO_HEADER, "Gyroscope.csv")
    return PhyphoxRecording(accel_t=accel_t, accel=accel, gyro_t=gyro_t, gyro=gyro, source=path)


def resample_common(accel_t, accel, gyro_t, gyro, fs=100.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Linearly interpolate both sensors onto a common uniform grid over their overlap.

    Returns (t, gyro_rs, accel_rs).
    """
    if not fs > 0:
        raise ValueError("fs must be > 0")
    at = np.asarray(accel_t, dtype=np.float64)
    gt = np.asarray(gyro_t, dtype=np.float64)
    a = np.asarray(accel, dtype=np.float64)
    g = np.asarray(gyro, dtype=np.float64)
    if at.ndim != 1 or gt.ndim != 1:
        raise ValueError("time arrays must be 1-D")
    if a.ndim != 2 or a.shape[1] != 3 or a.shape[0] != at.shape[0]:
        raise ValueError("accel must have shape (Na, 3) matching accel_t")
    if g.ndim != 2 or g.shape[1] != 3 or g.shape[0] != gt.shape[0]:
        raise ValueError("gyro must have shape (Ng, 3) matching gyro_t")
    if at.shape[0] < 2 or gt.shape[0] < 2:
        raise ValueError("need at least 2 samples per sensor")
    if not np.all(np.diff(at) > 0) or not np.all(np.diff(gt) > 0):
        raise ValueError("time must be strictly increasing")
    t0 = max(at[0], gt[0])
    t1 = min(at[-1], gt[-1])
    if not t1 > t0:
        raise ValueError("sensors do not overlap in time")
    m = int(np.floor((t1 - t0) * fs + 1e-9)) + 1
    if m < 2:
        raise ValueError("overlap too short for the requested fs (M < 2)")
    t = t0 + np.arange(m, dtype=np.float64) / fs
    gyro_rs = np.empty((m, 3), dtype=np.float64)
    accel_rs = np.empty((m, 3), dtype=np.float64)
    for i in range(3):
        gyro_rs[:, i] = np.interp(t, gt, g[:, i])
        accel_rs[:, i] = np.interp(t, at, a[:, i])
    return t, gyro_rs, accel_rs
