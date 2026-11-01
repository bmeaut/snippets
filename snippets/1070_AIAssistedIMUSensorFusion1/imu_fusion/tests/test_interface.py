"""Spec 8.4 - interface, separation, errors (I1-I5) and metric unit values (M1)."""
import inspect
import math
import os
import subprocess
import sys

import numpy as np
import pytest

import imu_filters as F
import imu_metrics as M
import imu_plots
import imu_sim

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------- I1
def _fresh_import(code):
    env = dict(os.environ, PYTHONPATH=ROOT)
    return subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env,
                          capture_output=True, text=True, timeout=120)


def test_I1_filters_import_isolation():
    code = ("import sys, imu_filters\n"
            "bad = [m for m in ('imu_sim','imu_metrics','imu_plots') if m in sys.modules]\n"
            "print(bad)\nsys.exit(1 if bad else 0)")
    r = _fresh_import(code)
    assert r.returncode == 0, r.stdout + r.stderr


def test_I1_metrics_import_isolation():
    code = ("import sys, imu_metrics\n"
            "bad = [m for m in ('imu_sim',) if m in sys.modules]\n"
            "print(bad)\nsys.exit(1 if bad else 0)")
    r = _fresh_import(code)
    assert r.returncode == 0, r.stdout + r.stderr


# ---------------------------------------------------------------- I2
EMPTY = inspect.Parameter.empty
SIGNATURES = {
    (imu_sim, "simulate_pitch_imu"): [
        ("duration", 60.0), ("fs", 100.0), ("trajectory", None),
        ("gyro_bias", (0.01, 0.01, 0.01)), ("gyro_noise_std", 0.005),
        ("accel_noise_std", 0.05), ("seed", None),
        ("gyro_bias_rw_std", 0.0), ("bias_step", None)],  # Tier 2 spec 4.1
    (imu_sim, "default_pitch_trajectory"): [("t", EMPTY)],
    (imu_sim, "constant_pitch_trajectory"): [("angle", EMPTY)],
    (F, "accel_tilt"): [("accel", EMPTY)],
    (F, "gyro_integrate"): [("t", EMPTY), ("gyro_rate", EMPTY), ("initial_angle", 0.0)],
    (F, "complementary_filter"): [("t", EMPTY), ("gyro_rate", EMPTY), ("accel_angle", EMPTY),
                                  ("tau", 0.2), ("initial_angle", None)],
    (M, "rmse"): [("estimate", EMPTY), ("truth", EMPTY)],
    (M, "max_abs_error"): [("estimate", EMPTY), ("truth", EMPTY)],
    (M, "drift_rate"): [("t", EMPTY), ("estimate", EMPTY), ("truth", EMPTY)],
}


@pytest.mark.parametrize("key", list(SIGNATURES), ids=lambda k: k[1])
def test_I2_signatures(key):
    module, name = key
    expected = SIGNATURES[key]
    params = list(inspect.signature(getattr(module, name)).parameters.values())
    assert [p.name for p in params] == [n for n, _ in expected]
    for p, (n, default) in zip(params, expected):
        if default is EMPTY:
            assert p.default is EMPTY, n
        elif isinstance(default, tuple):  # gyro_bias: any array-like equal to (0.01,)*3
            assert p.default is not EMPTY and np.array_equal(np.asarray(p.default), default), n
        else:
            assert p.default == default and type(p.default) is type(default), n


# ---------------------------------------------------------------- I3
def _t(n=5):
    return np.arange(n, dtype=float) * 0.01


def _sim_cases():
    S = imu_sim.simulate_pitch_imu
    return [
        ("duration_zero", lambda: S(duration=0.0)),
        ("duration_negative", lambda: S(duration=-1.0)),
        ("fs_zero", lambda: S(fs=0.0)),
        ("fs_negative", lambda: S(fs=-100.0)),
        ("N_equals_1", lambda: S(duration=0.01, fs=100.0)),
        ("N_equals_0", lambda: S(duration=0.001, fs=100.0)),
        ("gyro_noise_negative", lambda: S(gyro_noise_std=-0.001)),
        ("accel_noise_negative", lambda: S(accel_noise_std=-0.001)),
        ("bias_len2", lambda: S(gyro_bias=(0.0, 0.0))),
        ("bias_len4", lambda: S(gyro_bias=(0.0, 0.0, 0.0, 0.0))),
        ("bias_column", lambda: S(gyro_bias=np.zeros((3, 1)))),
        ("bias_row", lambda: S(gyro_bias=np.zeros((1, 3)))),
        ("pitch_too_large", lambda: S(trajectory=imu_sim.constant_pitch_trajectory(1.2))),
        ("pitch_too_negative", lambda: S(trajectory=imu_sim.constant_pitch_trajectory(-1.2))),
        ("pitch_exceeds_mid_run", lambda: S(duration=10.0, fs=10.0,
                                            trajectory=lambda t: (1.2 * np.sin(t), 1.2 * np.cos(t)))),
    ]


def _filter_cases():
    t, x = _t(5), np.arange(5, dtype=float)
    t_equal = t.copy(); t_equal[2] = t_equal[1]
    t_back = t[::-1].copy()
    empty = np.array([])
    cases = [
        ("accel_tilt_1d", lambda: F.accel_tilt(np.ones(3))),
        ("accel_tilt_2cols", lambda: F.accel_tilt(np.ones((5, 2)))),
        ("accel_tilt_4cols", lambda: F.accel_tilt(np.ones((5, 4)))),
        ("accel_tilt_3d", lambda: F.accel_tilt(np.ones((2, 3, 3)))),
        ("gyro_int_len_t_gt", lambda: F.gyro_integrate(t, x[:4])),
        ("gyro_int_len_t_lt", lambda: F.gyro_integrate(t[:4], x)),
        ("gyro_int_t_2d", lambda: F.gyro_integrate(t.reshape(5, 1), x)),
        ("gyro_int_rate_2d", lambda: F.gyro_integrate(t, x.reshape(5, 1))),
        ("gyro_int_empty", lambda: F.gyro_integrate(empty, empty)),
        ("gyro_int_t_equal", lambda: F.gyro_integrate(t_equal, x)),
        ("gyro_int_t_decreasing", lambda: F.gyro_integrate(t_back, x)),
        ("cf_tau_zero", lambda: F.complementary_filter(t, x, x, tau=0.0)),
        ("cf_tau_negative", lambda: F.complementary_filter(t, x, x, tau=-0.2)),
        ("cf_len_rate", lambda: F.complementary_filter(t, x[:4], x)),
        ("cf_len_accel", lambda: F.complementary_filter(t, x, x[:4])),
        ("cf_len_t", lambda: F.complementary_filter(t[:4], x, x)),
        ("cf_t_2d", lambda: F.complementary_filter(t.reshape(5, 1), x, x)),
        ("cf_rate_2d", lambda: F.complementary_filter(t, x.reshape(5, 1), x)),
        ("cf_accel_2d", lambda: F.complementary_filter(t, x, x.reshape(5, 1))),
        ("cf_empty", lambda: F.complementary_filter(empty, empty, empty)),
        ("cf_t_equal", lambda: F.complementary_filter(t_equal, x, x)),
        ("cf_t_decreasing", lambda: F.complementary_filter(t_back, x, x)),
    ]
    return cases


def _metric_cases():
    ok3, nan3, zero3 = np.array([1.0, 2.0, 3.0]), np.array([1.0, np.nan, 3.0]), np.zeros(3)
    t3 = np.array([0.0, 1.0, 2.0])
    empty = np.array([])
    cases = []
    for name in ("rmse", "max_abs_error"):
        fn = getattr(M, name)
        cases += [
            (f"{name}_shape_mismatch", lambda fn=fn: fn(ok3, np.zeros(4))),
            (f"{name}_empty", lambda fn=fn: fn(empty, empty)),
            (f"{name}_nan_estimate", lambda fn=fn: fn(nan3, zero3)),
            (f"{name}_nan_truth", lambda fn=fn: fn(ok3, nan3)),
        ]
    cases += [
        ("drift_shape_mismatch_est", lambda: M.drift_rate(t3, np.zeros(4), zero3)),
        ("drift_shape_mismatch_truth", lambda: M.drift_rate(t3, ok3, np.zeros(4))),
        ("drift_shape_mismatch_t", lambda: M.drift_rate(np.array([0.0, 1.0]), ok3, zero3)),
        ("drift_empty", lambda: M.drift_rate(empty, empty, empty)),
        ("drift_nan_estimate", lambda: M.drift_rate(t3, nan3, zero3)),
        ("drift_nan_truth", lambda: M.drift_rate(t3, ok3, nan3)),
        ("drift_nan_t", lambda: M.drift_rate(np.array([0.0, np.nan, 2.0]), ok3, zero3)),
        ("drift_single_sample", lambda: M.drift_rate(np.array([0.0]), np.array([1.0]), np.array([0.0]))),
    ]
    return cases


def _plot_cases():
    t, truth = _t(5), np.zeros(5)
    return [
        ("plot_empty_estimates", lambda: imu_plots.plot_comparison(t, truth, {})),
        ("plot_t_truth_mismatch", lambda: imu_plots.plot_comparison(t, np.zeros(4), {"a": np.zeros(5)})),
        ("plot_estimate_mismatch", lambda: imu_plots.plot_comparison(t, truth, {"a": np.zeros(4)})),
        ("plot_one_of_many_mismatch", lambda: imu_plots.plot_comparison(
            t, truth, {"a": np.zeros(5), "b": np.zeros(6)})),
    ]


ALL_ERROR_CASES = _sim_cases() + _filter_cases() + _metric_cases() + _plot_cases()


@pytest.mark.parametrize("call", [c for _, c in ALL_ERROR_CASES], ids=[n for n, _ in ALL_ERROR_CASES])
def test_I3_value_errors(call):
    with pytest.raises(ValueError):
        call()


def test_I3_boundary_pitch_pi_over_3_is_accepted():
    # negative control: |pitch| == pi/3 is within range (only > pi/3 + 1e-9 must raise)
    sim = imu_sim.simulate_pitch_imu(duration=1.0, trajectory=imu_sim.constant_pitch_trajectory(np.pi / 3),
                                     seed=0)
    assert sim.pitch_true.shape == (100,)


# ---------------------------------------------------------------- I4
def _snap(*arrays):
    return [np.array(a, copy=True) for a in arrays]


def _assert_same(before, after):
    for b, a in zip(before, after):
        assert b.shape == a.shape and b.dtype == a.dtype
        assert np.array_equal(b, a, equal_nan=True)


def test_I4_filters_do_not_modify_inputs(s1_runs):
    sim, _ = s1_runs[0]
    t, gyro, accel = sim.t.copy(), sim.gyro.copy(), sim.accel.copy()
    ap = F.accel_tilt(accel)[1]
    rate = gyro[:, 1].copy()
    before = _snap(t, gyro, accel, ap, rate)
    F.accel_tilt(accel)
    F.gyro_integrate(t, rate, 0.0)
    F.complementary_filter(t, rate, ap, tau=0.2)
    F.complementary_filter(t, rate, ap, tau=0.2, initial_angle=0.1)
    _assert_same(before, _snap(t, gyro, accel, ap, rate))


def test_I4_metrics_do_not_modify_inputs(s1_runs):
    sim, est = s1_runs[0]
    t, e, tr = sim.t.copy(), est["cf"].copy(), sim.pitch_true.copy()
    before = _snap(t, e, tr)
    M.rmse(e, tr)
    M.max_abs_error(e, tr)
    M.drift_rate(t, e, tr)
    _assert_same(before, _snap(t, e, tr))


def test_I4_plot_comparison_does_not_modify_inputs(s1_runs):
    sim, est = s1_runs[0]
    t, tr = sim.t.copy(), sim.pitch_true.copy()
    ests = {k: v.copy() for k, v in est.items()}
    before = _snap(t, tr, *ests.values())
    keys_before = list(ests)
    imu_plots.plot_comparison(t, tr, ests, title="x")
    assert list(ests) == keys_before
    _assert_same(before, _snap(t, tr, *ests.values()))


def test_I4_simulator_and_trajectories_do_not_modify_inputs():
    t = np.linspace(0.0, 5.0, 501)
    bias = np.array([0.01, -0.02, 0.03])
    before = _snap(t, bias)
    imu_sim.default_pitch_trajectory(t)
    imu_sim.constant_pitch_trajectory(0.2)(t)
    imu_sim.simulate_pitch_imu(duration=5.0, gyro_bias=bias, seed=0)
    _assert_same(before, _snap(t, bias))


# ---------------------------------------------------------------- I5
def _is_float64_vec(a, n):
    return isinstance(a, np.ndarray) and a.shape == (n,) and a.dtype == np.float64


def test_I5_return_shapes_and_dtypes():
    sim = imu_sim.simulate_pitch_imu(duration=5.0, seed=1)
    n = sim.t.size
    assert n == 500
    assert sim.gyro.shape == (n, 3) and sim.gyro.dtype == np.float64
    assert sim.accel.shape == (n, 3) and sim.accel.dtype == np.float64
    for name in ("t", "roll_true", "pitch_true"):
        assert _is_float64_vec(getattr(sim, name), n), name
    assert sim.gyro_bias.shape == (3,) and sim.gyro_bias.dtype == np.float64

    pitch, rate = imu_sim.default_pitch_trajectory(sim.t)
    assert _is_float64_vec(pitch, n) and _is_float64_vec(rate, n)
    pitch, rate = imu_sim.constant_pitch_trajectory(0.2)(sim.t)
    assert _is_float64_vec(pitch, n) and _is_float64_vec(rate, n)
    assert np.all(pitch == 0.2) and np.all(rate == 0.0)

    roll, pitch_est = F.accel_tilt(sim.accel)
    assert _is_float64_vec(roll, n) and _is_float64_vec(pitch_est, n)
    assert _is_float64_vec(F.gyro_integrate(sim.t, sim.gyro[:, 1], 0.0), n)
    assert _is_float64_vec(F.complementary_filter(sim.t, sim.gyro[:, 1], pitch_est), n)

    for val in (M.rmse(pitch_est, sim.pitch_true),
                M.max_abs_error(pitch_est, sim.pitch_true),
                M.drift_rate(sim.t, pitch_est, sim.pitch_true)):
        assert isinstance(val, (float, np.floating))
        assert np.ndim(val) == 0


# ---------------------------------------------------------------- M1
def test_M1_rmse_values():
    assert M.rmse(np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 3.0])) == 0
    assert M.rmse(np.array([3.0, 4.0]), np.array([0.0, 0.0])) == math.sqrt(12.5)


def test_M1_max_abs_error_value():
    assert M.max_abs_error(np.array([1.0, -5.0]), np.array([0.0, 0.0])) == 5


def test_M1_drift_rate_value():
    t = np.arange(0.0, 20.0, 0.1)
    est = 0.7 + 0.03 * t
    assert abs(M.drift_rate(t, est, np.zeros_like(t)) - 0.03) <= 1e-12
    truth = np.sin(t)  # error is still exactly 0.7 + 0.03 t
    assert abs(M.drift_rate(t, truth + est, truth) - 0.03) <= 1e-12
    t_nu = np.cumsum(np.random.default_rng(0).uniform(0.01, 0.2, 300))  # non-uniform
    assert abs(M.drift_rate(t_nu, 0.7 + 0.03 * t_nu, np.zeros_like(t_nu)) - 0.03) <= 1e-12
