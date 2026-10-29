# REQUIREMENTS — S&P 500 Stock Prices (2014–2017)

**Phiên bản:** 1.1 — bắt đầu triển khai theo yêu cầu ngày 26/10/2026  
**Trạng thái:** Đã triển khai và chạy script Python cùng notebook trên toàn bộ CSV; phạm vi không ML.  

**Phạm vi đã xác nhận ngày 26/10/2026:** Người dùng chọn **chỉ phân tích và phân nhóm**, không triển khai học máy. Các mục ML bên dưới chỉ lưu thiết kế mở rộng, không phải đầu ra phải nộp của phiên bản này. Tên báo cáo triển khai: *Phân tích lợi suất và rủi ro cổ phiếu S&P 500 giai đoạn 2014–2017*.
**Tài liệu liên quan:** `SP500_PROJECT_PLAN.md`, `METHODOLOGY.md`, `allowed_knowledge_reference.md`, `de_bai.md`.

## 1. Phạm vi và mục tiêu

**Tên đề tài hiện tại:** Phân tích lợi suất và rủi ro cổ phiếu S&P 500 giai đoạn 2014–2017: Hàm ý đối với lựa chọn đầu tư.

**Dữ liệu chính:** CSV cục bộ có 497.472 dòng, 505 mã; các cột `symbol,date,open,high,low,close,volume`; ngày từ 02/01/2014 đến 29/12/2017. Đã kiểm tra độ phủ và chất lượng; chưa xác minh tình trạng điều chỉnh giá.

**Phạm vi được thống nhất:** Phân tích tổng quan tất cả mã **đủ điều kiện** và phân tích sâu 5–10 mã theo tiêu chí minh bạch. Không coi mẫu cổ phiếu trong tệp là chỉ số S&P 500 lịch sử hoàn chỉnh. Không dùng dữ liệu bên ngoài để bổ sung biến phân tích.

## 2. Yêu cầu bắt buộc từ đề giảng viên (G)

| ID | Yêu cầu | Minh chứng cần có | Ưu tiên |
|---|---|---|---|
| G-01 | Nhập / xuất dữ liệu bằng Python | Đọc dữ liệu gốc; có đầu ra có thể kiểm tra | Bắt buộc |
| G-02 | Tiền xử lý, làm sạch dữ liệu | Thống kê lỗi, quy tắc xử lý, dữ liệu sạch | Bắt buộc |
| G-03 | Biến đổi dữ liệu để phân tích | Bảng đặc trưng / tổng hợp / so sánh | Bắt buộc |
| G-04 | Trực quan hóa dữ liệu | Biểu đồ có tiêu đề, nhãn, đơn vị | Bắt buộc |
| G-05 | Tổng hợp insight, gợi ý dựa trên dữ liệu | Nhận xét gắn với số liệu và hạn chế | Bắt buộc |
| G-06 | Báo cáo Python chia theo các phần bài giảng, có giải thích, phân tích và storytelling cuối | Notebook/báo cáo liền mạch | Bắt buộc |
| G-07 | Dùng học máy dự đoán từ dữ liệu | Mô hình, kết quả kiểm thử | **Tùy chọn theo đề** |

> Đây là chuyển hóa nội dung yêu cầu của tài liệu đề bài, **không phải thang điểm hoặc số biểu đồ tối thiểu do giảng viên quy định**. Chưa có rubric chấm điểm chi tiết.

## 3. Yêu cầu nội bộ của project (P)

| ID | Yêu cầu | Đầu ra / điều kiện hoàn thành | Trạng thái |
|---|---|---|---|
| P-01 | Xác nhận cấu trúc dữ liệu và khoảng ngày | Danh sách cột thực, kiểu dữ liệu, thời gian, mã; ghi vấn đề phát hiện | Đã hoàn thành |
| P-02 | Kiểm tra missing / duplicate / giá và volume bất hợp lệ | Bảng trước–sau làm sạch, số dòng bị loại và lý do | Đã hoàn thành |
| P-03 | Giữ dữ liệu gốc riêng với dữ liệu xử lý | Không ghi đè raw; xuất bản clean | Đã hoàn thành |
| P-04 | Tính daily return, cumulative price return, average daily return, daily volatility, CAGR | Bảng chỉ số theo mã; nêu công thức và điều kiện hợp lệ | Đã hoàn thành |
| P-05 | So sánh công bằng giữa các mã | Tiêu chí độ phủ và kỳ quan sát; các mã không đủ điều kiện được tách rõ | Đã hoàn thành |
| P-06 | Trình bày phân phối lợi suất, xếp hạng CAGR, quan hệ CAGR–volatility và đường giá chuẩn hóa | Biểu đồ và giải thích | Đã hoàn thành |
| P-07 | Phân nhóm theo quy tắc (không dùng K-Means/PCA) | 4 nhóm theo CAGR/volatility; bảng nhóm và scatter | Đã hoàn thành |
| P-08 | Phân tích sâu 5–10 mã được chọn theo quy tắc công bố trước | Bảng lý do chọn mã và biểu đồ so sánh | Đã hoàn thành |
| P-09 | Viết storytelling và hàm ý sàng lọc, không khẳng định lợi nhuận tương lai | Kết luận đối chiếu số liệu, nêu hạn chế | Đã hoàn thành |
| P-10 | Nếu chọn làm ML: dự đoán tăng/không tăng phiên tiếp theo | Logistic Regression, Random Forest, baseline, đánh giá out-of-time | **Có điều kiện** |

## 4. Yêu cầu kỹ thuật / giới hạn bắt buộc (T)

| ID | Quy định | Cách kiểm chứng |
|---|---|---|
| T-01 | Chỉ dùng thư viện, hàm, phương thức và cú pháp được **liệt kê cụ thể** trong `allowed_knowledge_reference.md` | Đối chiếu mọi lời gọi trong notebook với file gốc |
| T-02 | Không dùng K-Means, PCA, Silhouette, XGBoost hoặc thư viện bổ sung chưa được phép | Kiểm tra import và lời gọi |
| T-03 | Không tự động dùng `.shift()`, `.rolling()`, `.pct_change()`, `.cummax()`, `.sort_values()`, `.head()`, `.info()`, `.describe()` nếu không được cho phép trong file gốc | Dùng phép toán/indexing/vòng lặp/`sort_index` đã học |
| T-04 | Không đưa thông tin tương lai vào biến dự đoán; chia train/test theo thời gian | Kiểm tra mốc thời gian và cách tạo nhãn |
| T-05 | Nếu chuẩn hóa, `.fit()`/`.fit_transform()` chỉ trên train; `.transform()` trên test | Kiểm tra pipeline |
| T-06 | Khi cần sửa phần dữ liệu trích xuất, tạo bản sao `.copy()` | Kiểm tra việc cắt lát và gán |
| T-07 | Phép ngẫu nhiên phải có `random_state` hoặc `seed` theo quy định tài liệu | Kiểm tra mô hình / dữ liệu |
| T-08 | Mỗi biểu đồ có title, nhãn trục, đơn vị; biểu đồ cột giá trị tuyệt đối bắt đầu từ 0 | Kiểm tra biểu đồ |
| T-09 | Không coi kết quả phân tích giá là total return khi thiếu adjusted prices/dividends | Kiểm tra tên chỉ tiêu, kết luận |

**Thứ tự ưu tiên khi có xung đột:** đề của giảng viên → `allowed_knowledge_reference.md` → các quyết định đã thống nhất → kế hoạch chi tiết. Khi chưa chắc, dừng thao tác cụ thể và ghi cần làm rõ; không tự mở rộng danh sách hàm.

## 5. Yêu cầu đầu ra / nghiệm thu từng phần

### Deliverable D-01 — Dữ liệu và kiểm toán chất lượng
- [x] Ghi được schema và phạm vi CSV thực tế.
- [x] Có bảng kiểm lỗi theo loại (thiếu, khóa `ticker + date` trùng, giá không dương, volume âm, OHLC không nhất quán).
- [x] Có số lượng trước/sau và chính sách xử lý từng lỗi.
- [x] Bản dữ liệu xử lý không ghi đè raw.

### Deliverable D-02 — Bảng chỉ tiêu tài chính và trực quan
- [x] Công thức 5 chỉ tiêu ghi rõ trong Markdown.
- [x] Daily return được tính **bên trong từng mã**, đúng thứ tự phiên.
- [x] Có tiêu chí độ phủ và chính sách mã có thiếu dữ liệu.
- [x] Có bảng so sánh mã và ít nhất những **loại hình** biểu đồ đã đề xuất (số lượng cụ thể là mục tiêu nội bộ, không phải quy định giảng viên).
- [x] Không gọi dữ liệu OHLC thường là adjusted total return nếu chưa chứng minh được.

### Deliverable D-03 — Phân nhóm theo quy tắc
- [x] Công bố chỉ tiêu, ngưỡng và cách xử lý bằng ngưỡng trước khi diễn giải nhóm.
- [x] Có tổng số mã thuộc mỗi nhóm và tóm tắt đặc điểm.
- [x] Ghi rõ đây **không phải phân cụm học máy**.

### Deliverable D-04 — ML (chỉ khi chọn phạm vi mở rộng)
- [ ] Nhãn dự đoán ngày tiếp theo theo cùng mã; loại các dòng không thể gắn nhãn.
- [ ] Train theo giai đoạn trước và test theo giai đoạn sau, tránh nhãn train vượt ranh giới.
- [ ] Có mô hình Logistic Regression và Random Forest, cùng baseline xác lập từ train.
- [ ] Có bảng Accuracy, Precision, Recall, F1 tự tính, Confusion Matrix; ROC-AUC khi có xác suất phù hợp.
- [ ] Nêu rõ giới hạn của kết quả dự đoán.

### Deliverable D-05 — Báo cáo tổng hợp
- [x] Có câu hỏi nghiên cứu → phương pháp → output → diễn giải ở từng phần.
- [x] Kết luận dẫn ra kết quả thực; không viết số liệu hoặc insight trước khi chạy dữ liệu.
- [x] Phần storytelling kết nối các phần, có đề xuất thận trọng và hạn chế dữ liệu.

## 6. Không thuộc phạm vi hiện tại

- Thu thập nguồn giá hoặc dữ liệu doanh nghiệp từ bên ngoài dataset để cải thiện mô hình.
- Backtest chiến lược giao dịch, tính phí giao dịch hoặc khẳng định khả năng sinh lời thực tế.
- Dự báo giá bằng deep learning, XGBoost; clustering bằng K-Means, PCA.
- Tự động xây dựng website/dashboard/ứng dụng triển khai sản phẩm.

## 7. Những điểm chưa chốt (không được âm thầm giả định)

**Lựa chọn triển khai v1.1 được công bố:** chạy Python/Jupyter local; giữ khả năng mở notebook ở môi trường khác. CSV thực có các cột `symbol,date,open,high,low,close,volume`. Cửa sổ so sánh là ngày đầu–cuối toàn dataset; mã được xếp hạng phải có cả hai mốc, >=95% phiên có close hợp lệ và >=95% cặp phiên liên tiếp có return. Đây là tham số phương pháp, không phải yêu cầu giảng viên. Dùng độ lệch chuẩn tổng thể (NumPy `std`, ddof=0), số năm lịch/365.25. Chọn tối đa 8 mã bằng hai mã có CAGR thấp nhất/cao nhất trong mỗi nhóm; phá hòa theo symbol. Ngưỡng nhóm là trung bình trong tập đủ điều kiện, trường hợp bằng ngưỡng xếp phía cao. ML đã được người dùng xác nhận không triển khai; không dùng quy tắc lấy mẫu 80.000 dòng từ README đã bị loại bỏ.

Các mục dưới đây là danh sách ban đầu; lựa chọn v1.1 phía trên thay thế những mục đã xử lý. Tình trạng adjusted prices và yêu cầu nộp bổ sung vẫn chưa được xác nhận.

1. Môi trường chạy notebook: Google Colab hay Jupyter/VS Code local.
2. Có triển khai mục ML tùy chọn cho phiên nộp cuối hay không.
3. Tên và ý nghĩa các cột dữ liệu, giá có điều chỉnh chia tách/cổ tức hay không.
4. Tiêu chí độ phủ tối thiểu của một mã và cửa sổ thời gian so sánh chung.
5. Tiêu chí lựa chọn 5–10 mã tiêu biểu và ngưỡng phân nhóm.
6. Đề có yêu cầu hình thức nộp, số biểu đồ, rubric hoặc hạn nộp bổ sung hay không.

## 8. Traceability: yêu cầu → phần báo cáo

| Phần | Yêu cầu liên quan |
|---|---|
| 1. Khám phá/làm sạch | G-01, G-02, G-06; P-01..03 |
| 2. Lợi suất/rủi ro | G-03, G-04; P-04..06, P-08 |
| 3. Phân nhóm | G-03, G-04; P-07 |
| 4. ML | G-07 (tùy chọn); P-10 |
| 5. Đánh giá ML | G-07 (tùy chọn); P-10 |
| 6. Storytelling | G-05, G-06; P-09 |

---

**Quy tắc cập nhật:** Khi thay đổi scope hoặc quy trình, cập nhật `REQUIREMENTS.md` (cần làm gì) trước, rồi `METHODOLOGY.md` (làm thế nào) và `PROJECT_PLAN.md` (tiến độ). Không sửa file kiến thức gốc để hợp thức hóa hàm mới.
