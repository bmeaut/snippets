"""Tier 3 spec 11.5 / 11.6 - phyphox loader and resampler (RL1-RL3), real recordings (RR1-RR5)."""
import math
import zipfile

import numpy as np
import pytest

import imu_filters as F
import imu_io
import imu_metrics  # noqa: F401  (imported so a missing module fails loudly)
from tier3_helpers import (ACCEL_HEADER, GYRO_HEADER, REAL_FILES, csv_text, fmt_rows, real_run, write_zip)

ACCEL_TEXT_ROWS = [
    ["1.156000071E-3", "1.000000000E-1", "-2.500000000E-1", "9.810000000E+0"],
    ["1.100000000E-2", "1.250000000E-1", "-2.000000000E+0", "9.750000000E+0"],
    ["2.100000000E-2", "-1.500000000E+0", "5.000000000E-1", "-9.810000000E+0"],
    ["3.100000000E-2", "0.000000000E+0", "3.125000000E-2", "1.000000000E+1"],
]
GYRO_TEXT_ROWS = [
    ["2.000000000E-3", "1.000000000E-2", "-2.000000000E-2", "3.000000000E-2"],
    ["1.200000000E-2", "2.500000000E-1", "5.000000000E-1", "-1.250000000E-1"],
    ["2.200000000E-2", "-7.500000000E-1", "1.562500000E-2", "0.000000000E+0"],
]


def _arr(rows):
    return np.array([[float(x) for x in r] for r in rows], dtype=np.float64)


def _valid_members(**overrides):
    members = {"Accelerometer.csv": csv_text(ACCEL_HEADER, ACCEL_TEXT_ROWS),
               "Gyroscope.csv": csv_text(GYRO_HEADER, GYRO_TEXT_ROWS)}
    members.update(overrides)
    return members


def _load(tmp_path, members, name="rec.zip"):
    return imu_io.load_phyphox_zip(write_zip(tmp_path / name, members))


def _check_values(rec, accel_rows=ACCEL_TEXT_ROWS, gyro_rows=GYRO_TEXT_ROWS):
    a, g = _arr(accel_rows), _arr(gyro_rows)
    for arr in (rec.accel_t, rec.accel, rec.gyro_t, rec.gyro):
        assert isinstance(arr, np.ndarray) and arr.dtype == np.float64
    assert rec.accel_t.shape == (len(a),) and rec.accel.shape == (len(a), 3)
    assert rec.gyro_t.shape == (len(g),) and rec.gyro.shape == (len(g), 3)
    # the values in the fixtures are exact in binary or have <= 10 significant digits
    np.testing.assert_allclose(rec.accel_t, a[:, 0], rtol=1e-15, atol=0)
    np.testing.assert_allclose(rec.accel, a[:, 1:], rtol=1e-15, atol=0)
    np.testing.assert_allclose(rec.gyro_t, g[:, 0], rtol=1e-15, atol=0)
    np.testing.assert_allclose(rec.gyro, g[:, 1:], rtol=1e-15, atol=0)


# ---------------------------------------------------------------- RL1
def test_RL1_valid_zip_loads(tmp_path):
    path = write_zip(tmp_path / "rec.zip", _valid_members())
    rec = imu_io.load_phyphox_zip(path)
    _check_values(rec)
    assert rec.source == path
    assert isinstance(rec.source, str)


def test_RL1_exact_float_values_for_exactly_representable_numbers(tmp_path):
    rows_a = [["0.0", "0.5", "-0.25", "9.75"], ["1.25E-1", "1.5E0", "2.5E-1", "-1.0E+1"],
              ["2.5E-1", "1.5625E-2", "-3.125E-2", "8.0E0"]]
    rows_g = [["0.0", "0.5", "0.25", "0.125"], ["5.0E-1", "-1.5E0", "6.25E-2", "3.0E0"]]
    rec = _load(tmp_path, {"Accelerometer.csv": csv_text(ACCEL_HEADER, rows_a),
                           "Gyroscope.csv": csv_text(GYRO_HEADER, rows_g)})
    np.testing.assert_array_equal(rec.accel_t, [0.0, 0.125, 0.25])
    np.testing.assert_array_equal(rec.accel, [[0.5, -0.25, 9.75], [1.5, 0.25, -10.0], [0.015625, -0.03125, 8.0]])
    np.testing.assert_array_equal(rec.gyro_t, [0.0, 0.5])
    np.testing.assert_array_equal(rec.gyro, [[0.5, 0.25, 0.125], [-1.5, 0.0625, 3.0]])


def test_RL1_values_are_returned_unchanged_no_axis_remap_or_time_shift(tmp_path):
    rec = _load(tmp_path, _valid_members())
    assert rec.accel_t[0] > 0.0                      # no shift to start at zero
    assert rec.accel_t[0] != rec.gyro_t[0]           # the two clocks are kept separate
    a = _arr(ACCEL_TEXT_ROWS)
    assert rec.accel[2, 2] == a[2, 3] and rec.accel[2, 2] < 0   # z column last, sign kept


EXTRA_MEMBERS = {
    "meta/time.csv": "event,experiment time,system time,system time text\nSTART,0,0,x\n",
    "meta/device.csv": "property,value\nbrand,x\n",
    "Raw Data.csv": "a,b\n1,2\n",
    "Magnetometer.csv": "garbage that must be ignored",
    "readme.txt": "hello",
}


def test_RL1_extra_members_and_meta_are_ignored(tmp_path):
    members = _valid_members()
    members.update(EXTRA_MEMBERS)
    _check_values(_load(tmp_path, members))


def test_RL1_zip_without_meta_loads(tmp_path):
    members = _valid_members()
    assert not any(k.startswith("meta") for k in members)
    _check_values(_load(tmp_path, members))


def test_RL1_bom_crlf_and_trailing_blank_lines(tmp_path):
    members = {
        "Accelerometer.csv": csv_text(ACCEL_HEADER, ACCEL_TEXT_ROWS, newline="\r\n", trailing="\r\n\r\n", bom=True),
        "Gyroscope.csv": csv_text(GYRO_HEADER, GYRO_TEXT_ROWS, newline="\r\n", trailing="\r\n   \r\n\r\n", bom=True),
    }
    _check_values(_load(tmp_path, members))


def test_RL1_whitespace_only_lines_between_rows_are_skipped(tmp_path):
    a_text = ACCEL_HEADER + "\n" + ",".join(ACCEL_TEXT_ROWS[0]) + "\n   \n" + "\n".join(
        ",".join(r) for r in ACCEL_TEXT_ROWS[1:]) + "\n\n"
    _check_values(_load(tmp_path, _valid_members(**{"Accelerometer.csv": a_text})))


def test_RL1_header_with_quotes_and_spaces_is_accepted(tmp_path):
    quoted_a = '"Time (s)","X (m/s^2)","Y (m/s^2)","Z (m/s^2)"'
    spaced_g = ' Time (s) , X (rad/s) ,Y (rad/s), Z (rad/s) '
    members = {"Accelerometer.csv": csv_text(quoted_a, ACCEL_TEXT_ROWS),
               "Gyroscope.csv": csv_text(spaced_g, GYRO_TEXT_ROWS)}
    _check_values(_load(tmp_path, members))


def test_RL1_two_data_rows_are_enough(tmp_path):
    members = {"Accelerometer.csv": csv_text(ACCEL_HEADER, ACCEL_TEXT_ROWS[:2]),
               "Gyroscope.csv": csv_text(GYRO_HEADER, GYRO_TEXT_ROWS[:2])}
    _check_values(_load(tmp_path, members), ACCEL_TEXT_ROWS[:2], GYRO_TEXT_ROWS[:2])


def test_RL1_large_recording_shapes(tmp_path):
    n = 2000
    ta = np.arange(n) * 0.01 + 0.0013
    rows_a = fmt_rows(np.column_stack([ta, np.sin(ta), np.cos(ta), np.full(n, 9.81)]))
    rows_g = fmt_rows(np.column_stack([ta + 0.003, np.cos(ta), np.sin(ta), np.zeros(n)]))
    rec = _load(tmp_path, {"Accelerometer.csv": csv_text(ACCEL_HEADER, rows_a),
                           "Gyroscope.csv": csv_text(GYRO_HEADER, rows_g)})
    assert rec.accel.shape == (n, 3) and rec.gyro.shape == (n, 3)
    np.testing.assert_allclose(rec.accel_t, _arr(rows_a)[:, 0], rtol=1e-15, atol=0)


# ---------------------------------------------------------------- RL2
def _a_rows(rows):
    return {"Accelerometer.csv": csv_text(ACCEL_HEADER, rows)}


def _g_rows(rows):
    return {"Gyroscope.csv": csv_text(GYRO_HEADER, rows)}


def _bad_zip_cases():
    ok_a, ok_g = ACCEL_TEXT_ROWS, GYRO_TEXT_ROWS
    semi_a = "Time (s);X (m/s^2);Y (m/s^2);Z (m/s^2)\n0,001;0,1;0,2;9,81\n0,011;0,1;0,2;9,81\n0,021;0,1;0,2;9,81\n"
    android_a = '"Time (s)","Acceleration x (m/s^2)","Acceleration y (m/s^2)","Acceleration z (m/s^2)"'
    android_g = '"Time (s)","Gyroscope x (rad/s)","Gyroscope y (rad/s)","Gyroscope z (rad/s)"'
    cases = {
        "missing_accelerometer": {"Gyroscope.csv": csv_text(GYRO_HEADER, ok_g)},
        "missing_gyroscope": {"Accelerometer.csv": csv_text(ACCEL_HEADER, ok_a)},
        "empty_zip": {"readme.txt": "nothing here"},
        "members_only_in_subfolder": {"exp/Accelerometer.csv": csv_text(ACCEL_HEADER, ok_a),
                                      "exp/Gyroscope.csv": csv_text(GYRO_HEADER, ok_g)},
        "member_name_wrong_case": {"accelerometer.csv": csv_text(ACCEL_HEADER, ok_a),
                                   "gyroscope.csv": csv_text(GYRO_HEADER, ok_g)},
        "semicolon_decimal_comma_export": _valid_members(**{"Accelerometer.csv": semi_a}),
        "android_header_accelerometer": _valid_members(**{"Accelerometer.csv": csv_text(android_a, ok_a)}),
        "android_header_gyroscope": _valid_members(**{"Gyroscope.csv": csv_text(android_g, ok_g)}),
        "gyro_header_with_accel_units": _valid_members(**{"Gyroscope.csv": csv_text(ACCEL_HEADER, ok_g)}),
        "accel_header_with_gyro_units": _valid_members(**{"Accelerometer.csv": csv_text(GYRO_HEADER, ok_a)}),
        "header_missing_column": _valid_members(**{"Accelerometer.csv": csv_text("Time (s),X (m/s^2),Y (m/s^2)", ok_a)}),
        "header_extra_column": _valid_members(**{
            "Accelerometer.csv": csv_text(ACCEL_HEADER + ",W (m/s^2)", ok_a)}),
        "header_columns_swapped": _valid_members(**{
            "Accelerometer.csv": csv_text("Time (s),Y (m/s^2),X (m/s^2),Z (m/s^2)", ok_a)}),
        "no_header_data_first": _valid_members(**{"Accelerometer.csv": "\n".join(",".join(r) for r in ok_a) + "\n"}),
        "row_with_3_fields": _valid_members(**{
            "Accelerometer.csv": csv_text(ACCEL_HEADER, [ok_a[0], ok_a[1][:3], ok_a[2], ok_a[3]])}),
        "row_with_5_fields": _valid_members(**{
            "Gyroscope.csv": csv_text(GYRO_HEADER, [ok_g[0], ok_g[1] + ["1.0E0"], ok_g[2]])}),
        "non_numeric_cell": _valid_members(**{
            "Accelerometer.csv": csv_text(ACCEL_HEADER, [ok_a[0], ["1.1E-2", "abc", "0.0", "9.8"], ok_a[2]])}),
        "non_numeric_time": _valid_members(**{
            "Gyroscope.csv": csv_text(GYRO_HEADER, [ok_g[0], ["x", "0.0", "0.0", "0.0"], ok_g[2]])}),
        "empty_cell": _valid_members(**{
            "Accelerometer.csv": csv_text(ACCEL_HEADER, [ok_a[0], ["1.1E-2", "", "0.0", "9.8"], ok_a[2]])}),
        "nan_value": _valid_members(**{
            "Accelerometer.csv": csv_text(ACCEL_HEADER, [ok_a[0], ["1.1E-2", "nan", "0.0", "9.8"], ok_a[2]])}),
        "inf_value": _valid_members(**{
            "Gyroscope.csv": csv_text(GYRO_HEADER, [ok_g[0], ["1.2E-2", "inf", "0.0", "0.0"], ok_g[2]])}),
        "inf_time": _valid_members(**{
            "Gyroscope.csv": csv_text(GYRO_HEADER, [ok_g[0], ok_g[1], ["inf", "0.0", "0.0", "0.0"]])}),
        "only_one_data_row_accel": _valid_members(**{"Accelerometer.csv": csv_text(ACCEL_HEADER, ok_a[:1])}),
        "only_one_data_row_gyro": _valid_members(**{"Gyroscope.csv": csv_text(GYRO_HEADER, ok_g[:1])}),
        "no_data_rows_accel": _valid_members(**{"Accelerometer.csv": csv_text(ACCEL_HEADER, [])}),
        "no_data_rows_gyro": _valid_members(**{"Gyroscope.csv": ""}),
        "repeated_timestamp_accel": _valid_members(**{
            "Accelerometer.csv": csv_text(ACCEL_HEADER, [ok_a[0], ok_a[1], ok_a[1], ok_a[3]])}),
        "repeated_timestamp_gyro": _valid_members(**{
            "Gyroscope.csv": csv_text(GYRO_HEADER, [ok_g[0], ok_g[1], ok_g[1]])}),
        "decreasing_time": _valid_members(**{
            "Accelerometer.csv": csv_text(ACCEL_HEADER, [ok_a[1], ok_a[0], ok_a[2], ok_a[3]])}),
    }
    return cases


BAD_ZIPS = _bad_zip_cases()


@pytest.mark.parametrize("members", list(BAD_ZIPS.values()), ids=list(BAD_ZIPS))
def test_RL2_bad_zip_content_raises_value_error(tmp_path, members):
    path = write_zip(tmp_path / "bad.zip", members)
    with pytest.raises(ValueError):
        imu_io.load_phyphox_zip(path)


def test_RL2_not_a_zip_file(tmp_path):
    p = tmp_path / "not_a_zip.zip"
    p.write_text("this is plain text, not a zip archive")
    with pytest.raises(ValueError):
        imu_io.load_phyphox_zip(str(p))
    empty = tmp_path / "empty.zip"
    empty.write_bytes(b"")
    with pytest.raises(ValueError):
        imu_io.load_phyphox_zip(str(empty))


def test_RL2_missing_file_raises_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        imu_io.load_phyphox_zip(str(tmp_path / "does_not_exist.zip"))
    with pytest.raises(FileNotFoundError):
        imu_io.load_phyphox_zip(tmp_path / "does_not_exist_either.zip")


def test_RL2_pathlib_path_is_accepted(tmp_path):
    path = write_zip(tmp_path / "rec.zip", _valid_members())
    from pathlib import Path
    rec = imu_io.load_phyphox_zip(Path(path))
    _check_values(rec)


# ---------------------------------------------------------------- RL3
def _linear_signals(t, offset):
    a = np.column_stack([1.0 + 2.0 * t, -3.0 + 0.5 * t, 9.81 - 0.25 * t])
    g = np.column_stack([0.1 * t, 0.2 - 0.05 * t, -0.3 + 0.01 * t])
    return a, g


def test_RL3_linear_signals_resample_exactly_with_offset_clocks():
    gyro_t = np.arange(0.0, 10.0, 0.01)
    accel_t = gyro_t + 0.005                                   # accelerometer clock is +5 ms
    accel, _ = _linear_signals(accel_t, 0)
    _, gyro = _linear_signals(gyro_t, 0)
    fs = 100.0
    t, gyro_rs, accel_rs = imu_io.resample_common(accel_t, accel, gyro_t, gyro, fs=fs)
    t0, t1 = max(accel_t[0], gyro_t[0]), min(accel_t[-1], gyro_t[-1])
    n_expected = int(math.floor((t1 - t0) * fs + 1e-9)) + 1
    assert t.shape == (n_expected,) and gyro_rs.shape == (n_expected, 3) and accel_rs.shape == (n_expected, 3)
    for arr in (t, gyro_rs, accel_rs):
        assert arr.dtype == np.float64
    assert t[0] == t0 == 0.005                                  # starts at the later first timestamp
    np.testing.assert_allclose(np.diff(t), 1.0 / fs, rtol=0, atol=1e-12)
    assert t[-1] <= t1
    assert t[-1] + 1.0 / fs > t1 - 1e-9                          # the grid reaches the end of the overlap
    a_exact, g_exact = _linear_signals(t, 0)
    np.testing.assert_allclose(accel_rs, a_exact, rtol=0, atol=1e-12)
    np.testing.assert_allclose(gyro_rs, g_exact, rtol=0, atol=1e-12)


def test_RL3_return_order_is_time_gyro_accel():
    t_g = np.linspace(0.0, 2.0, 41)
    t_a = np.linspace(0.0, 2.0, 81)
    accel = np.column_stack([np.full(81, 1.0), np.full(81, 2.0), np.full(81, 3.0)])
    gyro = np.column_stack([np.full(41, 10.0), np.full(41, 20.0), np.full(41, 30.0)])
    t, gyro_rs, accel_rs = imu_io.resample_common(t_a, accel, t_g, gyro, fs=50.0)
    np.testing.assert_allclose(gyro_rs, [10.0, 20.0, 30.0] + np.zeros((t.size, 3)), rtol=0, atol=1e-12)
    np.testing.assert_allclose(accel_rs, [1.0, 2.0, 3.0] + np.zeros((t.size, 3)), rtol=0, atol=1e-12)


@pytest.mark.parametrize("fs", [100.0, 50.0, 37.0])
def test_RL3_non_uniform_timestamps_and_other_rates(fs):
    rng = np.random.default_rng(11)
    gyro_t = np.sort(rng.uniform(0.3, 20.0, 1500))
    accel_t = np.sort(rng.uniform(0.1, 19.7, 1700))
    accel, _ = _linear_signals(accel_t, 0)
    _, gyro = _linear_signals(gyro_t, 0)
    t, gyro_rs, accel_rs = imu_io.resample_common(accel_t, accel, gyro_t, gyro, fs=fs)
    t0, t1 = max(accel_t[0], gyro_t[0]), min(accel_t[-1], gyro_t[-1])
    assert t[0] == t0
    assert t.size == int(math.floor((t1 - t0) * fs + 1e-9)) + 1
    np.testing.assert_allclose(np.diff(t), 1.0 / fs, rtol=0, atol=1e-12)
    assert t[-1] <= t1 + 1e-12
    np.testing.assert_allclose(accel_rs, _linear_signals(t, 0)[0], rtol=0, atol=1e-12)
    np.testing.assert_allclose(gyro_rs, _linear_signals(t, 0)[1], rtol=0, atol=1e-12)


def test_RL3_extra_grid_length_guard_for_float_rounding():
    # (0.3 - 0.1) * 100 evaluates to 19.999999999999996; the +1e-9 in the spec keeps k = 20
    t_ax = np.array([0.1, 0.2, 0.3])
    a = np.zeros((3, 3))
    t, _, _ = imu_io.resample_common(t_ax, a, t_ax, a, fs=100.0)
    assert t.shape == (21,)
    t_ax = np.linspace(0.0, 1.0, 11)
    t, _, _ = imu_io.resample_common(t_ax, np.zeros((11, 3)), np.linspace(0, 1, 21), np.zeros((21, 3)), fs=100.0)
    assert t.shape == (101,)


def _rs_bad_calls():
    t = np.linspace(0.0, 1.0, 11)
    z = np.zeros((11, 3))
    R = imu_io.resample_common
    t_rep = t.copy(); t_rep[4] = t_rep[3]
    t_dec = t[::-1].copy()
    return {
        "fs_zero": lambda: R(t, z, t, z, fs=0.0),
        "fs_negative": lambda: R(t, z, t, z, fs=-100.0),
        "accel_two_columns": lambda: R(t, np.zeros((11, 2)), t, z),
        "gyro_two_columns": lambda: R(t, z, t, np.zeros((11, 2))),
        "accel_one_dimensional": lambda: R(t, np.zeros(11), t, z),
        "accel_length_mismatch": lambda: R(t, np.zeros((10, 3)), t, z),
        "gyro_length_mismatch": lambda: R(t, z, t, np.zeros((10, 3))),
        "accel_t_repeated": lambda: R(t_rep, z, t, z),
        "gyro_t_repeated": lambda: R(t, z, t_rep, z),
        "accel_t_decreasing": lambda: R(t_dec, z, t, z),
        "gyro_t_decreasing": lambda: R(t, z, t_dec, z),
        "no_overlap": lambda: R(t, z, t + 5.0, z),
        "overlap_shorter_than_one_sample": lambda: R(t, z, t - 0.995, z, fs=100.0),   # M = 1
        "single_grid_point_exact_touch": lambda: R(t, z, t + 1.0, z),
    }


RS_BAD = _rs_bad_calls()


@pytest.mark.parametrize("call", list(RS_BAD.values()), ids=list(RS_BAD))
def test_RL3_value_errors(call):
    with pytest.raises(ValueError):
        call()


# ================================================================== real recordings
RECORDINGS = ["A", "B"]


def _end_window(t):
    return (t >= t[-1] - 7.0) & (t <= t[-1] - 1.0)


def _rest_window(r):
    t = r.t
    return (t >= t[0] + 1.0) & (t <= t[0] + 7.0)


@pytest.mark.parametrize("name", RECORDINGS)
def test_RR1_recordings_load_and_have_expected_sampling(name):
    r = real_run(name)
    rec = r.rec
    assert rec.accel_t.size >= 5000 and rec.gyro_t.size >= 5000
    for ts in (rec.accel_t, rec.gyro_t):
        assert abs(np.median(np.diff(ts)) - 0.01) <= 0.02 * 0.01
    assert r.t[-1] - r.t[0] >= 55.0


@pytest.mark.parametrize("name", RECORDINGS)
def test_RR2_rest_window_statistics(name):
    r = real_run(name)
    est = r.est
    assert abs(est.gravity - 9.81) <= 0.2
    window = _rest_window(r)
    assert window.sum() >= 10
    per_axis_std = np.std(r.gyro[window], axis=0, ddof=1)
    assert np.all(per_axis_std <= 0.01), per_axis_std
    assert np.all(np.abs(est.gyro_bias) <= 0.01), est.gyro_bias
    assert est.accel_noise_std <= 0.05


@pytest.mark.parametrize("angle", [0, 1], ids=["roll", "pitch"])
def test_RR3_gyro_integration_agrees_with_accelerometer_tilt_recording_A(angle):
    r = real_run("A")
    roll_g, pitch_g = F.complementary_roll_pitch(r.t, r.gyro, r.accel, tau=1e9, gyro_bias=r.est.gyro_bias)
    roll_a, pitch_a = F.accel_tilt(r.accel)
    gyro_angle = (roll_g, pitch_g)[angle]
    accel_angle = (roll_a, pitch_a)[angle]
    corr = np.corrcoef(gyro_angle, accel_angle)[0, 1]
    assert corr >= 0.9, "Pearson r = %.3f" % corr


@pytest.mark.parametrize("name", RECORDINGS)
@pytest.mark.parametrize("angle", [0, 1], ids=["roll", "pitch"])
def test_RR4_end_position_matches_start_position(name, angle):
    r = real_run(name)
    est = r.kfg.roll if angle == 0 else r.kfg.pitch
    end = np.rad2deg(np.mean(est[_end_window(r.t)]))
    start = np.rad2deg(np.mean(est[_rest_window(r)]))
    assert abs(end - start) <= 2.0, "start %.2f deg, end %.2f deg" % (start, end)


@pytest.mark.parametrize("name", RECORDINGS)
@pytest.mark.parametrize("angle", [0, 1], ids=["roll", "pitch"])
def test_RR5_filter_agrees_with_accelerometer_in_the_end_window(name, angle):
    r = real_run(name)
    est = r.kfg.roll if angle == 0 else r.kfg.pitch
    acc = F.accel_tilt(r.accel)[angle]
    window = _end_window(r.t)
    assert window.sum() >= 100
    diff = np.rad2deg(np.mean(est[window]) - np.mean(acc[window]))
    assert abs(diff) <= 1.0, "difference %.3f deg" % diff


def test_RR_extra_both_real_files_are_present():
    missing = [str(p) for p in REAL_FILES.values() if not p.exists()]
    assert not missing, "missing real recordings: %s" % missing


def test_RR_extra_real_zip_has_the_required_members():
    for name, path in REAL_FILES.items():
        assert path.exists(), "missing %s" % path
        with zipfile.ZipFile(str(path)) as zf:
            names = zf.namelist()
        assert "Accelerometer.csv" in names and "Gyroscope.csv" in names, (name, names)
