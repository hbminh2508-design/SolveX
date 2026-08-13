# -*- coding: utf-8 -*-
"""SolveX Updater — Ứng dụng kiểm tra và quản lý cập nhật độc lập cho SolveX (v1.9.0).
Chạy tách biệt hoàn toàn khỏi tiến trình SolveX.exe chính.
"""

import argparse
import os
import subprocess
import sys
import webbrowser

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from solvex import style
from solvex.ui import render_markdown, wrap_html_page
from solvex.updater import (
    TARGET_GITHUB_REPO,
    BuildExeWorker,
    CheckUpdateWorker,
    DownloadUpdateWorker,
)
from solvex.version import APP_VERSION, CHANGELOG, changelog_markdown


class UpdaterWindow(QMainWindow):
    """Cửa sổ ứng dụng cập nhật độc lập cho SolveX."""

    def __init__(self, current_ver: str = None):
        super().__init__()
        self.current_ver = current_ver or APP_VERSION
        self.remote_ver = None
        self.download_url = f"https://github.com/{TARGET_GITHUB_REPO}"
        self.changelog_text = ""

        self.check_worker = None
        self.download_worker = None
        self.build_worker = None

        self._init_ui()
        self.setStyleSheet(style.get_stylesheet("dark"))

        # Tự động bắt đầu kiểm tra phiên bản mới sau 300ms
        QTimer.singleShot(300, self.start_check_update)

    def _init_ui(self):
        self.setWindowTitle(f"SolveX Updater v{self.current_ver} — Trình Cập Nhật Độc Lập")
        self.setMinimumSize(780, 580)
        self.resize(800, 620)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # ---------------- 1. HEADER CARD ----------------
        header_card = QFrame()
        header_card.setStyleSheet(f"""
            QFrame {{
                background-color: {style.DARK_PALETTE['CARD']};
                border: 1px solid {style.DARK_PALETTE['BORDER']};
                border-radius: 12px;
            }}
        """)
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(16, 14, 16, 14)

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(4)

        app_title = QLabel("🔄 SolveX App Updater")
        app_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        app_title.setStyleSheet(f"color: {style.DARK_PALETTE['TEXT']}; border: none;")

        app_subtitle = QLabel("Trình quản lý & kiểm tra cập nhật độc lập dành cho SolveX")
        app_subtitle.setFont(QFont("Segoe UI", 10))
        app_subtitle.setStyleSheet(f"color: {style.DARK_PALETTE['MUTED']}; border: none;")

        title_vbox.addWidget(app_title)
        title_vbox.addWidget(app_subtitle)

        header_layout.addLayout(title_vbox)
        header_layout.addStretch()

        # Badges hiển thị phiên bản
        ver_box = QVBoxLayout()
        ver_box.setSpacing(4)
        ver_box.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.lbl_installed_ver = QLabel(f"Phiên bản hiện tại:  <b>v{self.current_ver}</b>")
        self.lbl_installed_ver.setStyleSheet(f"""
            QLabel {{
                background-color: #1e293b;
                color: #94a3b8;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 12px;
            }}
        """)

        self.lbl_remote_ver = QLabel("Phiên bản trên GitHub: <b>Đang kiểm tra...</b>")
        self.lbl_remote_ver.setStyleSheet(f"""
            QLabel {{
                background-color: #0f172a;
                color: #0ea5e9;
                border: 1px solid #0284c7;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 12px;
            }}
        """)

        ver_box.addWidget(self.lbl_installed_ver)
        ver_box.addWidget(self.lbl_remote_ver)
        header_layout.addLayout(ver_box)

        main_layout.addWidget(header_card)

        # ---------------- 2. STATUS CARD ----------------
        self.status_card = QFrame()
        self.status_card.setStyleSheet(f"""
            QFrame {{
                background-color: {style.DARK_PALETTE['PANEL']};
                border: 1px solid {style.DARK_PALETTE['BORDER']};
                border-radius: 10px;
            }}
        """)
        status_layout = QHBoxLayout(self.status_card)
        status_layout.setContentsMargins(14, 12, 14, 12)

        self.lbl_status_icon = QLabel("🔍")
        self.lbl_status_icon.setFont(QFont("Segoe UI", 14))
        self.lbl_status_icon.setStyleSheet("border: none;")

        self.lbl_status_text = QLabel("Đang kiểm tra phiên bản mới từ GitHub Repository (hbminh2508-design/SolveX)...")
        self.lbl_status_text.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.lbl_status_text.setStyleSheet(f"color: {style.DARK_PALETTE['TEXT']}; border: none;")

        status_layout.addWidget(self.lbl_status_icon)
        status_layout.addWidget(self.lbl_status_text, 1)
        main_layout.addWidget(self.status_card)

        # ---------------- 3. CHANGELOG & DETAILS AREA ----------------
        cl_box = QVBoxLayout()
        cl_box.setSpacing(6)

        cl_title = QLabel("📋 Nhật Ký Cập Nhật / Release Notes:")
        cl_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        cl_title.setStyleSheet(f"color: {style.DARK_PALETTE['TEAL']};")
        cl_box.addWidget(cl_title)

        self.browser = QTextBrowser()
        self.browser.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {style.DARK_PALETTE['PANEL']};
                border: 1px solid {style.DARK_PALETTE['BORDER']};
                border-radius: 10px;
                padding: 10px;
            }}
        """)
        self._show_initial_changelog()
        cl_box.addWidget(self.browser, 1)
        main_layout.addLayout(cl_box, 1)

        # ---------------- 4. PROGRESS BAR CARD ----------------
        self.progress_card = QFrame()
        self.progress_card.setStyleSheet(f"""
            QFrame {{
                background-color: {style.DARK_PALETTE['CARD']};
                border: 1px solid {style.DARK_PALETTE['BORDER']};
                border-radius: 10px;
            }}
        """)
        prog_layout = QVBoxLayout(self.progress_card)
        prog_layout.setContentsMargins(14, 12, 14, 12)
        prog_layout.setSpacing(6)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(18)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {style.DARK_PALETTE['INPUT_BG']};
                border: 1px solid {style.DARK_PALETTE['BORDER']};
                border-radius: 9px;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0ea5e9, stop:1 #3b82f6);
                border-radius: 8px;
            }}
        """)

        self.lbl_progress_info = QLabel("Sẵn sàng tiến trình.")
        self.lbl_progress_info.setStyleSheet(f"color: {style.DARK_PALETTE['MUTED']}; border: none; font-size: 11px;")

        prog_layout.addWidget(self.progress_bar)
        prog_layout.addWidget(self.lbl_progress_info)
        main_layout.addWidget(self.progress_card)

        # ---------------- 5. ACTION BUTTONS ROW ----------------
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_check = QPushButton("🔍 Kiểm Tra Lại")
        self.btn_check.setFixedHeight(38)
        self.btn_check.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_check.clicked.connect(self.start_check_update)

        self.btn_download = QPushButton("⬇ Tải Bản Cập Nhật (.exe)")
        self.btn_download.setFixedHeight(38)
        self.btn_download.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_download.setEnabled(False)
        self.btn_download.setStyleSheet(f"""
            QPushButton {{
                background-color: {style.DARK_PALETTE['TEAL']};
                color: #ffffff;
                font-weight: bold;
                border-radius: 8px;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background-color: #0284c7;
            }}
            QPushButton:disabled {{
                background-color: #334155;
                color: #64748b;
            }}
        """)
        self.btn_download.clicked.connect(self.start_download_update)

        self.btn_install = QPushButton("⚡ Đóng SolveX & Build Cài Bản Mới")
        self.btn_install.setFixedHeight(38)
        self.btn_install.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_install.setStyleSheet(f"""
            QPushButton {{
                background-color: #10b981;
                color: #ffffff;
                font-weight: bold;
                border-radius: 8px;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
        """)
        self.btn_install.clicked.connect(self.trigger_build_installer)

        self.btn_github = QPushButton("🌐 GitHub Repo")
        self.btn_github.setFixedHeight(38)
        self.btn_github.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_github.clicked.connect(lambda: webbrowser.open(f"https://github.com/{TARGET_GITHUB_REPO}"))

        self.btn_close = QPushButton("Thoát")
        self.btn_close.setFixedHeight(38)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(self.close)

        btn_layout.addWidget(self.btn_check)
        btn_layout.addWidget(self.btn_download)
        btn_layout.addWidget(self.btn_install)
        btn_layout.addWidget(self.btn_github)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_close)

        main_layout.addLayout(btn_layout)

    def _show_initial_changelog(self):
        md_content = changelog_markdown()
        html = wrap_html_page(render_markdown(md_content), "dark")
        self.browser.setHtml(html)

    # ---------------- LOGIC KIỂM TRA CẬP NHẬT ----------------
    def start_check_update(self):
        self.btn_check.setEnabled(False)
        self.lbl_status_icon.setText("🔄")
        self.lbl_status_text.setText("Đang kiểm tra phiên bản mới từ GitHub Repository...")
        self.lbl_remote_ver.setText("Phiên bản trên GitHub: <b>Đang kiểm tra...</b>")

        self.check_worker = CheckUpdateWorker()
        self.check_worker.up_to_date.connect(self._on_up_to_date)
        self.check_worker.update_available.connect(self._on_update_available)
        self.check_worker.failed.connect(self._on_check_failed)
        self.check_worker.start()

    def _on_up_to_date(self, ver: str):
        self.btn_check.setEnabled(True)
        self.btn_download.setEnabled(False)
        self.lbl_status_icon.setText("✅")
        self.lbl_status_text.setText(f"Bạn đang sử dụng phiên bản mới nhất (v{ver}). Không cần cập nhật.")
        self.lbl_remote_ver.setText(f"Phiên bản trên GitHub: <b>v{ver} (Mới nhất)</b>")
        self.lbl_remote_ver.setStyleSheet("""
            QLabel {
                background-color: #064e3b;
                color: #34d399;
                border: 1px solid #059669;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 12px;
            }
        """)

    def _on_update_available(self, remote_ver: str, changelog: str, download_url: str):
        self.remote_ver = remote_ver
        self.download_url = download_url
        self.changelog_text = changelog

        self.btn_check.setEnabled(True)
        self.btn_download.setEnabled(True)

        self.lbl_status_icon.setText("🎉")
        self.lbl_status_text.setText(f"Đã tìm thấy phiên bản mới: SolveX v{remote_ver}! Bấm nút bên dưới để tải về hoặc build mới.")
        self.lbl_remote_ver.setText(f"Phiên bản trên GitHub: <b>v{remote_ver} (Có bản mới!)</b>")
        self.lbl_remote_ver.setStyleSheet("""
            QLabel {
                background-color: #1e1b4b;
                color: #818cf8;
                border: 1px solid #4338ca;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 12px;
            }
        """)

        header = f"# 🚀 Nhật ký cập nhật SolveX v{remote_ver}\n\n{changelog}\n\n---\n\n"
        full_md = header + changelog_markdown()
        self.browser.setHtml(wrap_html_page(render_markdown(full_md), "dark"))

    def _on_check_failed(self, err: str):
        self.btn_check.setEnabled(True)
        self.lbl_status_icon.setText("❌")
        self.lbl_status_text.setText(f"Không thể kiểm tra cập nhật: {err}")
        self.lbl_remote_ver.setText("Phiên bản trên GitHub: <b>Lỗi kết nối</b>")

    # ---------------- LOGIC TẢI BẢN MỚI ----------------
    def start_download_update(self):
        if not self.remote_ver:
            return

        self.btn_download.setEnabled(False)
        self.progress_bar.setValue(0)
        self.lbl_progress_info.setText("Đang khởi tạo tiến trình tải về...")

        self.download_worker = DownloadUpdateWorker(self.download_url, f"SolveX_v{self.remote_ver}.exe")
        self.download_worker.progress_signal.connect(self._on_download_progress)
        self.download_worker.download_finished.connect(self._on_download_finished)
        self.download_worker.no_asset_found.connect(self._on_no_asset_found)
        self.download_worker.failed.connect(self._on_download_failed)
        self.download_worker.start()

    def _on_download_progress(self, percent: float, speed_str: str, eta_str: str, downloaded: int, total: int):
        self.progress_bar.setValue(int(percent))
        dl_mb = downloaded / (1024 * 1024)
        total_mb = total / (1024 * 1024) if total > 0 else 0
        info = f"Tiến độ: {percent:.1f}% | Tốc độ: {speed_str} | Thời gian còn lại: {eta_str} | Đã tải: {dl_mb:.1f} MB / {total_mb:.1f} MB"
        self.lbl_progress_info.setText(info)

    def _on_download_finished(self, saved_path: str):
        self.btn_download.setEnabled(True)
        self.progress_bar.setValue(100)
        self.lbl_progress_info.setText(f"✓ Đã tải thành công: {saved_path}")

        reply = QMessageBox.question(
            self,
            "Tải Hoàn Tất — SolveX Updater",
            f"Đã tải thành công file cài đặt phiên bản mới tại:\n{saved_path}\n\n"
            f"Bạn có muốn tự động đóng tất cả ứng dụng SolveX cũ và cài đặt/build bản mới ngay bây giờ không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.trigger_build_installer()

    def _on_no_asset_found(self, web_url: str):
        self.btn_download.setEnabled(True)
        reply = QMessageBox.question(
            self,
            "SolveX Updater — Thông Báo",
            "Phiên bản mới đã có trên GitHub! Hiện chưa có sẵn file .exe đóng gói trên Releases Assets.\n\n"
            "Bạn có muốn tự động đóng SolveX và tự tạo bản build .exe mới ngay tại máy không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.trigger_build_installer()
        else:
            webbrowser.open(web_url)

    def _on_download_failed(self, err: str):
        self.btn_download.setEnabled(True)
        self.lbl_progress_info.setText(f"❌ Lỗi tải về: {err}")
        QMessageBox.critical(self, "Lỗi Tải Cập Nhật", err)

    # ---------------- LOGIC CÀI ĐẶT & BUILD BẢN MỚI ----------------
    def trigger_build_installer(self):
        reply = QMessageBox.question(
            self,
            "Xác Nhận Cài Đặt & Build SolveX",
            "Tiến trình sẽ đóng tất cả cửa sổ SolveX đang chạy để giải phóng file hệ thống, "
            "sau đó khởi chạy kịch bản build.bat tự động đóng gói ứng dụng mới.\n\n"
            "Bạn có chắc chắn muốn tiến hành không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        # 1. Kill old SolveX.exe instances
        try:
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/F", "/IM", "SolveX.exe"], capture_output=True, text=True)
        except Exception:
            pass

        # 2. Trigger build.bat or BuildExeWorker
        project_dir = os.path.dirname(os.path.abspath(__file__))
        build_bat = os.path.join(project_dir, "build.bat")

        if os.path.exists(build_bat):
            try:
                subprocess.Popen(["cmd.exe", "/c", build_bat], cwd=project_dir, creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)
                self.lbl_progress_info.setText("✓ Đã kích hoạt build.bat độc lập. Đang đóng updater...")
                QTimer.singleShot(1500, self.close)
                return
            except Exception as exc:
                QMessageBox.warning(self, "Lỗi Kích Hoạt Batch", f"Không thể khởi chạy build.bat: {exc}")

        # Fallback build worker
        self.lbl_progress_info.setText("Đang tiến hành tự động build SolveX.exe...")
        self.build_worker = BuildExeWorker(project_dir)
        self.build_worker.progress.connect(lambda msg: self.lbl_progress_info.setText(msg))
        self.build_worker.succeeded.connect(self._on_build_success)
        self.build_worker.failed.connect(lambda err: QMessageBox.critical(self, "Lỗi Build", err))
        self.build_worker.start()

    def _on_build_success(self, exe_path: str):
        self.lbl_progress_info.setText(f"✓ Build thành công: {exe_path}")
        reply = QMessageBox.information(
            self,
            "Build Thành Công",
            f"Đã đóng gói thành công phiên bản SolveX mới tại:\n{exe_path}\n\nBấm OK để khởi chạy ứng dụng mới!",
        )
        try:
            subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path))
            self.close()
        except Exception as exc:
            QMessageBox.warning(self, "Khởi Chạy Ứng Dụng", f"Không thể khởi chạy SolveX.exe: {exc}")


def main():
    parser = argparse.ArgumentParser(description="SolveX Independent Updater Application")
    parser.add_argument("--version", type=str, default=APP_VERSION, help="Current installed SolveX version")
    args, _ = parser.parse_known_args()

    app = QApplication(sys.argv)
    app.setApplicationName("SolveX Updater")
    app.setApplicationDisplayName("SolveX Updater")

    window = UpdaterWindow(current_ver=args.version)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
