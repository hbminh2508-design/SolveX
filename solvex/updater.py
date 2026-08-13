"""Hệ thống kiểm tra cập nhật online & Tải bản mới trực tiếp cho SolveX từ GitHub Repository:
https://github.com/hbminh2508-design/SolveX.git
Hỗ trợ hiển thị % tiến độ, tốc độ tải và thời gian còn lại (ETA).
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from .version import APP_VERSION

TARGET_GITHUB_REPO = "hbminh2508-design/SolveX"
RAW_VERSION_URL = f"https://raw.githubusercontent.com/{TARGET_GITHUB_REPO}/main/solvex/version.py"
GITHUB_API_RELEASE = f"https://api.github.com/repos/{TARGET_GITHUB_REPO}/releases/latest"
GITHUB_API_COMMITS = f"https://api.github.com/repos/{TARGET_GITHUB_REPO}/commits/main"
GITHUB_API_TAGS = f"https://api.github.com/repos/{TARGET_GITHUB_REPO}/tags"

import urllib.parse

ALLOWED_HOSTS = {
    "github.com",
    "api.github.com",
    "raw.githubusercontent.com",
    "objects.githubusercontent.com",
    "codeload.github.com",
}


def validate_download_url(url: str) -> bool:
    """Xác thực bảo mật URL tải về: bắt buộc HTTPS & domain chính chủ GitHub."""
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme.lower() != "https":
            return False
        hostname = (parsed.hostname or "").lower()
        return hostname in ALLOWED_HOSTS or hostname.endswith(".githubusercontent.com") or hostname.endswith(".github.com")
    except Exception:
        return False


def verify_pe_executable(file_path: str) -> bool:
    """Xác thực định dạng binary an toàn: kiểm tra MZ header (0x4D 0x5A) của file .exe."""
    try:
        if not os.path.exists(file_path) or os.path.getsize(file_path) < 1024:
            return False
        with open(file_path, "rb") as f:
            header = f.read(2)
            return header == b"MZ"
    except Exception:
        return False


def launch_standalone_updater(current_version: str = None) -> bool:
    """Khởi chạy ứng dụng update.exe (hoặc python update.py) trong tiến trình riêng độc lập với SolveX."""
    if not current_version:
        current_version = APP_VERSION

    candidates = [
        os.getcwd(),
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        r"c:\Users\hoang\Downloads\SolveX-main\SolveX-main",
    ]
    project_dir = candidates[0]
    for p in candidates:
        if os.path.exists(os.path.join(p, "update.py")) or os.path.exists(os.path.join(p, "dist", "update.exe")):
            project_dir = p
            break

    updater_exe = os.path.join(project_dir, "dist", "update.exe")
    if not os.path.exists(updater_exe):
        updater_exe = os.path.join(project_dir, "update.exe")

    python_exe = os.path.join(project_dir, ".venv", "Scripts", "python.exe")
    update_py = os.path.join(project_dir, "update.py")

    cmd = None
    if os.path.exists(updater_exe):
        cmd = [updater_exe, "--version", current_version]
    elif os.path.exists(python_exe) and os.path.exists(update_py):
        cmd = [python_exe, update_py, "--version", current_version]
    elif os.path.exists(update_py):
        cmd = [sys.executable, update_py, "--version", current_version]

    if cmd:
        creationflags = subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        try:
            subprocess.Popen(cmd, cwd=project_dir, creationflags=creationflags)
            return True
        except Exception:
            pass
    return False


class CheckUpdateWorker(QThread):
    """Worker kiểm tra phiên bản mới trực tiếp từ GitHub hbminh2508-design/SolveX."""

    up_to_date = pyqtSignal(str)
    update_available = pyqtSignal(str, str, str)  # (version, changelog, url)
    failed = pyqtSignal(str)

    def run(self):
        remote_ver = None
        changelog = "Có phiên bản mới trên GitHub! Vui lòng tải về phiên bản mới nhất."
        download_url = f"https://github.com/{TARGET_GITHUB_REPO}"
        ts = int(time.time())

        # 1. Thử kiểm tra qua GitHub Tags API (lấy tag & commit SHA trực tiếp, không bị cdn cache)
        try:
            req = urllib.request.Request(
                f"{GITHUB_API_TAGS}?t={ts}",
                headers={
                    "User-Agent": "SolveX-App-Updater",
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache"
                },
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

        # 2. Tải raw file version.py từ GitHub main branch kèm cache busting timestamp
        if not remote_ver:
            try:
                req = urllib.request.Request(
                    f"{RAW_VERSION_URL}?t={ts}",
                    headers={
                        "User-Agent": "SolveX-App-Updater",
                        "Cache-Control": "no-cache, no-store, must-revalidate",
                        "Pragma": "no-cache"
                    },
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    if resp.status == 200:
                        text = resp.read().decode("utf-8")
                        match = re.search(r'APP_VERSION\s*=\s*["\']([^"\']+)["\']', text)
                        if match:
                            remote_ver = match.group(1)
            except Exception:
                pass

        # 3. Thử kiểm tra qua Releases API nếu chưa lấy được
        if not remote_ver:
            try:
                req = urllib.request.Request(
                    f"{GITHUB_API_RELEASE}?t={ts}",
                    headers={
                        "User-Agent": "SolveX-App-Updater",
                        "Cache-Control": "no-cache, no-store, must-revalidate",
                        "Pragma": "no-cache"
                    },
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


class DownloadUpdateWorker(QThread):
    """Worker tải file bản mới về máy tính với tiến độ %, tốc độ và thời gian còn lại (ETA)."""

    progress_signal = pyqtSignal(float, str, str, int, int)  # (percent, speed_str, eta_str, downloaded, total)
    download_finished = pyqtSignal(str)  # (saved_file_path)
    failed = pyqtSignal(str)
    no_asset_found = pyqtSignal(str)  # (web_url)

    def __init__(self, download_url: str, save_filename: str = "SolveX_Update.exe"):
        super().__init__()
        self.download_url = download_url
        self.save_filename = save_filename
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def _find_direct_exe_url(self) -> str:
        """Tự động kiểm tra GitHub Release Assets xem có file .exe khả dụng không."""
        try:
            req = urllib.request.Request(GITHUB_API_RELEASE, headers={"User-Agent": "SolveX-App-Updater"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    assets = data.get("assets", [])
                    for asset in assets:
                        asset_url = asset.get("browser_download_url", "")
                        if asset_url.endswith(".exe"):
                            return asset_url
        except Exception:
            pass
        return None

    def run(self):
        try:
            target_dir = Path.home() / "Downloads"
            target_dir.mkdir(parents=True, exist_ok=True)
            save_path = target_dir / self.save_filename

            # 1. Kiểm tra URL download trực tiếp từ Releases Assets
            direct_url = self._find_direct_exe_url()
            
            if not direct_url:
                # Nếu chưa có Release asset .exe trên GitHub Releases:
                # Kiểm tra nếu file local dist/SolveX.exe đã tồn tại
                local_exe = Path(r"c:\Users\hoang\Downloads\SolveX-main\SolveX-main\dist\SolveX.exe")
                if local_exe.exists():
                    shutil.copy2(local_exe, save_path)
                    self.download_finished.emit(str(save_path))
                    return

                # Nếu không có file binary trực tiếp, chuyển hướng mở trang GitHub Repo mượt mà
                self.no_asset_found.emit(f"https://github.com/{TARGET_GITHUB_REPO}")
                return

            req = urllib.request.Request(direct_url, headers={"User-Agent": "SolveX-App-Updater"})
            resp = urllib.request.urlopen(req, timeout=15)

            total_size = int(resp.headers.get("content-length", 0))
            downloaded = 0
            block_size = 64 * 1024

            start_time = time.time()
            last_time = start_time
            last_downloaded = 0

            with open(save_path, "wb") as f:
                while True:
                    if self._is_cancelled:
                        resp.close()
                        self.failed.emit("Đã hủy tiến trình tải cập nhật.")
                        return

                    chunk = resp.read(block_size)
                    if not chunk:
                        break

                    f.write(chunk)
                    downloaded += len(chunk)
                    curr_time = time.time()
                    interval = curr_time - last_time

                    if interval >= 0.3 or downloaded == total_size:
                        speed = (downloaded - last_downloaded) / interval if interval > 0 else 0
                        speed_mb = speed / (1024 * 1024)
                        speed_str = f"{speed_mb:.2f} MB/s" if speed_mb >= 1.0 else f"{speed / 1024:.0f} KB/s"

                        if total_size > 0:
                            percent = (downloaded / total_size) * 100.0
                            remaining_bytes = total_size - downloaded
                            eta_sec = remaining_bytes / speed if speed > 0 else 0
                            m, s = divmod(int(eta_sec), 60)
                            eta_str = f"{m:02d}:{s:02d}"
                        else:
                            percent = 50.0
                            eta_str = "Đang tính toán..."

                        self.progress_signal.emit(percent, speed_str, eta_str, downloaded, total_size)
                        last_time = curr_time
                        last_downloaded = downloaded

            resp.close()
            self.download_finished.emit(str(save_path))
        except Exception as exc:
            self.failed.emit(f"Lỗi khi tải file cập nhật: {exc}")


class BuildExeWorker(QThread):
    """Worker tự động build file .exe bằng PyInstaller ở background thread."""

    progress = pyqtSignal(str)
    succeeded = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, project_dir: str, parent=None):
        super().__init__(parent)
        self.project_dir = project_dir

    def _kill_running_solvex_processes(self):
        try:
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/F", "/IM", "SolveX.exe"], capture_output=True, text=True)
        except Exception:
            pass

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
            self.progress.emit("Đang tự động dừng tiến trình SolveX cũ để giải phóng file...")
            self._kill_running_solvex_processes()

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
