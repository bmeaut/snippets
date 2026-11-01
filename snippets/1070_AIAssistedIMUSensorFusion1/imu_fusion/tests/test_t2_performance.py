"""Tier 2 spec 9.1 / 9.2 - statistical performance (KP1-KP9) and consistency (KC1).

Every criterion must hold for EVERY listed seed, so each test is parametrized over the
seeds of its scenario. Bias errors are against gyro_bias_true[:, 1]; angle errors are
against pitch_true. "RMSE over t >= X" uses the samples with t >= X.
"""
import numpy as np
import pytest

import imu_metrics as M
from tier2_helpers import SEEDS, run

B_Y = 0.01  # default bias of the y axis (S1, S2 have no random walk and no step)


def _rmse_from(r, x, est, truth):
    mask = r.t >= x
    assert mask.any()
    return M.rmse(est[mask], truth[mask])


@pytest.mark.parametrize("seed", SEEDS["S1"])
def test_KP1_kf_rmse_after_20s(seed):
    r = run("S1", seed)
    assert np.rad2deg(_rmse_from(r, 20.0, r.kf.angle, r.truth)) <= 0.06


@pytest.mark.parametrize("seed", SEEDS["S1"])
def test_KP2_kf_beats_cf(seed):
    r = run("S1", seed)
    kf = M.rmse(r.kf.angle, r.truth)
    cf = M.rmse(r.cf, r.truth)
    assert kf <= 0.6 * cf


@pytest.mark.parametrize("seed", SEEDS["S1"])
def test_KP3_kf_bias_error_after_20s(seed):
    r = run("S1", seed)
    mask = r.t >= 20.0
    assert np.max(np.abs(r.kf.bias[mask] - B_Y)) <= 1e-3


@pytest.mark.parametrize("seed", SEEDS["S1"])
def test_KP4_kf_max_error_after_20s(seed):
    r = run("S1", seed)
    mask = r.t >= 20.0
    assert np.rad2deg(M.max_abs_error(r.kf.angle[mask], r.truth[mask])) <= 0.2


@pytest.mark.parametrize("seed", SEEDS["S2"])
def test_KP5_kf_no_drift_long_run(seed):
    r = run("S2", seed)
    assert abs(M.drift_rate(r.t, r.kf.angle, r.truth)) <= 1e-5
    assert np.rad2deg(_rmse_from(r, 540.0, r.kf.angle, r.truth)) <= 0.06


@pytest.mark.parametrize("seed", SEEDS["S3"])
def test_KP6_kf_rmse_random_walk(seed):
    r = run("S3", seed)
    assert np.rad2deg(_rmse_from(r, 30.0, r.kf.angle, r.truth)) <= 0.06


@pytest.mark.parametrize("seed", SEEDS["S3"])
def test_KP7_kf_bias_rmse_random_walk(seed):
    r = run("S3", seed)
    assert _rmse_from(r, 30.0, r.kf.bias, r.bias_true) <= 5e-4


@pytest.mark.parametrize("seed", SEEDS["S4"])
def test_KP8_kf_bias_converges_after_step(seed):
    r = run("S4", seed)
    t_conv = M.convergence_time(r.t, r.kf.bias, r.bias_true, tol=1e-3, t_start=60.0)
    assert t_conv <= 90.0, f"bias settled at {t_conv} s"


@pytest.mark.parametrize("seed", SEEDS["S4"])
def test_KP9_kf_max_error_around_step(seed):
    r = run("S4", seed)
    mask = (r.t >= 60.0) & (r.t <= 90.0)
    assert mask.any()
    assert np.rad2deg(M.max_abs_error(r.kf.angle[mask], r.truth[mask])) <= 0.7


@pytest.mark.parametrize("seed", SEEDS["S3"])
def test_KC1_kf_bias_coverage(seed):
    r = run("S3", seed)
    mask = r.t >= 30.0
    std = np.sqrt(r.kf.cov[:, 1, 1])
    frac = M.coverage_fraction(r.kf.bias[mask], r.bias_true[mask], std[mask], 2.0)
    assert frac >= 0.90, f"coverage {frac:.3f}"
