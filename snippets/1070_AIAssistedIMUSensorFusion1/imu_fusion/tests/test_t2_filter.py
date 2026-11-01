"""Tier 2 spec 9.4 - deterministic Kalman-filter correctness and tuning (KD1-KD6, KT1-KT2)."""
import time

import numpy as np
import pytest

import imu_filters as F
import imu_sim
import tier2_reference as ref2
from tier2_helpers import SCENARIOS, SEEDS, run

import imu_metrics as M

R_DEFAULT = (0.05 / 9.81) ** 2


# ---------------------------------------------------------------- KD1
def test_KD1_noise_matrices_reference_values():
    Q, R = F.kalman_noise_matrices(0.01, 0.005, 0.05, 1e-4)
    Q = np.asarray(Q)
    assert Q.shape == (2, 2) and Q.dtype == np.float64
    np.testing.assert_allclose(np.diag(Q), [2.5e-9, 1e-10], rtol=1e-12, atol=0)
    assert Q[0, 1] == 0 and Q[1, 0] == 0
    assert isinstance(R, (float, np.floating))
    np.testing.assert_allclose(R, (0.05 / 9.81) ** 2, rtol=1e-12, atol=0)


@pytest.mark.parametrize("dt,sg,sa,sb,g", [
    (0.02, 0.008, 0.07, 3e-4, 9.80665),
    (0.5, 0.001, 0.2, 0.0, 9.81),
])
def test_KD1_noise_matrices_other_parameters(dt, sg, sa, sb, g):
    Q, R = F.kalman_noise_matrices(dt, sg, sa, sb, gravity=g)
    Q_ref, R_ref = ref2.ref_noise_matrices(dt, sg, sa, sb, g)
    np.testing.assert_allclose(Q[0, 0], Q_ref[0, 0], rtol=1e-12, atol=0)
    np.testing.assert_allclose(Q[1, 1], Q_ref[1, 1], rtol=1e-12, atol=0)
    assert Q[0, 1] == 0 and Q[1, 0] == 0
    np.testing.assert_allclose(R, R_ref, rtol=1e-12, atol=0)


# ---------------------------------------------------------------- KD2
def _random_problem(seed):
    rng = np.random.default_rng(2000 + seed)
    n = int(rng.integers(50, 300))
    dt = rng.uniform(0.005, 0.03, n - 1)  # non-uniform
    t = rng.uniform(-2.0, 2.0) + np.concatenate([[0.0], np.cumsum(dt)])
    gyro = rng.normal(0.0, 0.3, n)
    accel_angle = np.cumsum(rng.normal(0.0, 0.01, n)) + rng.normal(0.0, 0.003, n)
    return t, gyro, accel_angle


def _assert_matches_reference(got, want):
    a, b, c = want
    np.testing.assert_allclose(got.angle, a, rtol=0, atol=1e-10)
    np.testing.assert_allclose(got.bias, b, rtol=0, atol=1e-10)
    np.testing.assert_allclose(got.cov, c, rtol=1e-9, atol=1e-20)


@pytest.mark.parametrize("seed", range(5))
def test_KD2_recurrence_with_custom_parameters(seed):
    t, gyro, acc = _random_problem(seed)
    kw = dict(gyro_noise_std=0.008, accel_noise_std=0.07, bias_rw_std=3e-4, gravity=9.80,
              initial_angle=0.1, initial_bias=0.02,
              initial_cov=np.array([[2e-4, 1e-5], [1e-5, 5e-4]]))
    got = F.kalman_pitch(t, gyro, acc, **kw)
    _assert_matches_reference(got, ref2.ref_kalman_pitch(t, gyro, acc, **kw))


@pytest.mark.parametrize("seed", range(3))
def test_KD2_recurrence_with_defaults(seed):
    t, gyro, acc = _random_problem(100 + seed)
    got = F.kalman_pitch(t, gyro, acc)
    _assert_matches_reference(got, ref2.ref_kalman_pitch(t, gyro, acc))


def test_KD2_recurrence_initial_angle_only():
    t, gyro, acc = _random_problem(77)
    got = F.kalman_pitch(t, gyro, acc, initial_angle=-0.3)
    _assert_matches_reference(got, ref2.ref_kalman_pitch(t, gyro, acc, initial_angle=-0.3))


# ---------------------------------------------------------------- KD3
def test_KD3_constant_bias_noise_free():
    sim = imu_sim.simulate_pitch_imu(duration=60.0, trajectory=imu_sim.constant_pitch_trajectory(0.3),
                                     gyro_noise_std=0.0, accel_noise_std=0.0, seed=0)
    kf = F.kalman_pitch(sim.t, sim.gyro[:, 1], F.accel_tilt(sim.accel)[1])
    assert abs(kf.angle[-1] - 0.3) <= 1e-6
    assert abs(kf.bias[-1] - 0.01) <= 1e-6


# ---------------------------------------------------------------- KD4
def test_KD4_trapezoidal_integration_rule():
    sim = imu_sim.simulate_pitch_imu(duration=60.0, gyro_bias=(0.0, 0.0, 0.0),
                                     gyro_noise_std=0.0, accel_noise_std=0.0, seed=0)
    kf = F.kalman_pitch(sim.t, sim.gyro[:, 1], F.accel_tilt(sim.accel)[1])
    mask = sim.t >= 10.0
    assert np.max(np.abs(kf.angle[mask] - sim.pitch_true[mask])) <= 1e-4
    assert np.max(np.abs(kf.bias[mask])) <= 1e-4


# ---------------------------------------------------------------- KD5
def test_KD5_single_sample_defaults():
    t, gyro, acc = np.array([0.5]), np.array([0.3]), np.array([0.123])
    res = F.kalman_pitch(t, gyro, acc)
    assert res.angle.shape == (1,) and res.bias.shape == (1,) and res.cov.shape == (1, 2, 2)
    np.testing.assert_array_equal(res.angle, [0.123])
    np.testing.assert_array_equal(res.bias, [0.0])
    np.testing.assert_allclose(res.cov[0], np.diag([R_DEFAULT, 4e-4]), rtol=1e-12, atol=0)


def test_KD5_single_sample_with_initial_values():
    t, gyro, acc = np.array([0.5]), np.array([0.3]), np.array([0.123])
    cov0 = np.array([[3e-4, 1e-5], [1e-5, 6e-4]])
    res = F.kalman_pitch(t, gyro, acc, initial_angle=0.4, initial_bias=0.015, initial_cov=cov0)
    np.testing.assert_array_equal(res.angle, [0.4])
    np.testing.assert_array_equal(res.bias, [0.015])
    np.testing.assert_allclose(res.cov[0], cov0, rtol=1e-12, atol=0)


# ---------------------------------------------------------------- KD6
def test_KD6_covariance_sanity_on_s1():
    cov = run("S1", 0).kf.cov
    assert cov.shape == (6000, 2, 2)
    np.testing.assert_allclose(cov, cov.transpose(0, 2, 1), rtol=0, atol=1e-18)
    eig = np.linalg.eigvalsh(0.5 * (cov + cov.transpose(0, 2, 1)))
    assert np.all(eig > 0)
    assert np.all(cov[1:, 0, 0] < R_DEFAULT)


# ---------------------------------------------------------------- KT1 / KT2
SCALES = (0.1, 0.3, 1.0, 3.0, 10.0)


@pytest.fixture(scope="module")
def sweep():
    """KT1 grid: mean over seeds of KF angle RMSE (t >= 30 s) on S5, for each (sQ, sR).

    Returns (grid[len(SCALES), len(SCALES)] indexed [iQ, iR], elapsed seconds).
    The elapsed time includes the S5 simulations.
    """
    start = time.perf_counter()
    sims = [imu_sim.simulate_pitch_imu(seed=s, **SCENARIOS["S5"]) for s in SEEDS["S5"]]
    prepared = [(s.t, s.gyro[:, 1], F.accel_tilt(s.accel)[1], s.pitch_true, s.t >= 30.0) for s in sims]
    grid = np.empty((len(SCALES), len(SCALES)))
    for iq, sq in enumerate(SCALES):
        for ir, sr in enumerate(SCALES):
            vals = []
            for t, rate, ap, truth, mask in prepared:
                kf = F.kalman_pitch(t, rate, ap,
                                    gyro_noise_std=0.005 * np.sqrt(sq),
                                    bias_rw_std=1e-4 * np.sqrt(sq),
                                    accel_noise_std=0.05 * np.sqrt(sr))
                vals.append(M.rmse(kf.angle[mask], truth[mask]))
            grid[iq, ir] = np.mean(vals)
    return grid, time.perf_counter() - start


def test_KT1_nominal_tuning_is_near_optimal(sweep):
    grid, elapsed = sweep
    nominal = grid[SCALES.index(1.0), SCALES.index(1.0)]
    assert nominal <= 1.10 * grid.min(), f"nominal {np.rad2deg(nominal):.4f} deg vs min {np.rad2deg(grid.min()):.4f} deg"
    assert elapsed < 60.0, f"sweep took {elapsed:.1f} s"


def test_KT2_sweep_discriminates_between_settings(sweep):
    grid, elapsed = sweep
    nominal = grid[SCALES.index(1.0), SCALES.index(1.0)]
    assert grid.max() >= 1.25 * nominal
    assert elapsed < 60.0, f"sweep took {elapsed:.1f} s"
