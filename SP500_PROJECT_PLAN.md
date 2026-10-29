# KẾ HOẠCH MINI-PROJECT: S&P 500 STOCK PRICES (2014–2017)

> **Trạng thái ngày 26/10/2026:** Đã triển khai và chạy script/notebook, xuất báo cáo, bảng CSV và 5 biểu đồ. **Không làm ML theo xác nhận của người dùng.**  
> **Nguồn yêu cầu có trong workspace:** `de_bai.md`.  
> **Nguồn giới hạn kỹ thuật:** `allowed_knowledge_reference.md` (tài liệu quy chuẩn bắt buộc).  
> **Quy tắc:** Chỉ dùng thư viện, hàm, phương thức và cú pháp được liệt kê rõ trong tài liệu quy chuẩn. Khi cần thao tác chưa được nêu, phải kiểm tra/trao đổi trước, không tự ý bổ sung.

## 0. Tóm tắt dự án

**Cập nhật triển khai:** `sp500_analysis.py`, `sp500_analysis.ipynb`, `outputs/report.md`, `README.md` hướng dẫn chạy. Lựa chọn cuối: môi trường Python/Jupyter local; cửa sổ chung 02/01/2014–29/12/2017; ngưỡng độ phủ giá và cặp phiên 95%; volatility ddof=0; hai mã ở hai đầu CAGR mỗi nhóm. Chi tiết trong phần quyết định v1.1 của `METHODOLOGY.md`. Các phần ML bên dưới chỉ còn là thiết kế mở rộng được lưu lại, không thuộc bài hiện tại.

**Kết quả nghiệm thu:** 497.472 dòng raw → 497.460 dòng cho phân tích close; 483/505 mã đủ điều kiện; 8 mã chuyên sâu; nhóm A/B/C/D: 180/77/119/107. Đã kiểm thử công thức, tách mã, khoảng thiếu phiên, làm sạch và hòa ngưỡng; notebook Run All không có output lỗi. Giá adjusted vẫn chưa xác minh, báo cáo nêu rõ giới hạn.

**Tên đề tài hiện tại:** *Phân tích lợi suất và rủi ro cổ phiếu S&P 500 giai đoạn 2014–2017: Hàm ý đối với lựa chọn đầu tư.*

**Dữ liệu:** Bộ **S&P 500 Stock Prices 2014–2017** trong danh sách chủ đề của đề bài. Mô tả đề bài: mỗi bản ghi là dữ liệu một phiên giao dịch, có mã cổ phiếu, volume, high, low, open và close. Cần xác nhận tên cột chính xác, định dạng ngày, độ phủ và tình trạng điều chỉnh giá sau khi đọc CSV thực tế.

**Mục tiêu:** (1) chuẩn bị dữ liệu có chất lượng; (2) so sánh lợi suất và rủi ro lịch sử; (3) phân nhóm cổ phiếu bằng **quy tắc thống kê**; (4) thử nghiệm mô hình phân loại xu hướng giá phiên kế tiếp; (5) rút ra insight và hạn chế của cách tiếp cận.

**Phạm vi:** Phân tích tổng quan tất cả mã đủ điều kiện trong dataset, sau đó chọn **5–10 mã tiêu biểu dựa trên tiêu chí công bố rõ** để trực quan hóa và thảo luận sâu. Không khẳng định nhóm mã trong tệp đại diện hoàn toàn cho chỉ số S&P 500 lịch sử.

**Đầu ra chính:** Notebook phân tích có Markdown giải thích, biểu đồ, bảng số liệu và phần storytelling; CSV dữ liệu sạch / bảng tổng hợp khi thích hợp. **Môi trường Colab hay VS Code/Jupyter chưa chốt**; cả hai có thể dùng `.ipynb`.

**Bản đồ kiến thức:** nhập/xuất (chương 6–7), làm sạch (8–9), NumPy (4–5), biến đổi dữ liệu (10–11), trực quan hóa (12–13), mô hình học máy có giám sát (14–15).

---

## 1. Cấu trúc nội dung báo cáo

### Phần 1 — Nhập, khám phá và làm sạch dữ liệu

**Câu hỏi:** Tệp chứa những gì và chất lượng có đủ để phân tích không?

**Việc làm**
1. Đọc CSV và ghi lại tên cột, số hàng, số mã cổ phiếu, khoảng thời gian.
2. Kiểm tra kiểu dữ liệu; chuyển cột ngày sang datetime nếu cần.
3. Kiểm tra thiếu giá trị, trùng lặp (đặc biệt khóa `mã + ngày`), giá OHLC không dương, volume âm, các bất hợp lý của `high/low/open/close`.
4. Làm sạch theo **quy tắc được giải thích**: không thay giá thiếu bằng 0; tránh xóa dữ liệu tùy tiện; giữ bản raw và bản clean riêng biệt.
5. Bảo đảm dữ liệu của từng mã được xét theo thứ tự thời gian. Chọn cách sắp xếp chỉ dùng hàm được phép; ví dụ `set_index(...)` và `sort_index(...)` nếu phù hợp.

**Kiến thức / hàm có thể dùng:** `pd.read_csv`, `pd.to_datetime`, `.isna`, `.duplicated`, `.drop_duplicates`, `.dropna`, `.copy`, Boolean indexing, `.set_index`, `.sort_index`, `.reset_index`, `.to_csv`, `np.where`, toán tử so sánh.

**Đầu ra:** báo cáo số bản ghi và số lỗi trước/sau, bộ dữ liệu đã xử lý; giải thích quy tắc loại/giữ bản ghi.

**Điểm phải kiểm chứng:** tên cột, giá điều chỉnh hay chưa, trùng ngày theo mã, khoảng thời gian thực tế, hiện tượng split gây biến động giá giả tạo.

### Phần 2 — Phân tích lợi suất và rủi ro

**Câu hỏi:** Những mã nào có hiệu suất lịch sử nổi bật và đi kèm mức biến động nào?

| Chỉ tiêu | Định nghĩa / cách hiểu | Lưu ý |
|---|---|---|
| Daily return | `r_t = (P_t - P_(t-1)) / P_(t-1)` | So sánh các phiên liên tiếp **của cùng một mã**; không trộn hai mã. |
| Cumulative price return | `P_t / P_0 - 1` | Chỉ số giá, không chắc là tổng lợi nhuận bao gồm cổ tức. |
| Average daily return | Trung bình daily returns | Cần xác nhận số ngày có quan sát. |
| Volatility | Độ lệch chuẩn của daily returns | Nêu rõ là **volatility theo ngày**; nếu thường niên hóa phải ghi giả định số phiên/năm. |
| CAGR (giá) | `(P_end / P_start) ** (1 / years) - 1` | Dùng thời gian thực tế của từng mã và điều kiện đủ dữ liệu; không dùng khi giá không hợp lệ. |

**Phương pháp:** phép toán số học và vòng lặp / truy cập theo vị trí trên dữ liệu đã có thứ tự, `mean`, `std`, `np.sqrt`, phép nhóm / tổng hợp được cho phép. **Không dùng** `.pct_change()`, `.shift()`, `.rolling()`, `.cummax()` nếu không nằm trong danh mục.

**Biểu đồ dự kiến:** histogram lợi suất ngày; bar top/bottom CAGR (các mã đủ độ phủ); scatter CAGR–volatility; line của chỉ số giá chuẩn hóa về 100 cho 5–10 mã.

**Đầu ra:** bảng chỉ tiêu theo mã và 4 nhóm insight mô tả. **Maximum Drawdown** được giữ như tùy chọn bổ sung khi thật sự cần, không phải bắt buộc trong bản tối giản.

**Kiểm tra công bằng:** so sánh trên cùng khoảng ngày nếu cần; báo cáo số phiên/mức độ đầy đủ; không xếp hạng mã chỉ có vài quan sát chung với mã có đầy đủ bốn năm.

### Phần 3 — Phân nhóm cổ phiếu theo hiệu suất–rủi ro (không dùng K-Means)

**Câu hỏi:** Có thể chia các mã thành những nhóm mô tả dựa trên lợi suất và biến động như thế nào?

**Quy tắc dự kiến:** dùng hai tiêu chí CAGR và volatility của từng mã. Đặt ngưỡng 'cao/thấp' tương đối theo số liệu thực tế (ví dụ ngưỡng bình quân của tập đủ điều kiện, sau khi xác minh cách triển khai theo hàm được phép). Tạo bốn nhóm:

| Nhóm | CAGR | Volatility |
|---|---|---|
| 1 | Cao | Thấp |
| 2 | Cao | Cao |
| 3 | Thấp | Thấp |
| 4 | Thấp | Cao |

**Kiến thức / hàm:** phép so sánh, `np.where`, Boolean indexing, `groupby`, `mean`, `std`, `ax.scatter`, `ax.bar`.

**Đầu ra:** bảng số lượng và chỉ số của bốn nhóm, scatter CAGR–volatility minh họa ranh giới. Đây là **phân nhóm theo quy tắc**, không được gọi là phân cụm K-Means.

**Giới hạn:** các nhãn là tương đối theo tập dữ liệu và cách chọn ngưỡng; không tự suy diễn nhóm 'an toàn', 'tăng trưởng' hay khuyến nghị mua.

### Phần 4 — Thử nghiệm học máy dự đoán xu hướng giá (tùy chọn theo đề bài)

**Câu hỏi:** Dữ liệu giá và khối lượng đã biết tới cuối phiên t có giúp dự đoán giá đóng cửa phiên t+1 tăng hay không?

**Nhãn:** `y_t = 1` nếu `close_(t+1) > close_t`, ngược lại `0`. Tạo nhãn theo **phiên kế tiếp của cùng mã**; không dùng ngày khác mã, không rò rỉ dữ liệu ngày tiếp theo vào X.

**Đặc trưng đơn giản (không dùng rolling API):** lợi suất phiên t, `(high-low)/open` nếu hợp lệ, `(close-open)/open`, `volume_t`, thay đổi volume so với phiên trước. Không chọn feature cần kiến thức ngoài danh sách.

**Mô hình cho phép:** `LogisticRegression` và `RandomForestClassifier`. Dùng `.fit`, `.predict`, và `.predict_proba` nếu cần ROC-AUC.

**Tách dữ liệu:** theo thời gian, dự kiến train 2014–2016 và test 2017, **không shuffle**. Thực tế phải kiểm tra ngày và lọc những mẫu tại ranh giới sao cho nhãn không làm lộ kết quả tương lai của train. Chuẩn hóa với `StandardScaler`: chỉ `fit` trên train và `transform` trên test. Ghi `random_state` cho mô hình có yếu tố ngẫu nhiên.

**Đầu ra:** dự đoán và bảng kết quả theo mô hình. Việc chạy ML chỉ bắt đầu sau khi data pipeline hợp lệ.

### Phần 5 — Đánh giá mô hình

**Câu hỏi:** Hai mô hình có tốt hơn cách đoán đơn giản không?

- **Baseline:** luôn đoán nhãn có tần suất cao nhất **trong train**.
- **Chỉ số:** Accuracy, Precision, Recall, Confusion Matrix, ROC-AUC khi có điểm xác suất thích hợp. F1 được **tự tính bằng phép toán** từ Precision và Recall (`2PR/(P+R)`, có xử lý trường hợp mẫu số bằng 0), không cần hàm `f1_score` ngoài tài liệu.
- So sánh Logistic Regression, Random Forest và baseline trên **cùng tập test**.
- Có thể mô tả hệ số `coef_` của Logistic Regression nếu phù hợp với biến đã chuẩn hóa; **không tự ý dùng** `feature_importances_` vì chưa liệt kê trong danh sách.

**Kiến thức / hàm:** `accuracy_score`, `precision_score`, `recall_score`, `confusion_matrix`, `classification_report`, `roc_curve`, `roc_auc_score`, phép toán cơ bản, Matplotlib.

**Đầu ra:** bảng metrics, biểu đồ so sánh và diễn giải hạn chế (dự đoán đúng chiều giá ≠ chiến lược đầu tư sinh lời).

### Phần 6 — Storytelling và hàm ý đầu tư

**Luồng lập luận:**
1. Dữ liệu có đáng tin cậy cho phân tích lịch sử không?
2. Các mã khác nhau thế nào về lợi suất và biến động?
3. Bốn nhóm theo CAGR–volatility khác nhau ra sao?
4. Mô hình dự đoán có vượt baseline không? Nếu không, rút ra bài học gì?
5. Hàm ý đối với **sàng lọc / nghiên cứu thêm**, thay vì khuyến nghị mua bán chắc chắn.

**Hạn chế bắt buộc trình bày:** khoảng dữ liệu 2014–2017; khả năng thiếu adjusted close / cổ tức / chia tách; lựa chọn danh sách công ty có thể tạo sai lệch đại diện; không xét chi phí giao dịch, thuế và dữ liệu cơ bản doanh nghiệp; kết quả ML trên giai đoạn lịch sử không bảo đảm hiệu quả tương lai.

---

## 2. Các quyết định kỹ thuật đã chốt

- [x] Chủ đề 5: **S&P 500 Stock Prices (2014–2017)**.
- [x] Phân tích tổng quan toàn bộ dữ liệu hợp lệ và đào sâu 5–10 mã có tiêu chí chọn rõ ràng.
- [x] **Tuân thủ nghiêm ngặt** `allowed_knowledge_reference.md`.
- [x] Không dùng K-Means, PCA, silhouette, XGBoost.
- [x] Thay phân cụm học máy bằng phân nhóm dựa trên quy tắc CAGR–volatility.
- [x] Giữ mô hình Logistic Regression và Random Forest ở mục **tùy chọn**.
- [ ] Chọn môi trường notebook (Colab hoặc VS Code/Jupyter).
- [ ] Xem CSV gốc để kiểm chứng schema và định nghĩa giá.
- [ ] Quy định tiêu chí chọn các mã chuyên sâu và mức tối thiểu dữ liệu.
- [ ] Chốt có thực hiện phần ML tùy chọn trong lần nộp hay không.

## 3. Danh sách hạn chế — KHÔNG tự ý dùng

| Không tự động sử dụng | Lý do / phương án |
|---|---|
| `sklearn.cluster.KMeans`, `sklearn.decomposition.PCA`, `silhouette_score` | Không có trong tài liệu được phép → dùng phân nhóm theo quy tắc. |
| `.pct_change()`, `.shift()`, `.rolling()`, `.cummax()` | Không liệt kê → dùng phép toán, truy cập, vòng lặp/mảng đã học. |
| `f1_score` | Không liệt kê → tự tính từ Precision và Recall. |
| `feature_importances_` | Không được liệt kê → không sử dụng nếu chưa có xác nhận. |
| `yfinance`, `ta`, `backtrader`, XGBoost | Ngoài phạm vi và không cần thiết. |
| Sharpe Ratio chuẩn | Không có dữ liệu lãi suất phi rủi ro; không gán nhãn Sharpe cho tỷ lệ khác. |

> **Nguyên tắc kiểm tra:** Dù một phương thức khá phổ biến trong Pandas hay sklearn, nếu tài liệu quy chuẩn không nêu rõ, trước hết phải thay bằng kiến thức đã học hoặc ghi lại để xin xác nhận.

## 4. Quy tắc chất lượng thực hiện

1. Giữ file gốc bất biến; xuất kết quả làm sạch ra đường dẫn khác.
2. Giải thích quyết định xử lý dữ liệu thiếu/trùng/bất thường, kèm đếm trước–sau.
3. Xác nhận thứ tự phiên giao dịch trước khi tính lợi suất và nhãn tương lai.
4. Không dùng thống kê của test để chuẩn hóa dữ liệu train (tránh **data leakage**).
5. Trực quan hóa có tên biểu đồ, trục, đơn vị; trục lượng của biểu đồ cột bắt đầu từ 0.
6. Phân biệt **kết quả quan sát được** với **diễn giải** và **đề xuất**; không điền kết quả giả định vào báo cáo cuối.
7. Giữ seed / `random_state` khi thao tác mang tính ngẫu nhiên.

## 5. Checklist thiết kế ban đầu (lưu tham chiếu; trạng thái nghiệm thu hiện tại ở mục 0)

### Giai đoạn A — Chuẩn bị
- [ ] Tải và kiểm tra file CSV thật.
- [ ] Kiểm tra ngày, các cột OHLCV, tính hợp lệ và tính điều chỉnh giá.
- [ ] Chốt notebook và cách đặt đường dẫn file dữ liệu.
- [ ] Chốt ngưỡng dữ liệu tối thiểu khi so sánh các mã.

### Giai đoạn B — Dữ liệu và chỉ tiêu
- [ ] Hoàn thành phần 1 và báo cáo chất lượng dữ liệu.
- [ ] Tạo bảng lợi suất và rủi ro phần 2.
- [ ] Kiểm tra công thức bằng một số ví dụ nhỏ trước khi áp dụng toàn bộ.
- [ ] Hoàn thành 4–5 biểu đồ phục vụ câu hỏi nghiên cứu.

### Giai đoạn C — Phân nhóm và ML
- [ ] Thiết lập ngưỡng nhóm dựa trên dữ liệu thực tế.
- [ ] Vẽ và mô tả các nhóm ở phần 3.
- [ ] Nếu chọn ML: tạo nhãn/đặc trưng không rò rỉ, chia train–test theo thời gian.
- [ ] Nếu chọn ML: huấn luyện 2 mô hình, baseline, đánh giá thống nhất.

### Giai đoạn D — Báo cáo
- [ ] Viết nhận xét ngay dưới từng bảng/biểu đồ.
- [ ] Tổng hợp insight thành mạch storytelling.
- [ ] Nêu giới hạn dữ liệu/phương pháp.
- [ ] Rà soát lại toàn bộ hàm sử dụng với `allowed_knowledge_reference.md`.

## 6. Cấu trúc lưu trữ được đề xuất

```text
sp500-mini-project/
├── README.md                       # Mô tả ngắn, cách mở báo cáo
├── PROJECT_PLAN.md                 # File này: phạm vi, phương pháp, checklist
├── allowed_knowledge_reference.md  # Danh sách kiến thức gốc — không tự sửa
├── data/
│   ├── raw/                        # CSV ban đầu (giữ nguyên)
│   └── processed/                  # CSV sau làm sạch, bảng chỉ tiêu
├── notebooks/
│   └── sp500_analysis.ipynb        # Báo cáo chính: các phần 1–6
└── outputs/
    ├── figures/                    # Hình xuất từ các biểu đồ (nếu cần)
    └── tables/                     # Bảng tổng hợp xuất thêm (nếu cần)
```

**Lưu ý:** Đây mới là *đề xuất cấu trúc thư mục*, không yêu cầu phải tạo mọi thư mục ngay. Với mini-project này, **một notebook chính + một file kế hoạch + dữ liệu** là đủ; không cần tách thành sáu notebook nếu nhóm chưa có nhu cầu làm việc song song.

## 7. Nhật ký quyết định / thay đổi

| Trạng thái | Quyết định | Lý do |
|---|---|---|
| Đã chốt | Phân tích toàn bộ + chọn một số mã chuyên sâu | Vừa đủ tổng quan, vừa có biểu đồ dễ hiểu. |
| Đã chốt | Bỏ K-Means/PCA | Không có trong whitelist kiến thức. |
| Đã chốt | Phân nhóm CAGR–volatility theo quy tắc | Sử dụng phép toán và xử lý dữ liệu đã học. |
| Dự kiến | Giữ ML ở phần tùy chọn | Đề bài không bắt buộc; danh sách cho phép hai mô hình phân loại. |
| Chưa chốt | Notebook chạy ở môi trường nào | Không ảnh hưởng lớn đến cấu trúc báo cáo. |

---

**Điểm dừng hiện tại:** Đã có script và notebook chạy được, báo cáo từ kết quả thực. Các mục phương pháp dự kiến được thay thế bởi quyết định v1.1 ở đầu tài liệu; phần ML không triển khai. Cần đối chiếu thêm yêu cầu hình thức nộp/rubric nếu giảng viên cung cấp sau.
