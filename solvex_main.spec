# -*- mode: python ; coding: utf-8 -*-
"""Cấu hình PyInstaller cho SolveX main app (dùng khi cài đặt cập nhật từ update.exe).
Chỉ đóng gói SolveX.exe, không đóng gói update.exe để tránh xung đột file lock.
"""

from PyInstaller.utils.hooks import collect_all, collect_submodules

datas = [("assets", "assets")]
binaries = []
hiddenimports = [
    "cffi",
    "_cffi_backend",
    "numpy",
    "PIL._tkinter_finder",
]

for package in ("soundcard", "mss", "markdown"):
    try:
        pkg_datas, pkg_binaries, pkg_hidden = collect_all(package)
        datas += pkg_datas
        binaries += pkg_binaries
        hiddenimports += pkg_hidden
    except Exception:
        pass

hiddenimports += collect_submodules("markdown.extensions")

a_main = Analysis(
    ["main.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "scipy",
        "pandas",
        "PyQt5",
        "PySide6",
        "unittest",
        "test",
    ],
    noarchive=False,
)

pyz_main = PYZ(a_main.pure)

exe_main = EXE(
    pyz_main,
    a_main.scripts,
    a_main.binaries,
    a_main.datas,
    [],
    name="SolveX",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/icon.ico",
)
