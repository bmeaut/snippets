# Evaluation: IMU Sensor Fusion (Tiers 1–3)

**Bottom line:** the code implements the three specifications faithfully, and all 927 tests pass on the reference machine (Windows, Python 3.9.13). Nothing blocks acceptance. The weaknesses are in the notebook discussions, where several statements are not backed by the printed numbers, and in the real-data robustness, which the tests barely exercise. One finding contradicts both the Tier 3 notebook and spec §0.5: the gated KF's largest error comes from the falling flank of each acceleration pulse, not the rising flank.

**How this was evaluated:** I read every file in the package. I also extracted `imu_sim`, `imu_filters` and `imu_metrics` from `source_code.md` and ran them in my own environment (Linux, NumPy 2.5) to check five claims. The full test suite and the notebooks could not be run here, because the data zips and `.ipynb` files are not in the package.

---

## 1. Scores

| # | Category | Score | Evidence |
|---|---|---|---|
| 1 | Spec compliance | **4** | Every module, function, signature, dataclass, criterion ID and deliverable in T1-§9, T2-§10 and T3-§12 is present. Errata E1–E3 are applied: E1 needed no code change, the E2 3.9 syntax is checked statically, and the E3 KI2 test is updated. **Gaps:** the T3-§10 discussion contains no real-data observations; the RD5 text ("equals Δ·tau") is wrong and was never corrected; the KT1/KT2 rows in `TIER2_RESULTS.md` give seed 0 only, although the criterion averages seeds 0–2; the initial interactive output comes from a separate static cell, not from the widget cell itself. |
| 2 | Mathematical correctness | **4** | Checked by hand: body rates `(φ̇, cφθ̇, −sφθ̇)` and specific force `G(−sθ, sφcθ, cφcθ) + Rᵀa_w` follow from `R = Ry·Rx`; the inverse map `E(φ,θ;w)`; the pitch sensitivity `F[0,1] = −cos φm·dt`; the roll noise scaling `1/cos²θ` for both Q and R; `Q = diag(σg²dt², σb²dt)` and `R = (σa/G)²`; the inclusive-hold gate. The scalar loops match the matrix references within 1e-10 (KD2, RD1). **Deductions:** design-level statements are wrong (the falling flank in §0.5, the sign in RD5). The roll channel ignores its coupling to b_y (through −tanθ·sinφ) and to the fixed b_z estimate. The trapezoidal `Q[0,0]` is only an approximation, though the spec accepts it. |
| 3 | Estimation performance | **4** | Every criterion passes for every listed seed. Seed-0 margins are mostly 1.6–3×: KP1 1.85, KP2 2.54, RP1 2.17/2.96, RX1 2.48, RX2 2.26, RX3 2.31, RX5 2.36/2.88. **Thin margins:** KC1 0.933 against ≥ 0.90 (1.04×), KP8 72.79 s against ≤ 90 s (1.24×), KT1 at the limit of its own 1.10 ratio. Per-seed values are never reported, so the worst-seed margin is unknown. |
| 4 | Robustness | **3** | Gating cuts the worst disturbance error to 3.03°, compared with 12.45° for the ungated KF and 17.46° for the CF. Recovery is 1.21 s (KF-gated) against 2.42 s (KF). The quiet-period RMSE is unchanged at 0.034°/0.028°. **But:** the remaining error comes from the ungated falling flank; the ‖f‖ gate cannot see horizontal accelerations below about 2 m/s²; on recording A the gate is active for most of the 11–51 s motion phase (A pitch figure); recording B's benefit is shown only in a figure; RR4/RR5 pass by 15–1000×, so they test little; RR3 on B gives r = −0.04 and is not investigated. |
| 5 | Test quality | **4** | Every criterion ID has a named test. Expected values come from `tier1/2/3_reference.py`, which were written from the spec and never import the modules under test. Several tests would actually fail on a wrong design: KD4 (integration rule), RD3 (midpoint step), RD4 (exact inclusive hold boundary using dyadic time values), and an added RD5 sign test. Many negative controls are included. **Weaknesses:** RD2 and D7 compare the code against itself; the timing tests (KI6, RI6, G2, KG3, RG3) depend on the machine; the notebook "no ground truth" checks are heuristic AST scans; RD5 asserts only the magnitude, against the spec text; real-data criteria are lenient; no test checks that the notebook output matches the results files; the 14 pytest warnings are not explained. |
| 6 | Platform and reproducibility | **4** | Passes on Python 3.9.13 (927 tests in 43 s, against a 6-minute limit). Every module and test file is parsed with `feature_version=(3, 9)`, and the tests forbid 3.10+ constructs. Everything is seeded, and the seed-0 values agree across the executor sandbox (3.9.25 and 3.13) and the owner's run. **Gaps:** no requirements or lock file; pandas is declared as a runtime dependency but unused; the RI6, KI6 and notebook run times are never reported, although the RI6 limit had to be raised to 8 s (my run took 0.10 s for N = 15 000, about 0.4 s extrapolated to N = 60 000, but not on the reference machine); the Tier 2 figures predate the final code; the pytest record is a curated table, not a raw log. |
| 7 | Code and documentation quality | **3** | The code has clean module separation, with the import rules enforced by subprocess and static tests. The scalar Kalman loops are readable, and validation is thorough. **But:** the `imu_filters` and `imu_sim` docstrings are stale (Tier 1/2 only, "pitch-only"); the annotation styles are inconsistent (`X \| None` and `Optional`); validation code is duplicated; about seven statements in the notebooks and results files are inaccurate or not supported by the numbers (Section 6). |
| | **Average** | **3.71 / 5** | |

---

## 2. Measured results against the criteria (seed 0)

| Criterion | Measured | Threshold | Margin |
|---|---|---|---|
| P4 CF RMSE (S1) | 0.140° | ≤ 0.2° | 1.43 |
| P8 CF RMSE, t ≥ 540 s | 0.146° | ≤ 0.2° | 1.37 |
| KP1 KF RMSE, t ≥ 20 s | 0.0325° | ≤ 0.06° | 1.85 |
| KP2 KF/CF ratio | 0.236 | ≤ 0.6 | 2.54 |
| KP8 bias convergence time | 72.79 s | ≤ 90 s | **1.24** |
| KC1 bias 2σ coverage | 0.933 | ≥ 0.90 | **1.04** |
| RP1 KF RMSE roll/pitch | 0.0368° / 0.0270° | ≤ 0.08° | 2.17 / 2.96 |
| RP3 max bias error | 5.0e-4 rad/s | ≤ 1e-3 | 1.99 |
| RX1 KF-gated max disturbance error | 3.03° | ≤ 7.5° | 2.48 |
| RX4 worst recovery KF / gated / CF | 2.42 / 1.21 / 0.51 s | 10 / 10 / 3 s | 4.1 / 8.3 / 5.9 |
| RR3 Pearson r (A) | 0.9987 / 0.9991 | ≥ 0.9 | 1.11 |
| RR5 KF-gated vs accel tilt, end window | 0.002–0.011° | ≤ 1° | 91–500 |

---

## 3. Issues

Nothing found is **Blocking**: every criterion passes, and the definition of done (tests pass, plots reviewed by the owner) is met. Issues 1–3 should still be fixed before anyone relies on the documents.

| # | Rating | Location | Issue |
|---|---|---|---|
| 1 | Minor (fix) | `tier3.ipynb` Discussion; T3-§0.5 | **The gated KF's worst error is on the falling flank.** In my run the gate covers 30.38–31.84 s and reopens while the pulse lasts until 32.0 s. The largest errors occur at t = 31.9 s (2.46°, pitch) and t = 61.9 s (3.03°, roll). The spec's claim that the 0.2 s hold covers the falling flank is false under its own pulse model, and the notebook blames the rising flank. |
| 2 | Minor (fix) | `tier3.ipynb` Discussion, real-data bullet | It gives instructions ("Check the start-vs-end tables…", "compare the KF and KF-gated curves") instead of observations. The T3-§10 requirement to cover "the real-data observations" is not met. |
| 3 | Minor (fix) | T3 spec, RD5 | The spec says the final roll error "equals Δ·tau". The correct value is −Δ·tau, because the subtracted bias is too large by Δ. The test checks the magnitude, plus an extra sign test. An erratum is still needed. |
| 4 | Minor | T2-§0.4 vs §9 | The rule that every threshold sits ≥ 1.5× from its expected value is broken by KP8 (≈1.23×) and KC1 (≈1.06×). The executor flagged this in Note 13, but it was never resolved. |
| 5 | Minor | `TIER2_RESULTS.md`, KT1/KT2 rows | Seed-0 numbers are reported as KT1/KT2, but the criterion averages seeds 0–2. |
| 6 | Minor | `tier2.ipynb`, `fig_tier2_S1_error_comparison.png` | Not re-rendered after E3. The figure still shows the "Pitch error (°)" label and accel as a normal foreground line, unlike the final code. |
| 7 | Minor | `tier3.ipynb`, `render()` | The gated filter is labelled "KF". The default output appears twice in a live session (static cell and widget). The widget cell itself produces only `Output()` under nbconvert. |
| 8 | Minor | `plot_estimates` on real data | The legend label "disturbance" marks gated samples. On recording A those cover most of the normal tilting. |
| 9 | Minor | `imu_filters.py`, `imu_sim.py` | Module docstrings still describe Tier 1/2 and "pitch-only" simulation. The annotation styles are mixed. |
| 10 | Minor | Package | No environment file. The 14 warnings are unexplained. RI6, KI6 and notebook run times are unreported. `imu_io` is documented as using pandas but does not import it. |
| 11 | Minor | `TIER3_RESULTS.md`, StationaryEstimate table | The pooled noise is rebuilt from rounded values ("≈ 7.4e-4", "≈ 6.0e-4"), although the notebook prints 0.000741 and 0.000595. The signed biases are left out. |
| 12 | Minor | `imu_filters._check_initial_cov` | Small negative eigenvalues (within 1e-12, relative) are accepted, whereas T2-§5.3 says any negative eigenvalue raises. This is documented and harmless, but it departs from the spec text. |
| 13 | Minor | `tier2.ipynb` | The planner's steady-state Riccati values (§5.4) are not reproduced or compared with the measured values. |

---

## 4. Three biggest strengths

1. **An independent, rigorous test suite.** It has 927 tests, one named test per criterion ID. The reference implementations are transcribed line by line from the specs and never import the code under test. Several tests would actually fail on a wrong design: KD4 detects the integration rule, RD3 the midpoint Euler step, and RD4 the inclusive gate boundary using exact dyadic time values.
2. **A faithful and efficient implementation.** The pure-Python scalar loops reproduce the specified matrix recurrences to within 1e-10, and the module boundaries (`imu_filters` uses NumPy only) are enforced both in subprocesses and statically.
3. **Honest reporting.** The results files flag their own weak points: the RD5 sign, the §0.4 margin violations, the near-zero correlation on recording B, the gap between real and simulated noise levels, and the fact that the executor never saw the real recordings.

## 5. Three biggest risks

1. **Real-data robustness is barely tested.** RR4/RR5 pass by 15–1000×. RR3 runs only on recording A; recording B gives r = −0.04, and the cause is a guess. The 0.2 m/s² gate is about 30× the real accelerometer noise (0.006–0.010 m/s²), so it stays on through most of A's ordinary motion, and the gated filter then runs mainly on the gyro. None of this is quantified. The benefit on recording B is visible only in a figure.
2. **The gate has structural blind spots.** It only sees changes in ‖f‖, so it misses horizontal accelerations below about 2 m/s². The 0.2 s hold leaves about 0.15 s of every falling flank ungated, and that is where the remaining error occurs. The RX thresholds rest on transient estimates (T3-§0.6), and the simulated disturbances cover a narrow case: 2 s half-sine pulses at 3 m/s². Recording A also reaches about −56° pitch, close to the 60° validity limit, where the roll channel's 1/cos²θ scaling and the neglected b_y/b_z coupling grow quickly.
3. **Thin margins, reported for one seed only.** KC1 passes by 1.04× and KP8 by 1.24×, but the results report only seed 0 even though the tests check every seed. Timing margins are unreported, and the timing tests depend on the machine. The Tier 2 figures do not reflect the final code.

---

## 6. Claims the numbers do not support

| # | Source | Claim | What the numbers show |
|---|---|---|---|
| 1 | `tier3.ipynb` Discussion | "The CF is a few times worse than the KF" (S6) | The printed values give 0.0532/0.0368 = **1.45×** (roll) and 0.0453/0.0270 = **1.68×** (pitch). |
| 2 | `tier3.ipynb` Discussion | Gating leaves error because "during the first part of each pulse the accelerometer still reaches the filter ungated" | The KF-gated peaks are at **t = 31.9 s and 61.9 s**, after the gate reopens on the falling flank (my run). The rising flank is not where the maximum occurs. |
| 3 | `tier3.ipynb` Discussion | "The 15 Hz vibration averages out in the accelerometer path" | The accelerometer-tilt error reaches **14.1°** during 90–95 s (my run, and visible in `fig_tier3_S7_roll_error`). Only the filters attenuate it. |
| 4 | `tier2.ipynb` Discussion | The KF beats the CF because it estimates the bias, "so that offset disappears" | Only part of the gap. The CF's backward-rectangle integration rule alone contributes **0.068° RMS**. With trapezoidal integration the CF would score **0.122°** instead of 0.140° (my run). The 0.5 Hz ripple is visible in `fig_tier2_S1`. |
| 5 | `tier2.ipynb` Discussion | The tuning sweep "supports the Q/R derivation, including the approximation made for the trapezoidal increments" | The sweep scales Q[0,0] and Q[1,1] together in 3× steps, and the whole sQ = sR diagonal ties at 0.0280°. It cannot isolate a factor-2 error in Q[0,0]. |
| 6 | `TIER1_RESULTS.md` Note 4 | The 0.0023 rad P2 discrepancy comes from "the first-sample convention" | The bias term is exactly b·t[−1] (5999 steps × 0.01 s). The residual **0.002342** equals the summed gyro noise **0.002343** (my run), so it is random-walk noise. |
| 7 | `tier2.ipynb` Discussion | After the step the CF settles to an offset of "0.23 deg" | Not printed anywhere. It is analytically plausible (0.02 × 0.2 rad) but not shown. |
| 8 | T3 spec §0.5 (repeated implicitly in the notebook) | "The hold keeps the gate closed … across the falling flank of each pulse" | The flank stays below the detection threshold for about 0.46 s, but the hold covers only 0.2 s. The gate reopens while the pulse is still about 1.2 m/s². |
| 9 | `TIER3_RESULTS.md` Note 14 | Recording B's r ≈ −0.04 reflects small tilt changes compared with noise | The executor marks this as unverified, and nothing in the package checks it. The B zoom figure shows tilts of only about ±0.5° outside the disturbances, which is consistent but still not quantified. |
