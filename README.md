# Phân tích dữ liệu S&P 500 (2014–2017)

Bài làm đọc dữ liệu giá cổ phiếu, kiểm toán và làm sạch, tính lợi suất/rủi ro, phân nhóm theo quy tắc, vẽ biểu đồ và viết báo cáo có diễn giải. Phần học máy tùy chọn thử dự đoán chiều giá phiên kế tiếp và so sánh với cách dự đoán đơn giản.

Đề gốc: [de_bai.md](docs/de_bai.md). Giải thích từng thư mục và quan hệ giữa các file: [CAU_TRUC_DU_AN.md](docs/CAU_TRUC_DU_AN.md). Xem [luồng hoạt động](docs/README_LUONG_HOAT_DONG.md), [phương pháp](docs/METHODOLOGY.md), [kế hoạch học máy](docs/README_KE_HOACH_HOC_MAY.md) và [bài tổng hợp](docs/TONG_HOP_DU_AN.md).

## Chạy trên Windows

Mở PowerShell ở thư mục gốc dự án. Lần đầu hoặc khi cần cài thư viện:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 -Install
```

Những lần sau:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1
```

Runner chuẩn bị `.venv`, thư mục kết quả và chạy module `src.sp500_analysis`. Phân tích chỉ đọc CSV cục bộ trong `data/`. Có thể chạy trực tiếp từ **thư mục gốc** khi đã cài môi trường:

```powershell
.\.venv\Scripts\python.exe -m src.sp500_analysis
powershell -NoProfile -ExecutionPolicy Bypass -File .\test.ps1
```

Mở [notebook](notebooks/sp500_analysis.ipynb) bằng VS Code/Jupyter, chọn kernel `.venv` và **Run All** để xem từng phần. Notebook đọc dữ liệu từ `data/`, dùng cấu hình `src/analysis_config.py` và ghi vào `outputs/`. Chạy script không cập nhật các output đã lưu trong notebook; Run All và Save sẽ cập nhật chúng. Phần Markdown báo cáo cuối notebook là bản chụp, còn báo cáo mới nhất do lần chạy tạo ra ở [outputs/report.md](outputs/report.md).

## Đọc kết quả

- [Báo cáo chính](outputs/report.md): số liệu, biểu đồ, diễn giải và storytelling.
- [Bảng dữ liệu](outputs/tables/): kiểm toán, dữ liệu sạch, chỉ tiêu, nhóm và đánh giá ML.
- [Biểu đồ](outputs/figures/): năm hình phân tích và hai hình đánh giá ML.
- [Bản ghi kiểm chứng](outputs/validation.md): kết quả kiểm tra của phiên bản đã thực hiện, không tự cập nhật khi chạy lại.

Kết quả trên dữ liệu hiện có: 497.472 dòng gốc, 497.460 dòng sạch, 483 mã đủ điều kiện phân nhóm. Trong thử nghiệm ML, Accuracy của baseline là 52,75%, Logistic Regression 52,71% và Random Forest 50,36%; hai mô hình chưa vượt baseline theo chỉ số này. Các con số có thể thay đổi nếu thay dữ liệu hoặc cấu hình.
