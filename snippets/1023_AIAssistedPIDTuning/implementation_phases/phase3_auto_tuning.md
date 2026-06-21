# Phase 3: Automatic PID Tuning (Ziegler–Nichols Ultimate Gain Method)

## Objective
Implement the Ziegler–Nichols closed-loop tuning algorithm by extracting the ultimate gain and ultimate period from the plant’s frequency response, then compute PID gains and simulate the resulting closed-loop performance.

---

## 1. New Module: `tuner.py`

Create `tuner.py` in the project root. It must contain one public function:

    def ziegler_nichols_tune(plant):
        ...

### 1.1 Algorithm Steps

- Obtain the plant’s transfer function `Gp = plant.transfer_function()` (a `control.TransferFunction` object).
- Compute the **gain margin** and **phase crossover frequency** using `control.margin(Gp)`.
  - `gm, pm, w_p, w_g = control.margin(Gp)`
  - `gm` is the gain margin in linear scale (not dB). `w_p` is the frequency where the phase is –180° (rad/s).
- If `gm` is infinite or NaN (meaning the system cannot be made unstable by proportional gain alone), fall back to a conservative default:
  - `Ku = 5.0`, `Tu = 200.0`, and print a warning: "Gain margin infinite; using default Ku=5, Tu=200 for tuning."
- Otherwise, set:
  - Ultimate gain: `Ku = gm`
  - Ultimate period: `Tu = 2 * np.pi / w_p`
- Compute PID parameters using the classic Ziegler–Nichols rules:
  - `Kp = 0.6 * Ku`
  - `Ki = 2 * Kp / Tu`
  - `Kd = Kp * Tu / 8`
- Return a dictionary with keys `Ku`, `Tu`, `Kp`, `Ki`, `Kd`.

### 1.2 Imports

The function should import:
- `numpy as np`
- `control`

No other dependencies.

### 1.3 Notes

- The `control.margin` function expects a SISO LTI system. Our plant (with Padé delay) qualifies.
- The returned `Kp`, `Ki`, `Kd` are the final controller gains; these can be used directly with the existing `PIDController` class.
- Ensure all values are standard Python floats, not NumPy arrays of size 1.

---

## 2. Demonstration Script: `auto_tune.py`

Create a new script `auto_tune.py` that ties together the plant, the tuner, and the closed-loop simulation to validate the auto-tuned PID gains.

### 2.1 Imports

    import numpy as np
    import matplotlib.pyplot as plt
    import control
    from plant import ThermalPlant
    from controller import PIDController
    from tuner import ziegler_nichols_tune
    from utils import overshoot, rise_time, settling_time

### 2.2 Set Up Plant and Tune

    plant = ThermalPlant()
    tuning = ziegler_nichols_tune(plant)
    Kp, Ki, Kd = tuning['Kp'], tuning['Ki'], tuning['Kd']
    print(f"Ultimate Gain: {tuning['Ku']:.3f}, Ultimate Period: {tuning['Tu']:.2f} s")
    print(f"ZN PID Gains: Kp={Kp:.3f}, Ki={Ki:.5f}, Kd={Kd:.3f}")

### 2.3 Build and Simulate Closed Loop

Use the same structure as `closed_loop.py`:
- `Gp = plant.transfer_function()`
- `pid = PIDController(Kp, Ki, Kd)`, `Gc = pid.transfer_function()`
- `G_ol = Gc * Gp`
- `G_cl = control.feedback(G_ol, 1, sign=-1)`
- `t, y_dev = control.step_response(G_cl, T=800)`
- `T_abs = 20.0 + 40.0 * y_dev` (setpoint = 60 °C, ambient = 20 °C)

### 2.4 Plot

- Figure size (10, 6).
- Plot `t` vs `T_abs`, label "Temperature (ZN Tuned)".
- Dashed grey line at 60 °C, label "Setpoint".
- Grid, axis labels, title "Closed-Loop Response with Ziegler–Nichols Tuning".
- Save to `plots/zn_tuned_response.png`.

### 2.5 Compute and Print Metrics

- `overshoot_val = overshoot(T_abs, 60.0)`
- `rise_t = rise_time(t, T_abs, 60.0)`
- `settle_t = settling_time(t, T_abs, 60.0)`
- Print one per line, formatted to two decimal places:
  - `Overshoot: X.XX %`
  - `Rise time: X.XX s`
  - `Settling time: X.XX s`

### 2.6 Run

The script must be executable with `python auto_tune.py`.

---

## 3. Acceptance Criteria

- `python auto_tune.py` runs without errors.
- The script prints `Ku` and `Tu` (both positive finite numbers) and the three derived PID gains.
- The plot shows a temperature response that rises to 60 °C, possibly with some overshoot, and settles.
- Rise time and settling time are within 0–800 s.
- Overshoot is consistent with ZN tuning (typically 10–40% for such a system).
- The plot is saved to `plots/zn_tuned_response.png`.