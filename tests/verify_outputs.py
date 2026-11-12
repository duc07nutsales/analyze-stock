r"""Đối chiếu độc lập bảng CSV và biểu đồ PNG sau khi chạy script.

Chạy từ gốc dự án: .venv\Scripts\python.exe -X utf8 -m tests.verify_outputs
Đây là kiểm chứng đầu ra, không phải thuật toán phân tích của bài.
"""
from collections import defaultdict
import hashlib
import math
from pathlib import Path

import numpy as np
import pandas as pd


def close(actual, expected):
    assert math.isclose(float(actual), float(expected), rel_tol=1e-11, abs_tol=1e-12), (actual, expected)


def main():
    root = Path(__file__).resolve().parents[1]
    tables = root / 'outputs/tables'
    raw_hash = hashlib.sha256((root / 'data/S&P 500 Stock Prices 2014-2017.csv').read_bytes()).hexdigest()
    assert raw_hash == '2200ea7c7b98791314cb5b4a3072b4d4166da1ed78a3e3e178339199109837d2'
    groups = pd.read_csv(tables / 'group_summary.csv').set_index('group')
    annual = pd.read_csv(tables / 'group_annualized_comparison.csv').set_index('group')
    daily = pd.read_csv(tables / 'daily_returns.csv')
    for group, row in groups.iterrows():
        result = annual.loc[group]
        close(result['annualized_volatility'], row['mean_daily_volatility'] * math.sqrt(252))
        close(result['cagr_to_annualized_volatility'], row['mean_cagr'] / (row['mean_daily_volatility'] * math.sqrt(252)))
        close(result['stock_share'], row['stocks'] / groups['stocks'].sum())
    stocks = pd.read_csv(tables / 'selected_stock_comparison.csv')
    for _, row in stocks.iterrows():
        prices = daily[daily['symbol'] == row['symbol']]
        ratio = prices.iloc[-1]['close'] / prices.iloc[0]['close']
        close(row['final_normalized_price'], 100 * ratio)
        close(row['final_index_from_cagr'], 100 * ratio)
        close(row['annualized_volatility'], prices['daily_return'].dropna().to_numpy().std() * math.sqrt(252))
    eligible = pd.read_csv(tables / 'stock_groups.csv')
    values = daily[daily['symbol'].isin(eligible['symbol'])]['daily_return'].dropna()
    distribution = pd.read_csv(tables / 'return_distribution_summary.csv').iloc[0]
    assert distribution['outside_10pct'] == (values.abs() > 0.1).sum()
    assert distribution['valid_daily_returns'] == len(values)
    checks = pd.read_csv(tables / 'consistency_checks.csv')
    assert len(checks) == 6 and checks['passed'].all()
    assert (checks['absolute_difference'] <= 1e-12).all()

    predictions = pd.read_csv(tables / 'ml_test_predictions.csv')
    extra = pd.read_csv(tables / 'ml_supplementary_metrics.csv').set_index('model')
    normalized = pd.read_csv(tables / 'ml_confusion_matrices_normalized.csv')
    day_table = pd.read_csv(tables / 'ml_daily_evaluation.csv')
    labels = predictions['label'].to_numpy()
    baseline = predictions['baseline_prediction'].to_numpy() == labels
    columns = {'baseline_majority': 'baseline_prediction', 'logistic_regression': 'logistic_prediction',
               'random_forest': 'forest_prediction'}
    for model, column in columns.items():
        row = extra.loc[model]
        predicted = predictions[column].to_numpy()
        correct = predicted == labels
        n = len(correct)
        tn = int(((labels == 0) & (predicted == 0)).sum())
        fp = int(((labels == 0) & (predicted == 1)).sum())
        fn = int(((labels == 1) & (predicted == 0)).sum())
        tp = int(((labels == 1) & (predicted == 1)).sum())
        specificity, recall = tn / (tn + fp), tp / (tp + fn)
        accuracy = (tn + tp) / n
        delta = (int(correct.sum()) - int(baseline.sum())) / n
        close(row['accuracy'], accuracy)
        close(row['balanced_accuracy'], (specificity + recall) / 2)
        close(row['predicted_up_rate'], (tp + fp) / n)
        assert row['correct_difference_vs_baseline'] == correct.sum() - baseline.sum()
        se = math.sqrt(accuracy * (1 - accuracy) / n)
        close(row['accuracy_se_iid'], se)
        close(row['accuracy_ci95_iid_low'], max(0, accuracy - 1.96 * se))
        close(row['accuracy_ci95_iid_high'], min(1, accuracy + 1.96 * se))
        balanced_se = math.sqrt((specificity * (1 - specificity) / (tn + fp)
                                + recall * (1 - recall) / (tp + fn)) / 4)
        close(row['balanced_accuracy_se_iid'], balanced_se)
        paired = correct.astype(int) - baseline.astype(int)
        close(row['accuracy_difference_se_iid_paired'], paired.std(ddof=1) / math.sqrt(n))

        by_date = defaultdict(lambda: [0, 0, 0])
        for date, hit, base_hit in zip(predictions['target_date'], correct, baseline):
            by_date[date][0] += 1
            by_date[date][1] += int(hit)
            by_date[date][2] += int(base_hit)
        g = len(by_date)
        assert row['target_dates'] == g
        sums = [(hits - count * accuracy) for count, hits, _ in by_date.values()]
        delta_sums = [(hits - base_hits - count * delta) for count, hits, base_hits in by_date.values()]
        cluster_se = math.sqrt(g / (g - 1) * sum(x * x for x in sums)) / n
        delta_se = math.sqrt(g / (g - 1) * sum(x * x for x in delta_sums)) / n
        close(row['accuracy_se_date_cluster'], cluster_se)
        close(row['accuracy_difference_se_date_cluster'], delta_se)
        close(row['accuracy_difference_ci95_date_cluster_low'], delta - 1.96 * delta_se)
        close(row['accuracy_difference_ci95_date_cluster_high'], delta + 1.96 * delta_se)
        day_rows = day_table[day_table['model'] == model]
        assert len(day_rows) == g and day_rows['samples'].sum() == n
        for _, day in day_rows.iterrows():
            assert list(day[['samples', 'correct', 'baseline_correct']]) == by_date[day['target_date']]
        model_rates = normalized[normalized['model'] == model]
        for _, item in model_rates.iterrows():
            a, p = int(item['actual_label']), int(item['predicted_label'])
            count = int(((labels == a) & (predicted == p)).sum())
            support = int((labels == a).sum())
            assert item['count'] == count and item['actual_class_support'] == support
            close(item['row_normalized_rate'], count / support)
        for _, part in model_rates.groupby('actual_label'):
            close(part['row_normalized_rate'].sum(), 1)

    names = ['01_return_distribution', '02_cagr_ranking', '03_risk_return_groups', '04_group_counts',
             '05_group_annualized_risk_return', '06_selected_normalized_prices', '07_selected_final_index',
             '08_ml_metric_comparison', '09_ml_confusion_matrices', '10_ml_normalized_confusion_matrices',
             '11_ml_accuracy_intervals_balanced']
    assert {p.stem for p in (root / 'outputs/figures').glob('*.png')} == set(names)
    assert len(list(tables.glob('*.csv'))) == 28
    assert not list((root / 'outputs').glob('*.md'))
    assert not list((root / 'notebooks').glob('*.ipynb'))
    print('PASS: dữ liệu gốc giữ nguyên; 28 CSV, SE/CI và 11 hình khớp đầu ra.')


if __name__ == '__main__':
    main()
