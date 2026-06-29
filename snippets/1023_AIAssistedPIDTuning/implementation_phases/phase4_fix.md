# Phase 4 Fix: Slider Bugs & Auto-Tune Button Errors

## Problem Summary

Two issues observed during testing of `app.py`:

1. **Sliders unresponsive** — sometimes moving a slider doesn't register the new value; the slider snaps back to its previous position.

2. **Auto-tune buttons throw StreamlitAPIException**: "st.session_state.Kp_slider cannot be modified after the widget with key Kp_slider is instantiated." This happens for both "Load Ziegler–Nichols" and "Load Cohen–Coon" buttons. The error occurs because the button handler tries to write directly to a widget's bound session state key after that widget has already been rendered. Streamlit forbids this. The interesting side effect (slider shows auto-tuned values after the error) confirms the values are being set but via an invalid path.

---

## Root Cause Analysis

**Issue 2 — the crash:**

The current button handler writes to widget keys directly:
    st.session_state['Kp_slider'] = zn['Kp']   # ILLEGAL in Streamlit

Streamlit widget keys (ending in `_slider`) are managed internally. You may read them, but you may **not** write to them from outside the widget's own `value=` parameter. The correct approach is:

- Use **separate** session state keys (e.g. `kp_val`, `ki_val`, `kd_val`) as the "master" source of truth.
- The slider's `value=` parameter reads from these master keys.
- Button handlers write to these master keys, then call `st.rerun()` if needed (or let the natural rerun pick up the change).

**Issue 1 — slider unresponsiveness:**

Likely a secondary symptom of the same root cause: if the code ever tries to overwrite the widget key, Streamlit's internal state tracking gets confused, and subsequent slider drags may not register correctly. Fixing issue 2 will likely resolve issue 1. Additionally, ensure `value=` for each slider is explicitly bound to the session state key so that slider position and state stay synchronised.

---

## Required Changes to `app.py`

### 1. Initialise Master Gain Keys

At the top of the script (after constants, before sliders), initialise the "master" session state keys if they don't exist:

    # Initialise master gain keys once
    if 'kp_val' not in st.session_state:
        st.session_state['kp_val'] = 1.8
    if 'ki_val' not in st.session_state:
        st.session_state['ki_val'] = 0.008
    if 'kd_val' not in st.session_state:
        st.session_state['kd_val'] = 30.0

### 2. Rewrite Sliders to Use Master Keys

Replace the existing slider definitions with:

    Kp = st.sidebar.slider(
        "Kp (Proportional)", min_value=0.0, max_value=20.0,
        value=st.session_state['kp_val'], step=0.1, format="%.1f",
        key="Kp_slider"
    )
    # Sync slider's live value back to the master key on every change
    st.session_state['kp_val'] = Kp

    Ki = st.sidebar.slider(
        "Ki (Integral)", min_value=0.0, max_value=0.5,
        value=st.session_state['ki_val'], step=0.001, format="%.3f",
        key="Ki_slider"
    )
    st.session_state['ki_val'] = Ki

    Kd = st.sidebar.slider(
        "Kd (Derivative)", min_value=0.0, max_value=100.0,
        value=st.session_state['kd_val'], step=1.0, format="%.1f",
        key="Kd_slider"
    )
    st.session_state['kd_val'] = Kd

This pattern:
- Reads the slider's starting position from the master key.
- Immediately writes back whatever value the slider produces (user drag or programmatic change) to the master key, keeping them in sync.
- Keeps the widget `key` distinct from the master value key.

### 3. Rewrite Button Handlers to Write to Master Keys Only

Replace the button blocks with:

    if st.sidebar.button("Load Ziegler–Nichols Gains"):
        zn = ziegler_nichols_tune(plant)
        st.session_state['kp_val'] = float(np.clip(zn['Kp'], 0.0, 20.0))
        st.session_state['ki_val'] = float(np.clip(zn['Ki'], 0.0, 0.5))
        st.session_state['kd_val'] = float(np.clip(zn['Kd'], 0.0, 100.0))
        st.sidebar.success(f"ZN loaded: Kp={zn['Kp']:.2f}, Ki={zn['Ki']:.4f}, Kd={zn['Kd']:.1f}")
        st.rerun()

    if st.sidebar.button("Load Cohen–Coon Gains"):
        cc = cohen_coon_tune(plant)
        st.session_state['kp_val'] = float(np.clip(cc['Kp'], 0.0, 20.0))
        st.session_state['ki_val'] = float(np.clip(cc['Ki'], 0.0, 0.5))
        st.session_state['kd_val'] = float(np.clip(cc['Kd'], 0.0, 100.0))
        st.sidebar.success(f"CC loaded: Kp={cc['Kp']:.2f}, Ki={cc['Ki']:.4f}, Kd={cc['Kd']:.1f}")
        st.rerun()

Key points:
- Write **only** to `kp_val`, `ki_val`, `kd_val` — never to `Kp_slider`, `Ki_slider`, `Kd_slider`.
- Use `np.clip` to keep gains within slider bounds (prevents visual mismatch).
- Call `st.rerun()` to force an immediate re-render with the new values. (This is safe because the slider `value=` parameter reads from the master keys, which now hold the new values.)

### 4. Remove Any Leftover Widget-Key Writes

Search the entire `app.py` for any assignments to `st.session_state['Kp_slider']`, `st.session_state['Ki_slider']`, or `st.session_state['Kd_slider']` and delete them all. The only assignments to `*_slider` keys should be the ones done automatically by Streamlit when the slider widget renders.

### 5. Keep the Rest Unchanged

The following sections of `app.py` require **no changes**:
- Imports
- `st.set_page_config`, title, markdown header
- Constants (`SETPOINT`, `T_AMBIENT`, `T_SIM`)
- `get_plant()` with `st.cache_resource`
- Simulation logic (transfer function, step response, `T_abs`)
- Matplotlib plot and `st.pyplot(fig)`
- Metrics in three columns
- Footer

The only edits are in the gain initialisation, slider definitions, and button handlers.

---

## Acceptance Criteria

- `streamlit run app.py` launches without errors.
- Dragging any slider smoothly updates the plot and metrics in real time; no "snap back" behaviour.
- Clicking "Load Ziegler–Nichols Gains" immediately moves all three sliders to ZN values, updates the plot, and shows a success message — with **no StreamlitAPIException**.
- Clicking "Load Cohen–Coon Gains" does the same for CC values, including the detuning warning if applicable.
- Repeatedly alternating between ZN and CC buttons works correctly.
- Manually dragging sliders after using an auto-tune button works correctly.
- All four existing terminal scripts (`main.py`, `closed_loop.py`, `auto_tune.py`, `compare_tuning.py`) still run unchanged.