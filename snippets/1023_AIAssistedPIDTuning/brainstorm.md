# Brainstorm: AI-Assisted PID Tuning for a Simple Thermal Plant

---

## Overview

**Topic:** AI-Assisted PID Tuning for a Simple Thermal Plant

**Why a thermal system?**
- Intuitive — everyone understands heating something to a target temperature
- No control engineering background needed to follow along
- Simple first-order dynamics
- Relatable real-world application (ovens, heated chambers, industrial processes)

**What is PID Tuning?**
A PID controller adjusts a system output (e.g. heater power) to match a desired setpoint (e.g. target temperature) using three terms:
- **P (Proportional):** reacts to current error
- **I (Integral):** corrects accumulated past error
- **D (Derivative):** anticipates future error

Tuning = finding the right Kp, Ki, Kd values so the system responds well (fast, stable, minimal overshoot).

---

## Plant Model

**First-order thermal system with dead time:**

G(s) = K · e^(-θs) / (τs + 1)

**Parameters:**
- **K** — steady-state gain (°C per % heater power), e.g. 1.5
- **τ (tau)** — time constant (system sluggishness), e.g. 200 seconds
- **θ (theta)** — dead time (delay before response), e.g. 20 seconds

Exact parameter values to be finalized during the planning phase.

---

## Tool Split

| Role | Tool | Mode |
|------|------|------|
| Planning, outlining, clarifying questions | DeepSeek-V4-Pro | Expert mode, DeepThink enabled |
| Code generation, implementation | Claude Sonnet 4.6 | Medium Extended Thinking |

---

## Implementation Phases

1. **DeepSeek:** Model the thermal plant, define transfer function parameters
2. **DeepSeek:** Plan the full implementation structure, ask clarifying questions
3. **Claude:** Simulate open-loop step response
4. **Claude:** Implement closed-loop PID controller, plot response vs. setpoint reference line
5. **Claude:** Implement automatic tuning algorithm (Claude decides the method)
6. **Claude:** Build interactive UI with configurable Kp, Ki, Kd and performance metrics display

---

## Simulation & Visualization

**Plot will include:**
- Flat horizontal reference line at the setpoint
- PID controller temperature response curve tracking the setpoint

**Performance metrics to display:**
- Overshoot (%)
- Rise time
- Settling time

**Interactive UI:**
- Configurable Kp, Ki, Kd inputs/sliders
- Plot updates on parameter change
- Performance metrics update accordingly

---

## Important Framing Note

"AI-assisted" in this context means the AI wrote the code — not that the tuning algorithm itself is intelligent.
