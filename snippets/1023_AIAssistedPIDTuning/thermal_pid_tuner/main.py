"""
main.py
-------
Entry point for the Phase 1 open-loop step response simulation.

Instantiates the ThermalPlant, runs a 0→100 % heater step, and saves
a publication-quality plot to plots/open_loop_response.png.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")          # Non-interactive backend for file output
import matplotlib.pyplot as plt

from plant import ThermalPlant


def main() -> None:
    # ------------------------------------------------------------------
    # 1. Instantiate plant with default parameters
    # ------------------------------------------------------------------
    plant = ThermalPlant(K=1.5, tau=200.0, theta=20.0, T_amb=20.0)

    # ------------------------------------------------------------------
    # 2. Run open-loop step response: heater 0 → 100 %
    # ------------------------------------------------------------------
    t, T = plant.step_response(u_step=100.0, t_end=800.0, dt=0.5)

    # ------------------------------------------------------------------
    # 3. Steady-state reference
    # ------------------------------------------------------------------
    T_ss = plant.T_amb + plant.K * 100.0   # 20 + 1.5 * 100 = 170 °C

    # ------------------------------------------------------------------
    # 4. Publication-quality plot
    # ------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(t, T, linewidth=2, color="#1f77b4", label="Plant output T(t)")
    ax.axhline(T_ss, color="#d62728", linewidth=1.5,
               linestyle="--", label=f"Steady-state  {T_ss:.1f} °C")

    ax.set_xlabel("Time (s)", fontsize=13)
    ax.set_ylabel("Temperature (°C)", fontsize=13)
    ax.set_title("Open-Loop Step Response (Heater 0→100%)", fontsize=14, fontweight="bold")
    ax.legend(fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.set_xlim(t[0], t[-1])
    ax.set_ylim(plant.T_amb - 5, T_ss + 10)

    fig.tight_layout()

    # ------------------------------------------------------------------
    # 5. Save figure
    # ------------------------------------------------------------------
    plots_dir = os.path.join(os.path.dirname(__file__), "plots")
    os.makedirs(plots_dir, exist_ok=True)
    output_path = os.path.join(plots_dir, "open_loop_response.png")
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    # ------------------------------------------------------------------
    # 6. Summary
    # ------------------------------------------------------------------
    print(f"Steady-state temperature: {T_ss:.1f} °C")
    print(f"Plot saved to: {output_path}")


if __name__ == "__main__":
    main()
