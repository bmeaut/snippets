"""Spec 8.3 - simulator statistics (N1-N5). S1, seed 0, biases known."""
import dataclasses

import numpy as np
import pytest

import imu_sim
import tier1_reference as ref

G = ref.G


@pytest.fixture(scope="module")
def sim0(s1_runs):
    return s1_runs[0][0]


def _gyro_resid(sim):
    _, rate = ref.true_pitch_and_rate(sim.t)
    expected = np.column_stack([np.zeros_like(rate), rate, np.zeros_like(rate)]) + sim.gyro_bias
    return sim.gyro - expected


def _accel_resid(sim):
    theta, _ = ref.true_pitch_and_rate(sim.t)
    expected = G * np.column_stack([-np.sin(theta), np.zeros_like(theta), np.cos(theta)])
    return sim.accel - expected


@pytest.mark.parametrize("axis", [0, 1, 2])
def test_N1_gyro_residual_statistics(sim0, axis):
    res = _gyro_resid(sim0)[:, axis]
    n = sim0.t.size
    assert abs(np.std(res) / 0.005 - 1.0) <= 0.05
    assert abs(np.mean(res)) <= 4 * 0.005 / np.sqrt(n)


@pytest.mark.parametrize("axis", [0, 1, 2])
def test_N2_accel_residual_statistics(sim0, axis):
    res = _accel_resid(sim0)[:, axis]
    n = sim0.t.size
    assert abs(np.std(res) / 0.05 - 1.0) <= 0.05
    assert abs(np.mean(res)) <= 4 * 0.05 / np.sqrt(n)


def test_N3_residuals_uncorrelated(sim0):
    cols = np.hstack([_gyro_resid(sim0), _accel_resid(sim0)])  # (N, 6)
    corr = np.corrcoef(cols.T)
    off = corr[~np.eye(6, dtype=bool)]
    assert np.all(np.abs(off) < 0.1)


def test_N4_time_axis_shapes_dtypes(sim0):
    s = sim0
    assert s.t.shape == (6000,)
    assert s.t[0] == 0
    np.testing.assert_allclose(np.diff(s.t), 0.01, rtol=0, atol=1e-12)
    shapes = {"t": (6000,), "gyro": (6000, 3), "accel": (6000, 3),
              "roll_true": (6000,), "pitch_true": (6000,), "gyro_bias": (3,)}
    for name, shape in shapes.items():
        arr = getattr(s, name)
        assert isinstance(arr, np.ndarray), name
        assert arr.shape == shape, name
        assert arr.dtype == np.float64, name
    assert np.all(s.roll_true == 0)
    assert isinstance(s.fs, (float, np.floating))
    assert float(s.fs) == 100.0


def test_N4_pitch_true_matches_default_trajectory(sim0):
    # extra (spec 4.2/4.3): ground truth pitch is the default trajectory
    theta, _ = ref.true_pitch_and_rate(sim0.t)
    np.testing.assert_allclose(sim0.pitch_true, theta, rtol=0, atol=1e-12)


def test_N4_simulatedimu_is_frozen_dataclass(sim0):
    # extra (spec 4.2)
    assert dataclasses.is_dataclass(sim0)
    assert type(sim0).__dataclass_params__.frozen is True
    # Tier 2 spec 4.3 appends gyro_bias_true, so the Tier 1 fields must be a subset
    assert {"t", "gyro", "accel", "roll_true", "pitch_true", "gyro_bias", "fs"} <= {
        f.name for f in dataclasses.fields(sim0)}
    assert imu_sim.GRAVITY == 9.81


def test_N5_determinism_and_seed_sensitivity():
    a = imu_sim.simulate_pitch_imu(seed=0)
    b = imu_sim.simulate_pitch_imu(seed=0)
    for name in ("t", "gyro", "accel", "roll_true", "pitch_true", "gyro_bias"):
        assert np.array_equal(getattr(a, name), getattr(b, name)), name
    c = imu_sim.simulate_pitch_imu(seed=1)
    assert not np.array_equal(a.gyro, c.gyro)
    assert not np.array_equal(a.accel, c.accel)
