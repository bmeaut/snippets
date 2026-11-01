# Tier 2 Specification — Linear Kalman Filter for Pitch with Gyro-Bias State

**Status:** FINAL. Approved by the owner on 2026-10-31, including the §0 decisions and the §9 thresholds.
**Audience:** EXECUTOR (implements §4–§8) and TESTER (writes tests from §2–§10 without seeing code).
Where this document says "must", it is a testable requirement.
**Prerequisite:** the Tier 1 specification (`tier1_spec.md`, FINAL) stays binding. This document only lists what is added or changed. Tier 1 sections are cited as T1-§x.

---

## 0. Decisions in this tier (for owner review)

| # | Decision | Reason |
|---|---|---|
| 0.1 | The Kalman filter (KF) uses the **trapezoidal** rate `(ω[k−1] + ω[k]) / 2` in its prediction step. Tier 1 functions keep the backward-rectangle rule unchanged. | The Tier 1 rule `ω[k]·dt` effectively leads the angle by half a sample, giving an error of about `(dt/2)·ω(t)`. For the default trajectory that is ≈0.14° RMS. The KF's steady-state noise floor is ≈0.03°, so with the rectangle rule this artefact would dominate the KF error and hide its advantage over the CF. The trapezoidal rule reduces it to below 0.002°. Test KD4 detects which rule is used. |
| 0.2 | The filter's default `bias_rw_std = 1e-4` rad/s/√s. The random-walk scenarios S3 and S5 use the same value in the simulator. | Over 600 s this lets the bias wander by about ±0.0025 rad/s (1σ), about 25 % of the nominal bias. That is large enough to require tracking, and it is plausible for a phone-grade gyro. |
| 0.3 | The Tier 1 regression check uses a reference fixture. The TESTER writes a generator script, and the **owner** runs it on the current Tier 1 code **before** any Tier 2 change is installed. | The tester cannot run code. This lets the "bit-identical Tier 1 output" requirement be verified as a black box without a git tag. |
| 0.4 | Expected values in §9 are planner estimates from a continuous-time steady-state Riccati analysis (§5.4). Every threshold is at least 1.5× away from its expected value. | Response to the Tier 1 margin feedback. |

---

## 1. Scope

In scope for Tier 2:
- Simulator extension: gyro bias random walk and a bias step on the y axis.
- A linear 2-state Kalman filter for pitch, with state `[angle, gyro_bias_y]`, and a documented derivation of Q and R.
- Two new metrics: `convergence_time` and `coverage_fraction`.
- Two new plot functions: an error comparison without gyro-only, with an optional zoom window; and a bias estimate plot with a ±nσ band.
- A notebook `tier2.ipynb`.

Out of scope: roll estimation, linear acceleration or vibration, EKF, quaternions, adaptive or innovation-based tuning, CSV loading, angle wrapping, streaming APIs. These are unchanged from Tier 1 except that the bias may now vary over time.

---

## 2. Conventions

All of T1-§2 applies unchanged. In addition:

### 2.1 Bias random-walk unit (binding for simulator and filter)
`σ_b` (the parameter `gyro_bias_rw_std` in the simulator and `bias_rw_std` in the filter) has the unit **rad/s/√s**. A bias random walk with intensity `σ_b`, sampled at step `dt`, has independent increments:

`b[k] − b[k−1] ~ N(0, σ_b² · dt)`

so after time T the bias has drifted with standard deviation `σ_b · √T`. The filter's process noise for the bias state, `Q[1,1] = σ_b² · dt`, is the same quantity.

### 2.2 Reporting units
- Code still returns rad, rad/s and rad/s².
- Every printed table in the notebook, and every result in `TIER2_RESULTS.md`, must state its unit in the column header. Drift and bias values are printed in **both** rad/s and °/s, in separate columns.
- Each threshold in §9 that is given in rad/s also states its °/s equivalent.

---

## 3. File layout

Unchanged from T1-§3, with these additions:
```
project_root/
  tier2.ipynb
  TIER2_RESULTS.md                          # EXECUTOR
  tests/make_tier1_reference.py             # TESTER writes; owner runs once (see §9.3, KS1)
  tests/data/tier1_reference.npz            # produced by the script above, run by the owner
```
`make_tier1_reference.py` is a standalone script. Its name does not start with `test_`, so pytest does not collect it.
`imu_filters.py` must still not import `imu_sim`, `imu_metrics` or `imu_plots`.

Test-only dependencies are unchanged from Tier 1: pytest, jupyter/nbconvert and ipykernel.

---

## 4. Changes to `imu_sim.py`

### 4.1 New signature
```
simulate_pitch_imu(
    duration: float = 60.0,
    fs: float = 100.0,
    trajectory: Callable | None = None,
    gyro_bias = (0.01, 0.01, 0.01),
    gyro_noise_std: float = 0.005,
    accel_noise_std: float = 0.05,
    seed: int | None = None,
    gyro_bias_rw_std: float = 0.0,             # NEW, rad/s/√s, applies to all 3 axes
    bias_step: tuple[float, float] | None = None,  # NEW, (t_step [s], delta [rad/s]), y axis only
) -> SimulatedIMU
```
The first seven parameters keep their order and defaults. Tier 1 test I2 must be updated to this signature. No other Tier 1 test changes.

### 4.2 Bias model
Let `b0 = gyro_bias` (shape (3,)). For each axis i independently:
- `rw[0, i] = 0`
- `rw[k, i] = rw[k−1, i] + gyro_bias_rw_std · sqrt(t[k] − t[k−1]) · w[k, i]`, with `w ~ N(0, 1)` i.i.d., for k ≥ 1
- `step[k] = delta` if `bias_step` is given and `t[k] ≥ t_step`; otherwise `step[k] = 0`
- `bias[k, 0] = b0[0] + rw[k, 0]`
- `bias[k, 1] = b0[1] + rw[k, 1] + step[k]`
- `bias[k, 2] = b0[2] + rw[k, 2]`

The measurement model is that of T1-§4.4, with the constant bias replaced by `bias[k, :]`:

`gyro[k, i] = true_rate_i[k] + bias[k, i] + n_g[k, i]`

### 4.3 New field in `SimulatedIMU`
Appended after `fs`:

| Field | Type / shape | Meaning |
|---|---|---|
| `gyro_bias_true` | `(N, 3)` float64 | the bias actually applied at each sample, rad/s |

The field `gyro_bias` keeps its meaning: the `(3,)` initial bias `b0`. Therefore `gyro_bias_true[0] == gyro_bias` always.

### 4.4 Backward compatibility and randomness
- With `gyro_bias_rw_std == 0` and `bias_step is None`, the output for a given seed must be **bit-identical** to the Tier 1 release, in all Tier 1 fields. The simulator must not draw any extra random numbers in that case.
- If `gyro_bias_rw_std > 0`, the random-walk draws come from the same generator, after all Tier 1 draws.
- Determinism (same seed gives identical output) applies to all outputs, including `gyro_bias_true`.

### 4.5 New errors (`ValueError`)
- `gyro_bias_rw_std < 0`
- `bias_step` that is not a length-2 sequence of finite floats

A `t_step` outside `[t[0], t[−1]]` is allowed. It means the step either applies to every sample or to none.

---

## 5. Additions to `imu_filters.py`

### 5.1 `kalman_noise_matrices(dt, gyro_noise_std, accel_noise_std, bias_rw_std, gravity=9.81) -> tuple[ndarray, float]`
Returns `(Q, R)`:
- `Q = [[gyro_noise_std² · dt², 0], [0, bias_rw_std² · dt]]`, shape (2, 2), float64
- `R = (accel_noise_std / gravity)²`, a float in rad²

**Errors** (`ValueError`):
- `dt ≤ 0`
- `gyro_noise_std ≤ 0`
- `accel_noise_std ≤ 0`
- `bias_rw_std < 0`
- `gravity ≤ 0`

### 5.2 `KalmanResult` (frozen dataclass, defined in `imu_filters`)
| Field | Shape | Meaning |
|---|---|---|
| `angle` | `(N,)` float64 | posterior pitch estimate, rad |
| `bias` | `(N,)` float64 | posterior gyro-bias estimate for the axis passed in, rad/s |
| `cov` | `(N, 2, 2)` float64 | posterior covariance; `cov[k,0,0]` in rad², `cov[k,1,1]` in (rad/s)², `cov[k,0,1]` in rad²/s |

### 5.3 `kalman_pitch`
```
kalman_pitch(
    t, gyro_rate, accel_angle,
    gyro_noise_std: float = 0.005,     # rad/s per sample (sensor spec)
    accel_noise_std: float = 0.05,     # m/s² per axis (sensor spec)
    bias_rw_std: float = 1e-4,         # rad/s/√s (sensor spec, §2.1)
    gravity: float = 9.81,
    initial_angle: float | None = None,
    initial_bias: float = 0.0,
    initial_cov = None,                # array-like (2, 2) or None
) -> KalmanResult
```
**Inputs:**
- `t`, `gyro_rate` and `accel_angle` are as in T1-§5.3.
- The noise parameters are **sensor specifications**, given the way datasheet values would be. Callers must pass them explicitly or rely on the defaults. They must never be taken from a `SimulatedIMU` object.

**Initialization** (k = 0):
- `R` is as in §5.1.
- `angle[0] = initial_angle` if given, else `accel_angle[0]`
- `bias[0] = initial_bias`
- `cov[0] = initial_cov` if given, else `diag(R, 0.02²)`

No measurement update is applied at k = 0.

**Recurrence** for k ≥ 1, with `x = [angle, bias]`. This form is binding, and test KD2 reproduces it:
```
dt   = t[k] − t[k−1]
ω̄    = (gyro_rate[k−1] + gyro_rate[k]) / 2
Q    = kalman_noise_matrices(dt, gyro_noise_std, accel_noise_std, bias_rw_std, gravity)[0]
F    = [[1, −dt], [0, 1]]
x⁻   = [ angle[k−1] + (ω̄ − bias[k−1]) · dt ,  bias[k−1] ]
P⁻   = F · cov[k−1] · Fᵀ + Q
S    = P⁻[0,0] + R
K    = P⁻[:, 0] / S                  # shape (2,)
y    = accel_angle[k] − x⁻[0]
x    = x⁻ + K · y
cov[k] = P⁻ − S · (K Kᵀ)             # equals (I − K H) P⁻ with H = [1, 0]; symmetric by construction
```

**Errors** (`ValueError`):
- every case in T1-§5.3 except the one about tau
- the cases in §5.1
- `initial_cov` not of shape (2, 2), not symmetric (atol 1e-12), or with a negative eigenvalue

**Performance:** for N = 60 000 the call must complete in under 2 s on a typical laptop.

**Tier 2 usage:** `kalman_pitch(t, gyro[:,1], accel_tilt(accel)[1])`. The returned `bias` estimates `gyro_bias_true[:, 1]`.

### 5.4 Justification of Q and R (binding derivation; reproduce it in the notebook)
- **State model.** The angle evolves as `θ[k] = θ[k−1] + (ω_meas − b − n_g)·dt`. The gyro white noise `n_g` has standard deviation `σ_g` per sample, so it adds variance `σ_g²·dt²` to the angle each step. That gives `Q[0,0] = σ_g²·dt²`.
- **Bias model.** The bias follows the random walk of §2.1, so `Q[1,1] = σ_b²·dt`. The off-diagonal terms are zero because the two noise sources are independent.

  The trapezoidal average makes consecutive angle increments slightly correlated. Their per-step variance is `σ_g²·dt²/2`, but the low-frequency power, which is what governs long-run drift, equals `σ_g²·dt²` per step. The spec accepts this approximation, and the tuning sweep (KT1) checks it empirically.
- **Measurement.** For a stationary IMU, accelerometer noise with standard deviation `σ_a` on each axis perturbs the pitch from `atan2` by approximately `σ_a / G`. Only the noise component perpendicular to gravity in the x–z plane matters to first order, and it has standard deviation `σ_a` for any θ. The y-axis noise enters only at second order. That gives `R = (σ_a / G)²`.
- **Planner steady-state estimate** (continuous-time Riccati, defaults, 100 Hz):
  - angle σ ≈ 5.5e-4 rad (0.031°)
  - bias σ ≈ 2.4e-4 rad/s (0.014 °/s)
  - closed-loop poles ≈ −0.2 s⁻¹ and −0.95 s⁻¹, so bias errors decay with a time constant of about 5 s
- **Initial covariance.** `0.02²` for the bias says the filter believes the bias is within ±2× the nominal 0.01 rad/s. `R` for the angle reflects that the initial angle comes from a single accelerometer sample.

---

## 6. Additions to `imu_metrics.py`

The input rules and errors are as in T1-§6, plus the cases listed below.

### 6.1 `convergence_time(t, estimate, truth, tol, t_start=None) -> float`
- Let `e = estimate − truth` and consider only samples with `t ≥ t_start` (default `t[0]`).
- If no considered sample has `|e| > tol`, the function returns the time of the first considered sample.
- If the last sample has `|e| > tol`, it returns `inf`.
- Otherwise it returns `t[j+1]`, where `j` is the index of the last considered sample with `|e| > tol`.
- **Errors** (`ValueError`): `tol ≤ 0`, or no samples with `t ≥ t_start`.

### 6.2 `coverage_fraction(estimate, truth, std, n_sigma=2.0) -> float`
- Returns the fraction of samples with `|estimate − truth| ≤ n_sigma · std`. The comparison is inclusive.
- **Errors** (`ValueError`): any `std < 0`, `n_sigma ≤ 0`, a shape mismatch, empty input, or NaN.

---

## 7. Additions to `imu_plots.py`

`plot_comparison` (T1-§7.1) is unchanged.

### 7.1 `plot_error_comparison(t, truth, estimates, exclude=("gyro",), t_window=None, title="") -> Figure`
- **Shown estimates.** These are the keys of `estimates` that are not in `exclude`, in insertion order. Keys in `exclude` that do not appear in `estimates` are ignored.
- **Number of axes.** The figure has 1 axes if `t_window is None`, and 2 axes otherwise.
- **Axes 0** shows the error in **degrees** over the full time range. It has one line per shown key, labelled with the key, with x-data `t` and y-data `rad2deg(est − truth)`.
- **Axes 1** (only when `t_window = (t0, t1)` is given) has the same lines, restricted to samples with `t0 ≤ t ≤ t1`. Its x-limits equal `(t0, t1)`.
- **Y-limits.** On each axes, the y-limits lie within `[m − 0.1·r, M + 0.1·r]`, where `m` and `M` are the minimum and maximum of the y-data plotted on that axes and `r = M − m`. This is the requirement that makes the good estimators readable.
- Every axes has a legend and labelled axes, and the error axis label includes "°".
- The function must not call `plt.show()`.
- **Errors** (`ValueError`):
  - no shown estimates
  - a length mismatch
  - `t_window` with `t0 ≥ t1`
  - a window that contains no samples

### 7.2 `plot_bias_estimate(t, bias_est, bias_std, bias_true=None, n_sigma=2.0, title="") -> Figure`
- The figure has exactly 1 axes, in **°/s**.
- It contains these lines:
  - `"estimate"`, with y-data `rad2deg(bias_est)`
  - `"truth"`, with y-data `rad2deg(bias_true)`, only if `bias_true` is given
- It contains exactly one filled band (one `PolyCollection` in `ax.collections`), labelled `f"±{n_sigma:g}σ"`. The band spans `rad2deg(bias_est ± n_sigma·bias_std)`, so its vertex y-range equals `[min(lower), max(upper)]` (1e-9).
- The axes has a legend and labelled axes. The function must not call `plt.show()`.
- **Errors** (`ValueError`): a length mismatch or any `bias_std < 0`.

---

## 8. `tier2.ipynb`

The notebook must:
- Execute top to bottom via `jupyter nbconvert --to notebook --execute tier2.ipynb` in under 180 s.
- Use estimate dict keys `"gyro"`, `"accel"`, `"CF"` and `"KF"`. CF means tau = 0.2 and KF means the `kalman_pitch` defaults.
- Contain a markdown section reproducing the Q/R derivation of §5.4, with the numeric values of Q and R at dt = 0.01 s.
- Pass to the filters only sensor-spec constants defined in the notebook, never a `SimulatedIMU` field.

It must produce these sections, using seed 0 for every scenario:

| Section | Scenario | Content |
|---|---|---|
| Standard | S1 | Table of RMSE and max abs error, in °, per method. `plot_comparison` with all four methods. `plot_error_comparison` excluding gyro, with `t_window=(30, 40)`. `plot_bias_estimate` with truth. |
| Long run | S2 | Table of `drift_rate` per method in rad/s **and** °/s. `plot_error_comparison` excluding gyro. |
| Random-walk bias | S3 | KF angle and bias RMSE. The bias coverage fraction (KC1). `plot_bias_estimate` with truth. |
| Bias step | S4 | KF bias convergence time after the step. KF and CF max angle error in [60, 90] s. `plot_bias_estimate` and `plot_error_comparison` with `t_window=(55, 95)`. |
| Tuning sweep | S5 | Seed 0 only. A heatmap or table of KF RMSE over the §9.4 grid, with the (1, 1) cell marked. |
| Discussion | — | Short markdown discussion, including the KF-vs-CF behavior at the bias step. |

---

## 9. Scenarios and success criteria

**Scenarios** (all use `simulate_pitch_imu` defaults unless listed):

| ID | Simulator arguments | Seeds |
|---|---|---|
| S1 | defaults (60 s) — identical to Tier 1 | 0–9 |
| S2 | `duration=600` | 0–4 |
| S3 | `duration=600, gyro_bias_rw_std=1e-4` | 0–4 |
| S4 | `duration=120, bias_step=(60.0, 0.01)` | 0–4 |
| S5 | `duration=120, gyro_bias_rw_std=1e-4` | 0–2 |

**Estimators:**
- KF = `kalman_pitch(t, gyro[:,1], accel_tilt(accel)[1])` with defaults.
- CF = as in T1-§8.

Bias errors are computed against `gyro_bias_true[:,1]`. Angle errors are computed against `pitch_true`. "RMSE over t ≥ X" means the RMSE over the samples with `t ≥ X`. Each criterion must hold for **every** listed seed unless stated otherwise.

Expected values in brackets are planner estimates. They are not test values.

### 9.1 Statistical performance
| ID | Scen. | Criterion | (expected) |
|---|---|---|---|
| KP1 | S1 | KF angle RMSE over t ≥ 20 s ≤ 0.06° | (≈0.03°) |
| KP2 | S1 | KF angle RMSE (full run) ≤ 0.6 × CF RMSE (full run, same seed) | (ratio ≈0.3) |
| KP3 | S1 | \|KF bias − b_y\| ≤ 1e-3 rad/s (0.057 °/s) for all t ≥ 20 s | (max ≈5e-4) |
| KP4 | S1 | KF max abs angle error over t ≥ 20 s ≤ 0.2° | (≈0.11°) |
| KP5 | S2 | \|KF `drift_rate`\| ≤ 1e-5 rad/s (5.7e-4 °/s), and KF angle RMSE over t ≥ 540 s ≤ 0.06° | |
| KP6 | S3 | KF angle RMSE over t ≥ 30 s ≤ 0.06° | (≈0.032°) |
| KP7 | S3 | KF bias RMSE over t ≥ 30 s ≤ 5e-4 rad/s (0.029 °/s) | (≈2.4e-4) |
| KP8 | S4 | `convergence_time(t, KF bias, bias_true, tol=1e-3, t_start=60.0)` ≤ 90 s, so the bias has settled within 30 s of the step | (≈73 s) |
| KP9 | S4 | KF max abs angle error over 60 ≤ t ≤ 90 s ≤ 0.7° | (peak ≈0.4°) |

### 9.2 Consistency
| ID | Scen. | Criterion | (expected) |
|---|---|---|---|
| KC1 | S3 | `coverage_fraction(KF bias, bias_true, sqrt(cov[:,1,1]), 2.0)` over samples with t ≥ 30 s ≥ 0.90 | (≈0.95) |

### 9.3 Simulator extension
| ID | Criterion |
|---|---|
| KS1 | **Regression.** With all new options at their defaults, `simulate_pitch_imu(seed=s)` for s ∈ {0, 3} returns arrays identical (`array_equal`) to `tests/data/tier1_reference.npz` in the Tier 1 fields `t`, `gyro`, `accel`, `roll_true`, `pitch_true` and `gyro_bias`. Also, `gyro_bias_true` has every row equal to `gyro_bias`.<br>**Fixture generation.** The TESTER provides `tests/make_tier1_reference.py`, which must:<br>• import `imu_sim` from `project_root` and call `simulate_pitch_imu(seed=s)` for s ∈ {0, 3}, using only the 7 Tier 1 parameters<br>• save those six fields per seed to `tests/data/tier1_reference.npz` with keys `seed{s}_{field}` (e.g. `seed0_gyro`), using `numpy.savez`<br>• create `tests/data/` if it is missing, refuse to overwrite an existing file unless `--force` is given, and print the path written<br>The owner runs it once on the Tier 1 code before the Tier 2 changes are installed. The KS1 test fails with a clear message (it does not skip) if the file is missing. |
| KS2 | **Random-walk statistics.** With S3 settings and seed 0: `gyro_bias_true[0] == gyro_bias`. For each axis, `diff(gyro_bias_true[:, i])` has std within ±5 % of `1e-4·sqrt(0.01) = 1e-5` and \|mean\| ≤ 4·1e-5/√(N−1). The pairwise \|Pearson r\| between the three diff columns is < 0.1. The residual `gyro − true_rate − gyro_bias_true` has std within ±5 % of 0.005 per axis. |
| KS3 | **Step.** With `bias_step=(30.0, 0.01)` and no random walk: `gyro_bias_true[:,1] == b_y` for t < 30 and `== b_y + 0.01` for t ≥ 30 (atol 1e-15). Columns 0 and 2 are constant. |
| KS4 | **Noise-free.** With both noise stds 0, `gyro_bias_rw_std=1e-4` and `bias_step=(30.0, 0.01)`: `gyro[:,1] == pitch_rate + gyro_bias_true[:,1]` and `gyro[:,i] == gyro_bias_true[:,i]` for i = 0, 2 (1e-12). |
| KS5 | **Determinism.** With S3 settings, the same seed gives identical `gyro_bias_true` and `gyro`. Seeds 0 and 1 give different `gyro_bias_true`. |
| KS6 | Each `ValueError` case in §4.5 raises `ValueError`. |

### 9.4 Deterministic filter correctness and tuning
| ID | Criterion |
|---|---|
| KD1 | `kalman_noise_matrices(0.01, 0.005, 0.05, 1e-4)` returns `Q = diag(2.5e-9, 1e-10)` (rtol 1e-12, off-diagonals exactly 0) and `R = (0.05/9.81)²` (rtol 1e-12). |
| KD2 | **Recurrence.** On random inputs with non-uniform `t` (N ≥ 50), non-default noise parameters, a given `initial_angle`, a non-zero `initial_bias` and a custom symmetric positive-definite `initial_cov`, the output matches the §5.3 recurrence. Angle and bias match to atol 1e-10. `cov` matches to rtol 1e-9 and atol 1e-20. |
| KD3 | **Constant bias, noise-free.** `constant_pitch_trajectory(0.3)`, both noise stds 0, 60 s, default bias, KF defaults: \|angle[−1] − 0.3\| ≤ 1e-6 rad and \|bias[−1] − 0.01\| ≤ 1e-6 rad/s. |
| KD4 | **Integration rule.** Default trajectory, both noise stds 0, `gyro_bias=(0,0,0)`, 60 s, KF defaults: max \|angle − pitch_true\| ≤ 1e-4 rad and max \|bias\| ≤ 1e-4 rad/s, both over t ≥ 10 s. A rectangle-rule implementation would give an angle error of about 2e-3 rad. |
| KD5 | **N = 1.** The result is `angle == [accel_angle[0]]` (or `initial_angle`), `bias == [initial_bias]`, and `cov[0] == diag(R, 4e-4)` with defaults (rtol 1e-12). |
| KD6 | **Covariance sanity.** On S1 with seed 0, for all k: `cov[k]` is symmetric (atol 1e-18), both eigenvalues are > 0, and for k ≥ 1, `cov[k,0,0] < R`. |
| KT1 | **Tuning sweep.** For S5 and seeds 0–2, scale factors `sQ, sR ∈ {0.1, 0.3, 1, 3, 10}` (25 grid points). Run KF with `gyro_noise_std = 0.005·√sQ`, `bias_rw_std = 1e-4·√sQ` and `accel_noise_std = 0.05·√sR`, other arguments at their defaults. The metric is the KF angle RMSE over t ≥ 30 s, averaged over the seeds. The value at (1, 1) must be ≤ 1.10 × the grid minimum. |
| KT2 | **Sweep sensitivity.** On the KT1 grid, the grid maximum must be ≥ 1.25 × the value at (1, 1), which shows the sweep can discriminate between settings. KT1 and KT2 may share one computation, and together they must run in under 60 s. |

### 9.5 Metrics, plots, interface
| ID | Criterion |
|---|---|
| KM1 | `convergence_time` with `t=[0,1,2,3,4,5]`, `e=[0.5,0.2,0.05,0.2,0.01,0.01]` (as estimate, with truth = 0) and `tol=0.1` returns 4.0. With all \|e\| ≤ tol it returns `t[0]`. With the last sample violating it returns `inf`. With `t_start=2.5`, the first example returns 4.0, and with `e[3]=0.05` it returns 3.0. The §6.1 errors raise `ValueError`. |
| KM2 | `coverage_fraction([0,1,3],[0,0,0],[1,1,1])` returns 2/3. `coverage_fraction([2],[0],[1])` returns 1.0 (inclusive). The §6.2 errors raise `ValueError`. |
| KG1 | `plot_error_comparison` with keys gyro/accel/CF/KF and the default `exclude`, without a window, gives 1 axes with 3 lines labelled accel, CF, KF, and y-data `rad2deg(est − truth)` (1e-9). With `t_window=(30,40)` it gives 2 axes, where axes 1 has x-limits (30, 40) (1e-9) and line x-data within [30, 40]. On S1 data, the y-limit rule of §7.1 holds on both axes. With `exclude=()`, axes 0 has 4 lines. |
| KG2 | `plot_bias_estimate` with `bias_true` gives 1 axes, lines labelled "estimate" and "truth" with y-data in °/s (1e-9), and exactly one `PolyCollection` whose vertex y-range equals the §7.2 band (1e-9). Without `bias_true` it has only the "estimate" line. |
| KI1 | T1 test I1 still passes. |
| KI2 | `inspect.signature` names and defaults of `simulate_pitch_imu` (§4.1), `kalman_noise_matrices`, `kalman_pitch`, `convergence_time`, `coverage_fraction`, `plot_error_comparison` and `plot_bias_estimate` match the spec exactly. |
| KI3 | Every `ValueError` case in §4.5, §5, §6 and §7 raises `ValueError`. |
| KI4 | No new function modifies its input arrays. |
| KI5 | `KalmanResult` fields have the §5.2 shapes and float64 dtype. The new metrics return Python or NumPy floats. |
| KI6 | `kalman_pitch` on N = 60 000 (S3 seed 0) completes in under 2 s (wall clock, best of 3 runs). |
| KR1 | The full Tier 1 test suite passes. Its I2 is updated to the §4.1 signature; no other Tier 1 test is changed. |
| KG3 | `tier2.ipynb` executes via nbconvert without error in under 180 s. |

---

## 10. Deliverables and definition of done
**EXECUTOR delivers:**
- the module changes and `tier2.ipynb`
- `TIER2_RESULTS.md`, with one row per KP, KC and KT criterion: the measured value for seed 0, the threshold, the margin ratio (threshold/measured, or measured/threshold for lower bounds), and units as required by §2.2

**TESTER delivers:**
- tests for every ID in §9, named after the ID (for example `test_KP6_kf_rmse_random_walk`)
- `tests/make_tier1_reference.py` (KS1), delivered **before** the EXECUTOR installs any Tier 2 change
- the updated Tier 1 I2 test

**Owner** runs `python tests/make_tier1_reference.py` on the Tier 1 code and keeps the resulting `tests/data/tier1_reference.npz` in the repository. Only after that are the EXECUTOR's Tier 2 changes installed.

The whole `tests/` suite must run in under 5 minutes.

**Tier 2 is done when** all Tier 1 and Tier 2 tests pass and the owner has reviewed the notebook plots.
