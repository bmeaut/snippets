# AI-Assisted PID Tuning for a Simple Thermal Plant

A Python simulation and interactive dashboard for PID tuning of a first-order-plus-dead-time thermal system. Built as a demonstration of AI-assisted coding — the AI wrote the code; the tuning methods themselves are classical control engineering.

---

## Project Structure

    thermal_pid_tuner/
    ├── plant.py                  # Thermal plant model (FOPDT with Padé approximation)
    ├── controller.py             # Ideal PID controller transfer function
    ├── tuner.py                  # Auto-tuning: Ziegler-Nichols & Cohen-Coon
    ├── utils.py                  # Performance metrics (overshoot, rise time, settling time)
    ├── main.py                   # Phase 1: Open-loop step response
    ├── closed_loop.py            # Phase 2: Closed-loop PID with hand-tuned gains
    ├── auto_tune.py              # Phase 3: Ziegler-Nichols auto-tuned response
    ├── compare_tuning.py         # Phase 3.5: ZN vs Cohen-Coon comparison
    ├── app.py                    # Phase 4: Interactive Streamlit dashboard
    ├── requirements.txt          # Python dependencies
    ├── plots/                    # Saved figures from each script
    └── README.md                 # This file

---

## Plant Model

| Parameter          | Symbol | Value   | Unit              |
|--------------------|--------|---------|-------------------|
| Steady-state gain  | K      | 1.5     | °C / % heater     |
| Time constant      | τ      | 200.0   | seconds           |
| Dead time          | θ      | 20.0    | seconds           |
| Ambient temperature| T_amb  | 20.0    | °C                |

The transfer function is **K·e^(−θs) / (τs + 1)**, approximated with a 2nd-order Padé for the delay.

The setpoint for all closed-loop simulations is **60°C**.

---

## Setup

    py -m pip install -r requirements.txt

Dependencies: `numpy`, `scipy`, `matplotlib`, `control`, and `streamlit` (for the dashboard).

---

## How to Run Each Phase

### Phase 1 — Open-Loop Step Response
    py main.py

Heater jumps 0→100%. Plots the plant's natural S-shaped rise from 20°C to 170°C.  
Output: `plots/open_loop_response.png`

### Phase 2 — Closed-Loop PID (Hand-Tuned)
    py closed_loop.py

Manual PID gains: Kp=1.8, Ki=0.008, Kd=30. Simulates tracking the 60°C setpoint with unity negative feedback. Prints overshoot, rise time, and settling time.  
Output: `plots/closed_loop_pid_response.png`

### Phase 3 — Ziegler–Nichols Auto-Tuning
    py auto_tune.py

Extracts ultimate gain and period from the plant's frequency response via `control.margin`, then applies ZN rules. Prints Ku, Tu, and the derived PID gains plus performance metrics.  
Output: `plots/zn_tuned_response.png`

### Phase 3.5 — ZN vs. Cohen–Coon Comparison
    py compare_tuning.py

Runs both Ziegler–Nichols and Cohen–Coon tuning, plots both responses on the same axes, and prints a side-by-side metrics table.  
Output: `plots/tuning_comparison.png`

### Phase 4 — Interactive Dashboard
    py -m streamlit run app.py

Opens a browser tab with sliders for Kp, Ki, Kd, one-click loading of ZN and CC gains, and live updating plot + metrics. Move any slider to see the response change instantly.

---

## Performance Metrics

| Metric        | Definition                                                    |
|---------------|---------------------------------------------------------------|
| Overshoot     | (peak − setpoint) / setpoint × 100%                           |
| Rise time     | Time from 10% to 90% of the setpoint step                     |
| Settling time | Time to enter and remain within ±2% of the setpoint           |

---

## Auto-Tuning Methods

**Ziegler–Nichols (Ultimate Gain)** — Uses the gain margin and phase crossover frequency from the plant's frequency response to compute ultimate gain Ku and ultimate period Tu, then applies the classic ZN PID rules.

**Cohen–Coon** — A model-based method designed specifically for FOPDT processes. Uses the plant parameters (K, τ, θ) directly. In this simulation, raw CC gains are automatically detuned when necessary to maintain stability with the Padé-approximated plant.

---

## Notes

- The dead time is approximated with a 2nd-order Padé; this is a standard technique but introduces non-minimum-phase zeros that can interact with very high derivative gains.
- The PID controller is ideal form (no derivative filtering, no anti-windup) — appropriate for a linear simulation.
- "AI-assisted" refers to the code generation process, not the tuning algorithms themselves. All tuning methods are classical control engineering.