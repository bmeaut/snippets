#!/usr/bin/env python3
"""Generate tests/data/tier1_reference.npz  (Tier 2 spec, test KS1).

RUN THIS ONCE, ON THE CURRENT TIER 1 CODE, BEFORE INSTALLING ANY TIER 2 CHANGE.

    python tests/make_tier1_reference.py            # from project_root
    python tests/make_tier1_reference.py --force    # overwrite an existing file

What it does
  * imports `imu_sim` from project_root (the parent directory of tests/)
  * calls simulate_pitch_imu(seed=s) for s in {0, 3}, with only the 7 Tier 1
    parameters (i.e. all defaults, plus the seed)
  * saves t, gyro, accel, roll_true, pitch_true and gyro_bias per seed, with keys
    "seed{s}_{field}" (e.g. "seed0_gyro"), using numpy.savez
  * creates tests/data/ if missing, refuses to overwrite an existing file unless
    --force is given, and prints the path written

Safety check (not in the spec, added so the fixture cannot be generated from the
wrong code by accident): the script refuses to run if simulate_pitch_imu does not
have exactly the seven Tier 1 parameters, i.e. if Tier 2 changes are already
installed. Pass --no-signature-check only if you are sure the code is Tier 1.

The file name does not start with "test_", so pytest does not collect this script.
"""
import argparse
import inspect
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "data" / "tier1_reference.npz"

SEEDS = (0, 3)
FIELDS = ("t", "gyro", "accel", "roll_true", "pitch_true", "gyro_bias")
TIER1_PARAMS = ["duration", "fs", "trajectory", "gyro_bias", "gyro_noise_std",
                "accel_noise_std", "seed"]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Write tests/data/tier1_reference.npz from Tier 1 code.")
    parser.add_argument("--force", action="store_true", help="overwrite an existing file")
    parser.add_argument("--no-signature-check", action="store_true",
                        help="skip the check that imu_sim is the Tier 1 version")
    args = parser.parse_args(argv)

    if OUT.exists() and not args.force:
        print(f"ERROR: {OUT} already exists; refusing to overwrite (use --force).", file=sys.stderr)
        return 1

    sys.path.insert(0, str(ROOT))
    try:
        import imu_sim
    except ImportError as exc:
        print(f"ERROR: cannot import imu_sim from {ROOT}: {exc}", file=sys.stderr)
        return 1

    params = list(inspect.signature(imu_sim.simulate_pitch_imu).parameters)
    if params != TIER1_PARAMS and not args.no_signature_check:
        print("ERROR: simulate_pitch_imu does not have the Tier 1 signature "
              f"(found {params}).\nTier 2 changes seem to be installed already; the fixture "
              "must be generated from the Tier 1 code.\n(Use --no-signature-check to override.)",
              file=sys.stderr)
        return 1

    data = {}
    for seed in SEEDS:
        sim = imu_sim.simulate_pitch_imu(seed=seed)  # Tier 1 parameters only
        again = imu_sim.simulate_pitch_imu(seed=seed)
        for field in FIELDS:
            arr = np.array(getattr(sim, field), dtype=np.float64)
            if not np.array_equal(arr, np.array(getattr(again, field), dtype=np.float64)):
                print(f"ERROR: simulator is not deterministic for seed {seed}, field {field}.",
                      file=sys.stderr)
                return 1
            data[f"seed{seed}_{field}"] = arr

    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez(OUT, **data)
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
