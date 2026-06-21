"""
app.py
------
Phase 4: Interactive Streamlit dashboard for PID tuning.

Launch with:
    streamlit run app.py

Features
--------
- Three sidebar sliders (Kp, Ki, Kd) — update the plot on every change.
- "Load Ziegler-Nichols Gains" button — writes ZN gains into session state,
  sliders snap to those values on the next re-run.
- "Load Cohen-Coon Gains" button — same for CC gains.
- Main area: Matplotlib step-response plot + three st.metric tiles.

Slider-button synchronisation pattern (post Phase-4-fix)
----------------------------------------------------------
Streamlit forbids writing to a widget's own state key (e.g. 'Kp_slider')
after that widget has been instantiated — doing so raises
StreamlitAPIException.  The correct pattern, used here, is:

  1. Separate "master" session-state keys — 'kp_val', 'ki_val', 'kd_val' —
     are the single source of truth for the gains.
  2. Each slider reads its starting position from the master key via
     `value=st.session_state['kp_val']`, and uses a *different* key
     (`key='Kp_slider'`) purely for Streamlit's internal widget tracking.
  3. Immediately after each slider call, the live value is written back
     to the master key — this keeps slider position and master key in
     sync on manual drags.
  4. Button handlers write ONLY to the master keys (never to the
     '*_slider' widget keys) and then call `st.rerun()` to force an
     immediate re-render, which causes the sliders to read their new
     `value=` from the updated master keys.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")          # must be set before pyplot import
import matplotlib.pyplot as plt
import control
import streamlit as st

from plant      import ThermalPlant
from controller import PIDController
from tuner      import ziegler_nichols_tune, cohen_coon_tune
from utils      import overshoot, rise_time, settling_time

# ======================================================================
# Page configuration  (must be the first Streamlit call)
# ======================================================================
st.set_page_config(page_title="PID Tuner — Thermal Plant", layout="wide")

# ======================================================================
# Constants
# ======================================================================
SETPOINT  = 60.0
T_AMBIENT = 20.0
T_SIM     = 800.0
STEP_MAG  = SETPOINT - T_AMBIENT   # 40 °C

# ======================================================================
# Plant — cached so the Pade TF is not rebuilt on every slider move
# ======================================================================
@st.cache_resource
def get_plant() -> ThermalPlant:
    return ThermalPlant()

plant = get_plant()

# ======================================================================
# Initialise master gain keys once (Phase-2 placeholder defaults)
# ======================================================================
if "kp_val" not in st.session_state:
    st.session_state["kp_val"] = 1.8
if "ki_val" not in st.session_state:
    st.session_state["ki_val"] = 0.008
if "kd_val" not in st.session_state:
    st.session_state["kd_val"] = 30.0

# ======================================================================
# Sidebar — title & sliders (read from / write back to master keys)
# ======================================================================
st.sidebar.header("PID Gain Controls")

Kp = st.sidebar.slider(
    "Kp (Proportional)", min_value=0.0, max_value=20.0,
    value=st.session_state["kp_val"], step=0.1, format="%.1f",
    key="Kp_slider",
)
# Sync slider's live value back to the master key on every change
st.session_state["kp_val"] = Kp

Ki = st.sidebar.slider(
    "Ki (Integral)", min_value=0.0, max_value=0.5,
    value=st.session_state["ki_val"], step=0.001, format="%.3f",
    key="Ki_slider",
)
st.session_state["ki_val"] = Ki

Kd = st.sidebar.slider(
    "Kd (Derivative)", min_value=0.0, max_value=100.0,
    value=st.session_state["kd_val"], step=1.0, format="%.1f",
    key="Kd_slider",
)
st.session_state["kd_val"] = Kd

# ======================================================================
# Sidebar — auto-tune buttons (write ONLY to master keys, then rerun)
# ======================================================================
st.sidebar.markdown("---")
st.sidebar.markdown("### Auto-Tuning Methods")

if st.sidebar.button("Load Ziegler\u2013Nichols Gains"):
    zn = ziegler_nichols_tune(plant)
    st.session_state["kp_val"] = float(np.clip(zn["Kp"], 0.0, 20.0))
    st.session_state["ki_val"] = float(np.clip(zn["Ki"], 0.0, 0.5))
    st.session_state["kd_val"] = float(np.clip(zn["Kd"], 0.0, 100.0))
    st.sidebar.success(
        f"ZN loaded: Kp={zn['Kp']:.2f}, Ki={zn['Ki']:.4f}, Kd={zn['Kd']:.1f}"
    )
    st.rerun()

if st.sidebar.button("Load Cohen\u2013Coon Gains"):
    cc = cohen_coon_tune(plant)
    st.session_state["kp_val"] = float(np.clip(cc["Kp"], 0.0, 20.0))
    st.session_state["ki_val"] = float(np.clip(cc["Ki"], 0.0, 0.5))
    st.session_state["kd_val"] = float(np.clip(cc["Kd"], 0.0, 100.0))
    st.sidebar.success(
        f"CC loaded: Kp={cc['Kp']:.2f}, Ki={cc['Ki']:.4f}, Kd={cc['Kd']:.1f}"
    )
    st.rerun()

# ======================================================================
# Sidebar — footer
# ======================================================================
st.sidebar.markdown("---")
st.sidebar.caption(
    "Built for AI-Assisted PID Tuning demo.  "
    "Plant: FOPDT with Pad\u00e9 delay approximation."
)

# ======================================================================
# Main area — header
# ======================================================================
st.title("AI-Assisted PID Tuning for a Thermal Plant")
st.markdown(
    "Adjust the PID gains in the sidebar and observe the closed-loop "
    "response to a **60 °C** setpoint.  "
    "Use the auto-tune buttons to load pre-computed gains instantly."
)

# Display the current gains prominently
g1, g2, g3 = st.columns(3)
g1.markdown(f"**Kp** = `{Kp:.3f}`")
g2.markdown(f"**Ki** = `{Ki:.4f}`")
g3.markdown(f"**Kd** = `{Kd:.3f}`")

st.markdown("---")

# ======================================================================
# Simulation — runs on every re-render (gains may have changed)
# ======================================================================
try:
    pid  = PIDController(Kp, Ki, Kd)
    Gp   = plant.transfer_function()
    Gc   = pid.transfer_function()
    G_ol = control.series(Gc, Gp)
    G_cl = control.feedback(G_ol, 1, sign=-1)
    t, y_dev = control.step_response(G_cl, T=T_SIM, T_num=2000)

    # Ensure 1-D real arrays for plotting and metrics
    t     = np.real(np.asarray(t).flatten())
    y_dev = np.real(np.asarray(y_dev).flatten())
    T_abs = T_AMBIENT + STEP_MAG * y_dev

    sim_ok = True
    sim_error = None
except Exception as exc:
    sim_ok    = False
    sim_error = str(exc)

# ======================================================================
# Plot
# ======================================================================
fig, ax = plt.subplots(figsize=(10, 5))

if sim_ok:
    ax.plot(t, T_abs, "b-", linewidth=2, label="Temperature")
else:
    ax.text(
        0.5, 0.5,
        f"Simulation error:\n{sim_error}",
        ha="center", va="center", transform=ax.transAxes,
        color="red", fontsize=11,
    )

ax.axhline(
    y=SETPOINT, color="grey", linestyle="--",
    linewidth=1.5, label=f"Setpoint  {SETPOINT:.0f} \u00b0C",
)
ax.set_xlabel("Time (s)", fontsize=12)
ax.set_ylabel("Temperature (\u00b0C)", fontsize=12)
ax.set_title("Closed-Loop Step Response", fontsize=13, fontweight="bold")
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
fig.tight_layout()

st.pyplot(fig)
plt.close(fig)

# ======================================================================
# Performance metrics
# ======================================================================
st.markdown("### Performance Metrics")
col1, col2, col3 = st.columns(3)

if sim_ok:
    overshoot_val = overshoot(T_abs, SETPOINT)
    rise_t        = rise_time(t, T_abs, SETPOINT)
    settle_t      = settling_time(t, T_abs, SETPOINT)

    with col1:
        st.metric("Overshoot", f"{overshoot_val:.2f} %")
    with col2:
        st.metric(
            "Rise Time (10\u219290%)",
            f"{rise_t:.2f} s" if rise_t < float("inf") else ">800 s",
        )
    with col3:
        st.metric(
            "Settling Time (\u00b12%)",
            f"{settle_t:.2f} s" if settle_t < float("inf") else ">800 s",
        )
else:
    with col1:
        st.metric("Overshoot", "N/A")
    with col2:
        st.metric("Rise Time (10\u219290%)", "N/A")
    with col3:
        st.metric("Settling Time (\u00b12%)", "N/A")
