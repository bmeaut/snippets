# Phase 2: Closed-Loop PID Control Simulation

## Objective
Implement a PID controller as a transfer function, close the feedback loop with the thermal plant, simulate the step response to a 60 °C setpoint, plot the temperature tracking, and compute basic performance metrics.

---

## 1. PID Controller Module (`controller.py`)

Create a new file `controller.py` in the project root with a class `PIDController`.

### Class Interface

- **`__init__(self, Kp=1.0, Ki=0.0, Kd=0.0)`** – stores the three gains.
- **`transfer_function(self)`** – returns a `control.TransferFunction` object representing the ideal PID controller in the Laplace domain:

    Gc(s) = Kp + Ki/s + Kd*s

Use the `control.TransferFunction` constructor directly. For example:

    control.TransferFunction([Kd, Kp, Ki], [1, 0])

gives numerator `Kd s^2 + Kp s + Ki` and denominator `s`.

- No derivative filtering and no anti‑windup at this stage — pure ideal PID.

---

## 2. Performance Metrics (`utils.py`)

Replace the stubs in the existing `utils.py` with fully implemented functions. All functions must accept NumPy arrays for time `t` and output `y`, and return a single float.

### Required Functions

1. **`overshoot(y, setpoint)`**  
   - Returns `(max(y) - setpoint) / setpoint * 100` (percentage).  
   - If the maximum is less than or equal to the setpoint, return 0.0.

2. **`rise_time(t, y, setpoint, low=0.1, high=0.9)`**  
   - Assumes the system starts at an initial temperature below the setpoint and rises.  
   - Finds the first time `y` crosses `setpoint * low` and the first time it crosses `setpoint * high`, then returns `t_high - t_low`.  
   - If either bound is never reached, return `float('inf')`.

3. **`settling_time(t, y, setpoint, band=0.02)`**  
   - Returns the smallest time `t_s` such that for all `t >= t_s`,  
     `|y - setpoint| <= band * setpoint`.  
   - If the signal never settles within the simulation time, return `float('inf')`.  
   - Search backwards from the end of the array for efficiency.

All functions should handle the case where `y` is a 1D array. Use NumPy indexing and boolean masking.

---

## 3. Closed-Loop Simulation Script (`closed_loop.py`)

Create a new script `closed_loop.py` that ties everything together.

### 3.1 Imports
Import the following:
- `numpy as np`
- `matplotlib.pyplot as plt`
- `control` (python‑control)
- `plant` (ThermalPlant)
- `controller` (PIDController)
- `utils` (all three metric functions)

### 3.2 Parameters
Define:
- `SETPOINT = 60.0` (°C)
- `T_AMBIENT = 20.0` (°C)
- Placeholder PID gains:  
  `Kp = 1.8`  
  `Ki = 0.008`  
  `Kd = 30.0`
- Simulation end time: 800 s.

### 3.3 Build the Closed‑Loop System
1. Instantiate `ThermalPlant` with default parameters → `Gp = plant.transfer_function()`.
2. Instantiate `PIDController` with the placeholder gains → `Gc = pid.transfer_function()`.
3. Form the open‑loop series: `G_ol = Gc * Gp` (using `control.series()` or `*`).
4. Build the closed‑loop transfer function from reference (setpoint deviation) to output deviation:  
   `G_cl = control.feedback(G_ol, 1, sign=-1)`  
   (unity negative feedback).
5. The step magnitude from ambient to setpoint is `SETPOINT - T_AMBIENT = 40.0`.

### 3.4 Simulate Step Response
- Use `control.step_response(G_cl, T=800)` which returns `(t, y_dev)` — `y_dev` is the **temperature deviation** for a unit step input.
- Multiply `y_dev` by 40 to obtain the deviation for a 40 °C command, then add ambient:  
  `T_abs = T_AMBIENT + 40.0 * y_dev`
- Ensure `t` has enough points; the default from `step_response` is usually fine, but you can specify a `T_num` parameter for smoothness.

### 3.5 Plot
- Create a figure (size 10×6 recommended).
- Plot `t` vs `T_abs` with a solid line (label "Temperature").
- Add a dashed horizontal line at `SETPOINT` (label "Setpoint 60 °C", color grey or red).
- Label axes: `Time (s)` and `Temperature (°C)`.
- Title: `Closed-Loop PID Response to 60°C Setpoint`.
- Enable grid, use `tight_layout()`.
- Save the plot to `plots/closed_loop_pid_response.png` (create the directory if needed).

### 3.6 Compute and Print Metrics
- `overshoot_val = utils.overshoot(T_abs, SETPOINT)`
- `rise_t = utils.rise_time(t, T_abs, SETPOINT)`
- `settle_t = utils.settling_time(t, T_abs, SETPOINT)`
- Print one metric per line, formatted to two decimal places:
  - `Overshoot: X.XX %`
  - `Rise time: X.XX s`
  - `Settling time: X.XX s`

### 3.7 Run
The script must be executable with `python closed_loop.py`.

---

## 4. Acceptance Criteria

- `python closed_loop.py` runs without errors.
- The plot shows the temperature rising from 20 °C, approaching 60 °C, possibly overshooting, then settling near the setpoint.
- The reference line at 60 °C is visible.
- The three metrics are printed and are physically plausible (rise time between 50–400 s, overshoot 0–50 %, settling time ≤800 s).
- The plot is saved to `plots/closed_loop_pid_response.png`.