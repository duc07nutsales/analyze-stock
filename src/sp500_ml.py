"""Thử nghiệm phân loại chiều close phiên kế tiếp bằng dữ liệu giá có sẵn.

Code ML dùng các hàm trong allowed_knowledge_reference.md. Không gọi API.
Chạy qua sp500_analysis.py hoặc notebook để dùng cùng bản clean và báo cáo.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.metrics import confusion_matrix, roc_auc_score

from src.analysis_config import OUTPUT_DIR, ML_RANDOM_STATE, ML_N_TREES, ML_MAX_ITER


FEATURES = ["return_1d_t", "range_t", "intraday_t", "volume_t", "volume_change_t"]


def save_ml_table(frame, name):
    frame.to_csv(f"{OUTPUT_DIR}/tables/{name}.csv", index=False, encoding="utf-8-sig")


def build_ml_samples(clean):
    """Tạo mẫu theo từng mã; không dùng bộ lọc CAGR/độ phủ toàn kỳ.

    Cột `reason` cho biết vì sao từng dòng clean có/không có mẫu ML.
    Chỉ `label` dùng giá t+1; FEATURES chỉ dùng dữ liệu tới cuối t.
    """
    ordered = clean.set_index(["symbol", "date"]).sort_index().reset_index()
    blocks = []
    cutoff = pd.to_datetime("2017-01-01")
    for symbol, part in ordered.groupby("symbol"):
        part = part.copy()
        n = len(part)
        dates = np.array(part["date"], dtype="datetime64[ns]")
        sessions = np.array(part["session_id"], dtype=int)
        close = np.array(part["close"], dtype=float)
        open_price = np.array(part["open"], dtype=float)
        high = np.array(part["high"], dtype=float)
        low = np.array(part["low"], dtype=float)
        volume = np.array(part["volume"], dtype=float)
        complete = np.array(part["complete_ohlcv"], dtype=bool)

        previous_close = np.full(n, float("nan"))
        previous_volume = np.full(n, float("nan"))
        previous_sessions = np.full(n, -1)
        next_close = np.full(n, float("nan"))
        next_sessions = np.full(n, -1)
        target_dates = dates.copy()
        if n > 1:
            previous_close[1:] = close[:-1]
            previous_volume[1:] = volume[:-1]
            previous_sessions[1:] = sessions[:-1]
            next_close[:-1] = close[1:]
            next_sessions[:-1] = sessions[1:]
            target_dates[:-1] = dates[1:]

        previous_adjacent = sessions - previous_sessions == 1
        next_adjacent = next_sessions - sessions == 1
        previous_adjacent[0] = False
        next_adjacent[-1] = False
        previous_volume_ok = np.isfinite(previous_volume) & (previous_volume > 0)
        denominator_close = np.where(previous_close > 0, previous_close, 1.0)
        denominator_volume = np.where(previous_volume_ok, previous_volume, 1.0)
        denominator_open = np.where(open_price > 0, open_price, 1.0)
        return_1d = np.where(previous_adjacent, close / denominator_close - 1, float("nan"))
        range_today = (high - low) / denominator_open
        intraday = (close - open_price) / denominator_open
        volume_change = np.where(previous_adjacent & previous_volume_ok,
                                 volume / denominator_volume - 1, float("nan"))
        label = np.where(next_adjacent, np.where(next_close > close, 1, 0), -1)

        before = dates < cutoff
        next_before = target_dates < cutoff
        same_period = (before & next_before) | (~before & ~next_before)
        period = np.where(before, "train_2014_2016", "test_2017")
        reason = np.full(n, "included", dtype=object)
        reason = np.where(~next_adjacent, "no_adjacent_target", reason)
        reason = np.where((reason == "included") & ~previous_adjacent,
                          "no_adjacent_previous", reason)
        reason = np.where((reason == "included") & ~complete,
                          "incomplete_current_ohlcv", reason)
        reason = np.where((reason == "included") & ~previous_volume_ok,
                          "invalid_previous_volume", reason)
        finite_features = (np.isfinite(return_1d) & np.isfinite(range_today)
                           & np.isfinite(intraday) & np.isfinite(volume)
                           & np.isfinite(volume_change))
        reason = np.where((reason == "included") & ~finite_features,
                          "nonfinite_feature", reason)
        reason = np.where((reason == "included") & ~same_period,
                          "cross_period_boundary", reason)
        blocks.append(pd.DataFrame({
            "symbol": symbol, "date": dates, "target_date": target_dates,
            "session_id": sessions, "target_session_id": next_sessions,
            "label": label, "return_1d_t": return_1d, "range_t": range_today,
            "intraday_t": intraday, "volume_t": volume,
            "volume_change_t": volume_change, "period": period, "reason": reason,
        }))

    candidates = pd.concat(blocks, axis=0).reset_index(drop=True)
    audit = pd.crosstab(candidates["period"], candidates["reason"]).reset_index()
    save_ml_table(audit, "ml_sample_audit")
    samples = candidates[candidates["reason"] == "included"].copy()
    train = samples[samples["period"] == "train_2014_2016"].copy()
    test = samples[samples["period"] == "test_2017"].copy()
    print("Mẫu ML train/test:", len(train), len(test))
    print(audit)
    return train, test, audit


def evaluate_predictions(name, y_true, y_pred, y_score, n_train, train_positive):
    matrix = confusion_matrix(y_true, y_pred)
    tn, fp = int(matrix[0, 0]), int(matrix[0, 1])
    fn, tp = int(matrix[1, 0]), int(matrix[1, 1])
    precision = float(precision_score(y_true, y_pred, pos_label=1)) if tp + fp > 0 else 0.0
    recall = float(recall_score(y_true, y_pred, pos_label=1)) if tp + fn > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0.0
    auc = float(roc_auc_score(y_true, y_score)) if y_score is not None else float("nan")
    metrics = {"model": name, "train_samples": n_train, "test_samples": len(y_true),
               "train_positive_rate": train_positive / n_train,
               "test_positive_rate": int((y_true == 1).sum()) / len(y_true),
               "accuracy": float(accuracy_score(y_true, y_pred)),
               "precision_1": precision, "recall_1": recall,
               "f1_1": f1, "roc_auc": auc}
    counts = {"model": name, "tn": tn, "fp": fp, "fn": fn, "tp": tp}
    return metrics, counts


def fit_and_evaluate(train, test):
    x_train = np.array(train[FEATURES], dtype=float)
    x_test = np.array(test[FEATURES], dtype=float)
    y_train = np.array(train["label"], dtype=int)
    y_test = np.array(test["label"], dtype=int)
    if len(train) == 0 or len(test) == 0 or len(np.unique(y_train)) < 2 or len(np.unique(y_test)) < 2:
        print("Dừng ML: cần mẫu train/test và cả hai lớp 0/1 trong mỗi tập.")
        return None
    if not np.isfinite(x_train).all() or not np.isfinite(x_test).all():
        print("Dừng ML: còn đặc trưng không hữu hạn.")
        return None

    positives = int((y_train == 1).sum())
    negatives = int((y_train == 0).sum())
    baseline_label = 1 if positives > negatives else 0
    baseline_pred = np.full(len(y_test), baseline_label)

    scaler = StandardScaler()
    scaled_train = scaler.fit_transform(x_train)
    scaled_test = scaler.transform(x_test)
    logistic = LogisticRegression(max_iter=ML_MAX_ITER, random_state=ML_RANDOM_STATE)
    logistic.fit(scaled_train, y_train)
    logistic_pred = logistic.predict(scaled_test)
    logistic_score = logistic.predict_proba(scaled_test)[:, 1]

    forest = RandomForestClassifier(n_estimators=ML_N_TREES, random_state=ML_RANDOM_STATE)
    forest.fit(x_train, y_train)
    forest_pred = forest.predict(x_test)
    forest_score = forest.predict_proba(x_test)[:, 1]

    rows, matrices = [], []
    for name, prediction, score in [
            ("baseline_majority", baseline_pred, None),
            ("logistic_regression", logistic_pred, logistic_score),
            ("random_forest", forest_pred, forest_score)]:
        row, matrix = evaluate_predictions(name, y_test, prediction, score, len(y_train), positives)
        rows.append(row)
        matrices.append(matrix)
    metrics = pd.DataFrame(rows)
    confusion = pd.DataFrame(matrices)
    predictions = test[["symbol", "date", "target_date", "label"]].copy()
    predictions["baseline_prediction"] = baseline_pred
    predictions["logistic_prediction"] = logistic_pred
    predictions["forest_prediction"] = forest_pred
    predictions["logistic_probability_up"] = logistic_score
    predictions["forest_probability_up"] = forest_score
    save_ml_table(metrics, "ml_metrics")
    save_ml_table(confusion, "ml_confusion_matrices")
    save_ml_table(predictions, "ml_test_predictions")
    print(metrics)
    return metrics, confusion, predictions


def plot_ml_results(metrics, confusion):
    names = ["Baseline", "Logistic", "Random Forest"]
    fields = [("accuracy", "Accuracy"), ("precision_1", "Precision lớp tăng"),
              ("recall_1", "Recall lớp tăng"), ("f1_1", "F1 lớp tăng")]
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    for i, (field, title) in enumerate(fields):
        ax = axes[i // 2, i % 2]
        ax.bar(names, np.array(metrics[field]), color=["#777777", "#087f8c", "#df7b27"])
        ax.set_title(title)
        ax.set_xlabel("Cách dự đoán")
        ax.set_ylabel("Tỷ lệ (0–1)")
        ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/figures/ml_metric_comparison.png", dpi=160)

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for i, name in enumerate(names):
        ax = axes[i]
        counts = np.array(confusion[["tn", "fp", "fn", "tp"]])[i]
        ax.bar(["TN", "FP", "FN", "TP"], counts,
               color=["#4c6fb5", "#df7b27", "#ad4668", "#087f8c"])
        ax.set_title(name)
        ax.set_xlabel("Ô confusion matrix")
        ax.set_ylabel("Số mẫu test")
        ax.set_ylim(bottom=0)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/figures/ml_confusion_matrices.png", dpi=160)


def ml_markdown(train, test, audit, metrics, confusion):
    rows = []
    for model, n_train, n_test, accuracy, precision, recall, f1, auc in zip(
            metrics["model"], metrics["train_samples"], metrics["test_samples"],
            metrics["accuracy"], metrics["precision_1"], metrics["recall_1"],
            metrics["f1_1"], metrics["roc_auc"]):
        auc_text = f"{auc:.4f}" if np.isfinite(auc) else "N/A"
        rows.append(f"| {model} | {n_train:,} | {n_test:,} | {accuracy:.4f} | "
                    f"{precision:.4f} | {recall:.4f} | {f1:.4f} | {auc_text} |")
    base_accuracy = np.array(metrics["accuracy"])[0]
    logistic_gain = np.array(metrics["accuracy"])[1] - base_accuracy
    forest_gain = np.array(metrics["accuracy"])[2] - base_accuracy
    if logistic_gain <= 0 and forest_gain <= 0:
        comparison = "Trong lần kiểm tra này, cả hai mô hình đều không vượt baseline về Accuracy. "
    else:
        comparison = "Ít nhất một mô hình vượt baseline về Accuracy trong lần kiểm tra này. "
    train_rate = int((np.array(train["label"]) == 1).sum()) / len(train)
    test_rate = int((np.array(test["label"]) == 1).sum()) / len(test)
    text = (
        "\n\n## 7. Thử nghiệm học máy: chiều giá phiên kế tiếp\n\n"
        "**Câu hỏi:** Dữ liệu OHLCV đã biết cuối phiên `t` có giúp dự đoán close phiên kế tiếp "
        "cùng mã tăng (`1`) hay không tăng (`0`) không? Đây là phân loại chiều giá, không dự báo mức giá.\n\n"
        "Nhãn chỉ gắn khi có phiên liền kề cùng mã. Năm đặc trưng: daily return hiện tại, "
        "`(high-low)/open`, `(close-open)/open`, volume hiện tại, thay đổi volume so với phiên trước. "
        "Không dùng dữ liệu `t+1` trong đặc trưng. Không lọc mã theo kết quả CAGR hoặc độ phủ của cả kỳ. "
        "Train dùng mẫu có cả `t` và ngày nhãn trong 2014–2016; test dùng cả hai trong 2017. "
        "Scaler chỉ fit trên train. Random Forest dùng đặc trưng gốc.\n\n"
        f"Tập train có **{len(train):,} mẫu**, tỷ lệ tăng **{train_rate:.2%}**; "
        f"test có **{len(test):,} mẫu**, tỷ lệ tăng **{test_rate:.2%}**. "
        "Xem `tables/ml_sample_audit.csv` để biết số mẫu loại theo lý do. "
        "Baseline luôn đoán nhãn đa số của train.\n\n"
        "![So sánh chỉ số ML](figures/ml_metric_comparison.png)\n\n"
        "| Mô hình | Train | Test | Accuracy | Precision 1 | Recall 1 | F1 1 | ROC-AUC |\n"
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n"
        + "\n".join(rows) + "\n\n"
        "![Confusion matrix theo mô hình](figures/ml_confusion_matrices.png)\n\n"
        f"So với baseline, Accuracy của Logistic Regression chênh **{logistic_gain:+.4f}**, "
        f"Random Forest chênh **{forest_gain:+.4f}** (đơn vị tỷ lệ). "
        + comparison +
        "Baseline luôn đoán lớp tăng vì đó là nhãn đa số train; Recall lớp tăng bằng 1 "
        "theo cách đoán này nên F1 cao không tự chứng minh khả năng phân biệt hai lớp. "
        "Bảng `tables/ml_confusion_matrices.csv` có TN/FP/FN/TP; "
        "`tables/ml_test_predictions.csv` cho phép đối chiếu từng mẫu test. "
        "F1 được tính từ Precision/Recall, quy ước 0 khi mẫu số bằng 0. "
        "ROC-AUC dùng xác suất lớp tăng và chỉ có ý nghĩa khi test có cả hai lớp; "
        "baseline để N/A.\n\n"
        "## 8. Storytelling kết hợp và giới hạn ML\n\n"
        "Phần phân tích lịch sử cho thấy hiệu suất và biến động khác nhau giữa các mã. "
        "Thử nghiệm ML hỏi một câu khác: có dự đoán được **chiều** close phiên sau từ thông tin hiện tại hay không. "
        "So sánh với baseline và xem đồng thời Accuracy, Precision, Recall, F1 giúp tránh kết luận "
        "từ một chỉ số đơn lẻ. Dù mô hình có vượt baseline, điều đó không chứng minh có chiến lược "
        "giao dịch sinh lời. Dữ liệu chỉ đến 2017, giá có thể chưa điều chỉnh chia tách/cổ tức, "
        "mẫu công ty có thể thiên lệch, và bài không có phí, thuế, trượt giá hay backtest. "
        "Không diễn giải hệ số hay biến quan trọng như quan hệ nhân quả.\n"
    )
    return text


def run_ml(clean, base_report):
    train, test, audit = build_ml_samples(clean)
    outcome = fit_and_evaluate(train, test)
    if outcome is None:
        raise ValueError("Không đủ mẫu/lớp hợp lệ để đánh giá ML; xem ml_sample_audit.csv.")
    metrics, confusion, predictions = outcome
    plot_ml_results(metrics, confusion)
    addition = ml_markdown(train, test, audit, metrics, confusion)
    np.savetxt(f"{OUTPUT_DIR}/report.md", np.array([base_report + addition]), fmt="%s", encoding="utf-8")
    print("Đã cập nhật outputs/report.md với kết quả ML.")
    return addition
