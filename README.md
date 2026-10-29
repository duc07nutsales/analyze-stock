# Phân tích S&P 500 — 2014–2017

Bài phân tích dữ liệu bằng Python: làm sạch, tính lợi suất–rủi ro, phân nhóm theo quy tắc, trực quan hóa và storytelling. **Không có học máy**, theo lựa chọn của người dùng ngày 26/10/2026.

Giải thích luồng xử lý và vai trò của mọi file/thư mục: [README_LUONG_HOAT_DONG.md](README_LUONG_HOAT_DONG.md).

## File chính

- `sp500_analysis.py`: script đầy đủ, các phần có đánh dấu `# %%` để đọc/chạy theo phần trong VS Code.
- `sp500_analysis.ipynb`: notebook chứa code và kết quả đã chạy; mở bằng Jupyter hoặc VS Code, chọn Python `.venv` rồi Run All.
- `analysis_config.py`: đường dẫn CSV/output, ngưỡng độ phủ 95%, cờ biến động 20%.
- `outputs/report.md`: báo cáo có kết quả thực, bảng tóm tắt, hình và storytelling.
- `outputs/tables/`: CSV kiểm toán, dữ liệu sạch, lợi suất, chỉ tiêu, phân nhóm và mã được chọn.
- `outputs/figures/`: 5 hình PNG.
- `test_analysis.py`: kiểm thử phát triển cho công thức, làm sạch, khoảng thiếu phiên, tách mã và ngưỡng nhóm.

## Chạy trên Windows

Mở PowerShell trong thư mục project. Lần đầu:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 -Install
```

Những lần sau:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1
```

`ExecutionPolicy Bypass` chỉ áp dụng cho tiến trình chạy lệnh, không đổi thiết lập hệ thống. Runner tạo môi trường `.venv` nếu cần, tạo thư mục đầu ra và dùng backend Matplotlib không mở cửa sổ. Việc cài thư viện cần Internet; phân tích chỉ dùng CSV cục bộ.

Chạy trực tiếp khi đã có môi trường và thư mục đầu ra:

```powershell
.\.venv\Scripts\python.exe sp500_analysis.py
.\.venv\Scripts\python.exe test_analysis.py
```

Luôn chạy từ thư mục project. Các kết quả trong `outputs` được ghi lại khi chạy; CSV gốc giữ nguyên. `requirements.txt` liệt kê thư viện; `requirements-lock.txt` ghi phiên bản của môi trường đã kiểm tra. Python đã dùng: 3.14.8. Không cần scikit-learn cho bản không ML.

Notebook yêu cầu cùng CSV và `analysis_config.py`, cùng các thư mục `outputs/tables`, `outputs/figures` (runner chuẩn bị sẵn). Đổi cấu hình thì restart kernel và Run All. Script chạy lại không cập nhật các output đã lưu trong notebook; Run All và Save notebook để cập nhật chúng.

## Cách đọc kết quả

`quality_summary.csv` đếm cờ lỗi có thể chồng lấn; `cleaning_steps.csv` là số loại tuần tự không đếm lặp. `excluded_rows.csv` giữ dòng bị cách ly và lý do; `source_row` là số dòng CSV tính cả header.

`clean_prices.csv` phục vụ phân tích close, không khẳng định tất cả OHLCV đều hoàn chỉnh. `complete_ohlcv` đánh dấu khả năng dùng các trường khác. `daily_returns.csv` phân biệt lợi suất một phiên (`daily_return`) và lợi suất giữa hai quan sát (`observed_return`); khoảng thiếu phiên không được dùng như lợi suất ngày.

`stock_metrics_all.csv` có 505 mã, kể cả mã không đạt độ phủ. Chỉ `stock_groups.csv` (483 mã) được dùng so sánh cùng kỳ. `selected_stocks.csv` có 8 mã, lý do chọn, độ phủ và khoảng ngày. `group_thresholds.csv` công bố ngưỡng số thực đầy đủ.

Kết quả lần chạy đã kiểm tra: 497.472 dòng gốc; cách ly 12 dòng OHLC mâu thuẫn, còn 497.460 dòng. Nhóm A/B/C/D có lần lượt 180/77/119/107 mã. Các số này là kết quả quan sát, không phải hằng số ép vào thuật toán.

## Phạm vi kiến thức và giới hạn

Hàm phân tích dùng NumPy, Pandas, Matplotlib và Python cơ bản có trong `allowed_knowledge_reference.md`; không dùng `.shift()`, `.pct_change()`, `.rolling()`, `.sort_values()` hoặc clustering. Sắp xếp bằng `set_index` → `sort_index` → `reset_index`; dùng mảng và phép toán cho lợi suất. Không sửa danh sách kiến thức gốc.

PowerShell, Jupyter và bộ kiểm thử là hạ tầng chạy/kiểm chứng, không phải phương pháp phân tích bổ sung. Phương pháp, công thức và các lựa chọn được ghi trong `METHODOLOGY.md`. Notebook chứa phần code phân tích; script không cần thư viện Jupyter để tính kết quả.

Giá chưa được xác nhận điều chỉnh cổ tức/chia tách. Kết quả là lợi suất giá lịch sử, không phải total return hay khuyến nghị đầu tư. Không bổ sung dữ liệu bên ngoài, không backtest và không suy diễn quan hệ nhân quả.
