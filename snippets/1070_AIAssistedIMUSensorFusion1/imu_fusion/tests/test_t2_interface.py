"""Tier 2 spec 9.5 - interface (KI1-KI6), regression (KR1) and notebook (KG3)."""
import ast
import dataclasses
import inspect
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import numpy as np  # noqa: E402
import pytest  # noqa: E402

import imu_filters as F  # noqa: E402
import imu_metrics as M  # noqa: E402
import imu_plots  # noqa: E402
import imu_sim  # noqa: E402
from tier2_helpers import run  # noqa: E402

TESTS_DIR = Path(__file__).resolve().parent
ROOT = TESTS_DIR.parent


# ---------------------------------------------------------------- KI1
def _fresh_import(code):
    env = dict(os.environ, PYTHONPATH=str(ROOT))
    return subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env,
                          capture_output=True, text=True, timeout=120)


def test_KI1_filters_import_isolation():
    # same check as Tier 1 I1: imu_filters (now with the Kalman filter) imports no sibling module
    code = ("import sys, imu_filters\n"
            "bad = [m for m in ('imu_sim','imu_metrics','imu_plots') if m in sys.modules]\n"
            "print(bad)\nsys.exit(1 if bad else 0)")
    r = _fresh_import(code)
    assert r.returncode == 0, r.stdout + r.stderr


def test_KI1_metrics_import_isolation():
    code = ("import sys, imu_metrics\n"
            "bad = [m for m in ('imu_sim',) if m in sys.modules]\n"
            "print(bad)\nsys.exit(1 if bad else 0)")
    r = _fresh_import(code)
    assert r.returncode == 0, r.stdout + r.stderr


# ---------------------------------------------------------------- KI2
EMPTY = inspect.Parameter.empty
SIGNATURES = {
    (imu_sim, "simulate_pitch_imu"): [
        ("duration", 60.0), ("fs", 100.0), ("trajectory", None),
        ("gyro_bias", (0.01, 0.01, 0.01)), ("gyro_noise_std", 0.005),
        ("accel_noise_std", 0.05), ("seed", None),
        ("gyro_bias_rw_std", 0.0), ("bias_step", None)],
    (F, "kalman_noise_matrices"): [("dt", EMPTY), ("gyro_noise_std", EMPTY),
                                   ("accel_noise_std", EMPTY), ("bias_rw_std", EMPTY),
                                   ("gravity", 9.81)],
    (F, "kalman_pitch"): [("t", EMPTY), ("gyro_rate", EMPTY), ("accel_angle", EMPTY),
                          ("gyro_noise_std", 0.005), ("accel_noise_std", 0.05),
                          ("bias_rw_std", 1e-4), ("gravity", 9.81),
                          ("initial_angle", None), ("initial_bias", 0.0), ("initial_cov", None)],
    (M, "convergence_time"): [("t", EMPTY), ("estimate", EMPTY), ("truth", EMPTY),
                              ("tol", EMPTY), ("t_start", None)],
    (M, "coverage_fraction"): [("estimate", EMPTY), ("truth", EMPTY), ("std", EMPTY),
                               ("n_sigma", 2.0)],
    (imu_plots, "plot_error_comparison"): [("t", EMPTY), ("truth", EMPTY), ("estimates", EMPTY),
                                           ("exclude", ("gyro",)), ("t_window", None),
                                           ("title", ""), ("background", ("accel",)),
                                           ("shade", None)],  # Tier 3 erratum E3
    (imu_plots, "plot_bias_estimate"): [("t", EMPTY), ("bias_est", EMPTY), ("bias_std", EMPTY),
                                        ("bias_true", None), ("n_sigma", 2.0), ("title", "")],
}


@pytest.mark.parametrize("key", list(SIGNATURES), ids=lambda k: k[1])
def test_KI2_signatures(key):
    module, name = key
    expected = SIGNATURES[key]
    params = list(inspect.signature(getattr(module, name)).parameters.values())
    assert [p.name for p in params] == [n for n, _ in expected]
    for p, (n, default) in zip(params, expected):
        if default is EMPTY:
            assert p.default is EMPTY, n
        elif isinstance(default, tuple):  # sequence defaults: any sequence/array equal to the tuple
            assert p.default is not EMPTY, n
            if all(isinstance(x, float) for x in default):
                assert np.array_equal(np.asarray(p.default, dtype=float), default), n
            else:
                assert tuple(p.default) == default, n
        else:
            assert p.default == default and type(p.default) is type(default), n


# ---------------------------------------------------------------- KI3
def _t(n=5):
    return np.arange(n, dtype=float) * 0.01


def _kalman_cases():
    t, x = _t(5), np.arange(5, dtype=float) * 0.01
    t_equal = t.copy(); t_equal[2] = t_equal[1]
    t_back = t[::-1].copy()
    empty = np.array([])
    KP = F.kalman_pitch
    bad_asym = np.array([[1e-4, 1e-5], [2e-5, 1e-4]])
    bad_neg_eig = np.array([[1e-4, 1e-3], [1e-3, 1e-4]])  # symmetric, eigenvalue < 0
    return [
        # T1 section 5.3 cases (except tau)
        ("kf_len_rate", lambda: KP(t, x[:4], x)),
        ("kf_len_accel", lambda: KP(t, x, x[:4])),
        ("kf_len_t", lambda: KP(t[:4], x, x)),
        ("kf_t_2d", lambda: KP(t.reshape(5, 1), x, x)),
        ("kf_rate_2d", lambda: KP(t, x.reshape(5, 1), x)),
        ("kf_accel_2d", lambda: KP(t, x, x.reshape(5, 1))),
        ("kf_empty", lambda: KP(empty, empty, empty)),
        ("kf_t_equal", lambda: KP(t_equal, x, x)),
        ("kf_t_decreasing", lambda: KP(t_back, x, x)),
        # section 5.1 cases, seen through kalman_pitch
        ("kf_gyro_noise_zero", lambda: KP(t, x, x, gyro_noise_std=0.0)),
        ("kf_gyro_noise_negative", lambda: KP(t, x, x, gyro_noise_std=-0.005)),
        ("kf_accel_noise_zero", lambda: KP(t, x, x, accel_noise_std=0.0)),
        ("kf_accel_noise_negative", lambda: KP(t, x, x, accel_noise_std=-0.05)),
        ("kf_bias_rw_negative", lambda: KP(t, x, x, bias_rw_std=-1e-4)),
        ("kf_gravity_zero", lambda: KP(t, x, x, gravity=0.0)),
        ("kf_gravity_negative", lambda: KP(t, x, x, gravity=-9.81)),
        # initial_cov
        ("kf_cov_3x3", lambda: KP(t, x, x, initial_cov=np.eye(3) * 1e-4)),
        ("kf_cov_1d", lambda: KP(t, x, x, initial_cov=np.array([1e-4, 1e-4]))),
        ("kf_cov_batched", lambda: KP(t, x, x, initial_cov=np.ones((1, 2, 2)) * 1e-4)),
        ("kf_cov_asymmetric", lambda: KP(t, x, x, initial_cov=bad_asym)),
        ("kf_cov_negative_eigenvalue", lambda: KP(t, x, x, initial_cov=bad_neg_eig)),
    ]


def _noise_matrix_cases():
    N = F.kalman_noise_matrices
    return [
        ("nm_dt_zero", lambda: N(0.0, 0.005, 0.05, 1e-4)),
        ("nm_dt_negative", lambda: N(-0.01, 0.005, 0.05, 1e-4)),
        ("nm_gyro_zero", lambda: N(0.01, 0.0, 0.05, 1e-4)),
        ("nm_gyro_negative", lambda: N(0.01, -0.005, 0.05, 1e-4)),
        ("nm_accel_zero", lambda: N(0.01, 0.005, 0.0, 1e-4)),
        ("nm_accel_negative", lambda: N(0.01, 0.005, -0.05, 1e-4)),
        ("nm_bias_rw_negative", lambda: N(0.01, 0.005, 0.05, -1e-4)),
        ("nm_gravity_zero", lambda: N(0.01, 0.005, 0.05, 1e-4, gravity=0.0)),
        ("nm_gravity_negative", lambda: N(0.01, 0.005, 0.05, 1e-4, gravity=-9.81)),
    ]


def _sim_cases():
    S = imu_sim.simulate_pitch_imu
    return [
        ("sim_rw_negative", lambda: S(duration=5.0, gyro_bias_rw_std=-1e-4)),
        ("sim_step_len1", lambda: S(duration=5.0, bias_step=(1.0,))),
        ("sim_step_len3", lambda: S(duration=5.0, bias_step=(1.0, 0.01, 0.0))),
        ("sim_step_nan", lambda: S(duration=5.0, bias_step=(1.0, float("nan")))),
        ("sim_step_inf", lambda: S(duration=5.0, bias_step=(float("inf"), 0.01))),
    ]


def _metric_cases():
    t6, e6, z6 = np.arange(6, dtype=float), np.array([0.5, 0.2, 0.05, 0.2, 0.01, 0.01]), np.zeros(6)
    ones3, zeros3 = np.ones(3), np.zeros(3)
    return [
        ("ct_tol_zero", lambda: M.convergence_time(t6, e6, z6, tol=0.0)),
        ("ct_tol_negative", lambda: M.convergence_time(t6, e6, z6, tol=-1.0)),
        ("ct_no_samples_after_t_start", lambda: M.convergence_time(t6, e6, z6, tol=0.1, t_start=9.0)),
        ("ct_shape", lambda: M.convergence_time(t6, e6, np.zeros(4), tol=0.1)),
        ("ct_empty", lambda: M.convergence_time(np.array([]), np.array([]), np.array([]), tol=0.1)),
        ("ct_nan", lambda: M.convergence_time(t6, np.full(6, np.nan), z6, tol=0.1)),
        ("cf_std_negative", lambda: M.coverage_fraction(zeros3, zeros3, np.array([1.0, -0.1, 1.0]))),
        ("cf_n_sigma_zero", lambda: M.coverage_fraction(zeros3, zeros3, ones3, n_sigma=0.0)),
        ("cf_n_sigma_negative", lambda: M.coverage_fraction(zeros3, zeros3, ones3, n_sigma=-1.0)),
        ("cf_shape", lambda: M.coverage_fraction(zeros3, np.zeros(2), ones3)),
        ("cf_empty", lambda: M.coverage_fraction(np.array([]), np.array([]), np.array([]))),
        ("cf_nan", lambda: M.coverage_fraction(np.array([np.nan, 0, 0]), zeros3, ones3)),
    ]


def _plot_cases():
    t, truth = _t(10), np.zeros(10)
    ok = {"accel": np.zeros(10), "KF": np.zeros(10)}
    PE, PB = imu_plots.plot_error_comparison, imu_plots.plot_bias_estimate
    return [
        ("pe_empty_dict", lambda: PE(t, truth, {})),
        ("pe_only_excluded", lambda: PE(t, truth, {"gyro": np.zeros(10)})),
        ("pe_all_excluded", lambda: PE(t, truth, ok, exclude=("accel", "KF"))),
        ("pe_len_truth", lambda: PE(t, np.zeros(9), ok)),
        ("pe_len_estimate", lambda: PE(t, truth, {"accel": np.zeros(9)})),
        ("pe_len_t", lambda: PE(t[:9], truth, ok)),
        ("pe_window_equal", lambda: PE(t, truth, ok, t_window=(0.05, 0.05))),
        ("pe_window_reversed", lambda: PE(t, truth, ok, t_window=(0.07, 0.03))),
        ("pe_window_no_samples", lambda: PE(t, truth, ok, t_window=(10.0, 20.0))),
        ("pe_window_between_samples", lambda: PE(t, truth, ok, t_window=(0.031, 0.039))),
        ("pb_len_est", lambda: PB(t, np.zeros(9), np.ones(10))),
        ("pb_len_std", lambda: PB(t, np.zeros(10), np.ones(9))),
        ("pb_len_truth", lambda: PB(t, np.zeros(10), np.ones(10), bias_true=np.zeros(9))),
        ("pb_negative_std", lambda: PB(t, np.zeros(10), -np.ones(10))),
    ]


ALL_CASES = _sim_cases() + _noise_matrix_cases() + _kalman_cases() + _metric_cases() + _plot_cases()


@pytest.mark.parametrize("call", [c for _, c in ALL_CASES], ids=[n for n, _ in ALL_CASES])
def test_KI3_value_errors(call):
    with pytest.raises(ValueError):
        call()


def test_KI3_negative_controls_are_accepted():
    # boundary values that the spec allows must not raise
    Q, _ = F.kalman_noise_matrices(0.01, 0.005, 0.05, 0.0)       # bias_rw_std == 0 is allowed
    assert Q[1, 1] == 0
    t, x = _t(5), np.arange(5, dtype=float) * 0.01
    F.kalman_pitch(t, x, x, bias_rw_std=0.0)
    F.kalman_pitch(t, x, x, initial_cov=np.array([[2e-4, 1e-5], [1e-5, 5e-4]]))
    F.kalman_pitch(t, x, x, initial_cov=[[2e-4, 1e-5], [1e-5, 5e-4]])  # array-like
    ok = {"accel": np.zeros(10)}
    imu_plots.plot_error_comparison(_t(10), np.zeros(10), ok, t_window=(0.03, 0.03 + 1e-12 + 0.04))


# ---------------------------------------------------------------- KI4
def _snap(*arrays):
    return [np.array(a, copy=True) for a in arrays]


def _assert_same(before, after):
    for b, a in zip(before, after):
        assert b.shape == a.shape and b.dtype == a.dtype
        assert np.array_equal(b, a, equal_nan=True)


def test_KI4_kalman_pitch_does_not_modify_inputs():
    r = run("S1", 0)
    t, rate, ap = r.t.copy(), r.sim.gyro[:, 1].copy(), r.accel.copy()
    cov0 = np.array([[2e-4, 1e-5], [1e-5, 5e-4]])
    before = _snap(t, rate, ap, cov0)
    res = F.kalman_pitch(t, rate, ap, initial_cov=cov0)
    F.kalman_pitch(t, rate, ap)
    _assert_same(before, _snap(t, rate, ap, cov0))
    for out in (res.angle, res.bias, res.cov):  # results are new arrays
        for inp in (t, rate, ap, cov0):
            assert not np.shares_memory(out, inp)


def test_KI4_noise_matrices_and_metrics_do_not_modify_inputs():
    r = run("S4", 0)
    t, e, tr = r.t.copy(), r.kf.bias.copy(), r.bias_true.copy()
    std = np.sqrt(r.kf.cov[:, 1, 1]).copy()
    before = _snap(t, e, tr, std)
    M.convergence_time(t, e, tr, tol=1e-3, t_start=60.0)
    M.coverage_fraction(e, tr, std, 2.0)
    _assert_same(before, _snap(t, e, tr, std))


def test_KI4_plots_do_not_modify_inputs():
    r = run("S1", 0)
    t, tr = r.t.copy(), r.truth.copy()
    ests = {"gyro": r.gyro.copy(), "accel": r.accel.copy(), "CF": r.cf.copy(), "KF": r.kf.angle.copy()}
    before = _snap(t, tr, *ests.values())
    keys, window, exclude = list(ests), (30, 40), ("gyro",)
    imu_plots.plot_error_comparison(t, tr, ests, exclude=exclude, t_window=window, title="x")
    assert list(ests) == keys and window == (30, 40) and exclude == ("gyro",)
    _assert_same(before, _snap(t, tr, *ests.values()))

    bias, std, bt = r.kf.bias.copy(), np.sqrt(r.kf.cov[:, 1, 1]).copy(), r.bias_true.copy()
    before = _snap(t, bias, std, bt)
    imu_plots.plot_bias_estimate(t, bias, std, bt)
    _assert_same(before, _snap(t, bias, std, bt))


def test_KI4_simulator_does_not_modify_new_inputs():
    bias = np.array([0.01, -0.02, 0.03])
    step = np.array([3.0, 0.01])
    before = _snap(bias, step)
    imu_sim.simulate_pitch_imu(duration=5.0, gyro_bias=bias, gyro_bias_rw_std=1e-4, bias_step=step, seed=0)
    _assert_same(before, _snap(bias, step))


# ---------------------------------------------------------------- KI5
def test_KI5_kalman_result_fields():
    r = run("S1", 0)
    res, n = r.kf, r.t.size
    assert isinstance(res, F.KalmanResult)
    assert dataclasses.is_dataclass(F.KalmanResult)
    assert F.KalmanResult.__dataclass_params__.frozen is True
    assert [f.name for f in dataclasses.fields(F.KalmanResult)] == ["angle", "bias", "cov"]
    for name, shape in (("angle", (n,)), ("bias", (n,)), ("cov", (n, 2, 2))):
        arr = getattr(res, name)
        assert isinstance(arr, np.ndarray) and arr.shape == shape and arr.dtype == np.float64, name
    with pytest.raises(dataclasses.FrozenInstanceError):
        res.angle = res.bias


def test_KI5_new_metrics_return_floats():
    r = run("S4", 0)
    vals = [M.convergence_time(r.t, r.kf.bias, r.bias_true, tol=1e-3, t_start=60.0),
            M.convergence_time(r.t, r.kf.bias, r.bias_true, tol=1e-12),  # likely inf
            M.coverage_fraction(r.kf.bias, r.bias_true, np.sqrt(r.kf.cov[:, 1, 1]))]
    for v in vals:
        assert isinstance(v, (float, np.floating)) and np.ndim(v) == 0
    assert isinstance(F.kalman_noise_matrices(0.01, 0.005, 0.05, 1e-4)[1], (float, np.floating))


def test_KI5_simulatedimu_gains_gyro_bias_true():
    sim = imu_sim.simulate_pitch_imu(duration=5.0, seed=0, gyro_bias_rw_std=1e-4)
    names = [f.name for f in dataclasses.fields(sim)]
    assert names == ["t", "gyro", "accel", "roll_true", "pitch_true", "gyro_bias", "fs", "gyro_bias_true"]
    assert isinstance(sim.gyro_bias_true, np.ndarray)
    assert sim.gyro_bias_true.shape == (500, 3) and sim.gyro_bias_true.dtype == np.float64
    assert sim.gyro_bias.shape == (3,)


# ---------------------------------------------------------------- KI6
def test_KI6_kalman_pitch_speed_n60000():
    r = run("S3", 0)
    assert r.t.size == 60000
    rate, ap = r.sim.gyro[:, 1], r.accel
    times = []
    for _ in range(3):
        start = time.perf_counter()
        F.kalman_pitch(r.t, rate, ap)
        times.append(time.perf_counter() - start)
    assert min(times) < 2.0, f"best of 3: {min(times):.2f} s"


# ---------------------------------------------------------------- KR1
TIER1_FILES = ["test_performance.py", "test_deterministic.py", "test_simulator_stats.py",
               "test_interface.py", "test_plots_notebook.py"]


def test_KR1_tier1_suite_still_passes():
    """Runs the Tier 1 test files in a subprocess.

    The two Tier 1 notebook tests (G2) are deselected here because they run in the main
    session anyway and would double the notebook time budget.
    """
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
           "-k", "not G2_notebook"] + [str(TESTS_DIR / f) for f in TIER1_FILES]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=280)
    assert r.returncode == 0, r.stdout[-4000:] + r.stderr[-2000:]


# ---------------------------------------------------------------- KG3
NOTEBOOK = ROOT / "tier2.ipynb"


def test_KG3_notebook_executes_under_180s(tmp_path):
    assert NOTEBOOK.exists(), "tier2.ipynb missing"
    env = {k: v for k, v in os.environ.items() if k != "MPLBACKEND"}
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    cmd = [sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute",
           "--output-dir", str(tmp_path), "--output", "tier2_executed.ipynb", str(NOTEBOOK)]
    start = time.perf_counter()
    try:
        r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=210)
    except subprocess.TimeoutExpired:
        pytest.fail("nbconvert did not finish within 210 s")
    elapsed = time.perf_counter() - start
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-4000:]
    assert elapsed < 180.0, f"notebook took {elapsed:.1f} s"


def test_KG3_notebook_passes_no_truth_or_sim_fields_to_filters():
    """Heuristic static check of spec 8: filters get sensor-spec constants, never a
    SimulatedIMU field named *_true or gyro_bias / gyro_bias_true."""
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    filter_names = {"accel_tilt", "gyro_integrate", "complementary_filter", "kalman_pitch",
                    "kalman_noise_matrices"}
    banned_attrs = {"gyro_bias", "gyro_bias_true"}
    calls = {name: 0 for name in filter_names}
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        src = cell["source"]
        src = "".join(src) if isinstance(src, list) else src
        src = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith(("%", "!")))
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
            if name not in filter_names:
                continue
            calls[name] += 1
            for arg in list(node.args) + [kw.value for kw in node.keywords]:
                for sub in ast.walk(arg):
                    ident = getattr(sub, "attr", None) or getattr(sub, "id", None) or ""
                    assert "_true" not in ident and ident not in banned_attrs, \
                        f"{name}() receives ground truth or a simulator field ({ident})"
    assert calls["kalman_pitch"] >= 1, "notebook should call kalman_pitch"
