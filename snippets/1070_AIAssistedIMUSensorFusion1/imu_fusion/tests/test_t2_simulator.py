"""Tier 2 spec 9.3 - simulator extension (KS1-KS6)."""
from pathlib import Path

import numpy as np
import pytest

import imu_sim
import tier1_reference as ref1

DATA = Path(__file__).resolve().parent / "data" / "tier1_reference.npz"
TIER1_FIELDS = ("t", "gyro", "accel", "roll_true", "pitch_true", "gyro_bias")
S3 = dict(duration=600.0, gyro_bias_rw_std=1e-4)


# ---------------------------------------------------------------- KS1
@pytest.fixture(scope="module")
def tier1_reference():
    if not DATA.exists():
        pytest.fail(
            f"KS1 fixture {DATA} is missing. The owner must run "
            "`python tests/make_tier1_reference.py` on the Tier 1 code BEFORE installing "
            "any Tier 2 change (see tier2_spec.md 9.3, KS1).", pytrace=False)
    with np.load(DATA) as npz:
        return {k: npz[k] for k in npz.files}


@pytest.mark.parametrize("seed", [0, 3])
@pytest.mark.parametrize("field", TIER1_FIELDS)
def test_KS1_regression_tier1_output_bit_identical(tier1_reference, seed, field):
    key = f"seed{seed}_{field}"
    assert key in tier1_reference, f"{key} missing from {DATA.name}"
    sim = imu_sim.simulate_pitch_imu(seed=seed)
    got = np.asarray(getattr(sim, field))
    assert got.shape == tier1_reference[key].shape
    assert np.array_equal(got, tier1_reference[key]), f"{field} differs from the Tier 1 release"


@pytest.mark.parametrize("seed", [0, 3])
def test_KS1_gyro_bias_true_rows_equal_gyro_bias(seed):
    sim = imu_sim.simulate_pitch_imu(seed=seed)
    assert sim.gyro_bias_true.shape == (sim.t.size, 3)
    assert np.all(sim.gyro_bias_true == sim.gyro_bias)  # every row, exactly


# ---------------------------------------------------------------- KS2
@pytest.fixture(scope="module")
def s3_seed0():
    return imu_sim.simulate_pitch_imu(seed=0, **S3)


def test_KS2_initial_bias_equals_gyro_bias(s3_seed0):
    assert np.array_equal(s3_seed0.gyro_bias_true[0], s3_seed0.gyro_bias)


@pytest.mark.parametrize("axis", [0, 1, 2])
def test_KS2_random_walk_increment_statistics(s3_seed0, axis):
    d = np.diff(s3_seed0.gyro_bias_true[:, axis])
    n_minus_1 = d.size
    assert abs(np.std(d) / 1e-5 - 1.0) <= 0.05          # 1e-4 * sqrt(0.01)
    assert abs(np.mean(d)) <= 4 * 1e-5 / np.sqrt(n_minus_1)


def test_KS2_random_walk_increments_uncorrelated(s3_seed0):
    d = np.diff(s3_seed0.gyro_bias_true, axis=0)  # (N-1, 3)
    corr = np.corrcoef(d.T)
    off = corr[~np.eye(3, dtype=bool)]
    assert np.all(np.abs(off) < 0.1)


@pytest.mark.parametrize("axis", [0, 1, 2])
def test_KS2_gyro_residual_std(s3_seed0, axis):
    s = s3_seed0
    _, rate = ref1.true_pitch_and_rate(s.t)
    true_rate = np.column_stack([np.zeros_like(rate), rate, np.zeros_like(rate)])
    resid = s.gyro - true_rate - s.gyro_bias_true
    assert abs(np.std(resid[:, axis]) / 0.005 - 1.0) <= 0.05


# ---------------------------------------------------------------- KS3
def test_KS3_bias_step():
    sim = imu_sim.simulate_pitch_imu(bias_step=(30.0, 0.01), seed=0)
    b_y, delta = 0.01, 0.01
    before = sim.t < 30.0
    after = sim.t >= 30.0
    assert before.any() and after.any()
    np.testing.assert_allclose(sim.gyro_bias_true[before, 1], b_y, rtol=0, atol=1e-15)
    np.testing.assert_allclose(sim.gyro_bias_true[after, 1], b_y + delta, rtol=0, atol=1e-15)
    for axis in (0, 2):
        np.testing.assert_allclose(sim.gyro_bias_true[:, axis], 0.01, rtol=0, atol=1e-15)


def test_KS3_step_with_non_default_bias():
    sim = imu_sim.simulate_pitch_imu(gyro_bias=(0.01, -0.02, 0.03), bias_step=(30.0, 0.01), seed=0)
    np.testing.assert_allclose(sim.gyro_bias_true[sim.t < 30.0, 1], -0.02, rtol=0, atol=1e-15)
    np.testing.assert_allclose(sim.gyro_bias_true[sim.t >= 30.0, 1], -0.02 + 0.01, rtol=0, atol=1e-15)
    np.testing.assert_allclose(sim.gyro_bias_true[:, 0], 0.01, rtol=0, atol=1e-15)
    np.testing.assert_allclose(sim.gyro_bias_true[:, 2], 0.03, rtol=0, atol=1e-15)


@pytest.mark.parametrize("t_step,expect_step", [(-10.0, True), (0.0, True), (1e6, False)])
def test_KS3_step_time_outside_or_at_edge_is_allowed(t_step, expect_step):
    # spec 4.5: t_step outside [t[0], t[-1]] is allowed (applies to every sample or none)
    sim = imu_sim.simulate_pitch_imu(duration=10.0, bias_step=(t_step, 0.01), seed=0)
    want = 0.01 + (0.01 if expect_step else 0.0)
    np.testing.assert_allclose(sim.gyro_bias_true[:, 1], want, rtol=0, atol=1e-15)


def test_KS3_step_accepts_list():
    sim = imu_sim.simulate_pitch_imu(duration=10.0, bias_step=[5.0, 0.01], seed=0)
    assert sim.gyro_bias_true[sim.t >= 5.0, 1][0] == pytest.approx(0.02, abs=1e-15)


def test_KS3_extra_step_consumes_no_random_numbers():
    a = imu_sim.simulate_pitch_imu(duration=20.0, seed=5)
    b = imu_sim.simulate_pitch_imu(duration=20.0, bias_step=(10.0, 0.01), seed=5)
    assert np.array_equal(a.accel, b.accel)
    np.testing.assert_allclose(b.gyro - b.gyro_bias_true, a.gyro - a.gyro_bias_true, rtol=0, atol=1e-12)


# ---------------------------------------------------------------- KS4
def test_KS4_noise_free_model():
    sim = imu_sim.simulate_pitch_imu(gyro_noise_std=0.0, accel_noise_std=0.0,
                                     gyro_bias_rw_std=1e-4, bias_step=(30.0, 0.01), seed=0)
    _, rate = ref1.true_pitch_and_rate(sim.t)
    np.testing.assert_allclose(sim.gyro[:, 1], rate + sim.gyro_bias_true[:, 1], rtol=0, atol=1e-12)
    np.testing.assert_allclose(sim.gyro[:, 0], sim.gyro_bias_true[:, 0], rtol=0, atol=1e-12)
    np.testing.assert_allclose(sim.gyro[:, 2], sim.gyro_bias_true[:, 2], rtol=0, atol=1e-12)


# ---------------------------------------------------------------- KS5
def test_KS5_determinism_and_seed_sensitivity():
    a = imu_sim.simulate_pitch_imu(seed=0, **S3)
    b = imu_sim.simulate_pitch_imu(seed=0, **S3)
    assert np.array_equal(a.gyro_bias_true, b.gyro_bias_true)
    assert np.array_equal(a.gyro, b.gyro)
    c = imu_sim.simulate_pitch_imu(seed=1, **S3)
    assert not np.array_equal(a.gyro_bias_true, c.gyro_bias_true)


def test_KS5_extra_random_walk_draws_come_after_tier1_draws():
    # spec 4.4: the random-walk draws follow all Tier 1 draws, so the Tier 1 noise is unchanged
    a = imu_sim.simulate_pitch_imu(duration=20.0, seed=7)
    b = imu_sim.simulate_pitch_imu(duration=20.0, seed=7, gyro_bias_rw_std=1e-4)
    assert np.array_equal(a.accel, b.accel)
    np.testing.assert_allclose(b.gyro - b.gyro_bias_true, a.gyro - a.gyro_bias_true, rtol=0, atol=1e-12)


# ---------------------------------------------------------------- KS6
KS6_CASES = {
    "rw_negative": dict(gyro_bias_rw_std=-1e-4),
    "rw_tiny_negative": dict(gyro_bias_rw_std=-1e-12),
    "step_length_1": dict(bias_step=(30.0,)),
    "step_length_3": dict(bias_step=(30.0, 0.01, 1.0)),
    "step_empty": dict(bias_step=()),
    "step_scalar": dict(bias_step=30.0),
    "step_nan_time": dict(bias_step=(float("nan"), 0.01)),
    "step_nan_delta": dict(bias_step=(30.0, float("nan"))),
    "step_inf_time": dict(bias_step=(float("inf"), 0.01)),
    "step_inf_delta": dict(bias_step=(30.0, float("-inf"))),
    "step_non_numeric": dict(bias_step=("a", "b")),
}


@pytest.mark.parametrize("kwargs", list(KS6_CASES.values()), ids=list(KS6_CASES))
def test_KS6_value_errors(kwargs):
    with pytest.raises(ValueError):
        imu_sim.simulate_pitch_imu(duration=10.0, seed=0, **kwargs)


def test_KS6_zero_random_walk_and_step_none_are_accepted():
    sim = imu_sim.simulate_pitch_imu(duration=1.0, gyro_bias_rw_std=0.0, bias_step=None, seed=0)
    assert sim.gyro_bias_true.shape == (100, 3)
