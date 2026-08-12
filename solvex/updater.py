"""Hệ thống kiểm tra cập nhật online từ GitHub Repository chính thức:
https://github.com/hbminh2508-design/SolveX.git
Hỗ trợ kiểm tra theo định dạng phiên bản X.y.z.t... (Số phiên bản + Mã build commit).
"""

import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from .version import APP_VERSION

TARGET_GITHUB_REPO = "hbminh2508-design/SolveX"
RAW_VERSION_URL = f"https://raw.githubusercontent.com/{TARGET_GITHUB_REPO}/main/solvex/version.py"
GITHUB_API_RELEASE = f"https://api.github.com/repos/{TARGET_GITHUB_REPO}/releases/latest"
GITHUB_API_COMMITS = f"https://api.github.com/repos/{TARGET_GITHUB_REPO}/commits/main"
GITHUB_API_TAGS = f"https://api.github.com/repos/{TARGET_GITHUB_REPO}/tags"


class CheckUpdateWorker(QThread):
    """Worker kiểm tra phiên bản mới trực tiếp từ GitHub hbminh2508-design/SolveX."""

    up_to_date = pyqtSignal(str)
    update_available = pyqtSignal(str, str, str)  # (version, changelog, url)
    failed = pyqtSignal(str)

    def run(self):
        remote_ver = None
        changelog = "Có phiên bản mới trên GitHub! Vui lòng truy cập repository để tải về phiên bản mới nhất."
        download_url = f"https://github.com/{TARGET_GITHUB_REPO}"

        # 1. Tải raw file version.py từ GitHub main branch
        try:
            req = urllib.request.Request(
                RAW_VERSION_URL,
                headers={"User-Agent": "SolveX-App-Updater"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    text = resp.read().decode("utf-8")
                    match = re.search(r'APP_VERSION\s*=\s*["\']([^"\']+)["\']', text)
                    if match:
                        remote_ver = match.group(1)
        except Exception:
            pass

        # 2. Thử kiểm tra qua Tags API
        if not remote_ver:
            try:
                req = urllib.request.Request(
                    GITHUB_API_TAGS,
                    headers={"User-Agent": "SolveX-App-Updater"},
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    if resp.status == 200:
                        tags_data = json.loads(resp.read().decode("utf-8"))
                        if tags_data and isinstance(tags_data, list):
                            tag_name = tags_data[0].get("name", "").lstrip("v")
                            commit_sha = tags_data[0].get("commit", {}).get("sha", "")[:7]
                            remote_ver = f"{tag_name}.{commit_sha}" if commit_sha else tag_name
            except Exception:
                pass

        # 3. Thử kiểm tra qua Releases API nếu chưa lấy được
        if not remote_ver:
            try:
                req = urllib.request.Request(
                    GITHUB_API_RELEASE,
                    headers={"User-Agent": "SolveX-App-Updater"},
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        remote_ver = data.get("tag_name", "").lstrip("v")
                        if data.get("body"):
                            changelog = data.get("body")
                        if data.get("html_url"):
                            download_url = data.get("html_url")
            except Exception:
                pass

        # 4. So sánh phiên bản remote và local
        if remote_ver:
            if self._is_newer(remote_ver, APP_VERSION):
                self.update_available.emit(remote_ver, changelog, download_url)
                return
            else:
                self.up_to_date.emit(APP_VERSION)
                return

        # 5. Fallback check qua Commits API
        try:
            req = urllib.request.Request(
                GITHUB_API_COMMITS,
                headers={"User-Agent": "SolveX-App-Updater"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    commit_sha = data.get("sha", "")[:7]
                    self.up_to_date.emit(f"{APP_VERSION} (Commit: {commit_sha})")
                    return
        except Exception:
            pass

        self.up_to_date.emit(APP_VERSION)

    def _parse_version_components(self, ver_str: str):
        """Tách chuỗi X.y.z.t thành (thành_phần_số, mã_build)."""
        clean_str = ver_str.lstrip("v").strip()
        parts = clean_str.split(".")
        numbers = []
        build_code = ""
        for p in parts:
            if p.isdigit():
                numbers.append(int(p))
            else:
                build_code = p
        return tuple(numbers), build_code

    def _is_newer(self, remote: str, current: str) -> bool:
        try:
            r_num, r_build = self._parse_version_components(remote)
            c_num, c_build = self._parse_version_components(current)

            # Cân bằng độ dài tuple số
            max_len = max(len(r_num), len(c_num))
            r_padded = r_num + (0,) * (max_len - len(r_num))
            c_padded = c_num + (0,) * (max_len - len(c_num))

            if r_padded > c_padded:
                return True
            elif r_padded == c_padded:
                if r_build and c_build and r_build != c_build:
                    return True
            return False
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

    def _find_real_project_dir() -> str:
        candidates = [
            os.getcwd(),
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            r"c:\Users\hoang\Downloads\SolveX-main\SolveX-main",
        ]
        for path in candidates:
            if os.path.exists(os.path.join(path, "solvex.spec")):
                return path
            if os.path.exists(os.path.join(path, "main.py")):
                return path
        return candidates[0]

    def run(self):
        try:
            real_dir = BuildExeWorker._find_real_project_dir()
            self.progress.emit(f"Xác định thư mục dự án: {real_dir}")
            
            spec_file = os.path.join(real_dir, "solvex.spec")
            if not os.path.exists(spec_file):
                self.failed.emit(f"Không tìm thấy file {spec_file} trong thư mục dự án!")
                return

            python_exe = os.path.join(real_dir, ".venv", "Scripts", "python.exe")
            pyinstaller_exe = os.path.join(real_dir, ".venv", "Scripts", "pyinstaller.exe")

            if os.path.exists(pyinstaller_exe):
                cmd = [pyinstaller_exe, "--noconfirm", "--clean", spec_file]
            elif os.path.exists(python_exe):
                cmd = [python_exe, "-m", "PyInstaller", "--noconfirm", "--clean", spec_file]
            else:
                sys_pyinstaller = shutil.which("pyinstaller")
                if sys_pyinstaller:
                    cmd = [sys_pyinstaller, "--noconfirm", "--clean", spec_file]
                else:
                    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", spec_file]

            self.progress.emit(f"Bắt đầu tiến trình đóng gói: {' '.join(cmd)}")

            proc = subprocess.Popen(
                cmd,
                cwd=real_dir,
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
                exe_path = os.path.join(real_dir, "dist", "SolveX.exe")
                self.succeeded.emit(exe_path)
            else:
                self.failed.emit(f"Build thất bại với mã lỗi {proc.returncode}")
        except FileNotFoundError:
            self.failed.emit("Không tìm thấy PyInstaller trong môi trường hệ thống! Vui lòng cài đặt qua `pip install pyinstaller`.")
        except Exception as exc:
            self.failed.emit(str(exc))
