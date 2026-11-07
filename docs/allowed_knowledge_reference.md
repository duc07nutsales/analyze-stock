# Bảng Quy Chuẩn Kiến Thức & Thư Viện Python Cho Phép Trong Dự Án
*(Dựa trên giáo trình "Khoa học dữ liệu cơ bản trong kinh tế và kinh doanh", ĐH Kinh tế Quốc dân, 2026)*

Tài liệu này tổng hợp toàn bộ các thư viện, hàm, phương thức, cú pháp và khái niệm khoa học dữ liệu xuất hiện trong tài liệu. Bất kỳ thành viên nào tham gia dự án đều có thể sử dụng các nội dung này làm chuẩn mực kỹ thuật ("allowed knowledge").

---

## 1. Tổng Quan Về Các Thư Viện Được Phép Sử Dụng (Allowed Libraries)

| Thư viện | Alias quy ước | Mục đích chính |
| :--- | :--- | :--- |
| **Python Standard Library** | `math`, `random`, `re`, `time`, `os`, `sqlite3`, `datetime`, `warnings`, `io` | Tính toán cơ bản, xử lý số ngẫu nhiên, regex, thời gian, kết nối SQLite cục bộ, xử lý luồng dữ liệu |
| **NumPy** | `np` | Xử lý mảng đa chiều (`ndarray`), đại số tuyến tính, tính toán vector hóa, thống kê mảng |
| **Pandas** | `pd` | Cấu trúc dữ liệu bảng (`Series`, `DataFrame`), đọc/ghi dữ liệu, biến đổi cấu trúc, lọc/gộp |
| **Matplotlib** | `plt` (`matplotlib.pyplot`), `matplotlib.patches` | Trực quan hóa dữ liệu cơ bản, quản lý figure/axes, subplot |
| **Seaborn** | `sns` | Trực quan hóa dữ liệu thống kê mức cao, biểu đồ phân phối, tương quan, lưới phân loại |
| **Scikit-learn** | `sklearn.*` | Tiền xử lý, chia dữ liệu, huấn luyện mô hình học máy có giám sát, đánh giá chỉ số |
| **Requests & BeautifulSoup**| `requests`, `bs4.BeautifulSoup` | Thu thập dữ liệu web (Web scraping), gọi REST API, phân tích HTML/XML (RSS) |
| **Openpyxl / xlrd** | (Engine ngầm định) | Đọc và ghi tệp Excel qua `pd.read_excel` và `pd.ExcelWriter` |
| **Google Colab Drive** | `google.colab.drive` | Gắn kết bộ nhớ đám mây khi chạy trên môi trường Google Colab |

---

## 2. Chi Tiết Kiến Thức & Hàm Được Phép Theo Từng Chương

### CHƯƠNG 1 & CHƯƠNG 14 & CHƯƠNG 15: Quy Trình Khoa Học Dữ Liệu & Học Máy Có Giám Sát (Scikit-Learn)

#### 1. Quy trình chuẩn (Chu trình KHDL & Dự án ML)
1. **Xác định bài toán (Problem Definition):** Định rõ mục tiêu kinh doanh, chỉ số đánh giá, yêu cầu dữ liệu.
2. **Thu thập dữ liệu (Data Collection):** Cơ sở dữ liệu nội bộ, API, tệp tin, Web Scraping.
3. **Khai phá dữ liệu (EDA - Exploratory Data Analysis):** Thống kê mô tả, phát hiện ngoại lai, trực quan hóa.
4. **Tiền xử lý dữ liệu (Data Preprocessing):** Xử lý thiếu, loại bỏ trùng lặp, chuẩn hóa, mã hóa biến phân loại.
5. **Huấn luyện mô hình (Model Training):** Chia Train/Test, chọn thuật toán, khớp mô hình qua `.fit()`.
6. **Đánh giá mô hình (Model Evaluation):** Đo lường hiệu suất trên tập test độc lập.
7. **Triển khai & giám sát (Deployment & Monitoring):** Tích hợp vào hệ thống, theo dõi trôi dữ liệu/suy giảm hiệu năng.

#### 2. Các hàm và lớp trong `sklearn`
* **Chia tập dữ liệu:**
  * `sklearn.model_selection.train_test_split(X, y, test_size=..., random_state=..., stratify=...)`
* **Mô hình Hồi quy (Regression):**
  * `sklearn.linear_model.LinearRegression()`
    * Thuộc tính: `.coef_`, `.intercept_`
    * Phương thức: `.fit(X, y)`, `.predict(X)`
  * `sklearn.neighbors.KNeighborsRegressor(n_neighbors=k)`
  * `sklearn.tree.DecisionTreeRegressor(max_depth=..., random_state=...)`
  * `sklearn.ensemble.RandomForestRegressor(n_estimators=..., max_depth=..., max_features=..., random_state=...)`
* **Mô hình Phân loại (Classification):**
  * `sklearn.linear_model.LogisticRegression(max_iter=..., class_weight=..., random_state=...)`
    * Phương thức: `.fit(X, y)`, `.predict(X)`, `.predict_proba(X)`
  * `sklearn.neighbors.KNeighborsClassifier(n_neighbors=k)`
  * `sklearn.tree.DecisionTreeClassifier(max_depth=..., random_state=...)`
  * `sklearn.ensemble.RandomForestClassifier(n_estimators=..., random_state=...)`
* **Tiền xử lý và Điền khuyết (Preprocessing & Imputation):**
  * `sklearn.preprocessing.StandardScaler()`: $Z = \frac{X - \mu}{\sigma}$ (Dùng `.fit_transform()` cho Train, `.transform()` cho Test).
  * `sklearn.preprocessing.MinMaxScaler()`: $X_{\text{norm}} = \frac{X - X_{\min}}{X_{\max} - X_{\min}}$ (Đưa về khoảng $[0, 1]$).
  * `sklearn.preprocessing.RobustScaler()`: $X_{\text{robust}} = \frac{X - X_{\text{median}}}{\text{IQR}}$ (Chống chịu ngoại lai).
  * `sklearn.preprocessing.LabelEncoder()`: `.fit_transform()`, `.classes_`.
  * `sklearn.preprocessing.OneHotEncoder(sparse_output=False, drop='first')`: `.fit_transform()`, `.get_feature_names_out()`.
  * `sklearn.impute.KNNImputer(n_neighbors=..., weights=..., metric='nan_euclidean')`.
* **Đo lường & Đánh giá (Metrics):**
  * **Hồi quy:**
    * `sklearn.metrics.mean_squared_error(y_true, y_pred)` $\rightarrow \text{RMSE} = \sqrt{\text{MSE}}$
    * `sklearn.metrics.mean_absolute_error(y_true, y_pred)` (MAE)
    * `sklearn.metrics.r2_score(y_true, y_pred)` ($R^2$)
  * **Phân loại:**
    * `sklearn.metrics.accuracy_score(y_true, y_pred)`
    * `sklearn.metrics.precision_score(y_true, y_pred, pos_label=...)`
    * `sklearn.metrics.recall_score(y_true, y_pred, pos_label=...)`
    * `sklearn.metrics.confusion_matrix(y_true, y_pred)`
    * `sklearn.metrics.classification_report(y_true, y_pred)`
    * `sklearn.metrics.roc_curve(y_true, y_score)` $\rightarrow \text{fpr}, \text{tpr}, \text{thresholds}$
    * `sklearn.metrics.roc_auc_score(y_true, y_score)`
* **Trực quan hóa cấu trúc mô hình:**
  * `sklearn.tree.plot_tree(model, feature_names=..., class_names=..., filled=True, rounded=True, precision=...)`
* **Dữ liệu mẫu chuẩn tích hợp sẵn:**
  * `sklearn.datasets.fetch_california_housing()`
  * `sklearn.datasets.load_breast_cancer()`

---

### CHƯƠNG 2 & CHƯƠNG 3: Ngôn Ngữ Lập Trình Python Căn Bản

* **Kiểu dữ liệu nguyên thủy & kiểm tra:**
  * `int`, `float`, `bool` (`True`/`False`), `str`
  * Hàm hệ thống: `type()`, `print()`, `input()`, `len()`, `isinstance()`
* **Toán tử số học & so sánh:**
  * Số học: `+`, `-`, `*`, `/` (luôn trả về float), `//` (chia lấy nguyên), `%` (chia lấy dư), `**` (lũy thừa)
  * So sánh: `==`, `!=`, `>`, `>=`, `<`, `<=`, `is`
  * Logic: `and`, `or`, `not`
* **Ép kiểu (Type Casting):**
  * `int()`, `float()`, `str()`, `list()`, `tuple()`, `set()`, `dict()`
* **Cấu trúc dữ liệu chuỗi (String):**
  * Định dạng chuỗi: `f"...{var}..."` (f-string)
  * Phương thức: `.lower()`, `.upper()`, `.strip()`, `.replace(old, new)`, `.split(sep)`, `sep.join(list)`, `.startswith()`, `.endswith()`
* **Cấu trúc dữ liệu tuần tự & tập hợp:**
  * **List `[]` (mutable):** `.append()`, indexing, slicing `[start:stop:step]`, chỉ số âm `[-1]`.
  * **Tuple `()` (immutable):** Lưu trữ giá trị có thứ tự không thay đổi, unpacking `s, p = func()`.
  * **Set `{}` (unique, unordered):** Loại bỏ trùng lặp, toán tử tập hợp.
  * **Dictionary `{k: v}` (mutable, mapping):** Truy cập khóa `d[key]`, gán mới, `.keys()`, `.values()`, `.items()`.
* **Cấu trúc điều khiển & Vòng lặp:**
  * Rẽ nhánh: `if`, `elif`, `else`, cú pháp rút gọn 1 dòng: `x = a if cond else b`.
  * Vòng lặp: `for ... in ...:`, `while ...:`, `range(start, stop, step)`, `enumerate()`, `zip()`.
  * **List Comprehension:** `[expr for item in iterable if condition]`.
* **Hàm (Functions):**
  * Định nghĩa hàm: `def func_name(param1, opt_param=default): return value`.
  * Trả về nhiều giá trị thông qua tuple.
  * Hàm nặc danh: `lambda x: x + 1`.
* **Thư viện chuẩn hỗ trợ:**
  * `math.pi`, `math.sqrt()`
  * `random.randint()`, `random.choice()`, `random.normalvariate()`

---

### CHƯƠNG 4 & CHƯƠNG 5: Thư Viện Nền Tảng - NumPy

* **Khởi tạo đối tượng mảng (`ndarray`):**
  * `np.array(object, dtype=...)`
  * `np.zeros(shape)`, `np.zeros_like(arr)`
  * `np.ones(shape)`, `np.ones_like(arr)`
  * `np.empty(shape)`, `np.empty_like(arr)`
  * `np.full(shape, fill_value)`, `np.full_like(arr, fill_value)`
  * `np.arange(start, stop, step)`
  * `np.linspace(start, stop, num)`
  * `np.eye(N)`, `np.identity(N)`
  * `np.meshgrid(x_points, y_points)`
* **Thuộc tính mảng:**
  * `arr.shape`, `arr.dtype`, `arr.ndim`, `arr.T` (chuyển vị)
* **Ép kiểu & Sao chép:**
  * `arr.astype(np.float64 / np.int32 / ...)`
  * `arr.copy()` (tạo bản sao thực sự, tách rời view)
* **Định hình lại & Hoán đổi trục:**
  * `arr.reshape(shape)`
  * `arr.transpose(axes)`
  * `arr.swapaxes(ax1, ax2)`
* **Truy cập & Cắt lát (Indexing & Slicing):**
  * Cắt lát cơ bản: `arr[r_start:r_stop, c_start:c_stop]` (tạo view)
  * Fancy indexing (mảng chỉ số nguyên): `arr[[r1, r2], [c1, c2]]` (tạo copy)
  * Lưới chỉ số hình chữ nhật: `np.ix_([r1, r2], [c1, c2])`
  * Boolean indexing: `arr[arr > 0]`, kết hợp điều kiện bằng toán tử bitwise: `&` (and), `|` (or), `~` (not)
* **Hàm xử lý phần tử (Universal Functions - UFuncs):**
  * Đơn biến (Unary): `np.abs()`, `np.sqrt()`, `np.square()`, `np.exp()`, `np.log()`, `np.log10()`, `np.ceil()`, `np.floor()`, `np.rint()`, `np.modf()`, `np.isnan()`, `np.isfinite()`, `np.isinf()`, `np.cos()`, `np.sin()`
  * Nhị biến (Binary): `np.add()`, `np.subtract()`, `np.multiply()`, `np.divide()`, `np.maximum()`, `np.minimum()`, `np.power()`, `np.mod()`, `np.greater()`, `np.less()`, `np.equal()`
* **Biểu thức điều kiện:**
  * `np.where(condition, x, y)` (vectorized `x if cond else y`)
* **Thống kê & Toán học mảng:**
  * `arr.sum(axis=...)`, `np.sum(arr, axis=...)`
  * `arr.mean(axis=...)`, `np.mean(arr, axis=...)`
  * `arr.std()`, `arr.var()`, `arr.min()`, `arr.max()`
  * `arr.argmin()`, `arr.argmax()` (vị trí cực trị)
  * `arr.cumsum(axis=...)` (tổng tích lũy), `arr.cumprod(axis=...)` (tích tích lũy)
* **Mảng kiểu Boolean:**
  * `(arr > 0).sum()` (đếm số lượng True)
  * `arr.any()`, `arr.all()`
* **Sắp xếp & Tập hợp:**
  * `arr.sort(axis=...)` (sắp xếp tại chỗ)
  * `np.sort(arr)` (trả về bản sao đã sắp xếp)
  * `np.unique(arr)` (phần tử duy nhất)
  * `np.isin(arr, values_list)`
  * `np.intersect1d()`, `np.union1d()`, `np.setdiff1d()`, `np.setxor1d()`
* **Đại số tuyến tính (`numpy.linalg`):**
  * Phép nhân ma trận: `np.dot(A, B)` hoặc toán tử `@`
  * `np.linalg.inv(A)` (nghịch đảo), `np.linalg.det(A)` (định thức)
  * `np.linalg.pinv()`, `np.linalg.qr()`, `np.linalg.svd()`, `np.linalg.eig()`, `np.linalg.solve()`, `np.trace()`, `np.diag()`
* **Sinh số ngẫu nhiên (`np.random`):**
  * Bộ sinh: `rng = np.random.default_rng(seed=12345)`
  * Phân phối: `rng.standard_normal()`, `rng.uniform()`, `rng.integers()`, `rng.normal()`, `rng.poisson()`
  * Trực tiếp: `np.random.standard_normal()`, `np.random.uniform()`, `np.random.choice()`
* **Nhập/Xuất file nhị phân & văn bản:**
  * `np.save("file.npy", arr)`, `np.load("file.npy")`
  * `np.savez("archive.npz", a=arr1, b=arr2)`
  * `np.loadtxt("file.txt", delimiter=",")`, `np.savetxt("file.txt", arr, delimiter=",")`

---

### CHƯƠNG 6 & CHƯƠNG 7: Nhập & Lưu Trữ Dữ Liệu Với Python

* **Đọc/Ghi dữ liệu dạng bảng với Pandas:**
  * CSV/Text: `pd.read_csv(filepath, sep=..., header=..., names=..., index_col=..., skiprows=..., encoding=...)`
  * Xuất CSV: `df.to_csv("file.csv", index=False, encoding="utf-8")`
  * Excel: `pd.read_excel(filepath, sheet_name=...)`
  * Lớp xử lý nhiều sheet: `xlsx = pd.ExcelFile(filepath); df = xlsx.parse(sheet_name=...)`
  * Ghi nhiều sheet Excel:
    ```python
    with pd.ExcelWriter("out.xlsx") as writer:
        df1.to_excel(writer, sheet_name="Sheet1")
        df2.to_excel(writer, sheet_name="Sheet2")
    ```
  * JSON: `pd.read_json(filepath)`
  * HTML Table: `tables = pd.read_html(url_or_io)` (trả về danh sách DataFrames)
  * Chuyển đổi định dạng ngày tháng: `pd.to_datetime(col)`
* **Tương tác Web API & XML/RSS:**
  * Gọi API: `res = requests.get(url, headers=...)`
  * Kiểm tra phản hồi: `res.status_code == 200`, `res.raise_for_status()`
  * Trích xuất JSON: `data = res.json()`
  * Phân tích XML/HTML bằng BeautifulSoup:
    * `soup = BeautifulSoup(res.content, 'xml')`
    * `soup.find_all('item')`, `item.find('title').text`
* **Tương tác Cơ sở dữ liệu SQLite (`sqlite3`):**
  * Kết nối: `con = sqlite3.connect("dbname.sqlite")`
  * Thực thi SQL: `con.execute(query)`, `con.executemany(query, list_of_tuples)`, `con.commit()`, `con.close()`
  * Đọc vào Pandas:
    ```python
    cursor = con.execute("SELECT * FROM table")
    df = pd.DataFrame(cursor.fetchall(), columns=[x[0] for x in cursor.description])
    ```
  * Hoặc sử dụng trực tiếp: `pd.read_sql(query, con)`

---

### CHƯƠNG 8 & CHƯƠNG 9: Làm Sạch & Chuẩn Bị Dữ Liệu

* **Xử lý dữ liệu thiếu (Missing Data - `NaN`, `None`, `NaT`):**
  * Nhận diện: `df.isna()`, `df.isnull()`, `df.notna()`, `df.notnull()`
  * Thống kê: `df.isna().sum()`, `df.isna().any()`
  * Loại bỏ: `df.dropna(axis=0/1, how='any'/'all', thresh=..., subset=[...])`
  * Điền khuyết cơ bản:
    * Cố định / Thống kê: `df.fillna(value)`, `df['col'].fillna(df['col'].mean())`, `.median()`, `.mode()[0]`
    * Dãy thời gian: `df.ffill()` (forward-fill), `df.bfill()` (backward-fill)
  * Điền khuyết nâng cao: Sử dụng `RandomForestRegressor`, `KNNImputer`.
* **Xử lý dữ liệu trùng lặp (Duplicate Data):**
  * Nhận diện: `df.duplicated(subset=[...], keep='first'/'last'/False)`
  * Loại bỏ: `df.drop_duplicates(subset=[...], keep='first'/'last'/False)`
* **Xử lý chuỗi ký tự qua Pandas Accessor (`.str`):**
  * Làm sạch: `.str.lower()`, `.str.upper()`, `.str.title()`, `.str.strip()`
  * Tìm kiếm & Lọc: `.str.contains(pattern, case=..., regex=...)`, `.str.startswith()`, `.str.endswith()`
  * Biến đổi: `.str.replace(pat, repl, regex=...)`, `.str.split(sep)`, `.str.len()`
  * Biểu thức chính quy (Regex): `.str.extract(pattern)`, `.str.findall(pattern)`
* **Xử lý dữ liệu phân loại (Categorical Data):**
  * Kiểu `pd.Categorical`: `pd.Categorical(df['col'], categories=[...], ordered=True)`
  * Mã hóa One-Hot bằng Pandas: `pd.get_dummies(df, columns=[...], drop_first=True)`
  * Đồng bộ cột giữa train và test: `X_train_enc.align(X_test_enc, join='left', axis=1, fill_value=0)`

---

### CHƯƠNG 10 & CHƯƠNG 11: Sắp Xếp, Biến Đổi & Cấu Trúc Lại Dữ Liệu

* **Chỉ số phân cấp (Hierarchical Indexing / `MultiIndex`):**
  * Tạo chỉ mục: `df.set_index(['col1', 'col2'], drop=True/False)`
  * Hủy chỉ mục thành cột: `df.reset_index()`
  * Tạo MultiIndex thủ công: `pd.MultiIndex.from_tuples(...)`
  * Truy xuất dữ liệu:
    * Theo cấp ngoài: `df.loc['key1']`
    * Cắt lớp chéo (Cross-section): `df.xs('key2', level='col2')`
  * Hoán đổi cấp chỉ số: `df.swaplevel(0, 1)`
  * Sắp xếp theo chỉ số: `df.sort_index(level=...)`
  * Thống kê theo cấp: `df.groupby(level=...).mean()`
* **Kết hợp dữ liệu (Combining Datasets):**
  * **`pd.merge(left, right, ...)`:**
    * Các kiểu kết hợp (`how`): `'inner'`, `'outer'`, `'left'`, `'right'`
    * Khóa gộp: `on='key'`, hoặc `left_on='key1', right_on='key2'`
    * Gộp theo index: `left_index=True`, `right_index=True`
    * Xử lý tên cột trùng: `suffixes=('_x', '_y')`
    * Kiểm tra nguồn gốc hàng: `indicator=True` (cột `_merge`)
  * **`pd.concat([df1, df2, ...], axis=0/1, join='outer'/'inner', keys=[...])`:**
    * `axis=0`: Ghép nối theo dòng
    * `axis=1`: Ghép nối theo cột
    * `keys=[...]`: Tạo MultiIndex cho nguồn dữ liệu
* **Tổ chức lại cấu trúc bảng (Reshaping):**
  * Chuyển từ Rộng sang Dài (Wide to Long):
    * `df.melt(id_vars=[...], value_vars=[...], var_name='...', value_name='...')`
    * `df.stack(level=...)` (Nén cấp cột thành hàng)
  * Chuyển từ Dài sang Rộng (Long to Wide):
    * `df.pivot(index='...', columns='...', values='...')`
    * `df.pivot_table(index='...', columns='...', values='...', aggfunc='mean')`
    * `df.unstack(level=...)` (Giải nén cấp hàng thành cột)
  * Bảng chéo tần suất: `pd.crosstab(df['col1'], df['col2'])`

---

### CHƯƠNG 12 & CHƯƠNG 13: Trực Quan Hóa Dữ Liệu

#### 1. Nguyên lý thiết kế trực quan hóa (Wilke Framework)
* **Mục đích:** Khám phá (Exploration) vs Giải thích/Truyền đạt (Explanation/Storytelling).
* **Trung thực & Rõ ràng:**
  * Trục giá trị của biểu đồ cột **bắt buộc** phải bắt đầu từ 0 để phản ánh đúng tỷ lệ độ dài.
  * Tránh 3D không cần thiết; tránh quá nhiều màu sắc gây nhiễu thị giác.
  * Sử dụng bảng màu phù hợp: Phân loại (qualitative), Tuần tự (sequential), Phân kỳ (diverging).
  * Ưu tiên gắn nhãn trực tiếp (direct label) hơn là dùng bảng chú giải (legend) rời rạc khi có thể.

#### 2. Matplotlib (`matplotlib.pyplot`)
* **Khởi tạo:**
  * `fig = plt.figure(figsize=(w, h))`
  * `ax = fig.add_subplot(nrows, ncols, index)`
  * `fig, axes = plt.subplots(nrows, ncols, figsize=(w, h), sharex=False, sharey=False)`
* **Vẽ trên `Axes`:**
  * `ax.plot(x, y, color=..., linestyle=..., marker=..., label=..., drawstyle=...)`
  * `ax.scatter(x, y, color=..., marker=..., s=..., alpha=...)`
  * `ax.hist(data, bins=..., color=..., alpha=...)`
  * `ax.bar(x, height)`, `ax.barh(y, width)`
  * `ax.axvline(x=..., color=..., linestyle=...)`, `ax.axhline(y=...)`
* **Trang trí và Tùy biến:**
  * `ax.set_title()`, `ax.set_xlabel()`, `ax.set_ylabel()`
  * `ax.set(title=..., xlabel=..., ylabel=...)`
  * `ax.set_xlim([min, max])`, `ax.set_ylim([min, max])`
  * `ax.set_xticks([...])`, `ax.set_xticklabels([...], rotation=..., fontsize=...)`
  * `ax.legend(loc='best')`, `ax.grid(True, linestyle=..., alpha=...)`
* **Chú thích & Hình vẽ cơ bản:**
  * `ax.text(x, y, "Text", family=..., fontsize=...)`
  * `ax.annotate("Label", xy=(x_target, y_target), xytext=(x_text, y_text), arrowprops=dict(...))`
  * `matplotlib.patches`: `Rectangle()`, `Circle()`, `Polygon()`, thêm vào qua `ax.add_patch()`
* **Bố cục & Lưu trữ:**
  * `plt.tight_layout()`, `fig.subplots_adjust(wspace=..., hspace=...)`
  * `plt.savefig("filename.png", dpi=..., format="png"/"svg"/"pdf")`
  * Cấu hình toàn cục: `plt.rc("figure", figsize=(...))`, `plt.rcParams`, `plt.rcdefaults()`

#### 3. Pandas Plotting API
* Gọi trên Series / DataFrame: `obj.plot(kind='line'/'bar'/'barh'/'hist'/'kde'/'density'/'box'/'scatter', ax=..., subplots=..., layout=..., stacked=True/False, figsize=..., title=...)`
* Biểu đồ tần suất: `df['col'].value_counts().plot.bar()`

#### 4. Seaborn (`sns`)
* **Biểu đồ thống kê:**
  * Cột trung bình (có khoảng tin cậy): `sns.barplot(data=df, x=..., y=..., hue=..., orient='h'/'v')`
  * Đếm tần suất danh mục: `sns.countplot(data=df, x=...)`
  * Phân tán kèm đường hồi quy: `sns.regplot(data=df, x=..., y=..., ax=...)`
  * Phân tán điểm: `sns.scatterplot(data=df, x=..., y=..., hue=..., palette=..., s=...)`
  * Hộp phân phối: `sns.boxplot(data=df, x=..., y=..., color=...)`
  * Phân phối tần suất & KDE: `sns.histplot(data=..., bins=..., kde=True)`
  * Ma trận tương quan / Bảng nhiệt: `sns.heatmap(matrix, annot=True, fmt='d'/'0.2f', cmap='Blues')`
* **Đa diện & Lưới ma trận:**
  * Ma trận cặp biến: `sns.pairplot(df, diag_kind="kde", plot_kws={'alpha': 0.8})`
  * Lưới phân loại theo hàng/cột: `sns.catplot(data=df, x=..., y=..., hue=..., col=..., row=..., kind="bar"/"box")`
  * `sns.FacetGrid`
* **Thiết lập thẩm mỹ:**
  * `sns.set_style("whitegrid" / "darkgrid" / "white")`
  * `sns.set_palette("Set1" / "Greys_r")`

---

## 3. Quy Ước Code Đặt Biệt Cho Toàn Bộ Dự Án

1. **Tính Tái Lập (Reproducibility):** Mọi hàm ngẫu nhiên liên quan đến chia tập dữ liệu hoặc khởi tạo mô hình (`train_test_split`, `RandomForest`, `KMeans`, `np.random.default_rng`) đều phải chỉ định tham số `random_state` hoặc `seed`.
2. **Tránh Rò Rỉ Dữ Liệu (No Data Leakage):** Mọi bộ biến đổi chuẩn hóa (`StandardScaler`, `MinMaxScaler`, `Imputer`) **bắt buộc** chỉ được thực thi `fit` trên tập huấn luyện (`X_train`), sau đó dùng `transform` trên cả `X_train` và `X_test`.
3. **Độc Lập Bản Sao (Views vs Copies):** Khi cắt lát (`slicing`) DataFrame hoặc mảng NumPy mà có ý định chỉnh sửa giá trị, phải gọi `.copy()` một cách rõ ràng để tránh tác động ngược lên dữ liệu gốc hoặc gặp cảnh báo `SettingWithCopyWarning`.
4. **Trực Quan Hóa Chuẩn:** Mọi biểu đồ xuất ra phải có đầy đủ: tiêu đề (`title`), nhãn trục (`xlabel`, `ylabel`), chú giải đơn vị; nếu vẽ đồ thị cột so sánh giá trị tuyệt đối, trục số lượng phải bắt đầu từ 0.