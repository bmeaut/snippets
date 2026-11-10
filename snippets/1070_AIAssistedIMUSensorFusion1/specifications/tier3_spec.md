# Tier 3 Specification — Roll and Pitch, Motion Disturbances, Accelerometer Gating, phyphox Data

**Status:** FINAL. Approved by the owner on 2026-10-31, including the §0 decisions and the §11 thresholds (RI6 limit raised to 8 s).
**Audience:** EXECUTOR (implements §5–§10) and TESTER (writes tests from §2–§12 without seeing code).
Where this document says "must", it is a testable requirement.
**Prerequisites:** `tier1_spec.md` and `tier2_spec.md` (both FINAL) stay binding, as corrected by the errata in §1. This document lists only what is added or changed. Earlier sections are cited as T1-§x and T2-§x.

**Writing rule for this tier.** An invariant stated in this document holds only under the conditions written next to it. Where an allowed edge case breaks a general statement, the statement names that case.

---

## 0. Decisions in this tier (for owner review)

| # | Decision | Reason |
|---|---|---|
| 0.1 | The Euler-rate mapping in both new filters is evaluated at a **midpoint angle**. First the rates are computed with the previous estimates, then the angles are advanced half a step, then the rates are recomputed with those midpoint angles (§6.1). | Using the previous angles directly leaves a first-order error of `(dt/2)·tanθ·φ̇·θ̇` in the roll rate. On the default trajectory that reaches about 4e-3 rad/s, which is larger than the bias accuracy the KF is meant to achieve. The midpoint step reduces it to second order. The filter states still enter linearly. |
| 0.2 | **Two decoupled 2-state KFs:** roll with state `[φ, b_x]` and pitch with state `[θ, b_y]`. Each uses coefficients taken from the other filter's previous estimate: the pitch filter's `F[0,1] = −cos φ_mid · dt`, and the roll filter's `Q[0,0]` and `R` are scaled by `1/cos² θ`. | These coefficients are the exact sensitivities of each Euler rate to its own bias, and the noise gain of the roll channel. Each filter stays a linear, time-varying KF whose coefficients are known inputs. Nothing is linearized with respect to the filter's own state, so this is not an EKF. |
| 0.3 | The new roll/pitch complementary filter (CF) uses the same trapezoidal rate, the same midpoint Euler mapping, and a gyro bias subtracted from the initial stationary estimate. The Tier 1 CF stays unchanged. | Without this, the CF comparison would be dominated by artefacts the KF does not have: the half-sample lead, the uncorrected bias × τ offset, and the mapping error. |
| 0.4 | Every filter parameter except `bias_rw_std` is **estimated from the initial stationary window**, for simulated and real data alike, with one rule (§6.3). The estimated parameters are the gyro bias (3 axes), the gyro noise std, the accelerometer noise std and the local gravity. | You asked for this rule on real data. Applying it to simulated data as well means the simulated scenarios exercise the same code path. |
| 0.5 | Gating rule: if `| ‖f‖ − gravity | > gate_threshold` at any sample within the last `gate_hold` seconds (inclusive), R is multiplied by `gate_r_scale`. The defaults are `gate_hold = 0.2 s` and `gate_r_scale = 1e4`, and the scenarios use `gate_threshold = 0.2 m/s²`. | The hold keeps the gate closed across the zero crossings of the vibration and across the falling flank of each pulse. Known limitation: a *horizontal* acceleration changes ‖f‖ only to second order, so a 0.2 m/s² threshold detects horizontal accelerations only above about 2 m/s². The rising flank of each pulse therefore reaches the filter ungated, and the §11 thresholds account for this. |
| 0.6 | The disturbance thresholds (RX1–RX4) come from transient estimates of the filter dynamics. They are less certain than the steady-state estimates behind the Tier 2 thresholds, although each still keeps the ≥ 1.5× margin. | If one fails, we decide together whether the threshold or the code is wrong, as agreed for Tier 1. |
| 0.7 | **RR4 premise.** The check that the end-segment angle is within 2° of the start segment assumes the phone was put back on the table in the same orientation. The table is tilted about 2°, so a different heading (yaw) could change roll and pitch by a few degrees. RR5 adds a placement-independent check: the filter must agree with the accelerometer tilt in the same still window. | **Resolved:** the owner confirmed that both recordings ended in the starting position and heading (the start and end accelerometer means differ by less than 0.2°). RR4 and RR5 are both kept. |
| 0.8 | The simulated vibration adds a small artefact to the gyro *measurements* that is not part of the true motion. Ground-truth angles are unaffected by vibration. | This models a vibrating mount without adding rotations to the ground truth, which keeps the error metrics clean. |

---

## 1. Errata to Tiers 1 and 2

| # | Location | Correction |
|---|---|---|
| E1 | T2-§4.3 | "`gyro_bias_true[0] == gyro_bias` always" is replaced by: "`gyro_bias_true[0] == gyro_bias` holds when `bias_step is None` or `t_step > t[0]`. If `t_step ≤ t[0]`, then `gyro_bias_true[0, 1] == gyro_bias[1] + delta`." KS1 and KS2 only use cases where the original equality holds, so no Tier 2 test changes. |
| E2 | T1-§3, T2-§3 | "Python ≥ 3.10" is replaced by the platform requirements in §2.1. Signatures written as `X | None` in T1 and T2 are spec notation. Implementations must use Python 3.9-valid syntax (§2.1). |
| E3 | T2-§7.1 | `plot_error_comparison` gains two parameters, appended at the end (§9.1). The Tier 2 test KI2 must be updated to the new signature. KG1 still applies unchanged. |

---

## 2. Conventions and platform

All of T1-§2 and T2-§2 apply. In addition:

### 2.1 Platform (binding for all modules, notebooks and tests, including Tiers 1–2)
- **Reference machine:** Python 3.9.13, NumPy 2.0.2, Matplotlib 3.9.4, pandas 2.3.3. These are the minimum versions. Code must not use APIs that were added after these versions.
- **Forbidden syntax and APIs** (each is Python 3.10 or later):
  - `X | Y` in type hints that are evaluated at runtime. Use `Optional`/`Union`, or put `from __future__ import annotations` at the top of the module.
  - `X | Y` in `isinstance`.
  - `match` statements.
  - Parenthesized multi-item `with` statements.
  - Backslashes, or the enclosing quote character, inside f-string expressions.
  - `zip(..., strict=True)`.
  - `itertools.pairwise`.
  - `dataclass(slots=..., kw_only=...)`.
  - `typing.TypeAlias`, `ParamSpec` and `Self`.
  - `except*`.
  - The `tomllib` module.
- **NumPy:** functions added in NumPy 2.1 or later are not allowed, for example `np.unstack` and `np.cumulative_sum`.
- **Notebook-only dependency:** `ipywidgets`. No `imu_*` module may import it.

### 2.2 Euler kinematics (yaw ≡ 0 in all simulated data)
- Rotation from body to world: `R = Ry(θ) · Rx(φ)`, which written out is:

  `R = [[cθ, sθ·sφ, sθ·cφ], [0, cφ, −sφ], [−sθ, cθ·sφ, cθ·cφ]]`

  where `c` and `s` denote cos and sin.
- Body rates from Euler rates (used by the simulator):
  - `ωx = φ̇`
  - `ωy = cos φ · θ̇`
  - `ωz = −sin φ · θ̇`
- Euler rates from body rates (used by the filters). This map is denoted `E(φ, θ; w)`:
  - `φ̇ = w_x + tan θ · (sin φ · w_y + cos φ · w_z)`
  - `θ̇ = cos φ · w_y − sin φ · w_z`
- The mapping is valid for |θ| ≤ 60°. Behavior beyond that is unspecified.

### 2.3 Units in reports
The rule of T2-§2.2 applies. Angles are printed in °, and rates and biases in both rad/s and °/s. Accelerations and noise levels are printed in m/s² and rad/s.

---

## 3. Scope

In scope for Tier 3:
- A roll-and-pitch simulator with linear-acceleration and vibration disturbance segments.
- A stationary-parameter estimator.
- A roll/pitch CF.
- A roll/pitch KF with optional accelerometer gating.
- A phyphox zip loader and resampler.
- Plot additions.
- `tier3.ipynb`, including an interactive section.

Out of scope:
- yaw and magnetometer
- EKF and quaternions
- estimating the z-axis gyro bias inside the filter
- bias random walk in the new simulator
- centripetal acceleration
- the phyphox Android export format and phyphox meta files
- automatic detection of still segments
- streaming APIs

---

## 4. File layout

Unchanged from T2-§3, with these additions:
```
project_root/
  imu_io.py                      # phyphox loading and resampling (numpy, pandas, zipfile)
  tier3.ipynb
  TIER3_RESULTS.md               # EXECUTOR
  data/phone_tilts.zip           # owner-provided recording A
  data/phone_disturbances.zip    # owner-provided recording B
```
Import rules:
- `imu_filters` must not import `imu_sim`, `imu_metrics`, `imu_plots`, `imu_io`, pandas or matplotlib.
- `imu_io` must not import `imu_sim`, `imu_filters` or `imu_plots`.
- `imu_plots` may import `imu_metrics`.

**Runtime dependencies:** NumPy, Matplotlib and pandas (pandas only in `imu_io`). The notebook also needs `ipywidgets`.
**Test-only dependencies:** pytest, jupyter/nbconvert and ipykernel.

---

## 5. Additions to `imu_sim.py`

`simulate_pitch_imu` and everything else from Tiers 1 and 2 stays unchanged.

### 5.1 Trajectories
A **roll-pitch trajectory** is a callable that maps `t (N,)` to `(roll, pitch, roll_rate, pitch_rate)`, each `(N,)`, in rad and rad/s. The rates are the exact analytic derivatives.

- `default_roll_pitch_trajectory(t)`. Let `τ = t − 5.0`.
  - For `t < 5.0`, all four outputs are 0. This is the rest phase.
  - For `t ≥ 5.0`:
    - `roll(t)  = 0.6 · sin(2π·0.05·τ) · sin(2π·0.17·τ)`
    - `pitch(t) = 0.7 · sin(2π·0.04·τ) · sin(2π·0.23·τ)`
    - The rates follow from the product rule, `d/dτ [A sin(aτ) sin(bτ)] = A·(a cos(aτ) sin(bτ) + b sin(aτ) cos(bτ))`, with `a = 2π·f1` and `b = 2π·f2`.

  Both angles and both rates are continuous at `t = 5`. As a consequence of these formulas, |roll| ≤ 0.6 rad and |pitch| ≤ 0.7 rad.
- `constant_roll_pitch_trajectory(roll: float, pitch: float) -> Callable`. Both angles are constant for all `t`, and both rates are 0.

### 5.2 Disturbance segments
- `LinearAccelSegment(NamedTuple)` has fields `t_start` (s), `duration` (s), `peak` (m/s²) and `azimuth` (rad).
  - It applies the world-frame linear acceleration `a_w(t) = peak · sin(π (t − t_start) / duration) · (cos azimuth, sin azimuth, 0)` for `t_start ≤ t ≤ t_start + duration`, and zero otherwise.
- `VibrationSegment(NamedTuple)` has fields `t_start` (s), `duration` (s), `accel_amp` (m/s²), `freq` (Hz) and `gyro_amp` (rad/s).
  - For `t_start ≤ t ≤ t_start + duration`, and for each body axis i with phase `p_i ∈ (0, 2π/3, 4π/3)`:
    - the accelerometer gets an additive `accel_amp · sin(2π·freq·(t − t_start) + p_i)`
    - the gyro measurement gets an additive `gyro_amp · sin(2π·freq·(t − t_start) + p_i)`
  - This is a sensor-level artefact. It does not change the true angles (§0.8).
- Plain tuples of the same length and field order are accepted in place of the NamedTuples.
- Constants:
  - `DEFAULT_LINEAR_ACCEL_SEGMENTS = (LinearAccelSegment(30.0, 2.0, 3.0, 0.0), LinearAccelSegment(60.0, 2.0, 3.0, π/2))`
  - `DEFAULT_VIBRATION_SEGMENTS = (VibrationSegment(90.0, 5.0, 2.0, 15.0, 0.05),)`

### 5.3 `SimulatedRollPitchIMU` (frozen dataclass)
| Field | Shape | Meaning |
|---|---|---|
| `t` | `(N,)` float64 | s |
| `gyro` | `(N, 3)` float64 | measured, rad/s |
| `accel` | `(N, 3)` float64 | measured specific force, m/s² |
| `roll_true`, `pitch_true` | `(N,)` float64 | rad |
| `gyro_bias` | `(3,)` float64 | constant bias applied, rad/s |
| `fs` | float | Hz |
| `disturbed_true` | `(N,)` bool | True if sample k lies inside any disturbance segment (closed interval) |

### 5.4 `simulate_roll_pitch_imu`
```
simulate_roll_pitch_imu(
    duration: float = 120.0,
    fs: float = 100.0,
    trajectory: Optional[Callable] = None,       # None -> default_roll_pitch_trajectory
    gyro_bias = (0.01, 0.01, 0.01),              # rad/s
    gyro_noise_std: float = 0.005,               # rad/s
    accel_noise_std: float = 0.05,               # m/s²
    seed: Optional[int] = None,
    linear_accel_segments = (),                  # sequence of LinearAccelSegment
    vibration_segments = (),                     # sequence of VibrationSegment
) -> SimulatedRollPitchIMU
```
**Sampling.** As in T1-§4.4: `N = int(round(duration·fs))` and `t[k] = k/fs`.

**Model.** With `φ, θ, φ̇, θ̇ = trajectory(t)`, `b = gyro_bias`, `V_a` and `V_g` the sums of the vibration terms, and `n_g`, `n_a` white Gaussian noise drawn from one `default_rng(seed)`:
- `gyro = (φ̇, cosφ·θ̇, −sinφ·θ̇) + b + V_g + n_g`
- `accel = GRAVITY·(−sinθ, sinφ·cosθ, cosφ·cosθ) + Rᵀ·Σ a_w + V_a + n_a`

`R` is the matrix of §2.2, and the sum runs over all linear-acceleration segments. Written out, for `a_w = (ax, ay, 0)`:

`Rᵀ·a_w = (cθ·ax,  sθ·sφ·ax + cφ·ay,  sθ·cφ·ax − sφ·ay)`

**Determinism.** As in T1-§4.4.

**Errors** (`ValueError`):
- the Tier 1 cases of T1-§4.4, applied to both angles (|roll| or |pitch| > π/3 + 1e-9)
- a segment with the wrong number of fields, or a non-finite value
- `duration ≤ 0`
- `peak < 0`
- `accel_amp < 0` or `gyro_amp < 0`
- `freq ≤ 0` or `freq ≥ fs/2`

---

## 6. Additions to `imu_filters.py`

### 6.1 Shared step definitions (binding for §6.2 and §6.4)
For k ≥ 1, given the previous estimates `φp, θp` and a bias-corrected trapezoidal rate vector `w` (defined in each filter):
```
dt       = t[k] − t[k−1]
(r1, p1) = E(φp, θp; w)                       # §2.2
φm       = φp + 0.5·dt·r1
θm       = θp + 0.5·dt·p1
(r, p)   = E(φm, θm; w)                       # Euler rates used for the step
```
`(roll_acc, pitch_acc) = accel_tilt(accel)` from T1-§5.1.

### 6.2 `complementary_roll_pitch`
```
complementary_roll_pitch(t, gyro, accel, tau=0.2, gyro_bias=(0.0, 0.0, 0.0),
                         initial_roll=None, initial_pitch=None) -> Tuple[ndarray, ndarray]
```
**Returns** `(roll, pitch)`, each `(N,)` in rad.

**Recurrence:**
- `roll[0] = initial_roll`, or `roll_acc[0]` if None. `pitch[0]` is defined the same way.
- For k ≥ 1:
  - `w = (gyro[k−1] + gyro[k])/2 − gyro_bias`
  - apply §6.1 with `φp = roll[k−1]` and `θp = pitch[k−1]`
  - `α = tau/(tau + dt)`
  - `roll[k] = α·(φp + r·dt) + (1−α)·roll_acc[k]`
  - `pitch[k] = α·(θp + p·dt) + (1−α)·pitch_acc[k]`

**Errors** (`ValueError`):
- `tau ≤ 0`
- `t` not of shape (N,), or `gyro` / `accel` not of shape (N, 3)
- `N < 1`
- `t` not strictly increasing
- `gyro_bias` not of shape (3,)

### 6.3 `estimate_stationary(t, gyro, accel, t_start, t_end) -> StationaryEstimate`
The function uses the samples with `t_start ≤ t ≤ t_end`. `StationaryEstimate` is a frozen dataclass with these fields:

| Field | Definition |
|---|---|
| `gyro_bias` | `(3,)`, the mean of gyro over the window, rad/s |
| `gyro_noise_std` | `sqrt(mean_i var_i(gyro))` with `ddof=1`, rad/s |
| `accel_noise_std` | `sqrt(mean_i var_i(accel))` with `ddof=1`, m/s² |
| `gravity` | `mean(‖accel_k‖)` over the window, m/s² |
| `n_samples` | int |

**Errors** (`ValueError`): fewer than 10 samples in the window, `t_start ≥ t_end`, or the shape errors listed in §6.2.

### 6.4 `kalman_roll_pitch`
```
kalman_roll_pitch(
    t, gyro, accel,
    gyro_noise_std: float = 0.005,
    accel_noise_std: float = 0.05,
    bias_rw_std: float = 1e-4,
    gravity: float = 9.81,
    gyro_bias_z: float = 0.0,
    initial_bias = (0.0, 0.0),                # (b_x, b_y), rad/s
    gate_threshold: Optional[float] = None,   # m/s²; None disables gating
    gate_hold: float = 0.2,                   # s
    gate_r_scale: float = 1e4,
    initial_roll: Optional[float] = None,
    initial_pitch: Optional[float] = None,
) -> RollPitchKalmanResult
```
`RollPitchKalmanResult` is a frozen dataclass with these fields:
- `roll`, `pitch`, `bias_x`, `bias_y`: each `(N,)` float64
- `cov_roll`, `cov_pitch`: each `(N, 2, 2)` float64
- `gated`: `(N,)` bool

**Gate.**
- `R0 = (accel_noise_std/gravity)²`.
- `trig[k] = (gate_threshold is not None) and | ‖accel[k]‖ − gravity | > gate_threshold`
- `gated[k] = any(trig[j])` over all j ≤ k with `t[j] ≥ t[k] − gate_hold`
- If `gate_threshold is None`, then `gated` is all False.

**Initialization** (k = 0, no measurement update):
- `roll[0]` and `pitch[0]` are set as in §6.2.
- `(bias_x[0], bias_y[0]) = initial_bias`.
- `cov_roll[0] = diag(R0 / cos²(pitch[0]), 0.02²)`.
- `cov_pitch[0] = diag(R0, 0.02²)`.

**Recurrence.** This form is binding, and test RD1 reproduces it. For k ≥ 1, with `φp, θp, bxp, byp` the posteriors at k−1:
```
ḡ   = (gyro[k−1] + gyro[k]) / 2
w   = (ḡ_x − bxp,  ḡ_y − byp,  ḡ_z − gyro_bias_z)
apply §6.1  → r, p, φm, θm
c2  = cos²(θp);   s = gate_r_scale if gated[k] else 1
ROLL : x⁻ = [φp + r·dt, bxp];  F = [[1, −dt], [0, 1]]
       Q = diag(gyro_noise_std²·dt² / c2, bias_rw_std²·dt);  R = s·R0 / c2;  z = roll_acc[k]
PITCH: x⁻ = [θp + p·dt, byp];  F = [[1, −cos(φm)·dt], [0, 1]]
       Q = diag(gyro_noise_std²·dt², bias_rw_std²·dt);  R = s·R0;  z = pitch_acc[k]
each : P⁻ = F·cov[k−1]·Fᵀ + Q;  S = P⁻[0,0] + R;  K = P⁻[:,0] / S
       x = x⁻ + K·(z − x⁻[0]);  cov[k] = P⁻ − S·(K Kᵀ)
```
**Reduction property** (tested by RD2, which follows from the recurrence). Suppose all of the following hold:
- `gyro[:,0] ≡ 0`, `gyro[:,2] ≡ 0` and `accel[:,1] ≡ 0`
- `accel[:,2] > 0`
- `gyro_bias_z = 0`, `initial_bias[0] = 0`, `initial_roll` is None or 0
- gating is off

Then `roll ≡ 0`, `bias_x ≡ 0`, and `pitch`, `bias_y` and `cov_pitch` equal the T2 `kalman_pitch` output on `(t, gyro[:,1], pitch_acc)` with the same noise parameters, `initial_bias = initial_bias[1]` and `initial_angle = initial_pitch`.

**Errors** (`ValueError`):
- the shape and time cases of §6.2
- the cases of T2-§5.1
- `gate_threshold` not None and ≤ 0
- `gate_hold < 0`
- `gate_r_scale < 1`
- `initial_bias` not of length 2

**Performance:** for N = 60 000 the call must take under 8 s on the reference machine, measured as the best of 3 runs.

**Implementation recommendation** (not tested beyond RI6). Inside the per-sample loop, write the 2×2 covariance propagation and update with scalar arithmetic on Python floats: for example, `p00, p01, p11` for each filter, using the symmetry of `cov`. Avoid allocating small NumPy arrays or calling `np.dot` / `@` per step, because their overhead dominates at this size. Use `math.sin`, `math.cos` and `math.tan` on scalars instead of their NumPy versions. Precompute whatever the loop does not depend on before it starts: `accel_tilt`, the trapezoidal gyro means, `dt` and the `gated` flags. Write the results into preallocated output arrays. The scalar form must still reproduce the §6.4 recurrence within the RD1 tolerances.

---

## 7. `imu_io.py`

### 7.1 `PhyphoxRecording` (frozen dataclass)
| Field | Shape |
|---|---|
| `accel_t` | `(Na,)` float64, s |
| `accel` | `(Na, 3)` float64, m/s² |
| `gyro_t` | `(Ng,)` float64, s |
| `gyro` | `(Ng, 3)` float64, rad/s |
| `source` | str, the zip path |

### 7.2 `load_phyphox_zip(path) -> PhyphoxRecording`
**Accepted input** is a phyphox 1.2.1 (iOS) "simple experiment" export in the format **"CSV (Comma, decimal point)"**:
- The zip must contain the members `Accelerometer.csv` and `Gyroscope.csv` at the archive root, with exactly those names.
- Any other members, including `meta/time.csv` and `meta/device.csv`, are ignored and may be absent.

**File format** of each CSV member:
- UTF-8 text. An optional BOM is ignored. Line endings may be `\n` or `\r\n`.
- The first line is a header of four comma-separated fields. After stripping whitespace and one pair of surrounding double quotes from each field, the header must equal exactly:
  - `Accelerometer.csv`: `Time (s)`, `X (m/s^2)`, `Y (m/s^2)`, `Z (m/s^2)`
  - `Gyroscope.csv`: `Time (s)`, `X (rad/s)`, `Y (rad/s)`, `Z (rad/s)`
- Each following non-empty line has 4 comma-separated decimal numbers, with a decimal point and optional exponent (e.g. `1.156000071E-3`).
- Lines that are empty or contain only whitespace are skipped.

**Output.** Values are returned unchanged: no unit conversion, no axis remapping, and no time shift. The phyphox iOS axes and signs match T1-§2.2–2.3.

**Errors:**
- `FileNotFoundError` if `path` does not exist.
- `ValueError` in these cases:
  - not a zip file
  - a required member is missing
  - a header mismatch (which catches, among others, the semicolon/decimal-comma export)
  - a line with the wrong field count
  - a non-numeric or non-finite value
  - fewer than 2 data rows
  - time not strictly increasing

### 7.3 `resample_common(accel_t, accel, gyro_t, gyro, fs=100.0) -> Tuple[t, gyro_rs, accel_rs]`
- The overlap is `t0 = max(accel_t[0], gyro_t[0])` and `t1 = min(accel_t[−1], gyro_t[−1])`.
- The grid is `t[k] = t0 + k/fs` for `k = 0 … floor((t1 − t0)·fs + 1e-9)`.
- Each axis is linearly interpolated with `np.interp`.
- **Returns** `t (M,)`, `gyro_rs (M, 3)` and `accel_rs (M, 3)`, all float64.
- **Errors** (`ValueError`): `fs ≤ 0`, shape mismatches, non-increasing time, or `M < 2`.

---

## 8. Additions to `imu_metrics.py`

No new functions. Disturbance metrics are computed with the existing functions on masked or sliced arrays, as defined in §11.

---

## 9. Changes to `imu_plots.py`

### 9.1 `plot_error_comparison` — new parameters (E3)
```
plot_error_comparison(t, truth, estimates, exclude=("gyro",), t_window=None, title="",
                      background=("accel",), shade=None) -> Figure
```
**Background lines.** These are shown keys (keys not in `exclude`) that are also in `background`.
- They are drawn **before** all other lines, with `alpha ≤ 0.4` and a `zorder` lower than every foreground line.
- Foreground lines have `alpha` None or 1.
- A key that is in both `exclude` and `background` is excluded.

**Y-limits** apply on each axes. Let `m_f` and `M_f` be the min and max of the foreground y-data on that axes, and `r_f = M_f − m_f`.
- If at least one foreground line exists and `r_f > 0`, the limits must contain `[m_f, M_f]` and lie within `[m_f − 0.1·r_f, M_f + 0.1·r_f]`.
- If at least one foreground line exists and `r_f = 0`, the limits are `(m_f − 1, m_f + 1)`.
- If all shown keys are background keys, the T2-§7.1 rule applies to all plotted lines.

**Shading.** `shade` is either None or a bool array of shape (N,).
- For each maximal run of consecutive True samples `i…j`, every axes gets one `axvspan(t[i], t[j])` with `alpha ≤ 0.3`.
- Only the first span is labelled, `"disturbance"`.
- If `shade` is None, no spans are drawn.

**Errors:** the cases of T2-§7.1, plus `ValueError` if `shade` has the wrong shape.

### 9.2 `plot_estimates(t, estimates, title="", shade=None) -> Figure`
- The figure is for real data, where there is no truth. It has exactly 1 axes.
- It has one line per key, labelled with the key, with y-data `rad2deg(estimate)`.
- `shade` behaves as in §9.1.
- The y-axis label contains "°". The axes has a legend. The function must not call `plt.show()`.
- **Errors** (`ValueError`): an empty dict, a length mismatch, or `shade` with the wrong shape.

---

## 10. `tier3.ipynb`

The notebook must:
- Execute via `jupyter nbconvert --to notebook --execute tier3.ipynb` in under 240 s, without a live front end.
- Follow §2.1, and pass no `*_true` field to any filter.

**Estimator configuration** (binding for the notebook and for §11). The method keys are:
- `"accel"`
- `"CF"`
- `"KF"`
- `"KF-gated"`

All four use `est = estimate_stationary(t, gyro, accel, W0, W1)`, where `(W0, W1)` is the **rest window**:
- `(0.0, 4.5)` for simulated data
- `(t[0] + 1.0, t[0] + 7.0)` for real data, after `resample_common`

| Key | Call |
|---|---|
| accel | `accel_tilt(accel)` |
| CF | `complementary_roll_pitch(t, gyro, accel, tau=0.2, gyro_bias=est.gyro_bias)` |
| KF | `kalman_roll_pitch(t, gyro, accel, gyro_noise_std=est.gyro_noise_std, accel_noise_std=est.accel_noise_std, gravity=est.gravity, gyro_bias_z=est.gyro_bias[2], initial_bias=(est.gyro_bias[0], est.gyro_bias[1]))` |
| KF-gated | the same as KF, with `gate_threshold=0.2` |

The notebook must contain these sections, with seed 0 for simulated data:

| Section | Content |
|---|---|
| Clean run (S6) | Table of RMSE per angle and method, in °. `plot_error_comparison` per angle, with `background=("accel",)`. A bias plot (T2 `plot_bias_estimate`) for `bias_x` and `bias_y` with truth. |
| Disturbances (S7) | Table per method and angle: max abs error inside `disturbed_true` (°), recovery time per segment (s), and quiet RMSE (°), as defined in §11. `plot_error_comparison` per angle with `shade=disturbed_true`. A zoom with `t_window=(28, 40)`. |
| Real data A and B | Table of the `StationaryEstimate` values, with units. `plot_estimates` per angle with `shade=KF-gated.gated`, and one zoom. A table of start-window vs end-window mean angles per method (°). KF bias estimates in rad/s and °/s. |
| Interactive | An ipywidgets section (see below). |
| Discussion | Short markdown, covering gating at the rising flank of a pulse (§0.5), CF vs KF recovery, and the real-data observations. |

**Interactive section** (not tested beyond notebook execution).
- **Controls:**
  - a dataset dropdown with options S6, S7, A and B
  - the CF tau, on a log scale from 0.02 to 2 s
  - a KF Q scale and an R scale, each on a log scale from 0.01 to 100, applied as in T2 KT1
  - a gating checkbox
  - the gate threshold, from 0.05 to 2 m/s²
- **Output:** the error plot (simulated data) or the angle plot (real data), plus a small metrics table.
- Data is loaded once, before the widgets are created.
- Under nbconvert the cell must render its initial output for the default control values without error. It must not wait for user input.

---

## 11. Scenarios and success criteria

**Scenarios:**

| ID | Call | Seeds |
|---|---|---|
| S6 | `simulate_roll_pitch_imu()` (120 s, no disturbances) | 0–4 |
| S7 | `simulate_roll_pitch_imu(duration=150.0, linear_accel_segments=DEFAULT_LINEAR_ACCEL_SEGMENTS, vibration_segments=DEFAULT_VIBRATION_SEGMENTS)` | 0–4 |

**Definitions:**
- Estimators are configured as in §10. Errors are computed against `roll_true` and `pitch_true`.
- **"Max disturbance error"** is the maximum, over both angles, of `max_abs_error` restricted to samples where `disturbed_true` is True.
- **Recovery** applies to each S7 segment s and each angle. Its window runs from the segment end `e_s` to the next segment start, or to the end of the run for the last segment. The windows are [32, 60), [62, 90) and [95, 150]. Recovery time is `convergence_time(window, tol=deg2rad(0.5)) − e_s`, using the window's own `t`, estimate and truth. An `inf` result counts as a failure.
- **"Quiet"** samples are those with `t ≥ 20` that are not disturbed and not within 15 s after any segment end. These are [20, 30), [47, 60), [77, 90) and [110, 150].

Each criterion must hold for every listed seed. Expected values in brackets are planner estimates, not test values.

### 11.1 Clean performance (S6)
| ID | Criterion | (expected) |
|---|---|---|
| RP1 | KF and KF-gated: RMSE over t ≥ 20 s ≤ 0.08°, for roll and for pitch | (roll ≈0.04°, pitch ≈0.03°) |
| RP2 | CF: RMSE over t ≥ 20 s ≤ 0.15°, for roll and for pitch | (≈0.05–0.07°) |
| RP3 | KF: \|bias_x − b_x\| and \|bias_y − b_y\| ≤ 1e-3 rad/s (0.057 °/s) for all t ≥ 20 s | (max ≈5e-4) |

### 11.2 Disturbances (S7)
| ID | Criterion | (expected) |
|---|---|---|
| RX1 | KF-gated max disturbance error ≤ 7.5° | (≈4–5°) |
| RX2 | KF-gated max disturbance error ≤ 0.55 × KF max disturbance error (same seed) | (ratio ≈0.35) |
| RX3 | KF-gated max disturbance error ≤ 0.4 × CF max disturbance error (same seed) | (ratio ≈0.25) |
| RX4 | Recovery time for every segment and angle: ≤ 10 s for KF and KF-gated, ≤ 3 s for CF | (KF ≈3–5 s, KF-gated ≈2–3 s, CF ≈0.5 s) |
| RX5 | KF-gated quiet RMSE ≤ 0.08°, for each angle | (≈0.04°) |

### 11.3 Deterministic filter correctness
| ID | Criterion |
|---|---|
| RD1 | **KF recurrence.** On random inputs (N ≥ 50) with non-uniform `t`, |angles| ≤ 0.8 rad, non-default parameters, `gate_threshold` set so that about 30 % of samples trigger, and `gate_hold` covering several samples, `kalman_roll_pitch` matches §6.4. `gated` matches exactly. Angles and biases match to atol 1e-10. Covariances match to rtol 1e-9 and atol 1e-20. |
| RD2 | **Reduction.** The §6.4 reduction property holds on the T2 S1 data (seed 0) with `accel[:,1]`, `gyro[:,0]` and `gyro[:,2]` set to 0: `roll` and `bias_x` are exactly 0, and `pitch`, `bias_y` and `cov_pitch` equal `kalman_pitch` to atol 1e-12. |
| RD3 | **Noise-free tracking.** Default trajectory, both noise stds 0, `gyro_bias=(0.01, −0.02, 0.03)`, 120 s. KF called with defaults, except `gyro_bias_z=0.03` and `initial_bias=(0.01, −0.02)`. For t ≥ 5 s: max \|roll error\| and max \|pitch error\| ≤ 2e-4 rad, and max \|bias_x − 0.01\| and max \|bias_y + 0.02\| ≤ 2e-4 rad/s. *(A mapping without the midpoint step would give about 1e-3.)* |
| RD4 | **Gate logic.** On hand-built inputs, with non-uniform `t` and `‖accel‖` crossing the threshold at known samples, `gated` follows §6.4. This includes the inclusive hold boundary `t[j] = t[k] − gate_hold`, and the case `gate_threshold=None`, where `gated` is all False. |
| RD5 | **CF recurrence and steady state.** `complementary_roll_pitch` matches §6.2 on random inputs (1e-12). With `constant_roll_pitch_trajectory(0.2, 0.3)`, no noise, true bias b, and `gyro_bias = b + (Δ, 0, 0)` where Δ = 0.01: the final roll error equals `Δ·tau` (1e-6) and the final pitch error is ≤ 1e-9. |
| RD6 | **N = 1.** Both filters return their initial values. `cov_roll[0]` and `cov_pitch[0]` are as in §6.4 (rtol 1e-12). `gated[0]` follows the gate rule. |
| RD7 | **`estimate_stationary` exact values.** On hand-made arrays with known means and variances, all fields match the §6.3 definitions (1e-12). |
| RD8 | **`estimate_stationary` statistics.** On S6 with seed 0 and window (0, 4.5): \|gyro_bias − b\| ≤ 4·0.005/√n per axis; gyro_noise_std and accel_noise_std are within ±10 % of 0.005 and 0.05; \|gravity − 9.81\| ≤ 0.01. |

### 11.4 Simulator
| ID | Criterion |
|---|---|
| RS1 | **Noise-free, no disturbances.** `gyro == (φ̇, cosφ·θ̇, −sinφ·θ̇) + b` and `accel == GRAVITY·(−sinθ, sinφcosθ, cosφcosθ)` (1e-12), using the trajectory's own outputs. `disturbed_true` is all False. |
| RS2 | **Linear segment, noise-free.** With one `LinearAccelSegment(10.0, 2.0, 3.0, 0.7)`: `accel` minus the gravity term equals the §5.4 expression `Rᵀ·a_w` (1e-12), and is 0 outside [10, 12]. `disturbed_true` is True exactly where 10 ≤ t ≤ 12. `gyro` and the true angles equal those of a run without the segment. |
| RS3 | **Vibration, noise-free.** With one `VibrationSegment(10.0, 1.0, 2.0, 15.0, 0.05)`: the differences in `accel` and `gyro` relative to a run without vibration equal the §5.2 terms (1e-12). The true angles are identical. |
| RS4 | **Trajectory.** For t < 5, all outputs of `default_roll_pitch_trajectory` are 0. \|roll\| ≤ 0.6 and \|pitch\| ≤ 0.7. On t ∈ [5.01, 120], the rates match a central difference of the angles with step 1e-6 s (atol 1e-6). |
| RS5 | **Noise statistics and determinism.** On S6 with seed 0, the residuals of `gyro` and `accel` against the noise-free model have std within ±5 % of 0.005 and 0.05 per axis. The same seed gives identical arrays. Seeds 0 and 1 give different `gyro` arrays. |
| RS6 | Each `ValueError` case in §5.4 raises `ValueError`. |

### 11.5 phyphox loader and resampler (synthetic fixtures; the TESTER builds zips in `tmp_path`)
| ID | Criterion |
|---|---|
| RL1 | A valid zip in the §7.2 format, with values in the exponent notation shown there, loads with exact float values, shapes and dtypes. Extra members and `meta/*` are ignored. A zip without `meta/` also loads. A BOM, `\r\n` line endings and trailing blank lines are accepted. |
| RL2 | Each §7.2 error case raises the specified exception. This includes a semicolon/decimal-comma export, an Android-style header (e.g. `"Acceleration x (m/s^2)"`), members inside a subfolder only, a non-numeric cell, and a repeated timestamp. |
| RL3 | `resample_common`: for linear test signals, the resampled values are exact (1e-12). With accelerometer timestamps offset +5 ms from the gyro timestamps, the grid starts at the later first timestamp, has step 1/fs (1e-12) and ends at or before the earlier last timestamp. The §7.3 errors raise `ValueError`. |

### 11.6 Real recordings (`data/phone_tilts.zip` = A, `data/phone_disturbances.zip` = B)
The tests fail, and do not skip, if a file is missing. They use the §10 configuration and the common grid at 100 Hz.

| ID | Criterion | (measured by owner) |
|---|---|---|
| RR1 | Both files load. Each sensor has ≥ 5000 samples. The median sample spacing is within 2 % of 0.01 s. The common grid spans ≥ 55 s. | (60 s, 100 Hz) |
| RR2 | Rest window: \|est.gravity − 9.81\| ≤ 0.2 m/s²; every per-axis gyro std ≤ 0.01 rad/s; \|est.gyro_bias\| ≤ 0.01 rad/s per axis; est.accel_noise_std ≤ 0.05 m/s². | (9.84; 0.0009; 1e-4; 0.01) |
| RR3 | **Axis and sign consistency, recording A.** `complementary_roll_pitch(..., tau=1e9, gyro_bias=est.gyro_bias)`, which is pure Euler-mapped gyro integration, has Pearson r ≥ 0.9 against `accel_tilt` for roll and for pitch. | (≈0.99) |
| RR4 | For A and B, and for each angle: \|mean KF-gated angle over [t_last − 7, t_last − 1] − mean over the rest window\| ≤ 2°. *(Valid because both recordings end in the starting position and heading, §0.7.)* | (accel start vs end < 0.2°) |
| RR5 | For A and B, and for each angle: \|mean KF-gated angle − mean accel tilt\| over the end window [t_last − 7, t_last − 1] ≤ 1°. | |

### 11.7 Plots, interface, regression
| ID | Criterion |
|---|---|
| RG1 | `plot_error_comparison` with keys gyro/accel/CF/KF and the defaults: the first line is `"accel"`, with `alpha ≤ 0.4` and a `zorder` below that of CF and KF. The §9.1 y-limit rule holds on S7 data. With `background=()` all lines have `alpha` None or 1. With `shade=disturbed_true` from S7, axes 0 has exactly 3 spans, and exactly one legend entry is "disturbance". With `shade=None` there are no spans. |
| RG2 | `plot_estimates`: 1 axes, one line per key with `rad2deg` y-data (1e-9), labels as specified, and shading as in RG1. The §9.2 errors raise `ValueError`. |
| RI1 | In fresh interpreters: `import imu_filters` loads none of `imu_sim`, `imu_metrics`, `imu_plots`, `imu_io`, `pandas` or `matplotlib`. `import imu_io` loads none of `imu_sim`, `imu_filters` or `imu_plots`. |
| RI2 | `inspect.signature` names and defaults match §5.4, §6.2–6.4, §7.2–7.3 and §9. The Tier 2 KI2 test is updated for E3. |
| RI3 | Every `ValueError` and `FileNotFoundError` case in §5–§9 is raised as specified. |
| RI4 | No new function modifies its inputs. |
| RI5 | Return shapes and dtypes are as specified. `gated` and `disturbed_true` have dtype bool. |
| RI6 | `kalman_roll_pitch` on N = 60 000 (for example 600 s of S6 settings with seed 0) runs in under 8 s on the reference machine (wall clock, best of 3). |
| RI7 | The Tier 1 and Tier 2 suites pass, with only the KI2 update from E3. |
| RG3 | `tier3.ipynb` executes via nbconvert in under 240 s. |

---

## 12. Deliverables and definition of done
**EXECUTOR delivers:**
- `imu_io.py`, the module changes and `tier3.ipynb`, all following §2.1
- `TIER3_RESULTS.md`, with these columns for every RP, RX and RR criterion: the seed-0 value, the threshold, the margin ratio, and units per §2.3. It also contains the real-data `StationaryEstimate` table.

**TESTER delivers:**
- tests for every ID in §11, named after the ID (for example `test_RX2_gating_vs_ungated`), with Python 3.9-valid syntax
- the updated Tier 2 KI2 test

**Owner** places the two recordings in `data/`.

The whole `tests/` suite must run in under 6 minutes on the reference machine.

**Tier 3 is done when** all Tier 1–3 tests pass on the reference machine and the owner has reviewed the notebook plots.
