# Hướng dẫn dự án phân tích S&P 500

Dự án đọc dữ liệu giá cổ phiếu giai đoạn 2014–2017, làm sạch, tính lợi suất và mức biến động, chia nhóm cổ phiếu, thử dự đoán chiều giá phiên tiếp theo và vẽ biểu đồ. Toàn bộ code xử lý nằm trong một file: [src/sp500_analysis.py](src/sp500_analysis.py).

Khi chạy, chương trình xuất **28 bảng CSV** trong `outputs/tables/` và **11 ảnh PNG** trong `outputs/figures/`. File README này được viết riêng để giải thích code và các đầu ra. Chương trình không sinh báo cáo Markdown, Word hoặc notebook.

## 1. Chạy chương trình

Mở PowerShell trong thư mục gốc, nơi có `run.ps1`. Lần đầu, chạy:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 -Install
```

Những lần sau:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1
```

`run.ps1` chuẩn bị môi trường Python `.venv`, cài thư viện khi có `-Install`, tạo thư mục đầu ra và gọi script chính. Phân tích và học máy dùng CSV cục bộ. Internet chỉ cần khi cài thư viện.

## 2. Luồng hoạt động

```text
run.ps1
   ↓
src/sp500_analysis.py đọc CSV trong data/
   ↓
Kiểm tra dữ liệu → làm sạch → bảng giá sạch
   ↓
   ├── Tính lợi suất, CAGR, biến động → phân nhóm → 7 hình mô tả
   │
   └── Tạo mẫu ML → huấn luyện 2014–2016 → kiểm tra 2017 → 4 hình ML
   ↓
outputs/tables/  (28 CSV)       outputs/figures/  (11 PNG)
```

Chương trình chạy phần phân tích mô tả trước, rồi mới chạy học máy. Cả hai dùng bảng giá sạch; phần học máy không dùng danh sách nhóm cổ phiếu làm bộ lọc đầu vào.

| Bước trong script | Đầu vào | Cách xử lý | Đầu ra |
| --- | --- | --- | --- |
| Đọc — `load_data()` | CSV gốc. | Đọc các cột mã, ngày, giá và khối lượng. | Bảng gốc trong bộ nhớ, CSV năm dòng đầu. |
| Làm sạch — `clean_data()` | Bảng gốc. | Kiểm tra thiếu/trùng/giá không hợp lệ, cách ly dòng lỗi, lập lịch phiên. | Giá sạch, cờ lỗi, lý do loại và lịch phiên. |
| Phân tích — `price_metrics()`, `analyze_prices()` | Giá sạch và lịch phiên. | Tính riêng từng mã theo thứ tự thời gian: lợi suất, CAGR, độ biến động và độ phủ. | Chuỗi lợi suất và chỉ tiêu tất cả mã. |
| Phân nhóm — `group_stocks()` | Chỉ tiêu từng mã. | Chọn mã đủ hai đầu kỳ và đạt độ phủ 95%; chia bốn nhóm, lấy hai mã ở hai đầu CAGR mỗi nhóm. | Nhóm, ngưỡng, tổng hợp nhóm và tám mã xem sâu. |
| Tính bổ sung — `build_descriptive_supplements()`, `build_consistency_checks()` | Giá, chỉ tiêu và nhóm. | Quy đổi biến động theo năm, tính chỉ số cuối kỳ, khoảng cách tới ngưỡng và đối soát các tổng. | Bảng bổ sung theo Word, bảng kiểm tra nhất quán. |
| Vẽ — `make_figures()` | Các bảng phân tích. | Vẽ phân phối, xếp hạng, nhóm và diễn biến giá. | Hình 1–7. |
| Học máy — `run_ml()` | Bảng giá sạch. | Tạo mẫu, huấn luyện hai mô hình, so với baseline, tính chỉ số và sai số. | Bảy CSV học máy, Hình 8–11; bổ sung đối soát mẫu ML. |

`main()` ở cuối script gọi các bước trên. Dữ liệu chủ yếu được truyền giữa các hàm trong bộ nhớ; CSV được ghi để xem và kiểm chứng. Một số bảng như lịch phiên và bảng đối soát cũng được đọc lại khi cần. Dữ liệu gốc được giữ nguyên.

## 3. File và thư mục

```text
python_analyze_stock/
├── README.md                 File hướng dẫn đang đọc
├── run.ps1                   Chạy phân tích
├── test.ps1                  Chạy các kiểm thử nhỏ
├── requirements.txt          Thư viện cần cài
├── requirements-lock.txt     Phiên bản thư viện và phụ thuộc đã kiểm tra
├── data/
│   └── S&P 500 Stock Prices 2014-2017.csv
├── src/
│   ├── __init__.py
│   └── sp500_analysis.py     Toàn bộ code và tham số
├── tests/
│   ├── __init__.py
│   ├── test_analysis.py
│   ├── test_ml.py
│   └── verify_outputs.py
├── docs/
│   ├── de_bai.md             Đề gốc
│   └── allowed_knowledge_reference.md
└── outputs/
    ├── tables/               28 bảng CSV
    └── figures/              11 ảnh PNG
```

| File | Đầu vào | Công dụng / đầu ra |
| --- | --- | --- |
| [run.ps1](run.ps1) | Python, `requirements.txt`, script chính. | Chuẩn bị môi trường rồi chạy phân tích để tạo CSV/PNG. |
| [requirements.txt](requirements.txt) | Danh sách thư viện được khai báo. | Cho công cụ cài đặt biết cần NumPy, Pandas, Matplotlib và scikit-learn. |
| [requirements-lock.txt](requirements-lock.txt) | Phiên bản các thư viện đã kiểm tra. | Ghi đúng phiên bản, gồm cả phụ thuộc; runner mặc định cài theo `requirements.txt`. |
| `data/S&P 500 Stock Prices 2014-2017.csv` | Dữ liệu được cung cấp. | Đầu vào gốc: một dòng là một mã trong một phiên. |
| [src/sp500_analysis.py](src/sp500_analysis.py) | CSV gốc và tham số ở đầu file. | Tính toán và xuất tất cả CSV/PNG. Chữ trong file phục vụ chú thích, nhãn biểu đồ, lý do xử lý và thông báo terminal. |
| [src/__init__.py](src/__init__.py) | Không nhận dữ liệu phân tích. | Đánh dấu gói Python để chạy hoặc import script. |
| [test.ps1](test.ps1) | Môi trường `.venv` và hai bộ kiểm thử. | Chạy `test_analysis.py`, `test_ml.py`; báo PASS hoặc lỗi. |
| [tests/test_analysis.py](tests/test_analysis.py) | Dữ liệu nhỏ có kết quả biết trước. | Kiểm tra làm sạch, công thức, thiếu phiên, nhóm và chỉ tiêu bổ sung. |
| [tests/test_ml.py](tests/test_ml.py) | Các mẫu ML nhỏ. | Kiểm tra nhãn, ranh giới thời gian, chỉ số và sai số. |
| [tests/verify_outputs.py](tests/verify_outputs.py) | CSV/PNG đã xuất và CSV gốc. | Tính lại độc lập các kết quả bổ sung, kiểm tra số file và dữ liệu gốc; chỉ báo PASS/lỗi, không tạo báo cáo. |
| [tests/__init__.py](tests/__init__.py) | Không nhận dữ liệu phân tích. | Đánh dấu gói kiểm thử. |
| [docs/de_bai.md](docs/de_bai.md) | Nội dung đề. | Tài liệu tham chiếu khi xác định mục tiêu. |
| [docs/allowed_knowledge_reference.md](docs/allowed_knowledge_reference.md) | Danh sách kiến thức được phép. | Tài liệu tham chiếu khi viết code. |
| `Bao_cao_SP500_Bai_kiem_tra_2 (3).docx` | Báo cáo Word được cung cấp. | Dùng đối chiếu phép tính, bảng và số hình. Chương trình không tự đọc hoặc sửa file Word. |
| `.gitignore` | Quy tắc bỏ qua file. | Giúp Git bỏ qua môi trường và file tạm. |

`.venv/` chứa môi trường Python; `__pycache__/` chứa file Python tự sinh. `.cache/` chứa cache và bản lưu tài liệu/công cụ của các phiên bản trước; không phải đầu ra sử dụng của bài. `.git/` lưu lịch sử phiên bản.

## 4. Các bảng trong outputs/tables

CSV có thể mở bằng Excel. Các tỷ lệ được lưu dưới dạng số thực, ví dụ `0.05` tương ứng `5%`; cột có hậu tố `_pp` dùng đơn vị điểm phần trăm.

| File | Đầu vào | Nội dung và cách dùng |
| --- | --- | --- |
| `raw_preview.csv` | CSV gốc. | Năm dòng đầu để xem dạng dữ liệu. |
| `schema.csv` | CSV gốc. | Tên cột và kiểu dữ liệu khi đọc. |
| `missing_by_column.csv` | CSV gốc. | Số giá trị thiếu theo cột. |
| `quality_flags.csv` | Dữ liệu được kiểm tra. | Cờ lỗi từng dòng; một dòng có thể có nhiều cờ. |
| `quality_summary.csv` | Các cờ lỗi. | Tổng số dòng bị từng loại lỗi; các số có thể chồng lấn. |
| `cleaning_steps.csv` | Các bước làm sạch. | Số loại và còn lại sau từng bước; không đếm lặp dòng loại. |
| `excluded_rows.csv` | Dòng không đạt quy tắc. | Dòng bị cách ly/loại, lý do và số dòng nguồn để tra lại. |
| `clean_prices.csv` | Dữ liệu sau làm sạch. | Giá dùng được cho phân tích close, mã phiên và cờ đủ OHLCV. |
| `calendar.csv` | Ngày hợp lệ trong dữ liệu gốc. | Các ngày quan sát và số thứ tự phiên. |
| `daily_returns.csv` | Giá sạch và lịch phiên. | `observed_return`, `daily_return`, lợi suất tích lũy và chỉ số giá chuẩn hóa. |
| `extreme_returns_review.csv` | Lợi suất giữa các quan sát. | Biến động có trị tuyệt đối từ 20% để xem lại; không tự xóa các biến động này. |
| `stock_metrics_all.csv` | Chuỗi giá sạch từng mã. | CAGR, biến động, độ phủ và lý do không đạt điều kiện so sánh. |
| `stock_groups.csv` | Các mã đủ điều kiện. | Danh sách mã và nhóm A/B/C/D để so sánh cùng kỳ. |
| `group_thresholds.csv` | Chỉ tiêu của tập đủ điều kiện. | Hai ngưỡng trung bình dùng chia nhóm. |
| `group_summary.csv` | Các mã đã chia nhóm. | Số mã, tỷ trọng và chỉ tiêu trung bình của từng nhóm. |
| `selected_stocks.csv` | Các mã trong nhóm. | Tám mã xem sâu, chỉ tiêu và lý do chọn. |
| `group_annualized_comparison.csv` | Tổng hợp nhóm. | Volatility quy năm và tỷ số CAGR/volatility quy năm — Bảng 11 trong Word. |
| `selected_stock_comparison.csv` | Tám mã được chọn. | Chỉ số cuối kỳ, lợi suất tích lũy và chỉ tiêu quy năm — Bảng 13 trong Word. |
| `return_distribution_summary.csv` | Lợi suất một phiên của tập đủ điều kiện. | Số hợp lệ, số ngoài ±10%, min/max/trung bình/độ lệch chuẩn. |
| `group_threshold_distances.csv` | Chỉ tiêu và hai ngưỡng. | Khoảng cách tới ngưỡng để nhận biết các mã gần ranh giới. |
| `consistency_checks.csv` | Tổng dòng, mã, nhóm, ngưỡng và mẫu ML. | Đối soát số liệu — Bảng 14 trong Word; `passed=True` nghĩa là kiểm tra khớp. |
| `ml_sample_audit.csv` | Giá sạch được xét tạo mẫu. | Số mẫu train/test được dùng hoặc bị loại theo lý do. |
| `ml_metrics.csv` | Đáp án thật và dự đoán năm 2017. | Accuracy, Precision, Recall, F1, ROC-AUC. |
| `ml_confusion_matrices.csv` | Đáp án và dự đoán. | Số đúng/sai của từng lớp: TN, FP, FN, TP. |
| `ml_test_predictions.csv` | Các mẫu test và mô hình. | Mã, ngày, đáp án thật, dự đoán và xác suất từng mẫu. |
| `ml_confusion_matrices_normalized.csv` | Ma trận đếm đúng/sai. | Tỷ lệ từng ô chia cho tổng mẫu của lớp thực tế. |
| `ml_supplementary_metrics.csv` | Dự đoán, ma trận và ngày nhãn. | Số đúng, chênh baseline, specificity, balanced accuracy, sai số và CI — Bảng 19 trong Word. |
| `ml_daily_evaluation.csv` | Dự đoán gom theo ngày nhãn. | Số mẫu/số đúng mỗi ngày của mô hình và baseline; dùng đối chiếu sai số theo ngày. |

## 5. Các hình trong outputs/figures

Số đầu tên file tương ứng số hình trong Word. Hình 1–7 thể hiện phân tích lịch sử; Hình 8–11 thể hiện đánh giá dự đoán.

| File | Dữ liệu dùng vẽ | Nội dung |
| --- | --- | --- |
| `01_return_distribution.png` | Lợi suất một phiên của tập đủ điều kiện. | Phân phối đầy đủ và vùng phóng to ±10%. |
| `02_cagr_ranking.png` | CAGR của tập đủ điều kiện. | Mười mã CAGR cao nhất và mười mã thấp nhất. |
| `03_risk_return_groups.png` | CAGR, volatility và nhóm. | Vị trí từng mã trên hai trục lợi suất–biến động. |
| `04_group_counts.png` | Số mã trong nhóm. | Quy mô bốn nhóm. |
| `05_group_annualized_risk_return.png` | Chỉ tiêu trung bình nhóm. | CAGR, biến động quy năm và tỷ số tham khảo. |
| `06_selected_normalized_prices.png` | Giá chuẩn hóa tám mã. | Diễn biến khi cùng bắt đầu ở 100. |
| `07_selected_final_index.png` | Chỉ số cuối kỳ tám mã. | Giá cuối kỳ so với mốc đầu 100, thang logarit. |
| `08_ml_metric_comparison.png` | Bảng chỉ số ML. | So sánh ba cách dự đoán qua bốn chỉ số. |
| `09_ml_confusion_matrices.png` | Ma trận đếm đúng/sai. | Số mẫu tăng/không tăng được dự đoán đúng hoặc sai. |
| `10_ml_normalized_confusion_matrices.png` | Ma trận chuẩn hóa theo hàng. | Tỷ lệ đúng/sai trong từng lớp thực tế. |
| `11_ml_accuracy_intervals_balanced.png` | Accuracy, CI iid và balanced accuracy. | Khoảng minh họa cho Accuracy và chỉ số cân bằng hai lớp. |

## 6. Tên biến, tham số và cách học máy hoạt động

Nếu giá tăng từ 100 lên 105 ở hai phiên liền kề, lợi suất là `105/100 - 1 = 5%`. Chương trình tính riêng từng mã, tránh nối giá của hai cổ phiếu khác nhau.

| Tên | Ý nghĩa |
| --- | --- |
| `observed_return` | Lợi suất giữa hai lần quan sát cùng mã; có thể đi qua khoảng thiếu phiên. |
| `daily_return` | Lợi suất một phiên; để trống nếu hai quan sát không phải hai phiên liền kề. |
| `cagr` | Tăng trưởng bình quân năm từ giá đầu/cuối, số năm = số ngày lịch/365,25. |
| `daily_volatility` | Độ lệch chuẩn của lợi suất một phiên, `ddof=0`. |
| `annualized_volatility` | Biến động ngày × √252, chỉ là quy đổi tham khảo. |
| `normalized_price` | Chỉ số giá tại từng phiên, giá đầu kỳ = 100. |
| `final_normalized_price` | Chỉ số cuối kỳ tính trực tiếp từ giá; được đối chiếu với CAGR chưa làm tròn. |
| `cagr_to_annualized_volatility` | Tỷ số CAGR/biến động quy năm; không trừ lãi suất phi rủi ro nên không phải Sharpe. |

Tham số ở đầu script: `DATA_FILE` là đường dẫn dữ liệu, `OUTPUT_DIR` là nơi lưu kết quả, `MIN_COVERAGE=0.95` là ngưỡng độ phủ, `EXTREME_RETURN=0.20` là ngưỡng gắn cờ biến động lớn. ML dùng `ML_RANDOM_STATE=42`, `ML_N_TREES=30`, `ML_MAX_ITER=1000`; quy đổi năm dùng `TRADING_DAYS_PER_YEAR=252`, CI 95% dùng `NORMAL_95_Z=1.96`.

Bốn nhóm theo CAGR/volatility: **A cao/thấp, B cao/cao, C thấp/thấp, D thấp/cao**. Cao/thấp là so với ngưỡng trung bình của tập đủ điều kiện. Hai mã được lấy ở hai đầu CAGR mỗi nhóm để minh họa khác biệt trong nhóm.

Học máy nhận năm thông tin đã biết cuối phiên: `return_1d_t`, `range_t`, `intraday_t`, `volume_t`, `volume_change_t`. Đáp án là giá đóng cửa phiên liền kề tiếp theo tăng (`1`) hay không tăng (`0`). Giá tương lai chỉ dùng làm đáp án, không đưa vào đặc trưng.

Dữ liệu 2014–2016 dùng huấn luyện; 2017 dùng kiểm tra. Logistic Regression chuẩn hóa bằng dữ liệu train; Random Forest dùng đặc trưng gốc. Baseline luôn đoán lớp đa số của train. Mỗi lần chạy đều huấn luyện lại trên máy; hiện chỉ lưu dự đoán và các bảng đánh giá, chưa lưu mô hình ra file.

`specificity_0 = TN/(TN+FP)` và `balanced_accuracy = (specificity_0 + recall_1)/2`. SE Accuracy iid là `sqrt(p*(1-p)/N)`; CI minh họa bằng `p ± 1.96*SE`, chặn tại [0,1]. Công thức iid giả định mẫu độc lập. Bảng bổ sung có so sánh ghép cặp mô hình với baseline, gom sai số theo ngày nhãn để cho phép các mã cùng ngày phụ thuộc; vẫn giả định các ngày độc lập và chưa xử lý tự tương quan theo thời gian.

## 7. Những kết quả hiện đã có

Trên dữ liệu hiện tại: 497.472 dòng gốc, cách ly 12 dòng OHLC mâu thuẫn, còn 497.460 dòng dùng cho phân tích close. Có 505 mã được tính chỉ tiêu, 483 mã đủ điều kiện phân nhóm; A/B/C/D lần lượt có 180/77/119/107 mã. Tám mã được chọn là CB, STZ, CTSH, NVDA, GE, C, CHK, CTXS.

Phần ML có 370.378 mẫu train và 125.520 mẫu test. Accuracy của baseline, Logistic Regression và Random Forest lần lượt 52,75%, 52,71%, 50,36%; balanced accuracy lần lượt khoảng 0,5000, 0,5012, 0,5041. Các con số này là kết quả quan sát, không được ép vào thuật toán.

Phân tích cho thấy hiệu suất lịch sử khác nhau rõ giữa các mã và mức biến động cao không bảo đảm CAGR cao. Hai mô hình hiện chưa vượt baseline theo Accuracy. Giá có thể chưa điều chỉnh cổ tức/chia tách; chỉ tiêu mô tả biến động giá lịch sử, chưa chứng minh hiệu quả giao dịch. Những hướng Sharpe, drawdown, beta, phân tích ngành và walk-forward trong Word vẫn là hướng phát triển.

## 8. Kiểm thử và cách đọc đầu ra

Kiểm tra công thức và cách xử lý bằng các mẫu nhỏ:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\test.ps1
```

Sau khi chạy phân tích, đối chiếu các file thực tế:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m tests.verify_outputs
```

Để đọc kết quả, bắt đầu từ `cleaning_steps.csv` → `stock_metrics_all.csv` → `group_summary.csv` → `selected_stock_comparison.csv` → `ml_metrics.csv`. Sau đó xem các hình theo số 01–11 và tra `ml_test_predictions.csv` nếu muốn xem dự đoán cụ thể.

Các file cùng tên trong `outputs/` được ghi lại khi chạy. Hãy xem terminal xác nhận hoàn tất trước khi sử dụng; nếu dừng giữa chừng, một số file có thể vẫn thuộc lần chạy trước. README này được biên soạn riêng và cần cập nhật nếu thay đổi cách tính hoặc cấu trúc file.
