"""
compare_tuning.py
-----------------
Phase 3.5: Cohen-Coon auto-tuning and comparison with Ziegler-Nichols.

1. Tunes the plant with both ZN and Cohen-Coon.
2. Simulates closed-loop step responses for each.
3. Overlays both responses on a single plot.
4. Prints a formatted metrics comparison table.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")          # Non-interactive backend for file output
import matplotlib.pyplot as plt
import control

from plant      import ThermalPlant
from controller import PIDController
from tuner      import ziegler_nichols_tune, cohen_coon_tune
from utils      import overshoot, rise_time, settling_time

# ----------------------------------------------------------------------
# Parameters
# ----------------------------------------------------------------------
SETPOINT  = 60.0
T_AMBIENT = 20.0
T_SIM     = 800.0
STEP_MAG  = SETPOINT - T_AMBIENT   # 40 degrees C

# ----------------------------------------------------------------------
# 1. Instantiate plant and run both tuners
# ----------------------------------------------------------------------
plant = ThermalPlant()

zn = ziegler_nichols_tune(plant)
cc = cohen_coon_tune(plant)

print("=" * 60)
print(f"Ziegler-Nichols PID:  Kp={zn['Kp']:.4f},  Ki={zn['Ki']:.5f},  Kd={zn['Kd']:.4f}")
print(f"Cohen-Coon PID:       Kp={cc['Kp']:.4f},  Ki={cc['Ki']:.5f},  Kd={cc['Kd']:.4f}")
print(f"  (Kc={cc['Kc']:.4f},  tauI={cc['tauI']:.2f} s,  tauD={cc['tauD']:.2f} s,"
      f"  detuning factor={cc['detune_f']:.4f})")
print("=" * 60)

# ----------------------------------------------------------------------
# 2. Helper: build closed loop and simulate
# ----------------------------------------------------------------------
def simulate_closed_loop(Kp, Ki, Kd):
    """
    Build a unity-negative-feedback closed-loop system with the given
    PID gains and simulate a step from ambient to setpoint.

    Returns
    -------
    t     : np.ndarray  Time vector  [s]
    T_abs : np.ndarray  Absolute temperature  [degrees C]
    """
    pid  = PIDController(Kp, Ki, Kd)
    Gp   = plant.transfer_function()
    Gc   = pid.transfer_function()
    G_ol = control.series(Gc, Gp)
    G_cl = control.feedback(G_ol, 1, sign=-1)
    t, y_dev = control.step_response(G_cl, T=T_SIM, T_num=2000)
    T_abs = T_AMBIENT + STEP_MAG * np.real(y_dev)
    return t, T_abs


t_zn, T_zn = simulate_closed_loop(zn["Kp"], zn["Ki"], zn["Kd"])
t_cc, T_cc = simulate_closed_loop(cc["Kp"], cc["Ki"], cc["Kd"])

# ----------------------------------------------------------------------
# 3. Plot both responses on the same axes
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(t_zn, T_zn, linewidth=2, color="#1f77b4", label="Ziegler-Nichols")
ax.plot(t_cc, T_cc, linewidth=2, color="#ff7f0e", label="Cohen-Coon")
ax.axhline(SETPOINT, color="grey", linewidth=1.5,
           linestyle="--", label=f"Setpoint  {SETPOINT:.0f} deg C")

ax.set_xlabel("Time (s)", fontsize=13)
ax.set_ylabel("Temperature (deg C)", fontsize=13)
ax.set_title("ZN vs Cohen-Coon Tuning Comparison",
             fontsize=14, fontweight="bold")
ax.legend(fontsize=11)
ax.grid(True, linestyle="--", alpha=0.6)
ax.set_xlim(t_zn[0], t_zn[-1])

fig.tight_layout()

plots_dir   = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(plots_dir, exist_ok=True)
output_path = os.path.join(plots_dir, "tuning_comparison.png")
fig.savefig(output_path, dpi=150)
plt.close(fig)

print(f"Plot saved to: {output_path}")

# ----------------------------------------------------------------------
# 4. Compute metrics for both methods
# ----------------------------------------------------------------------
os_zn  = overshoot(T_zn, SETPOINT)
rt_zn  = rise_time(t_zn, T_zn, SETPOINT)
st_zn  = settling_time(t_zn, T_zn, SETPOINT)

os_cc  = overshoot(T_cc, SETPOINT)
rt_cc  = rise_time(t_cc, T_cc, SETPOINT)
st_cc  = settling_time(t_cc, T_cc, SETPOINT)

# ----------------------------------------------------------------------
# 5. Print formatted comparison table
# ----------------------------------------------------------------------
col_w = 18
print()
print(f"{'Metric':<24} {'Ziegler-Nichols':>{col_w}} {'Cohen-Coon':>{col_w}}")
print("-" * (24 + col_w * 2 + 2))
print(f"{'Overshoot (%)':<24} {os_zn:>{col_w}.2f} {os_cc:>{col_w}.2f}")
print(f"{'Rise time (s)':<24} {rt_zn:>{col_w}.2f} {rt_cc:>{col_w}.2f}")
print(f"{'Settling time (s)':<24} {st_zn:>{col_w}.2f} {st_cc:>{col_w}.2f}")
