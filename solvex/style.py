"""Bảng màu và stylesheet dùng chung — Thiết kế 2026 WinUI 3 (Floating Sidebar & Menu Bar).
Góc bo 12-14px mềm mại, Floating Sidebar rời mép, Fluent Dark & Light Mode.
"""

FONT_STACK = '"Segoe UI Variable Display", "Segoe UI Variable Text", "Segoe UI", sans-serif'

DARK_PALETTE = {
    "INK": "#18181b",
    "PANEL": "#242427",
    "PANEL_LIGHT": "#2d2d32",
    "BORDER": "#38383e",
    "BORDER_FOCUS": "#f59e0b",
    "TEXT": "#ffffff",
    "MUTED": "#a1a1aa",
    "AMBER": "#f59e0b",
    "TEAL": "#10b981",
    "RED": "#ef4444",
}

LIGHT_PALETTE = {
    "INK": "#f4f4f5",
    "PANEL": "#ffffff",
    "PANEL_LIGHT": "#f8fafc",
    "BORDER": "#e4e4e7",
    "BORDER_FOCUS": "#d97706",
    "TEXT": "#09090b",
    "MUTED": "#71717a",
    "AMBER": "#d97706",
    "TEAL": "#059669",
    "RED": "#dc2626",
}

INK = DARK_PALETTE["INK"]
PANEL = DARK_PALETTE["PANEL"]
PANEL_LIGHT = DARK_PALETTE["PANEL_LIGHT"]
BORDER = DARK_PALETTE["BORDER"]
TEXT = DARK_PALETTE["TEXT"]
MUTED = DARK_PALETTE["MUTED"]
AMBER = DARK_PALETTE["AMBER"]
TEAL = DARK_PALETTE["TEAL"]
RED = DARK_PALETTE["RED"]


def get_palette(theme: str = "dark") -> dict:
    return LIGHT_PALETTE if theme == "light" else DARK_PALETTE


def get_stylesheet(theme: str = "dark") -> str:
    p = get_palette(theme)
    hover_bg = "#e2e8f0" if theme == "light" else "#383838"
    pressed_bg = "#cbd5e1" if theme == "light" else "#222222"
    disabled_fg = "#94a3b8" if theme == "light" else "#666666"

    return f"""
QWidget {{
    background: {p['INK']};
    color: {p['TEXT']};
    font-family: {FONT_STACK};
    font-size: 13px;
}}

/* Native Menu Bar */
QMenuBar {{
    background: {p['INK']};
    color: {p['TEXT']};
    border-bottom: 1px solid {p['BORDER']};
    padding: 2px 6px;
}}
QMenuBar::item {{
    background: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}}
QMenuBar::item:selected {{
    background: {p['PANEL_LIGHT']};
    color: {p['AMBER']};
}}

QMenu {{
    background: {p['PANEL']};
    color: {p['TEXT']};
    border: 1px solid {p['BORDER']};
    border-radius: 8px;
    padding: 4px;
}}
QMenu::item {{
    padding: 6px 20px 6px 12px;
    border-radius: 4px;
}}
QMenu::item:selected {{
    background: {p['PANEL_LIGHT']};
    color: {p['AMBER']};
}}

/* Floating Sidebar 2026 */
QFrame#NavSidebar {{
    background: {p['PANEL']};
    border: 1px solid {p['BORDER']};
    border-radius: 14px;
    margin: 10px 4px 10px 10px;
}}

QPushButton#NavBtn {{
    background: transparent;
    border: none;
    border-radius: 8px;
    padding: 11px 14px;
    text-align: left;
    color: {p['MUTED']};
    font-size: 13px;
    font-weight: 500;
}}
QPushButton#NavBtn:hover {{
    background: {p['PANEL_LIGHT']};
    color: {p['TEXT']};
}}
QPushButton#NavBtn:checked {{
    background: {"#f1f5f9" if theme == "light" else "#323238"};
    color: {p['AMBER']};
    font-weight: 600;
    border-left: 3.5px solid {p['AMBER']};
}}

/* Header Toolbar */
QFrame#HeaderBar {{
    background: {p['PANEL']};
    border-bottom: 1px solid {p['BORDER']};
}}

/* Panels and Cards */
QFrame#Panel, QFrame#Card {{
    background: {p['PANEL']};
    border: 1px solid {p['BORDER']};
    border-radius: 12px;
}}

QLabel#Brand {{
    font-size: 20px;
    font-weight: 700;
    color: {p['TEXT']};
}}

QLabel#Tagline {{
    color: {p['MUTED']};
    font-size: 11px;
}}

QLabel#SectionLabel {{
    color: {p['MUTED']};
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
}}

QLabel#Preview {{
    background: {p['INK']};
    border: 1px dashed {p['BORDER']};
    border-radius: 8px;
    color: {p['MUTED']};
}}

/* Inputs & Form Controls */
QLineEdit, QPlainTextEdit, QComboBox, QSpinBox, QTextEdit {{
    background: {p['PANEL_LIGHT']};
    border: 1px solid {p['BORDER']};
    border-radius: 8px;
    padding: 7px 10px;
    color: {p['TEXT']};
    selection-background-color: {p['AMBER']};
    selection-color: #ffffff;
}}

QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QTextEdit:focus {{
    border: 1px solid {p['AMBER']};
}}

QComboBox::drop-down {{ border: none; width: 22px; }}
QComboBox QAbstractItemView {{
    background: {p['PANEL_LIGHT']};
    border: 1px solid {p['BORDER']};
    selection-background-color: {p['AMBER']};
    selection-color: #ffffff;
}}

/* Buttons */
QPushButton {{
    background: {p['PANEL_LIGHT']};
    border: 1px solid {p['BORDER']};
    border-radius: 8px;
    padding: 8px 16px;
    color: {p['TEXT']};
    font-weight: 500;
}}
QPushButton:hover {{ background: {hover_bg}; }}
QPushButton:pressed {{ background: {pressed_bg}; }}
QPushButton:disabled {{ color: {disabled_fg}; border-color: {p['BORDER']}; }}

QPushButton#HeaderQuickBtn {{
    background: {p['PANEL_LIGHT']};
    border: 1px solid {p['BORDER']};
    border-radius: 6px;
    padding: 5px 10px;
    font-size: 12px;
    font-weight: 600;
}}
QPushButton#HeaderQuickBtn:hover {{ background: {hover_bg}; }}

QPushButton#PrimaryBtn {{
    background: {p['AMBER']};
    color: #ffffff;
    border: none;
    font-weight: 600;
}}
QPushButton#PrimaryBtn:hover {{ background: #f59e0b; }}

QPushButton#Solve {{
    background: {p['AMBER']};
    color: #ffffff;
    border: none;
    font-size: 14px;
    font-weight: 700;
    padding: 12px 16px;
    border-radius: 10px;
}}
QPushButton#Solve:hover {{ background: #f59e0b; }}

QPushButton#Listen {{
    background: {p['TEAL']};
    color: #ffffff;
    border: none;
    font-size: 14px;
    font-weight: 700;
    padding: 12px 16px;
    border-radius: 10px;
}}
QPushButton#Listen:hover {{ background: #10b981; }}

QPushButton#Listening {{
    background: {p['RED']};
    color: #ffffff;
    border: none;
    font-size: 14px;
    font-weight: 700;
    padding: 12px 16px;
    border-radius: 10px;
}}
QPushButton#Listening:hover {{ background: #ef4444; }}

QPushButton#Send {{
    background: {p['AMBER']};
    color: #ffffff;
    border: none;
    font-weight: 700;
    border-radius: 8px;
}}

QCheckBox, QRadioButton {{ spacing: 8px; color: {p['TEXT']}; }}
QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px; height: 16px;
    border: 1px solid {p['BORDER']};
    border-radius: 4px;
    background: {p['PANEL_LIGHT']};
}}
QRadioButton::indicator {{ border-radius: 8px; }}
QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
    background: {p['AMBER']};
    border: 1px solid {p['AMBER']};
}}

QProgressBar {{
    background: {p['PANEL_LIGHT']};
    border: 1px solid {p['BORDER']};
    border-radius: 4px;
    height: 7px;
    text-align: center;
}}
QProgressBar::chunk {{ background: {p['AMBER']}; border-radius: 3px; }}

QTextBrowser#Chat {{
    background: {p['PANEL']};
    border: 1px solid {p['BORDER']};
    border-radius: 12px;
    padding: 10px;
}}

QListWidget {{
    background: {p['PANEL']};
    border: 1px solid {p['BORDER']};
    border-radius: 10px;
    padding: 4px;
}}
QListWidget::item {{
    padding: 8px 10px;
    border-radius: 6px;
    margin-bottom: 2px;
}}
QListWidget::item:hover {{ background: {p['PANEL_LIGHT']}; }}
QListWidget::item:selected {{ background: {p['AMBER']}; color: #ffffff; font-weight: 600; }}

QScrollBar:vertical {{
    background: transparent; width: 8px; margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: {"#cbd5e1" if theme == "light" else "#444444"}; border-radius: 4px; min-height: 28px;
}}
QScrollBar::handle:vertical:hover {{ background: {"#94a3b8" if theme == "light" else "#666666"}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: none; }}

QStatusBar {{ color: {p['MUTED']}; background: {p['INK']}; border-top: 1px solid {p['BORDER']}; }}
QSplitter::handle {{ background: transparent; width: 6px; }}
"""


def get_compact_stylesheet(theme: str = "dark") -> str:
    p = get_palette(theme)
    return f"""
QWidget#CompactTitleBar {{
    background: transparent;
    border: none;
}}
QLabel#CompactTitle {{
    color: {p['MUTED']};
    font-size: 12px;
    font-weight: 600;
}}
QPushButton#CaptionBtn, QPushButton#CaptionBtnClose {{
    background: transparent;
    border: none;
    border-radius: 6px;
    color: {p['TEXT']};
    font-size: 13px;
    padding: 0px;
}}
QPushButton#CaptionBtn:hover {{ background: {"#e2e8f0" if theme == "light" else "#383838"}; }}
QPushButton#CaptionBtnClose:hover {{ background: {p['RED']}; color: #ffffff; }}

QPushButton#ToolbarBtn {{
    background: {p['PANEL_LIGHT']};
    border: 1px solid {p['BORDER']};
    border-radius: 8px;
    padding: 8px 12px;
    color: {p['TEXT']};
    font-weight: 600;
}}
QPushButton#ToolbarBtn:hover {{ background: {"#e2e8f0" if theme == "light" else "#3a3a3a"}; }}
"""


def get_busy_stylesheet(theme: str = "dark") -> str:
    p = get_palette(theme)
    return f"""
QLabel#BusyLabel {{
    color: {p['TEXT']};
    font-size: 12px;
    font-weight: 600;
}}
QProgressBar {{
    background: {p['PANEL_LIGHT']};
    border: 1px solid {p['BORDER']};
    border-radius: 4px;
    height: 7px;
}}
QProgressBar::chunk {{ background: {p['AMBER']}; border-radius: 3px; }}
"""


def get_chat_css(theme: str = "dark") -> str:
    p = get_palette(theme)
    return f"""
body {{ color: {p['TEXT']}; font-family: {FONT_STACK}; font-size: 13px; line-height: 1.5; }}
pre {{ background: {p['INK']}; border: 1px solid {p['BORDER']}; border-radius: 6px;
      padding: 10px; font-family: Consolas, "DejaVu Sans Mono", monospace; }}
code {{ background: {p['INK']}; padding: 2px 4px; border-radius: 4px; font-family: Consolas, monospace; }}
table {{ border-collapse: collapse; width: 100%; margin: 8px 0; }}
th, td {{ border: 1px solid {p['BORDER']}; padding: 6px 10px; text-align: left; }}
th {{ background: {p['PANEL_LIGHT']}; color: {p['AMBER']}; }}
h1, h2, h3 {{ color: {p['AMBER']}; margin-top: 12px; margin-bottom: 6px; }}
a {{ color: {p['TEAL']}; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
.question-img {{ border: 1px solid {p['BORDER']}; border-radius: 8px; margin: 8px 0; max-width: 100%; }}
"""

STYLESHEET = get_stylesheet("dark")
COMPACT_STYLESHEET = get_compact_stylesheet("dark")
BUSY_STYLESHEET = get_busy_stylesheet("dark")
CHAT_CSS = get_chat_css("dark")
