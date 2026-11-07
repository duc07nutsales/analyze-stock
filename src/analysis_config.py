"""Các lựa chọn công bố trước khi diễn giải kết quả; chạy từ thư mục project."""

DATA_FILE = "data/S&P 500 Stock Prices 2014-2017.csv"
OUTPUT_DIR = "outputs"
MIN_COVERAGE = 0.95
EXTREME_RETURN = 0.20  # Chỉ gắn cờ |return| >= 20%, không tự xóa.
ML_RANDOM_STATE = 42
ML_N_TREES = 30
ML_MAX_ITER = 1000
