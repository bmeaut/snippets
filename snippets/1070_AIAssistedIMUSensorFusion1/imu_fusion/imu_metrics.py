"""Error metrics. Depends on NumPy only. Inputs in rad; e = estimate - truth."""
from __future__ import annotations

import numpy as np


def _prep(*arrays):
    out = [np.asarray(a, dtype=np.float64) for a in arrays]
    if any(a.ndim != 1 for a in out):
        raise ValueError("inputs must be 1-D")
    if any(a.shape != out[0].shape for a in out):
        raise ValueError("input shapes do not match")
    if out[0].shape[0] == 0:
        raise ValueError("inputs must not be empty")
    if any(np.isnan(a).any() for a in out):
        raise ValueError("inputs must not contain NaN")
    return out


def rmse(estimate, truth) -> float:
    est, tru = _prep(estimate, truth)
    e = est - tru
    return float(np.sqrt(np.mean(e * e)))


def max_abs_error(estimate, truth) -> float:
    est, tru = _prep(estimate, truth)
    return float(np.max(np.abs(est - tru)))


def drift_rate(t, estimate, truth) -> float:
    """OLS slope of e = estimate - truth against t, in rad/s."""
    tt, est, tru = _prep(t, estimate, truth)
    if tt.shape[0] < 2:
        raise ValueError("drift_rate requires N >= 2")
    e = est - tru
    tc = tt - tt.mean()
    denom = float(np.sum(tc * tc))
    if denom == 0.0:
        raise ValueError("t must not be constant")
    return float(np.sum(tc * (e - e.mean())) / denom)


def convergence_time(t, estimate, truth, tol, t_start=None) -> float:
    """Time after which |estimate - truth| stays <= tol (samples with t >= t_start only).

    Returns the first considered time if |e| never exceeds tol, inf if the last sample
    violates tol, otherwise t[j + 1] where j is the last violating considered sample.
    """
    tt, est, tru = _prep(t, estimate, truth)
    if not tol > 0:
        raise ValueError("tol must be > 0")
    start = tt[0] if t_start is None else float(t_start)
    mask = tt >= start
    if not mask.any():
        raise ValueError("no samples with t >= t_start")
    tc = tt[mask]
    viol = np.abs(est[mask] - tru[mask]) > tol
    if not viol.any():
        return float(tc[0])
    if viol[-1]:
        return float("inf")
    j = int(np.nonzero(viol)[0][-1])
    return float(tc[j + 1])


def coverage_fraction(estimate, truth, std, n_sigma=2.0) -> float:
    """Fraction of samples with |estimate - truth| <= n_sigma * std (inclusive)."""
    est, tru, s = _prep(estimate, truth, std)
    if np.any(s < 0):
        raise ValueError("std must be >= 0")
    if not n_sigma > 0:
        raise ValueError("n_sigma must be > 0")
    return float(np.mean(np.abs(est - tru) <= n_sigma * s))
