"""
auto_tune.py
------------
Phase 3: Automatic PID tuning via Ziegler–Nichols ultimate gain method.

1. Extracts Ku and Tu from the plant's frequency response.
2. Computes ZN PID gains.
3. Simulates the closed-loop step response to a 60 °C setpoint.
4. Plots and saves the result; prints performance metrics.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")          # Non-interactive backend for file output
import matplotlib.pyplot as plt
import control

from plant      import ThermalPlant
from controller import PIDController
from tuner      import ziegler_nichols_tune
from utils      import overshoot, rise_time, settling_time

# ----------------------------------------------------------------------
# 1. Set up plant and run auto-tuner
# ----------------------------------------------------------------------
plant  = ThermalPlant()
tuning = ziegler_nichols_tune(plant)

Kp = tuning["Kp"]
Ki = tuning["Ki"]
Kd = tuning["Kd"]

print(f"Ultimate Gain:  {tuning['Ku']:.3f},  Ultimate Period: {tuning['Tu']:.2f} s")
print(f"ZN PID Gains:   Kp={Kp:.3f},  Ki={Ki:.5f},  Kd={Kd:.3f}")

# ----------------------------------------------------------------------
# 2. Build closed-loop system
# ----------------------------------------------------------------------
Gp  = plant.transfer_function()
pid = PIDController(Kp, Ki, Kd)
Gc  = pid.transfer_function()

G_ol = control.series(Gc, Gp)             # open-loop: Gc(s) · Gp(s)
G_cl = control.feedback(G_ol, 1, sign=-1) # unity negative feedback

# ----------------------------------------------------------------------
# 3. Simulate step response
#    y_dev is the deviation response to a unit step;
#    scale by 40 °C (setpoint - ambient) and shift to absolute temperature.
# ----------------------------------------------------------------------
T_AMBIENT = 20.0
SETPOINT  = 60.0
STEP_MAG  = SETPOINT - T_AMBIENT   # 40 °C

t, y_dev = control.step_response(G_cl, T=800, T_num=2000)
T_abs = T_AMBIENT + STEP_MAG * np.real(y_dev)

# ----------------------------------------------------------------------
# 4. Plot
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(t, T_abs, linewidth=2, color="#1f77b4", label="Temperature (ZN Tuned)")
ax.axhline(SETPOINT, color="grey", linewidth=1.5,
           linestyle="--", label="Setpoint")

ax.set_xlabel("Time (s)", fontsize=13)
ax.set_ylabel("Temperature (°C)", fontsize=13)
ax.set_title("Closed-Loop Response with Ziegler–Nichols Tuning",
             fontsize=14, fontweight="bold")
ax.legend(fontsize=11)
ax.grid(True, linestyle="--", alpha=0.6)
ax.set_xlim(t[0], t[-1])

fig.tight_layout()

plots_dir   = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(plots_dir, exist_ok=True)
output_path = os.path.join(plots_dir, "zn_tuned_response.png")
fig.savefig(output_path, dpi=150)
plt.close(fig)

# ----------------------------------------------------------------------
# 5. Performance metrics
# ----------------------------------------------------------------------
overshoot_val = overshoot(T_abs, SETPOINT)
rise_t        = rise_time(t, T_abs, SETPOINT)
settle_t      = settling_time(t, T_abs, SETPOINT)

print(f"Overshoot:     {overshoot_val:.2f} %")
print(f"Rise time:     {rise_t:.2f} s")
print(f"Settling time: {settle_t:.2f} s")
print(f"Plot saved to: {output_path}")
