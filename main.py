"""SolveX - trợ lý làm bài tập. Điểm khởi động ứng dụng."""

import sys

from PyQt6.QtWidgets import QApplication

from solvex.ui import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SolveX")
    app.setApplicationDisplayName("SolveX")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
