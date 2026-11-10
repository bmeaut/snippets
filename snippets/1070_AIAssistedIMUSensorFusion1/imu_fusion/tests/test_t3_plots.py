"""Tier 3 spec 11.7 - plots (RG1, RG2)."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pytest  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.patches import Polygon, Rectangle  # noqa: E402

import imu_plots  # noqa: E402
from tier3_helpers import sim_run  # noqa: E402

EPS = 1e-9
S7_SPANS = [(30.0, 32.0), (60.0, 62.0), (90.0, 95.0)]    # the maximal True runs of disturbed_true in S7


@pytest.fixture(scope="module")
def s7():
    r = sim_run("S7", 0)
    roll_truth = r.truth[0]
    estimates = {
        "gyro": roll_truth + 0.01 * r.t,                  # a drifting stand-in for gyro integration
        "accel": r.angles["accel"][0],
        "CF": r.angles["CF"][0],
        "KF": r.angles["KF"][0],
    }
    return r.t, roll_truth, estimates, r.sim.disturbed_true


def _spans(ax):
    """(x0, x1, alpha, label) of every axvspan-like patch on `ax`."""
    out = []
    for p in ax.patches:
        if isinstance(p, Rectangle):
            x0, x1 = p.get_x(), p.get_x() + p.get_width()
        elif isinstance(p, Polygon):
            xs = np.asarray(p.get_xy())[:, 0]
            x0, x1 = xs.min(), xs.max()
        else:
            continue
        out.append((min(x0, x1), max(x0, x1), p.get_alpha(), p.get_label()))
    return out


def _legend_texts(ax):
    leg = ax.get_legend()
    return [] if leg is None else [t.get_text() for t in leg.get_texts()]


def _check_ylim(ax, foreground_y, all_y):
    """Spec 9.1 y-limit rule."""
    lo, hi = ax.get_ylim()
    if foreground_y:
        y = np.concatenate(foreground_y)
        m, big_m = y.min(), y.max()
        r = big_m - m
        if r > 0:
            assert lo <= m + EPS and hi >= big_m - EPS, "limits must contain the foreground data"
            assert lo >= m - 0.1 * r - EPS and hi <= big_m + 0.1 * r + EPS
        else:
            assert abs(lo - (m - 1.0)) <= EPS and abs(hi - (m + 1.0)) <= EPS
    else:
        y = np.concatenate(all_y)
        m, big_m = y.min(), y.max()
        r = big_m - m
        assert lo >= m - 0.1 * r - EPS and hi <= big_m + 0.1 * r + EPS


# ---------------------------------------------------------------- RG1
def test_RG1_background_line_is_first_faint_and_below_the_foreground(s7):
    t, truth, ests, _ = s7
    fig = imu_plots.plot_error_comparison(t, truth, ests)
    assert isinstance(fig, Figure) and len(fig.axes) == 1
    ax = fig.axes[0]
    labels = [ln.get_label() for ln in ax.lines]
    assert labels == ["accel", "CF", "KF"]                 # gyro excluded; accel drawn first
    accel_line, cf_line, kf_line = ax.lines
    assert accel_line.get_alpha() is not None and accel_line.get_alpha() <= 0.4
    assert accel_line.get_zorder() < cf_line.get_zorder()
    assert accel_line.get_zorder() < kf_line.get_zorder()
    for ln in (cf_line, kf_line):
        assert ln.get_alpha() is None or ln.get_alpha() == 1
    np.testing.assert_allclose(accel_line.get_ydata(), np.rad2deg(ests["accel"] - truth), rtol=0, atol=EPS)


def test_RG1_background_line_is_drawn_first_even_if_listed_last(s7):
    t, truth, ests, _ = s7
    reordered = {"KF": ests["KF"], "CF": ests["CF"], "accel": ests["accel"], "gyro": ests["gyro"]}
    fig = imu_plots.plot_error_comparison(t, truth, reordered)
    ax = fig.axes[0]
    assert ax.lines[0].get_label() == "accel"
    assert [ln.get_label() for ln in ax.lines[1:]] == ["KF", "CF"]    # the foreground keeps insertion order


def test_RG1_ylim_rule_on_s7_data(s7):
    t, truth, ests, _ = s7
    err = {k: np.rad2deg(v - truth) for k, v in ests.items()}
    fig = imu_plots.plot_error_comparison(t, truth, ests)
    _check_ylim(fig.axes[0], [err["CF"], err["KF"]], [err["accel"], err["CF"], err["KF"]])
    # the background noise is wider than the foreground, so the rule is not vacuous
    assert np.ptp(err["accel"]) > np.ptp(err["KF"])
    fig = imu_plots.plot_error_comparison(t, truth, ests, t_window=(28, 40))
    assert len(fig.axes) == 2
    mask = (t >= 28) & (t <= 40)
    _check_ylim(fig.axes[0], [err["CF"], err["KF"]], [])
    _check_ylim(fig.axes[1], [err["CF"][mask], err["KF"][mask]], [])
    lo, hi = fig.axes[1].get_xlim()
    assert abs(lo - 28.0) <= EPS and abs(hi - 40.0) <= EPS


def test_RG1_background_empty_gives_plain_lines(s7):
    t, truth, ests, _ = s7
    fig = imu_plots.plot_error_comparison(t, truth, ests, background=())
    ax = fig.axes[0]
    assert [ln.get_label() for ln in ax.lines] == ["accel", "CF", "KF"]
    for ln in ax.lines:
        assert ln.get_alpha() is None or ln.get_alpha() == 1
    err = {k: np.rad2deg(v - truth) for k, v in ests.items()}
    _check_ylim(ax, [err["accel"], err["CF"], err["KF"]], [])


def test_RG1_key_in_both_exclude_and_background_is_excluded(s7):
    t, truth, ests, _ = s7
    fig = imu_plots.plot_error_comparison(t, truth, ests, exclude=("gyro", "accel"), background=("accel",))
    assert [ln.get_label() for ln in fig.axes[0].lines] == ["CF", "KF"]
    fig = imu_plots.plot_error_comparison(t, truth, ests, exclude=(), background=("accel", "gyro"))
    ax = fig.axes[0]
    assert [ln.get_label() for ln in ax.lines[:2]] == ["gyro", "accel"] or \
        [ln.get_label() for ln in ax.lines[:2]] == ["accel", "gyro"]
    assert [ln.get_label() for ln in ax.lines[2:]] == ["CF", "KF"]
    for ln in ax.lines[:2]:
        assert ln.get_alpha() is not None and ln.get_alpha() <= 0.4


def test_RG1_shading_with_disturbed_true(s7):
    t, truth, ests, disturbed = s7
    fig = imu_plots.plot_error_comparison(t, truth, ests, shade=disturbed)
    ax = fig.axes[0]
    spans = _spans(ax)
    assert len(spans) == 3
    for (x0, x1, alpha, label), (e0, e1) in zip(sorted(spans), S7_SPANS):
        assert abs(x0 - e0) <= EPS and abs(x1 - e1) <= EPS
        assert alpha is not None and alpha <= 0.3
    assert [s[3] for s in sorted(spans)].count("disturbance") == 1
    assert _legend_texts(ax).count("disturbance") == 1
    # the lines are unchanged by the shading
    assert [ln.get_label() for ln in ax.lines] == ["accel", "CF", "KF"]


def test_RG1_shading_every_axes_gets_the_spans(s7):
    t, truth, ests, disturbed = s7
    fig = imu_plots.plot_error_comparison(t, truth, ests, t_window=(28, 40), shade=disturbed)
    assert len(fig.axes) == 2
    for ax in fig.axes:
        assert len(_spans(ax)) == 3
    assert _legend_texts(fig.axes[0]).count("disturbance") == 1
    lo, hi = fig.axes[1].get_xlim()
    assert abs(lo - 28.0) <= EPS and abs(hi - 40.0) <= EPS
    err = {k: np.rad2deg(v - truth) for k, v in ests.items()}
    mask = (t >= 28) & (t <= 40)
    _check_ylim(fig.axes[0], [err["CF"], err["KF"]], [])
    _check_ylim(fig.axes[1], [err["CF"][mask], err["KF"][mask]], [])


def test_RG1_no_shade_means_no_spans(s7):
    t, truth, ests, _ = s7
    for kwargs in ({}, {"shade": None}, {"t_window": (28, 40)}):
        fig = imu_plots.plot_error_comparison(t, truth, ests, **kwargs)
        for ax in fig.axes:
            assert len(_spans(ax)) == 0
            assert "disturbance" not in _legend_texts(ax)


def test_RG1_extra_shade_runs_all_false_all_true_and_edges(s7):
    t, truth, ests, _ = s7
    none = np.zeros(t.shape, dtype=bool)
    assert len(_spans(imu_plots.plot_error_comparison(t, truth, ests, shade=none).axes[0])) == 0
    everything = np.ones(t.shape, dtype=bool)
    spans = _spans(imu_plots.plot_error_comparison(t, truth, ests, shade=everything).axes[0])
    assert len(spans) == 1 and abs(spans[0][0] - t[0]) <= EPS and abs(spans[0][1] - t[-1]) <= EPS
    mask = np.zeros(t.shape, dtype=bool)
    mask[[10, 11, 12, 100, 14000, 14001]] = True          # three runs, one of them a single sample pair
    spans = sorted(_spans(imu_plots.plot_error_comparison(t, truth, ests, shade=mask).axes[0]))
    assert len(spans) == 3
    expected = [(t[10], t[12]), (t[100], t[100]), (t[14000], t[14001])]
    for (x0, x1, _, _), (e0, e1) in zip(spans, expected):
        assert abs(x0 - e0) <= EPS and abs(x1 - e1) <= EPS    # axvspan(t[i], t[j]); i == j gives zero width


def test_RG1_extra_constant_foreground_gets_unit_margin(s7):
    t, truth, ests, _ = s7
    zero_truth = np.zeros_like(truth)                    # exactly constant error: r_f == 0 in floating point
    c = np.deg2rad(0.3)
    flat = {"accel": ests["accel"], "KF": np.full_like(truth, c)}
    fig = imu_plots.plot_error_comparison(t, zero_truth, flat)
    lo, hi = fig.axes[0].get_ylim()
    m = float(np.rad2deg(c))
    assert abs(lo - (m - 1.0)) <= EPS and abs(hi - (m + 1.0)) <= EPS


def test_RG1_extra_only_background_keys_use_the_tier2_rule(s7):
    t, truth, ests, _ = s7
    fig = imu_plots.plot_error_comparison(t, truth, {"accel": ests["accel"]})
    ax = fig.axes[0]
    assert [ln.get_label() for ln in ax.lines] == ["accel"]
    _check_ylim(ax, [], [np.rad2deg(ests["accel"] - truth)])


def test_RG1_extra_labels_legend_and_show(s7, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("plt.show() must not be called")

    monkeypatch.setattr(plt, "show", boom)
    t, truth, ests, disturbed = s7
    fig = imu_plots.plot_error_comparison(t, truth, ests, shade=disturbed, t_window=(28, 40), title="x")
    for ax in fig.axes:
        assert ax.get_legend() is not None
        assert "°" in ax.get_ylabel()
    assert fig.axes[-1].get_xlabel().strip() != ""


@pytest.mark.parametrize("bad_shade", [
    np.zeros(14999, dtype=bool), np.zeros(15001, dtype=bool), np.zeros((15000, 1), dtype=bool),
    np.zeros((2, 15000), dtype=bool)], ids=["short", "long", "column", "2d"])
def test_RG1_shade_with_wrong_shape_raises(s7, bad_shade):
    t, truth, ests, _ = s7
    with pytest.raises(ValueError):
        imu_plots.plot_error_comparison(t, truth, ests, shade=bad_shade)


# ---------------------------------------------------------------- RG2
@pytest.fixture(scope="module")
def estimates_real_like():
    r = sim_run("S7", 0)
    ests = {"CF": r.angles["CF"][1], "KF": r.angles["KF"][1], "KF-gated": r.angles["KF-gated"][1]}
    return r.t, ests, r.sim.disturbed_true


def test_RG2_plot_estimates_structure_and_data(estimates_real_like):
    t, ests, _ = estimates_real_like
    fig = imu_plots.plot_estimates(t, ests, title="demo")
    assert isinstance(fig, Figure) and len(fig.axes) == 1
    ax = fig.axes[0]
    assert [ln.get_label() for ln in ax.lines] == ["CF", "KF", "KF-gated"]
    for ln, key in zip(ax.lines, ests):
        np.testing.assert_allclose(ln.get_ydata(), np.rad2deg(ests[key]), rtol=0, atol=EPS)
        np.testing.assert_allclose(ln.get_xdata(), t, rtol=0, atol=1e-12)
    assert "°" in ax.get_ylabel()
    assert ax.get_legend() is not None
    assert ax.get_xlabel().strip() != ""
    assert len(_spans(ax)) == 0


def test_RG2_plot_estimates_shading(estimates_real_like):
    t, ests, disturbed = estimates_real_like
    fig = imu_plots.plot_estimates(t, ests, shade=disturbed)
    ax = fig.axes[0]
    spans = sorted(_spans(ax))
    assert len(spans) == 3
    for (x0, x1, alpha, _), (e0, e1) in zip(spans, S7_SPANS):
        assert abs(x0 - e0) <= EPS and abs(x1 - e1) <= EPS and alpha is not None and alpha <= 0.3
    assert [s[3] for s in spans].count("disturbance") == 1
    assert _legend_texts(ax).count("disturbance") == 1
    assert [ln.get_label() for ln in ax.lines] == ["CF", "KF", "KF-gated"]
    assert len(_spans(imu_plots.plot_estimates(t, ests, shade=None).axes[0])) == 0


def test_RG2_plot_estimates_does_not_call_show(estimates_real_like, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("plt.show() must not be called")

    monkeypatch.setattr(plt, "show", boom)
    t, ests, disturbed = estimates_real_like
    imu_plots.plot_estimates(t, ests, title="x", shade=disturbed)


def test_RG2_plot_estimates_errors(estimates_real_like):
    t, ests, _ = estimates_real_like
    n = t.size
    P = imu_plots.plot_estimates
    with pytest.raises(ValueError):
        P(t, {})
    with pytest.raises(ValueError):
        P(t[:-1], ests)
    with pytest.raises(ValueError):
        P(t, {"KF": ests["KF"][:-1]})
    with pytest.raises(ValueError):
        P(t, {"CF": ests["CF"], "KF": ests["KF"][:-1]})
    for bad in (np.zeros(n - 1, dtype=bool), np.zeros(n + 1, dtype=bool), np.zeros((n, 1), dtype=bool)):
        with pytest.raises(ValueError):
            P(t, ests, shade=bad)
