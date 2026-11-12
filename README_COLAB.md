# Hướng dẫn chạy project trên Google Colab

## 1. Mở project

Mở đường link Google Colab được chia sẻ và đăng nhập tài khoản Google. Chọn **File → Save a copy in Drive** để lưu một bản notebook vào Google Drive của bạn.

## 2. Chạy chương trình

Chọn **Connect (Kết nối)** ở góc trên bên phải. Sau khi project đã có trong thư mục `/content/analyze-stock`, notebook cần có hai ô code sau, theo đúng thứ tự. Nếu người chia sẻ đã thêm sẵn thì không cần thêm lại.

**Ô 1 — mở thư mục project và cài thư viện:**

```python
%cd /content/analyze-stock
%pip install -r requirements.txt
```

**Ô 2 — tạo thư mục kết quả và chạy file Python:**

```python
%cd /content/analyze-stock

import os
from pathlib import Path

for folder in ["outputs/tables", "outputs/figures"]:
    Path(folder).mkdir(parents=True, exist_ok=True)

os.environ["MPLBACKEND"] = "Agg"

!python -u -m src.sp500_analysis
```

Chọn **Runtime → Run all (Chạy tất cả)** để chạy các ô theo thứ tự. Lệnh cuối của ô 2 gọi file `src/sp500_analysis.py`. Run all chỉ chạy các ô trong notebook, không tự chạy những file đang mở ở bảng Files.

Chờ tất cả các ô chạy xong; quá trình có thể mất vài phút.

Khi hoàn tất, chương trình hiển thị:

```text
Hoàn thành. Bảng CSV: outputs/tables; biểu đồ PNG: outputs/figures.
```

Nếu có ô báo lỗi, xử lý lỗi trước khi sử dụng kết quả.

## 3. Xem và tải kết quả

Mở biểu tượng **Files (Tệp)** ở thanh bên trái, tìm thư mục `outputs` trong thư mục project:

- `tables`: chứa 28 bảng kết quả CSV, có thể mở bằng Excel.
- `figures`: chứa 11 biểu đồ PNG.

Nhấp chuột phải vào file cần lấy và chọn **Download (Tải xuống)**.

Hãy tải kết quả trước khi kết thúc phiên Colab vì các file trong phiên chạy chỉ được lưu tạm thời. Lưu notebook vào Drive không tự lưu các file kết quả này.
