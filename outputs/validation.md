# Kiểm chứng lần chạy

- SHA-256 CSV gốc giữ nguyên: `2200EA7C7B98791314CB5B4A3072B4D4166DA1ED78A3E3E178339199109837D2`.
- Công thức được tính lại độc lập bằng datetime/statistics cho **505 mã**, sai lệch <1e-12.
- Đối soát dòng raw = clean + excluded; không có khóa trùng sau xử lý; source_row không chồng lấn.
- Daily return không nối qua mã hoặc khoảng thiếu phiên; observed_return giữ biến động giữa hai quan sát.
- 483 mã đạt điều kiện, tổng bốn nhóm khớp; 8 mã được chọn không trùng.
- Đã đối chiếu các lời gọi API của sp500_analysis.py với danh sách hàm cho phép; không có API ngoài danh sách kiểm tra.
- Notebook đồng bộ 6 phần mô tả với script và phần ML với module; tất cả cell đã chạy, không có output lỗi, có 7 hình nhúng.
- Đã xem trực tiếp 7 PNG: nhãn, đơn vị và chữ tiếng Việt rõ; biểu đồ giá dùng tick theo năm.
- Bộ fixture test_analysis.py kiểm tra công thức, một quan sát, khoảng thiếu phiên, thiếu OHL/volume, trùng hoàn toàn, khóa xung đột, giá lỗi, ngày lỗi, mã trắng và hòa ngưỡng.

Đây là bằng chứng cho phiên bản đã chạy. Nếu đổi dữ liệu hoặc tham số, chạy lại phân tích và kiểm tra tương ứng.

## Phần ML mở rộng ngày 06/11/2026

- Đối chiếu 125.520 mẫu test với `clean_prices.csv`: đúng mã, đúng phiên liền kề và đúng nhãn tăng/không tăng.
- Kiểm toán mẫu cộng lại đúng 497.460 dòng clean; train 370.378, test 125.520.
- Tính lại TN/FP/FN/TP, Accuracy, Precision, Recall và F1 từ dự đoán từng mẫu; khớp CSV metrics tới 1e-12.
- Xác suất của hai mô hình nằm trong [0, 1]; baseline đoán nhãn đa số train.
- Notebook có 7 code cell đã chạy không lỗi, 7 hình nhúng và phần báo cáo Markdown cuối.
- Các chỉ số được giữ nguyên khi hai mô hình không vượt baseline về Accuracy.
