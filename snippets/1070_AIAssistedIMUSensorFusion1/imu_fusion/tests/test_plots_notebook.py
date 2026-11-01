"""Spec 8.4 - plotting (G1) and notebook execution (G2)."""
import ast
import json
import os
import subprocess
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pytest  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

import imu_plots  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _data():
    rng = np.random.default_rng(7)
    t = np.arange(200) * 0.01
    truth = 0.5 * np.sin(2 * np.pi * 0.3 * t)
    ests = {"gyro": truth + 0.01 * t + rng.normal(0, 0.002, t.size),
            "accel": truth + rng.normal(0, 0.005, t.size),
            "cf": truth + rng.normal(0, 0.001, t.size)}
    return t, truth, ests


def test_G1_plot_comparison_structure_and_data():
    t, truth, ests = _data()
    fig = imu_plots.plot_comparison(t, truth, ests, title="demo")
    assert isinstance(fig, Figure)
    assert len(fig.axes) == 2
    ax0, ax1 = fig.axes
    assert len(ax0.lines) == 4
    assert len(ax1.lines) == 3

    assert [ln.get_label() for ln in ax0.lines] == ["truth", "gyro", "accel", "cf"]
    assert [ln.get_label() for ln in ax1.lines] == ["gyro", "accel", "cf"]

    for ln in list(ax0.lines) + list(ax1.lines):
        np.testing.assert_allclose(ln.get_xdata(), t, rtol=0, atol=1e-12)

    np.testing.assert_allclose(ax0.lines[0].get_ydata(), np.rad2deg(truth), rtol=0, atol=1e-9)
    for ln, (name, e) in zip(ax0.lines[1:], ests.items()):
        np.testing.assert_allclose(ln.get_ydata(), np.rad2deg(e), rtol=0, atol=1e-9)
    for ln, (name, e) in zip(ax1.lines, ests.items()):
        np.testing.assert_allclose(ln.get_ydata(), np.rad2deg(e - truth), rtol=0, atol=1e-9)

    for ax in (ax0, ax1):
        assert ax.get_legend() is not None
        assert ax.get_ylabel().strip() != ""
    assert ax1.get_xlabel().strip() != ""


def test_G1_plot_comparison_respects_insertion_order():
    t, truth, ests = _data()
    reordered = {"cf": ests["cf"], "gyro": ests["gyro"], "accel": ests["accel"]}
    fig = imu_plots.plot_comparison(t, truth, reordered)
    assert [ln.get_label() for ln in fig.axes[0].lines] == ["truth", "cf", "gyro", "accel"]
    assert [ln.get_label() for ln in fig.axes[1].lines] == ["cf", "gyro", "accel"]


def test_G1_plot_comparison_does_not_call_show(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("plt.show() must not be called")

    monkeypatch.setattr(plt, "show", boom)
    t, truth, ests = _data()
    imu_plots.plot_comparison(t, truth, ests, title="x")


# ---------------------------------------------------------------- G2
NOTEBOOK = os.path.join(ROOT, "tier1.ipynb")


def test_G2_notebook_executes_under_120s(tmp_path):
    assert os.path.exists(NOTEBOOK), "tier1.ipynb missing"
    env = {k: v for k, v in os.environ.items() if k != "MPLBACKEND"}
    env["PYTHONPATH"] = ROOT + os.pathsep + env.get("PYTHONPATH", "")
    cmd = [sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute",
           "--output-dir", str(tmp_path), "--output", "tier1_executed.ipynb", NOTEBOOK]
    start = time.perf_counter()
    try:
        r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=150)
    except subprocess.TimeoutExpired:
        pytest.fail("nbconvert did not finish within 150 s")
    elapsed = time.perf_counter() - start
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-4000:]
    assert elapsed < 120.0, f"notebook took {elapsed:.1f} s"


def test_G2_notebook_passes_no_truth_to_filters():
    """Heuristic static check of spec 7.2: no *_true expression appears in a filter call."""
    with open(NOTEBOOK, encoding="utf-8") as fh:
        nb = json.load(fh)
    filter_names = {"accel_tilt", "gyro_integrate", "complementary_filter"}
    n_calls = 0
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
            n_calls += 1
            for arg in list(node.args) + [kw.value for kw in node.keywords]:
                for sub in ast.walk(arg):
                    ident = getattr(sub, "attr", None) or getattr(sub, "id", None) or ""
                    assert "_true" not in ident, f"{name}() receives ground truth ({ident})"
    assert n_calls >= 3, "notebook should call all three estimators"
