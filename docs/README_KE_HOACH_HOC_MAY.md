# Kế hoạch bổ sung học máy cho bài S&P 500 (2014–2017)

**Trạng thái ngày 06/11/2026:** Kế hoạch đã được kiểm tra và triển khai. Phần bên dưới ghi quy tắc đã chốt trước khi chạy; kết quả thực và mức hoàn thành nằm ngay sau đây.

**Kết quả thực:** 370.378 mẫu train, 125.520 mẫu test. Accuracy baseline đa số 52,75%, Logistic Regression 52,71%, Random Forest 50,36%; hai mô hình không vượt baseline về Accuracy. Xem [báo cáo](../outputs/report.md), [bảng metrics](../outputs/tables/ml_metrics.csv), [kiểm toán mẫu](../outputs/tables/ml_sample_audit.csv) và [notebook](../notebooks/sp500_analysis.ipynb). Các con số được ghi sau khi chạy, không phải giả định của kế hoạch.

Phần học máy là mục **tùy chọn** ở dòng 8 của [de_bai.md](de_bai.md). Người dùng đã chọn triển khai bổ sung ở phiên bản này. Kết quả thực chỉ được ghi sau khi chạy mô hình.

## 1. Mục tiêu và cách hoạt động

Câu hỏi thử nghiệm: **Sau khi kết thúc phiên giao dịch `t`, liệu giá đóng cửa ở phiên kế tiếp của cùng mã có cao hơn giá đóng cửa phiên `t` không?**

```text
Dữ liệu giá đã làm sạch
      ↓
Tạo đặc trưng chỉ từ thông tin biết đến cuối phiên t
      ↓
Tạo nhãn bằng close của phiên kế tiếp cùng mã
      ↓
Chia train 2014–2016 / test 2017 theo thời gian
      ↓
Huấn luyện Logistic Regression và Random Forest trên máy
      ↓
Dự đoán test 2017; so sánh với baseline
      ↓
Bảng chỉ số, confusion matrix, diễn giải và giới hạn
```

Đây là học máy **chạy cục bộ bằng scikit-learn**, qua `.fit()` và `.predict()`. Không gọi API, không kết nối ChatGPT, không huấn luyện mô hình ngôn ngữ. Bài toán là **phân loại tăng/không tăng**, không dự báo mức giá chính xác hoặc lợi nhuận giao dịch.

## 2. Dữ liệu đầu vào và đơn vị mẫu

- Dùng [CSV gốc](<../data/S&P 500 Stock Prices 2014-2017.csv>) thông qua chính sách làm sạch hiện có trong [sp500_analysis.py](../src/sp500_analysis.py). Không thêm dữ liệu bên ngoài.
- Mỗi mẫu là **một mã ở một ngày `t`**. Dữ liệu từng mã được sắp theo `date` và có `session_id` từ lịch quan sát của dataset.
- Chỉ dùng mẫu có close hợp lệ và đủ các trường cần thiết cho đặc trưng. Không lấy riêng 483 mã đã qua bộ lọc so sánh cả kỳ: bộ lọc này biết thông tin đến cuối 2017 và có thể làm sai lệch đánh giá dự đoán.
- Không lấy mẫu huấn luyện theo kết quả phân nhóm CAGR–volatility: hai chỉ tiêu đó được tính từ cả kỳ, bao gồm dữ liệu tương lai đối với năm 2014–2016.
- Giữ một bảng đếm số mẫu bị loại theo lý do, theo giai đoạn train/test, để kiểm tra thiên lệch do thiếu dữ liệu.

## 3. Nhãn cần dự đoán

Với mã `s`, ở ngày `t`:

```text
y(s,t) = 1  nếu close(s,t+1) > close(s,t)
y(s,t) = 0  nếu close(s,t+1) <= close(s,t)
```

`t+1` là **phiên giao dịch liền kề trong lịch dataset**, không phải ngày lịch kế tiếp. Chỉ ghép giá với **cùng mã**. Nếu không có quan sát ở phiên liền kề hoặc đã tới dòng cuối của mã, không tạo mẫu có nhãn. Điều này giữ ý nghĩa “phiên kế tiếp”, không biến biến động qua nhiều phiên bị thiếu thành nhãn một phiên.

**Thời điểm dự đoán:** sau khi phiên `t` đóng cửa. Vì vậy giá/volume của chính ngày `t` được biết, nhưng giá/volume của `t+1` chỉ được dùng để tạo **đáp án kiểm tra**, tuyệt đối không đưa vào đặc trưng.

## 4. Đặc trưng đầu vào dự kiến

| Tên biến | Công thức | Điều kiện |
| --- | --- | --- |
| `return_1d_t` | `close_t / close_(t-1) - 1` | Phiên trước cùng mã phải liền kề và close > 0 |
| `range_t` | `(high_t - low_t) / open_t` | Có OHLC hợp lệ; open > 0 |
| `intraday_t` | `(close_t - open_t) / open_t` | Có open/close hợp lệ; open > 0 |
| `volume_t` | Volume của phiên `t` | Không thiếu, không âm |
| `volume_change_t` | `volume_t / volume_(t-1) - 1` | Phiên trước cùng mã liền kề; volume trước > 0 |

Mẫu thiếu bất kỳ đặc trưng nào ở bảng trên sẽ bị loại **khỏi ML**, nhưng không xóa khỏi CSV gốc hoặc bảng phân tích mô tả. Không điền thiếu bằng 0 và không dùng giá của mã khác để tạo đặc trưng. Ngày đầu chuỗi từng mã thường không có `return_1d_t` và `volume_change_t`, nên không tham gia ML. Việc giữ `volume_t=0` ở phiên hiện tại là hợp lệ nếu các điều kiện khác đạt; mẫu có `volume_(t-1)=0` sẽ bị loại vì không tính được tỷ lệ thay đổi.

Các biến trên là lựa chọn thử nghiệm đơn giản, phù hợp [allowed_knowledge_reference.md](allowed_knowledge_reference.md). Không dùng `.shift()`, `.pct_change()`, `.rolling()` hay thư viện chỉ báo kỹ thuật ngoài danh mục. Tạo cặp phiên bằng indexing/slicing theo từng mã như quy trình hiện tại.

## 5. Chia train và test để tránh lộ đáp án

| Tập | Quy tắc dự kiến |
| --- | --- |
| Train | Ngày đặc trưng `t` **và** ngày dùng tạo nhãn `t+1` đều thuộc 2014–2016 |
| Test | Ngày đặc trưng `t` **và** ngày dùng tạo nhãn `t+1` đều thuộc năm 2017 |

Ngày ở cuối 2016 có đáp án nằm sang 2017 phải bỏ khỏi train. Ngày ở cuối 2017 không có phiên sau trong dữ liệu phải bỏ khỏi test. Đặc trưng của một mẫu đầu 2017 có thể dùng thông tin phiên trước thuộc cuối 2016, vì thông tin đó đã tồn tại tại thời điểm dự đoán. Tuy nhiên, nhãn và phép đánh giá của test không được dùng để học tham số mô hình, chọn baseline hoặc chuẩn hóa.

Không dùng chia ngẫu nhiên theo bản ghi vì cùng mã và các phiên gần nhau có quan hệ theo thời gian. Không chọn mẫu, ngưỡng hoặc mô hình bằng cách xem trước kết quả test rồi sửa phương pháp để tăng điểm. Ghi số dòng và tỷ lệ nhãn `0/1` ở từng tập trước khi diễn giải chỉ số.

## 6. Các mô hình và baseline

| Cách dự đoán | Vai trò | Cách dùng |
| --- | --- | --- |
| **Baseline đa số** | Mốc kiểm tra | Tìm nhãn phổ biến nhất **trong train**, dùng nhãn ấy cho mọi mẫu test. Nếu hòa, chọn `0` theo quy ước công bố trước. |
| **Logistic Regression** | Mô hình tuyến tính cơ bản | Dùng `StandardScaler` fit chỉ trên train, transform train/test; sau đó fit và predict. |
| **Random Forest Classifier** | Mô hình đối chiếu phi tuyến | Fit trên đặc trưng gốc và predict; không cần chuẩn hóa chỉ vì Logistic Regression cần. |

Thông số đã dùng: `LogisticRegression(max_iter=1000, random_state=42)` và `RandomForestClassifier(n_estimators=30, random_state=42)`. Mốc 30 cây nhằm giữ thời gian chạy hợp lý trên toàn bộ mẫu train; không cắt train xuống một số dòng cố định. Thời gian chạy phụ thuộc máy. Đây là thông số thử nghiệm được chọn trước khi xem kết quả test, không phải kết quả tối ưu hóa.

Nếu thư viện/máy không đủ tài nguyên để fit Random Forest trên toàn bộ train, cần ghi rõ điều đó và đưa ra thay đổi có thể kiểm chứng trước khi diễn giải lại kết quả; không thay thế bằng kết quả từ một mẫu lấy tùy ý mà vẫn trình bày như toàn bộ dữ liệu.

## 7. Đánh giá kết quả

Ba cách dự đoán sẽ được so sánh trên **cùng một tập test 2017**:

| Chỉ số | Ý nghĩa |
| --- | --- |
| Accuracy | Tỷ lệ dự đoán đúng tổng thể |
| Precision lớp tăng (`1`) | Trong số phiên dự đoán tăng, bao nhiêu phiên thực sự tăng |
| Recall lớp tăng (`1`) | Trong số phiên thực sự tăng, mô hình nhận ra bao nhiêu |
| F1 lớp tăng (`1`) | Trung bình điều hòa của Precision và Recall; tự tính `2PR/(P+R)` |
| Confusion matrix | Số đúng/sai ở từng loại dự đoán (`TN`, `FP`, `FN`, `TP`) |
| ROC-AUC | Chỉ áp dụng cho mô hình có xác suất dự đoán phù hợp và test có cả hai lớp |

Nếu một tỷ lệ có mẫu số bằng 0, báo cáo ghi quy ước 0 thay vì để kết quả không xác định. ROC-AUC dùng điểm/xác suất lớp `1`, không dùng nhãn nhị phân. Baseline đa số có thể không có giá trị ROC-AUC hữu ích, nên bảng có thể để `N/A` cho baseline. Chỉ diễn giải mô hình tốt hơn baseline khi mức cải thiện được nêu bằng số thực tế trên cùng tập test; kết quả chưa chạy sẽ không được điền trước.

Biểu đồ dự kiến: cột so sánh các chỉ số chính và confusion matrix cho từng mô hình (có nhãn, đơn vị và đường gốc 0 khi áp dụng). Bảng phải cho biết số mẫu train/test và tỷ lệ nhãn, vì Accuracy riêng lẻ dễ gây hiểu nhầm khi hai lớp lệch nhau.

## 8. Các file sẽ tạo hoặc cập nhật sau khi được chốt

| File/thư mục | Việc sẽ làm |
| --- | --- |
| `src/sp500_analysis.py` | Một file gồm làm sạch, phân tích, tạo mẫu, huấn luyện và đánh giá ML. |
| `sp500_analysis.ipynb` | Thêm phần học máy sau phân tích và phân nhóm, trình bày câu hỏi, code, bảng, biểu đồ và diễn giải. |
| `outputs/tables/ml_sample_audit.csv` | Số mẫu tạo được/bị loại và lý do theo train/test. |
| `outputs/tables/ml_metrics.csv` | Baseline và hai mô hình trên cùng test; kèm số mẫu và chỉ số. |
| `outputs/tables/ml_confusion_matrices.csv` | Các ô TN/FP/FN/TP theo mô hình. |
| `outputs/tables/ml_test_predictions.csv` | Ngày, mã, nhãn thật và dự đoán của ba cách trên tập test để đối chiếu kết quả. |
| `outputs/figures/ml_*.png` | Hình đánh giá khi kết quả thực có sẵn. |
| `outputs/report.md` | Bổ sung câu hỏi ML, phương pháp, kết quả thực, so sánh baseline và giới hạn trong storytelling. |
| `requirements.txt` | Thêm `scikit-learn` vì bản phân tích hiện tại không cần thư viện này. |
| `run.ps1` | Thêm bước chạy ML sau khi làm sạch/phân tích, có kiểm tra lỗi để không coi đầu ra cũ là kết quả mới. |
| `test_ml.py` | Kiểm thử nhãn, ranh giới thời gian, dữ liệu thiếu và chỉ số đánh giá. |
| `README.md`, `REQUIREMENTS.md`, `METHODOLOGY.md`, `SP500_PROJECT_PLAN.md` | Cập nhật cách chạy, phạm vi, phương pháp và trạng thái sau khi triển khai. |

Tên file cụ thể của các hình/bảng có thể điều chỉnh để khớp code, nhưng phải giữ khả năng truy vết từng kết luận về bảng hoặc hình đã chạy. Không ghi đè CSV gốc; các bảng và hình phân tích hiện tại tiếp tục dùng được.

## 9. Trình tự triển khai khi được chốt

1. Cập nhật yêu cầu và phương pháp của phần ML theo quy tắc ở README này, sau đó sửa trạng thái trong kế hoạch.
2. Tái sử dụng `clean_data()` và lịch `session_id`; tạo nhãn/đặc trưng theo từng mã, ghi bảng kiểm toán mẫu.
3. Kiểm thử bằng chuỗi nhỏ: ngày đầu/cuối, thiếu phiên, đổi mã, volume trước bằng 0 và ranh giới 2016/2017.
4. Chia train/test theo thời gian, kiểm tra nhãn hai lớp và thông tin không vượt thời điểm dự đoán.
5. Fit scaler trên train, huấn luyện hai mô hình và baseline với tham số cố định.
6. Xuất dự đoán/tổng hợp chỉ số, confusion matrix và hình; so sánh trên cùng test.
7. Chạy lại notebook, cập nhật báo cáo từ **kết quả thực**, kiểm tra lời gọi hàm theo danh sách kiến thức được phép và đối chiếu các số trong bảng với báo cáo.

## 10. Điều kiện hoàn thành và giới hạn diễn giải

Phần này được coi là hoàn thành khi có: bảng giải thích số mẫu bị loại; nhãn đúng phiên kế tiếp cùng mã; tách train/test theo thời gian không lộ nhãn 2017 vào train; hai mô hình và baseline chạy được; bảng Accuracy/Precision/Recall/F1/confusion matrix trên cùng test; ROC-AUC khi phù hợp; notebook/báo cáo giải thích kết quả và giới hạn.

Dữ liệu chỉ có 2014–2017 và tình trạng điều chỉnh cổ tức/chia tách chưa xác nhận. Danh sách mã và bộ lọc mẫu có thể gây thiên lệch. Mức dự đoán đúng chiều giá **không chứng minh khả năng giao dịch có lãi**: project không tính phí, thuế, trượt giá hay backtest. Kết quả sẽ chỉ là một thử nghiệm học máy có giám sát trên dữ liệu lịch sử.

**Điểm rà soát:** Đã sửa đường dẫn vì README nằm trong `docs/`. Các quy tắc về mẫu, ranh giới thời gian, scaler và baseline đủ rõ để triển khai mà không nhìn trước kết quả test. Không lọc mã bằng chỉ tiêu của cả giai đoạn 2014–2017. Kết quả yếu được giữ nguyên, không tinh chỉnh ngầm bằng tập test.
