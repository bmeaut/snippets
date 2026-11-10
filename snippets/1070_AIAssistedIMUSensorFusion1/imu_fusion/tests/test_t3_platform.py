"""Tier 3 spec 2.1 (platform, binding for all modules and tests incl. Tiers 1-2) - static checks.

These are not numbered §11 criteria; they are added because spec 2.1 makes the Python 3.9 rules
binding. They are source-level heuristics that also work when the suite runs on a newer Python.
Python 3.9-valid syntax.
"""
import ast
import re
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent
ROOT = TESTS_DIR.parent

MODULE_FILES = sorted(ROOT.glob("imu_*.py"))
TEST_FILES = sorted(TESTS_DIR.glob("*.py"))
ALL_FILES = MODULE_FILES + TEST_FILES


def _tree(path):
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path), feature_version=(3, 9))


def _has_future_annotations(tree):
    return any(isinstance(n, ast.ImportFrom) and n.module == "__future__"
               and any(a.name == "annotations" for a in n.names) for n in tree.body)


def _annotations(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = node.args
            for a in args.posonlyargs + args.args + args.kwonlyargs + [args.vararg, args.kwarg]:
                if a is not None and a.annotation is not None:
                    yield a.annotation
            if node.returns is not None:
                yield node.returns
        elif isinstance(node, ast.AnnAssign):
            yield node.annotation


def _contains_bitor(node):
    return any(isinstance(n, ast.BinOp) and isinstance(n.op, ast.BitOr) for n in ast.walk(node))


def test_modules_exist():
    names = {p.name for p in MODULE_FILES}
    assert {"imu_sim.py", "imu_filters.py", "imu_metrics.py", "imu_plots.py", "imu_io.py"} <= names


@pytest.mark.parametrize("path", ALL_FILES, ids=lambda p: p.name)
def test_syntax_is_python39(path):
    _tree(path)


@pytest.mark.parametrize("path", ALL_FILES, ids=lambda p: p.name)
def test_no_python310_constructs(path):
    tree = _tree(path)
    problems = []
    for node in ast.walk(tree):
        if hasattr(ast, "Match") and isinstance(node, ast.Match):
            problems.append("match statement at line %d" % node.lineno)
        if hasattr(ast, "TryStar") and isinstance(node, ast.TryStar):
            problems.append("except* at line %d" % node.lineno)
        if isinstance(node, ast.Call):
            fn = node.func
            name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
            kws = {k.arg for k in node.keywords}
            if name == "zip" and "strict" in kws:
                problems.append("zip(strict=...) at line %d" % node.lineno)
            if name == "pairwise":
                problems.append("pairwise at line %d" % node.lineno)
            if name == "dataclass" and kws & {"slots", "kw_only"}:
                problems.append("dataclass(slots/kw_only) at line %d" % node.lineno)
            if name == "isinstance" and len(node.args) == 2 and _contains_bitor(node.args[1]):
                problems.append("isinstance with X | Y at line %d" % node.lineno)
        if isinstance(node, ast.ImportFrom):
            if node.module == "itertools" and any(a.name == "pairwise" for a in node.names):
                problems.append("itertools.pairwise import at line %d" % node.lineno)
            if node.module == "typing" and any(a.name in ("TypeAlias", "ParamSpec", "Self") for a in node.names):
                problems.append("typing.TypeAlias/ParamSpec/Self at line %d" % node.lineno)
            if node.module and node.module.split(".")[0] == "tomllib":
                problems.append("tomllib at line %d" % node.lineno)
        if isinstance(node, ast.Import) and any(a.name.split(".")[0] == "tomllib" for a in node.names):
            problems.append("tomllib at line %d" % node.lineno)
        if isinstance(node, ast.Attribute) and node.attr in ("unstack", "cumulative_sum", "cumulative_prod"):
            problems.append("NumPy >= 2.1 API %s at line %d" % (node.attr, node.lineno))
    if not _has_future_annotations(tree):
        for ann in _annotations(tree):
            if _contains_bitor(ann):
                problems.append("X | Y in an annotation at line %d (needs Optional/Union or "
                                "'from __future__ import annotations')" % ann.lineno)
    text = path.read_text(encoding="utf-8")
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        m = re.match(r"^(async\s+)?with\s*\((.*)$", stripped)
        if m and (stripped.endswith("(") or re.search(r"\bas\b", m.group(2))):
            problems.append("parenthesized multi-item with at line %d" % i)
    assert not problems, "%s: %s" % (path.name, "; ".join(problems))


@pytest.mark.parametrize("path", MODULE_FILES, ids=lambda p: p.name)
def test_modules_do_not_import_ipywidgets_and_only_io_imports_pandas(path):
    tree = _tree(path)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert "ipywidgets" not in imported
    if path.name != "imu_io.py":
        assert "pandas" not in imported


def test_import_rules_between_modules_are_respected_statically():
    def imported(name):
        tree = _tree(ROOT / name)
        out = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                out.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                out.add(node.module.split(".")[0])
        return out

    assert not imported("imu_filters.py") & {"imu_sim", "imu_metrics", "imu_plots", "imu_io", "pandas", "matplotlib"}
    assert not imported("imu_io.py") & {"imu_sim", "imu_filters", "imu_plots"}
