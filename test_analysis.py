"""Kiểm tra phát triển: chạy python test_analysis.py; không là nội dung bài giảng.

Các fixture kiểm tra ý nghĩa tài chính và lỗi dữ liệu, không chỉ so lại code.
Không ghi đè outputs: thay hàm lưu CSV bằng bộ thu bảng trong bộ nhớ.
"""

import numpy as np
import pandas as pd
import sp500_analysis as analysis


def test_return_semantics():
    close = np.array([100.0, 110.0, 99.0, 108.9])
    result = analysis.price_metrics(close, np.array([0, 1, 2, 3]), np.array([0, 1, 4, 5]))
    observed, daily, gaps, cumulative, average, volatility, cagr = result
    assert np.isnan(daily[0])
    assert np.abs(daily[1:] - np.array([0.1, -0.1, 0.1])).max() < 1e-12
    assert np.abs(cumulative[-1] - 0.089) < 1e-12
    assert np.abs(average - 1 / 30) < 1e-12
    assert np.abs(volatility - np.sqrt(0.00888888888888889)) < 1e-12
    assert np.abs(cagr - (1.089 ** (365.25 / 5) - 1)) < 1e-8
    assert not gaps.any()
    # Phiên bị thiếu không được biến thành một daily return giả.
    result = analysis.price_metrics(np.array([100.0, 110.0, 121.0]),
                                    np.array([0, 1, 3]), np.array([0, 1, 5]))
    assert np.isnan(result[1][2]) and result[2][2]
    assert np.abs(result[0][2] - 0.1) < 1e-12
    assert np.abs(result[3][-1] - 0.21) < 1e-12
    single = analysis.price_metrics(np.array([50.0]), np.array([0]), np.array([0]))
    assert np.isnan(single[4]) and np.isnan(single[5]) and np.isnan(single[6])


def test_cleaning_and_groups():
    saved = {}
    original_save = analysis.save_table

    def capture(frame, name):
        saved[name] = frame.copy()

    analysis.save_table = capture
    nan = float("nan")
    columns = ["symbol", "date", "open", "high", "low", "close", "volume"]
    raw = pd.DataFrame([
        [" a ", "2014-01-02", 100, 105, 95, 100, 10],
        ["A", "2014-01-02", 100, 105, 95, 100, 10],  # duplicate after normalization
        ["A", "2014-01-03", 110, 115, 105, 110, 10],
        ["A", "2014-01-07", 121, 125, 115, 121, 10],
        ["B", "2014-01-02", nan, nan, nan, 50, -5],  # valid close remains
        ["B", "2014-01-03", 50, 52, 49, 55, 10],  # inconsistent OHLC
        ["C", "2014-01-02", 1, 2, 0, 0, 10],  # invalid close
        ["D", "2014-01-02", 10, 12, 8, 10, 10],
        ["D", "2014-01-02", 10, 12, 8, 11, 10],  # conflicting key: both excluded
        ["E", "bad-date", 10, 12, 8, 10, 10],
        ["F", "2014-01-06", 10, 12, 8, nan, 10],  # keeps Jan 6 in calendar
        [" ", "2014-01-02", 10, 12, 8, 10, 10],
    ], columns=columns)
    before = raw.copy()
    clean, audit, calendar, steps = analysis.clean_data(raw)
    assert len(clean) == 4
    assert list(clean["symbol"]) == ["A", "A", "A", "B"]
    assert len(calendar) == 4
    assert list(clean["session_id"]) == [0, 1, 3, 0]
    assert not bool(np.array(clean["complete_ohlcv"])[-1])
    assert int(steps["removed"].sum()) + len(clean) == len(raw)
    assert int(clean.duplicated(subset=["symbol", "date"]).sum()) == 0
    assert list(raw["symbol"]) == list(before["symbol"])
    metrics, daily = analysis.analyze_prices(clean, calendar)
    assert not np.array(metrics["eligible"]).any()
    a_daily = np.array(daily[daily["symbol"] == "A"]["daily_return"])
    assert np.isnan(a_daily[-1])
    # Không được nối lợi suất từ cuối A sang đầu B.
    assert np.isnan(np.array(daily[daily["symbol"] == "B"]["daily_return"])[0])
    sample = pd.DataFrame({"symbol": ["A", "B", "C", "D"], "eligible": [True] * 4,
                           "cagr": [0.1, 0.3, 0.1, 0.3], "daily_volatility": [0.01, 0.01, 0.03, 0.03]})
    groups, summary, selected, thresholds = analysis.group_stocks(sample)
    assert list(groups["group"]) == ["C", "A", "D", "B"]
    assert int(summary["stocks"].sum()) == 4
    tied = pd.DataFrame({"symbol": ["A", "B", "C"], "eligible": [True] * 3,
                         "cagr": [0.2] * 3, "daily_volatility": [0.02] * 3})
    groups, _, selected, _ = analysis.group_stocks(tied)
    assert list(groups["group"]) == ["B", "B", "B"]
    assert list(selected["symbol"]) == ["A", "C"]
    analysis.save_table = original_save


if __name__ == "__main__":
    test_return_semantics()
    test_cleaning_and_groups()
    print("PASS: công thức, khoảng thiếu phiên, tách mã, làm sạch, độ phủ, phân nhóm và hòa ngưỡng.")
