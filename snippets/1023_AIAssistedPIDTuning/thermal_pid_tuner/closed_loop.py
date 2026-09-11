"""
closed_loop.py
--------------
Phase 2: Closed-loop PID control simulation.

Builds the feedback loop  r → [PID] → [Plant] → y  and simulates a
step from ambient (20 °C) to the target setpoint (60 °C).
Plots the response, computes performance metrics, and saves the figure.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")          # Non-interactive backend for file output
import matplotlib.pyplot as plt
import control

from plant      import ThermalPlant
from controller import PIDController
import utils

# ----------------------------------------------------------------------
# Parameters
# ----------------------------------------------------------------------
SETPOINT  = 60.0    # °C  – target temperature
T_AMBIENT = 20.0    # °C  – starting / ambient temperature
STEP_MAG  = SETPOINT - T_AMBIENT   # 40 °C command step in deviation space

# Placeholder PID gains (to be optimised in later phases)
Kp = 1.8
Ki = 0.008
Kd = 30.0

T_END = 800        # s  – simulation horizon

# ----------------------------------------------------------------------
# 1. Build plant and controller transfer functions
# ----------------------------------------------------------------------
thermal_plant = ThermalPlant()          # K=1.5, tau=200, theta=20, T_amb=20
pid           = PIDController(Kp=Kp, Ki=Ki, Kd=Kd)

Gp = thermal_plant.transfer_function()
Gc = pid.transfer_function()

# ----------------------------------------------------------------------
# 2. Form open-loop and close the feedback loop
# ----------------------------------------------------------------------
G_ol = control.series(Gc, Gp)                  # Gc(s) · Gp(s)
G_cl = control.feedback(G_ol, 1, sign=-1)      # unity negative feedback

# ----------------------------------------------------------------------
# 3. Simulate step response (unit step in deviation space)
# ----------------------------------------------------------------------
t, y_dev = control.step_response(G_cl, T=T_END, T_num=2000)

# Convert deviation output → absolute temperature
# y_dev is the response to a unit step; scale by STEP_MAG then shift
T_abs = T_AMBIENT + STEP_MAG * np.real(y_dev)

# ----------------------------------------------------------------------
# 4. Plot
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(t, T_abs, linewidth=2, color="#1f77b4", label="Temperature")
ax.axhline(SETPOINT, color="#d62728", linewidth=1.5,
           linestyle="--", label=f"Setpoint {SETPOINT:.0f} °C")

ax.set_xlabel("Time (s)", fontsize=13)
ax.set_ylabel("Temperature (°C)", fontsize=13)
ax.set_title("Closed-Loop PID Response to 60°C Setpoint",
             fontsize=14, fontweight="bold")
ax.legend(fontsize=11)
ax.grid(True, linestyle="--", alpha=0.6)
ax.set_xlim(t[0], t[-1])

fig.tight_layout()

plots_dir   = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(plots_dir, exist_ok=True)
output_path = os.path.join(plots_dir, "closed_loop_pid_response.png")
fig.savefig(output_path, dpi=150)
plt.close(fig)

# ----------------------------------------------------------------------
# 5. Performance metrics
# ----------------------------------------------------------------------
overshoot_val = utils.overshoot(T_abs, SETPOINT)
rise_t        = utils.rise_time(t, T_abs, SETPOINT)
settle_t      = utils.settling_time(t, T_abs, SETPOINT)

print(f"Overshoot:     {overshoot_val:.2f} %")
print(f"Rise time:     {rise_t:.2f} s")
print(f"Settling time: {settle_t:.2f} s")
print(f"Plot saved to: {output_path}")
