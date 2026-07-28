# -*- mode: python ; coding: utf-8 -*-
"""Cấu hình PyInstaller cho SolveX.

Chạy:  pyinstaller --noconfirm solvex.spec
Kết quả: dist/SolveX.exe (một file duy nhất)
"""

from PyInstaller.utils.hooks import collect_all, collect_submodules

datas = []
binaries = []
hiddenimports = [
    "cffi",
    "_cffi_backend",
    "numpy",
    "PIL._tkinter_finder",
]

# soundcard nạp thư viện native qua cffi nên PyInstaller không tự thấy được.
for package in ("soundcard", "mss", "markdown"):
    try:
        pkg_datas, pkg_binaries, pkg_hidden = collect_all(package)
        datas += pkg_datas
        binaries += pkg_binaries
        hiddenimports += pkg_hidden
    except Exception:
        pass

hiddenimports += collect_submodules("markdown.extensions")

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "scipy", "pandas", "PyQt5", "PySide6"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="SolveX",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,          # đổi thành True nếu cần xem log lỗi khi chạy
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,              # thay bằng "icon.ico" nếu bạn có icon
)
