"""Kiểm thử phát triển: nhãn, ranh giới thời gian và đánh giá ML."""

import numpy as np
import pandas as pd
from src import sp500_analysis as ml


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


def test_supplemental_metrics():
    captured = {}
    original = ml.save_ml_table
    ml.save_ml_table = lambda frame, name: captured.update({name: frame.copy()})
    y = np.array([0, 1, 0, 1])
    predictions = pd.DataFrame({
        "label": y, "target_date": ["2017-01-03", "2017-01-03", "2017-01-04", "2017-01-04"],
        "baseline_prediction": [1, 1, 1, 1], "logistic_prediction": [0, 1, 0, 0],
        "forest_prediction": [1, 1, 1, 1],
    })
    rows, matrices = [], []
    for name, field in zip(["baseline_majority", "logistic_regression", "random_forest"],
                           ["baseline_prediction", "logistic_prediction", "forest_prediction"]):
        row, counts = ml.evaluate_predictions(name, y, np.array(predictions[field]), None, 10, 6)
        rows.append(row)
        matrices.append(counts)
    result, normalized = ml.build_ml_supplements(pd.DataFrame(rows), pd.DataFrame(matrices), predictions)
    logistic = result[result["model"] == "logistic_regression"]
    assert int(np.array(logistic["correct_predictions"])[0]) == 3
    assert int(np.array(logistic["correct_difference_vs_baseline"])[0]) == 1
    assert np.array(logistic["balanced_accuracy"])[0] == 0.75
    assert np.array(logistic["specificity_0"])[0] == 1.0
    assert abs(np.array(logistic["accuracy_se_iid"])[0] - np.sqrt(0.75 * 0.25 / 4)) < 1e-12
    assert np.array(logistic["accuracy_se_date_cluster"])[0] == 0.25
    assert np.array(logistic["accuracy_difference_se_date_cluster"])[0] == 0.25
    assert int(np.array(logistic["target_dates"])[0]) == 2
    baseline = result[result["model"] == "baseline_majority"]
    assert np.array(baseline["accuracy_difference_se_date_cluster"])[0] == 0
    assert np.array(logistic["accuracy_ci95_iid_high"])[0] == 1.0
    for _, part in normalized.groupby(["model", "actual_label"]):
        assert abs(part["row_normalized_rate"].sum() - 1) < 1e-12
    assert len(captured["ml_daily_evaluation"]) == 6
    ml.save_ml_table = original


if __name__ == "__main__":
    test_samples()
    test_metrics()
    test_supplemental_metrics()
    print("PASS: nhãn, phiên liền kề, ranh giới train/test, volume và chỉ số ML.")
