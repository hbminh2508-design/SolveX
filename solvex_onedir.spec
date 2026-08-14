# -*- mode: python ; coding: utf-8 -*-
"""Cấu hình PyInstaller cho SolveX phiên bản Non-Portable (Thư mục cài đặt / Onedir).
Giúp cập nhật tức thì (0 compilation) bằng cách ghi đè file trực tiếp khi tải bản cập nhật về.
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

a_onedir = Analysis(
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

pyz_onedir = PYZ(a_onedir.pure)

exe_onedir = EXE(
    pyz_onedir,
    a_onedir.scripts,
    [],
    exclude_binaries=True,
    name="SolveX",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/icon.ico",
)

coll = COLLECT(
    exe_onedir,
    a_onedir.binaries,
    a_onedir.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="SolveX",
)
