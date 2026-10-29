# METHODOLOGY — Phương pháp phân tích S&P 500 (2014–2017)

**Phiên bản:** 1.1 — đã triển khai và chạy trên CSV ngày 26/10/2026.  
**Ràng buộc cao nhất về kỹ thuật:** `allowed_knowledge_reference.md`. File này hướng dẫn *cách* thực hiện, **không thay thế** danh sách cho phép đầy đủ. Mọi ví dụ và thuật toán dưới đây chỉ là thiết kế; kiểm chứng lại đúng chữ ký hàm khi viết code.

## 0. Khung thực hiện

### Quyết định thực thi v1.1 (thay thế những lựa chọn dự kiến bên dưới)

- Theo xác nhận của người dùng: **chỉ phân tích và phân nhóm, không ML**. Mục 4–5 giữ làm thiết kế tham khảo, không chạy.
- Schema thực: `symbol,date,open,high,low,close,volume`; 497.472 dòng, 505 mã; 02/01/2014–29/12/2017, 1.007 ngày quan sát.
- Trùng hoàn toàn: giữ bản đầu sau chuẩn hóa symbol/ngày. Khóa trùng có nội dung khác: cách ly tất cả bản ghi còn lại của khóa đó. Giữ `source_row` để truy ngược CSV.
- Thiếu khóa, close không hữu hạn/không dương, OHLC mâu thuẫn: cách ly. Thiếu OHL hoặc volume lỗi vẫn giữ cho phân tích close nếu close hợp lệ và không có mâu thuẫn OHLC đã quan sát; đánh dấu `complete_ohlcv=False`. Không tính chỉ tiêu thanh khoản từ những dòng này. Bản này chỉ tính chỉ tiêu từ close.
- `quality_summary.csv` đếm các cờ có thể chồng lấn; `cleaning_steps.csv` đếm số dòng loại tuần tự; `excluded_rows.csv` lưu lý do chính. Kết quả thực: 12 dòng OHLC mâu thuẫn bị cách ly; giữ 497.460 dòng, gồm 11 dòng thiếu một số OHL nhưng close còn hợp lệ.
- Lịch tham chiếu là hợp các ngày hợp lệ trong CSV trước khi làm sạch giá. Không có lịch sàn bên ngoài. Return qua khoảng thiếu một hoặc nhiều phiên được lưu riêng ở `observed_return`, không dùng trong daily volatility/average daily return.
- Xếp hạng và phân nhóm: có giá ở cả hai mốc kỳ chung, độ phủ giá >=95%, độ phủ cặp phiên có daily return >=95%. Tham số nằm trong `analysis_config.py`. Kết quả: 483 mã đạt, 22 mã không đạt; bảng tất cả mã có lý do loại khỏi so sánh.
- Volatility: NumPy `std()` mặc định ddof=0. CAGR dùng số ngày lịch thực tế/365.25; chuyển ngày sang mảng NumPy datetime64[D] rồi số nguyên để tính khoảng cách.
- Bốn nhóm theo ngưỡng trung bình của tập đủ điều kiện; bằng ngưỡng (dung sai tuyệt đối 1e-12 ở đơn vị tỷ lệ) thuộc phía cao. Không làm tròn chỉ tiêu trước phân nhóm.
- Chọn hai đầu CAGR mỗi nhóm: hòa thì symbol tăng dần; nếu cả nhóm cùng CAGR, lấy hai symbol đầu/cuối để không lặp. Dataset này chọn 8 mã. Đây là lựa chọn ví dụ theo hiệu suất lịch sử, không phải mẫu ngẫu nhiên.
- Cờ cực đoan: `abs(observed_return)>=0.20`; giữ nguyên trong tính toán nếu cặp phiên hợp lệ. Ngưỡng chỉ phục vụ rà soát, không xác nhận split và không tự winsorize/xóa ngoại lai.
- Script `sp500_analysis.py`, notebook `sp500_analysis.ipynb`, báo cáo `outputs/report.md`; 5 hình PNG, bảng CSV và bộ kiểm thử `test_analysis.py`. Không dùng dữ liệu ngoài.

**Dữ liệu** → Kiểm toán/làm sạch → Tạo chỉ tiêu giá/lợi suất → So sánh/phân nhóm → (tùy chọn) Phân loại tăng giá phiên kế tiếp → Đánh giá → Storytelling.

- Mỗi khối báo cáo trình bày: **câu hỏi → định nghĩa → thao tác → kết quả/bảng/biểu đồ → giải thích**.
- Các mục thiết kế bên dưới dùng `ticker` theo nghĩa mô tả; tên cột thực tế là `symbol`.
- Dữ liệu chỉ cho phép phân tích **biến động giá lịch sử**, không mặc nhiên là tổng lợi nhuận sau cổ tức/chia tách.
- **Không dùng** web/API hay thêm dữ liệu phụ trợ để thực hiện phân tích.

## 1. Nhập và kiểm toán chất lượng dữ liệu

### 1.1 Nhập / kiểm tra
- Đọc CSV với `pd.read_csv(...)`; dùng `pd.to_datetime(...)` cho ngày nếu cần.
- Kiểm tra số dòng/cột qua thuộc tính có trong tài liệu (`.shape` trên NumPy; với DataFrame, nếu cần truy cập thuộc tính chưa liệt kê rõ thì dùng những cách đã xác nhận hợp lệ trong tài liệu hoặc trình bày trực tiếp kết quả bảng); xác định số mã bằng `np.unique(...)` hoặc cấu trúc Python cơ bản.
- Kiểm tra khoảng thời gian và những chuỗi giá theo từng mã; ghi rõ giai đoạn thực tế của tập đủ điều kiện.

### 1.2 Quy tắc dữ liệu không hợp lệ

| Kiểm tra | Quy tắc dự kiến | Xử lý dự kiến |
|---|---|---|
| Thiếu mã hoặc ngày | Thiếu khóa nhận dạng | Loại khỏi phân tích theo mã/phiên; ghi số lượng |
| Thiếu OHLC | Không tính được chỉ tiêu phụ thuộc giá | Không điền bằng 0; loại khỏi các phép tính yêu cầu giá, lưu lý do |
| Thiếu volume | Không tính được đặc trưng volume | Chỉ loại khỏi phân tích cần volume; nếu cần một bảng chung thì công bố cách chọn |
| Trùng (`ticker`, `date`) | Một mã không nên có hai quan sát phiên cùng ngày | Kiểm tra sự trùng và khác biệt; chỉ drop trùng khi có nguyên tắc rõ |
| `open/high/low/close <= 0` | Giá không hợp lệ cho tỷ suất | Đánh dấu và loại khỏi phép tính tương ứng |
| `volume < 0` | Khối lượng không hợp lệ | Đánh dấu và loại khỏi phân tích volume |
| `high < low`, `high < open/close`, `low > open/close` | OHLC không nhất quán | Đánh dấu để kiểm tra, không âm thầm sửa |
| Giá thay đổi đột biến | Có thể do split/chất lượng dữ liệu | Gắn cờ thảo luận; không tự loại theo một ngưỡng tùy ý |

**Phương thức dự kiến đã nêu trong tài liệu:** `.isna()`, `.duplicated(subset=...)`, `.drop_duplicates(subset=...)`, `.dropna(subset=...)`, `.copy()`, `.set_index([...])`, `.sort_index()`, `.reset_index()`, `.to_csv()`, Boolean indexing, `np.where()`.

### 1.3 Thứ tự giao dịch
- Chỉ tính chuỗi theo cùng mã và thứ tự ngày tăng dần.
- Ưu tiên sắp bằng `set_index(['ticker', 'date'])` → `sort_index()` → `reset_index()` (đều được tài liệu liệt kê); không dùng `.sort_values()` nếu chưa được cho phép.
- Cần xác minh xem CSV đã là phiên giao dịch liên tiếp và xử lý thế nào khi thiếu ngày; **không** mặc định mỗi ngày lịch là một phiên.

## 2. Công thức lợi suất–rủi ro

Cho một mã với chuỗi giá đóng cửa đã sắp thứ tự `P_0, P_1, ..., P_n` ở các phiên hợp lệ. Chỉ số `t` là **thứ tự phiên giao dịch**, không phải ngày lịch.

| Chỉ tiêu | Công thức / quy ước | Điều kiện |
|---|---|---|
| Daily price return | `r_t = P_t / P_(t-1) - 1`, `t>=1` | `P_(t-1)>0`, hai quan sát cùng mã; ngày đầu không có return |
| Cumulative price return | `R_t = P_t / P_0 - 1` | `P_0>0`; mốc chuẩn hóa phải công bố |
| Normalized price index | `I_t = 100 * P_t/P_0` | So sánh 5–10 mã cùng mốc ngày khi thích hợp |
| Average daily return | `mean(r_1,...,r_n)` | Có tối thiểu 1 daily return hợp lệ |
| Daily volatility | Độ lệch chuẩn của daily returns, dùng `std` theo quy ước xác định khi code | Có đủ phiên; nêu rõ đơn vị theo ngày và quy ước độ lệch chuẩn |
| CAGR (price-based) | `(P_end / P_start)**(1/Y) - 1` | `Y>0` là số năm lịch giữa ngày bắt đầu/kết thúc thực tế; giá hợp lệ |

**Điểm cần chốt khi kiểm tra CSV:** dùng cửa sổ chung hay chỉ chấp nhận các mã có đủ dữ liệu; cách xác định `Y` bằng ngày thực; quy ước population/sample volatility; cách trình bày giá chưa adjusted. Không trộn kết quả các cửa sổ quan sát không tương đương vào bảng xếp hạng chung.

**Thực hiện bằng kiến thức được phép:** vòng `for`, `range`, indexing/slicing, phép toán `+ - * / **`, NumPy `np.array()`, `.mean()`, `.std()`, `np.sqrt()`, `np.unique()`, `.copy()`, `pd.to_datetime()` và Pandas `groupby` theo những ví dụ nằm trong tài liệu. **Không dùng** `.pct_change()`, `.shift()`, `.rolling()`, `.cummax()`.

**Ngoài phạm vi bắt buộc:** Maximum Drawdown; có thể thêm khi thật sự cần bằng vòng lặp và phép so sánh cơ bản, với công thức `DD_t = P_t / max(P_0,...,P_t) - 1`, `MDD = min_t DD_t`. Cần kiểm tra nguồn giá trước khi diễn giải.

### 2.1 Tiêu chí so sánh và chọn mã
1. Kiểm tra số phiên và khoảng ngày của từng mã.
2. Đặt tiêu chí tối thiểu **sau khi xem dữ liệu thực**; ưu tiên một khoảng thời gian so sánh chung.
3. Xếp hạng top/bottom CAGR chỉ trong nhóm đủ điều kiện.
4. Chọn 5–10 mã theo **quy tắc công bố** (ví dụ điển hình các mức CAGR/volatility khác nhau; tránh chọn chỉ những mã đã nổi tiếng).
5. Ghi bảng `ticker / lý do được chọn / số phiên / ngày đầu–cuối` trong báo cáo.

### 2.2 Trực quan hóa
- `sns.histplot(...)` hoặc `ax.hist(...)`: phân phối daily return; tránh hiểu dữ liệu gộp mọi ngày/mọi mã là các quan sát độc lập.
- `ax.bar(...)`, `ax.barh(...)`: nhóm có CAGR cao/thấp. Nếu có giá trị âm, không thể đặt giá trị gốc của trục phần âm bằng 0 một cách máy móc; giữ **đường gốc 0** và thể hiện cả phần âm/dương trung thực, đồng thời tuân thủ nguyên tắc biểu đồ của giáo trình.
- `ax.scatter(...)`: CAGR so với volatility.
- `ax.plot(...)`: chỉ số giá chuẩn hóa (mốc 100) hoặc cumulative price return cho 5–10 mã.
- Dùng `ax.set_title`, `ax.set_xlabel`, `ax.set_ylabel`, `ax.legend`, `plt.tight_layout`, `plt.savefig` khi cần.

## 3. Phân nhóm theo quy tắc (không phải clustering ML)

**Đơn vị phân tích:** mỗi mã = một dòng trong bảng chỉ tiêu.

**Hai biến:** CAGR (hiệu suất) và daily volatility (biến động). Chỉ mã qua bộ lọc đủ điều kiện mới tham gia.

**Ngưỡng phân loại dự kiến:** trung bình CAGR và trung bình volatility của các mã đủ điều kiện (`mean` được phép). Đây là phương pháp dễ kiểm chứng, nhưng có thể nhạy với ngoại lai; diễn giải ngưỡng trong báo cáo. Nếu muốn đổi ngưỡng, ghi phiên bản và lý do trước khi so sánh kết quả.

| Nhóm | Điều kiện |
|---|---|
| A | `CAGR >= mean_CAGR` và `volatility < mean_volatility` |
| B | `CAGR >= mean_CAGR` và `volatility >= mean_volatility` |
| C | `CAGR < mean_CAGR` và `volatility < mean_volatility` |
| D | `CAGR < mean_CAGR` và `volatility >= mean_volatility` |

- Thao tác: Boolean indexing, `np.where()` (có thể lồng theo điều kiện), `.groupby(...)`, `.mean()`, `pd.crosstab(...)` nếu phù hợp, scatter phân màu với `ax.scatter`/`sns.scatterplot`.
- Đầu ra: số mã theo nhóm, CAGR/volatility bình quân từng nhóm, giải thích nhãn **tương đối**.
- Không gọi nhóm là K-Means cluster; không nhận định quan hệ nhân quả hoặc đảm bảo sinh lời.

## 4. Học máy có giám sát (tùy chọn, nếu chốt thực hiện)

### 4.1 Bài toán và thời điểm dự đoán
- Dự đoán **sau khi kết thúc phiên `t`**: giá đóng cửa `t+1` tăng so với `t` hay không.
- `y_t = 1` nếu `P_(t+1) > P_t`, ngược lại `0`.
- Các dòng cuối chuỗi mỗi mã **không có nhãn**, phải loại khỏi tập học máy.
- Xây dựng nhãn với vòng lặp/indexing trên chuỗi đã sắp xếp theo mã–ngày. Không dùng `.shift()`.

### 4.2 Đặc trưng có thể tạo bằng phép toán cơ bản

| Biến đầu vào cho ngày `t` | Công thức / mô tả | Ghi chú |
|---|---|---|
| `return_1d_t` | `close_t / close_(t-1) - 1` | Cần phiên trước cùng mã |
| `range_t` | `(high_t - low_t) / open_t` | Chỉ khi `open_t>0` |
| `intraday_t` | `(close_t - open_t) / open_t` | Chỉ khi `open_t>0` |
| `volume_t` | Khối lượng phiên `t` | Không dùng volume của `t+1` |
| `volume_change_t` | `volume_t/volume_(t-1)-1` | Chỉ khi volume trước > 0; xử lý volume = 0 rõ ràng |

Không dùng đặc trưng từ `t+1`; không tạo lag/rolling qua ranh giới mã. Các biến được công bố là **giả thuyết thử nghiệm**, không phải đã được chứng minh hữu ích.

### 4.3 Chia train/test đúng theo thời gian
- Kế hoạch: dữ liệu để huấn luyện trước năm 2017 và đánh giá trên năm 2017, tùy phạm vi ngày thực tế.
- **Quan trọng:** Mẫu train phải có cả ngày tạo nhãn `t+1` nằm trong giai đoạn train; bỏ mẫu sát ranh giới nếu ngày tương lai thuộc test. Khi tạo đặc trưng test có thể dùng thông tin giá **đã quan sát đến `t`** từ giai đoạn trước, nhưng không lấy nhãn test để fit.
- Không chia ngẫu nhiên theo bản ghi; không dùng `train_test_split` mặc định vì không phù hợp mục tiêu đánh giá theo thời gian. Lọc theo ngày bằng Boolean indexing.
- Chỉ huấn luyện trên dòng có đủ đặc trưng hợp lệ và nhãn.
- **Chống data leakage:** bất cứ thống kê chuẩn hóa/điền khuyết học từ dữ liệu phải fit train, rồi áp dụng test; không tính tham số trên train+test.

### 4.4 Mô hình
- **Logistic Regression**: `LogisticRegression(max_iter=..., random_state=...)` (mô hình cơ sở), trên đầu vào chuẩn hóa bằng `StandardScaler().fit_transform(X_train)` và `.transform(X_test)`.
- **Random Forest**: `RandomForestClassifier(n_estimators=..., random_state=...)` (mô hình đối chiếu). Không cần ép chuẩn hóa chỉ vì Logistic Regression cần; nếu sử dụng cùng đầu vào chuẩn hóa phải nói rõ.
- Chỉ dùng `.fit`, `.predict`, `.predict_proba` được phép theo tài liệu (đối chiếu lớp sklearn tương ứng). Không tự thêm search/tuning/cross-validation chưa được cho phép.

## 5. Đánh giá ML (tùy chọn)

**Baseline:** xác định nhãn phổ biến nhất **trên train**, sau đó dự đoán nhãn ấy cho mọi mẫu trong test. Không dùng phân phối test để chọn baseline.

| Chỉ số | Cách thực hiện | Cần lưu ý |
|---|---|---|
| Accuracy | `accuracy_score(...)` | Dễ gây hiểu nhầm khi lệch lớp |
| Precision | `precision_score(...)` | Lớp dương là tăng giá (`1`), xử lý khi không có dự đoán dương |
| Recall | `recall_score(...)` | Lớp dương là tăng giá (`1`) |
| F1 | `2 * precision * recall / (precision + recall)` | Tự tính bằng phép toán cơ bản, mẫu số 0 → quy ước 0 |
| Confusion Matrix | `confusion_matrix(...)` | Giải thích TP, FP, TN, FN |
| ROC-AUC | `roc_auc_score(...)` với `predict_proba` khi khả thi | Chỉ có nghĩa khi test có cả hai lớp; so sánh bằng điểm/xác suất không phải dự đoán nhị phân |

**Giải thích mô hình:** có thể mô tả hệ số `.coef_` của Logistic Regression (thuộc tài liệu); không sử dụng `feature_importances_` nếu danh sách chưa ghi rõ. Cường độ hệ số/đóng góp của biến không cho phép suy luận nhân quả.

**Diễn giải bắt buộc:** so sánh hai mô hình với baseline trên cùng test; predictive accuracy không chứng minh phương pháp đầu tư có lãi; không có backtest phí/slippage.

## 6. Storytelling và chất lượng kết luận

1. **Mức độ đáng tin của dữ liệu**: kiểm toán dữ liệu và tính đủ điều kiện.
2. **Hiệu suất–rủi ro**: mã nào nổi bật, biến động kèm theo ra sao, giới hạn đo lường.
3. **Nhóm mô tả**: bốn nhóm CAGR–volatility khác gì nhau, tương đối theo mẫu.
4. **ML nếu triển khai**: có vượt baseline không, tại sao chưa đủ để giao dịch.
5. **Hàm ý**: bộ chỉ tiêu phù hợp làm bộ lọc/điểm khởi đầu nghiên cứu thêm; không tuyên bố khuyến nghị mua/bán chắc chắn.

**Giới hạn phải báo cáo:** chỉ 2014–2017; có thể chưa điều chỉnh cổ tức/chia tách; danh sách công ty không phản ánh lịch sử thành phần chỉ số ở mọi thời điểm; không có lãi suất phi rủi ro, chi phí giao dịch và yếu tố cơ bản; không suy rộng sang tương lai.

## 7. Bảng đối chiếu thư viện / hàm ↔ chương học

| Nhóm thao tác | Hàm, cú pháp tiêu biểu **có trong file gốc** | Chương trong file gốc |
|---|---|---|
| Python cơ bản | `for`, `if`, `range`, indexing/slicing, `len`, `dict`, `list`, toán tử so sánh và số học | 2–3 |
| NumPy | `np.array`, `np.unique`, `np.where`, `.mean`, `.std`, `np.sqrt`, `.copy` | 4–5 |
| Import/export | `pd.read_csv`, `pd.to_datetime`, `df.to_csv` | 6–7 |
| Data cleaning | `.isna`, `.dropna`, `.duplicated`, `.drop_duplicates`, Boolean indexing | 8–9 |
| Nhóm / sắp xếp | `.set_index`, `.sort_index`, `.reset_index`, `.groupby(level=...)`, `pd.crosstab`, `pd.pivot_table`, `pd.merge` (nếu cần) | 10–11 |
| Matplotlib | `plt.subplots`, `ax.plot`, `ax.scatter`, `ax.hist`, `ax.bar`, `ax.barh`, `ax.set_title`, `ax.set_xlabel`, `ax.set_ylabel`, `ax.legend`, `plt.tight_layout` | 12–13 |
| Seaborn | `sns.histplot`, `sns.boxplot`, `sns.scatterplot`, `sns.heatmap` | 12–13 |
| Mô hình (tùy chọn) | `LogisticRegression`, `RandomForestClassifier`, `.fit`, `.predict`, `.predict_proba`, `StandardScaler` | 14–15 |
| Metrics (tùy chọn) | `accuracy_score`, `precision_score`, `recall_score`, `confusion_matrix`, `classification_report`, `roc_curve`, `roc_auc_score` | 14–15 |

**Chú ý:** Các bảng trên chỉ liệt kê công cụ dự kiến dùng trong project, **không phải toàn bộ công cụ được cho phép**. Muốn thêm hàm/phương thức nào, tra đúng mục trong `allowed_knowledge_reference.md`. Ví dụ: `.sort_values`, `.head`, `.info`, `.describe`, `.pct_change`, `.rolling`, `.shift`, `.cummax`, `KMeans`, `PCA`, `silhouette_score`, `f1_score`, `feature_importances_` hiện **không được tự ý sử dụng**.

## 8. Các kiểm tra trước khi bắt đầu triển khai

- [ ] CSV đúng tên và đường dẫn; tên cột thực tế, đơn vị giá/volume và định dạng ngày.
- [ ] Khả năng giá đã điều chỉnh (nếu không xác nhận được, phải diễn giải là biến động **giá được cung cấp**, không phải total return).
- [ ] Khóa duy nhất ticker–date, các sự kiện trùng/thiếu, các thay đổi giá quá lớn.
- [ ] Chốt bộ lọc số phiên và khoảng ngày; chốt 5–10 mã biểu diễn.
- [ ] Chốt môi trường notebook và có đưa ML tùy chọn vào bản nộp không.
- [ ] Kiểm tra từng lời gọi hàm khi viết notebook với tài liệu cho phép.

---

**Nguyên tắc cuối:** Không viết ra insight định lượng trước khi chạy dữ liệu. Mỗi kết luận phải dẫn được tới bảng hoặc biểu đồ thực tế trong notebook. Khi thiết kế thuật toán cần cú pháp chưa rõ được phép, đánh dấu `NEEDS_REVIEW` và không tự thay thế bằng một hàm ngoài danh sách.
