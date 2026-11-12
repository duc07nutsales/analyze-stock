# Hướng dẫn chạy project trên Google Colab

## 1. Mở project

Mở đường link Google Colab được chia sẻ và đăng nhập tài khoản Google. Chọn **File → Save a copy in Drive** để lưu một bản notebook vào Google Drive của bạn.

## 2. Chạy chương trình

Chọn **Connect (Kết nối)** ở góc trên bên phải, sau đó chọn **Runtime → Run all (Chạy tất cả)**.

Các ô lệnh sẽ chạy lần lượt để chuẩn bị dữ liệu, cài thư viện và thực hiện phân tích. Chờ tất cả các ô chạy xong; quá trình có thể mất vài phút.

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
