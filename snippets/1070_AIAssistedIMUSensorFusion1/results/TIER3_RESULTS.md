# TIER3_RESULTS

**Owner-confirmed:** all Tier 1–3 tests passed and the `tier3.ipynb` plots were reviewed.

Values below come from the owner's run of the "Criteria values" cell of `tier3.ipynb` (seed 0 for simulated data; recordings A = `data/phone_tilts.zip` and B = `data/phone_disturbances.zip` for real data). The simulated values are identical to the executor's own sandbox run with the same seed.

Margin ratio = threshold / measured for upper bounds, and measured / threshold for lower bounds (RR1 sample counts and grid length, RR3). Angles are in °, rates and biases in rad/s and °/s, accelerations and noise levels in m/s² (§2.3). Margins are computed from the printed values, so those that rest on rounded printouts are approximate.

## Clean run (S6, seed 0)

| ID | Quantity | Unit | Measured (seed 0) | Threshold | Margin ratio |
|---|---|---|---|---|---|
| RP1 | KF RMSE, t ≥ 20 s: roll / pitch | ° | 0.0368 / 0.0270 | ≤ 0.08 ° | 2.17 / 2.96 |
| RP1 | KF-gated RMSE, t ≥ 20 s: roll / pitch | ° | 0.0368 / 0.0270 | ≤ 0.08 ° | 2.17 / 2.96 |
| RP2 | CF RMSE, t ≥ 20 s: roll / pitch | ° | 0.0532 / 0.0453 | ≤ 0.15 ° | 2.82 / 3.31 |
| RP3 | max \|bias_x − b_x\|, t ≥ 20 s | rad/s (°/s) | 5.018e-4 rad/s (0.0288 °/s) | ≤ 1e-3 rad/s (0.057 °/s) | 1.99 |
| RP3 | max \|bias_y − b_y\|, t ≥ 20 s | rad/s (°/s) | 4.580e-4 rad/s (0.0262 °/s) | ≤ 1e-3 rad/s (0.057 °/s) | 2.18 |

## Disturbances (S7, seed 0)

Max disturbance error per method (°): accel 19.915, CF 17.460, KF 12.449, KF-gated 3.028.

| ID | Quantity | Unit | Measured (seed 0) | Threshold | Margin ratio |
|---|---|---|---|---|---|
| RX1 | KF-gated max disturbance error (max over both angles) | ° | 3.028 | ≤ 7.5 ° | 2.48 |
| RX2 | KF-gated / KF max disturbance error | – (ratio) | 0.243 | ≤ 0.55 | 2.26 |
| RX3 | KF-gated / CF max disturbance error | – (ratio) | 0.173 | ≤ 0.4 | 2.31 |
| RX4a | worst recovery time, KF (all segments, both angles) | s | 2.42 | ≤ 10 s | 4.13 |
| RX4b | worst recovery time, KF-gated | s | 1.21 | ≤ 10 s | 8.26 |
| RX4c | worst recovery time, CF | s | 0.51 | ≤ 3 s | 5.88 |
| RX5 | KF-gated quiet RMSE: roll / pitch | ° | 0.0339 / 0.0278 | ≤ 0.08 ° | 2.36 / 2.88 |

## Real recordings

| ID | Quantity | Unit | A | B | Threshold | Margin ratio (A / B) |
|---|---|---|---|---|---|---|
| RR1 | samples per sensor (accel = gyro) | – | 6020 | 6000 | ≥ 5000 | 1.20 / 1.20 |
| RR1 | median sample spacing (accel and gyro) | s | 0.01000 | 0.01000 | within 2 % of 0.01 s | deviation < 0.05 % (printed to 5 decimals), margin > 40 |
| RR1 | common-grid span | s | 60.2 | 60.0 | ≥ 55 s | 1.09 / 1.09 |
| RR2 | \|gravity − 9.81\| (gravity 9.8417 / 9.8456) | m/s² | 0.032 | 0.036 | ≤ 0.2 m/s² | 6.3 / 5.6 |
| RR2 | gyro std per axis, max of the three (x, y, z: A 0.00076, 0.00073, 0.00073; B 0.00060, 0.00060, 0.00059) | rad/s | 0.00076 | 0.00060 | ≤ 0.01 rad/s | 13.2 / 16.7 |
| RR2 | \|gyro bias\| per axis, max of the three (A 6e-5, 3e-5, 5e-5; B 2e-5, 1e-5, 1e-5) | rad/s (°/s) | 6e-5 rad/s (0.0034 °/s) | 2e-5 rad/s (0.0011 °/s) | ≤ 0.01 rad/s (0.573 °/s) | ≈ 167 / ≈ 500 (printed to 5 decimals) |
| RR2 | accel noise std | m/s² | 0.0061 | 0.0097 | ≤ 0.05 m/s² | 8.2 / 5.2 |
| RR3 | Pearson r, Euler-mapped gyro integration vs accel tilt: roll / pitch | – | 0.9987 / 0.9991 | −0.0378 / −0.0471 (B not a criterion, see Note 14) | ≥ 0.9 (recording A) | 1.11 / 1.11 (A) |
| RR4 | \|end-window mean − rest-window mean\|, KF-gated: roll / pitch | ° | 0.118 / 0.138 | 0.097 / 0.002 | ≤ 2 ° | 16.9 / 14.5 (A); 20.6 / ≈ 1000 (B) |
| RR5 | \|KF-gated mean − accel tilt mean\| in end window: roll / pitch | ° | 0.002 / 0.003 | 0.005 / 0.011 | ≤ 1 ° | ≈ 500 / ≈ 333 (A); ≈ 200 / ≈ 91 (B) |

## `StationaryEstimate` of the real recordings (rest window t[0] + 1 s … t[0] + 7 s)

Only the "Criteria values" output was provided, so this table contains what that output shows. The signed bias components, the pooled `gyro_noise_std` as returned by the function and `n_samples` are printed in the notebook's "StationaryEstimate over the rest window" table; they are not repeated here.

| Set | gravity (m/s²) | accel_noise_std (m/s²) | gyro std per axis x / y / z (rad/s) | \|gyro_bias\| per axis x / y / z (rad/s) | \|gyro_bias\| per axis x / y / z (°/s) | `gyro_noise_std` pooled, derived from the per-axis values (rad/s) |
|---|---|---|---|---|---|---|
| A | 9.8417 | 0.0061 | 0.00076 / 0.00073 / 0.00073 | 6e-5 / 3e-5 / 5e-5 | 0.0034 / 0.0017 / 0.0029 | ≈ 7.4e-4 |
| B | 9.8456 | 0.0097 | 0.00060 / 0.00060 / 0.00059 | 2e-5 / 1e-5 / 1e-5 | 0.0011 / 0.0006 / 0.0006 | ≈ 6.0e-4 |

The pooled values are `sqrt(mean of the three per-axis variances)` computed from the rounded per-axis stds, so they are approximate.

## Notes (concerns / ambiguities, implemented as written)

1. **Real recordings.** The executor never saw the recordings; the loader, resampler and notebook were developed on synthetic zips in the §7.2 format. The owner's run on the real files loaded both recordings and passed the tests, so no format problem was found.
2. **Quoted data fields.** §7.2 says the header may carry one pair of double quotes per field, but is silent on data lines. The loader also strips one pair of quotes around numeric data fields, so a quoted number is accepted instead of raising `ValueError`. Everything else in the data lines is strict (decimal point, optional exponent, finite).
3. **`imu_io` does not import pandas.** The CSV parsing is done with the standard library and NumPy so that every error case of §7.2 is detected exactly. pandas remains an allowed dependency but is unused.
4. **RD5 sign.** With `gyro_bias = b + (Δ, 0, 0)` the bias is over-corrected, so the roll estimate ends **below** the truth: `roll_final − roll_true = −Δ·tau` (−0.0020 rad for Δ = 0.01, tau = 0.2). The spec states "equals Δ·tau"; I read this as the magnitude. The final pitch error is about 1e-16.
5. **`estimate_stationary` validation.** §6.3 lists "the shape errors listed in §6.2". I check that `t` is 1-D, that `gyro` and `accel` are (N, 3) and of the same length as `t`, in addition to `t_start ≥ t_end` and fewer than 10 samples. I do not check that `t` is strictly increasing, because §6.3 does not list it.
6. **Gate comparison.** `gated[k]` uses exactly `t[j] ≥ t[k] − gate_hold` in floating point (the spec formula), implemented by tracking the time of the most recent trigger. The latest trigger is the one that maximises `t[j]`, so this equals the "any j ≤ k" definition.
7. **`kalman_roll_pitch` covariance form.** The scalar loop propagates the symmetric covariances as `(p00, p01, p11)`. For the spec's initial covariances (diagonal) this is identical to the matrix recurrence; checks against a full-matrix implementation agree to well within the stated tolerances.
8. **`plot_error_comparison` details.** The y-limits use a 5 % margin around the foreground data (inside the 10 % allowed). The error-axis label is "Angle error (°)" (it was "Pitch error (°)" before, because the function now also serves roll). With the new default `background=("accel",)`, Tier 2 plots show the accelerometer error faded instead of as a regular line; the Tier 2 notebook was not changed. Tier 2 test KI2 had to be updated for the new signature (E3).
9. **Interactive section.** Under nbconvert there is no front end, so an output widget would not render. The notebook therefore first draws the output for the default control values with a plain function call (S7, tau = 0.2 s, sQ = sR = 1, gating on, threshold 0.2 m/s²), then creates the live widgets with `interactive_output`. In a live session the default output therefore appears twice (once static, once from the widgets).
10. **Extra notebook cell.** The notebook has an additional "Criteria values" cell that prints the numbers behind RP, RX and RR in one place (the source of this file). It does not change any computation.
11. **Recovery times of the accelerometer.** The S7 table also prints recovery times for the raw `accel` method. Its error noise (about 0.3 ° RMS) exceeds the 0.5 ° tolerance at times, so some of its recovery times are large or `inf`; this is expected and not part of RX4.
12. **Python/library versions.** All modules and the three notebooks were verified in a clean Python 3.9.25 environment with NumPy 2.0.2, Matplotlib 3.9.4, pandas 2.3.3 and ipywidgets 8.1.9. The owner's run on the reference machine (3.9.13) passed.
13. **Errata E1.** The simulator already implemented T2-§4.2 literally (`gyro_bias_true[0, 1] == gyro_bias[1] + delta` when `t_step ≤ t[0]`), so no code change was needed for E1.
14. **RR3 for recording B.** RR3 applies to recording A only. For B the printed Pearson r is about −0.04 (roll) and −0.05 (pitch), far from 0.9. This is not a criterion violation. My reading, not verified from the data: B is the disturbance recording, whose tilt excursions are probably small compared with the gyro and accelerometer noise and the disturbances, so the two angle series have little common variation to correlate. Plotting both for B would confirm it.
15. **Real-data noise levels versus the simulation.** The rest-window estimates on the real recordings are much smaller than the simulated sensor specification: accelerometer noise 0.006–0.010 m/s² (simulation: 0.05) and gyro noise about 6–7e-4 rad/s (simulation: 0.005). The filters adapt automatically because every parameter except `bias_rw_std` is estimated from the rest window (§0.4). The bias random-walk intensity stays at the default 1e-4 rad/s/√s, which is not matched to these quieter sensors.
