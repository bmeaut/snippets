# Phase 4: Interactive Streamlit Dashboard

## Objective
Build an interactive web app using Streamlit that lets users adjust Kp, Ki, Kd with sliders, see the closed-loop temperature response update in real time, and view the three performance metrics (overshoot, rise time, settling time). Include one-click loading of Ziegler–Nichols and Cohen–Coon auto-tuned gains.

---

## 1. New File: `app.py`

Create `app.py` in the project root. This is the Streamlit application, launched with:

    streamlit run app.py

### 1.1 Imports

    import streamlit as st
    import numpy as np
    import matplotlib.pyplot as plt
    import control
    from plant import ThermalPlant
    from controller import PIDController
    from tuner import ziegler_nichols_tune, cohen_coon_tune
    from utils import overshoot, rise_time, settling_time

### 1.2 Page Configuration

At the top of the script, set:

    st.set_page_config(page_title="PID Tuner — Thermal Plant", layout="wide")
    st.title("AI-Assisted PID Tuning for a Thermal Plant")
    st.markdown("Adjust the PID gains below and observe the closed-loop response to a 60°C setpoint.")

### 1.3 Constants

    SETPOINT = 60.0
    T_AMBIENT = 20.0
    T_SIM = 800.0

### 1.4 Plant Initialisation

Use `st.cache_resource` to instantiate the plant once:

    @st.cache_resource
    def get_plant():
        return ThermalPlant()

    plant = get_plant()

### 1.5 Sidebar — Gain Controls

Place all controls in `st.sidebar`.

#### Sliders

Three sliders for manual tuning:

    Kp = st.sidebar.slider("Kp (Proportional)", min_value=0.0, max_value=20.0, value=1.8, step=0.1, format="%.1f")
    Ki = st.sidebar.slider("Ki (Integral)", min_value=0.0, max_value=0.5, value=0.008, step=0.001, format="%.3f")
    Kd = st.sidebar.slider("Kd (Derivative)", min_value=0.0, max_value=100.0, value=30.0, step=1.0, format="%.1f")

Initial values match the Phase 2 placeholder gains.

#### Auto-Tune Buttons

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Auto-Tuning Methods")

    if st.sidebar.button("Load Ziegler–Nichols Gains"):
        zn = ziegler_nichols_tune(plant)
        st.session_state['Kp'] = zn['Kp']
        st.session_state['Ki'] = zn['Ki']
        st.session_state['Kd'] = zn['Kd']
        st.sidebar.success(f"ZN loaded: Kp={zn['Kp']:.2f}, Ki={zn['Ki']:.4f}, Kd={zn['Kd']:.1f}")

    if st.sidebar.button("Load Cohen–Coon Gains"):
        cc = cohen_coon_tune(plant)
        st.session_state['Kp'] = cc['Kp']
        st.session_state['Ki'] = cc['Ki']
        st.session_state['Kd'] = cc['Kd']
        st.sidebar.success(f"CC loaded: Kp={cc['Kp']:.2f}, Ki={cc['Ki']:.4f}, Kd={cc['Kd']:.1f}")

Note: Streamlit sliders don't natively bind to `st.session_state` values set by buttons unless you use a workaround. The simplest approach is:

- After a button click, store the desired gains in `st.session_state` (e.g. `st.session_state['Kp_zn']`).
- Read slider values from session state with defaults:

        Kp = st.sidebar.slider("Kp ...", value=st.session_state.get('Kp_default', 1.8))

Then on button press, update the relevant session state key. An alternative is to use `st.number_input` for tighter control, but sliders were specified. Implement whichever pattern is cleanest — the essential behaviour is that clicking a button updates the displayed slider values and the plot re-runs.

### 1.6 Main Area — Plot and Metrics

#### 1.6.1 Build and Simulate

    pid = PIDController(Kp, Ki, Kd)
    Gp = plant.transfer_function()
    Gc = pid.transfer_function()
    G_ol = Gc * Gp
    G_cl = control.feedback(G_ol, 1, sign=-1)
    t, y_dev = control.step_response(G_cl, T=T_SIM)
    T_abs = T_AMBIENT + (SETPOINT - T_AMBIENT) * y_dev

#### 1.6.2 Plot

Use `st.pyplot` with a Matplotlib figure:

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(t, T_abs, 'b-', linewidth=2, label='Temperature')
    ax.axhline(y=SETPOINT, color='grey', linestyle='--', linewidth=1.5, label=f'Setpoint {SETPOINT}°C')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Temperature (°C)')
    ax.set_title('Closed-Loop Step Response')
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig)

#### 1.6.3 Performance Metrics

Compute and display in three columns:

    col1, col2, col3 = st.columns(3)

    overshoot_val = overshoot(T_abs, SETPOINT)
    rise_t = rise_time(t, T_abs, SETPOINT)
    settle_t = settling_time(t, T_abs, SETPOINT)

    with col1:
        st.metric("Overshoot", f"{overshoot_val:.2f} %")
    with col2:
        st.metric("Rise Time (10→90%)", f"{rise_t:.2f} s" if rise_t < float('inf') else ">800 s")
    with col3:
        st.metric("Settling Time (±2%)", f"{settle_t:.2f} s" if settle_t < float('inf') else ">800 s")

Format `inf` values as `">800 s"` to keep the display clean.

### 1.7 Footer

    st.sidebar.markdown("---")
    st.sidebar.caption("Built for AI-Assisted PID Tuning demo. Plant: FOPDT with Padé delay approximation.")

---

## 2. Acceptance Criteria

- `streamlit run app.py` opens a browser tab with the dashboard.
- The sidebar contains three sliders (Kp, Ki, Kd) and two auto-tune buttons.
- Dragging any slider immediately updates the plot and all three metrics.
- Clicking "Load Ziegler–Nichols Gains" sets the sliders to the ZN values from Phase 3 and updates the plot.
- Clicking "Load Cohen–Coon Gains" sets the sliders to the CC values from Phase 3.5 and updates the plot.
- The plot shows a dashed horizontal reference line at 60°C.
- The three metrics are displayed prominently with correct units.
- The app does not crash when extreme slider values are chosen (e.g. very high Kd); if the system becomes unstable, the plot will show large oscillations — that is acceptable behaviour.
- All existing scripts (`python main.py`, `python closed_loop.py`, `python auto_tune.py`, `python compare_tuning.py`) continue to work unchanged.

---

## 3. Notes for the Coding Assistant

- Streamlit re‑runs the entire script on every widget interaction; `st.cache_resource` for the plant avoids re‑creating the Padé approximation on every slider move.
- Keep the transfer‑function creation and simulation inside the main body — they need to re‑execute when gains change.
- If the slider‑button synchronisation proves tricky, a practical solution is to replace `st.slider` with `st.number_input` for the auto‑tune buttons, or use `st.session_state` keys to hold "requested" values that the slider reads from on each run.
- The spec uses `control.step_response` which returns arrays; ensure these are 1D before plotting.