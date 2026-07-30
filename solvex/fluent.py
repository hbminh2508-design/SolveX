"""Bật hiệu ứng Mica + tiêu đề tối của Windows 11 cho cửa sổ, nếu có thể.

Chỉ có tác dụng trên Windows 11 (build 22621+) qua DWM API. Ở các hệ điều
hành khác (hoặc Windows cũ hơn) hàm này không làm gì — giao diện vẫn dùng
theme Fluent vẽ bằng stylesheet như bình thường.
"""

import ctypes
import sys

_DWMWA_USE_IMMERSIVE_DARK_MODE = 20
_DWMWA_SYSTEMBACKDROP_TYPE = 38
_DWMSBT_MAINWINDOW = 2  # Mica


def apply_mica(widget) -> None:
    """Thử bật Mica backdrop + tiêu đề tối cho cửa sổ đã có handle (winId)."""
    if sys.platform != "win32":
        return
    try:
        hwnd = int(widget.winId())
        dwmapi = ctypes.windll.dwmapi

        dark = ctypes.c_int(1)
        dwmapi.DwmSetWindowAttribute(
            hwnd, _DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(dark), ctypes.sizeof(dark)
        )

        backdrop = ctypes.c_int(_DWMSBT_MAINWINDOW)
        dwmapi.DwmSetWindowAttribute(
            hwnd, _DWMWA_SYSTEMBACKDROP_TYPE, ctypes.byref(backdrop), ctypes.sizeof(backdrop)
        )
    except Exception:
        pass  # build Windows cũ / không có DWM — bỏ qua, dùng theme vẽ tay
