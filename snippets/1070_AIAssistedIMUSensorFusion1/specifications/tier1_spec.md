# Tier 1 Specification — IMU Simulation, Gyro Integration, Accelerometer Tilt, Complementary Filter

**Status:** FINAL. Approved by the owner on 2026-10-31, including the §8 thresholds.
**Audience:** EXECUTOR (implements §3–§7) and TESTER (writes tests from §2–§9 without seeing code).
Where this document says "must", it is a testable requirement.

---

## 1. Scope

In scope for Tier 1:
- Simulating a 6-axis IMU undergoing **pitch-only** rotation (roll ≡ 0, yaw ≡ 0) with known ground truth.
- Three pitch estimators: gyro integration, accelerometer-only tilt, complementary filter.
- Metrics (RMSE, drift rate, max absolute error) and one comparison-plot function.
- A notebook that runs the comparison.

Out of scope (do **not** implement): roll motion, Euler-rate kinematics, linear acceleration or vibration, gyro bias random walk, Kalman filtering, CSV loading, angle wrapping, streaming/class-based APIs.

---

## 2. Conventions (binding for all tiers)

### 2.1 Units
| Quantity | Unit in code |
|---|---|
| Time | s |
| Angles | rad |
| Angular rate | rad/s |
| Acceleration / specific force | m/s² |

Degrees are used **only** in plots and printed tables. No function in §4–§6 accepts or returns degrees.

### 2.2 Body frame (Android / phyphox convention)
With the phone in portrait orientation, screen facing the viewer:
- **x** points to the right edge of the screen
- **y** points to the top edge of the screen
- **z** points out of the screen, toward the viewer

### 2.3 Sensor sign conventions
- **Gyroscope:** angular velocity of the body relative to the world, expressed in the body frame. Positive values mean counter-clockwise rotation about the axis when viewed from the positive end, which is the right-hand rule.
- **Accelerometer:** specific force `f = a − g_vec`, in the body frame. A phone lying flat, screen up and stationary reads `f ≈ (0, 0, +G)`.
- `G = 9.81` m/s², exposed as the constant `imu_sim.GRAVITY`.

### 2.4 Attitude angles
- Rotation from body to world: `R = Rz(yaw) · Ry(pitch) · Rx(roll)` (ZYX order), with yaw ≡ 0 in this project.
- **Roll φ** is rotation about body x. Positive roll raises the top edge of a flat, screen-up phone.
- **Pitch θ** is rotation about body y. Positive pitch lowers the right edge of a flat, screen-up phone.
- For a stationary sensor, the specific force in the body frame is:

  `f = G · ( −sin θ,  sin φ · cos θ,  cos φ · cos θ )`

- Accelerometer tilt formulas, binding for §5.1:

  `roll  = atan2(f_y, f_z)`
  `pitch = atan2(−f_x, sqrt(f_y² + f_z²))`

  These are invariant to positive scaling of `f`.
- Pitch is valid in the range |θ| ≤ 60° (π/3 rad). Behavior outside this range is unspecified, except where §4 requires an error.
- Do **not** use Android's built-in orientation API conventions. Those use different signs.

### 2.5 Array conventions
- Time series are NumPy `float64` arrays. `N` is the number of samples.
- Scalar series have shape `(N,)`. 3-axis series have shape `(N, 3)` with columns `[x, y, z]`.
- Timestamps `t` have shape `(N,)` and must be strictly increasing. They need not be uniform and need not start at 0.
- Functions must **not** modify their input arrays. They return new arrays.

---

## 3. File layout

```
project_root/
  imu_sim.py       # simulation only (may import numpy)
  imu_filters.py   # estimators only (numpy only; MUST NOT import imu_sim, imu_metrics, imu_plots)
  imu_metrics.py   # metrics only (numpy only)
  imu_plots.py     # plotting (numpy, matplotlib; may import imu_metrics)
  tier1.ipynb      # notebook; imports the modules above
  tests/           # owned by TESTER
```

Tests import the modules by name from `project_root`, for example `import imu_filters`. The only runtime dependencies are Python ≥ 3.10, NumPy and Matplotlib.

Test-only dependencies (not imported by any module in this layout):
- `pytest` — test runner for all §8 tests.
- `jupyter` / `nbconvert` — executes `tier1.ipynb` for test G2.
- `ipykernel` — provides the Python kernel that nbconvert uses to run the notebook.

---

## 4. `imu_sim.py`

### 4.1 Constants
- `GRAVITY: float = 9.81`

### 4.2 `SimulatedIMU` (frozen dataclass)
| Field | Type / shape | Meaning |
|---|---|---|
| `t` | `(N,)` float64 | timestamps, s |
| `gyro` | `(N, 3)` float64 | measured angular rate, rad/s |
| `accel` | `(N, 3)` float64 | measured specific force, m/s² |
| `roll_true` | `(N,)` float64 | ground-truth roll, rad (all zeros in Tier 1) |
| `pitch_true` | `(N,)` float64 | ground-truth pitch, rad |
| `gyro_bias` | `(3,)` float64 | the constant bias that was applied, rad/s |
| `fs` | float | sample rate, Hz |

Ground-truth fields carry the suffix `_true`. Filters never receive them.

### 4.3 Trajectories
A **trajectory** is a callable `traj(t: ndarray (N,)) -> tuple[pitch (N,), pitch_rate (N,)]`, in rad and rad/s, where `pitch_rate` is the exact analytic derivative of `pitch`.

- `default_pitch_trajectory(t) -> tuple[ndarray, ndarray]`

  `pitch(t)      = 0.5·sin(2π·0.1·t) + 0.2·sin(2π·0.5·t)`
  `pitch_rate(t) = 0.5·2π·0.1·cos(2π·0.1·t) + 0.2·2π·0.5·cos(2π·0.5·t)`

  Note that `pitch(0) = 0` and max |pitch| ≤ 0.7 rad (about 40°).

- `constant_pitch_trajectory(angle: float) -> Callable`

  Returns a trajectory with `pitch ≡ angle` and `pitch_rate ≡ 0`.

### 4.4 `simulate_pitch_imu`
```
simulate_pitch_imu(
    duration: float = 60.0,
    fs: float = 100.0,
    trajectory: Callable | None = None,      # None -> default_pitch_trajectory
    gyro_bias = (0.01, 0.01, 0.01),          # array-like, shape (3,), rad/s
    gyro_noise_std: float = 0.005,           # rad/s, per sample, per axis
    accel_noise_std: float = 0.05,           # m/s², per sample, per axis
    seed: int | None = None,
) -> SimulatedIMU
```
**Sampling.** `N = int(round(duration * fs))` and `t[k] = k / fs` for `k = 0 … N−1`.

**Model.** With `θ, θ̇ = trajectory(t)`, roll ≡ 0 and the IMU at the center of rotation, so there is no centripetal term:
- `gyro[:, 0] = b_x + n_gx`
- `gyro[:, 1] = θ̇ + b_y + n_gy`
- `gyro[:, 2] = b_z + n_gz`
- `accel = GRAVITY · (−sin θ, 0, cos θ) + n_a`

All noise terms are independent, zero-mean Gaussian and white. The gyro noise has std `gyro_noise_std` and the accelerometer noise has std `accel_noise_std`. Both are drawn from a single `numpy.random.default_rng(seed)`.

**Determinism.** Two calls with the same integer `seed` and arguments must return bit-identical arrays. Different seeds must produce different noise.

**Errors.** The function raises `ValueError` in each of these cases:
- `duration ≤ 0`
- `fs ≤ 0`
- `N < 2`
- a negative noise std
- `gyro_bias` not of shape `(3,)`
- any |pitch| > π/3 + 1e-9 returned by the trajectory

---

## 5. `imu_filters.py`

None of these functions accept ground-truth inputs. None of them wrap angles.

### 5.1 `accel_tilt(accel) -> tuple[ndarray, ndarray]`
- **Input:** `accel` of shape `(N, 3)`.
- **Returns:** `(roll, pitch)`, each of shape `(N,)`, in rad, using the formulas in §2.4.
- **Errors:** `ValueError` if `accel` is not 2-D with 3 columns.
- The result for a zero vector is unspecified.

### 5.2 `gyro_integrate(t, gyro_rate, initial_angle=0.0) -> ndarray`
- **Inputs:** `t` of shape `(N,)`; `gyro_rate` of shape `(N,)`, which is one gyro axis in rad/s.
- **Returns:** `angle` of shape `(N,)`, computed as:
  - `angle[0] = initial_angle`
  - `angle[k] = angle[k−1] + gyro_rate[k] · (t[k] − t[k−1])` for k ≥ 1

  This is a backward rectangle rule using the *current* sample.
- **Errors:** `ValueError` in these cases:
  - mismatched lengths
  - non-1-D inputs
  - `N < 1`
  - `t` not strictly increasing

### 5.3 `complementary_filter(t, gyro_rate, accel_angle, tau=0.2, initial_angle=None) -> ndarray`
- **Inputs:**
  - `t` of shape `(N,)`
  - `gyro_rate` of shape `(N,)`, in rad/s
  - `accel_angle` of shape `(N,)`, in rad (for example the pitch output of `accel_tilt`)
  - `tau` in s, which must be > 0
- **Returns:** `angle` of shape `(N,)`, computed as:
  - `angle[0] = initial_angle` if given, else `accel_angle[0]`
  - For k ≥ 1:
    - `dt = t[k] − t[k−1]`
    - `α = tau / (tau + dt)`
    - `angle[k] = α · (angle[k−1] + gyro_rate[k] · dt) + (1 − α) · accel_angle[k]`
- **Errors:** `ValueError` in these cases:
  - `tau ≤ 0`
  - mismatched lengths
  - non-1-D inputs
  - `N < 1`
  - `t` not strictly increasing

**Tier 1 usage.** Pitch uses `gyro_rate = gyro[:, 1]` and `accel_angle = accel_tilt(accel)[1]`. Because roll ≡ 0, the body y-rate equals the pitch rate.

---

## 6. `imu_metrics.py`

All inputs are 1-D arrays of equal length, in rad. `ValueError` is raised for:
- a shape mismatch
- empty input
- any NaN in the inputs

Error is defined as `e = estimate − truth`.

| Function | Returns |
|---|---|
| `rmse(estimate, truth) -> float` | `sqrt(mean(e²))`, rad |
| `max_abs_error(estimate, truth) -> float` | `max(|e|)`, rad |
| `drift_rate(t, estimate, truth) -> float` | slope of the ordinary least-squares line fit of `e` against `t`, rad/s. Requires N ≥ 2. |

---

## 7. `imu_plots.py` and notebook

### 7.1 `plot_comparison(t, truth, estimates, title="") -> matplotlib.figure.Figure`
- **Inputs:**
  - `truth` of shape `(N,)`, in rad
  - `estimates`: a `dict[str, ndarray (N,)]`, in rad. Its insertion order defines the line order.
- **Returns:** a Figure with exactly **2 axes**.
  - **Axes 0** shows the angles in **degrees**. It has `1 + len(estimates)` lines: first the truth line, labelled `"truth"`, then one line per estimate, labelled with its dict key.
  - **Axes 1** shows the errors in **degrees**. It has `len(estimates)` lines, labelled with the dict keys, with y-data `rad2deg(estimate − truth)`.
  - The x-data of every line is `t`. Both axes have a legend and labelled axes.
- The function must not call `plt.show()`.
- **Errors:** `ValueError` for an empty `estimates` dict or any length mismatch.

### 7.2 `tier1.ipynb`
The notebook must:
- Execute top to bottom without error, using `jupyter nbconvert --to notebook --execute tier1.ipynb`, in under 120 s.
- **Standard run.** Simulate scenario S1 with seed 0. Run all three estimators (gyro integration with `initial_angle=0`, and tau = 0.2 for the complementary filter). Print a table of RMSE and max abs error in degrees per method, and show `plot_comparison`.
- **Long run.** Simulate scenario S2 with seed 0. Print `drift_rate` per method in °/s, and show `plot_comparison`.
- Include a short markdown discussion of the results.
- Pass no `*_true` field to any filter function.

---

## 8. Scenarios and success criteria

**Scenarios:**
- **S1:** `simulate_pitch_imu()` with all defaults (60 s, 100 Hz, default trajectory) and seeds 0–9.
- **S2:** `simulate_pitch_imu(duration=600.0)`, otherwise defaults, with seeds 0–4.
- **Estimators** in S1/S2 are configured as:
  - gyro: `gyro_integrate(t, gyro[:,1], 0.0)`
  - accel: `accel_tilt(accel)[1]`
  - CF: `complementary_filter(t, gyro[:,1], accel_pitch, tau=0.2)`

All metrics are computed on pitch against `pitch_true`. Unless stated otherwise, each criterion must hold for **every** listed seed.

The approximate expected values in brackets are planner estimates for reviewer context. They are not test values.

### 8.1 Statistical performance
| ID | Scenario | Criterion | (expected) |
|---|---|---|---|
| P1 | S1 | Accel-only RMSE is in `[0.8, 1.2] × (0.05 / 9.81)` rad, i.e. 0.234°–0.350° | (≈0.29°) |
| P2 | S1 | Gyro-only: \|final error − b_y · t[−1]\| ≤ 0.03 rad | (final error ≈ 0.60 rad) |
| P3 | S1 | Gyro-only RMSE > 10° | (≈20°) |
| P4 | S1 | CF RMSE ≤ 0.2° | (≈0.14°) |
| P5 | S1 | CF RMSE ≤ 0.7 × accel-only RMSE (same seed) | (ratio ≈0.5) |
| P6 | S2 | Gyro `drift_rate` is within ±5 % of b_y = 0.01 rad/s | |
| P7 | S2 | \|CF `drift_rate`\| ≤ 1e-5 rad/s and \|accel `drift_rate`\| ≤ 1e-5 rad/s | |
| P8 | S2 | CF RMSE over samples with t ≥ 540 s ≤ 0.2° | |

### 8.2 Deterministic correctness (noise-free: both noise stds = 0)
| ID | Criterion (tolerance `atol`) |
|---|---|
| D1 | With biases (0.01, −0.02, 0.03): `gyro[:,0] == 0.01`, `gyro[:,1] == pitch_rate + (−0.02)` and `gyro[:,2] == 0.03`. `accel == GRAVITY·(−sin θ, 0, cos θ)`. Tolerance 1e-12. |
| D2 | `accel_tilt` on D1 data returns pitch == `pitch_true` and roll == 0 (1e-9). |
| D3 | Reference vectors for `accel_tilt`, as (roll, pitch) in degrees, within 1e-9 rad, where s = sin and c = cos: `(0,0,G)→(0,0)`; `(0,G,0)→(90,0)`; `(−G·s30°, 0, G·c30°)→(0,30)`; `(0, G·s20°, G·c20°)→(20,0)`; `(−G·s30°, G·s20°·c30°, G·c20°·c30°)→(20,30)`. Results are unchanged when the input is scaled by 0.5 or 3. |
| D4 | `gyro_integrate` with a constant rate r on non-uniform `t` returns `initial_angle + r·(t − t[0])` (1e-12). |
| D5 | `gyro_integrate` and `complementary_filter` match the §5.2 / §5.3 recurrences on random inputs with non-uniform `t` (1e-12). |
| D6 | CF steady state: `constant_pitch_trajectory(0.3)`, b_y = 0.01, tau = 0.2, 60 s. The final CF error equals `b_y · tau = 0.002` rad (1e-6). |
| D7 | CF limits over a 10 s S1 run with seed 0: with `tau=1e9` and `initial_angle=0`, the output equals `gyro_integrate(…, 0.0)` (1e-6 rad). With `tau=1e-9`, the output equals `accel_angle` (1e-6 rad). |
| D8 | `N = 1`: `gyro_integrate` returns `[initial_angle]` and CF returns `[accel_angle[0]]`. |

### 8.3 Simulator statistics (S1, seed 0, both biases known)
| ID | Criterion |
|---|---|
| N1 | For each gyro axis, the residual `gyro − true_rate − bias` has std within ±5 % of 0.005 and \|mean\| ≤ 4·0.005/√N. |
| N2 | For each accel axis, the residual `accel − GRAVITY·(−sin θ, 0, cos θ)` has std within ±5 % of 0.05 and \|mean\| ≤ 4·0.05/√N. |
| N3 | The pairwise Pearson correlation between any two of the six residual columns is \|r\| < 0.1. |
| N4 | `t` has shape (6000,), `t[0] == 0` and `diff(t) == 0.01` (1e-12). All array shapes and dtypes match §4.2. `roll_true` is all zeros. |
| N5 | The same seed gives identical arrays (`array_equal`). Seeds 0 and 1 give different `gyro` arrays. |

### 8.4 Interface, separation and errors
| ID | Criterion |
|---|---|
| I1 | In a fresh interpreter (subprocess), `import imu_filters` leaves `imu_sim`, `imu_metrics` and `imu_plots` absent from `sys.modules`. The same holds for `import imu_metrics` with respect to `imu_sim`. |
| I2 | `inspect.signature` parameter names and defaults exactly match §4.4, §5 and §6. |
| I3 | Every `ValueError` case listed in §4.4, §5, §6 and §7.1 raises `ValueError`. |
| I4 | No function modifies its input arrays (compare copies before and after the call). |
| I5 | The return shapes and `float64` dtype match the spec. `rmse`, `max_abs_error` and `drift_rate` return Python or NumPy floats. |
| M1 | `rmse([1,2,3],[1,2,3]) == 0`; `rmse([3,4],[0,0]) == sqrt(12.5)`; `max_abs_error([1,−5],[0,0]) == 5`; `drift_rate` of an error exactly equal to `0.7 + 0.03·t` is 0.03 (1e-12). |
| G1 | `plot_comparison` with 3 estimates returns a `Figure` with 2 axes: 4 lines on axes 0 and 3 lines on axes 1. The labels are as specified. The y-data of the truth line equals `rad2deg(truth)` and the y-data of the error lines equals `rad2deg(est − truth)` (1e-9). |
| G2 | `tier1.ipynb` executes via nbconvert without error in under 120 s. |

---

## 9. Deliverables and definition of done
**EXECUTOR delivers:**
- the four modules and `tier1.ipynb`
- a short `TIER1_RESULTS.md` with the measured S1 and S2 values (seed 0) for P1–P8

**TESTER delivers:**
- pytest tests in `tests/`, covering every ID in §8, each test named after its ID (for example `test_P4_cf_rmse`)

**Tier 1 is done when** all §8 tests pass and the owner has reviewed the notebook plots.
