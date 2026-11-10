"""Scenario runner for the Tier 2 tests (tier2_spec.md section 9).

Results are cached per (scenario, seed) so each simulation + filter run happens once
per pytest session. Tests must treat the returned arrays as read-only.
"""
import functools
from types import SimpleNamespace

# Spec 9 scenario table: simulator arguments (all others at defaults) and seeds.
SCENARIOS = {
    "S1": {},
    "S2": dict(duration=600.0),
    "S3": dict(duration=600.0, gyro_bias_rw_std=1e-4),
    "S4": dict(duration=120.0, bias_step=(60.0, 0.01)),
    "S5": dict(duration=120.0, gyro_bias_rw_std=1e-4),
}
SEEDS = {
    "S1": tuple(range(10)),
    "S2": tuple(range(5)),
    "S3": tuple(range(5)),
    "S4": tuple(range(5)),
    "S5": tuple(range(3)),
}


@functools.lru_cache(maxsize=None)
def run(scenario, seed):
    """Simulate `scenario` with `seed`; run gyro, accel, CF (tau=0.2) and KF (defaults)."""
    import imu_filters as F
    import imu_sim

    sim = imu_sim.simulate_pitch_imu(seed=seed, **SCENARIOS[scenario])
    rate = sim.gyro[:, 1]
    accel_pitch = F.accel_tilt(sim.accel)[1]
    return SimpleNamespace(
        sim=sim,
        t=sim.t,
        truth=sim.pitch_true,
        bias_true=sim.gyro_bias_true[:, 1],
        accel=accel_pitch,
        gyro=F.gyro_integrate(sim.t, rate, 0.0),
        cf=F.complementary_filter(sim.t, rate, accel_pitch, tau=0.2),
        kf=F.kalman_pitch(sim.t, rate, accel_pitch),
    )
