"""Bảng màu và stylesheet dùng chung — theo ngôn ngữ Fluent Design / WinUI3
(Windows 11 dark mode): góc bo 6-8px, nền dạng Mica, chữ Segoe UI Variable."""

INK = "#202020"          # nền cửa sổ kiểu Mica (Windows 11 dark app background)
PANEL = "#2c2c2c"        # nền thẻ/card (CardBackgroundFillColorDefault)
PANEL_LIGHT = "#333333"  # nền ô nhập liệu
BORDER = "#3d3d3d"       # viền mảnh kiểu Fluent (CardStrokeColorDefault)
TEXT = "#f3f3f3"         # TextFillColorPrimary
MUTED = "#9d9d9d"        # TextFillColorSecondary
AMBER = "#f0a63c"        # màu thương hiệu SolveX (đồng bộ với logo)
TEAL = "#3fbfb0"
RED = "#ff6b81"

FONT_STACK = '"Segoe UI Variable Text", "Segoe UI", "Inter", "Noto Sans", sans-serif'

STYLESHEET = f"""
QWidget {{
    background: {INK};
    color: {TEXT};
    font-family: {FONT_STACK};
    font-size: 13px;
}}

QFrame#Panel {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}

QLabel#Brand {{
    font-size: 19px;
    font-weight: 600;
    letter-spacing: 0.2px;
    color: {TEXT};
}}

QLabel#Tagline {{
    color: {MUTED};
    font-size: 11px;
}}

QLabel#SectionLabel {{
    color: {MUTED};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.8px;
    padding-top: 4px;
}}

QLabel#Preview {{
    background: {INK};
    border: 1px dashed {BORDER};
    border-radius: 8px;
    color: {MUTED};
}}

QLineEdit, QPlainTextEdit, QComboBox, QSpinBox, QTextEdit {{
    background: {PANEL_LIGHT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 9px;
    selection-background-color: {AMBER};
    selection-color: #191204;
}}

QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QTextEdit:focus {{
    border: 1px solid {AMBER};
}}

QComboBox::drop-down {{ border: none; width: 18px; }}
QComboBox QAbstractItemView {{
    background: {PANEL_LIGHT};
    border: 1px solid {BORDER};
    selection-background-color: {AMBER};
    selection-color: #191204;
}}

QPushButton {{
    background: {PANEL_LIGHT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 7px 14px;
    color: {TEXT};
}}
QPushButton:hover {{ background: #3a3a3a; }}
QPushButton:pressed {{ background: #262626; }}
QPushButton:disabled {{ color: #6b6b6b; border-color: #2c2c2c; }}

QPushButton#Solve {{
    background: {AMBER};
    color: #191204;
    border: none;
    font-size: 14px;
    font-weight: 600;
    padding: 12px 14px;
    border-radius: 8px;
}}
QPushButton#Solve:hover {{ background: #ffb84f; }}
QPushButton#Solve:disabled {{ background: #4a3d22; color: #8d7a4e; }}

QPushButton#Listen {{
    background: {TEAL};
    color: #04211e;
    border: none;
    font-size: 14px;
    font-weight: 600;
    padding: 12px 14px;
    border-radius: 8px;
}}
QPushButton#Listen:hover {{ background: #55d8c8; }}
QPushButton#Listen:disabled {{ background: #22463f; color: #4e857c; }}

QPushButton#Listening {{
    background: {RED};
    color: #2a0710;
    border: none;
    font-size: 14px;
    font-weight: 600;
    padding: 12px 14px;
    border-radius: 8px;
}}
QPushButton#Listening:hover {{ background: #ff8b9c; }}

QPushButton#Send {{
    background: {AMBER};
    color: #191204;
    border: none;
    font-weight: 600;
    border-radius: 6px;
}}
QPushButton#Send:hover {{ background: #ffb84f; }}
QPushButton#Send:disabled {{ background: #4a3d22; color: #8d7a4e; }}

QCheckBox {{ spacing: 7px; }}
QCheckBox::indicator {{
    width: 15px; height: 15px;
    border: 1px solid {BORDER};
    border-radius: 4px;
    background: {PANEL_LIGHT};
}}
QCheckBox::indicator:checked {{
    background: {AMBER};
    border: 1px solid {AMBER};
}}

QProgressBar {{
    background: {PANEL_LIGHT};
    border: 1px solid {BORDER};
    border-radius: 4px;
    height: 7px;
    text-align: center;
}}
QProgressBar::chunk {{ background: {AMBER}; border-radius: 3px; }}

QTextBrowser#Chat {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 6px;
}}

QScrollBar:vertical {{
    background: transparent; width: 9px; margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: #4a4a4a; border-radius: 4px; min-height: 28px;
}}
QScrollBar::handle:vertical:hover {{ background: #5a5a5a; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: none; }}

QStatusBar {{ color: {MUTED}; }}
QSplitter::handle {{ background: transparent; width: 8px; }}
"""

# Cửa sổ nhỏ (bảng điều khiển nổi) — khung Fluent riêng + thanh tiêu đề tự vẽ.
# Nền thẻ bo góc của CompactRoot/BusyRoot do paintEvent() trong ui.py tự vẽ
# (QWidget thường không tự sơn nền theo QSS khi dùng WA_TranslucentBackground),
# nên ở đây chỉ còn style cho các control con.
COMPACT_STYLESHEET = f"""
QWidget#CompactTitleBar {{
    background: transparent;
    border: none;
}}
QLabel#CompactTitle {{
    color: {MUTED};
    font-size: 12px;
    font-weight: 600;
}}
QPushButton#CaptionBtn, QPushButton#CaptionBtnClose {{
    background: transparent;
    border: none;
    border-radius: 6px;
    color: {TEXT};
    font-size: 13px;
    padding: 0px;
}}
QPushButton#CaptionBtn:hover {{ background: #3f3f3f; }}
QPushButton#CaptionBtn:pressed {{ background: #4a4a4a; }}
QPushButton#CaptionBtnClose:hover {{ background: {RED}; color: #2a0710; }}
QPushButton#CaptionBtnClose:pressed {{ background: #d64b60; color: #2a0710; }}

QPushButton#ToolbarBtn {{
    background: {PANEL_LIGHT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 12px;
    color: {TEXT};
    font-weight: 600;
}}
QPushButton#ToolbarBtn:hover {{ background: #3a3a3a; }}
QPushButton#ToolbarBtn:pressed {{ background: #262626; }}
QPushButton#ToolbarBtn:disabled {{ color: #6b6b6b; border-color: #2c2c2c; }}
QPushButton#ToolbarBtnListening {{
    background: {RED};
    border: 1px solid {RED};
    border-radius: 8px;
    padding: 8px 12px;
    color: #2a0710;
    font-weight: 700;
}}
"""

# Ô báo "đang giải…" nổi góc màn hình khi ở chế độ khay hệ thống.
# Nền thẻ bo góc của BusyRoot do paintEvent() tự vẽ, xem ghi chú ở trên.
BUSY_STYLESHEET = f"""
QLabel#BusyLabel {{
    color: {TEXT};
    font-size: 12px;
    font-weight: 600;
}}
QProgressBar {{
    background: {PANEL_LIGHT};
    border: 1px solid {BORDER};
    border-radius: 4px;
    height: 7px;
}}
QProgressBar::chunk {{ background: {AMBER}; border-radius: 3px; }}
"""

# CSS cho nội dung HTML bên trong khung chat
CHAT_CSS = f"""
body {{ color: {TEXT}; font-family: {FONT_STACK}; font-size: 13px; }}
pre {{ background: {INK}; border: 1px solid {BORDER}; border-radius: 6px;
      padding: 8px; font-family: Consolas, "DejaVu Sans Mono", monospace; }}
code {{ background: {INK}; font-family: Consolas, "DejaVu Sans Mono", monospace; }}
table {{ border-collapse: collapse; }}
th, td {{ border: 1px solid {BORDER}; padding: 5px 9px; }}
th {{ background: {PANEL_LIGHT}; }}
h1, h2, h3 {{ color: {AMBER}; }}
a {{ color: {TEAL}; }}
"""
