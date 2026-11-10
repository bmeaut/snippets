# TIER2_RESULTS

**Owner-confirmed:** the full test suite passed (489 tests, Python 3.9.13) and the `tier2.ipynb` plots were reviewed.

Measured values below are for **seed 0** in every scenario, produced by the executor in its sandbox (Python 3.9.25 and 3.13) with the same code and data as the corrected `tier2.ipynb`. The notebook itself prints the S1 table, the S2 drift table, the S3 and S4 results and the S5 grid; the few quantities it does not print (the t ≥ 20 s statistics for KP1, KP3, KP4, and the t ≥ 540 s RMSE for KP5b) were computed from the same seed-0 arrays with a separate script. All printed notebook values agree with this table.

Margin ratio = threshold / measured for upper bounds, and measured / threshold for lower bounds (KC1, KT2). Rates and biases are given in both rad/s and °/s (§2.2).

## Statistical performance and consistency

| ID | Scenario | Quantity | Unit | Measured (seed 0) | Threshold | Margin ratio |
|---|---|---|---|---|---|---|
| KP1 | S1 | KF angle RMSE, t ≥ 20 s | ° | 0.0325 | ≤ 0.06 ° | 1.85 |
| KP2 | S1 | KF RMSE / CF RMSE (full run; 0.0331 ° / 0.1402 °) | – (ratio) | 0.236 | ≤ 0.6 | 2.54 |
| KP3 | S1 | max \|KF bias − b_y\|, t ≥ 20 s | rad/s (°/s) | 3.70e-4 rad/s (0.0212 °/s) | ≤ 1e-3 rad/s (0.057 °/s) | 2.70 |
| KP4 | S1 | KF max abs angle error, t ≥ 20 s | ° | 0.1144 | ≤ 0.2 ° | 1.75 |
| KP5a | S2 | KF angle `drift_rate` (absolute value) | rad/s (°/s) | 1.63e-7 rad/s (9.36e-6 °/s) | ≤ 1e-5 rad/s (5.7e-4 °/s) | 61.2 |
| KP5b | S2 | KF angle RMSE, t ≥ 540 s | ° | 0.0374 | ≤ 0.06 ° | 1.60 |
| KP6 | S3 | KF angle RMSE, t ≥ 30 s | ° | 0.0322 | ≤ 0.06 ° | 1.86 |
| KP7 | S3 | KF bias RMSE, t ≥ 30 s | rad/s (°/s) | 2.53e-4 rad/s (0.0145 °/s) | ≤ 5e-4 rad/s (0.029 °/s) | 1.97 |
| KP8 | S4 | `convergence_time` of KF bias (tol = 1e-3 rad/s = 0.057 °/s, t_start = 60 s); absolute time (12.79 s after the step) | s | 72.79 | ≤ 90 s | 1.24 |
| KP9 | S4 | KF max abs angle error, 60 ≤ t ≤ 90 s (CF: 0.4359 °) | ° | 0.4112 | ≤ 0.7 ° | 1.70 |
| KC1 | S3 | bias coverage fraction (2σ), t ≥ 30 s | – (fraction) | 0.933 | ≥ 0.90 | 1.04 |

## Tuning sweep (S5, seed 0 only in the notebook)

| ID | Scenario | Quantity | Unit | Measured (seed 0) | Threshold | Margin ratio |
|---|---|---|---|---|---|---|
| KT1 | S5 | KF RMSE at (sQ, sR) = (1, 1) divided by grid minimum (0.02801 ° / 0.02801 °) | – (ratio) | 1.0000005 | ≤ 1.10 | 1.10 |
| KT2 | S5 | grid maximum (0.0669 °) divided by KF RMSE at (1, 1) (0.0280 °) | – (ratio) | 2.388 | ≥ 1.25 | 1.91 |

KF angle RMSE (°, t ≥ 30 s, seed 0); rows = sQ, columns = sR:

| sQ \ sR | 0.1 | 0.3 | 1 | 3 | 10 |
|---|---|---|---|---|---|
| 0.1 | 0.0280 | 0.0283 | 0.0336 | 0.0431 | 0.0594 |
| 0.3 | 0.0317 | 0.0280 | 0.0285 | 0.0336 | 0.0443 |
| **1** | 0.0398 | 0.0322 | **0.0280** | 0.0283 | 0.0336 |
| 3 | 0.0506 | 0.0398 | 0.0317 | 0.0280 | 0.0285 |
| 10 | 0.0669 | 0.0519 | 0.0398 | 0.0322 | 0.0280 |

The spec's KT1/KT2 criteria average seeds 0–2; the values above are seed 0 only, as the notebook runs.

## Other seed-0 results printed by the notebook (for reference)

| Scenario | Method | RMSE (°) | Max abs error (°) |
|---|---|---|---|
| S1 | gyro | 19.6836 | 34.5059 |
| S1 | accel | 0.2916 | 1.0575 |
| S1 | CF | 0.1402 | 0.3470 |
| S1 | KF | 0.0331 | 0.2006 |

| Scenario | Method | Drift (rad/s) | Drift (°/s) |
|---|---|---|---|
| S2 | gyro | 9.991e-03 | 5.724e-01 |
| S2 | accel | 1.519e-07 | 8.701e-06 |
| S2 | CF | 1.777e-07 | 1.018e-05 |
| S2 | KF | 1.634e-07 | 9.364e-06 |

## Notes (concerns / ambiguities, implemented as written)

1. **`gyro_bias_true[0] == gyro_bias` "always" (§4.3) vs. §4.5.** If `bias_step` has `t_step ≤ t[0]` (allowed by §4.5, "applies to every sample"), §4.2 gives `gyro_bias_true[0, 1] = b0[1] + delta`, so the "always" statement cannot hold. I implemented §4.2 literally; the equality holds whenever the step is later than t[0] or absent.
2. **Random-walk draw shape.** §4.2 uses `w[k, i]` for k ≥ 1 only. I draw an `(N−1, 3)` standard-normal array from the same generator after the two Tier 1 draws, so `w[0]` is not drawn. The spec does not fix the draw layout.
3. **Tier 1 bit-identity.** With `gyro_bias_rw_std == 0` and `bias_step is None`, no extra random numbers are drawn and the bias array is a plain copy of `gyro_bias`. In my sandbox, seeds 0 and 3 are `array_equal` to output saved from the Tier 1 code before the change; the owner's fixture-based KS1 test passed.
4. **`kalman_pitch` noise-parameter validation.** The §5.1 error cases are checked once at the start by calling `kalman_noise_matrices` with a placeholder `dt = 1.0`; per-step `Q` is then computed inline with the same formulas.
5. **`initial_cov` handling.** The covariance is propagated element-wise without symmetrization, so `cov[k,0,1]` and `cov[k,1,0]` are kept separately (identical for the default and any exactly symmetric input). A negative eigenvalue raises `ValueError`; a tiny negative round-off relative to the largest eigenvalue (< 1e-12 relative) is tolerated so that valid positive semi-definite matrices are not rejected.
6. **`plot_error_comparison` details.** (a) A length mismatch is checked on all entries of `estimates`, including keys in `exclude`; the spec only says "a length mismatch". (b) The y-limits use a 5 % margin around the plotted data, which lies inside the 10 % allowed by §7.1; for perfectly flat data (r = 0) a tiny pad is added, because the rule cannot be met exactly there. (c) A string passed as `exclude` is treated as a single key. (d) No extra lines (such as a zero line) are drawn, so line counts match §9.5.
7. **`plot_bias_estimate` extra validation.** `n_sigma ≤ 0` also raises `ValueError`; §7.2 lists only a length mismatch and negative `bias_std`.
8. **KT1 at (1, 1).** In the seed 0 sweep the nominal cell ties with the other cells on the sQ = sR diagonal (all about 0.0280 °; (1, 1) is within 5e-7 relative of the grid minimum). This is expected from the structure of the Kalman gain: scaling Q and R together leaves the steady-state gain nearly unchanged. It is not a problem for the ≤ 1.10 criterion.
9. **Notebook filter inputs.** `tier2.ipynb` defines the sensor-spec constants (`GYRO_NOISE_STD`, `ACCEL_NOISE_STD`, `BIAS_RW_STD`, `GRAVITY`) and passes them to `kalman_pitch` explicitly; their values equal the function defaults, so "KF = defaults" holds. No `SimulatedIMU` field other than the measured `t`, `gyro` and `accel` reaches a filter.
10. **Discussion text.** The notebook's discussion qualitatively describes the step behavior (the CF settles to a larger offset of about b·τ, the KF re-converges in roughly 10–15 s). The seed-0 values above agree (KF re-converges 12.79 s after the step); KF and CF peak errors in the 60–90 s window are similar (0.411 ° and 0.436 °).
11. **Tier 1 test I2** had to be updated to the §4.1 signature of `simulate_pitch_imu`, as stated in §4.1.
12. **Python version.** The spec requires Python ≥ 3.10, but the test machine runs 3.9.13. After fixing a Python-3.12-only f-string in the notebook, all modules and both notebooks run on 3.9 (modules use `from __future__ import annotations`). Consider stating 3.9 as the supported minimum.
13. **Margins versus §0.4.** §0.4 says every threshold is at least 1.5× away from its planner-expected value. Measured against the expected values quoted in §9, KP8 (73 s vs. 90 s, ratio 1.23) and KC1 (0.95 vs. 0.90, ratio 1.06) are closer than 1.5×, and the measured seed-0 margins for these two are the smallest (KP8 1.24, KC1 1.04). Both still pass on every listed seed.
