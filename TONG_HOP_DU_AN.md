# Tổng hợp dự án phân tích cổ phiếu S&P 500 (2014–2017)

**Ngày tổng hợp:** 26/10/2026.  
**Trạng thái:** Đã viết script, chạy notebook trên toàn bộ CSV, xuất bảng/biểu đồ/báo cáo và kiểm tra kết quả.  
**Phạm vi đã xác nhận:** Chỉ phân tích dữ liệu và phân nhóm cổ phiếu; không triển khai học máy.

Tài liệu này mô tả toàn bộ bài làm hiện tại: yêu cầu, dữ liệu, phương pháp, cấu trúc mã, kết quả, cách chạy và giới hạn. Các con số là kết quả của phiên bản đã kiểm tra, không phải số liệu đặt trước. Khi thay dữ liệu hoặc tham số, cần chạy lại và cập nhật phần kết quả của tài liệu này.

## 1. Bài toán và mục tiêu

Đây là mini-project môn khoa học dữ liệu. Bài làm cần thể hiện quy trình nhập/xuất dữ liệu, tiền xử lý, biến đổi dữ liệu, trực quan hóa và tổng hợp insight thành một báo cáo Python có giải thích và storytelling.

Chủ đề được chọn là phân tích giá cổ phiếu S&P 500 giai đoạn 2014–2017. Các câu hỏi chính:

1. Dữ liệu gồm những gì, có lỗi nào và cần xử lý ra sao?
2. Các cổ phiếu khác nhau thế nào về lợi suất giá và độ biến động?
3. Làm thế nào để so sánh các mã trên cùng kỳ quan sát?
4. Có thể chia cổ phiếu thành những nhóm mô tả nào theo hiệu suất–rủi ro?
5. Những mã được chọn để xem sâu minh họa điều gì, và kết quả có giới hạn nào?

Đầu ra chính là notebook chạy lại được, có code, bảng, biểu đồ và diễn giải. Script Python cung cấp cách chạy toàn bộ quy trình từ một lệnh. Phần học máy trong kế hoạch ban đầu đã được người dùng quyết định không thực hiện.

## 2. Nguồn yêu cầu và giới hạn kỹ thuật

| Tài liệu | Vai trò |
| --- | --- |
| `de_bai.md` | Nội dung yêu cầu của bài tập |
| `allowed_knowledge_reference.md` | Danh sách thư viện, hàm, phương thức và kiến thức được phép |
| `REQUIREMENTS.md` | Đặc tả phạm vi, yêu cầu và điều kiện hoàn thành |
| `METHODOLOGY.md` | Công thức, quy tắc xử lý và các quyết định triển khai |
| `SP500_PROJECT_PLAN.md` | Kế hoạch ban đầu và cập nhật trạng thái thực hiện |

Mã phân tích dùng Python cơ bản, NumPy, Pandas và Matplotlib. Không tự mở rộng danh sách kiến thức gốc. Cụ thể:

- Sắp xếp bằng `set_index()` → `sort_index()` → `reset_index()`.
- Tính lợi suất bằng mảng, indexing/slicing và phép toán trong từng mã.
- Không dùng `.shift()`, `.pct_change()`, `.rolling()`, `.cummax()` hoặc `.sort_values()`.
- Phân nhóm bằng điều kiện thống kê; không dùng K-Means, PCA hay thuật toán phân cụm.
- Không thu thập giá, dữ liệu doanh nghiệp hoặc biến bổ sung từ bên ngoài.

PowerShell, Jupyter và bộ kiểm thử là hạ tầng chạy và kiểm chứng; không phải phương pháp phân tích bổ sung của bài.

## 3. Dữ liệu đầu vào

File nguồn: `S&P 500 Stock Prices 2014-2017.csv`.

| Thuộc tính | Giá trị đã xác nhận |
| --- | --- |
| Số dòng | 497.472 |
| Số mã cổ phiếu | 505 |
| Số ngày giao dịch có quan sát | 1.007 |
| Ngày đầu | 02/01/2014 |
| Ngày cuối | 29/12/2017 |
| Đơn vị quan sát | Một mã cổ phiếu trong một phiên |

| Cột | Ý nghĩa sử dụng |
| --- | --- |
| `symbol` | Mã cổ phiếu |
| `date` | Ngày giao dịch |
| `open` | Giá mở cửa |
| `high` | Giá cao nhất phiên |
| `low` | Giá thấp nhất phiên |
| `close` | Giá đóng cửa, dùng tính các chỉ tiêu chính |
| `volume` | Khối lượng giao dịch |

Không có cột adjusted close. Tình trạng điều chỉnh cổ tức/chia tách chưa được xác nhận. Vì vậy, báo cáo dùng khái niệm **lợi suất giá được cung cấp**, không gọi là tổng lợi nhuận bao gồm cổ tức.

## 4. Quy trình tổng thể

```text
CSV gốc
  → Đọc dữ liệu, chuẩn hóa mã/ngày
  → Kiểm toán lỗi và ghi dấu vết xử lý
  → Giữ dữ liệu close hợp lệ, sắp xếp từng mã theo ngày
  → Tính lợi suất, độ biến động, CAGR và độ phủ
  → Lọc tập đủ điều kiện so sánh cùng kỳ
  → Phân thành bốn nhóm, chọn tám mã để xem sâu
  → Xuất bảng CSV, năm biểu đồ và báo cáo storytelling
```

File gốc luôn giữ nguyên. Mọi dữ liệu xử lý và kết quả được ghi vào `outputs/`.

## 5. Kiểm toán và làm sạch dữ liệu

### 5.1. Những gì được kiểm tra

- Thiếu mã, ngày hoặc các trường giá/khối lượng.
- Ngày không chuyển đổi được.
- Giá trị không hữu hạn, giá không dương, khối lượng âm.
- Dòng trùng hoàn toàn và khóa `symbol + date` trùng.
- Các mâu thuẫn OHLC: `high < low`, `high < open`, `high < close`, `low > open`, `low > close`.

Mã được bỏ khoảng trắng và chuyển thành chữ hoa; ngày được chuyển sang datetime. `source_row` ghi số dòng tương ứng trong CSV gốc, tính cả dòng tiêu đề, để truy vết.

### 5.2. Chính sách xử lý

| Tình huống | Cách xử lý |
| --- | --- |
| Trùng hoàn toàn sau chuẩn hóa mã/ngày | Giữ bản đầu, ghi nhận bản bị loại |
| Cùng mã/ngày nhưng khác nội dung | Cách ly tất cả bản còn lại của khóa xung đột |
| Thiếu mã hoặc ngày không hợp lệ | Loại khỏi phân tích theo mã/phiên |
| Close không hữu hạn hoặc không dương | Loại khỏi phân tích lợi suất |
| OHLC mâu thuẫn | Cách ly cả dòng vì chưa biết giá nào sai |
| Thiếu một số OHL hoặc volume lỗi nhưng close còn dùng được | Giữ để phân tích close nếu không có mâu thuẫn OHLC đã quan sát; đặt `complete_ohlcv=False` |
| Biến động giá lớn | Gắn cờ để rà soát, không tự xóa |

Không điền giá thiếu bằng 0. `clean_prices.csv` là bảng dùng cho phân tích close, không đồng nghĩa mọi trường OHLCV đều hoàn chỉnh.

### 5.3. Kết quả kiểm tra thực tế

| Phát hiện | Số dòng |
| --- | ---: |
| Thiếu open | 11 |
| Thiếu high | 8 |
| Thiếu low | 8 |
| OHLC mâu thuẫn | 12 |
| Trùng hoàn toàn | 0 |
| Dòng bị loại do thiếu khóa | 0 |
| Dòng bị loại do khóa xung đột | 0 |
| Dòng bị loại do close không hợp lệ | 0 |

Các cờ lỗi có thể chồng lấn; không cộng số thiếu từng cột để suy ra số dòng phải xóa. Cờ `nonfinite` bao gồm cả giá trị thiếu, nên cũng không cộng riêng với cờ `missing`.

Sau xử lý: **497.472 − 12 = 497.460 dòng** dùng cho phân tích close. Trong số giữ lại có **11 dòng chưa đủ OHLCV**.

`quality_summary.csv` đếm các loại lỗi, còn `cleaning_steps.csv` đếm số dòng bị loại tuần tự, không đếm lặp. `excluded_rows.csv` lưu dòng bị loại và lý do chính.

## 6. Thứ tự phiên và khoảng thiếu dữ liệu

Lịch tham chiếu là hợp các ngày hợp lệ trong CSV, lấy trước khi làm sạch giá. Mỗi ngày được gán một `session_id`; đây là lịch quan sát của dataset, chưa được đối chiếu với lịch sàn độc lập.

Mỗi mã được sắp theo ngày. Script phân biệt:

- `observed_return`: thay đổi giá giữa hai quan sát liên tiếp của cùng mã, kể cả khi có phiên thiếu ở giữa.
- `daily_return`: chỉ nhận giá trị khi hai quan sát thuộc hai phiên liền kề trong lịch tham chiếu.
- `gap_before`: đánh dấu có khoảng thiếu phiên trước dòng hiện tại.

Ví dụ, nếu lịch có phiên 1, 2, 3 nhưng một mã chỉ có giá ở phiên 1 và 3, thay đổi giữa hai mức giá được lưu là `observed_return`; nó không được dùng như lợi suất một phiên trong tính trung bình và volatility.

Kết quả có **20 lợi suất qua khoảng thiếu phiên**. Có **85 biến động quan sát có trị tuyệt đối từ 20% trở lên** được lưu để rà soát. Không tự loại các biến động này; cờ không chứng minh đó là lỗi hoặc một sự kiện chia tách.

## 7. Công thức chỉ tiêu

Gọi `P_t` là close của một mã tại phiên `t`.

| Chỉ tiêu | Công thức | Cách hiểu |
| --- | --- | --- |
| Daily return | `P_t / P_(t-1) - 1` | Thay đổi giá một phiên; yêu cầu hai phiên liền kề, cùng mã |
| Cumulative price return | `P_t / P_0 - 1` | Thay đổi giá so với đầu kỳ |
| Normalized price | `100 * P_t / P_0` | Đưa giá đầu kỳ về 100 để so sánh tương đối |
| Average daily return | Trung bình daily return hợp lệ | Trung bình số học, không phải CAGR |
| Daily volatility | Độ lệch chuẩn daily return hợp lệ | Dùng NumPy `std()`, `ddof=0`; không thường niên hóa |
| CAGR giá | `(P_end / P_start) ** (1 / Y) - 1` | Tốc độ tăng trưởng giá kép quy đổi theo năm |

Trong CAGR, `Y = số ngày lịch thực tế giữa hai mốc / 365.25`. Mã chỉ có một quan sát không có CAGR hợp lệ. Ngày đầu chuỗi không có daily return. Volatility cần tối thiểu hai daily return hợp lệ.

Các tỷ lệ lưu trong CSV ở dạng thập phân: `0.10` tương đương `10%`. Bảng trình bày và biểu đồ đổi sang phần trăm; thuật toán không làm tròn trước khi phân nhóm.

## 8. Điều kiện so sánh công bằng

Kỳ so sánh chung là **02/01/2014–29/12/2017**. Một mã chỉ được xếp hạng và phân nhóm khi:

1. Có giá hợp lệ tại cả ngày đầu và ngày cuối kỳ chung.
2. Có close hợp lệ ở ít nhất 95% trong 1.007 phiên.
3. Có daily return hợp lệ ở ít nhất 95% trong 1.006 cặp phiên liên tiếp.
4. CAGR và volatility hữu hạn, đủ dữ liệu để tính.

Ngưỡng 95% là lựa chọn phương pháp được công bố trong `analysis_config.py`, không phải yêu cầu bắt buộc của giảng viên.

Kết quả: **483 mã đạt**, **22 mã không đạt**. Bảng `stock_metrics_all.csv` vẫn có chỉ tiêu theo kỳ riêng và lý do không đạt của các mã còn lại; không đưa chúng vào bảng xếp hạng chung. Không tự hạ ngưỡng để buộc mọi mã được chọn.

## 9. Phân nhóm cổ phiếu

Đơn vị phân nhóm là một mã trong tập 483 mã đủ điều kiện. Hai ngưỡng là trung bình CAGR và trung bình daily volatility của tập này:

| Ngưỡng | Giá trị hiển thị |
| --- | ---: |
| CAGR | 9,40%/năm |
| Daily volatility | 1,54%/phiên |

Giá trị đầy đủ được lưu trong `group_thresholds.csv`. Trường hợp bằng ngưỡng được xếp về phía cao; dùng dung sai tuyệt đối `1e-12` ở đơn vị tỷ lệ để xử lý sai số số thực.

| Nhóm | Điều kiện | Số mã | CAGR trung bình | Daily volatility trung bình |
| --- | --- | ---: | ---: | ---: |
| A | CAGR cao, biến động thấp | 180 | 16,27%/năm | 1,24% |
| B | CAGR cao, biến động cao | 77 | 21,98%/năm | 1,91% |
| C | CAGR thấp, biến động thấp | 119 | 2,94%/năm | 1,27% |
| D | CAGR thấp, biến động cao | 107 | −4,05%/năm | 2,08% |

Đây là **phân nhóm theo quy tắc thống kê**, không phải phân cụm học máy. Cao/thấp là tương đối so với ngưỡng của mẫu; CAGR thấp không nhất thiết âm, biến động thấp không đồng nghĩa an toàn. Trung bình nhóm là trung bình các chỉ tiêu từng mã, không phải hiệu suất của một danh mục đã được backtest.

## 10. Tám mã được chọn để phân tích sâu

Mỗi nhóm lấy hai mã ở hai đầu CAGR. Nếu nhiều mã cùng CAGR cực trị, ưu tiên symbol tăng dần; nếu cả nhóm có cùng CAGR thì lấy symbol đầu/cuối để tránh lặp. Cách chọn minh họa sự khác biệt trong nhóm, không phải lấy mẫu ngẫu nhiên hay đề xuất danh mục đầu tư.

| Mã | Nhóm | Vị trí trong nhóm | CAGR | Daily volatility | Độ phủ giá |
| --- | --- | --- | ---: | ---: | ---: |
| CB | A | CAGR thấp nhất | 9,51% | 0,94% | 100,00% |
| STZ | A | CAGR cao nhất | 34,90% | 1,31% | 100,00% |
| CTSH | B | CAGR thấp nhất | 9,52% | 1,60% | 100,00% |
| NVDA | B | CAGR cao nhất | 87,21% | 2,37% | 100,00% |
| GE | C | CAGR thấp nhất | −10,78% | 1,18% | 100,00% |
| C | C | CAGR cao nhất | 9,26% | 1,52% | 100,00% |
| CHK | D | CAGR thấp nhất | −37,98% | 4,55% | 99,90% |
| CTXS | D | CAGR cao nhất | 8,96% | 1,79% | 100,00% |

CAGR trong bảng có đơn vị %/năm. Cả tám mã có cùng hai mốc đầu–cuối. CHK có 1.006 quan sát và 1.004 daily return hợp lệ; các mã còn lại trong bảng có 1.007 quan sát và 1.006 daily return.

Trong toàn bộ tập đủ điều kiện, NVDA có CAGR cao nhất và CHK thấp nhất. CB và CTSH có CAGR khá gần nhau nhưng thuộc hai phía ngưỡng biến động. GE và mã C cùng nhóm C dù CAGR khác dấu: điều này minh họa nhãn “thấp” là dưới ngưỡng trung bình, không phải đồng nghĩa thua lỗ.

## 11. Năm biểu đồ và cách đọc

### 11.1. Phân phối lợi suất một phiên

![Phân phối lợi suất](outputs/figures/01_return_distribution.png)

Dùng các daily return hợp lệ của tập đủ điều kiện. Hình trái giữ toàn bộ phân phối; hình phải phóng to vùng từ −10% đến 10% và ghi số quan sát ngoài vùng. Phóng to hình không làm thay đổi dữ liệu dùng tính chỉ tiêu. Các quan sát mã–phiên có thể phụ thuộc lẫn nhau.

### 11.2. Xếp hạng CAGR

![Xếp hạng CAGR](outputs/figures/02_cagr_ranking.png)

So sánh 10 mã thấp nhất và 10 mã cao nhất trên kỳ chung. Thanh bắt đầu từ đường 0, thể hiện được cả giá trị âm và dương. CAGR mô tả hai đầu kỳ, cần đọc cùng volatility và đường giá.

### 11.3. Hiệu suất–rủi ro và ranh giới nhóm

![Phân nhóm theo CAGR và volatility](outputs/figures/03_risk_return_groups.png)

Mỗi điểm là một mã: trục ngang là daily volatility, trục dọc là CAGR. Hai đường nét đứt biểu diễn ngưỡng trung bình; màu thể hiện nhóm A/B/C/D. Không suy ra quan hệ nhân quả từ biểu đồ này.

### 11.4. Số lượng mã trong từng nhóm

![Quy mô bốn nhóm](outputs/figures/04_group_counts.png)

Tổng số mã của bốn nhóm bằng 483. Nhóm A đông nhất với 180 mã, nhóm B ít nhất với 77 mã. Đây là phân bố số mã trong tập được lọc, không phải tỷ trọng vốn hóa thị trường.

### 11.5. Giá chuẩn hóa của tám mã

![Giá chuẩn hóa](outputs/figures/05_selected_normalized_prices.png)

Mỗi đường bắt đầu ở mốc 100 cùng ngày, giúp so sánh thay đổi tương đối. Khoảng thiếu phiên để đứt đường, không nội suy. Bốn ô có thang dọc riêng; phải đọc giá trị trục khi so sánh giữa các ô.

Các hình được liên kết tương đối. Khi chuyển tài liệu sang máy khác, giữ thư mục `outputs/figures/` cùng cấu trúc để hình hiển thị; phần mô tả và số liệu vẫn nằm trong file Markdown này.

## 12. Cấu trúc mã và vai trò các hàm

Script `sp500_analysis.py` được chia bằng dấu `# %%`, có thể đọc theo phần trong VS Code.

| Hàm | Vai trò |
| --- | --- |
| `load_data()` | Đọc CSV và trình bày thông tin đầu vào |
| `save_table()` | Xuất DataFrame thành CSV UTF-8 có BOM |
| `clean_data()` | Chuẩn hóa, kiểm toán, cách ly lỗi, tạo lịch và bảng giá dùng được |
| `price_metrics()` | Tính lợi suất, khoảng thiếu phiên, tích lũy, trung bình, volatility và CAGR cho một mã |
| `analyze_prices()` | Áp dụng theo từng mã, tính độ phủ, ghi lý do đủ/không đủ điều kiện |
| `group_stocks()` | Tính ngưỡng, gán nhóm, tổng hợp nhóm và chọn mã chuyên sâu |
| `save_figure()` | Căn bố cục và lưu PNG ở 160 dpi |
| `make_figures()` | Tạo năm biểu đồ |
| `markdown_table()` | Định dạng bảng văn bản Markdown |
| `write_report()` | Sinh báo cáo từ kết quả của lần chạy hiện tại |
| `main()` | Điều phối quy trình; dừng nếu không đủ dữ liệu hoặc không có mã đạt điều kiện |

Notebook chứa sáu phần code tương ứng và phần Markdown giải thích. Notebook đã lưu kết quả chạy và năm hình nhúng. Không cần học máy hoặc thư viện scikit-learn cho bài hiện tại.

## 13. Cấu trúc file và đầu ra

```text
project/
├── TONG_HOP_DU_AN.md                 # Tài liệu tổng hợp này
├── de_bai.md                        # Đề bài
├── allowed_knowledge_reference.md   # Giới hạn kiến thức
├── REQUIREMENTS.md                  # Yêu cầu và nghiệm thu
├── METHODOLOGY.md                   # Phương pháp chi tiết
├── SP500_PROJECT_PLAN.md            # Kế hoạch và cập nhật
├── README.md                        # Hướng dẫn ngắn
├── S&P 500 Stock Prices 2014-2017.csv
├── sp500_analysis.py                # Script chính
├── sp500_analysis.ipynb             # Notebook có kết quả
├── analysis_config.py              # Tham số
├── test_analysis.py                # Kiểm thử phát triển
├── run.ps1                         # Lệnh chạy Windows
├── requirements.txt                # Thư viện cần cài
├── requirements-lock.txt           # Phiên bản môi trường đã kiểm tra
└── outputs/
    ├── report.md                   # Báo cáo sinh tự động
    ├── validation.md               # Ghi nhận kiểm chứng phiên bản đã chạy
    ├── tables/                     # 15 bảng CSV
    └── figures/                    # 5 hình PNG
```

`.venv/` chứa môi trường Python; `.cache/` chứa cache và công cụ hỗ trợ phát triển. Hai thư mục này không phải nội dung phân tích cần trình bày trong báo cáo.

| Bảng trong `outputs/tables/` | Nội dung |
| --- | --- |
| `schema.csv` | Tên cột và kiểu dữ liệu khi đọc |
| `missing_by_column.csv` | Số thiếu của từng cột |
| `quality_flags.csv` | Cờ chất lượng cho từng dòng nguồn |
| `quality_summary.csv` | Tổng hợp số dòng bị gắn từng loại cờ |
| `cleaning_steps.csv` | Số bị loại và còn lại qua từng bước |
| `excluded_rows.csv` | Dòng bị cách ly/loại và lý do |
| `clean_prices.csv` | Giá dùng được cho phân tích close, session_id và cờ OHLCV |
| `calendar.csv` | Lịch ngày quan sát và session_id |
| `daily_returns.csv` | Giá, lợi suất, khoảng thiếu, tích lũy và giá chuẩn hóa |
| `extreme_returns_review.csv` | Các biến động lớn được gắn cờ |
| `stock_metrics_all.csv` | Chỉ tiêu 505 mã, độ phủ và lý do không đạt |
| `stock_groups.csv` | 483 mã đủ điều kiện cùng nhãn nhóm |
| `group_summary.csv` | Số mã và chỉ tiêu trung bình từng nhóm |
| `group_thresholds.csv` | Hai ngưỡng đầy đủ và quy tắc bằng ngưỡng |
| `selected_stocks.csv` | Tám mã chuyên sâu và lý do chọn |

## 14. Tham số và hướng dẫn chạy

### 14.1. Cấu hình

Trong `analysis_config.py`:

```python
DATA_FILE = "S&P 500 Stock Prices 2014-2017.csv"
OUTPUT_DIR = "outputs"
MIN_COVERAGE = 0.95
EXTREME_RETURN = 0.20
```

`MIN_COVERAGE` áp dụng cho cả độ phủ giá và độ phủ cặp phiên. `EXTREME_RETURN` chỉ điều khiển gắn cờ, không lọc bỏ dữ liệu. Giữ `OUTPUT_DIR="outputs"` khi dùng runner mặc định; nếu đổi đường dẫn thì cần tạo các thư mục `tables` và `figures` tương ứng trước khi chạy.

### 14.2. Chạy script trên Windows

Mở PowerShell trong thư mục project. Lần đầu hoặc khi cần cài thư viện:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 -Install
```

Chạy lại khi đã có thư viện:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1
```

Runner tạo `.venv` nếu chưa có, tạo các thư mục đầu ra, cấu hình cache Matplotlib trong project và chạy script bằng Python của `.venv`. Backend không mở cửa sổ biểu đồ. `ExecutionPolicy Bypass` chỉ áp dụng cho tiến trình của lệnh, không thay đổi thiết lập hệ thống.

Cài thư viện cần Internet; chạy phân tích chỉ đọc CSV cục bộ. Môi trường đã kiểm tra dùng Python 3.14.8. Các thư viện phân tích chính là NumPy, Pandas và Matplotlib; nbformat, nbclient, ipykernel phục vụ notebook.

Khi đã chuẩn bị thư mục và thư viện, cũng có thể chạy trực tiếp:

```powershell
.\.venv\Scripts\python.exe sp500_analysis.py
.\.venv\Scripts\python.exe test_analysis.py
```

Các file đầu ra cùng tên được ghi lại sau mỗi lần chạy. Nếu lần chạy báo lỗi hoặc dừng sớm, không coi những file còn lại từ lần trước là kết quả mới hoàn chỉnh.

### 14.3. Chạy notebook

1. Mở `sp500_analysis.ipynb` bằng VS Code hoặc Jupyter từ thư mục project.
2. Chọn Python/kernel thuộc `.venv`.
3. Giữ CSV và `analysis_config.py` cùng thư mục; bảo đảm có `outputs/tables/` và `outputs/figures/`.
4. Chọn **Run All** rồi lưu notebook.
5. Nếu đổi cấu hình, restart kernel trước khi Run All.

Chạy script không cập nhật các output đã lưu trong notebook. Muốn notebook phản ánh lần chạy mới thì phải Run All và Save. `TONG_HOP_DU_AN.md` và `outputs/validation.md` là bản tổng hợp của phiên bản đã kiểm tra, không tự cập nhật theo script.

## 15. Kiểm chứng đã thực hiện

### 15.1. Kiểm thử bằng dữ liệu nhỏ

`test_analysis.py` kiểm tra công thức với kết quả biết trước, chuỗi một quan sát, khoảng thiếu phiên, tách mã, thiếu OHL/volume, trùng hoàn toàn, khóa xung đột, giá lỗi, ngày lỗi, mã trắng, điều kiện độ phủ và quy tắc hòa ngưỡng.

Một lỗi số thực ở trường hợp bằng ngưỡng đã được phát hiện và sửa bằng dung sai `1e-12`. Bộ kiểm thử sau sửa đã chạy thành công.

### 15.2. Đối chiếu kết quả thực

- Tính lại chỉ tiêu độc lập bằng vòng lặp, datetime và statistics cho **505 mã**; sai lệch dưới `1e-12`.
- Kiểm tra số dòng raw bằng clean cộng excluded; khóa mã/ngày không trùng sau xử lý; source_row giữa phần giữ và phần loại không chồng lấn.
- Kiểm tra lợi suất không nối qua mã hoặc khoảng thiếu phiên.
- Kiểm tra tổng số mã các nhóm bằng 483 và tám mã được chọn không trùng.
- Đối chiếu các lời gọi API của script với danh sách cho phép.
- Kiểm tra notebook đồng bộ sáu phần code với script, chạy không có output lỗi và chứa năm hình nhúng.
- Xem trực tiếp cả năm PNG; kiểm tra chữ tiếng Việt, nhãn, đơn vị, bố cục và nhãn năm.

SHA-256 của CSV gốc trước/sau giữ nguyên:

```text
2200EA7C7B98791314CB5B4A3072B4D4166DA1ED78A3E3E178339199109837D2
```

Các kiểm chứng xác nhận việc triển khai và đối soát kết quả của phiên bản này; không xác nhận giá đã được điều chỉnh hay dataset đại diện hoàn chỉnh cho thị trường.

## 16. Storytelling và kết luận của bài

Bài phân tích bắt đầu bằng việc xác định chất lượng dữ liệu thay vì xếp hạng ngay từ giá thô. Từ 497.472 dòng, 12 dòng OHLC mâu thuẫn được cách ly và các bản ghi còn lại giữ dấu vết kiểm tra. Những thiếu hụt không ảnh hưởng đến close được xử lý theo đúng mục đích sử dụng, tránh loại dữ liệu không cần thiết.

Sau đó, độ phủ và kỳ quan sát đưa 483 mã về một cơ sở so sánh chung. Kết quả cho thấy hiệu suất lịch sử phân hóa: NVDA có CAGR khoảng 87,21%/năm, trong khi CHK khoảng −37,98%/năm. Tuy nhiên, CAGR không phản ánh toàn bộ đường đi của giá; volatility và đồ thị chuẩn hóa bổ sung thông tin về mức dao động.

Bốn nhóm giúp tổ chức sự khác biệt này. Nhóm A kết hợp CAGR trên trung bình với biến động dưới trung bình; nhóm B đi cùng biến động cao hơn. Nhóm C/D cho thấy các trường hợp dưới ngưỡng CAGR. Việc lấy hai đầu CAGR trong từng nhóm làm rõ rằng ngay cả các cổ phiếu cùng nhãn vẫn có hiệu suất khác nhau đáng kể.

Hàm ý phù hợp là sử dụng bảng chỉ tiêu và nhóm như một bước sàng lọc để nghiên cứu thêm. Không biến nhãn nhóm thành kết luận mua/bán hoặc xem hiệu suất lịch sử là lời hứa lợi nhuận tương lai.

## 17. Giới hạn và phần không triển khai

| Giới hạn | Ảnh hưởng đến cách diễn giải |
| --- | --- |
| Chỉ có giai đoạn 2014–2017 | Không tự suy rộng sang giai đoạn khác |
| Chưa xác nhận điều chỉnh cổ tức/chia tách | Các tỷ suất là biến động giá được cung cấp, không phải total return |
| Danh sách công ty có thể có survivorship bias | Không coi mẫu là toàn bộ S&P 500 lịch sử tại mọi thời điểm |
| Bộ lọc đủ độ phủ | Có thể tạo thiên lệch chọn mẫu |
| Lịch lấy từ ngày quan sát trong CSV | Không phát hiện được ngày thiếu đồng thời ở toàn dataset nếu không có lịch ngoài |
| Ngưỡng trung bình nhạy với ngoại lai | Nhóm phụ thuộc mẫu và quy tắc ngưỡng |
| Biến động cực đoan được giữ lại | Có thể tác động lớn đến volatility; cần đọc cờ rà soát |
| Không có dữ liệu cơ bản, lãi suất phi rủi ro, thuế/phí | Không đánh giá đầy đủ quyết định hay hiệu quả đầu tư thực tế |

Không triển khai ML, deep learning, K-Means/PCA, dự báo giá, Sharpe ratio, backtest, website hay dashboard. Maximum Drawdown là ý tưởng tùy chọn trong tài liệu ban đầu, chưa được đưa vào bản hiện tại.

Phần phân tích đã hoàn thành và kiểm chứng trong phạm vi được chọn. Những điều chưa xác nhận là tình trạng điều chỉnh giá và các yêu cầu hình thức nộp/rubric/hạn nộp bổ sung của giảng viên, nếu có.

## 18. Liên kết để kiểm tra lại

- [Script Python](sp500_analysis.py)
- [Notebook có kết quả](sp500_analysis.ipynb)
- [Báo cáo sinh từ script](outputs/report.md)
- [Ghi nhận kiểm chứng](outputs/validation.md)
- [Cấu hình](analysis_config.py)
- [Phương pháp chi tiết](METHODOLOGY.md)
- [Đề bài](de_bai.md)
- [Danh sách kiến thức cho phép](allowed_knowledge_reference.md)

Tài liệu tổng hợp này được đối chiếu với script, cấu hình, báo cáo, bảng kết quả và ghi nhận kiểm chứng đang có trong project; không sử dụng README cũ đã bị loại bỏ.
