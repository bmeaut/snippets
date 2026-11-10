# TIER1_RESULTS

## Owner-confirmed run (notebook, seed 0)

The owner executed `tier1.ipynb` and the tester's pytest suite: **all 237 tests passed.**

| Scenario | Method | Result (owner's run) |
|---|---|---|
| S1 | Gyro | RMSE 19.684°, max abs error 34.506° |
| S1 | Accel | RMSE 0.292°, max abs error 1.057° |
| S1 | Complementary | RMSE 0.140°, max abs error 0.347° |
| S2 | Gyro | drift rate 0.572435 °/s |
| S2 | Accel | drift rate 0.000009 °/s |
| S2 | Complementary | drift rate 0.000010 °/s |

These match the executor's sandbox measurements below (the accel and CF drift values are 8.70e-6 and 1.02e-5 °/s before rounding to six decimals). The CF drift of 0.000010 °/s is 1.8e-7 rad/s, well under the 1e-5 rad/s limit in P7; see Note 2.

---

## Executor's sandbox measurements

Measured by the EXECUTOR in its own sandbox (Python 3.13, NumPy 2.5, Matplotlib 3.11) with seed 0 unless noted.
The P-criteria were also checked on every listed seed (S1: 0-9, S2: 0-4) with an ad-hoc script.

## S1 (60 s, 100 Hz, seed 0)

| ID | Quantity | Measured | Criterion | Result |
|---|---|---|---|---|
| P1 | Accel-only RMSE | 0.2916° (5.089e-3 rad) | 0.234°–0.350° | pass |
| P2 | Gyro final error (rad) | 0.6022 rad; b_y·t[-1] = 0.5999 rad; difference 0.0023 rad | ≤ 0.03 rad | pass |
| P3 | Gyro-only RMSE | 19.68° | > 10° | pass |
| P4 | CF RMSE | 0.1402° | ≤ 0.2° | pass |
| P5 | CF RMSE / accel RMSE | 0.481 | ≤ 0.7 | pass |

Max abs error (S1, seed 0): gyro 34.51°, accel 1.057°, CF 0.347°.

## S2 (600 s, 100 Hz, seed 0)

| ID | Quantity | Measured | Criterion | Result |
|---|---|---|---|---|
| P6 | Gyro drift rate | 9.991e-3 rad/s (0.5724 °/s), -0.09 % from 0.01 | within ±5 % | pass |
| P7 | CF drift rate | 1.78e-7 rad/s (1.02e-5 °/s) | ≤ 1e-5 rad/s | pass |
| P7 | Accel drift rate | 1.52e-7 rad/s (8.70e-6 °/s) | ≤ 1e-5 rad/s | pass |
| P8 | CF RMSE, t ≥ 540 s | 0.1456° | ≤ 0.2° | pass |

P1–P8 also held for every listed seed (S1 seeds 0–9, S2 seeds 0–4).

Spot checks of deterministic criteria: D2 max error 0.0; D6 final CF error 0.0020000 rad (target 0.002); D7 max deviation 4.7e-10 (tau=1e9) and 2.3e-9 (tau=1e-9), both below 1e-6; N4 shapes/dtypes as specified. `tier1.ipynb` executes via `jupyter nbconvert --to notebook --execute` in about 5 s (limit 120 s).

## Notes (concerns / ambiguities, implemented as written)

1. **Spec file name.** The task refers to `tier1_spec_v1.md`; the file provided was `tier1_spec.md`. I implemented that document.
2. **P7 units.** The 1e-5 limit is in rad/s. The notebook prints drift in °/s, where the CF value reads 1.02e-5 °/s; that is 1.78e-7 rad/s, so the criterion is met. A reader comparing the printed °/s value to 1e-5 could be misled.
3. **P8 margin.** CF RMSE for t ≥ 540 s (0.146°) is close to the 0.2° limit relative to its expected value; the 0.11° bias offset b·tau contributes to it. The check passed on all five seeds here.
4. **Gyro P2 reference.** `b_y · t[-1]` ignores the first-sample convention (angle[0] = initial_angle with no increment), which introduces about 0.0023 rad of discrepancy against the true integral; this stays inside the 0.03 tolerance.
5. **D7 with `tau=1e-9`.** α is about 1e-7, leaving a residual of about 2e-9 rad relative to `accel_angle`, within the 1e-6 tolerance.
6. **Trajectory shape errors.** Spec §4.4 does not say what to do if a user trajectory returns arrays whose shape is not (N,). I raise `ValueError`.
7. **Extra validation.** `imu_metrics` also raises `ValueError` for non-1-D inputs and for `drift_rate` with constant `t`; `plot_comparison` raises `ValueError` for non-dict `estimates`. These go beyond the listed cases but do not conflict with them.
8. **Noise draw order.** All gyro noise (N×3) is drawn first, then all accel noise (N×3), from one `default_rng(seed)`. The spec does not fix the order; any other order gives different but statistically equivalent results.
9. **Figure creation.** `plot_comparison` uses `plt.subplots`, so figures register with pyplot (it never calls `plt.show()`). The notebook displays and closes each figure to avoid duplicates.
10. **NaN handling.** Only `imu_metrics` checks for NaN (as specified); the filters do not.
