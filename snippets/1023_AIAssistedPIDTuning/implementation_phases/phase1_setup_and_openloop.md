# Phase 1: Project Setup & Open-Loop Step Response Simulation

## Objective
Set up the project environment, implement the thermal plant model as a transfer function, and simulate its open-loop step response. The result is a plot showing how the plant’s temperature naturally evolves when the heater is turned on to full power, with no controller.

---

## 1. Project Structure
Create the following directory layout:

    thermal_pid_tuner/
    ├── plant.py            # Thermal plant model
    ├── utils.py            # Performance metric functions (for later phases)
    ├── main.py             # Entry point for open-loop simulation
    ├── requirements.txt    # Python dependencies
    └── plots/              # Directory for saved figures

---

## 2. Dependencies (`requirements.txt`)

    numpy>=1.24
    scipy>=1.10
    matplotlib>=3.7
    control>=0.9

All simulations and control objects will use the `control` library (also known as `python-control`).

---

## 3. Thermal Plant Model (`plant.py`)

### Plant Parameters

| Parameter | Symbol | Value  | Unit             |
|-----------|--------|--------|------------------|
| Steady‑state gain | K   | 1.5    | °C / % heater    |
| Time constant     | τ   | 200.0  | seconds          |
| Dead time         | θ   | 20.0   | seconds          |
| Ambient temperature | T_amb | 20.0 | °C              |

The transfer function from heater power deviation (Δu in %) to temperature deviation (ΔT in °C) is:

               K · e^(-θs)
    G(s) = ───────────────
                τ s + 1

The absolute temperature is:  
`T(t) = T_amb + output of G(s) for a given heater input u(t).`

Heater input is bounded between 0 % and 100 %.

### Implementation

Create a class `ThermalPlant` with:
- **`__init__(self, K=1.5, tau=200.0, theta=20.0, T_amb=20.0)`** – stores parameters.
- **`transfer_function(self)`** – returns a `control.TransferFunction` object using a **2nd‑order Padé approximation** for the dead time.
- **`step_response(self, u_step=100.0, t_end=800.0, dt=0.5)`** – simulates the step response (heater jumps from 0 to `u_step` at t=0) and returns `(t, T)` where `T` is the absolute temperature.

**Important details:**

- The `control` library does not directly support pure dead time. Use `control.pade(θ, n=2)` to obtain numerator/denominator polynomials, then multiply the rational part `K / (τ s + 1)` by the Padé approximation. The `control.series()` function can help.
- For simulation, use `control.step_response()` or `control.forced_response()` with a step input signal.
- Ensure the initial temperature is `T_amb` (output starts at 0 deviation, then add `T_amb`).
- The time vector should span 0 to `t_end` with step `dt`; ensure the output array covers the full simulation.

---

## 4. Main Script (`main.py`)

The script should:
1. Import `ThermalPlant` from `plant.py`.
2. Instantiate the plant with default parameters.
3. Call `step_response(u_step=100.0, t_end=800.0)`.
4. Create a publication‑quality plot:
   - X‑axis: Time (s)
   - Y‑axis: Temperature (°C)
   - Title: **Open‑Loop Step Response (Heater 0→100%)**
   - Grid on, tight layout.
   - Include a dashed horizontal line at the steady‑state temperature (ambient + K·100) as a visual reference.
5. Save the figure as `plots/open_loop_response.png` (the `plots` directory must exist; create it if necessary).
6. Print a summary line: `"Steady-state temperature: X °C"`

---

## 5. Acceptance Criteria

- Running `python main.py` produces no errors.
- The plot shows a smooth, delayed S‑shaped rise from 20 °C to the steady‑state value.
- The delay (~20 s before any noticeable change) and the time constant (~200 s for 63% of the rise) are visually coherent.
- The steady‑state temperature equals 20 + 1.5×100 = 170 °C; the dashed line matches this value.

---

## 6. Notes for the Coding Assistant

- Use `control.pade(theta, 2)` → returns `(num_pade, den_pade)` as 1D arrays of polynomial coefficients (descending powers). Then create `control.TransferFunction` objects for the Padé part and the first‑order lag, and multiply them.
- Ensure all vectors (time, input, output) are plain NumPy arrays or lists that `matplotlib` can handle directly.
- Avoid complex numbers leaking into the temperature output – the Padé approximation yields real coefficients, so output should remain real.