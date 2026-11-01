"""Tier 2 spec 9.5 - new metrics (KM1, KM2) and new plots (KG1, KG2)."""
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pytest  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

import imu_metrics as M  # noqa: E402
import imu_plots  # noqa: E402
from tier2_helpers import run  # noqa: E402

EPS = 1e-9  # numeric slack for float comparisons of axis limits


# ---------------------------------------------------------------- KM1
T6 = np.arange(6, dtype=float)
E6 = np.array([0.5, 0.2, 0.05, 0.2, 0.01, 0.01])
ZERO6 = np.zeros(6)


def test_KM1_convergence_time_basic():
    assert M.convergence_time(T6, E6, ZERO6, tol=0.1) == 4.0


def test_KM1_all_within_tolerance_returns_first_time():
    assert M.convergence_time(T6, np.full(6, 0.01), ZERO6, tol=0.1) == T6[0]
    t = T6 + 2.0
    assert M.convergence_time(t, np.full(6, 0.01), ZERO6, tol=0.1) == 2.0


def test_KM1_last_sample_violating_returns_inf():
    e = E6.copy()
    e[-1] = 0.5
    r = M.convergence_time(T6, e, ZERO6, tol=0.1)
    assert r == math.inf


def test_KM1_t_start():
    assert M.convergence_time(T6, E6, ZERO6, tol=0.1, t_start=2.5) == 4.0
    e = E6.copy()
    e[3] = 0.05
    assert M.convergence_time(T6, e, ZERO6, tol=0.1, t_start=2.5) == 3.0


def test_KM1_extra_cases_from_the_definition():
    e = E6.copy()
    e[3] = 0.05
    assert M.convergence_time(T6, e, ZERO6, tol=0.1) == 2.0           # last violation at index 1
    assert M.convergence_time(T6, np.full(6, 0.1), ZERO6, tol=0.1) == 0.0   # |e| == tol is not a violation
    assert M.convergence_time(T6, -E6, ZERO6, tol=0.1) == 4.0         # sign of the error is irrelevant
    truth = np.sin(T6)
    assert M.convergence_time(T6, truth + E6, truth, tol=0.1) == 4.0  # error = estimate - truth
    assert M.convergence_time(T6, E6, ZERO6, tol=0.1, t_start=5.0) == 5.0  # one considered sample
    assert M.convergence_time(T6, E6, ZERO6, tol=0.1, t_start=2.0) == 4.0  # t_start is inclusive


@pytest.mark.parametrize("call", [
    lambda: M.convergence_time(T6, E6, ZERO6, tol=0.0),
    lambda: M.convergence_time(T6, E6, ZERO6, tol=-0.1),
    lambda: M.convergence_time(T6, E6, ZERO6, tol=0.1, t_start=5.5),
    lambda: M.convergence_time(T6, E6, ZERO6, tol=0.1, t_start=100.0),
    lambda: M.convergence_time(T6, E6, np.zeros(5), tol=0.1),
    lambda: M.convergence_time(T6[:5], E6, ZERO6, tol=0.1),
    lambda: M.convergence_time(np.array([]), np.array([]), np.array([]), tol=0.1),
    lambda: M.convergence_time(T6, np.array([0.5, np.nan, 0.05, 0.2, 0.01, 0.01]), ZERO6, tol=0.1),
    lambda: M.convergence_time(T6, E6, np.array([np.nan] + [0.0] * 5), tol=0.1),
], ids=["tol_zero", "tol_negative", "t_start_after_last", "t_start_far_after_last",
        "shape_truth", "shape_t", "empty", "nan_estimate", "nan_truth"])
def test_KM1_value_errors(call):
    with pytest.raises(ValueError):
        call()


# ---------------------------------------------------------------- KM2
def test_KM2_coverage_fraction_values():
    r = M.coverage_fraction(np.array([0.0, 1.0, 3.0]), np.zeros(3), np.ones(3))
    assert abs(r - 2 / 3) <= 1e-12
    assert M.coverage_fraction(np.array([2.0]), np.array([0.0]), np.array([1.0])) == 1.0  # inclusive


def test_KM2_extra_n_sigma_and_sign():
    est, truth, std = np.array([0.0, 1.0, 3.0]), np.zeros(3), np.ones(3)
    assert M.coverage_fraction(est, truth, std, n_sigma=3.0) == 1.0
    assert abs(M.coverage_fraction(est, truth, std, n_sigma=0.5) - 1 / 3) <= 1e-12
    assert abs(M.coverage_fraction(est, truth, std, n_sigma=1.0) - 2 / 3) <= 1e-12
    assert M.coverage_fraction(-est, truth, std, n_sigma=1.0) == pytest.approx(2 / 3, abs=1e-12)
    assert M.coverage_fraction(est, truth, np.zeros(3), n_sigma=2.0) == pytest.approx(1 / 3, abs=1e-12)


@pytest.mark.parametrize("call", [
    lambda: M.coverage_fraction(np.zeros(3), np.zeros(3), np.array([1.0, -1.0, 1.0])),
    lambda: M.coverage_fraction(np.zeros(3), np.zeros(3), np.ones(3), n_sigma=0.0),
    lambda: M.coverage_fraction(np.zeros(3), np.zeros(3), np.ones(3), n_sigma=-2.0),
    lambda: M.coverage_fraction(np.zeros(3), np.zeros(4), np.ones(3)),
    lambda: M.coverage_fraction(np.zeros(4), np.zeros(3), np.ones(3)),
    lambda: M.coverage_fraction(np.zeros(3), np.zeros(3), np.ones(4)),
    lambda: M.coverage_fraction(np.array([]), np.array([]), np.array([])),
    lambda: M.coverage_fraction(np.array([0, np.nan, 0.0]), np.zeros(3), np.ones(3)),
    lambda: M.coverage_fraction(np.zeros(3), np.array([0, np.nan, 0.0]), np.ones(3)),
    lambda: M.coverage_fraction(np.zeros(3), np.zeros(3), np.array([1.0, np.nan, 1.0])),
], ids=["std_negative", "n_sigma_zero", "n_sigma_negative", "shape_truth", "shape_estimate",
        "shape_std", "empty", "nan_estimate", "nan_truth", "nan_std"])
def test_KM2_value_errors(call):
    with pytest.raises(ValueError):
        call()


# ---------------------------------------------------------------- KG1
@pytest.fixture(scope="module")
def s1():
    r = run("S1", 0)
    ests = {"gyro": r.gyro, "accel": r.accel, "CF": r.cf, "KF": r.kf.angle}
    return r.t, r.truth, ests


def _check_ylim_rule(ax, ydata_list):
    y = np.concatenate([np.asarray(v, dtype=float) for v in ydata_list])
    m, big_m = y.min(), y.max()
    rng = big_m - m
    lo, hi = ax.get_ylim()
    assert lo >= m - 0.1 * rng - EPS, f"ylim low {lo} < {m - 0.1 * rng}"
    assert hi <= big_m + 0.1 * rng + EPS, f"ylim high {hi} > {big_m + 0.1 * rng}"


def test_KG1_default_exclude_no_window(s1):
    t, truth, ests = s1
    fig = imu_plots.plot_error_comparison(t, truth, ests, title="demo")
    assert isinstance(fig, Figure)
    assert len(fig.axes) == 1
    ax = fig.axes[0]
    assert [ln.get_label() for ln in ax.lines] == ["accel", "CF", "KF"]
    for ln, key in zip(ax.lines, ["accel", "CF", "KF"]):
        np.testing.assert_allclose(ln.get_xdata(), t, rtol=0, atol=1e-12)
        np.testing.assert_allclose(ln.get_ydata(), np.rad2deg(ests[key] - truth), rtol=0, atol=1e-9)
    assert ax.get_legend() is not None
    assert "°" in ax.get_ylabel()
    assert ax.get_xlabel().strip() != ""


def test_KG1_window_gives_second_axes(s1):
    t, truth, ests = s1
    fig = imu_plots.plot_error_comparison(t, truth, ests, t_window=(30, 40))
    assert len(fig.axes) == 2
    ax0, ax1 = fig.axes
    keys = ["accel", "CF", "KF"]
    assert [ln.get_label() for ln in ax0.lines] == keys
    assert [ln.get_label() for ln in ax1.lines] == keys
    lo, hi = ax1.get_xlim()
    assert abs(lo - 30.0) <= EPS and abs(hi - 40.0) <= EPS
    mask = (t >= 30) & (t <= 40)
    for ln, key in zip(ax1.lines, keys):
        x = np.asarray(ln.get_xdata(), dtype=float)
        assert x.min() >= 30.0 and x.max() <= 40.0
        np.testing.assert_allclose(x, t[mask], rtol=0, atol=1e-12)
        np.testing.assert_allclose(ln.get_ydata(), np.rad2deg(ests[key][mask] - truth[mask]),
                                   rtol=0, atol=1e-9)
    for ln, key in zip(ax0.lines, keys):  # axes 0 keeps the full range
        np.testing.assert_allclose(ln.get_xdata(), t, rtol=0, atol=1e-12)
    for ax in (ax0, ax1):
        assert ax.get_legend() is not None
        assert "°" in ax.get_ylabel()
    assert ax1.get_xlabel().strip() != ""


def test_KG1_ylim_rule_on_s1_data(s1):
    t, truth, ests = s1
    fig = imu_plots.plot_error_comparison(t, truth, ests, t_window=(30, 40))
    ax0, ax1 = fig.axes
    keys = ["accel", "CF", "KF"]
    _check_ylim_rule(ax0, [np.rad2deg(ests[k] - truth) for k in keys])
    mask = (t >= 30) & (t <= 40)
    _check_ylim_rule(ax1, [np.rad2deg(ests[k][mask] - truth[mask]) for k in keys])
    # the same rule without a window
    fig2 = imu_plots.plot_error_comparison(t, truth, ests)
    _check_ylim_rule(fig2.axes[0], [np.rad2deg(ests[k] - truth) for k in keys])


def test_KG1_exclude_empty_shows_all_four(s1):
    t, truth, ests = s1
    fig = imu_plots.plot_error_comparison(t, truth, ests, exclude=(), background=())  # Tier 3: keep insertion order
    assert len(fig.axes[0].lines) == 4
    assert [ln.get_label() for ln in fig.axes[0].lines] == ["gyro", "accel", "CF", "KF"]


def test_KG1_extra_exclude_rules_and_order(s1):
    t, truth, ests = s1
    fig = imu_plots.plot_error_comparison(t, truth, ests, exclude=("gyro", "nonexistent"))
    assert [ln.get_label() for ln in fig.axes[0].lines] == ["accel", "CF", "KF"]
    reordered = {"KF": ests["KF"], "CF": ests["CF"], "accel": ests["accel"], "gyro": ests["gyro"]}
    fig = imu_plots.plot_error_comparison(t, truth, reordered, background=())  # Tier 3: keep insertion order
    assert [ln.get_label() for ln in fig.axes[0].lines] == ["KF", "CF", "accel"]
    fig = imu_plots.plot_error_comparison(t, truth, ests, exclude=("gyro", "accel"))
    assert [ln.get_label() for ln in fig.axes[0].lines] == ["CF", "KF"]


def test_KG1_does_not_call_show(monkeypatch, s1):
    def boom(*a, **k):
        raise AssertionError("plt.show() must not be called")

    monkeypatch.setattr(plt, "show", boom)
    t, truth, ests = s1
    imu_plots.plot_error_comparison(t, truth, ests, t_window=(30, 40), title="x")


# ---------------------------------------------------------------- KG2
def _bias_data():
    t = np.arange(300) * 0.1
    rng = np.random.default_rng(3)
    truth = 0.01 + 0.002 * np.sin(0.3 * t)
    est = truth + rng.normal(0, 3e-4, t.size)
    std = np.abs(rng.normal(3e-4, 5e-5, t.size))
    return t, est, std, truth


def _band_vertices_y(ax):
    polys = [c for c in ax.collections if isinstance(c, PolyCollection)]
    assert len(polys) == 1, f"expected exactly one PolyCollection, found {len(polys)}"
    verts = np.concatenate([p.vertices for p in polys[0].get_paths()])
    return polys[0], verts[:, 1]


@pytest.mark.parametrize("n_sigma,label", [(None, "±2σ"), (3.0, "±3σ"), (2.5, "±2.5σ")])
def test_KG2_bias_plot_with_truth(n_sigma, label):
    t, est, std, truth = _bias_data()
    kwargs = {} if n_sigma is None else {"n_sigma": n_sigma}
    n = 2.0 if n_sigma is None else n_sigma
    fig = imu_plots.plot_bias_estimate(t, est, std, truth, title="demo", **kwargs)
    assert isinstance(fig, Figure)
    assert len(fig.axes) == 1
    ax = fig.axes[0]
    lines = {ln.get_label(): ln for ln in ax.lines}
    assert set(lines) == {"estimate", "truth"} and len(ax.lines) == 2
    np.testing.assert_allclose(lines["estimate"].get_ydata(), np.rad2deg(est), rtol=0, atol=1e-9)
    np.testing.assert_allclose(lines["truth"].get_ydata(), np.rad2deg(truth), rtol=0, atol=1e-9)
    for ln in lines.values():
        np.testing.assert_allclose(ln.get_xdata(), t, rtol=0, atol=1e-12)
    band, ys = _band_vertices_y(ax)
    lower, upper = np.rad2deg(est - n * std), np.rad2deg(est + n * std)
    assert abs(ys.min() - lower.min()) <= 1e-9
    assert abs(ys.max() - upper.max()) <= 1e-9
    assert band.get_label() == label
    assert ax.get_legend() is not None
    assert ax.get_xlabel().strip() != "" and ax.get_ylabel().strip() != ""


def test_KG2_bias_plot_without_truth():
    t, est, std, _ = _bias_data()
    fig = imu_plots.plot_bias_estimate(t, est, std)
    ax = fig.axes[0]
    assert len(fig.axes) == 1
    assert [ln.get_label() for ln in ax.lines] == ["estimate"]
    np.testing.assert_allclose(ax.lines[0].get_ydata(), np.rad2deg(est), rtol=0, atol=1e-9)
    band, ys = _band_vertices_y(ax)
    assert abs(ys.min() - np.rad2deg(est - 2.0 * std).min()) <= 1e-9
    assert abs(ys.max() - np.rad2deg(est + 2.0 * std).max()) <= 1e-9


def test_KG2_does_not_call_show(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("plt.show() must not be called")

    monkeypatch.setattr(plt, "show", boom)
    t, est, std, truth = _bias_data()
    imu_plots.plot_bias_estimate(t, est, std, truth, title="x")
