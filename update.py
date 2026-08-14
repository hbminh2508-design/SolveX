# -*- coding: utf-8 -*-
"""SolveX Updater — Ứng dụng kiểm tra và quản lý cập nhật độc lập cho SolveX (v1.11.0).
Chạy tách biệt hoàn toàn khỏi tiến trình SolveX.exe chính.
Tích hợp bảo mật nâng cao (Anti-Malware Pinning & Signature Check).
"""

import argparse
import html
import os
import shutil
import subprocess
import sys
import time
import urllib.parse
import webbrowser

from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
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
    CheckUpdateWorker,
    DownloadUpdateWorker,
    validate_download_url,
    verify_pe_executable,
)
from solvex.version import APP_VERSION, CHANGELOG, changelog_markdown


def find_project_dir() -> str:
    """Tìm thư mục gốc dự án chứa file solvex_main.spec hoặc solvex.spec.
    Tự động xử lý chính xác khi chạy từ file .py hoặc khi đã đóng gói thành update.exe (PyInstaller).
    """
    candidates = []

    # 1. Thư mục chứa file thực thi (khi chạy dưới dạng update.exe)
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        candidates.append(exe_dir)
        candidates.append(os.path.dirname(exe_dir))  # Nếu update.exe nằm trong dist/

    # 2. Thư mục làm việc hiện tại (cwd)
    candidates.append(os.getcwd())

    # 3. Thư mục của script
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        candidates.append(script_dir)
        candidates.append(os.path.dirname(script_dir))
    except Exception:
        pass

    # Duyệt qua các thư mục ứng viên để tìm thư mục gốc dự án
    for c in candidates:
        if not c or not os.path.exists(c):
            continue
        if (
            os.path.exists(os.path.join(c, "solvex_main.spec"))
            or os.path.exists(os.path.join(c, "solvex.spec"))
            or os.path.exists(os.path.join(c, "main.py"))
        ):
            return c

    return candidates[0] if candidates else os.getcwd()


class InstallMainWorker(QThread):
    """Worker đóng gói & cài đặt ứng dụng chính SolveX.exe tốc độ siêu nhanh (Fast Flash Update)."""

    progress_signal = pyqtSignal(int, str)  # (percent 0-100, log_line)
    succeeded = pyqtSignal(str)              # (exe_path)
    failed = pyqtSignal(str)

    def __init__(self, project_dir: str, downloaded_exe_path: str = None, parent=None):
        super().__init__(parent)
        self.project_dir = project_dir
        self.downloaded_exe_path = downloaded_exe_path

    def run(self):
        try:
            self.progress_signal.emit(5, "Đang khởi động tiến trình cài đặt siêu tốc (Flash Update)...")

            # 1. Dừng an toàn tất cả các tiến trình SolveX.exe cũ
            self.progress_signal.emit(10, "Đang dừng tiến trình SolveX.exe cũ để giải phóng file hệ thống...")
            if sys.platform == "win32":
                try:
                    subprocess.run(["taskkill", "/F", "/IM", "SolveX.exe"], capture_output=True, text=True)
                except Exception:
                    pass
            time.sleep(0.5)

            target_dir = os.path.join(self.project_dir, "dist")
            os.makedirs(target_dir, exist_ok=True)
            target_exe = os.path.join(target_dir, "SolveX.exe")

            # Xóa cache cũ trong build/solvex_main để bắt buộc PyInstaller đóng gói đúng phiên bản mới nhất từ mã nguồn
            build_cache_dir = os.path.join(self.project_dir, "build", "solvex_main")
            if os.path.exists(build_cache_dir):
                try:
                    shutil.rmtree(build_cache_dir, ignore_errors=True)
                except Exception:
                    pass

            # 2. CHẾ ĐỘ CẬP NHẬT SIÊU TỐC (1-SECOND FLASH UPDATE CHO CẢ PORTABLE & NON-PORTABLE):
            # Nếu đã có sẵn file .exe đóng gói sẵn hoặc file .zip gói ứng dụng, thay thế/giải nén trực tiếp trong 1 giây!
            if self.downloaded_exe_path and os.path.exists(self.downloaded_exe_path):
                # 2A. File nén Zip chứa toàn bộ thư mục Non-Portable
                if self.downloaded_exe_path.lower().endswith(".zip"):
                    import zipfile
                    self.progress_signal.emit(40, f"⚡ Đang giải nén gói cập nhật Non-Portable: {self.downloaded_exe_path}")
                    with zipfile.ZipFile(self.downloaded_exe_path, "r") as zf:
                        zf.extractall(target_dir)
                    self.progress_signal.emit(100, f"✓ Cập nhật Non-Portable hoàn tất trong 1 giây! Thư mục ứng dụng: {target_dir}")
                    self.succeeded.emit(target_exe)
                    return

                # 2B. File .exe thực thi Portable hoặc Installer
                elif verify_pe_executable(self.downloaded_exe_path):
                    self.progress_signal.emit(50, f"⚡ Áp dụng Cập Nhật Siêu Tốc 1 giây từ file thực thi: {self.downloaded_exe_path}")
                    shutil.copy2(self.downloaded_exe_path, target_exe)

                    # Copy đồng thời sang thư mục nơi update.exe đang chạy (nếu khác dist)
                    if getattr(sys, "frozen", False):
                        running_dir = os.path.dirname(sys.executable)
                        if running_dir and running_dir != target_dir:
                            dest_exe = os.path.join(running_dir, "SolveX.exe")
                            try:
                                shutil.copy2(self.downloaded_exe_path, dest_exe)
                            except Exception:
                                pass

                    self.progress_signal.emit(100, f"✓ Cài đặt hoàn tất trong 1 giây! File thực thi sẵn sàng: {target_exe}")
                    self.succeeded.emit(target_exe)
                    return

            # 3. CHẾ ĐỘ BIÊN DỊCH BỘ NHỚ ĐỆM TỐC ĐỘ CAO (FAST CACHED COMPILATION):
            # Kiểm tra file spec riêng chỉ build SolveX.exe (solvex_main.spec)
            spec_file = os.path.join(self.project_dir, "solvex_main.spec")
            if not os.path.exists(spec_file):
                spec_file = os.path.join(self.project_dir, "solvex.spec")

            if not os.path.exists(spec_file):
                self.failed.emit(f"Không tìm thấy file cấu hình {spec_file}!")
                return

            # Tìm PyInstaller trong môi trường ảo .venv hoặc hệ thống
            python_exe = os.path.join(self.project_dir, ".venv", "Scripts", "python.exe")
            pyinstaller_exe = os.path.join(self.project_dir, ".venv", "Scripts", "pyinstaller.exe")

            if os.path.exists(pyinstaller_exe):
                cmd = [pyinstaller_exe, "--noconfirm", spec_file]
            elif os.path.exists(python_exe):
                cmd = [python_exe, "-m", "PyInstaller", "--noconfirm", spec_file]
            else:
                sys_pyinstaller = shutil.which("pyinstaller")
                if sys_pyinstaller:
                    cmd = [sys_pyinstaller, "--noconfirm", spec_file]
                else:
                    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", spec_file]

            self.progress_signal.emit(20, f"⚡ Biên dịch phiên bản mới siêu tốc: {' '.join(cmd)}")

            # Khởi chạy PyInstaller
            proc = subprocess.Popen(
                cmd,
                cwd=self.project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            current_pct = 20
            for line in proc.stdout:
                line_str = line.strip()
                if not line_str:
                    continue

                if "Analyzing" in line_str:
                    current_pct = min(current_pct + 3, 55)
                elif "Building PYZ" in line_str:
                    current_pct = 70
                elif "Building PKG" in line_str:
                    current_pct = 85
                elif "Building EXE" in line_str or "Fixing EXE headers" in line_str:
                    current_pct = 95

                self.progress_signal.emit(current_pct, line_str)

            proc.wait()

            if proc.returncode == 0:
                # Copy đồng thời sang thư mục nơi update.exe đang chạy (nếu update.exe đặt ở vị trí khác)
                if getattr(sys, "frozen", False):
                    running_dir = os.path.dirname(sys.executable)
                    if running_dir and running_dir != target_dir and os.path.exists(target_exe):
                        dest_exe = os.path.join(running_dir, "SolveX.exe")
                        try:
                            shutil.copy2(target_exe, dest_exe)
                        except Exception:
                            pass

                # 4. Xác thực an toàn PE header (MZ) cho file SolveX.exe mới build
                if verify_pe_executable(target_exe):
                    self.progress_signal.emit(100, f"✓ Cài đặt thành công phiên bản mới! File thực thi sẵn sàng: {target_exe}")
                    self.succeeded.emit(target_exe)
                else:
                    self.failed.emit(f"File thực thi {target_exe} không vượt qua kiểm tra an toàn binary PE (MZ Header)!")
            else:
                self.failed.emit(f"Tiến trình cài đặt & build thất bại với mã lỗi {proc.returncode}")

        except Exception as exc:
            self.failed.emit(f"Lỗi cài đặt: {exc}")


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
        self.install_worker = None

        self._init_ui()
        self.setStyleSheet(style.get_stylesheet("dark"))

        # Tự động kiểm tra phiên bản mới sau 300ms
        QTimer.singleShot(300, self.start_check_update)

    def _init_ui(self):
        self.setWindowTitle("SolveX Updater — Trình Cập Nhật Độc Lập")
        self.setMinimumSize(800, 640)
        self.resize(840, 680)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

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

        app_subtitle = QLabel("Trình quản lý & kiểm tra cập nhật độc lập bảo mật dành cho SolveX")
        app_subtitle.setFont(QFont("Segoe UI", 10))
        app_subtitle.setStyleSheet(f"color: {style.DARK_PALETTE['MUTED']}; border: none;")

        title_vbox.addWidget(app_title)
        title_vbox.addWidget(app_subtitle)

        header_layout.addLayout(title_vbox)
        header_layout.addStretch()

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
        status_layout.setContentsMargins(14, 10, 14, 10)

        self.lbl_status_icon = QLabel("🔍")
        self.lbl_status_icon.setFont(QFont("Segoe UI", 14))
        self.lbl_status_icon.setStyleSheet("border: none;")

        self.lbl_status_text = QLabel("Đang kiểm tra phiên bản mới từ GitHub Repository chính chủ (hbminh2508-design/SolveX)...")
        self.lbl_status_text.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        self.lbl_status_text.setStyleSheet(f"color: {style.DARK_PALETTE['TEXT']}; border: none;")

        status_layout.addWidget(self.lbl_status_icon)
        status_layout.addWidget(self.lbl_status_text, 1)
        main_layout.addWidget(self.status_card)

        # ---------------- 3. CHANGELOG & DETAILS AREA ----------------
        cl_box = QVBoxLayout()
        cl_box.setSpacing(4)

        cl_title = QLabel("📋 Nhật Ký Cập Nhật / Release Notes:")
        cl_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
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

        # ---------------- 4. PROGRESS CARDS (DOWNLOAD & INSTALL) ----------------
        # 4A. Download Progress Card
        self.download_card = QFrame()
        self.download_card.setStyleSheet(f"""
            QFrame {{
                background-color: {style.DARK_PALETTE['CARD']};
                border: 1px solid {style.DARK_PALETTE['BORDER']};
                border-radius: 10px;
            }}
        """)
        dl_layout = QVBoxLayout(self.download_card)
        dl_layout.setContentsMargins(14, 10, 14, 10)
        dl_layout.setSpacing(4)

        dl_hdr = QLabel("📥 Tiến Độ Tải Cập Nhật:")
        dl_hdr.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        dl_hdr.setStyleSheet(f"color: {style.DARK_PALETTE['TEAL']}; border: none;")
        dl_layout.addWidget(dl_hdr)

        self.download_progress_bar = QProgressBar()
        self.download_progress_bar.setRange(0, 100)
        self.download_progress_bar.setValue(0)
        self.download_progress_bar.setFixedHeight(16)
        self.download_progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {style.DARK_PALETTE['INPUT_BG']};
                border: 1px solid {style.DARK_PALETTE['BORDER']};
                border-radius: 8px;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
                font-size: 10px;
            }}
            QProgressBar::chunk {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0ea5e9, stop:1 #3b82f6);
                border-radius: 7px;
            }}
        """)

        self.lbl_download_info = QLabel("Sẵn sàng tải.")
        self.lbl_download_info.setStyleSheet(f"color: {style.DARK_PALETTE['MUTED']}; border: none; font-size: 11px;")

        dl_layout.addWidget(self.download_progress_bar)
        dl_layout.addWidget(self.lbl_download_info)
        main_layout.addWidget(self.download_card)

        # 4B. Install/Build Progress Card (CHUYÊN TRÁCH TIẾN TRÌNH CÀI ĐẶT SOLVEX.EXE)
        self.install_card = QFrame()
        self.install_card.setStyleSheet(f"""
            QFrame {{
                background-color: {style.DARK_PALETTE['CARD']};
                border: 1px solid {style.DARK_PALETTE['BORDER']};
                border-radius: 10px;
            }}
        """)
        inst_layout = QVBoxLayout(self.install_card)
        inst_layout.setContentsMargins(14, 10, 14, 10)
        inst_layout.setSpacing(4)

        inst_hdr = QLabel("🛠 Tiến Độ Cài Đặt & Đóng Gói SolveX.exe:")
        inst_hdr.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        inst_hdr.setStyleSheet("color: #10b981; border: none;")
        inst_layout.addWidget(inst_hdr)

        self.install_progress_bar = QProgressBar()
        self.install_progress_bar.setRange(0, 100)
        self.install_progress_bar.setValue(0)
        self.install_progress_bar.setFixedHeight(16)
        self.install_progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {style.DARK_PALETTE['INPUT_BG']};
                border: 1px solid {style.DARK_PALETTE['BORDER']};
                border-radius: 8px;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
                font-size: 10px;
            }}
            QProgressBar::chunk {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #059669);
                border-radius: 7px;
            }}
        """)

        self.lbl_install_info = QLabel("Chưa cài đặt.")
        self.lbl_install_info.setStyleSheet(f"color: {style.DARK_PALETTE['MUTED']}; border: none; font-size: 11px;")

        inst_layout.addWidget(self.install_progress_bar)
        inst_layout.addWidget(self.lbl_install_info)
        main_layout.addWidget(self.install_card)

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

        self.btn_install = QPushButton("⚡ Đóng SolveX & Cài Đặt Bản Mới")
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
            QPushButton:disabled {{
                background-color: #334155;
                color: #64748b;
            }}
        """)
        self.btn_install.clicked.connect(self.trigger_install_app)

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
        html_text = wrap_html_page(render_markdown(md_content), "dark")
        self.browser.setHtml(html_text)

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
        self.lbl_status_text.setText(f"Đã tìm thấy phiên bản mới: SolveX v{remote_ver}! Bấm nút bên dưới để tải về hoặc cài đặt.")
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

    # ---------------- LOGIC TẢI BẢN MỚI (BẢO MẬT HTTPS & PINNING) ----------------
    def start_download_update(self):
        if not self.remote_ver:
            return

        # Kiểm tra bảo mật URL tải về
        if not validate_download_url(self.download_url):
            QMessageBox.critical(self, "Cảnh Báo Bảo Mật", "URL tải về không thuộc domain chính chủ của GitHub Repository (hbminh2508-design/SolveX)! Tiến trình bị hủy bỏ vì lý do an toàn.")
            return

        self.btn_download.setEnabled(False)
        self.download_progress_bar.setValue(0)
        self.lbl_download_info.setText("Đang khởi tạo tiến trình tải về bảo mật...")

        self.download_worker = DownloadUpdateWorker(self.download_url, f"SolveX_v{self.remote_ver}.exe")
        self.download_worker.progress_signal.connect(self._on_download_progress)
        self.download_worker.download_finished.connect(self._on_download_finished)
        self.download_worker.no_asset_found.connect(self._on_no_asset_found)
        self.download_worker.failed.connect(self._on_download_failed)
        self.download_worker.start()

    def _on_download_progress(self, percent: float, speed_str: str, eta_str: str, downloaded: int, total: int):
        self.download_progress_bar.setValue(int(percent))
        dl_mb = downloaded / (1024 * 1024)
        total_mb = total / (1024 * 1024) if total > 0 else 0
        info = f"Tiến độ tải: {percent:.1f}% | Tốc độ: {speed_str} | Còn lại: {eta_str} | Đã tải: {dl_mb:.1f} MB / {total_mb:.1f} MB"
        self.lbl_download_info.setText(info)

    def _on_download_finished(self, saved_path: str):
        self.downloaded_exe_path = saved_path
        self.btn_download.setEnabled(True)
        self.download_progress_bar.setValue(100)
        self.lbl_download_info.setText(f"✓ Đã tải thành công file an toàn: {saved_path}")

        reply = QMessageBox.question(
            self,
            "Tải Hoàn Tất — SolveX Updater",
            f"Đã tải thành công file cài đặt phiên bản mới tại:\n{saved_path}\n\n"
            f"Bạn có muốn tự động đóng tiến trình SolveX cũ và tiến hành cài đặt siêu tốc ngay bây giờ không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.trigger_install_app()

    def _on_no_asset_found(self, web_url: str):
        self.btn_download.setEnabled(True)
        reply = QMessageBox.question(
            self,
            "SolveX Updater — Thông Báo",
            "Phiên bản mới đã có trên GitHub! Hiện chưa có sẵn file .exe đóng gói sẵn trên Releases Assets.\n\n"
            "Bạn có muốn tự động tiến hành cài đặt & biên dịch phiên bản SolveX.exe mới ngay tại máy không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.trigger_install_app()
        else:
            webbrowser.open(web_url)

    def _on_download_failed(self, err: str):
        self.btn_download.setEnabled(True)
        self.lbl_download_info.setText(f"❌ Lỗi tải về: {err}")
        QMessageBox.critical(self, "Lỗi Tải Cập Nhật", err)

    # ---------------- LOGIC CÀI ĐẶT & BUILD CHỈ SOLVEX.EXE (CÓ THANH TIẾN TRÌNH CÀI ĐẶT TRỰC QUAN) ----------------
    def trigger_install_app(self):
        reply = QMessageBox.question(
            self,
            "Xác Nhận Cài Đặt SolveX",
            "Tiến trình sẽ đóng tất cả cửa sổ SolveX đang chạy để giải phóng file hệ thống, "
            "sau đó tiến hành đóng gói & cài đặt phiên bản SolveX.exe mới.\n\n"
            "Lưu ý: Chỉ cài đặt/build ứng dụng chính SolveX.exe (không đụng tới update.exe để đảm bảo an toàn tuyệt đối và tránh lỗi khóa file).\n\n"
            "Bạn có chắc chắn muốn tiến hành không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.btn_install.setEnabled(False)
        self.install_progress_bar.setValue(0)
        self.lbl_install_info.setText("Đang khởi tạo tiến trình cài đặt SolveX.exe...")

        project_dir = find_project_dir()
        downloaded_exe = getattr(self, "downloaded_exe_path", None)

        self.install_worker = InstallMainWorker(project_dir, downloaded_exe)
        self.install_worker.progress_signal.connect(self._on_install_progress)
        self.install_worker.succeeded.connect(self._on_install_success)
        self.install_worker.failed.connect(self._on_install_failed)
        self.install_worker.start()

    def _on_install_progress(self, percent: int, log_line: str):
        self.install_progress_bar.setValue(percent)
        self.lbl_install_info.setText(log_line)

    def _on_install_success(self, exe_path: str):
        self.btn_install.setEnabled(True)
        self.install_progress_bar.setValue(100)
        self.lbl_install_info.setText(f"✓ Cài đặt thành công: {exe_path}")

        reply = QMessageBox.information(
            self,
            "Cài Đặt Hoàn Tất",
            f"Đã hoàn thành đóng gói & cài đặt phiên bản SolveX mới tại:\n{exe_path}\n\nBấm OK để khởi chạy ứng dụng SolveX mới!",
        )
        try:
            subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path))
            self.close()
        except Exception as exc:
            QMessageBox.warning(self, "Khởi Chạy Ứng Dụng", f"Không thể tự khởi chạy SolveX.exe: {exc}")

    def _on_install_failed(self, err: str):
        self.btn_install.setEnabled(True)
        self.lbl_install_info.setText(f"❌ Lỗi cài đặt: {err}")
        QMessageBox.critical(self, "Lỗi Cài Đặt", err)


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
