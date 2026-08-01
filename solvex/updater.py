"""Hệ thống kiểm tra cập nhật online từ GitHub Repository chính thức:
https://github.com/hbminh2508-design/SolveX.git
và tự động build file .exe bằng PyInstaller.
"""

import json
import os
import subprocess
import urllib.request
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from .version import APP_VERSION

TARGET_GITHUB_REPO = "hbminh2508-design/SolveX"
GITHUB_API_RELEASE = f"https://api.github.com/repos/{TARGET_GITHUB_REPO}/releases/latest"
GITHUB_API_COMMITS = f"https://api.github.com/repos/{TARGET_GITHUB_REPO}/commits/main"


class CheckUpdateWorker(QThread):
    """Worker kiểm tra phiên bản mới trên GitHub hbminh2508-design/SolveX."""

    up_to_date = pyqtSignal(str)
    update_available = pyqtSignal(str, str, str)  # (version, changelog, url)
    failed = pyqtSignal(str)

    def run(self):
        # 1. Thử kiểm tra qua Release API
        try:
            req = urllib.request.Request(
                GITHUB_API_RELEASE,
                headers={"User-Agent": "SolveX-App-Updater"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    remote_ver = data.get("tag_name", "").lstrip("v")
                    changelog = data.get("body", "Có phiên bản mới trên GitHub!")
                    download_url = data.get("html_url", f"https://github.com/{TARGET_GITHUB_REPO}")
                    if self._is_newer(remote_ver, APP_VERSION):
                        self.update_available.emit(remote_ver, changelog, download_url)
                        return
                    else:
                        self.up_to_date.emit(APP_VERSION)
                        return
        except Exception:
            pass

        # 2. Thử kiểm tra qua Commits API nếu chưa có Releases
        try:
            req = urllib.request.Request(
                GITHUB_API_COMMITS,
                headers={"User-Agent": "SolveX-App-Updater"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    commit_sha = data.get("sha", "")[:7]
                    commit_msg = data.get("commit", {}).get("message", "")
                    # Nếu kiểm tra thành công
                    self.up_to_date.emit(f"{APP_VERSION} (Commit: {commit_sha})")
                    return
        except Exception as exc:
            pass

        # Báo đã là phiên bản mới nhất nếu mạng lỗi hoặc repo chưa phát hành tag mới
        self.up_to_date.emit(APP_VERSION)

    def _is_newer(self, remote: str, current: str) -> bool:
        try:
            r_parts = [int(x) for x in remote.split(".")]
            c_parts = [int(x) for x in current.split(".")]
            return r_parts > c_parts
        except Exception:
            return False


class BuildExeWorker(QThread):
    """Worker tự động build file .exe bằng PyInstaller ở background thread."""

    progress = pyqtSignal(str)
    succeeded = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, project_dir: str, parent=None):
        super().__init__(parent)
        self.project_dir = project_dir

    def run(self):
        try:
            self.progress.emit("Bắt đầu tiến trình đóng gói .exe...")
            pyinstaller_exe = os.path.join(self.project_dir, ".venv", "Scripts", "pyinstaller.exe")
            spec_file = os.path.join(self.project_dir, "solvex.spec")

            if not os.path.exists(pyinstaller_exe):
                pyinstaller_exe = "pyinstaller"

            cmd = [pyinstaller_exe, "--noconfirm", "--clean", spec_file]
            self.progress.emit(f"Chạy lệnh: {' '.join(cmd)}")
            
            proc = subprocess.Popen(
                cmd,
                cwd=self.project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            for line in proc.stdout:
                line_str = line.strip()
                if line_str:
                    self.progress.emit(line_str)

            proc.wait()
            if proc.returncode == 0:
                exe_path = os.path.join(self.project_dir, "dist", "SolveX.exe")
                self.succeeded.emit(exe_path)
            else:
                self.failed.emit(f"Build thất bại với mã lỗi {proc.returncode}")
        except Exception as exc:
            self.failed.emit(str(exc))
