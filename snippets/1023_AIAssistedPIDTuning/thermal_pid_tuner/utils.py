"""
utils.py
--------
Performance metric functions for closed-loop PID evaluation.

All functions accept 1-D NumPy arrays and return a single float.
"""

import numpy as np


def overshoot(y: np.ndarray, setpoint: float) -> float:
    """
    Percentage overshoot relative to the setpoint.

    Returns (max(y) - setpoint) / setpoint * 100.
    Returns 0.0 if the output never exceeds the setpoint.

    Parameters
    ----------
    y        : np.ndarray  1-D output signal
    setpoint : float       Target value

    Returns
    -------
    float  Overshoot in %
    """
    y = np.asarray(y, dtype=float)
    peak = float(np.max(y))
    if peak <= setpoint:
        return 0.0
    return (peak - setpoint) / setpoint * 100.0


def rise_time(t: np.ndarray, y: np.ndarray, setpoint: float,
              low: float = 0.1, high: float = 0.9) -> float:
    """
    Time for the output to rise from (low * setpoint) to (high * setpoint).

    Finds the first crossing of each threshold and returns t_high - t_low.
    Returns float('inf') if either threshold is never crossed.

    Parameters
    ----------
    t        : np.ndarray  Time vector  [s]
    y        : np.ndarray  1-D output signal
    setpoint : float       Target value
    low      : float       Lower threshold as a fraction of setpoint (default 0.1)
    high     : float       Upper threshold as a fraction of setpoint (default 0.9)

    Returns
    -------
    float  Rise time in seconds
    """
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)

    low_val  = setpoint * low
    high_val = setpoint * high

    # First index where y >= low_val
    low_idx = np.where(y >= low_val)[0]
    if len(low_idx) == 0:
        return float("inf")

    # First index where y >= high_val
    high_idx = np.where(y >= high_val)[0]
    if len(high_idx) == 0:
        return float("inf")

    t_low  = float(t[low_idx[0]])
    t_high = float(t[high_idx[0]])
    return t_high - t_low


def settling_time(t: np.ndarray, y: np.ndarray,
                  setpoint: float, band: float = 0.02) -> float:
    """
    Smallest time t_s such that |y(t) - setpoint| <= band * setpoint
    for all t >= t_s.

    Searches backwards from the end of the array for efficiency.
    Returns float('inf') if the signal never settles within the simulation.

    Parameters
    ----------
    t        : np.ndarray  Time vector  [s]
    y        : np.ndarray  1-D output signal
    setpoint : float       Target value
    band     : float       Tolerance as a fraction of setpoint (default 0.02 = 2 %)

    Returns
    -------
    float  Settling time in seconds
    """
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)

    threshold = band * abs(setpoint)
    within_band = np.abs(y - setpoint) <= threshold

    # Walk backwards to find the last index where signal is OUTSIDE the band
    outside_indices = np.where(~within_band)[0]
    if len(outside_indices) == 0:
        # Always within band — settled from the start
        return float(t[0])

    last_outside = outside_indices[-1]

    # If the very last sample is still outside, it never settled
    if last_outside >= len(t) - 1:
        return float("inf")

    return float(t[last_outside + 1])
