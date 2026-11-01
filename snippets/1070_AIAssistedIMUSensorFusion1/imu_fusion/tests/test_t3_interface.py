"""Tier 3 spec 11.7 - interface (RI1-RI7) and notebook (RG3)."""
import ast
import copy
import dataclasses
import inspect
import io
import json
import os
import subprocess
import sys
import time
import tokenize
import zipfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import numpy as np  # noqa: E402
import pytest  # noqa: E402

import imu_filters as F  # noqa: E402
import imu_io  # noqa: E402
import imu_plots  # noqa: E402
import imu_sim  # noqa: E402
from tier3_helpers import ACCEL_HEADER, GYRO_HEADER, csv_text, sim_run, write_zip  # noqa: E402

TESTS_DIR = Path(__file__).resolve().parent
ROOT = TESTS_DIR.parent


# ---------------------------------------------------------------- RI1
def _fresh(code):
    env = dict(os.environ, PYTHONPATH=str(ROOT))
    return subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), env=env,
                          capture_output=True, text=True, timeout=120)


def test_RI1_filters_import_isolation():
    code = ("import sys, imu_filters\n"
            "names = ('imu_sim', 'imu_metrics', 'imu_plots', 'imu_io', 'pandas', 'matplotlib')\n"
            "bad = [m for m in names if m in sys.modules]\n"
            "print(bad)\nsys.exit(1 if bad else 0)")
    r = _fresh(code)
    assert r.returncode == 0, r.stdout + r.stderr


def test_RI1_io_import_isolation():
    code = ("import sys, imu_io\n"
            "names = ('imu_sim', 'imu_filters', 'imu_plots')\n"
            "bad = [m for m in names if m in sys.modules]\n"
            "print(bad)\nsys.exit(1 if bad else 0)")
    r = _fresh(code)
    assert r.returncode == 0, r.stdout + r.stderr


def test_RI1_extra_earlier_isolation_rules_still_hold():
    code = ("import sys, imu_metrics\nsys.exit(1 if 'imu_sim' in sys.modules else 0)")
    assert _fresh(code).returncode == 0
    code = ("import sys, imu_filters\n"
            "sys.exit(1 if any(m in sys.modules for m in ('imu_sim','imu_metrics','imu_plots')) else 0)")
    assert _fresh(code).returncode == 0


# ---------------------------------------------------------------- RI2
EMPTY = inspect.Parameter.empty
SIGNATURES = {
    (imu_sim, "simulate_roll_pitch_imu"): [
        ("duration", 120.0), ("fs", 100.0), ("trajectory", None), ("gyro_bias", (0.01, 0.01, 0.01)),
        ("gyro_noise_std", 0.005), ("accel_noise_std", 0.05), ("seed", None),
        ("linear_accel_segments", ()), ("vibration_segments", ())],
    (imu_sim, "default_roll_pitch_trajectory"): [("t", EMPTY)],
    (imu_sim, "constant_roll_pitch_trajectory"): [("roll", EMPTY), ("pitch", EMPTY)],
    (F, "complementary_roll_pitch"): [
        ("t", EMPTY), ("gyro", EMPTY), ("accel", EMPTY), ("tau", 0.2),
        ("gyro_bias", (0.0, 0.0, 0.0)), ("initial_roll", None), ("initial_pitch", None)],
    (F, "estimate_stationary"): [("t", EMPTY), ("gyro", EMPTY), ("accel", EMPTY),
                                 ("t_start", EMPTY), ("t_end", EMPTY)],
    (F, "kalman_roll_pitch"): [
        ("t", EMPTY), ("gyro", EMPTY), ("accel", EMPTY), ("gyro_noise_std", 0.005),
        ("accel_noise_std", 0.05), ("bias_rw_std", 1e-4), ("gravity", 9.81), ("gyro_bias_z", 0.0),
        ("initial_bias", (0.0, 0.0)), ("gate_threshold", None), ("gate_hold", 0.2),
        ("gate_r_scale", 1e4), ("initial_roll", None), ("initial_pitch", None)],
    (imu_io, "load_phyphox_zip"): [("path", EMPTY)],
    (imu_io, "resample_common"): [("accel_t", EMPTY), ("accel", EMPTY), ("gyro_t", EMPTY),
                                  ("gyro", EMPTY), ("fs", 100.0)],
    (imu_plots, "plot_error_comparison"): [
        ("t", EMPTY), ("truth", EMPTY), ("estimates", EMPTY), ("exclude", ("gyro",)),
        ("t_window", None), ("title", ""), ("background", ("accel",)), ("shade", None)],
    (imu_plots, "plot_estimates"): [("t", EMPTY), ("estimates", EMPTY), ("title", ""), ("shade", None)],
}


@pytest.mark.parametrize("key", list(SIGNATURES), ids=lambda k: k[1])
def test_RI2_signatures(key):
    module, name = key
    expected = SIGNATURES[key]
    params = list(inspect.signature(getattr(module, name)).parameters.values())
    assert [p.name for p in params] == [n for n, _ in expected]
    for p, (n, default) in zip(params, expected):
        if default is EMPTY:
            assert p.default is EMPTY, n
        elif isinstance(default, tuple):          # any sequence/array equal to the tuple
            assert p.default is not EMPTY, n
            if all(isinstance(x, float) for x in default):
                assert np.array_equal(np.asarray(p.default, dtype=float), default), n
            else:
                assert tuple(p.default) == default, n
        else:
            assert p.default == default and type(p.default) is type(default), n


# ---------------------------------------------------------------- RI3
def _t(n=5):
    return np.arange(n, dtype=float) * 0.01


def _inputs(n=5):
    return _t(n), np.zeros((n, 3)), np.tile([0.0, 0.0, 9.81], (n, 1))


def _shape_time_cases(call, prefix):
    """The shape/time error cases of spec 6.2, applied to `call(t, gyro, accel)`."""
    t, g, a = _inputs()
    t_equal = t.copy(); t_equal[2] = t_equal[1]
    return {
        prefix + "_t_2d": lambda: call(t.reshape(5, 1), g, a),
        prefix + "_gyro_2cols": lambda: call(t, np.zeros((5, 2)), a),
        prefix + "_gyro_4cols": lambda: call(t, np.zeros((5, 4)), a),
        prefix + "_gyro_1d": lambda: call(t, np.zeros(5), a),
        prefix + "_gyro_short": lambda: call(t, np.zeros((4, 3)), a),
        prefix + "_accel_2cols": lambda: call(t, g, np.ones((5, 2))),
        prefix + "_accel_1d": lambda: call(t, g, np.ones(5)),
        prefix + "_accel_short": lambda: call(t, g, np.ones((4, 3))),
        prefix + "_t_short": lambda: call(t[:4], g, a),
        prefix + "_empty": lambda: call(np.array([]), np.zeros((0, 3)), np.zeros((0, 3))),
        prefix + "_t_equal": lambda: call(t_equal, g, a),
        prefix + "_t_decreasing": lambda: call(t[::-1].copy(), g, a),
    }


def _all_cases():
    cases = {}
    t, g, a = _inputs()
    CF, KF = F.complementary_roll_pitch, F.kalman_roll_pitch
    cases.update(_shape_time_cases(lambda *x: CF(*x), "cf"))
    cases.update({
        "cf_tau_zero": lambda: CF(t, g, a, tau=0.0),
        "cf_tau_negative": lambda: CF(t, g, a, tau=-0.2),
        "cf_bias_len2": lambda: CF(t, g, a, gyro_bias=(0.0, 0.0)),
        "cf_bias_len4": lambda: CF(t, g, a, gyro_bias=(0.0, 0.0, 0.0, 0.0)),
        "cf_bias_column": lambda: CF(t, g, a, gyro_bias=np.zeros((3, 1))),
    })
    cases.update(_shape_time_cases(lambda *x: KF(*x), "kf"))
    cases.update({
        "kf_gyro_noise_zero": lambda: KF(t, g, a, gyro_noise_std=0.0),
        "kf_gyro_noise_negative": lambda: KF(t, g, a, gyro_noise_std=-0.005),
        "kf_accel_noise_zero": lambda: KF(t, g, a, accel_noise_std=0.0),
        "kf_accel_noise_negative": lambda: KF(t, g, a, accel_noise_std=-0.05),
        "kf_bias_rw_negative": lambda: KF(t, g, a, bias_rw_std=-1e-4),
        "kf_gravity_zero": lambda: KF(t, g, a, gravity=0.0),
        "kf_gravity_negative": lambda: KF(t, g, a, gravity=-9.81),
        "kf_gate_threshold_zero": lambda: KF(t, g, a, gate_threshold=0.0),
        "kf_gate_threshold_negative": lambda: KF(t, g, a, gate_threshold=-0.2),
        "kf_gate_hold_negative": lambda: KF(t, g, a, gate_threshold=0.2, gate_hold=-0.1),
        "kf_gate_hold_negative_gate_off": lambda: KF(t, g, a, gate_hold=-0.1),
        "kf_gate_r_scale_below_1": lambda: KF(t, g, a, gate_threshold=0.2, gate_r_scale=0.5),
        "kf_gate_r_scale_zero": lambda: KF(t, g, a, gate_threshold=0.2, gate_r_scale=0.0),
        "kf_gate_r_scale_negative": lambda: KF(t, g, a, gate_threshold=0.2, gate_r_scale=-10.0),
        "kf_initial_bias_len1": lambda: KF(t, g, a, initial_bias=(0.01,)),
        "kf_initial_bias_len3": lambda: KF(t, g, a, initial_bias=(0.01, 0.0, 0.0)),
    })
    # estimate_stationary: spec 6.3
    tt = np.arange(100) * 0.5
    gg, aa = np.zeros((100, 3)), np.tile([0.0, 0.0, 9.81], (100, 1))
    ES = F.estimate_stationary
    cases.update({
        "es_nine_samples": lambda: ES(tt, gg, aa, 0.0, 4.0),
        "es_no_samples": lambda: ES(tt, gg, aa, 1000.0, 2000.0),
        "es_one_sample": lambda: ES(tt, gg, aa, 5.0, 5.2),
        "es_t_start_equals_t_end": lambda: ES(tt, gg, aa, 5.0, 5.0),
        "es_t_start_after_t_end": lambda: ES(tt, gg, aa, 10.0, 5.0),
        "es_t_2d": lambda: ES(tt.reshape(100, 1), gg, aa, 0.0, 20.0),
        "es_gyro_2cols": lambda: ES(tt, np.zeros((100, 2)), aa, 0.0, 20.0),
        "es_gyro_1d": lambda: ES(tt, np.zeros(100), aa, 0.0, 20.0),
        "es_gyro_short": lambda: ES(tt, np.zeros((99, 3)), aa, 0.0, 20.0),
        "es_accel_2cols": lambda: ES(tt, gg, np.ones((100, 2)), 0.0, 20.0),
        "es_accel_1d": lambda: ES(tt, gg, np.ones(100), 0.0, 20.0),
        "es_accel_short": lambda: ES(tt, gg, np.ones((99, 3)), 0.0, 20.0),
        "es_t_short": lambda: ES(tt[:99], gg, aa, 0.0, 20.0),
    })
    return cases


ALL_CASES = _all_cases()


@pytest.mark.parametrize("call", list(ALL_CASES.values()), ids=list(ALL_CASES))
def test_RI3_value_errors(call):
    with pytest.raises(ValueError):
        call()


def test_RI3_negative_controls_are_accepted():
    t, g, a = _inputs()
    F.kalman_roll_pitch(t, g, a, gate_hold=0.0, gate_threshold=0.2)
    F.kalman_roll_pitch(t, g, a, gate_r_scale=1.0, gate_threshold=0.2)
    F.kalman_roll_pitch(t, g, a, bias_rw_std=0.0)
    F.kalman_roll_pitch(t, g, a, gate_threshold=1e-9)
    F.kalman_roll_pitch(t, g, a, initial_bias=[0.01, -0.01])
    F.kalman_roll_pitch(t[:1], g[:1], a[:1])
    F.complementary_roll_pitch(t, g, a, gyro_bias=[0.0, 0.0, 0.0])
    tt = np.arange(100) * 0.5
    est = F.estimate_stationary(tt, np.zeros((100, 3)), np.tile([0.0, 0.0, 9.81], (100, 1)), 0.0, 4.5)
    assert est.n_samples == 10                       # exactly 10 samples are enough


def test_RI3_missing_file_raises_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        imu_io.load_phyphox_zip(str(tmp_path / "nope.zip"))


def test_RI3_io_value_errors_smoke(tmp_path):
    not_zip = tmp_path / "x.zip"
    not_zip.write_text("not a zip")
    with pytest.raises(ValueError):
        imu_io.load_phyphox_zip(str(not_zip))
    only_accel = write_zip(tmp_path / "one.zip", {"Accelerometer.csv": csv_text(
        ACCEL_HEADER, [["0", "0", "0", "9.8"], ["1", "0", "0", "9.8"]])})
    with pytest.raises(ValueError):
        imu_io.load_phyphox_zip(only_accel)
    with pytest.raises(ValueError):
        imu_io.resample_common(_t(5), np.zeros((5, 3)), _t(5), np.zeros((5, 3)), fs=0.0)


# ---------------------------------------------------------------- RI4
def _snap(*arrays):
    return [np.array(a, copy=True) for a in arrays]


def _assert_same(before, after):
    for b, a in zip(before, after):
        assert b.shape == a.shape and b.dtype == a.dtype
        assert np.array_equal(b, a, equal_nan=True)


def test_RI4_filters_do_not_modify_inputs():
    r = sim_run("S6", 0)
    t, g, a = r.t.copy(), r.sim.gyro.copy(), r.sim.accel.copy()
    bias, init_bias = np.array([0.01, 0.01, 0.01]), np.array([0.01, 0.01])
    before = _snap(t, g, a, bias, init_bias)
    res = F.kalman_roll_pitch(t, g, a, gyro_bias_z=0.01, initial_bias=init_bias, gate_threshold=0.2)
    cf = F.complementary_roll_pitch(t, g, a, gyro_bias=bias)
    est = F.estimate_stationary(t, g, a, 0.0, 4.5)
    _assert_same(before, _snap(t, g, a, bias, init_bias))
    outputs = [res.roll, res.pitch, res.bias_x, res.bias_y, res.cov_roll, res.cov_pitch, res.gated,
               cf[0], cf[1], est.gyro_bias]
    for out in outputs:
        for inp in (t, g, a, bias, init_bias):
            assert not np.shares_memory(out, inp)


def test_RI4_simulator_and_trajectories_do_not_modify_inputs():
    t = np.linspace(0.0, 20.0, 2001)
    bias = np.array([0.01, -0.02, 0.03])
    lin = [(10.0, 2.0, 3.0, 0.7)]
    vib = [(12.0, 1.0, 2.0, 15.0, 0.05)]
    lin_before, vib_before = copy.deepcopy(lin), copy.deepcopy(vib)
    before = _snap(t, bias)
    imu_sim.default_roll_pitch_trajectory(t)
    imu_sim.constant_roll_pitch_trajectory(0.1, 0.2)(t)
    imu_sim.simulate_roll_pitch_imu(duration=20.0, gyro_bias=bias, linear_accel_segments=lin,
                                    vibration_segments=vib, seed=0)
    _assert_same(before, _snap(t, bias))
    assert lin == lin_before and vib == vib_before
    assert imu_sim.DEFAULT_LINEAR_ACCEL_SEGMENTS[0] == (30.0, 2.0, 3.0, 0.0)


def test_RI4_resample_and_loader_do_not_modify_inputs(tmp_path):
    rows = [["%.9E" % v for v in (0.01 * i, 0.1, 0.2, 9.8)] for i in range(50)]
    path = write_zip(tmp_path / "r.zip", {"Accelerometer.csv": csv_text(ACCEL_HEADER, rows),
                                          "Gyroscope.csv": csv_text(GYRO_HEADER, rows)})
    bytes_before = Path(path).read_bytes()
    rec = imu_io.load_phyphox_zip(path)
    assert Path(path).read_bytes() == bytes_before
    before = _snap(rec.accel_t, rec.accel, rec.gyro_t, rec.gyro)
    out = imu_io.resample_common(rec.accel_t, rec.accel, rec.gyro_t, rec.gyro, fs=100.0)
    _assert_same(before, _snap(rec.accel_t, rec.accel, rec.gyro_t, rec.gyro))
    for arr in out:
        for inp in (rec.accel_t, rec.accel, rec.gyro_t, rec.gyro):
            assert not np.shares_memory(arr, inp)


def test_RI4_plots_do_not_modify_inputs():
    r = sim_run("S7", 0)
    t, truth = r.t.copy(), r.truth[0].copy()
    ests = {"gyro": truth + 0.01, "accel": r.angles["accel"][0].copy(), "CF": r.angles["CF"][0].copy(),
            "KF": r.angles["KF"][0].copy()}
    shade = r.sim.disturbed_true.copy()
    keys, background, exclude = list(ests), ("accel",), ("gyro",)
    before = _snap(t, truth, shade, *ests.values())
    imu_plots.plot_error_comparison(t, truth, ests, exclude=exclude, t_window=(28, 40), background=background,
                                    shade=shade)
    imu_plots.plot_estimates(t, ests, shade=shade)
    assert list(ests) == keys and background == ("accel",) and exclude == ("gyro",)
    _assert_same(before, _snap(t, truth, shade, *ests.values()))


# ---------------------------------------------------------------- RI5
def _vec(a, n, dtype=np.float64):
    return isinstance(a, np.ndarray) and a.shape == (n,) and a.dtype == dtype


def test_RI5_simulated_roll_pitch_imu_shapes_and_dtypes():
    sim = imu_sim.simulate_roll_pitch_imu(duration=5.0, seed=0, linear_accel_segments=((1.0, 1.0, 1.0, 0.0),))
    n = 500
    assert dataclasses.is_dataclass(sim) and type(sim).__dataclass_params__.frozen is True
    for name in ("t", "roll_true", "pitch_true"):
        assert _vec(getattr(sim, name), n), name
    for name in ("gyro", "accel"):
        arr = getattr(sim, name)
        assert arr.shape == (n, 3) and arr.dtype == np.float64, name
    assert sim.gyro_bias.shape == (3,) and sim.gyro_bias.dtype == np.float64
    assert isinstance(sim.fs, (float, np.floating))
    assert _vec(sim.disturbed_true, n, dtype=np.bool_) and sim.disturbed_true.dtype == bool
    roll, pitch, roll_rate, pitch_rate = imu_sim.default_roll_pitch_trajectory(sim.t)
    for out in (roll, pitch, roll_rate, pitch_rate):
        assert _vec(out, n)
    with pytest.raises(dataclasses.FrozenInstanceError):
        sim.fs = 1.0


def test_RI5_filter_outputs_shapes_and_dtypes():
    r = sim_run("S7", 0)
    n = r.t.size
    for res in (r.kf, r.kfg):
        assert dataclasses.is_dataclass(res) and type(res).__dataclass_params__.frozen is True
        assert [f.name for f in dataclasses.fields(res)] == [
            "roll", "pitch", "bias_x", "bias_y", "cov_roll", "cov_pitch", "gated"]
        for name in ("roll", "pitch", "bias_x", "bias_y"):
            assert _vec(getattr(res, name), n), name
        for name in ("cov_roll", "cov_pitch"):
            arr = getattr(res, name)
            assert isinstance(arr, np.ndarray) and arr.shape == (n, 2, 2) and arr.dtype == np.float64, name
        assert _vec(res.gated, n, dtype=np.bool_) and res.gated.dtype == bool
    assert not r.kf.gated.any() and r.kfg.gated.any()
    roll, pitch = r.angles["CF"]
    assert isinstance(r.angles["CF"], tuple) and len(r.angles["CF"]) == 2
    assert _vec(roll, n) and _vec(pitch, n)
    with pytest.raises(dataclasses.FrozenInstanceError):
        r.kf.roll = r.kf.pitch


def test_RI5_stationary_estimate_fields():
    est = sim_run("S6", 0).est
    assert dataclasses.is_dataclass(est) and type(est).__dataclass_params__.frozen is True
    assert {f.name for f in dataclasses.fields(est)} == {
        "gyro_bias", "gyro_noise_std", "accel_noise_std", "gravity", "n_samples"}
    assert isinstance(est.gyro_bias, np.ndarray) and est.gyro_bias.shape == (3,)
    assert est.gyro_bias.dtype == np.float64
    for v in (est.gyro_noise_std, est.accel_noise_std, est.gravity):
        assert isinstance(v, (float, np.floating)) and np.ndim(v) == 0
    assert isinstance(est.n_samples, (int, np.integer)) and not isinstance(est.n_samples, bool)
    with pytest.raises(dataclasses.FrozenInstanceError):
        est.gravity = 1.0


def test_RI5_phyphox_recording_and_resample_dtypes(tmp_path):
    rows_a = [["%.9E" % v for v in (0.01 * i, 0.1, 0.2, 9.8)] for i in range(60)]
    rows_g = [["%.9E" % v for v in (0.01 * i + 0.003, 0.01, 0.02, 0.03)] for i in range(60)]
    path = write_zip(tmp_path / "r.zip", {"Accelerometer.csv": csv_text(ACCEL_HEADER, rows_a),
                                          "Gyroscope.csv": csv_text(GYRO_HEADER, rows_g)})
    rec = imu_io.load_phyphox_zip(path)
    assert dataclasses.is_dataclass(rec) and type(rec).__dataclass_params__.frozen is True
    assert [f.name for f in dataclasses.fields(rec)] == ["accel_t", "accel", "gyro_t", "gyro", "source"]
    assert _vec(rec.accel_t, 60) and _vec(rec.gyro_t, 60)
    assert rec.accel.shape == (60, 3) and rec.accel.dtype == np.float64
    assert rec.gyro.shape == (60, 3) and rec.gyro.dtype == np.float64
    assert isinstance(rec.source, str)
    t, gyro, accel = imu_io.resample_common(rec.accel_t, rec.accel, rec.gyro_t, rec.gyro)
    m = t.size
    assert _vec(t, m) and gyro.shape == (m, 3) and accel.shape == (m, 3)
    assert gyro.dtype == np.float64 and accel.dtype == np.float64
    with pytest.raises(dataclasses.FrozenInstanceError):
        rec.source = "x"


# ---------------------------------------------------------------- RI6
def test_RI6_kalman_roll_pitch_speed_n60000():
    sim = imu_sim.simulate_roll_pitch_imu(duration=600.0, seed=0)
    assert sim.t.size == 60000
    times = []
    for _ in range(3):
        start = time.perf_counter()
        F.kalman_roll_pitch(sim.t, sim.gyro, sim.accel)
        times.append(time.perf_counter() - start)
    assert min(times) < 8.0, "best of 3: %.2f s" % min(times)


# ---------------------------------------------------------------- RI7
TIER1_FILES = ["test_performance.py", "test_deterministic.py", "test_simulator_stats.py",
               "test_interface.py", "test_plots_notebook.py"]
TIER2_FILES = ["test_t2_simulator.py", "test_t2_filter.py", "test_t2_performance.py",
               "test_t2_metrics_plots.py", "test_t2_interface.py"]


def test_RI7_tier1_and_tier2_suites_still_pass():
    """Runs the Tier 1 and Tier 2 test files in a subprocess.

    Deselected here, because they run in the main session anyway and would double the notebook
    time: the Tier 1 and Tier 2 notebook tests. KR1 (which itself runs the Tier 1 files) is
    deselected because the Tier 1 files are run directly.
    """
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
           "-k", "not G2_notebook and not KG3_notebook and not KR1"]
    cmd += [str(TESTS_DIR / f) for f in TIER1_FILES + TIER2_FILES]
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stdout[-4000:] + r.stderr[-2000:]


# ---------------------------------------------------------------- RG3
NOTEBOOK = ROOT / "tier3.ipynb"


def _at_statement_start(preceding_lines):
    """True if the text of preceding_lines ends outside any open bracket, string or backslash continuation."""
    if not preceding_lines:
        return True
    text = "\n".join(preceding_lines) + "\n"
    try:
        for _ in tokenize.generate_tokens(io.StringIO(text).readline):
            pass
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return False
    return True


def _strip_ipython_lines(src):
    """Replace real IPython magic / shell lines by 'pass'.

    A line is a magic only if it starts (after indentation) with '%' or '!' AND it begins a new
    statement; continuation lines of an open bracket (e.g. '% (a, b)' of a %-format) are kept.
    """
    lines = src.splitlines()
    out = []
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith(("%", "!")) and _at_statement_start(lines[:i]):
            out.append(line[:len(line) - len(stripped)] + "pass")
        else:
            out.append(line)
    return "\n".join(out)


def _notebook_code_cells():
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        src = cell["source"]
        src = "".join(src) if isinstance(src, list) else src
        yield _strip_ipython_lines(src)


def test_RG3_notebook_executes_under_240s(tmp_path):
    assert NOTEBOOK.exists(), "tier3.ipynb missing"
    env = {k: v for k, v in os.environ.items() if k != "MPLBACKEND"}
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    cmd = [sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute",
           "--output-dir", str(tmp_path), "--output", "tier3_executed.ipynb", str(NOTEBOOK)]
    start = time.perf_counter()
    try:
        r = subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=280)
    except subprocess.TimeoutExpired:
        pytest.fail("nbconvert did not finish within 280 s")
    elapsed = time.perf_counter() - start
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-4000:]
    assert elapsed < 240.0, "notebook took %.1f s" % elapsed


def test_RG3_notebook_passes_no_ground_truth_to_filters():
    """Heuristic static check of spec 10: no *_true expression appears in a filter call."""
    filter_names = {"accel_tilt", "complementary_roll_pitch", "kalman_roll_pitch", "estimate_stationary",
                    "gyro_integrate", "complementary_filter", "kalman_pitch"}
    n_calls = 0
    for src in _notebook_code_cells():
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
            n_calls += 1
            for arg in list(node.args) + [kw.value for kw in node.keywords]:
                for sub in ast.walk(arg):
                    ident = getattr(sub, "attr", None) or getattr(sub, "id", None) or ""
                    assert "_true" not in ident, "%s() receives ground truth (%s)" % (name, ident)
    assert n_calls >= 4, "notebook should call the Tier 3 estimators"


def test_RG3_notebook_code_is_python39_syntax():
    for src in _notebook_code_cells():
        ast.parse(src, feature_version=(3, 9))


def test_RG3_notebook_listed_keys_and_section_titles_are_present():
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    code = "\n".join(_notebook_code_cells())
    for key in ('"accel"', '"CF"', '"KF"', '"KF-gated"'):
        assert key in code.replace("'", '"'), "estimate key %s not used in the notebook" % key
    markdown = "\n".join("".join(c["source"]) if isinstance(c["source"], list) else c["source"]
                         for c in nb["cells"] if c["cell_type"] == "markdown").lower()
    for word in ("clean", "disturbance", "real", "interactive", "discussion"):
        assert word in markdown, "no markdown mentioning %r" % word
