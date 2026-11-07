"""Kiểm thử phát triển: nhãn, ranh giới thời gian và đánh giá ML."""

import numpy as np
import pandas as pd
from src import sp500_ml as ml


def test_samples():
    captured = {}
    original = ml.save_ml_table
    ml.save_ml_table = lambda frame, name: captured.update({name: frame.copy()})
    dates = ["2016-12-28", "2016-12-29", "2016-12-30",
             "2017-01-03", "2017-01-04", "2017-01-05"]
    rows = []
    for symbol, prices, volumes in [
            ("A", [100, 102, 101, 103, 104, 102], [10] * 6),
            ("B", [50, 49, 51, 50, 52, 53], [0, 10, 0, 10, 10, 10])]:
        for i, day in enumerate(dates):
            rows.append({"symbol": symbol, "date": day, "session_id": i,
                         "open": prices[i], "high": prices[i] + 1,
                         "low": prices[i] - 1, "close": prices[i],
                         "volume": volumes[i], "complete_ohlcv": True})
    rows.append({"symbol": "C", "date": "2016-12-28", "session_id": 0,
                 "open": 20, "high": 21, "low": 19, "close": 20,
                 "volume": 10, "complete_ohlcv": True})
    rows.append({"symbol": "C", "date": "2016-12-30", "session_id": 2,
                 "open": 22, "high": 23, "low": 21, "close": 22,
                 "volume": 10, "complete_ohlcv": True})
    train, test, audit = ml.build_ml_samples(pd.DataFrame(rows))
    assert list(train["symbol"]) == ["A"]
    assert list(train["date"]) == [pd.Timestamp("2016-12-29")]
    assert list(train["target_date"]) == [pd.Timestamp("2016-12-30")]
    assert list(train["label"]) == [0]
    assert list(test["symbol"]) == ["A", "A", "B"]
    assert list(test["label"]) == [1, 0, 1]
    assert all(test["date"] >= pd.Timestamp("2017-01-01"))
    assert all(train["target_date"] < pd.Timestamp("2017-01-01"))
    assert int(audit["cross_period_boundary"].sum()) >= 1
    assert int(audit["invalid_previous_volume"].sum()) >= 1
    assert int(audit["no_adjacent_target"].sum()) >= 1
    assert int(audit["no_adjacent_previous"].sum()) >= 1
    assert int(np.array(train["return_1d_t"])[0] * 100) == 2
    ml.save_ml_table = original


def test_metrics():
    y_true = np.array([0, 1, 1, 0])
    predicted = np.array([0, 1, 0, 0])
    row, counts = ml.evaluate_predictions("fixture", y_true, predicted,
                                           np.array([0.1, 0.9, 0.4, 0.2]), 10, 6)
    assert counts == {"model": "fixture", "tn": 2, "fp": 0, "fn": 1, "tp": 1}
    assert row["accuracy"] == 0.75
    assert row["precision_1"] == 1.0
    assert row["recall_1"] == 0.5
    assert abs(row["f1_1"] - 2 / 3) < 1e-12
    assert row["roc_auc"] == 1.0
    baseline, _ = ml.evaluate_predictions("baseline", y_true, np.zeros(4, dtype=int), None, 10, 6)
    assert baseline["precision_1"] == 0 and baseline["f1_1"] == 0
    assert np.isnan(baseline["roc_auc"])


if __name__ == "__main__":
    test_samples()
    test_metrics()
    print("PASS: nhãn, phiên liền kề, ranh giới train/test, volume và chỉ số ML.")
