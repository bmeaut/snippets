"""Spec 8.2 - deterministic correctness (D1-D8). Noise-free where stated."""
import numpy as np
import pytest

import imu_filters as F
import imu_sim
import tier1_reference as ref

G = ref.G


def _noise_free(**kw):
    return imu_sim.simulate_pitch_imu(gyro_noise_std=0.0, accel_noise_std=0.0, **kw)


# ---------------------------------------------------------------- D1
def test_D1_noise_free_simulator_model():
    bias = (0.01, -0.02, 0.03)
    sim = _noise_free(gyro_bias=bias, seed=0)
    theta, rate = ref.true_pitch_and_rate(sim.t)
    np.testing.assert_allclose(sim.gyro[:, 0], 0.01, rtol=0, atol=1e-12)
    np.testing.assert_allclose(sim.gyro[:, 1], rate + (-0.02), rtol=0, atol=1e-12)
    np.testing.assert_allclose(sim.gyro[:, 2], 0.03, rtol=0, atol=1e-12)
    expected_acc = G * np.column_stack([-np.sin(theta), np.zeros_like(theta), np.cos(theta)])
    np.testing.assert_allclose(sim.accel, expected_acc, rtol=0, atol=1e-12)
    np.testing.assert_allclose(sim.gyro_bias, bias, rtol=0, atol=1e-12)


# ---------------------------------------------------------------- D2
def test_D2_accel_tilt_recovers_truth():
    sim = _noise_free(gyro_bias=(0.01, -0.02, 0.03), seed=0)
    roll, pitch = F.accel_tilt(sim.accel)
    np.testing.assert_allclose(pitch, sim.pitch_true, rtol=0, atol=1e-9)
    np.testing.assert_allclose(roll, 0.0, rtol=0, atol=1e-9)


# ---------------------------------------------------------------- D3
_s30, _c30 = np.sin(np.deg2rad(30)), np.cos(np.deg2rad(30))
_s20, _c20 = np.sin(np.deg2rad(20)), np.cos(np.deg2rad(20))
D3_CASES = [
    ((0.0, 0.0, G), (0.0, 0.0)),
    ((0.0, G, 0.0), (90.0, 0.0)),
    ((-G * _s30, 0.0, G * _c30), (0.0, 30.0)),
    ((0.0, G * _s20, G * _c20), (20.0, 0.0)),
    ((-G * _s30, G * _s20 * _c30, G * _c20 * _c30), (20.0, 30.0)),
]


@pytest.mark.parametrize("scale", [1.0, 0.5, 3.0])
@pytest.mark.parametrize("vec,expected_deg", D3_CASES)
def test_D3_accel_tilt_reference_vectors(vec, expected_deg, scale):
    acc = scale * np.array([vec], dtype=np.float64)
    roll, pitch = F.accel_tilt(acc)
    assert roll.shape == (1,) and pitch.shape == (1,)
    assert abs(roll[0] - np.deg2rad(expected_deg[0])) <= 1e-9
    assert abs(pitch[0] - np.deg2rad(expected_deg[1])) <= 1e-9


def test_D3_accel_tilt_reference_vectors_batched():
    acc = np.array([v for v, _ in D3_CASES], dtype=np.float64)
    exp = np.deg2rad(np.array([e for _, e in D3_CASES]))
    for scale in (1.0, 0.5, 3.0):
        roll, pitch = F.accel_tilt(scale * acc)
        np.testing.assert_allclose(roll, exp[:, 0], rtol=0, atol=1e-9)
        np.testing.assert_allclose(pitch, exp[:, 1], rtol=0, atol=1e-9)


# ---------------------------------------------------------------- D4
def test_D4_gyro_integrate_constant_rate_nonuniform():
    rng = np.random.default_rng(4)
    t = 2.5 + np.cumsum(rng.uniform(0.001, 0.05, 200))  # non-uniform, t[0] != 0
    r, a0 = 0.37, -0.4
    out = F.gyro_integrate(t, np.full(t.shape, r), a0)
    np.testing.assert_allclose(out, a0 + r * (t - t[0]), rtol=0, atol=1e-12)
    out_default = F.gyro_integrate(t, np.full(t.shape, r))
    np.testing.assert_allclose(out_default, r * (t - t[0]), rtol=0, atol=1e-12)


# ---------------------------------------------------------------- D5
def _random_inputs(seed):
    rng = np.random.default_rng(1000 + seed)
    n = int(rng.integers(50, 400))
    dt = rng.uniform(0.002, 0.05, n - 1)
    t = rng.uniform(-3, 3) + np.concatenate([[0.0], np.cumsum(dt)])
    rate = rng.normal(0.0, 1.0, n)
    acc_angle = rng.normal(0.0, 0.5, n)
    return t, rate, acc_angle


@pytest.mark.parametrize("seed", range(5))
@pytest.mark.parametrize("initial", [0.0, 0.37, -1.2])
def test_D5_gyro_integrate_matches_recurrence(seed, initial):
    t, rate, _ = _random_inputs(seed)
    np.testing.assert_allclose(
        F.gyro_integrate(t, rate, initial), ref.ref_gyro_integrate(t, rate, initial),
        rtol=0, atol=1e-12)


@pytest.mark.parametrize("seed", range(5))
@pytest.mark.parametrize("tau", [0.05, 0.2, 1.0, 5.0])
@pytest.mark.parametrize("initial", [None, 0.37])
def test_D5_complementary_filter_matches_recurrence(seed, tau, initial):
    t, rate, acc_angle = _random_inputs(seed)
    got = F.complementary_filter(t, rate, acc_angle, tau=tau, initial_angle=initial)
    want = ref.ref_complementary(t, rate, acc_angle, tau=tau, initial_angle=initial)
    np.testing.assert_allclose(got, want, rtol=0, atol=1e-12)


def test_D5_complementary_filter_default_tau_is_0_2():
    t, rate, acc_angle = _random_inputs(99)
    got = F.complementary_filter(t, rate, acc_angle)
    want = ref.ref_complementary(t, rate, acc_angle, tau=0.2)
    np.testing.assert_allclose(got, want, rtol=0, atol=1e-12)


# ---------------------------------------------------------------- D6
def test_D6_cf_steady_state_error_is_by_times_tau():
    b_y, tau = 0.01, 0.2
    sim = _noise_free(duration=60.0, trajectory=imu_sim.constant_pitch_trajectory(0.3),
                      gyro_bias=(0.0, b_y, 0.0), seed=0)
    accel_pitch = F.accel_tilt(sim.accel)[1]
    cf = F.complementary_filter(sim.t, sim.gyro[:, 1], accel_pitch, tau=tau)
    final_error = cf[-1] - sim.pitch_true[-1]
    assert abs(final_error - b_y * tau) <= 1e-6


def test_D6_cf_steady_state_with_default_bias():
    # spec D6 states b_y = 0.01, which is also the default bias on every axis
    sim = _noise_free(duration=60.0, trajectory=imu_sim.constant_pitch_trajectory(0.3), seed=0)
    accel_pitch = F.accel_tilt(sim.accel)[1]
    cf = F.complementary_filter(sim.t, sim.gyro[:, 1], accel_pitch, tau=0.2)
    assert abs((cf[-1] - sim.pitch_true[-1]) - 0.01 * 0.2) <= 1e-6


# ---------------------------------------------------------------- D7
def test_D7_cf_limits():
    sim = imu_sim.simulate_pitch_imu(duration=10.0, seed=0)
    accel_pitch = F.accel_tilt(sim.accel)[1]
    rate = sim.gyro[:, 1]
    big = F.complementary_filter(sim.t, rate, accel_pitch, tau=1e9, initial_angle=0.0)
    np.testing.assert_allclose(big, F.gyro_integrate(sim.t, rate, 0.0), rtol=0, atol=1e-6)
    small = F.complementary_filter(sim.t, rate, accel_pitch, tau=1e-9)
    np.testing.assert_allclose(small, accel_pitch, rtol=0, atol=1e-6)


# ---------------------------------------------------------------- D8
def test_D8_single_sample():
    t = np.array([0.5])
    rate = np.array([0.3])
    acc_angle = np.array([0.123])
    out_g = F.gyro_integrate(t, rate, 0.4)
    assert out_g.shape == (1,)
    np.testing.assert_array_equal(out_g, [0.4])
    np.testing.assert_array_equal(F.gyro_integrate(t, rate), [0.0])
    out_cf = F.complementary_filter(t, rate, acc_angle)
    assert out_cf.shape == (1,)
    np.testing.assert_array_equal(out_cf, [0.123])
