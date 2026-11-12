# =============================================================================
### PHẦN 1. NHẬP THƯ VIỆN, THAM SỐ VÀ ĐỌC DỮ LIỆU
# =============================================================================
"""Phân tích S&P 500; chạy bằng .\run.ps1 từ PowerShell.

Chỉ dùng CSV cục bộ; bước ML chạy sau phần phân tích mô tả.
Xuất bảng CSV và biểu đồ PNG; dữ liệu gốc được giữ nguyên.
"""

### 1.1. Thư viện xử lý dữ liệu, vẽ biểu đồ và học máy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.metrics import confusion_matrix, roc_auc_score

### 1.2. Đường dẫn đầu vào và nơi lưu kết quả
DATA_FILE = "data/S&P 500 Stock Prices 2014-2017.csv"
OUTPUT_DIR = "outputs"

### 1.3. Ngưỡng phân tích và tham số mô hình
MIN_COVERAGE = 0.95
EXTREME_RETURN = 0.20  # Chỉ gắn cờ |return| >= 20%, không tự xóa.
ML_RANDOM_STATE = 42
ML_N_TREES = 30
ML_MAX_ITER = 1000
TRADING_DAYS_PER_YEAR = 252  # Quy ước tham khảo, không phải số phiên thực mỗi năm.
NORMAL_95_Z = 1.96


### 1.4. Hàm lưu bảng kết quả thành CSV
def save_table(frame, name):
    frame.to_csv(f"{OUTPUT_DIR}/tables/{name}.csv", index=False, encoding="utf-8-sig")


### 1.5. Đọc CSV gốc và lưu năm dòng đầu
def load_data():
    raw = pd.read_csv(DATA_FILE)
    save_table(raw[:5].copy(), "raw_preview")
    print("Số dòng dữ liệu gốc:", len(raw))
    print("Tên cột:", list(raw))
    return raw


# =============================================================================
### PHẦN 2. KIỂM TRA CHẤT LƯỢNG VÀ LÀM SẠCH DỮ LIỆU — chương 8–9
# =============================================================================
def clean_data(raw):
    ### 2.1. Chuẩn hóa mã cổ phiếu, ngày và số dòng nguồn
    columns = ["symbol", "date", "open", "high", "low", "close", "volume"]
    data = raw[columns].copy()
    data["symbol"] = data["symbol"].str.strip().str.upper()
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    exact_duplicate = np.array(data.duplicated(subset=columns))
    data["source_row"] = np.arange(len(data)) + 2  # Dòng CSV, tính cả header.

    ### 2.2. Thống kê dữ liệu thiếu và kiểu dữ liệu từng cột
    missing_rows = []
    schema_rows = []
    for column in columns:
        missing_rows.append({"column": column, "missing": int(raw[column].isna().sum())})
        schema_rows.append({"column": column, "loaded_dtype": str(np.array(raw[column]).dtype)})
    save_table(pd.DataFrame(missing_rows), "missing_by_column")
    save_table(pd.DataFrame(schema_rows), "schema")

    ### 2.3. Gắn cờ thiếu, trùng, giá không hợp lệ và mâu thuẫn OHLC
    flags = pd.DataFrame({"source_row": data["source_row"], "symbol": data["symbol"],
                          "date": data["date"]})
    flags["missing_symbol"] = data["symbol"].isna() | (data["symbol"] == "")
    flags["invalid_date"] = data["date"].isna()
    flags["exact_duplicate"] = exact_duplicate
    flags["duplicate_key_raw"] = data.duplicated(subset=["symbol", "date"], keep=False)
    for column in ["open", "high", "low", "close", "volume"]:
        values = np.array(data[column], dtype=float)
        flags[f"missing_{column}"] = data[column].isna()
        flags[f"nonfinite_{column}"] = ~np.isfinite(values)
        flags[f"invalid_sign_{column}"] = values < 0 if column == "volume" else values <= 0

    inconsistent = ((data["high"] < data["low"]) | (data["high"] < data["open"])
                    | (data["high"] < data["close"]) | (data["low"] > data["open"])
                    | (data["low"] > data["close"]))
    flags["inconsistent_ohlc"] = inconsistent
    summary = []
    for name in list(flags)[3:]:
        summary.append({"check": name, "flagged_rows": int(flags[name].sum())})
    audit = pd.DataFrame(summary)
    save_table(audit, "quality_summary")
    save_table(flags, "quality_flags")

    ### 2.4. Lập lịch tham chiếu từ các ngày hợp lệ trước khi cách ly giá
    valid_dates = data[data["date"].notna()]["date"]
    calendar = np.unique(np.array(valid_dates, dtype="datetime64[D]"))
    day_numbers = calendar.astype(np.int32)
    session_lookup = {int(day): i for i, day in enumerate(day_numbers)}

    ### 2.5. Loại trùng, cách ly dòng lỗi và ghi lý do theo từng bước
    data["exclude_reason"] = np.where(exact_duplicate, "exact_duplicate", "")
    remaining = data[~exact_duplicate].copy()
    conflicting = remaining.duplicated(subset=["symbol", "date"], keep=False)
    conflict_ids = np.array(remaining[conflicting]["source_row"])
    conflict = np.isin(np.array(data["source_row"]), conflict_ids)
    missing_key = np.array(flags["missing_symbol"] | flags["invalid_date"])
    bad_close = ~np.isfinite(np.array(data["close"], dtype=float)) | (np.array(data["close"]) <= 0)
    steps = [{"step": "raw", "removed": 0, "remaining": len(data)}]
    keep = np.ones(len(data), dtype=bool)
    for name, mask in [("exact_duplicate", exact_duplicate), ("missing_key", missing_key),
                       ("conflicting_key", conflict), ("invalid_close", bad_close),
                       ("inconsistent_ohlc", np.array(inconsistent))]:
        newly_removed = keep & mask
        data["exclude_reason"] = np.where(newly_removed, name, data["exclude_reason"])
        keep = keep & ~mask
        steps.append({"step": name, "removed": int(newly_removed.sum()),
                      "remaining": int(keep.sum())})
    excluded = data[~keep].copy()
    clean = data[keep].copy()
    clean = clean.set_index(["symbol", "date"]).sort_index().reset_index()
    clean_days = np.array(clean["date"], dtype="datetime64[D]").astype(np.int32)
    clean["session_id"] = [session_lookup[int(day)] for day in clean_days]
    ### 2.6. Đánh dấu dòng đủ OHLCV để dùng cho phép tính cần đủ các cột
    complete_ohlcv = np.ones(len(clean), dtype=bool)
    for column in ["open", "high", "low", "close", "volume"]:
        values = np.array(clean[column], dtype=float)
        valid_sign = values >= 0 if column == "volume" else values > 0
        complete_ohlcv = complete_ohlcv & np.isfinite(values) & valid_sign
    clean["complete_ohlcv"] = complete_ohlcv
    ### 2.7. Xuất dữ liệu sạch, lịch phiên và các bảng kiểm toán
    save_table(excluded, "excluded_rows")
    save_table(pd.DataFrame(steps), "cleaning_steps")
    save_table(clean, "clean_prices")
    save_table(pd.DataFrame({"date": calendar, "session_id": np.arange(len(calendar))}), "calendar")
    print("Số dòng dùng cho phân tích close:", len(clean))
    print("Dòng cách ly/loại trùng:", len(excluded))
    print(pd.DataFrame(steps))
    return clean, audit, calendar, pd.DataFrame(steps)


# =============================================================================
### PHẦN 3. TÍNH LỢI SUẤT VÀ CHỈ TIÊU TỪ GIÁ
# =============================================================================

### 3.1. Công thức lợi suất, mức biến động và CAGR cho một mã
def price_metrics(close, sessions, days):
    n = len(close)
    observed = np.full(n, float("nan"))
    daily = np.full(n, float("nan"))
    gaps = np.zeros(n, dtype=bool)
    if n > 1:
        observed[1:] = close[1:] / close[:-1] - 1
        consecutive = sessions[1:] - sessions[:-1] == 1
        daily[1:] = np.where(consecutive, observed[1:], float("nan"))
        gaps[1:] = ~consecutive
    valid_daily = daily[np.isfinite(daily)]
    average = valid_daily.mean() if len(valid_daily) > 0 else float("nan")
    volatility = valid_daily.std() if len(valid_daily) >= 2 else float("nan")
    years = (int(days[-1]) - int(days[0])) / 365.25
    cagr = (close[-1] / close[0]) ** (1 / years) - 1 if years > 0 else float("nan")
    cumulative = close / close[0] - 1
    return observed, daily, gaps, cumulative, average, volatility, cagr


### 3.2. Tính chỉ tiêu cho tất cả mã, kiểm tra độ phủ và xuất bảng
def analyze_prices(clean, calendar):
    metrics = []
    daily_parts = []
    common_days = calendar.astype(np.int32)
    for symbol, part in clean.groupby("symbol"):
        part = part.copy()
        close = np.array(part["close"], dtype=float)
        sessions = np.array(part["session_id"])
        dates = np.array(part["date"], dtype="datetime64[D]")
        days = dates.astype(np.int32)
        observed, daily, gaps, cumulative, average, volatility, cagr = price_metrics(close, sessions, days)
        n_returns = int(np.isfinite(daily).sum())
        coverage = len(part) / len(calendar)
        return_coverage = n_returns / (len(calendar) - 1) if len(calendar) > 1 else 0.0
        full_endpoints = days[0] == common_days[0] and days[-1] == common_days[-1]
        eligible = (full_endpoints and coverage >= MIN_COVERAGE
                    and return_coverage >= MIN_COVERAGE and np.isfinite(cagr)
                    and np.isfinite(volatility))
        reasons = []
        if not full_endpoints:
            reasons.append("missing_common_endpoint")
        if coverage < MIN_COVERAGE:
            reasons.append("low_price_coverage")
        if return_coverage < MIN_COVERAGE:
            reasons.append("low_return_coverage")
        if not np.isfinite(cagr) or not np.isfinite(volatility):
            reasons.append("insufficient_metrics")
        metrics.append({"symbol": symbol, "start_date": str(dates[0]), "end_date": str(dates[-1]),
                        "observations": len(part), "daily_returns": n_returns,
                        "price_coverage": coverage, "return_coverage": return_coverage,
                        "gap_returns": int(gaps.sum()), "cumulative_price_return": float(cumulative[-1]),
                        "average_daily_return": average, "daily_volatility": volatility, "cagr": cagr,
                        "extreme_daily_returns": int((np.abs(daily) >= EXTREME_RETURN).sum()),
                        "eligible": bool(eligible), "exclusion_reason": ";".join(reasons)})
        part["observed_return"] = observed
        part["daily_return"] = daily
        part["gap_before"] = gaps
        part["cumulative_price_return"] = cumulative
        part["normalized_price"] = 100 * (1 + cumulative)
        part["extreme_return_flag"] = np.abs(observed) >= EXTREME_RETURN
        daily_parts.append(part)
    metrics = pd.DataFrame(metrics)
    daily = pd.concat(daily_parts, axis=0).reset_index(drop=True)
    save_table(metrics, "stock_metrics_all")
    save_table(daily, "daily_returns")
    save_table(daily[daily["extreme_return_flag"]], "extreme_returns_review")
    print("Số mã được tính chỉ tiêu:", len(metrics))
    print("Số mã đủ điều kiện so sánh:", int(metrics["eligible"].sum()))
    return metrics, daily


# =============================================================================
### PHẦN 4. PHÂN NHÓM, CHỌN MÃ VÀ TÍNH BỔ SUNG
# =============================================================================

### 4.1. Định nghĩa bốn nhóm theo CAGR và mức biến động
GROUP_NAMES = {"A": "CAGR cao / biến động thấp", "B": "CAGR cao / biến động cao",
               "C": "CAGR thấp / biến động thấp", "D": "CAGR thấp / biến động cao"}


### 4.2. Chia nhóm bằng ngưỡng trung bình và chọn hai mã mỗi nhóm
def group_stocks(metrics):
    eligible = metrics[metrics["eligible"]].copy()
    cagr_threshold = np.array(eligible["cagr"]).mean()
    volatility_threshold = np.array(eligible["daily_volatility"]).mean()
    # Sai số tuyệt đối 1e-12 ở đơn vị tỷ lệ: coi bằng ngưỡng về mặt số học.
    high_return = (eligible["cagr"] >= cagr_threshold) | (np.abs(eligible["cagr"] - cagr_threshold) <= 1e-12)
    high_risk = ((eligible["daily_volatility"] >= volatility_threshold)
                 | (np.abs(eligible["daily_volatility"] - volatility_threshold) <= 1e-12))
    eligible["group"] = np.where(high_return, np.where(high_risk, "B", "A"),
                                  np.where(high_risk, "D", "C"))
    summaries = []
    selected_parts = []
    for group in ["A", "B", "C", "D"]:
        members = eligible[eligible["group"] == group].copy()
        summaries.append({"group": group, "definition": GROUP_NAMES[group], "stocks": len(members),
                          "mean_cagr": np.array(members["cagr"]).mean() if len(members) else float("nan"),
                          "mean_daily_volatility": np.array(members["daily_volatility"]).mean()
                          if len(members) else float("nan")})
        if len(members) > 0:
            ranked = members.set_index(["cagr", "symbol"]).sort_index().reset_index()
            first = ranked[:1].copy()
            first["selection_reason"] = f"CAGR thấp nhất trong nhóm {group} (hòa: symbol tăng dần)"
            selected_parts.append(first)
            if len(members) > 1:
                # Chọn symbol nhỏ nhất nếu nhiều mã cùng CAGR cao nhất.
                highest_cagr = np.array(ranked["cagr"])[-1]
                last = ranked[ranked["cagr"] == highest_cagr][:1].copy()
                if np.array(last["symbol"])[0] == np.array(first["symbol"])[0]:
                    last = ranked[-1:].copy()
                last["selection_reason"] = f"CAGR cao nhất trong nhóm {group} (hòa: symbol tăng dần)"
                selected_parts.append(last)
    selected = pd.concat(selected_parts, axis=0).reset_index(drop=True)
    summary = pd.DataFrame(summaries)
    summary["stock_share"] = np.array(summary["stocks"]) / len(eligible)
    thresholds = pd.DataFrame({"metric": ["cagr", "daily_volatility"],
                               "threshold": [cagr_threshold, volatility_threshold],
                               "rule": ["high_if_greater_or_equal_tol_1e-12", "high_if_greater_or_equal_tol_1e-12"]})
    save_table(eligible, "stock_groups")
    save_table(summary, "group_summary")
    save_table(selected, "selected_stocks")
    save_table(thresholds, "group_thresholds")
    print(summary)
    return eligible, summary, selected, thresholds


### 4.3. Quy đổi rủi ro theo năm, chỉ số cuối kỳ và khoảng cách tới ngưỡng
def build_descriptive_supplements(eligible, daily, summary, selected, thresholds):
    """Bảng 11/13 và bằng chứng bổ sung trong báo cáo Word, dùng số chưa làm tròn."""
    annual_factor = np.sqrt(TRADING_DAYS_PER_YEAR)
    group_comparison = summary.copy()
    annual_vol = np.array(group_comparison["mean_daily_volatility"]) * annual_factor
    group_comparison["annualized_volatility"] = annual_vol
    group_comparison["cagr_to_annualized_volatility"] = np.array(summary["mean_cagr"]) / np.where(
        annual_vol > 0, annual_vol, float("nan"))
    save_table(group_comparison, "group_annualized_comparison")

    selected_comparison = selected.copy()
    days = (np.array(pd.to_datetime(selected["end_date"]), dtype="datetime64[D]").astype(np.int32)
            - np.array(pd.to_datetime(selected["start_date"]), dtype="datetime64[D]").astype(np.int32))
    selected_comparison["calendar_days"] = days
    selected_comparison["years"] = days / 365.25
    selected_comparison["final_normalized_price"] = 100 * (1 + np.array(selected["cumulative_price_return"]))
    selected_comparison["final_index_from_cagr"] = 100 * (1 + np.array(selected["cagr"])) ** (days / 365.25)
    annual_vol = np.array(selected["daily_volatility"]) * annual_factor
    selected_comparison["annualized_volatility"] = annual_vol
    selected_comparison["cagr_to_annualized_volatility"] = np.array(selected["cagr"]) / np.where(
        annual_vol > 0, annual_vol, float("nan"))
    selected_comparison = selected_comparison.set_index(
        ["final_normalized_price", "symbol"]).sort_index().reset_index()
    save_table(selected_comparison, "selected_stock_comparison")

    chosen = daily[np.isin(np.array(daily["symbol"]), np.array(eligible["symbol"]))]
    values = np.array(chosen["daily_return"])
    values = values[np.isfinite(values)]
    distribution = pd.DataFrame([{
        "valid_daily_returns": len(values), "within_10pct": int((np.abs(values) <= 0.10).sum()),
        "outside_10pct": int((np.abs(values) > 0.10).sum()),
        "minimum_return": float(values.min()), "maximum_return": float(values.max()),
        "mean_return": float(values.mean()), "std_return": float(values.std()),
    }])
    save_table(distribution, "return_distribution_summary")

    distances = eligible[["symbol", "group", "cagr", "daily_volatility"]].copy()
    bounds = np.array(thresholds["threshold"])
    distances["cagr_distance_pp"] = (np.array(eligible["cagr"]) - bounds[0]) * 100
    distances["volatility_distance_pp"] = (np.array(eligible["daily_volatility"]) - bounds[1]) * 100
    distances["absolute_cagr_distance_pp"] = np.abs(np.array(distances["cagr_distance_pp"]))
    distances = distances.set_index(["absolute_cagr_distance_pp", "symbol"]).sort_index().reset_index()
    save_table(distances, "group_threshold_distances")
    return group_comparison, selected_comparison, distribution


### 4.4. Đối soát số dòng, số mã, tổng nhóm và các ngưỡng
def build_consistency_checks(raw, clean, metrics, eligible, summary, thresholds):
    steps = pd.read_csv(f"{OUTPUT_DIR}/tables/cleaning_steps.csv")
    weights = np.array(summary["stocks"]) / len(eligible)
    bounds = np.array(thresholds["threshold"])
    checks = [
        ("all_symbols", len(eligible) + int((~np.array(metrics["eligible"])).sum()), len(metrics)),
        ("group_symbols", int(summary["stocks"].sum()), len(eligible)),
        ("raw_equals_clean_plus_excluded", len(clean) + int(steps["removed"].sum()), len(raw)),
        ("weighted_cagr_threshold", float((weights * np.array(summary["mean_cagr"])).sum()), bounds[0]),
        ("weighted_volatility_threshold", float((weights * np.array(summary["mean_daily_volatility"])).sum()), bounds[1]),
    ]
    rows = [{"check": name, "actual": actual, "expected": expected,
             "absolute_difference": abs(actual - expected), "passed": abs(actual - expected) <= 1e-12}
            for name, actual, expected in checks]
    result = pd.DataFrame(rows)
    save_table(result, "consistency_checks")
    return result


# =============================================================================
### PHẦN 5. VẼ BẢY BIỂU ĐỒ PHÂN TÍCH DỮ LIỆU
# =============================================================================

### 5.1. Hàm căn bố cục và lưu ảnh PNG
def save_figure(name):
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/figures/{name}.png", dpi=160)


### 5.2. Vẽ lần lượt Hình 1–7 từ các bảng phân tích
def make_figures(eligible, daily, summary, selected, thresholds,
                 group_comparison, selected_comparison):
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.spines.right"] = False
    palette = {"A": "#087f8c", "B": "#df7b27", "C": "#4c6fb5", "D": "#ad4668"}
    ### 5.2.1. Hình 1 — Phân phối lợi suất một phiên
    chosen_daily = daily[np.isin(np.array(daily["symbol"]), np.array(eligible["symbol"]))]
    returns = np.array(chosen_daily["daily_return"])
    returns = returns[np.isfinite(returns)] * 100
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    axes[0].hist(returns, bins=100, color="#087f8c")
    axes[0].set_title("Lợi suất một phiên — toàn bộ phân phối")
    center = returns[np.abs(returns) <= 10]
    axes[1].hist(center, bins=100, color="#4c6fb5")
    axes[1].set_title(f"Phóng to [-10%, 10%]; ngoài vùng: {len(returns)-len(center):,}")
    for ax in axes:
        ax.set_xlabel("Lợi suất giá một phiên (%)")
        ax.set_ylabel("Số quan sát mã–phiên")
        ax.set_ylim(bottom=0)
    save_figure("01_return_distribution")

    ### 5.2.2. Hình 2 — Xếp hạng mười CAGR cao nhất và thấp nhất
    ranked = eligible.set_index(["cagr", "symbol"]).sort_index().reset_index()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, subset, title, color in [(axes[0], ranked[:10], "10 mã CAGR thấp nhất", "#ad4668"),
                                      (axes[1], ranked[-10:], "10 mã CAGR cao nhất", "#087f8c")]:
        ax.barh(list(subset["symbol"]), np.array(subset["cagr"]) * 100, color=color)
        ax.axvline(0, color="#333333", linewidth=0.8)
        ax.set_title(title)
        ax.set_xlabel("CAGR giá (%/năm)")
        ax.set_ylabel("Mã cổ phiếu")
    save_figure("02_cagr_ranking")

    ### 5.2.3. Hình 3 — Quan hệ CAGR, mức biến động và bốn nhóm
    fig, ax = plt.subplots(figsize=(10, 6))
    for group in ["A", "B", "C", "D"]:
        members = eligible[eligible["group"] == group]
        ax.scatter(np.array(members["daily_volatility"]) * 100,
                   np.array(members["cagr"]) * 100, alpha=0.65, s=28,
                   color=palette[group], label=f"{group}: {GROUP_NAMES[group]}")
    bounds = np.array(thresholds["threshold"])
    ax.axhline(bounds[0] * 100, color="#555555", linestyle="--", linewidth=0.8)
    ax.axvline(bounds[1] * 100, color="#555555", linestyle="--", linewidth=0.8)
    ax.set_title("Hiệu suất–rủi ro: ngưỡng trung bình của tập đủ điều kiện")
    ax.set_xlabel("Độ lệch chuẩn lợi suất một phiên (%)")
    ax.set_ylabel("CAGR giá (%/năm)")
    ax.legend(fontsize=9)
    save_figure("03_risk_return_groups")

    ### 5.2.4. Hình 4 — Số cổ phiếu trong từng nhóm
    fig, ax = plt.subplots(figsize=(8, 4.5))
    counts = np.array(summary["stocks"])
    ax.bar([f"Nhóm {g}" for g in summary["group"]], counts,
           color=[palette[g] for g in summary["group"]])
    for i, count in enumerate(counts):
        ax.text(i, count, str(count), ha="center", va="bottom")
    ax.set_title("Số cổ phiếu trong bốn nhóm theo quy tắc")
    ax.set_xlabel("Nhóm CAGR–biến động")
    ax.set_ylabel("Số mã cổ phiếu")
    ax.set_ylim(0, counts.max() * 1.16)
    save_figure("04_group_counts")

    ### 5.2.5. Hình 5 — CAGR, biến động quy năm và tỷ số tham khảo
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
    for ax, field, title, unit, scale in zip(
            axes, ["mean_cagr", "annualized_volatility", "cagr_to_annualized_volatility"],
            ["CAGR trung bình", "Biến động quy năm", "CAGR / biến động quy năm"],
            ["%/năm", "%/năm", "Tỷ số tham khảo"], [100, 100, 1]):
        values = np.array(group_comparison[field]) * scale
        ax.bar(list(group_comparison["group"]), values, color=[palette[g] for g in summary["group"]])
        ax.axhline(0, color="#555555", linewidth=0.8)
        ax.set_ylim(bottom=float(np.minimum(0, values.min() * 1.2)), top=float(values.max() * 1.2))
        ax.set_title(title)
        ax.set_xlabel("Nhóm cổ phiếu")
        ax.set_ylabel(unit)
    save_figure("05_group_annualized_risk_return")

    ### 5.2.6. Hình 6 — Diễn biến giá tám mã, cùng mốc đầu kỳ bằng 100
    # Chèn NaN ở phiên thiếu để không nối đường qua khoảng trống.
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True)
    # Dùng session_id trực tiếp, không suy ra lịch riêng của từng mã.
    calendar_frame = pd.read_csv(f"{OUTPUT_DIR}/tables/calendar.csv")
    all_dates = pd.to_datetime(calendar_frame["date"])
    year_labels = np.unique(np.array([str(date)[:4] for date in calendar_frame["date"]]))
    year_ticks = pd.to_datetime([f"{year}-01-02" for year in year_labels])
    for i, group in enumerate(["A", "B", "C", "D"]):
        ax = axes[i // 2, i % 2]
        members = selected[selected["group"] == group]
        for symbol in members["symbol"]:
            series = daily[daily["symbol"] == symbol]
            normalized = np.full(len(all_dates), float("nan"))
            normalized[np.array(series["session_id"], dtype=int)] = np.array(series["normalized_price"])
            ax.plot(all_dates, normalized, label=symbol, linewidth=1.3)
        ax.axhline(100, color="#777777", linestyle="--", linewidth=0.8)
        ax.set_title(f"{group}: {GROUP_NAMES[group]}")
        ax.set_xlabel("Năm giao dịch")
        ax.set_ylabel("Chỉ số giá (phiên đầu = 100)")
        ax.set_xticks(year_ticks)
        ax.set_xticklabels(year_labels)
        if len(members):
            ax.legend()
    save_figure("06_selected_normalized_prices")

    ### 5.2.7. Hình 7 — Chỉ số cuối kỳ của tám mã trên thang logarit
    # Vẽ điểm trên log10(chỉ số), ghi tick theo chỉ số gốc; không vẽ cột từ gốc log tùy ý.
    fig, ax = plt.subplots(figsize=(10, 5))
    final_values = np.array(selected_comparison["final_normalized_price"])
    positions = np.arange(len(final_values))
    ax.scatter(np.log10(final_values), positions,
               color=[palette[g] for g in selected_comparison["group"]], s=65)
    for i, value in enumerate(final_values):
        ax.text(float(np.log10(value)) + 0.025, i, f"{value:.1f}", va="center")
    ticks = np.array([10, 30, 100, 300, 1000, 3000])
    ax.set_xticks(np.log10(ticks))
    ax.set_xticklabels([str(value) for value in ticks])
    ax.set(yticks=positions, yticklabels=list(selected_comparison["symbol"]))
    ax.axvline(2, color="#777777", linestyle="--", linewidth=0.8)
    ax.set_title("Chỉ số giá cuối kỳ của tám mã được chọn")
    ax.set_xlabel("Chỉ số giá cuối kỳ — thang logarit (đầu kỳ = 100)")
    ax.set_ylabel("Mã cổ phiếu")
    save_figure("07_selected_final_index")
    print("Đã xuất 7 hình phân tích mô tả vào outputs/figures.")


# =============================================================================
### PHẦN 6. HỌC MÁY: TẠO MẪU, HUẤN LUYỆN VÀ ĐÁNH GIÁ
# =============================================================================

### 6.1. Năm đặc trưng đầu vào và hàm lưu bảng ML
FEATURES = ["return_1d_t", "range_t", "intraday_t", "volume_t", "volume_change_t"]


def save_ml_table(frame, name):
    frame.to_csv(f"{OUTPUT_DIR}/tables/{name}.csv", index=False, encoding="utf-8-sig")


### 6.2. Tạo đặc trưng, nhãn phiên tiếp theo và chia train/test theo năm
def build_ml_samples(clean):
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


### 6.3. Tính Accuracy, Precision, Recall, F1, ROC-AUC và ma trận đúng/sai
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


### 6.4. Huấn luyện hai mô hình và so sánh với baseline
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

    ### 6.4.1. Baseline — Luôn đoán lớp đa số của tập train
    positives = int((y_train == 1).sum())
    negatives = int((y_train == 0).sum())
    baseline_label = 1 if positives > negatives else 0
    baseline_pred = np.full(len(y_test), baseline_label)

    ### 6.4.2. Logistic Regression — Chuẩn hóa theo train rồi huấn luyện
    scaler = StandardScaler()
    scaled_train = scaler.fit_transform(x_train)
    scaled_test = scaler.transform(x_test)
    logistic = LogisticRegression(max_iter=ML_MAX_ITER, random_state=ML_RANDOM_STATE)
    logistic.fit(scaled_train, y_train)
    logistic_pred = logistic.predict(scaled_test)
    logistic_score = logistic.predict_proba(scaled_test)[:, 1]

    ### 6.4.3. Random Forest — Huấn luyện trên đặc trưng gốc
    forest = RandomForestClassifier(n_estimators=ML_N_TREES, random_state=ML_RANDOM_STATE)
    forest.fit(x_train, y_train)
    forest_pred = forest.predict(x_test)
    forest_score = forest.predict_proba(x_test)[:, 1]

    ### 6.4.4. Đánh giá trên cùng tập test và lưu dự đoán từng mẫu
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


### 6.5. Chỉ số bổ sung, chuẩn hóa ma trận và khoảng tin cậy
def build_ml_supplements(metrics, confusion, predictions):
    """Bảng 19 và Hình 10–11; CI iid được tách khỏi so sánh ghép cặp theo ngày."""
    y_true = np.array(predictions["label"], dtype=int)
    baseline_correct = np.array(predictions["baseline_prediction"], dtype=int) == y_true
    baseline_count = int(baseline_correct.sum())
    n = len(y_true)
    rows, normalized_rows, day_rows = [], [], []
    fields = ["baseline_prediction", "logistic_prediction", "forest_prediction"]
    for i, (name, field) in enumerate(zip(metrics["model"], fields)):
        predicted = np.array(predictions[field], dtype=int)
        correct = predicted == y_true
        tn, fp, fn, tp = np.array(confusion[["tn", "fp", "fn", "tp"]], dtype=int)[i]
        negative_count, positive_count = int(tn + fp), int(tp + fn)
        specificity = tn / negative_count if negative_count > 0 else float("nan")
        recall = tp / positive_count if positive_count > 0 else float("nan")
        accuracy = int(correct.sum()) / n
        balanced_accuracy = (specificity + recall) / 2
        accuracy_se = np.sqrt(accuracy * (1 - accuracy) / n)
        balanced_se = np.sqrt((specificity * (1 - specificity) / negative_count
                               + recall * (1 - recall) / positive_count) / 4)
        paired_delta = correct.astype(float) - baseline_correct.astype(float)
        delta = float(paired_delta.mean())
        paired_se = np.sqrt(((paired_delta - delta) ** 2).sum() / (n * (n - 1))) if n > 1 else float("nan")

        by_day = predictions[["target_date"]].copy()
        by_day["correct"] = correct.astype(int)
        by_day["baseline_correct"] = baseline_correct.astype(int)
        accuracy_residual_sums, delta_residual_sums = [], []
        for date, day in by_day.groupby("target_date"):
            day_n = len(day)
            day_correct = int(day["correct"].sum())
            day_baseline = int(day["baseline_correct"].sum())
            accuracy_residual_sums.append(day_correct - day_n * accuracy)
            delta_residual_sums.append(day_correct - day_baseline - day_n * delta)
            day_rows.append({"model": name, "target_date": date, "samples": day_n,
                             "correct": day_correct, "baseline_correct": day_baseline,
                             "accuracy": day_correct / day_n,
                             "accuracy_difference": (day_correct - day_baseline) / day_n})
        g = len(accuracy_residual_sums)
        cluster_se = np.sqrt(g / (g - 1) * (np.array(accuracy_residual_sums) ** 2).sum() / n ** 2) if g > 1 else float("nan")
        delta_cluster_se = np.sqrt(g / (g - 1) * (np.array(delta_residual_sums) ** 2).sum() / n ** 2) if g > 1 else float("nan")
        rows.append({
            "model": name, "test_samples": n, "correct_predictions": int(correct.sum()),
            "correct_difference_vs_baseline": int(correct.sum()) - baseline_count,
            "predicted_up_rate": float((predicted == 1).mean()),
            "specificity_0": specificity, "recall_1": recall, "balanced_accuracy": balanced_accuracy,
            "balanced_accuracy_se_iid": balanced_se, "accuracy": accuracy, "accuracy_se_iid": accuracy_se,
            "accuracy_ci95_iid_low": float(np.maximum(0, accuracy - NORMAL_95_Z * accuracy_se)),
            "accuracy_ci95_iid_high": float(np.minimum(1, accuracy + NORMAL_95_Z * accuracy_se)),
            "accuracy_difference_vs_baseline": delta, "accuracy_difference_se_iid_paired": paired_se,
            "target_dates": g, "accuracy_se_date_cluster": cluster_se,
            "accuracy_ci95_date_cluster_low": float(np.maximum(0, accuracy - NORMAL_95_Z * cluster_se)),
            "accuracy_ci95_date_cluster_high": float(np.minimum(1, accuracy + NORMAL_95_Z * cluster_se)),
            "accuracy_difference_se_date_cluster": delta_cluster_se,
            "accuracy_difference_ci95_date_cluster_low": delta - NORMAL_95_Z * delta_cluster_se,
            "accuracy_difference_ci95_date_cluster_high": delta + NORMAL_95_Z * delta_cluster_se,
        })
        for actual, predicted_label, count, support in [
                (0, 0, tn, negative_count), (0, 1, fp, negative_count),
                (1, 0, fn, positive_count), (1, 1, tp, positive_count)]:
            normalized_rows.append({"model": name, "actual_label": actual, "predicted_label": predicted_label,
                                    "count": int(count), "actual_class_support": support,
                                    "row_normalized_rate": count / support if support > 0 else float("nan")})
    supplementary = pd.DataFrame(rows)
    normalized = pd.DataFrame(normalized_rows)
    save_ml_table(supplementary, "ml_supplementary_metrics")
    save_ml_table(normalized, "ml_confusion_matrices_normalized")
    save_ml_table(pd.DataFrame(day_rows), "ml_daily_evaluation")
    return supplementary, normalized


### 6.6. Hàm vẽ ma trận đúng/sai dưới dạng số đếm hoặc tỷ lệ
def draw_confusion_matrix(ax, counts, normalized):
    matrix = np.array([[counts[0], counts[1]], [counts[2], counts[3]]], dtype=float)
    supports = matrix.sum(axis=1)
    for actual in [0, 1]:
        for predicted in [0, 1]:
            value = matrix[actual, predicted]
            rate = value / supports[actual] if supports[actual] > 0 else float("nan")
            shade = rate if normalized else value / matrix.max()
            color = (1 - 0.85 * shade, 1 - 0.55 * shade, 1 - 0.25 * shade)
            ax.add_patch(Rectangle((predicted - 0.5, actual - 0.5), 1, 1, facecolor=color, edgecolor="white"))
            ax.text(predicted, actual, f"{rate:.1%}" if normalized else f"{int(value):,}",
                    ha="center", va="center", color="white" if shade > 0.65 else "black", fontsize=13)
    ax.set(xlim=(-0.5, 1.5), ylim=(1.5, -0.5), xticks=[0, 1], yticks=[0, 1],
           xticklabels=["Không tăng", "Tăng"], yticklabels=["Không tăng", "Tăng"])
    ax.set_xlabel("Nhãn dự đoán")
    ax.set_ylabel("Nhãn thực tế")


### 6.7. Vẽ Hình 8–11 để so sánh và đánh giá mô hình
def plot_ml_results(metrics, confusion, supplementary):
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
    plt.savefig(f"{OUTPUT_DIR}/figures/08_ml_metric_comparison.png", dpi=160)

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for i, name in enumerate(names):
        ax = axes[i]
        counts = np.array(confusion[["tn", "fp", "fn", "tp"]])[i]
        draw_confusion_matrix(ax, counts, False)
        ax.set_title(name)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/figures/09_ml_confusion_matrices.png", dpi=160)

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for i, name in enumerate(names):
        counts = np.array(confusion[["tn", "fp", "fn", "tp"]])[i]
        draw_confusion_matrix(axes[i], counts, True)
        axes[i].set_title(name + " — chuẩn hóa hàng")
    save_figure("10_ml_normalized_confusion_matrices")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    positions = np.arange(len(names))
    for i, accuracy, low, high in zip(positions, supplementary["accuracy"],
                                      supplementary["accuracy_ci95_iid_low"], supplementary["accuracy_ci95_iid_high"]):
        axes[0].plot([i, i], [low, high], color="#087f8c", linewidth=2)
        axes[0].scatter([i], [accuracy], color="#087f8c", s=45)
        axes[0].text(i, high + 0.0015, f"{accuracy:.2%}", ha="center", fontsize=9)
    axes[0].set_title("Accuracy và CI 95% minh họa (giả định iid)")
    axes[0].set_ylabel("Accuracy — trục phóng to")
    axes[0].set_ylim(float(np.array(supplementary["accuracy_ci95_iid_low"]).min()) - 0.006,
                     float(np.array(supplementary["accuracy_ci95_iid_high"]).max()) + 0.008)
    axes[1].bar(names, np.array(supplementary["balanced_accuracy"]), color=["#777777", "#087f8c", "#df7b27"])
    axes[1].axhline(0.5, color="#555555", linestyle="--")
    axes[1].set_title("Balanced accuracy trên test 2017")
    axes[1].set_ylabel("Trung bình Recall hai lớp")
    axes[1].set_ylim(0, 1)
    for ax in axes:
        ax.set_xticks(positions)
        ax.set_xticklabels(names)
        ax.set_xlabel("Cách dự đoán")
    save_figure("11_ml_accuracy_intervals_balanced")


### 6.8. Điều phối phần ML và đối soát tổng số mẫu
def run_ml(clean):
    train, test, audit = build_ml_samples(clean)
    outcome = fit_and_evaluate(train, test)
    if outcome is None:
        raise ValueError("Không đủ mẫu/lớp hợp lệ để đánh giá ML; xem ml_sample_audit.csv.")
    metrics, confusion, predictions = outcome
    supplementary, normalized = build_ml_supplements(metrics, confusion, predictions)
    plot_ml_results(metrics, confusion, supplementary)
    checks = pd.read_csv(f"{OUTPUT_DIR}/tables/consistency_checks.csv")
    audit_total = int(np.array(audit[list(audit)[1:]], dtype=int).sum())
    extra_check = pd.DataFrame([{"check": "ml_used_plus_excluded_equals_clean", "actual": audit_total,
                                 "expected": len(clean), "absolute_difference": abs(audit_total - len(clean)),
                                 "passed": audit_total == len(clean)}])
    save_table(pd.concat([checks, extra_check], axis=0), "consistency_checks")
    return metrics, confusion, predictions, supplementary, normalized


# =============================================================================
### PHẦN 7. CHẠY TOÀN BỘ QUY TRÌNH
# =============================================================================

### 7.1. Gọi lần lượt đọc, làm sạch, phân tích, vẽ hình và học máy
def main():
    raw = load_data()
    clean, _, calendar, _ = clean_data(raw)
    if len(clean) == 0 or len(calendar) < 2:
        print("Dừng: không đủ dữ liệu giá/ngày để phân tích.")
        return None
    metrics, daily = analyze_prices(clean, calendar)
    if int(metrics["eligible"].sum()) == 0:
        print("Dừng: không có mã đủ điều kiện. Xem stock_metrics_all.csv; không tự hạ ngưỡng.")
        return None
    eligible, summary, selected, thresholds = group_stocks(metrics)
    group_comparison, selected_comparison, _ = build_descriptive_supplements(
        eligible, daily, summary, selected, thresholds)
    build_consistency_checks(raw, clean, metrics, eligible, summary, thresholds)
    make_figures(eligible, daily, summary, selected, thresholds, group_comparison, selected_comparison)
    result = run_ml(clean)
    print("Hoàn thành. Bảng CSV: outputs/tables; biểu đồ PNG: outputs/figures.")
    return result


### 7.2. Điểm bắt đầu khi chạy script
if __name__ == "__main__":
    main()
