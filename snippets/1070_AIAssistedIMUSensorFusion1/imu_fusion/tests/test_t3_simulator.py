"""Tier 3 spec 11.4 - roll/pitch simulator (RS1-RS6)."""
import dataclasses
import math

import numpy as np
import pytest

import imu_sim
import tier3_reference as ref3

G = ref3.G
NOISE_FREE = dict(gyro_noise_std=0.0, accel_noise_std=0.0)
BIAS = (0.01, -0.02, 0.03)


def _noise_free(**kw):
    kw = dict(NOISE_FREE, **kw)
    kw.setdefault("seed", 0)
    return imu_sim.simulate_roll_pitch_imu(**kw)


# ---------------------------------------------------------------- RS1
def test_RS1_noise_free_model_default_trajectory():
    sim = _noise_free(gyro_bias=BIAS)
    roll, pitch, roll_rate, pitch_rate = imu_sim.default_roll_pitch_trajectory(sim.t)  # trajectory's own outputs
    expected_gyro = ref3.body_rates(roll, roll_rate, pitch_rate) + np.array(BIAS)
    np.testing.assert_allclose(sim.gyro, expected_gyro, rtol=0, atol=1e-12)
    np.testing.assert_allclose(sim.accel, ref3.gravity_term(roll, pitch), rtol=0, atol=1e-12)
    np.testing.assert_allclose(sim.roll_true, roll, rtol=0, atol=1e-12)
    np.testing.assert_allclose(sim.pitch_true, pitch, rtol=0, atol=1e-12)
    assert sim.disturbed_true.dtype == bool
    assert sim.disturbed_true.shape == sim.t.shape
    assert not sim.disturbed_true.any()


def test_RS1_noise_free_model_constant_trajectory():
    traj = imu_sim.constant_roll_pitch_trajectory(0.4, -0.5)
    sim = _noise_free(duration=10.0, trajectory=traj, gyro_bias=BIAS)
    roll, pitch, roll_rate, pitch_rate = traj(sim.t)
    np.testing.assert_allclose(sim.gyro, ref3.body_rates(roll, roll_rate, pitch_rate) + np.array(BIAS),
                               rtol=0, atol=1e-12)
    np.testing.assert_allclose(sim.accel, ref3.gravity_term(roll, pitch), rtol=0, atol=1e-12)
    np.testing.assert_allclose(sim.gyro, np.array(BIAS) + np.zeros((sim.t.size, 3)), rtol=0, atol=1e-12)
    assert not sim.disturbed_true.any()


# ---------------------------------------------------------------- RS2
LIN = (10.0, 2.0, 3.0, 0.7)


def _lin_case(segments):
    with_seg = _noise_free(duration=20.0, gyro_bias=BIAS, linear_accel_segments=segments)
    without = _noise_free(duration=20.0, gyro_bias=BIAS)
    return with_seg, without


@pytest.mark.parametrize("segment", [LIN, (10.0, 2.0, 3.0, 0.0), (12.5, 3.0, 1.5, math.pi / 2)],
                         ids=["az0.7", "az0", "az_pi_2"])
def test_RS2_linear_accel_segment(segment):
    sim, base = _lin_case((segment,))
    t0, dur = segment[0], segment[1]
    gravity = ref3.gravity_term(sim.roll_true, sim.pitch_true)
    delta = sim.accel - gravity
    expected = ref3.ref_linear_accel_body(sim.t, sim.roll_true, sim.pitch_true, [segment])
    np.testing.assert_allclose(delta, expected, rtol=0, atol=1e-12)
    # the closed form written in spec 5.4 agrees as well
    closed = ref3.ref_linear_accel_closed_form(sim.t, sim.roll_true, sim.pitch_true, [segment])
    np.testing.assert_allclose(delta, closed, rtol=0, atol=1e-12)
    inside = (sim.t >= t0) & (sim.t <= t0 + dur)
    assert inside.any()
    assert np.max(np.abs(delta[inside])) > 0.1          # the disturbance is really there
    np.testing.assert_allclose(delta[~inside], 0.0, rtol=0, atol=1e-12)
    np.testing.assert_array_equal(sim.disturbed_true, inside)
    np.testing.assert_allclose(sim.gyro, base.gyro, rtol=0, atol=1e-12)
    np.testing.assert_array_equal(sim.roll_true, base.roll_true)
    np.testing.assert_array_equal(sim.pitch_true, base.pitch_true)


def test_RS2_disturbed_true_exact_interval():
    sim, _ = _lin_case((LIN,))
    assert np.array_equal(sim.disturbed_true, (sim.t >= 10.0) & (sim.t <= 12.0))
    assert sim.disturbed_true.sum() == 201          # closed interval at fs = 100 Hz


def test_RS2_extra_plain_tuple_and_overlapping_segments_are_summed():
    seg_a, seg_b = (10.0, 2.0, 3.0, 0.7), (11.0, 2.0, 2.0, 2.0)
    sim = _noise_free(duration=20.0, linear_accel_segments=(seg_a, seg_b))
    delta = sim.accel - ref3.gravity_term(sim.roll_true, sim.pitch_true)
    expected = ref3.ref_linear_accel_body(sim.t, sim.roll_true, sim.pitch_true, [seg_a, seg_b])
    np.testing.assert_allclose(delta, expected, rtol=0, atol=1e-12)
    inside = (sim.t >= 10.0) & (sim.t <= 13.0)
    np.testing.assert_array_equal(sim.disturbed_true, inside)
    # NamedTuple input gives the same result as the plain tuple
    named = _noise_free(duration=20.0, linear_accel_segments=(imu_sim.LinearAccelSegment(*seg_a),
                                                              imu_sim.LinearAccelSegment(*seg_b)))
    np.testing.assert_array_equal(named.accel, sim.accel)


def test_RS2_extra_peak_zero_segment_is_a_no_op_on_accel():
    sim = _noise_free(duration=20.0, linear_accel_segments=((10.0, 2.0, 0.0, 0.3),))
    base = _noise_free(duration=20.0)
    np.testing.assert_allclose(sim.accel, base.accel, rtol=0, atol=1e-12)
    assert sim.disturbed_true[(sim.t >= 10.0) & (sim.t <= 12.0)].all()


# ---------------------------------------------------------------- RS3
VIB = (10.0, 1.0, 2.0, 15.0, 0.05)


@pytest.mark.parametrize("segment", [VIB, (9.5, 2.0, 0.7, 4.0, 0.2)], ids=["default15Hz", "other"])
def test_RS3_vibration_segment(segment):
    sim = _noise_free(duration=20.0, gyro_bias=BIAS, vibration_segments=(segment,))
    base = _noise_free(duration=20.0, gyro_bias=BIAS)
    acc_add, gyr_add = ref3.ref_vibration(sim.t, [segment])
    np.testing.assert_allclose(sim.accel - base.accel, acc_add, rtol=0, atol=1e-12)
    np.testing.assert_allclose(sim.gyro - base.gyro, gyr_add, rtol=0, atol=1e-12)
    inside = (sim.t >= segment[0]) & (sim.t <= segment[0] + segment[1])
    assert np.max(np.abs(sim.accel - base.accel)[inside]) > 0.1 * segment[2]
    np.testing.assert_allclose((sim.accel - base.accel)[~inside], 0.0, rtol=0, atol=1e-12)
    np.testing.assert_allclose((sim.gyro - base.gyro)[~inside], 0.0, rtol=0, atol=1e-12)
    np.testing.assert_array_equal(sim.roll_true, base.roll_true)
    np.testing.assert_array_equal(sim.pitch_true, base.pitch_true)
    np.testing.assert_array_equal(sim.disturbed_true, inside)


def test_RS3_extra_phases_of_the_three_axes_differ_by_120_degrees():
    sim = _noise_free(duration=12.0, vibration_segments=(VIB,))
    base = _noise_free(duration=12.0)
    d = sim.accel - base.accel
    k = int(round(10.0 * 100.0))            # first sample of the segment: sin(p_i)
    np.testing.assert_allclose(d[k], 2.0 * np.sin([0.0, 2 * np.pi / 3, 4 * np.pi / 3]), rtol=0, atol=1e-12)


# ---------------------------------------------------------------- RS4
def test_RS4_trajectory_rest_phase_and_bounds():
    t = np.linspace(0.0, 4.99, 500)
    for out in imu_sim.default_roll_pitch_trajectory(t):
        assert out.shape == t.shape and out.dtype == np.float64
        assert np.all(out == 0.0)
    t_all = np.linspace(0.0, 400.0, 400001)
    roll, pitch, _, _ = imu_sim.default_roll_pitch_trajectory(t_all)
    assert np.max(np.abs(roll)) <= 0.6
    assert np.max(np.abs(pitch)) <= 0.7


def test_RS4_trajectory_matches_formulas():
    t = np.linspace(0.0, 150.0, 7501)
    got = imu_sim.default_roll_pitch_trajectory(t)
    want = ref3.ref_default_trajectory(t)
    for g, w in zip(got, want):
        np.testing.assert_allclose(g, w, rtol=0, atol=1e-12)


def test_RS4_rates_are_derivatives_of_angles():
    t = np.linspace(5.01, 120.0, 2000)
    h = 1e-6
    roll, pitch, roll_rate, pitch_rate = imu_sim.default_roll_pitch_trajectory(t)
    rp, pp, _, _ = imu_sim.default_roll_pitch_trajectory(t + h)
    rm, pm, _, _ = imu_sim.default_roll_pitch_trajectory(t - h)
    np.testing.assert_allclose(roll_rate, (rp - rm) / (2 * h), rtol=0, atol=1e-6)
    np.testing.assert_allclose(pitch_rate, (pp - pm) / (2 * h), rtol=0, atol=1e-6)


def test_RS4_extra_continuity_at_the_start_of_motion():
    at = imu_sim.default_roll_pitch_trajectory(np.array([5.0]))
    just_after = imu_sim.default_roll_pitch_trajectory(np.array([5.0 + 1e-9]))
    for a, b in zip(at, just_after):
        assert a[0] == 0.0
        assert abs(b[0]) < 1e-6


def test_RS4_extra_constant_trajectory():
    t = np.linspace(0.0, 3.0, 31)
    roll, pitch, roll_rate, pitch_rate = imu_sim.constant_roll_pitch_trajectory(0.2, -0.3)(t)
    for out in (roll, pitch, roll_rate, pitch_rate):
        assert out.shape == t.shape and out.dtype == np.float64
    assert np.all(roll == 0.2) and np.all(pitch == -0.3)
    assert np.all(roll_rate == 0.0) and np.all(pitch_rate == 0.0)


# ---------------------------------------------------------------- RS5
@pytest.fixture(scope="module")
def s6_seed0():
    return imu_sim.simulate_roll_pitch_imu(seed=0)


def test_RS5_noise_statistics(s6_seed0):
    s = s6_seed0
    roll, pitch, roll_rate, pitch_rate = ref3.ref_default_trajectory(s.t)
    gyro_model = ref3.body_rates(roll, roll_rate, pitch_rate) + s.gyro_bias
    accel_model = ref3.gravity_term(roll, pitch)
    g_res, a_res = s.gyro - gyro_model, s.accel - accel_model
    for axis in range(3):
        assert abs(np.std(g_res[:, axis]) / 0.005 - 1.0) <= 0.05
        assert abs(np.std(a_res[:, axis]) / 0.05 - 1.0) <= 0.05


def test_RS5_shapes_and_time_axis(s6_seed0):
    s = s6_seed0
    n = 12000
    assert s.t.shape == (n,) and s.t[0] == 0
    np.testing.assert_allclose(np.diff(s.t), 0.01, rtol=0, atol=1e-12)
    assert s.gyro.shape == (n, 3) and s.accel.shape == (n, 3)
    assert float(s.fs) == 100.0


def test_RS5_determinism_and_seed_sensitivity():
    a = imu_sim.simulate_roll_pitch_imu(seed=0)
    b = imu_sim.simulate_roll_pitch_imu(seed=0)
    for name in ("t", "gyro", "accel", "roll_true", "pitch_true", "gyro_bias", "disturbed_true"):
        assert np.array_equal(getattr(a, name), getattr(b, name)), name
    c = imu_sim.simulate_roll_pitch_imu(seed=1)
    assert not np.array_equal(a.gyro, c.gyro)


def test_RS5_extra_determinism_with_disturbances():
    kw = dict(duration=40.0, seed=3, linear_accel_segments=imu_sim.DEFAULT_LINEAR_ACCEL_SEGMENTS,
              vibration_segments=((20.0, 3.0, 2.0, 15.0, 0.05),))
    a, b = imu_sim.simulate_roll_pitch_imu(**kw), imu_sim.simulate_roll_pitch_imu(**kw)
    assert np.array_equal(a.gyro, b.gyro) and np.array_equal(a.accel, b.accel)


# ---------------------------------------------------------------- RS6
def _bad_calls():
    S = imu_sim.simulate_roll_pitch_imu
    L = (10.0, 2.0, 3.0, 0.7)
    V = (10.0, 1.0, 2.0, 15.0, 0.05)
    nan, inf = float("nan"), float("inf")
    cases = {
        # Tier 1 cases of T1-4.4
        "duration_zero": lambda: S(duration=0.0),
        "duration_negative": lambda: S(duration=-1.0),
        "fs_zero": lambda: S(fs=0.0),
        "fs_negative": lambda: S(fs=-100.0),
        "N_equals_1": lambda: S(duration=0.01, fs=100.0),
        "N_equals_0": lambda: S(duration=0.001, fs=100.0),
        "gyro_noise_negative": lambda: S(gyro_noise_std=-0.001),
        "accel_noise_negative": lambda: S(accel_noise_std=-0.001),
        "bias_len2": lambda: S(gyro_bias=(0.0, 0.0)),
        "bias_len4": lambda: S(gyro_bias=(0.0, 0.0, 0.0, 0.0)),
        "bias_column": lambda: S(gyro_bias=np.zeros((3, 1))),
        # both angles must stay within pi/3 + 1e-9
        "roll_too_large": lambda: S(trajectory=imu_sim.constant_roll_pitch_trajectory(1.2, 0.0)),
        "roll_too_negative": lambda: S(trajectory=imu_sim.constant_roll_pitch_trajectory(-1.2, 0.0)),
        "pitch_too_large": lambda: S(trajectory=imu_sim.constant_roll_pitch_trajectory(0.0, 1.2)),
        "pitch_too_negative": lambda: S(trajectory=imu_sim.constant_roll_pitch_trajectory(0.0, -1.2)),
        "roll_exceeds_mid_run": lambda: S(duration=10.0, fs=10.0, trajectory=lambda t: (
            1.2 * np.sin(t), 0.1 * np.sin(t), 1.2 * np.cos(t), 0.1 * np.cos(t))),
        "pitch_exceeds_mid_run": lambda: S(duration=10.0, fs=10.0, trajectory=lambda t: (
            0.1 * np.sin(t), 1.2 * np.sin(t), 0.1 * np.cos(t), 1.2 * np.cos(t))),
        # linear acceleration segments
        "lin_3_fields": lambda: S(duration=20.0, linear_accel_segments=((10.0, 2.0, 3.0),)),
        "lin_5_fields": lambda: S(duration=20.0, linear_accel_segments=((10.0, 2.0, 3.0, 0.7, 1.0),)),
        "lin_nan_t_start": lambda: S(duration=20.0, linear_accel_segments=((nan, 2.0, 3.0, 0.7),)),
        "lin_inf_duration": lambda: S(duration=20.0, linear_accel_segments=((10.0, inf, 3.0, 0.7),)),
        "lin_nan_peak": lambda: S(duration=20.0, linear_accel_segments=((10.0, 2.0, nan, 0.7),)),
        "lin_inf_azimuth": lambda: S(duration=20.0, linear_accel_segments=((10.0, 2.0, 3.0, inf),)),
        "lin_duration_zero": lambda: S(duration=20.0, linear_accel_segments=((10.0, 0.0, 3.0, 0.7),)),
        "lin_duration_negative": lambda: S(duration=20.0, linear_accel_segments=((10.0, -2.0, 3.0, 0.7),)),
        "lin_peak_negative": lambda: S(duration=20.0, linear_accel_segments=((10.0, 2.0, -3.0, 0.7),)),
        "lin_second_segment_bad": lambda: S(duration=20.0, linear_accel_segments=(L, (10.0, 2.0, -1.0, 0.0))),
        # vibration segments
        "vib_4_fields": lambda: S(duration=20.0, vibration_segments=((10.0, 1.0, 2.0, 15.0),)),
        "vib_6_fields": lambda: S(duration=20.0, vibration_segments=((10.0, 1.0, 2.0, 15.0, 0.05, 1.0),)),
        "vib_nan_t_start": lambda: S(duration=20.0, vibration_segments=((nan, 1.0, 2.0, 15.0, 0.05),)),
        "vib_inf_freq": lambda: S(duration=20.0, vibration_segments=((10.0, 1.0, 2.0, inf, 0.05),)),
        "vib_nan_gyro_amp": lambda: S(duration=20.0, vibration_segments=((10.0, 1.0, 2.0, 15.0, nan),)),
        "vib_duration_zero": lambda: S(duration=20.0, vibration_segments=((10.0, 0.0, 2.0, 15.0, 0.05),)),
        "vib_duration_negative": lambda: S(duration=20.0, vibration_segments=((10.0, -1.0, 2.0, 15.0, 0.05),)),
        "vib_accel_amp_negative": lambda: S(duration=20.0, vibration_segments=((10.0, 1.0, -2.0, 15.0, 0.05),)),
        "vib_gyro_amp_negative": lambda: S(duration=20.0, vibration_segments=((10.0, 1.0, 2.0, 15.0, -0.05),)),
        "vib_freq_zero": lambda: S(duration=20.0, vibration_segments=((10.0, 1.0, 2.0, 0.0, 0.05),)),
        "vib_freq_negative": lambda: S(duration=20.0, vibration_segments=((10.0, 1.0, 2.0, -5.0, 0.05),)),
        "vib_freq_equals_nyquist": lambda: S(duration=20.0, vibration_segments=((10.0, 1.0, 2.0, 50.0, 0.05),)),
        "vib_freq_above_nyquist": lambda: S(duration=20.0, vibration_segments=((10.0, 1.0, 2.0, 60.0, 0.05),)),
        "vib_freq_nyquist_other_fs": lambda: S(duration=20.0, fs=50.0,
                                               vibration_segments=((10.0, 1.0, 2.0, 25.0, 0.05),)),
    }
    return cases


BAD = _bad_calls()


@pytest.mark.parametrize("call", list(BAD.values()), ids=list(BAD))
def test_RS6_value_errors(call):
    with pytest.raises(ValueError):
        call()


def test_RS6_boundary_values_are_accepted():
    S = imu_sim.simulate_roll_pitch_imu
    S(duration=20.0, linear_accel_segments=((10.0, 2.0, 0.0, 0.7),))                 # peak == 0
    S(duration=20.0, vibration_segments=((10.0, 1.0, 0.0, 15.0, 0.0),))              # amplitudes == 0
    S(duration=20.0, vibration_segments=((10.0, 1.0, 2.0, 49.9, 0.05),))             # just below fs/2
    S(duration=20.0, fs=50.0, vibration_segments=((10.0, 1.0, 2.0, 24.9, 0.05),))
    sim = S(duration=2.0, trajectory=imu_sim.constant_roll_pitch_trajectory(math.pi / 3, -math.pi / 3))
    assert sim.t.shape == (200,)
    sim = S(duration=2.0, linear_accel_segments=(), vibration_segments=())
    assert not sim.disturbed_true.any()


# ---------------------------------------------------------------- constants / types (spec 5.2, 5.3)
def test_RS_extra_segment_types_and_default_constants():
    assert imu_sim.LinearAccelSegment._fields == ("t_start", "duration", "peak", "azimuth")
    assert imu_sim.VibrationSegment._fields == ("t_start", "duration", "accel_amp", "freq", "gyro_amp")
    lin = imu_sim.DEFAULT_LINEAR_ACCEL_SEGMENTS
    assert tuple(tuple(s) for s in lin) == ((30.0, 2.0, 3.0, 0.0), (60.0, 2.0, 3.0, math.pi / 2))
    vib = imu_sim.DEFAULT_VIBRATION_SEGMENTS
    assert tuple(tuple(s) for s in vib) == ((90.0, 5.0, 2.0, 15.0, 0.05),)
    assert all(isinstance(s, imu_sim.LinearAccelSegment) for s in lin)
    assert all(isinstance(s, imu_sim.VibrationSegment) for s in vib)


def test_RS_extra_simulated_roll_pitch_imu_is_frozen_dataclass():
    sim = imu_sim.simulate_roll_pitch_imu(duration=2.0, seed=0)
    assert dataclasses.is_dataclass(sim)
    assert type(sim).__dataclass_params__.frozen is True
    assert [f.name for f in dataclasses.fields(sim)] == [
        "t", "gyro", "accel", "roll_true", "pitch_true", "gyro_bias", "fs", "disturbed_true"]
