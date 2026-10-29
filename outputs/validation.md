# Kiểm chứng lần chạy

- SHA-256 CSV gốc giữ nguyên: `2200EA7C7B98791314CB5B4A3072B4D4166DA1ED78A3E3E178339199109837D2`.
- Công thức được tính lại độc lập bằng datetime/statistics cho **505 mã**, sai lệch <1e-12.
- Đối soát dòng raw = clean + excluded; không có khóa trùng sau xử lý; source_row không chồng lấn.
- Daily return không nối qua mã hoặc khoảng thiếu phiên; observed_return giữ biến động giữa hai quan sát.
- 483 mã đạt điều kiện, tổng bốn nhóm khớp; 8 mã được chọn không trùng.
- Đã đối chiếu các lời gọi API của sp500_analysis.py với danh sách hàm cho phép; không có API ngoài danh sách kiểm tra.
- Notebook đồng bộ 6 phần code với script; tất cả cell đã chạy, không có output lỗi, có 5 hình nhúng.
- Đã xem trực tiếp 5 PNG: nhãn, đơn vị và chữ tiếng Việt rõ; biểu đồ giá dùng tick theo năm.
- Bộ fixture test_analysis.py kiểm tra công thức, một quan sát, khoảng thiếu phiên, thiếu OHL/volume, trùng hoàn toàn, khóa xung đột, giá lỗi, ngày lỗi, mã trắng và hòa ngưỡng.

Đây là bằng chứng cho phiên bản đã chạy. Nếu đổi dữ liệu hoặc tham số, chạy lại phân tích và kiểm tra tương ứng.
