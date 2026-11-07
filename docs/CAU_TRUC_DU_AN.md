# Cấu trúc thư mục dự án

Tài liệu này mô tả vị trí, công dụng và mối liên hệ của từng nhóm file. Mọi lệnh chạy dưới đây bắt đầu ở **thư mục gốc dự án** (nơi có `run.ps1`).

```text
python_analyze_stock/
├── README.md                         Hướng dẫn bắt đầu
├── run.ps1                           Lệnh chạy trên Windows
├── test.ps1                          Lệnh chạy kiểm thử
├── requirements.txt                  Thư viện cần cài
├── requirements-lock.txt             Phiên bản thư viện đã kiểm tra
├── data/
│   └── S&P 500 Stock Prices 2014-2017.csv   Dữ liệu gốc
├── src/
│   ├── __init__.py                   Đánh dấu gói mã nguồn
│   ├── analysis_config.py            Đường dẫn và tham số
│   ├── sp500_analysis.py             Quy trình phân tích chính
│   └── sp500_ml.py                   Thử nghiệm học máy
├── notebooks/
│   └── sp500_analysis.ipynb          Báo cáo có code và kết quả từng bước
├── tests/
│   ├── __init__.py                   Đánh dấu gói kiểm thử
│   ├── test_analysis.py              Kiểm thử làm sạch, công thức, phân nhóm
│   └── test_ml.py                    Kiểm thử mẫu và đánh giá ML
├── docs/
│   ├── de_bai.md                     Đề gốc
│   ├── allowed_knowledge_reference.md  Giới hạn kiến thức được phép
│   ├── REQUIREMENTS.md               Yêu cầu chi tiết
│   ├── METHODOLOGY.md                 Phương pháp và công thức
│   ├── SP500_PROJECT_PLAN.md         Kế hoạch và trạng thái
│   ├── README_KE_HOACH_HOC_MAY.md    Thiết kế phần ML
│   ├── README_LUONG_HOAT_DONG.md     Luồng xử lý
│   ├── TONG_HOP_DU_AN.md             Bài tổng hợp kết quả
│   └── CAU_TRUC_DU_AN.md             File đang đọc
└── outputs/
    ├── report.md                     Báo cáo sinh từ chương trình
    ├── validation.md                 Bản ghi kiểm chứng đã thực hiện
    ├── tables/                       CSV kết quả trung gian và cuối
    └── figures/                      PNG biểu đồ
```

| Thư mục | Chứa gì và dùng để làm gì | Liên quan đến thư mục khác |
| --- | --- | --- |
| [data/](../data/) | CSV giá gốc, giữ nguyên để có thể chạy lại và đối chiếu. | `src/sp500_analysis.py` đọc file này theo đường dẫn trong `src/analysis_config.py`. |
| [src/](../src/) | Mã phân tích và cấu hình. `sp500_analysis.py` làm sạch, tính chỉ tiêu, phân nhóm, vẽ hình, viết báo cáo; sau đó gọi `sp500_ml.py` để đánh giá mô hình. | Đọc `data/`, ghi `outputs/`; được `run.ps1`, notebook và `tests/` sử dụng. |
| [notebooks/](../notebooks/) | Notebook trình bày từng phần code cùng bảng/hình đã chạy. | Dùng cùng CSV, cấu hình và thư mục đầu ra với script; cần mở từ gốc dự án để đường dẫn tương đối hoạt động. |
| [tests/](../tests/) | Các trường hợp dữ liệu nhỏ kiểm tra ý nghĩa công thức, làm sạch, ranh giới thời gian và chỉ số ML. | Import hàm từ `src/`; không phải đầu vào của phân tích chính. |
| [docs/](./) | Đề bài, giới hạn kiến thức, yêu cầu, phương pháp, kế hoạch và giải thích kết quả. | Giải thích các quyết định trong `src/` và cách đọc `outputs/`. |
| [outputs/](../outputs/) | Bảng, hình và báo cáo của lần chạy. | Được tạo bởi `src/` hoặc notebook. `report.md` liên kết hình bằng đường dẫn tương đối đến `figures/`. |

`run.ps1` là điểm chạy thuận tiện: tạo môi trường `.venv` nếu cần, chuẩn bị `outputs/tables/`, `outputs/figures/` rồi chạy `python -m src.sp500_analysis`. `test.ps1` chạy hai bộ kiểm thử với cấu hình terminal/cache phù hợp trên Windows. `requirements.txt` chứa thư viện cần cài; `requirements-lock.txt` ghi phiên bản của môi trường đã kiểm tra. `README.md` hướng dẫn thao tác ngắn.

## Cách các phần nối với nhau

```text
docs/de_bai.md + docs/allowed_knowledge_reference.md
                    ↓ quy định phạm vi
data/CSV → src/sp500_analysis.py → src/sp500_ml.py
                    ↓                    ↓
              outputs/tables/ + outputs/figures/
                              ↓
                       outputs/report.md
```

`src/analysis_config.py` cung cấp tên file dữ liệu, nơi lưu kết quả và tham số cho cả hai module. Notebook là cách xem và chạy lần lượt các bước; file `outputs/report.md` là báo cáo được sinh từ dữ liệu hiện tại. `docs/TONG_HOP_DU_AN.md` là bản tổng hợp đã viết cho phiên bản được kiểm tra, nên không tự thay đổi khi chạy lại chương trình.

## File tự sinh

`.venv/` là môi trường Python cục bộ; `.cache/` chứa cache Matplotlib/Jupyter và công cụ kiểm chứng trong quá trình phát triển; `__pycache__/` là bytecode Python. Các thư mục này không phải dữ liệu gốc hay kết quả cần nộp và được `.gitignore` bỏ qua. `outputs/validation.md` cũng là bản ghi kiểm chứng tĩnh, cần chạy lại công cụ kiểm chứng nếu dữ liệu hoặc code thay đổi.
