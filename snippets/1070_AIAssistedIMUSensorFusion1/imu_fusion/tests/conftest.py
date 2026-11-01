"""Shared fixtures for the Tier 1 test-suite.

Only information from tier1_spec.md is used here. The scenarios (S1, S2) and the
estimator configuration are exactly those of spec section 8.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless; must happen before any pyplot import

import numpy as np  # noqa: E402
import pytest  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def estimate_pitch(sim):
    """Spec section 8 estimator configuration (gyro, accel, CF with tau=0.2)."""
    import imu_filters as F

    accel_pitch = F.accel_tilt(sim.accel)[1]
    return {
        "gyro": F.gyro_integrate(sim.t, sim.gyro[:, 1], 0.0),
        "accel": accel_pitch,
        "cf": F.complementary_filter(sim.t, sim.gyro[:, 1], accel_pitch, tau=0.2),
    }


def _build(seeds, **sim_kwargs):
    import imu_sim

    runs = {}
    for seed in seeds:
        sim = imu_sim.simulate_pitch_imu(seed=seed, **sim_kwargs)
        runs[seed] = (sim, estimate_pitch(sim))
    return runs


@pytest.fixture(scope="session")
def project_root():
    return ROOT


@pytest.fixture(scope="session")
def s1_runs():
    """S1: simulate_pitch_imu() with all defaults, seeds 0-9. {seed: (sim, estimates)}."""
    return _build(range(10))


@pytest.fixture(scope="session")
def s2_runs():
    """S2: simulate_pitch_imu(duration=600.0), seeds 0-4. {seed: (sim, estimates)}."""
    return _build(range(5), duration=600.0)


@pytest.fixture(autouse=True)
def _close_figures():
    yield
    import matplotlib.pyplot as plt

    plt.close("all")
