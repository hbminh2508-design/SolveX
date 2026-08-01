"""Bật hiệu ứng Mica + Acrylic Glassmorphism cho cửa sổ Windows 11 qua DWM API.
"""

import ctypes
import sys

_DWMWA_USE_IMMERSIVE_DARK_MODE = 20
_DWMWA_SYSTEMBACKDROP_TYPE = 38

# DWM Backdrop Types
_DWMSBT_AUTO = 0
_DWMSBT_NONE = 1
_DWMSBT_MAINWINDOW = 2  # Mica
_DWMSBT_TRANSIENTWINDOW = 3  # Acrylic Glass
_DWMSBT_TABBEDWINDOW = 4     # Mica Alt


def apply_mica(widget, dark_mode: bool = True, glass_mode: bool = True) -> None:
    """Thử bật Acrylic/Mica Glassmorphism + tiêu đề tối cho cửa sổ đã có winId."""
    if sys.platform != "win32":
        return
    try:
        hwnd = int(widget.winId())
        dwmapi = ctypes.windll.dwmapi

        dark = ctypes.c_int(1 if dark_mode else 0)
        dwmapi.DwmSetWindowAttribute(
            hwnd, _DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(dark), ctypes.sizeof(dark)
        )

        backdrop_type = _DWMSBT_TRANSIENTWINDOW if glass_mode else _DWMSBT_MAINWINDOW
        backdrop = ctypes.c_int(backdrop_type)
        dwmapi.DwmSetWindowAttribute(
            hwnd, _DWMWA_SYSTEMBACKDROP_TYPE, ctypes.byref(backdrop), ctypes.sizeof(backdrop)
        )
    except Exception:
        pass
