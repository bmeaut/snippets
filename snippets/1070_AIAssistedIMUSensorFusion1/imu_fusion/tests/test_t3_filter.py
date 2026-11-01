"""Tier 3 spec 11.3 - deterministic filter correctness (RD1-RD8)."""
import math

import numpy as np
import pytest

import imu_filters as F
import imu_sim
import tier3_reference as ref3

R_DEFAULT = (0.05 / 9.81) ** 2


# ------------------------------------------------------------------ random problem generator
def _random_problem(seed, n=None, tilt=0.5):
    """Non-uniform t, |angles| <= 0.8 rad, accelerometer consistent with the angles plus
    disturbances, small random gyro."""
    rng = np.random.default_rng(3000 + seed)
    n = int(rng.integers(60, 250)) if n is None else n
    dt = rng.uniform(0.005, 0.03, n - 1)
    t = rng.uniform(-2.0, 2.0) + np.concatenate([[0.0], np.cumsum(dt)])
    k = np.arange(n)
    roll = tilt * np.sin(0.05 * k + rng.uniform(0, 6)) + 0.02 * rng.normal(size=n)
    pitch = 0.9 * tilt * np.sin(0.037 * k + rng.uniform(0, 6)) + 0.02 * rng.normal(size=n)
    roll, pitch = np.clip(roll, -0.8, 0.8), np.clip(pitch, -0.8, 0.8)
    accel = ref3.gravity_term(roll, pitch) * (1.0 + 0.04 * rng.normal(size=(n, 1)))
    accel = accel + rng.normal(0.0, 0.15, size=(n, 3))
    gyro = rng.normal(0.0, 0.05, size=(n, 3))
    return t, gyro, accel


def _assert_kf_matches(got, want):
    assert np.array_equal(got.gated, want["gated"])
    np.testing.assert_allclose(got.roll, want["roll"], rtol=0, atol=1e-10)
    np.testing.assert_allclose(got.pitch, want["pitch"], rtol=0, atol=1e-10)
    np.testing.assert_allclose(got.bias_x, want["bias_x"], rtol=0, atol=1e-10)
    np.testing.assert_allclose(got.bias_y, want["bias_y"], rtol=0, atol=1e-10)
    np.testing.assert_allclose(got.cov_roll, want["cov_roll"], rtol=1e-9, atol=1e-20)
    np.testing.assert_allclose(got.cov_pitch, want["cov_pitch"], rtol=1e-9, atol=1e-20)


# ------------------------------------------------------------------ RD1
@pytest.mark.parametrize("seed", range(4))
def test_RD1_kalman_recurrence_with_gating(seed):
    t, gyro, accel = _random_problem(seed)
    gravity = 9.80
    dev = np.abs(np.linalg.norm(accel, axis=1) - gravity)
    threshold = float(np.quantile(dev, 0.70))          # about 30 % of the samples trigger
    hold = 4.0 * float(np.median(np.diff(t)))           # covers several samples
    kw = dict(gyro_noise_std=0.008, accel_noise_std=0.07, bias_rw_std=3e-4, gravity=gravity,
              gyro_bias_z=0.004, initial_bias=(0.01, -0.02), gate_threshold=threshold,
              gate_hold=hold, gate_r_scale=50.0, initial_roll=0.1, initial_pitch=-0.2)
    got = F.kalman_roll_pitch(t, gyro, accel, **kw)
    want = ref3.ref_kf_roll_pitch(t, gyro, accel, **kw)
    assert 0.1 < want["gated"].mean() < 0.95           # the gate really is exercised
    assert 0.2 < np.mean(np.abs(np.linalg.norm(accel, axis=1) - gravity) > threshold) < 0.4
    _assert_kf_matches(got, want)


@pytest.mark.parametrize("seed", range(3))
def test_RD1_kalman_recurrence_gating_off_and_default_initialisation(seed):
    t, gyro, accel = _random_problem(10 + seed)
    kw = dict(gyro_noise_std=0.006, accel_noise_std=0.09, bias_rw_std=2e-4)
    _assert_kf_matches(F.kalman_roll_pitch(t, gyro, accel, **kw), ref3.ref_kf_roll_pitch(t, gyro, accel, **kw))
    _assert_kf_matches(F.kalman_roll_pitch(t, gyro, accel), ref3.ref_kf_roll_pitch(t, gyro, accel))


def test_RD1_kalman_recurrence_large_tilt():
    # |angles| up to 0.8 rad exercises the tan(theta) and 1/cos^2(theta) coefficients
    t, gyro, accel = _random_problem(77, n=200, tilt=0.8)
    kw = dict(gyro_noise_std=0.01, accel_noise_std=0.1, gate_threshold=0.3, gate_hold=0.05)
    _assert_kf_matches(F.kalman_roll_pitch(t, gyro, accel, **kw), ref3.ref_kf_roll_pitch(t, gyro, accel, **kw))


# ------------------------------------------------------------------ RD2
def _s1_zeroed():
    sim = imu_sim.simulate_pitch_imu(seed=0)
    gyro = np.zeros_like(sim.gyro)
    gyro[:, 1] = sim.gyro[:, 1]
    accel = sim.accel.copy()
    accel[:, 1] = 0.0
    return sim.t, gyro, accel


def test_RD2_reduction_to_kalman_pitch():
    t, gyro, accel = _s1_zeroed()
    assert np.all(accel[:, 2] > 0)
    got = F.kalman_roll_pitch(t, gyro, accel)
    pitch_acc = F.accel_tilt(accel)[1]
    want = F.kalman_pitch(t, gyro[:, 1], pitch_acc)
    assert np.all(got.roll == 0)
    assert np.all(got.bias_x == 0)
    np.testing.assert_allclose(got.pitch, want.angle, rtol=0, atol=1e-12)
    np.testing.assert_allclose(got.bias_y, want.bias, rtol=0, atol=1e-12)
    np.testing.assert_allclose(got.cov_pitch, want.cov, rtol=0, atol=1e-12)
    assert not got.gated.any()


def test_RD2_extra_reduction_with_non_default_parameters():
    t, gyro, accel = _s1_zeroed()
    kw = dict(gyro_noise_std=0.007, accel_noise_std=0.06, bias_rw_std=2e-4, gravity=9.8)
    got = F.kalman_roll_pitch(t, gyro, accel, initial_bias=(0.0, 0.02), initial_pitch=0.1, initial_roll=0.0, **kw)
    want = F.kalman_pitch(t, gyro[:, 1], F.accel_tilt(accel)[1], initial_bias=0.02, initial_angle=0.1, **kw)
    assert np.all(got.roll == 0) and np.all(got.bias_x == 0)
    np.testing.assert_allclose(got.pitch, want.angle, rtol=0, atol=1e-12)
    np.testing.assert_allclose(got.bias_y, want.bias, rtol=0, atol=1e-12)
    np.testing.assert_allclose(got.cov_pitch, want.cov, rtol=0, atol=1e-12)


# ------------------------------------------------------------------ RD3
def test_RD3_noise_free_tracking():
    b = (0.01, -0.02, 0.03)
    sim = imu_sim.simulate_roll_pitch_imu(duration=120.0, gyro_noise_std=0.0, accel_noise_std=0.0,
                                          gyro_bias=b, seed=0)
    res = F.kalman_roll_pitch(sim.t, sim.gyro, sim.accel, gyro_bias_z=0.03, initial_bias=(0.01, -0.02))
    m = sim.t >= 5.0
    assert np.max(np.abs(res.roll[m] - sim.roll_true[m])) <= 2e-4
    assert np.max(np.abs(res.pitch[m] - sim.pitch_true[m])) <= 2e-4
    assert np.max(np.abs(res.bias_x[m] - 0.01)) <= 2e-4
    assert np.max(np.abs(res.bias_y[m] + 0.02)) <= 2e-4


# ------------------------------------------------------------------ RD4
def _gate_case(devs, t, gravity=8.0):
    """accel with a single non-zero component, so that ||f|| = gravity + dev exactly (dyadic values)."""
    accel = np.zeros((len(t), 3))
    accel[:, 2] = gravity + np.asarray(devs, dtype=float)
    return np.asarray(t, dtype=float), np.zeros((len(t), 3)), accel


def _gated(t, gyro, accel, threshold, hold, gravity=8.0):
    return F.kalman_roll_pitch(t, gyro, accel, gravity=gravity, gate_threshold=threshold,
                               gate_hold=hold).gated


T_GATE = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 1.625, 2.0, 3.0, 3.25]


def test_RD4_gate_hand_computed_with_inclusive_hold_boundary():
    # trigger only at index 2 (t = 0.5, dev 0.5 > 0.25); hold = 0.5 -> gated while t <= 1.0 (inclusive)
    devs = [0, 0, 0.5, 0, 0, 0, 0, 0, 0, 0]
    t, gyro, accel = _gate_case(devs, T_GATE)
    got = _gated(t, gyro, accel, 0.25, 0.5)
    expected = [False, False, True, True, True, False, False, False, False, False]
    assert got.dtype == bool
    assert got.tolist() == expected
    assert np.array_equal(got, ref3.ref_gate(t, accel, 8.0, 0.25, 0.5))


def test_RD4_gate_threshold_is_strict_and_negative_deviations_trigger():
    # dev exactly 0.25 does not trigger (strict >); dev -0.5 (||f|| below gravity) does
    devs = [0.25, 0, 0, -0.5, 0, 0, 0, 0, 0.25, 0]
    t, gyro, accel = _gate_case(devs, T_GATE)
    got = _gated(t, gyro, accel, 0.25, 0.25)
    expected = [False, False, False, True, True, False, False, False, False, False]
    assert got.tolist() == expected     # hold 0.25 covers index 3 (t=.75) and index 4 (t=1.0, boundary)


@pytest.mark.parametrize("hold", [0.0, 0.25, 0.5, 1.0, 100.0], ids=lambda h: "hold%g" % h)
def test_RD4_gate_matches_definition_for_several_holds(hold):
    devs = [0, 0.5, 0, 0, -0.5, 0, 0.5, 0, 0, 0.5]
    t, gyro, accel = _gate_case(devs, T_GATE)
    got = _gated(t, gyro, accel, 0.25, hold)
    assert np.array_equal(got, ref3.ref_gate(t, accel, 8.0, 0.25, hold))


def test_RD4_gate_hold_zero_gates_only_trigger_samples():
    devs = [0, 0.5, 0, 0, -0.5, 0, 0.5, 0, 0, 0.5]
    t, gyro, accel = _gate_case(devs, T_GATE)
    got = _gated(t, gyro, accel, 0.25, 0.0)
    assert got.tolist() == [d != 0 for d in devs]


def test_RD4_gate_hold_longer_than_the_record_gates_everything_after_first_trigger():
    devs = [0, 0, 0, 0.5, 0, 0, 0, 0, 0, 0]
    t, gyro, accel = _gate_case(devs, T_GATE)
    got = _gated(t, gyro, accel, 0.25, 100.0)
    assert got.tolist() == [False, False, False] + [True] * 7


def test_RD4_gate_none_threshold_never_gates():
    devs = [0, 5.0, 0, -5.0, 0, 0, 0, 0, 5.0, 0]
    t, gyro, accel = _gate_case(devs, T_GATE)
    res = F.kalman_roll_pitch(t, gyro, accel, gravity=8.0, gate_threshold=None, gate_hold=100.0)
    assert res.gated.dtype == bool and res.gated.shape == (10,)
    assert not res.gated.any()
    res = F.kalman_roll_pitch(t, gyro, accel, gravity=8.0)             # the default is None
    assert not res.gated.any()


def test_RD4_gate_trigger_at_first_sample():
    devs = [0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    t, gyro, accel = _gate_case(devs, T_GATE)
    got = _gated(t, gyro, accel, 0.25, 0.5)
    assert got.tolist() == [True, True, True, False, False, False, False, False, False, False]


def test_RD4_gate_raises_r_only_while_gated():
    # With a huge accelerometer outlier at a gated sample the angle must barely move.
    t = np.arange(40) * 0.25
    accel = np.zeros((40, 3)); accel[:, 2] = 8.0
    accel[20] = [8.0 * math.sin(0.5), 0.0, 8.0 * math.cos(0.5) + 0.5]   # tilted outlier, ||f|| > threshold
    gyro = np.zeros((40, 3))
    base = dict(gravity=8.0, gate_hold=0.0)
    ungated = F.kalman_roll_pitch(t, gyro, accel, **base)
    gated = F.kalman_roll_pitch(t, gyro, accel, gate_threshold=0.25, gate_r_scale=1e4, **base)
    assert gated.gated[20] and not gated.gated[19]
    assert abs(gated.pitch[20]) < 0.1 * abs(ungated.pitch[20])
    assert abs(ungated.pitch[20]) > 1e-3


# ------------------------------------------------------------------ RD5
@pytest.mark.parametrize("seed", range(4))
@pytest.mark.parametrize("initial", [(None, None), (0.15, -0.25)], ids=["init_none", "init_given"])
def test_RD5_cf_matches_recurrence(seed, initial):
    t, gyro, accel = _random_problem(20 + seed)
    kw = dict(tau=0.35, gyro_bias=(0.01, -0.02, 0.03), initial_roll=initial[0], initial_pitch=initial[1])
    roll, pitch = F.complementary_roll_pitch(t, gyro, accel, **kw)
    r_ref, p_ref = ref3.ref_cf_roll_pitch(t, gyro, accel, **kw)
    np.testing.assert_allclose(roll, r_ref, rtol=0, atol=1e-12)
    np.testing.assert_allclose(pitch, p_ref, rtol=0, atol=1e-12)


def test_RD5_cf_defaults():
    t, gyro, accel = _random_problem(31)
    roll, pitch = F.complementary_roll_pitch(t, gyro, accel)
    r_ref, p_ref = ref3.ref_cf_roll_pitch(t, gyro, accel)
    np.testing.assert_allclose(roll, r_ref, rtol=0, atol=1e-12)
    np.testing.assert_allclose(pitch, p_ref, rtol=0, atol=1e-12)


def _steady_state_run(delta, tau=0.2):
    b = (0.01, 0.01, 0.01)
    sim = imu_sim.simulate_roll_pitch_imu(duration=60.0, trajectory=imu_sim.constant_roll_pitch_trajectory(0.2, 0.3),
                                          gyro_noise_std=0.0, accel_noise_std=0.0, gyro_bias=b, seed=0)
    bias_arg = (b[0] + delta, b[1], b[2])
    roll, pitch = F.complementary_roll_pitch(sim.t, sim.gyro, sim.accel, tau=tau, gyro_bias=bias_arg)
    return roll - sim.roll_true, pitch - sim.pitch_true


def test_RD5_cf_steady_state_bias_offset():
    delta, tau = 0.01, 0.2
    roll_err, pitch_err = _steady_state_run(delta, tau)
    # spec: "the final roll error equals delta * tau (1e-6)"; compared as a magnitude, see Notes
    assert abs(abs(roll_err[-1]) - delta * tau) <= 1e-6
    assert abs(pitch_err[-1]) <= 1e-9


def test_RD5_extra_sign_of_the_steady_state_error():
    # the bias that is subtracted is too large by delta, so the estimate lags: error = -delta * tau
    delta, tau = 0.01, 0.2
    roll_err, _ = _steady_state_run(delta, tau)
    assert abs(roll_err[-1] - (-delta * tau)) <= 1e-6
    roll_err2, _ = _steady_state_run(-delta, tau)
    assert abs(roll_err2[-1] - (delta * tau)) <= 1e-6


# ------------------------------------------------------------------ RD6
@pytest.mark.parametrize("initial", [(None, None), (0.3, -0.1)], ids=["init_none", "init_given"])
@pytest.mark.parametrize("threshold", [None, 0.2, 5.0], ids=["gate_off", "trigger", "no_trigger"])
def test_RD6_single_sample(initial, threshold):
    t = np.array([0.5])
    gyro = np.array([[0.01, 0.02, 0.03]])
    accel = np.array([[-1.5, 2.0, 9.9]])                  # ||f|| = 10.2, deviates from 9.81 by ~0.4
    norm = float(np.linalg.norm(accel[0]))
    roll_acc, pitch_acc = ref3.ref_accel_tilt(accel)
    res = F.kalman_roll_pitch(t, gyro, accel, initial_bias=(0.011, -0.012), gate_threshold=threshold,
                              initial_roll=initial[0], initial_pitch=initial[1])
    roll0 = roll_acc[0] if initial[0] is None else initial[0]
    pitch0 = pitch_acc[0] if initial[1] is None else initial[1]
    assert res.roll.shape == (1,) and res.cov_roll.shape == (1, 2, 2) and res.gated.shape == (1,)
    np.testing.assert_allclose(res.roll, [roll0], rtol=1e-12, atol=0)
    np.testing.assert_allclose(res.pitch, [pitch0], rtol=1e-12, atol=0)
    np.testing.assert_allclose(res.bias_x, [0.011], rtol=1e-12, atol=0)
    np.testing.assert_allclose(res.bias_y, [-0.012], rtol=1e-12, atol=0)
    np.testing.assert_allclose(res.cov_roll[0], np.diag([R_DEFAULT / math.cos(pitch0) ** 2, 4e-4]),
                               rtol=1e-12, atol=0)
    np.testing.assert_allclose(res.cov_pitch[0], np.diag([R_DEFAULT, 4e-4]), rtol=1e-12, atol=0)
    expected_gated = threshold is not None and abs(norm - 9.81) > threshold
    assert res.gated.dtype == bool
    assert bool(res.gated[0]) == expected_gated


def test_RD6_single_sample_cf():
    t = np.array([0.5])
    gyro = np.array([[0.01, 0.02, 0.03]])
    accel = np.array([[-1.5, 2.0, 9.9]])
    roll_acc, pitch_acc = ref3.ref_accel_tilt(accel)
    roll, pitch = F.complementary_roll_pitch(t, gyro, accel)
    assert roll.shape == (1,) and pitch.shape == (1,)
    np.testing.assert_allclose(roll, roll_acc, rtol=1e-12, atol=0)
    np.testing.assert_allclose(pitch, pitch_acc, rtol=1e-12, atol=0)
    roll, pitch = F.complementary_roll_pitch(t, gyro, accel, initial_roll=0.3, initial_pitch=-0.1)
    np.testing.assert_array_equal(roll, [0.3])
    np.testing.assert_array_equal(pitch, [-0.1])


# ------------------------------------------------------------------ RD7
def _stationary_arrays():
    n = 40
    t = np.arange(n) * 0.5                                   # dyadic times: the window edges are exact
    sign = np.where(np.arange(n) % 2 == 0, 1.0, -1.0)
    gm, ga = np.array([0.01, -0.02, 0.03]), np.array([0.004, 0.006, 0.002])
    am, aa = np.array([1.0, -2.0, 9.0]), np.array([0.05, 0.10, 0.20])
    gyro = np.full((n, 3), 1000.0)
    accel = np.full((n, 3), 1000.0)
    window = slice(10, 30)                                   # t = 5.0 ... 14.5 (20 samples)
    gyro[window] = gm + ga * sign[window, None]
    accel[window] = am + aa * sign[window, None]
    return t, gyro, accel, gm, ga, am, aa


def test_RD7_estimate_stationary_exact_values():
    t, gyro, accel, gm, ga, am, aa = _stationary_arrays()
    est = F.estimate_stationary(t, gyro, accel, 5.0, 14.5)    # both window edges are inclusive
    n = 20
    var_g = n * ga ** 2 / (n - 1)                              # balanced +-a, ddof=1
    var_a = n * aa ** 2 / (n - 1)
    np.testing.assert_allclose(est.gyro_bias, gm, rtol=0, atol=1e-12)
    assert np.shape(est.gyro_bias) == (3,)
    assert abs(est.gyro_noise_std - math.sqrt(np.mean(var_g))) <= 1e-12
    assert abs(est.accel_noise_std - math.sqrt(np.mean(var_a))) <= 1e-12
    expected_gravity = 0.5 * (np.linalg.norm(am + aa) + np.linalg.norm(am - aa))
    assert abs(est.gravity - expected_gravity) <= 1e-12
    assert est.n_samples == 20


def test_RD7_window_edges_are_inclusive_and_exclusive_outside():
    t, gyro, accel, *_ = _stationary_arrays()
    assert F.estimate_stationary(t, gyro, accel, 5.0, 14.5).n_samples == 20
    assert F.estimate_stationary(t, gyro, accel, 5.0, 14.25).n_samples == 19
    assert F.estimate_stationary(t, gyro, accel, 5.25, 14.5).n_samples == 19
    assert F.estimate_stationary(t, gyro, accel, 4.75, 14.75).n_samples == 20


@pytest.mark.parametrize("seed", range(3))
def test_RD7_estimate_stationary_random_data(seed):
    rng = np.random.default_rng(500 + seed)
    n = 300
    t = np.arange(n) * 0.01
    gyro = rng.normal([0.01, -0.02, 0.03], [0.004, 0.006, 0.005], size=(n, 3))
    accel = rng.normal([0.3, -0.2, 9.7], [0.04, 0.06, 0.05], size=(n, 3))
    est = F.estimate_stationary(t, gyro, accel, 0.5, 2.0)
    want = ref3.ref_stationary(t, gyro, accel, 0.5, 2.0)
    np.testing.assert_allclose(est.gyro_bias, want["gyro_bias"], rtol=0, atol=1e-12)
    assert abs(est.gyro_noise_std - want["gyro_noise_std"]) <= 1e-12
    assert abs(est.accel_noise_std - want["accel_noise_std"]) <= 1e-12
    assert abs(est.gravity - want["gravity"]) <= 1e-12
    assert est.n_samples == want["n_samples"]


# ------------------------------------------------------------------ RD8
def test_RD8_estimate_stationary_on_s6():
    sim = imu_sim.simulate_roll_pitch_imu(seed=0)
    est = F.estimate_stationary(sim.t, sim.gyro, sim.accel, 0.0, 4.5)
    n = est.n_samples
    assert n == 451
    for axis in range(3):
        assert abs(est.gyro_bias[axis] - sim.gyro_bias[axis]) <= 4 * 0.005 / math.sqrt(n)
    assert abs(est.gyro_noise_std / 0.005 - 1.0) <= 0.10
    assert abs(est.accel_noise_std / 0.05 - 1.0) <= 0.10
    assert abs(est.gravity - 9.81) <= 0.01
