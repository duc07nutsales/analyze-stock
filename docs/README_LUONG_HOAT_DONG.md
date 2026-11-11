# Luồng hoạt động của dự án

Xem [cấu trúc thư mục](CAU_TRUC_DU_AN.md) để biết mỗi file nằm ở đâu và dùng để làm gì. [README.md](../README.md) có lệnh chạy ngắn; [TONG_HOP_DU_AN.md](TONG_HOP_DU_AN.md) trình bày phương pháp và kết quả đầy đủ.

```text
data/CSV + tham số đầu src/sp500_analysis.py
                ↓
src/sp500_analysis.py
  1. Đọc CSV, kiểm toán thiếu/trùng/giá không hợp lệ
  2. Làm sạch, đánh dấu phiên giao dịch và ghi bảng chất lượng
  3. Tính lợi suất, CAGR, độ biến động, độ phủ
  4. Chọn mã đủ điều kiện và phân bốn nhóm theo quy tắc
  5. Vẽ năm biểu đồ, viết phần phân tích mô tả
                ↓
src/sp500_analysis.py (phần học máy)
  6. Tạo đặc trưng và nhãn cho phiên kế tiếp của cùng mã
  7. Train bằng 2014–2016; test trên 2017
  8. So sánh Logistic Regression, Random Forest với baseline
                ↓
outputs/tables/ + outputs/figures/ + outputs/report.md
```

`run.ps1` chuyển về thư mục gốc dự án, chuẩn bị môi trường và gọi `src.sp500_analysis`. File này chạy phần học máy sau phân tích mô tả. Notebook trong `notebooks/` cho phép xem và chạy từng phần của cùng quy trình; chọn **Run All** khi đã mở project từ thư mục gốc.

## Ý nghĩa từng giai đoạn

| Giai đoạn | Đầu vào | Đầu ra cần xem |
| --- | --- | --- |
| Kiểm toán, làm sạch | CSV gốc trong `data/` | `outputs/tables/quality_summary.csv`, `cleaning_steps.csv`, `excluded_rows.csv`, `clean_prices.csv` |
| Phân tích | Bảng giá sạch | `daily_returns.csv`, `stock_metrics_all.csv` |
| Phân nhóm | Chỉ tiêu của mã đủ độ phủ | `stock_groups.csv`, `group_thresholds.csv`, `group_summary.csv`, `selected_stocks.csv` |
| Trực quan hóa | Lợi suất, chỉ tiêu và nhóm | Năm ảnh `01_` đến `05_` trong `outputs/figures/` |
| Học máy | Giá sạch theo từng mã, phiên liền kề | `ml_sample_audit.csv`, `ml_metrics.csv`, `ml_confusion_matrices.csv`, `ml_test_predictions.csv` và hai ảnh `ml_` |
| Báo cáo | Các bảng và hình vừa tính | `outputs/report.md` với diễn giải và storytelling |

Phần phân nhóm xếp cổ phiếu theo CAGR và độ biến động lịch sử. Phần học máy là thử nghiệm **dự đoán chiều giá phiên kế tiếp**, được đánh giá riêng trên năm 2017; nhãn thực chỉ dùng để huấn luyện/đo kết quả, không đưa vào đặc trưng của cùng mẫu.

Các file trong `outputs/` được ghi lại khi chạy tương ứng. Nếu chạy dừng giữa chừng, một số file có thể vẫn thuộc lần trước; xem terminal trước khi dùng kết quả. `outputs/validation.md` và `TONG_HOP_DU_AN.md` là bản ghi/tổng hợp của phiên bản đã kiểm chứng, không tự cập nhật theo lần chạy mới. Notebook cũng có output lưu sẵn; chạy script không đổi output đó. Phần Markdown cuối notebook là bản chụp, còn báo cáo hiện hành ở `outputs/report.md`.
