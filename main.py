"""SolveX - trợ lý làm bài tập. Điểm khởi động ứng dụng."""

import sys

from PyQt6.QtWidgets import QApplication

from solvex.ui import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SolveX")
    app.setApplicationDisplayName("SolveX")
    # SolveX chạy nền qua tray icon + bảng điều khiển nổi, nên ẩn cửa sổ
    # đầy đủ (cài đặt/hội thoại) không được làm thoát ứng dụng.
    app.setQuitOnLastWindowClosed(False)

    window = MainWindow()  # tự hiện bảng điều khiển nổi + tray icon khi khởi tạo
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
