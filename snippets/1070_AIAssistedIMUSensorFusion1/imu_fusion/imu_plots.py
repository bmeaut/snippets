"""Plotting. Angles are given in rad and displayed in degrees (bias in deg/s)."""
from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def plot_comparison(t, truth, estimates, title: str = "") -> Figure:
    """Two-axes figure: angles (deg) and errors (deg). Does not call plt.show()."""
    if not isinstance(estimates, dict) or len(estimates) == 0:
        raise ValueError("estimates must be a non-empty dict")
    t = np.asarray(t, dtype=np.float64)
    truth = np.asarray(truth, dtype=np.float64)
    if t.ndim != 1 or truth.shape != t.shape:
        raise ValueError("t and truth must be 1-D arrays of equal length")
    est = {}
    for name, series in estimates.items():
        arr = np.asarray(series, dtype=np.float64)
        if arr.shape != t.shape:
            raise ValueError(f"estimate '{name}' length does not match t")
        est[name] = arr

    fig, (ax0, ax1) = plt.subplots(2, 1, sharex=True, figsize=(10, 7))
    ax0.plot(t, np.rad2deg(truth), label="truth", color="black", linewidth=1.5)
    for name, arr in est.items():
        ax0.plot(t, np.rad2deg(arr), label=name, linewidth=1.0)
    ax0.set_ylabel("Pitch (deg)")
    ax0.set_title(title)
    ax0.grid(True, alpha=0.3)
    ax0.legend(loc="best")

    for name, arr in est.items():
        ax1.plot(t, np.rad2deg(arr - truth), label=name, linewidth=1.0)
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Pitch error (deg)")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="best")

    fig.tight_layout()
    return fig


def _check_shade(shade, t):
    """Return a bool array of shape t.shape, or None."""
    if shade is None:
        return None
    arr = np.asarray(shade)
    if arr.shape != t.shape:
        raise ValueError("shade must have the same shape as t")
    return arr.astype(bool)


def _shade_spans(ax, t, mask):
    """One axvspan per maximal run of True samples; only the first one is labelled."""
    if mask is None:
        return
    n = mask.shape[0]
    first = True
    i = 0
    while i < n:
        if mask[i]:
            j = i
            while j + 1 < n and mask[j + 1]:
                j += 1
            kwargs = {"label": "disturbance"} if first else {}
            ax.axvspan(t[i], t[j], alpha=0.2, color="tab:red", linewidth=0, **kwargs)
            first = False
            i = j + 1
        else:
            i += 1


def _draw_error_axes(ax, x, background, foreground, t_full, mask):
    for name, y in background.items():
        ax.plot(x, y, label=name, linewidth=1.0, alpha=0.35, zorder=1)
    for name, y in foreground.items():
        ax.plot(x, y, label=name, linewidth=1.0, zorder=3)
    _shade_spans(ax, t_full, mask)
    if foreground:
        ys = list(foreground.values())
    else:
        ys = list(background.values())
    m = min(float(np.min(y)) for y in ys)
    M = max(float(np.max(y)) for y in ys)
    r = M - m
    if foreground:
        if r > 0:
            ax.set_ylim(m - 0.05 * r, M + 0.05 * r)
        else:
            ax.set_ylim(m - 1.0, m + 1.0)
    else:
        pad = 0.05 * r if r > 0 else max(abs(m) * 0.05, 1e-6)
        ax.set_ylim(m - pad, M + pad)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Angle error (°)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")


def plot_error_comparison(t, truth, estimates, exclude=("gyro",), t_window=None, title="",
                          background=("accel",), shade=None) -> Figure:
    """Error (deg) of the estimates not in `exclude`; optional second axes zoomed on t_window.

    Keys in `background` are drawn first, faded and below the other lines; `shade` marks
    runs of True samples as disturbance spans.
    """
    if not isinstance(estimates, dict):
        raise ValueError("estimates must be a dict")
    if isinstance(exclude, str):
        exclude = (exclude,)
    if isinstance(background, str):
        background = (background,)
    t = np.asarray(t, dtype=np.float64)
    truth = np.asarray(truth, dtype=np.float64)
    if t.ndim != 1 or truth.shape != t.shape:
        raise ValueError("t and truth must be 1-D arrays of equal length")
    mask = _check_shade(shade, t)

    errors = {}
    for name, series in estimates.items():
        arr = np.asarray(series, dtype=np.float64)
        if arr.shape != t.shape:
            raise ValueError(f"estimate '{name}' length does not match t")
        if name not in exclude:
            errors[name] = np.rad2deg(arr - truth)
    if not errors:
        raise ValueError("no estimates to show")

    sel = None
    if t_window is not None:
        try:
            t0, t1 = (float(v) for v in t_window)
        except (TypeError, ValueError):
            raise ValueError("t_window must be a (t0, t1) pair") from None
        if not t0 < t1:
            raise ValueError("t_window requires t0 < t1")
        sel = (t >= t0) & (t <= t1)
        if not sel.any():
            raise ValueError("t_window contains no samples")

    bg = {k: v for k, v in errors.items() if k in background}
    fg = {k: v for k, v in errors.items() if k not in background}

    n_axes = 1 if sel is None else 2
    fig, axes = plt.subplots(n_axes, 1, squeeze=False, figsize=(10, 3.8 * n_axes))
    axes = axes[:, 0]
    _draw_error_axes(axes[0], t, bg, fg, t, mask)
    axes[0].set_title(title)
    if sel is not None:
        _draw_error_axes(axes[1], t[sel], {k: v[sel] for k, v in bg.items()},
                         {k: v[sel] for k, v in fg.items()}, t, mask)
        axes[1].set_xlim(t0, t1)
    fig.tight_layout()
    return fig


def plot_estimates(t, estimates, title="", shade=None) -> Figure:
    """Angle estimates (deg) for real data, where no truth exists. One axes."""
    if not isinstance(estimates, dict) or len(estimates) == 0:
        raise ValueError("estimates must be a non-empty dict")
    t = np.asarray(t, dtype=np.float64)
    if t.ndim != 1:
        raise ValueError("t must be 1-D")
    mask = _check_shade(shade, t)
    series = {}
    for name, values in estimates.items():
        arr = np.asarray(values, dtype=np.float64)
        if arr.shape != t.shape:
            raise ValueError(f"estimate '{name}' length does not match t")
        series[name] = arr

    fig, ax = plt.subplots(1, 1, figsize=(10, 4))
    for name, arr in series.items():
        ax.plot(t, np.rad2deg(arr), label=name, linewidth=1.0)
    _shade_spans(ax, t, mask)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Angle (°)")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    return fig


def plot_bias_estimate(t, bias_est, bias_std, bias_true=None, n_sigma=2.0, title="") -> Figure:
    """Gyro-bias estimate with a +/- n_sigma band, in deg/s. Does not call plt.show()."""
    t = np.asarray(t, dtype=np.float64)
    est = np.asarray(bias_est, dtype=np.float64)
    std = np.asarray(bias_std, dtype=np.float64)
    if t.ndim != 1 or est.shape != t.shape or std.shape != t.shape:
        raise ValueError("t, bias_est and bias_std must be 1-D arrays of equal length")
    truth = None
    if bias_true is not None:
        truth = np.asarray(bias_true, dtype=np.float64)
        if truth.shape != t.shape:
            raise ValueError("bias_true length does not match t")
    if np.any(std < 0):
        raise ValueError("bias_std must be >= 0")
    if not n_sigma > 0:
        raise ValueError("n_sigma must be > 0")

    fig, ax = plt.subplots(1, 1, figsize=(10, 4))
    lower = np.rad2deg(est - n_sigma * std)
    upper = np.rad2deg(est + n_sigma * std)
    ax.fill_between(t, lower, upper, alpha=0.25, color="tab:blue", linewidth=0,
                    label=f"±{n_sigma:g}σ")
    ax.plot(t, np.rad2deg(est), label="estimate", color="tab:blue", linewidth=1.2)
    if truth is not None:
        ax.plot(t, np.rad2deg(truth), label="truth", color="black", linewidth=1.2)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Gyro bias (°/s)")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    return fig
