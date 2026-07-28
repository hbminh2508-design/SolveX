"""Bảng màu và stylesheet dùng chung."""

INK = "#14161d"
PANEL = "#1c1f28"
PANEL_LIGHT = "#242833"
BORDER = "#333846"
TEXT = "#e6e8ef"
MUTED = "#8a90a3"
AMBER = "#f0a63c"
TEAL = "#3fbfb0"
RED = "#e5566d"

STYLESHEET = f"""
QWidget {{
    background: {INK};
    color: {TEXT};
    font-family: "Segoe UI", "Inter", "Noto Sans", sans-serif;
    font-size: 13px;
}}

QFrame#Panel {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 10px;
}}

QLabel#Brand {{
    font-size: 19px;
    font-weight: 700;
    letter-spacing: 0.5px;
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
    border-radius: 7px;
    padding: 6px 9px;
    selection-background-color: {AMBER};
    selection-color: {INK};
}}

QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QTextEdit:focus {{
    border: 1px solid {AMBER};
}}

QComboBox::drop-down {{ border: none; width: 18px; }}
QComboBox QAbstractItemView {{
    background: {PANEL_LIGHT};
    border: 1px solid {BORDER};
    selection-background-color: {AMBER};
    selection-color: {INK};
}}

QPushButton {{
    background: {PANEL_LIGHT};
    border: 1px solid {BORDER};
    border-radius: 7px;
    padding: 7px 14px;
    color: {TEXT};
}}
QPushButton:hover {{ background: #2c3140; }}
QPushButton:pressed {{ background: #191c24; }}
QPushButton:disabled {{ color: #565b6b; border-color: #262a35; }}

QPushButton#Solve {{
    background: {AMBER};
    color: #191204;
    border: none;
    font-size: 14px;
    font-weight: 700;
    padding: 12px 14px;
}}
QPushButton#Solve:hover {{ background: #ffb84f; }}
QPushButton#Solve:disabled {{ background: #4a3d22; color: #8d7a4e; }}

QPushButton#Listen {{
    background: {TEAL};
    color: #04211e;
    border: none;
    font-size: 14px;
    font-weight: 700;
    padding: 12px 14px;
}}
QPushButton#Listen:hover {{ background: #55d8c8; }}
QPushButton#Listen:disabled {{ background: #22463f; color: #4e857c; }}

QPushButton#Listening {{
    background: {RED};
    color: #2a0710;
    border: none;
    font-size: 14px;
    font-weight: 700;
    padding: 12px 14px;
}}
QPushButton#Listening:hover {{ background: #ff6b81; }}

QPushButton#Send {{
    background: {AMBER};
    color: #191204;
    border: none;
    font-weight: 700;
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
QProgressBar::chunk {{ background: {TEAL}; border-radius: 3px; }}

QTextBrowser#Chat {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 6px;
}}

QScrollBar:vertical {{
    background: transparent; width: 9px; margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: #3b4152; border-radius: 4px; min-height: 28px;
}}
QScrollBar::handle:vertical:hover {{ background: #4c5468; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: none; }}

QStatusBar {{ color: {MUTED}; }}
QSplitter::handle {{ background: transparent; width: 8px; }}
"""

# CSS cho nội dung HTML bên trong khung chat
CHAT_CSS = f"""
body {{ color: {TEXT}; font-family: "Segoe UI","Noto Sans",sans-serif; font-size: 13px; }}
pre {{ background: {INK}; border: 1px solid {BORDER}; border-radius: 6px;
      padding: 8px; font-family: Consolas, "DejaVu Sans Mono", monospace; }}
code {{ background: {INK}; font-family: Consolas, "DejaVu Sans Mono", monospace; }}
table {{ border-collapse: collapse; }}
th, td {{ border: 1px solid {BORDER}; padding: 5px 9px; }}
th {{ background: {PANEL_LIGHT}; }}
h1, h2, h3 {{ color: {AMBER}; }}
a {{ color: {TEAL}; }}
"""
