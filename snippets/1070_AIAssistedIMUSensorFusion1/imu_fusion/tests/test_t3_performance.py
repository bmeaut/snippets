"""Tier 3 spec 11.1 / 11.2 - clean performance (RP1-RP3) and disturbances (RX1-RX5).

S6: simulate_roll_pitch_imu(), seeds 0-4.  S7: 150 s with the default segments, seeds 0-4.
Estimators are configured as in spec section 10 (rest window (0.0, 4.5)). Every criterion
must hold for every seed. Angles are compared in degrees where the spec states degrees.
"""
import numpy as np
import pytest

import imu_metrics as M
from tier3_helpers import (QUIET_INTERVALS, RECOVERY_WINDOWS, S6_SEEDS, S7_SEEDS, SEGMENT_ENDS,
                           interval_mask, sim_run)

ANGLES = ("roll", "pitch")


def _err(run, key, angle_index):
    return run.angles[key][angle_index], run.truth[angle_index]


def _rmse_deg(run, key, angle_index, mask):
    est, truth = _err(run, key, angle_index)
    return float(np.rad2deg(M.rmse(est[mask], truth[mask])))


def _max_disturbance_error_deg(run, key):
    """Maximum over both angles of max_abs_error restricted to disturbed_true samples."""
    mask = run.sim.disturbed_true
    assert mask.any()
    return max(float(np.rad2deg(M.max_abs_error(run.angles[key][i][mask], run.truth[i][mask])))
               for i in (0, 1))


# ---------------------------------------------------------------- RP1-RP3 (S6)
@pytest.mark.parametrize("seed", S6_SEEDS)
@pytest.mark.parametrize("key", ["KF", "KF-gated"])
@pytest.mark.parametrize("angle", [0, 1], ids=ANGLES)
def test_RP1_kf_rmse_clean(seed, key, angle):
    r = sim_run("S6", seed)
    assert _rmse_deg(r, key, angle, r.t >= 20.0) <= 0.08


@pytest.mark.parametrize("seed", S6_SEEDS)
@pytest.mark.parametrize("angle", [0, 1], ids=ANGLES)
def test_RP2_cf_rmse_clean(seed, angle):
    r = sim_run("S6", seed)
    assert _rmse_deg(r, "CF", angle, r.t >= 20.0) <= 0.15


@pytest.mark.parametrize("seed", S6_SEEDS)
def test_RP3_kf_bias_error_clean(seed):
    r = sim_run("S6", seed)
    m = r.t >= 20.0
    b = r.sim.gyro_bias
    assert np.max(np.abs(r.kf.bias_x[m] - b[0])) <= 1e-3
    assert np.max(np.abs(r.kf.bias_y[m] - b[1])) <= 1e-3


# ---------------------------------------------------------------- RX1-RX5 (S7)
@pytest.mark.parametrize("seed", S7_SEEDS)
def test_RX1_gated_kf_max_disturbance_error(seed):
    r = sim_run("S7", seed)
    assert _max_disturbance_error_deg(r, "KF-gated") <= 7.5


@pytest.mark.parametrize("seed", S7_SEEDS)
def test_RX2_gating_vs_ungated(seed):
    r = sim_run("S7", seed)
    gated = _max_disturbance_error_deg(r, "KF-gated")
    ungated = _max_disturbance_error_deg(r, "KF")
    assert gated <= 0.55 * ungated, "gated %.2f deg vs ungated %.2f deg" % (gated, ungated)


@pytest.mark.parametrize("seed", S7_SEEDS)
def test_RX3_gated_kf_vs_cf(seed):
    r = sim_run("S7", seed)
    gated = _max_disturbance_error_deg(r, "KF-gated")
    cf = _max_disturbance_error_deg(r, "CF")
    assert gated <= 0.4 * cf, "gated %.2f deg vs CF %.2f deg" % (gated, cf)


def _recovery_time(run, key, angle_index, window, segment_end):
    lo, hi, hi_inclusive = window
    mask = (run.t >= lo) & ((run.t <= hi) if hi_inclusive else (run.t < hi))
    est, truth = _err(run, key, angle_index)
    t_conv = M.convergence_time(run.t[mask], est[mask], truth[mask], tol=np.deg2rad(0.5))
    return t_conv - segment_end


@pytest.mark.parametrize("seed", S7_SEEDS)
@pytest.mark.parametrize("key,limit", [("KF", 10.0), ("KF-gated", 10.0), ("CF", 3.0)],
                         ids=["KF", "KF-gated", "CF"])
def test_RX4_recovery_time(seed, key, limit):
    r = sim_run("S7", seed)
    for window, end in zip(RECOVERY_WINDOWS, SEGMENT_ENDS):
        for angle_index, name in enumerate(ANGLES):
            rec = _recovery_time(r, key, angle_index, window, end)
            assert np.isfinite(rec), "%s %s never recovers in window %s" % (key, name, window[:2])
            assert rec <= limit, "%s %s recovery %.2f s after t=%g (limit %g s)" % (key, name, rec, end, limit)


@pytest.mark.parametrize("seed", S7_SEEDS)
@pytest.mark.parametrize("angle", [0, 1], ids=ANGLES)
def test_RX5_gated_kf_quiet_rmse(seed, angle):
    r = sim_run("S7", seed)
    quiet = interval_mask(r.t, QUIET_INTERVALS)
    assert quiet.any()
    assert not (quiet & r.sim.disturbed_true).any()      # the quiet intervals avoid every segment
    assert _rmse_deg(r, "KF-gated", angle, quiet) <= 0.08


def test_RX_extra_s7_segment_layout_matches_the_definitions():
    # the windows and segment ends used above are those implied by the default segments
    r = sim_run("S7", 0)
    d = r.sim.disturbed_true
    t = r.t
    for lo, hi in ((30.0, 32.0), (60.0, 62.0), (90.0, 95.0)):
        assert d[(t >= lo) & (t <= hi)].all()
    assert d.sum() == 201 + 201 + 501
    assert t.size == 15000 and t[-1] < 150.0
