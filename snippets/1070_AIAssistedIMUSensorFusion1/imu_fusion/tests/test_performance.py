"""Spec 8.1 - statistical performance (P1-P8).

Every criterion must hold for EVERY listed seed (S1: 0-9, S2: 0-4), so each test is
parametrized over the seeds. All metrics are on pitch against pitch_true.
"""
import numpy as np
import pytest

import imu_metrics as M

B_Y = 0.01  # default gyro bias per spec 4.4

S1_SEEDS = list(range(10))
S2_SEEDS = list(range(5))


@pytest.mark.parametrize("seed", S1_SEEDS)
def test_P1_accel_rmse(s1_runs, seed):
    sim, est = s1_runs[seed]
    r = M.rmse(est["accel"], sim.pitch_true)
    ref = 0.05 / 9.81
    assert 0.8 * ref <= r <= 1.2 * ref, f"accel RMSE {np.rad2deg(r):.4f} deg"


@pytest.mark.parametrize("seed", S1_SEEDS)
def test_P2_gyro_final_error(s1_runs, seed):
    sim, est = s1_runs[seed]
    final_err = est["gyro"][-1] - sim.pitch_true[-1]
    assert abs(final_err - B_Y * sim.t[-1]) <= 0.03


@pytest.mark.parametrize("seed", S1_SEEDS)
def test_P3_gyro_rmse_large(s1_runs, seed):
    sim, est = s1_runs[seed]
    assert np.rad2deg(M.rmse(est["gyro"], sim.pitch_true)) > 10.0


@pytest.mark.parametrize("seed", S1_SEEDS)
def test_P4_cf_rmse(s1_runs, seed):
    sim, est = s1_runs[seed]
    assert np.rad2deg(M.rmse(est["cf"], sim.pitch_true)) <= 0.2


@pytest.mark.parametrize("seed", S1_SEEDS)
def test_P5_cf_beats_accel(s1_runs, seed):
    sim, est = s1_runs[seed]
    cf = M.rmse(est["cf"], sim.pitch_true)
    acc = M.rmse(est["accel"], sim.pitch_true)
    assert cf <= 0.7 * acc


@pytest.mark.parametrize("seed", S2_SEEDS)
def test_P6_gyro_drift_rate(s2_runs, seed):
    sim, est = s2_runs[seed]
    d = M.drift_rate(sim.t, est["gyro"], sim.pitch_true)
    assert abs(d - B_Y) <= 0.05 * B_Y


@pytest.mark.parametrize("seed", S2_SEEDS)
def test_P7_cf_and_accel_no_drift(s2_runs, seed):
    sim, est = s2_runs[seed]
    d_cf = M.drift_rate(sim.t, est["cf"], sim.pitch_true)
    d_acc = M.drift_rate(sim.t, est["accel"], sim.pitch_true)
    assert abs(d_cf) <= 1e-5
    assert abs(d_acc) <= 1e-5


@pytest.mark.parametrize("seed", S2_SEEDS)
def test_P8_cf_late_rmse(s2_runs, seed):
    sim, est = s2_runs[seed]
    mask = sim.t >= 540.0
    assert mask.any()
    r = M.rmse(est["cf"][mask], sim.pitch_true[mask])
    assert np.rad2deg(r) <= 0.2
