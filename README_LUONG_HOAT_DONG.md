# Luồng hoạt động và ý nghĩa các file của project

Tài liệu này giải thích **chương trình chạy như thế nào** và **từng file/thư mục dùng để làm gì**. [README.md](README.md) là hướng dẫn chạy ngắn; [TONG_HOP_DU_AN.md](TONG_HOP_DU_AN.md) trình bày phương pháp và kết quả phân tích đầy đủ.

Project hiện làm phần phân tích dữ liệu và phân nhóm cổ phiếu S&P 500 giai đoạn 2014–2017. Phần học máy là tùy chọn trong đề và đã được chọn không thực hiện.

## 1. Nhìn nhanh luồng dữ liệu

```text
S&P 500 Stock Prices 2014-2017.csv    analysis_config.py
                  │                         │
                  └──────────┬──────────────┘
                             ▼
                     sp500_analysis.py
                             │
              1. Đọc CSV và kiểm toán dữ liệu
                             ▼
              2. Làm sạch, lập lịch phiên
                             ▼
              3. Tính lợi suất, rủi ro, độ phủ
                             ▼
              4. Lọc mã đủ điều kiện, phân nhóm
                             ▼
              5. Chọn mã, vẽ hình, viết báo cáo
                             │
              ┌──────────────┼────────────────┐
              ▼              ▼                ▼
    outputs/tables/   outputs/figures/   outputs/report.md
```

`run.ps1` chuẩn bị môi trường và gọi `sp500_analysis.py`. `sp500_analysis.ipynb` chứa cùng phần code phân tích ở dạng notebook để xem từng bước cùng kết quả đã chạy; notebook cũng đọc CSV và ghi vào các đầu ra nêu trên khi chọn **Run All**. Hai cách chạy là hai điểm vào của cùng quy trình, không phải hai bộ dữ liệu khác nhau.

## 2. Luồng khi chạy script

1. **Chuẩn bị:** [run.ps1](run.ps1) chuyển về thư mục project, tạo `.venv` nếu chưa có, cài thư viện khi dùng tùy chọn `-Install`, rồi tạo `outputs/tables/`, `outputs/figures/` và cache Matplotlib. Nó đặt backend không mở cửa sổ trước khi chạy Python.
2. **Đọc đầu vào:** `load_data()` trong [sp500_analysis.py](sp500_analysis.py) đọc CSV theo tên ở [analysis_config.py](analysis_config.py), in số dòng và tên cột.
3. **Kiểm toán và làm sạch:** `clean_data()` kiểm tra thiếu/trùng/giá trị bất hợp lệ/quan hệ OHLC, chuẩn hóa mã và ngày, ghi cờ lỗi, cách ly dòng không dùng được cho phân tích close, rồi lập lịch phiên. Dữ liệu CSV gốc không bị ghi đè.
4. **Tính chỉ tiêu:** `analyze_prices()` xử lý từng mã theo thứ tự ngày. `price_metrics()` tính lợi suất một phiên, lợi suất tích lũy, giá chuẩn hóa, lợi suất trung bình, volatility và CAGR. Lợi suất qua khoảng thiếu phiên được lưu riêng, không đưa vào chỉ tiêu “một phiên”.
5. **Chọn tập so sánh:** script yêu cầu hai đầu kỳ chung, ít nhất 95% phiên có close hợp lệ và ít nhất 95% cặp phiên có daily return hợp lệ. Bảng tất cả mã vẫn lưu cả những mã không đạt và lý do.
6. **Phân nhóm:** `group_stocks()` tính ngưỡng trung bình CAGR và volatility của tập đủ điều kiện, gán bốn nhóm A/B/C/D và chọn hai mã ở hai đầu CAGR của mỗi nhóm để xem sâu.
7. **Trực quan hóa và diễn giải:** `make_figures()` tạo năm hình PNG. `write_report()` dùng các số vừa tính để viết [outputs/report.md](outputs/report.md), gồm bảng tóm tắt, diễn giải, storytelling và giới hạn dữ liệu.

Hàm `main()` gọi các bước theo thứ tự trên. Script dừng nếu không có đủ ngày/giá hoặc không có mã nào đạt tiêu chí so sánh. Nếu một lần chạy dừng sớm, các file còn lại trong `outputs/` có thể là kết quả từ lần chạy trước; cần xem thông báo trên terminal trước khi sử dụng chúng.

## 3. Sơ đồ file và thư mục

```text
chip project/
├── de_bai.md
├── allowed_knowledge_reference.md
├── REQUIREMENTS.md
├── METHODOLOGY.md
├── SP500_PROJECT_PLAN.md
├── README.md
├── README_LUONG_HOAT_DONG.md
├── TONG_HOP_DU_AN.md
├── S&P 500 Stock Prices 2014-2017.csv
├── analysis_config.py
├── sp500_analysis.py
├── sp500_analysis.ipynb
├── run.ps1
├── requirements.txt
├── requirements-lock.txt
├── test_analysis.py
├── outputs/
│   ├── report.md
│   ├── validation.md
│   ├── tables/
│   └── figures/
├── .venv/             (tạo trên máy khi cài môi trường)
├── .cache/            (cache và công cụ hỗ trợ phát triển)
└── __pycache__/       (cache Python, tự sinh khi import)
```

### 3.1. Tài liệu đầu vào và quy định

| File | Ý nghĩa |
| --- | --- |
| [de_bai.md](de_bai.md) | Đề bài: yêu cầu nhập/xuất, làm sạch, biến đổi, vẽ biểu đồ, insight và báo cáo Python; ML là tùy chọn. |
| [allowed_knowledge_reference.md](allowed_knowledge_reference.md) | Danh sách kiến thức và lời gọi thư viện được phép dùng trong code phân tích. |
| [REQUIREMENTS.md](REQUIREMENTS.md) | Chuyển đề bài thành yêu cầu và điều kiện hoàn thành của project. |
| [METHODOLOGY.md](METHODOLOGY.md) | Ghi công thức, chính sách làm sạch, tiêu chí độ phủ, quy tắc nhóm và những giới hạn cần diễn giải. |
| [SP500_PROJECT_PLAN.md](SP500_PROJECT_PLAN.md) | Kế hoạch ban đầu và cập nhật trạng thái triển khai. Những mục ML trong bản kế hoạch chỉ là thiết kế tham khảo. |
| [S&P 500 Stock Prices 2014-2017.csv](<S&P 500 Stock Prices 2014-2017.csv>) | Dữ liệu đầu vào gốc; mỗi dòng tương ứng một mã trong một ngày giao dịch. |

### 3.2. Code, cấu hình và hướng dẫn

| File | Ý nghĩa |
| --- | --- |
| [analysis_config.py](analysis_config.py) | Tên CSV, thư mục kết quả, ngưỡng độ phủ `0.95` và ngưỡng gắn cờ biến động `0.20`. |
| [sp500_analysis.py](sp500_analysis.py) | Code phân tích chính; các khối `# %%` chia thành nhập dữ liệu, làm sạch, chỉ tiêu, phân nhóm, biểu đồ và báo cáo. |
| [sp500_analysis.ipynb](sp500_analysis.ipynb) | Bản notebook có Markdown giải thích, code từng bước, bảng và hình đã chạy. Mở bằng Jupyter hoặc VS Code. |
| [run.ps1](run.ps1) | Lệnh chạy trên Windows; chuẩn bị thư mục/môi trường và gọi script chính. |
| [requirements.txt](requirements.txt) | Tên các thư viện cần cài để chạy phân tích và notebook. |
| [requirements-lock.txt](requirements-lock.txt) | Phiên bản thư viện đã ghi nhận ở môi trường kiểm tra. |
| [test_analysis.py](test_analysis.py) | Kiểm thử với dữ liệu nhỏ cho công thức, xử lý lỗi, khoảng thiếu phiên và quy tắc phân nhóm. |
| [README.md](README.md) | Hướng dẫn ngắn để cài, chạy và đọc kết quả. |
| [TONG_HOP_DU_AN.md](TONG_HOP_DU_AN.md) | Mô tả toàn bộ bài làm và kết quả cụ thể. |
| `README_LUONG_HOAT_DONG.md` | File hiện tại: giải thích luồng hoạt động và vai trò các file. |

### 3.3. Thư mục kết quả

| Đường dẫn | Ý nghĩa |
| --- | --- |
| [outputs/report.md](outputs/report.md) | Báo cáo được sinh từ lần chạy script/notebook: số liệu, hình liên kết, diễn giải và storytelling. |
| [outputs/validation.md](outputs/validation.md) | Bản ghi kiểm chứng của phiên bản đã chạy; không tự cập nhật khi chạy lại script. |
| `outputs/tables/` | Các CSV về dữ liệu, chất lượng, chỉ tiêu và nhóm; xem bảng dưới. |
| `outputs/figures/` | Năm ảnh biểu đồ PNG; được liên kết trong báo cáo. |

Các file trong `outputs/` cùng tên sẽ được ghi lại khi chạy thành công các bước tương ứng. File `sp500_analysis.ipynb` đã lưu kết quả của một lần chạy; **chạy script không cập nhật output nằm trong notebook**. Để đồng bộ notebook sau khi đổi dữ liệu/cấu hình, hãy chọn Run All và Save notebook. Tài liệu tổng hợp và bản ghi kiểm chứng cũng cần được rà soát lại nếu kết quả đổi.

## 4. Đọc các bảng CSV theo thứ tự nào?

### 4.1. Chất lượng dữ liệu và làm sạch

| File trong `outputs/tables/` | Nội dung, cách dùng |
| --- | --- |
| `schema.csv` | Tên cột và kiểu dữ liệu được đọc. |
| `missing_by_column.csv` | Số giá trị thiếu theo từng cột. |
| `quality_flags.csv` | Cờ kiểm toán ở mức từng dòng nguồn. Một dòng có thể có nhiều cờ. |
| `quality_summary.csv` | Tổng số dòng bị gắn từng loại cờ; các tổng có thể chồng lấn. |
| `cleaning_steps.csv` | Số dòng bị loại lần lượt qua từng bước; phù hợp để đối soát raw → clean. |
| `excluded_rows.csv` | Những dòng bị cách ly hoặc loại trùng, kèm lý do chính và `source_row` để tra lại CSV. |
| `clean_prices.csv` | Dòng dùng được cho phân tích close, đã sắp theo mã/ngày; có `session_id` và `complete_ohlcv`. |
| `calendar.csv` | Các ngày có quan sát và mã thứ tự `session_id`. |

`clean_prices.csv` vẫn có thể chứa dòng thiếu open/high/low hoặc volume, miễn close hợp lệ và OHLC quan sát được không mâu thuẫn. `complete_ohlcv=False` nhắc rằng dòng đó không phù hợp cho một phép tính cần đầy đủ các trường này.

### 4.2. Chỉ tiêu và phân nhóm

| File trong `outputs/tables/` | Nội dung, cách dùng |
| --- | --- |
| `daily_returns.csv` | Chuỗi close, `observed_return`, `daily_return`, cờ khoảng thiếu, lợi suất tích lũy và giá chuẩn hóa. |
| `extreme_returns_review.csv` | Các biến động giữa hai quan sát có trị tuyệt đối từ 20% trở lên để rà soát; không phải danh sách bị xóa. |
| `stock_metrics_all.csv` | Chỉ tiêu theo mã cho toàn bộ dữ liệu; có độ phủ, cờ `eligible` và `exclusion_reason`. |
| `stock_groups.csv` | Chỉ các mã đủ điều kiện so sánh cùng kỳ, kèm nhãn nhóm A/B/C/D. |
| `group_thresholds.csv` | Hai ngưỡng dùng để phân nhóm và quy tắc xử lý bằng ngưỡng. |
| `group_summary.csv` | Số mã và CAGR/volatility trung bình của từng nhóm. |
| `selected_stocks.csv` | Các mã được chọn để xem sâu, kèm lý do chọn và chỉ tiêu liên quan. |

Vì `stock_metrics_all.csv` chứa cả mã không đạt độ phủ, hãy dùng **`stock_groups.csv`** khi xếp hạng hoặc so sánh trên kỳ chung. `daily_return` chỉ tính cho hai phiên liền kề; `observed_return` có thể trải qua khoảng thiếu phiên.

### 4.3. Năm hình PNG

| File trong `outputs/figures/` | Nội dung |
| --- | --- |
| `01_return_distribution.png` | Phân phối lợi suất một phiên và bản phóng to ±10%. |
| `02_cagr_ranking.png` | Mười mã có CAGR thấp nhất và mười mã cao nhất trong tập đủ điều kiện. |
| `03_risk_return_groups.png` | Quan hệ CAGR–volatility, màu nhóm và hai đường ngưỡng. |
| `04_group_counts.png` | Số mã trong từng nhóm. |
| `05_selected_normalized_prices.png` | Giá chuẩn hóa về 100 của những mã được chọn, chia theo nhóm. |

## 5. Cách chạy và đọc kết quả

Mở PowerShell tại thư mục project. Lần đầu, hoặc khi cần cài thư viện:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 -Install
```

Khi đã có `.venv` và thư viện:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1
```

Sau khi lệnh hoàn thành, đọc theo trình tự: `outputs/tables/cleaning_steps.csv` → `outputs/tables/stock_metrics_all.csv` → `outputs/tables/group_summary.csv` → `outputs/report.md`. Muốn xem code cùng kết quả từng phần, mở notebook và chọn **Run All**. Muốn kiểm tra các trường hợp dữ liệu nhỏ:

```powershell
.\.venv\Scripts\python.exe test_analysis.py
```

`-Install` cần kết nối để cài thư viện. Bản phân tích không gọi nguồn dữ liệu ngoài. `-ExecutionPolicy Bypass` chỉ áp dụng cho tiến trình PowerShell đang chạy. Chạy từ thư mục project để các đường dẫn tương đối tới CSV và `outputs/` hoạt động đúng.

## 6. Thư mục tự sinh và những lưu ý khi chia sẻ project

| Thư mục/file | Vai trò |
| --- | --- |
| `.venv/` | Môi trường Python cục bộ; có thể tạo lại bằng `run.ps1 -Install`. |
| `.cache/` | Cache Matplotlib/Jupyter và công cụ phát triển của lần làm bài; không phải dữ liệu đầu vào hay kết quả học thuật. |
| `__pycache__/` | Bytecode Python tự sinh sau khi import; không cần đọc để hiểu project. |
| `.gitignore` | Danh sách những thư mục cache và môi trường không nên đưa vào Git. |

Để người khác chạy lại bài, cần giữ CSV gốc, các file `.py`, `run.ps1`, `requirements.txt` và các tài liệu phương pháp. Để xem ngay kết quả đã kiểm tra, giữ thêm notebook và toàn bộ `outputs/`, đặc biệt thư mục `outputs/figures/` vì báo cáo Markdown liên kết hình bằng đường dẫn tương đối. Giá chưa được xác nhận điều chỉnh cổ tức/chia tách, nên các chỉ tiêu trong bài là biến động **giá được cung cấp**, không phải total return.
