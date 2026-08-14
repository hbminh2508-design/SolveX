"""SolveX - trợ lý làm bài tập. Điểm khởi động ứng dụng."""

import sys

from PyQt6.QtWidgets import QApplication

from solvex.security import SingleInstanceLock, apply_dll_hijack_protection
from solvex.ui import MainWindow


def main():
    apply_dll_hijack_protection()

    instance_lock = SingleInstanceLock()
    if not instance_lock.acquire():
        # Đã có 1 tiến trình SolveX đang chạy
        print("SolveX đã đang chạy trong hệ thống.")

    app = QApplication(sys.argv)
    app.setApplicationName("SolveX")
    app.setApplicationDisplayName("SolveX")
    app.setQuitOnLastWindowClosed(False)

    window = MainWindow()

    # Kiểm tra chế độ hiển thị khi khởi động (full / compact / tray)
    startup_mode = window.config.get("startup_mode", "compact")
    if startup_mode == "full":
        window.show_full_window()
        window.toolbar.show()
    elif startup_mode == "tray":
        window.minimize_to_tray()
        if window.tray:
            window.tray.showMessage(
                "SolveX",
                "SolveX đang chạy ngầm trong khay hệ thống.",
                window.tray.Icon.Information,
                3000,
            )
    else:  # "compact" mặc định
        window.toolbar.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
