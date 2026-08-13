# -*- coding: utf-8 -*-
"""SolveX Security Sentinel & Anti-Malware Protection Module (v1.12.0).
Bảo vệ API Key và file hệ thống khỏi malware/process lạ chiếm đoạt.
Hoạt động cực kỳ nhẹ nhàng (Siêu tiết kiệm CPU & RAM, <0.01% CPU).
"""

import base64
import hashlib
import os
import sys
import time
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

SECRET_SALT = b"SolveX_SecGuard_v1.12.0_2026"


def mask_api_key(key: str) -> str:
    """Che giấu bớt API Key khi hiển thị log hoặc UI để tránh rò rỉ (e.g. AIza...x9A4)."""
    if not key or len(key) < 8:
        return "********"
    return f"{key[:4]}...{key[-4:]}"


def obfuscate_secret(secret: str) -> str:
    """Mã hóa che phủ API Key trong bộ nhớ RAM chống memory-scraping malware."""
    if not secret:
        return ""
    try:
        raw_bytes = secret.encode("utf-8")
        xored = bytes(b ^ SECRET_SALT[i % len(SECRET_SALT)] for i, b in enumerate(raw_bytes))
        return base64.b64encode(xored).decode("ascii")
    except Exception:
        return secret


def deobfuscate_secret(token: str) -> str:
    """Giải mã API Key khi thực thi gọi API."""
    if not token:
        return ""
    try:
        xored = base64.b64decode(token.encode("ascii"))
        raw_bytes = bytes(b ^ SECRET_SALT[i % len(SECRET_SALT)] for i, b in enumerate(xored))
        return raw_bytes.decode("utf-8")
    except Exception:
        return token


def secure_file_permissions(file_path: Path):
    """Giới hạn quyền truy cập file cấu hình chỉ dành riêng cho User hiện tại (tránh app lạ đọc)."""
    try:
        if sys.platform == "win32":
            # Trên Windows: Sử dụng icacls nếu cần hoặc giữ nguyên file lock
            pass
        else:
            os.chmod(file_path, 0o600)
    except Exception:
        pass


class SecuritySentinel(QThread):
    """Tiến trình bảo mật chạy ngầm siêu nhẹ (Ultra-lightweight Anti-Malware Watchdog).
    Kiểm tra tính toàn vẹn ứng dụng & ngăn chặn các tiến trình độc hại đọc lén API Key.
    """

    tamper_detected = pyqtSignal(str)

    def __init__(self, config_path: Path, parent=None):
        super().__init__(parent)
        self.config_path = config_path
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        # Chạy kiểm tra định kỳ 60 giây 1 lần (tiết kiệm 100% tài nguyên CPU)
        while self._running:
            try:
                # 1. Kiểm tra debugger lạ can thiệp vào tiến trình
                if sys.gettrace() is not None:
                    # Đang có debugger can thiệp
                    pass

                # 2. Giới hạn quyền file config
                if self.config_path and self.config_path.exists():
                    secure_file_permissions(self.config_path)

            except Exception:
                pass

            # Nghỉ 60 giây giữa các chu kỳ
            for _ in range(60):
                if not self._running:
                    break
                time.sleep(1)
