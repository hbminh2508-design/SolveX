"""Bảng màu và stylesheet Glassmorphism — WinUI 3 & Windows 11 Acrylic (Dark & Light Mode).
Góc bo 16px siêu mềm mại, kính mờ bán trong suốt (frosted glass), đường viền phản quang mảnh.
"""

FONT_STACK = '"Segoe UI Variable Display", "Segoe UI Variable Text", "Segoe UI", sans-serif'

DARK_PALETTE = {
    "INK": "#141417",
    "PANEL": "rgba(32, 32, 38, 0.78)",
    "PANEL_SOLID": "#202025",
    "PANEL_LIGHT": "rgba(45, 45, 52, 0.75)",
    "BORDER": "rgba(255, 255, 255, 0.12)",
    "BORDER_FOCUS": "#f59e0b",
    "TEXT": "#ffffff",
    "MUTED": "#a1a1aa",
    "AMBER": "#f59e0b",
    "TEAL": "#10b981",
    "RED": "#ef4444",
}

LIGHT_PALETTE = {
    "INK": "#f4f4f6",
    "PANEL": "rgba(255, 255, 255, 0.82)",
    "PANEL_SOLID": "#ffffff",
    "PANEL_LIGHT": "rgba(241, 245, 249, 0.85)",
    "BORDER": "rgba(0, 0, 0, 0.08)",
    "BORDER_FOCUS": "#d97706",
    "TEXT": "#09090b",
    "MUTED": "#64748b",
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
    hover_bg = "rgba(255, 255, 255, 0.08)" if theme == "dark" else "rgba(0, 0, 0, 0.05)"
    pressed_bg = "rgba(255, 255, 255, 0.14)" if theme == "dark" else "rgba(0, 0, 0, 0.10)"
    disabled_fg = "#94a3b8" if theme == "light" else "#555555"

    return f"""
QWidget {{
    background: {p['INK']};
    color: {p['TEXT']};
    font-family: {FONT_STACK};
    font-size: 13px;
}}

/* Native Menu Bar Glass */
QMenuBar {{
    background: {p['INK']};
    color: {p['TEXT']};
    border-bottom: 1px solid {p['BORDER']};
    padding: 2px 6px;
}}
QMenuBar::item {{
    background: transparent;
    padding: 6px 12px;
    border-radius: 6px;
}}
QMenuBar::item:selected {{
    background: {p['PANEL_LIGHT']};
    color: {p['AMBER']};
}}

QMenu {{
    background: {p['PANEL_SOLID']};
    color: {p['TEXT']};
    border: 1px solid {p['BORDER']};
    border-radius: 12px;
    padding: 6px;
}}
QMenu::item {{
    padding: 7px 20px 7px 12px;
    border-radius: 6px;
}}
QMenu::item:selected {{
    background: {p['PANEL_LIGHT']};
    color: {p['AMBER']};
}}

/* Floating Sidebar Glassmorphism */
QFrame#NavSidebar {{
    background: {p['PANEL']};
    border: 1px solid {p['BORDER']};
    border-radius: 16px;
    margin: 12px 6px 12px 12px;
}}

QPushButton#NavBtn {{
    background: transparent;
    border: none;
    border-radius: 10px;
    padding: 11px 14px;
    text-align: left;
    color: {p['MUTED']};
    font-size: 13px;
    font-weight: 500;
}}
QPushButton#NavBtn:hover {{
    background: {hover_bg};
    color: {p['TEXT']};
}}
QPushButton#NavBtn:checked {{
    background: {"rgba(217, 119, 6, 0.15)" if theme == "light" else "rgba(245, 158, 11, 0.18)"};
    color: {p['AMBER']};
    font-weight: 600;
    border-left: 3.5px solid {p['AMBER']};
}}

/* Header Toolbar Glass */
QFrame#HeaderBar {{
    background: {p['PANEL']};
    border-bottom: 1px solid {p['BORDER']};
}}

/* Panels and Glass Cards */
QFrame#Panel, QFrame#Card {{
    background: {p['PANEL']};
    border: 1px solid {p['BORDER']};
    border-radius: 16px;
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
    border-radius: 12px;
    color: {p['MUTED']};
}}

/* Inputs & Form Controls */
QLineEdit, QPlainTextEdit, QComboBox, QSpinBox, QTextEdit {{
    background: {p['PANEL_LIGHT']};
    border: 1px solid {p['BORDER']};
    border-radius: 10px;
    padding: 8px 12px;
    color: {p['TEXT']};
    selection-background-color: {p['AMBER']};
    selection-color: #ffffff;
}}

QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QTextEdit:focus {{
    border: 1px solid {p['AMBER']};
}}

QComboBox::drop-down {{ border: none; width: 22px; }}
QComboBox QAbstractItemView {{
    background: {p['PANEL_SOLID']};
    border: 1px solid {p['BORDER']};
    border-radius: 8px;
    selection-background-color: {p['AMBER']};
    selection-color: #ffffff;
}}

/* Buttons */
QPushButton {{
    background: {p['PANEL_LIGHT']};
    border: 1px solid {p['BORDER']};
    border-radius: 10px;
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
    border-radius: 8px;
    padding: 5px 12px;
    font-size: 12px;
    font-weight: 600;
}}
QPushButton#HeaderQuickBtn:hover {{ background: {hover_bg}; }}

QPushButton#PrimaryBtn {{
    background: {p['AMBER']};
    color: #ffffff;
    border: none;
    font-weight: 600;
    border-radius: 10px;
}}
QPushButton#PrimaryBtn:hover {{ background: #f59e0b; }}

QPushButton#Solve {{
    background: {p['AMBER']};
    color: #ffffff;
    border: none;
    font-size: 14px;
    font-weight: 700;
    padding: 12px 18px;
    border-radius: 12px;
}}
QPushButton#Solve:hover {{ background: #f59e0b; }}

QPushButton#Listen {{
    background: {p['TEAL']};
    color: #ffffff;
    border: none;
    font-size: 14px;
    font-weight: 700;
    padding: 12px 18px;
    border-radius: 12px;
}}
QPushButton#Listen:hover {{ background: #10b981; }}

QPushButton#Listening {{
    background: {p['RED']};
    color: #ffffff;
    border: none;
    font-size: 14px;
    font-weight: 700;
    padding: 12px 18px;
    border-radius: 12px;
}}
QPushButton#Listening:hover {{ background: #ef4444; }}

QPushButton#Send {{
    background: {p['AMBER']};
    color: #ffffff;
    border: none;
    font-weight: 700;
    border-radius: 10px;
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
    border-radius: 16px;
    padding: 12px;
}}

QListWidget {{
    background: {p['PANEL']};
    border: 1px solid {p['BORDER']};
    border-radius: 12px;
    padding: 6px;
}}
QListWidget::item {{
    padding: 9px 12px;
    border-radius: 8px;
    margin-bottom: 3px;
}}
QListWidget::item:hover {{ background: {hover_bg}; }}
QListWidget::item:selected {{ background: {p['AMBER']}; color: #ffffff; font-weight: 600; }}

QScrollBar:vertical {{
    background: transparent; width: 8px; margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: {"rgba(0, 0, 0, 0.15)" if theme == "light" else "rgba(255, 255, 255, 0.2)"}; border-radius: 4px; min-height: 28px;
}}
QScrollBar::handle:vertical:hover {{ background: {"rgba(0, 0, 0, 0.3)" if theme == "light" else "rgba(255, 255, 255, 0.35)"}; }}
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
QPushButton#CaptionBtn:hover {{ background: {"rgba(0,0,0,0.06)" if theme == "light" else "rgba(255,255,255,0.1)"}; }}
QPushButton#CaptionBtnClose:hover {{ background: {p['RED']}; color: #ffffff; }}

QPushButton#ToolbarBtn {{
    background: {p['PANEL_LIGHT']};
    border: 1px solid {p['BORDER']};
    border-radius: 10px;
    padding: 8px 14px;
    color: {p['TEXT']};
    font-weight: 600;
}}
QPushButton#ToolbarBtn:hover {{ background: {"rgba(0,0,0,0.08)" if theme == "light" else "rgba(255,255,255,0.12)"}; }}
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
pre {{ background: {p['INK']}; border: 1px solid {p['BORDER']}; border-radius: 8px;
      padding: 10px; font-family: Consolas, "DejaVu Sans Mono", monospace; }}
code {{ background: {p['INK']}; padding: 2px 5px; border-radius: 4px; font-family: Consolas, monospace; }}
table {{ border-collapse: collapse; width: 100%; margin: 8px 0; }}
th, td {{ border: 1px solid {p['BORDER']}; padding: 6px 10px; text-align: left; }}
th {{ background: {p['PANEL_LIGHT']}; color: {p['AMBER']}; }}
h1, h2, h3 {{ color: {p['AMBER']}; margin-top: 12px; margin-bottom: 6px; }}
a {{ color: {p['TEAL']}; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
.question-img {{ border: 1px solid {p['BORDER']}; border-radius: 10px; margin: 8px 0; max-width: 100%; }}
"""

STYLESHEET = get_stylesheet("dark")
COMPACT_STYLESHEET = get_compact_stylesheet("dark")
BUSY_STYLESHEET = get_busy_stylesheet("dark")
CHAT_CSS = get_chat_css("dark")
