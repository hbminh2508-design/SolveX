"""Hệ thống Theme & Styling WinUI 3 Fluent / Ultra dành cho SolveX.
Tự động điều chỉnh khoảng cách, màu sắc, font chữ chuẩn Unicode Tiếng Việt/English.
Hỗ trợ chế độ Tự động theo Hệ điều hành (Auto OS Theme).
"""

import sys

# Bang màu WinUI 3 Fluent Palette
DARK_PALETTE = {
    "BG": "#16181d",
    "PANEL": "#1e2128",
    "PANEL_SOLID": "#1e2128",
    "HEADER": "#181a20",
    "CARD": "#242832",
    "CARD_HOVER": "#2c313e",
    "BORDER": "#323846",
    "BORDER_LIGHT": "#40485a",
    "TEXT": "#f0f3f8",
    "MUTED": "#9ca3af",
    "AMBER": "#f59e0b",
    "AMBER_HOVER": "#d97706",
    "TEAL": "#0ea5e9",
    "RED": "#ef4444",
    "RED_HOVER": "#dc2626",
    "SELECTION": "#3b82f6",
    "INPUT_BG": "#1b1e25",
}

LIGHT_PALETTE = {
    "BG": "#f4f6f9",
    "PANEL": "#ffffff",
    "PANEL_SOLID": "#ffffff",
    "HEADER": "#eef2f7",
    "CARD": "#ffffff",
    "CARD_HOVER": "#f0f4f8",
    "BORDER": "#dbe1e8",
    "BORDER_LIGHT": "#cbd5e1",
    "TEXT": "#1e293b",
    "MUTED": "#64748b",
    "AMBER": "#d97706",
    "AMBER_HOVER": "#b45309",
    "TEAL": "#0284c7",
    "RED": "#dc2626",
    "RED_HOVER": "#b91c1c",
    "SELECTION": "#2563eb",
    "INPUT_BG": "#f8fafc",
}

# Alias màu dùng chung
AMBER = "#f59e0b"
TEAL = "#0ea5e9"
RED = "#ef4444"
TEXT = "#f0f3f8"
MUTED = "#9ca3af"
BORDER = "#323846"


def detect_system_theme() -> str:
    """Tự động phát hiện giao diện Tối/Sáng từ Windows Registry."""
    if sys.platform == "win32":
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return "light" if value == 1 else "dark"
        except Exception:
            pass
    return "dark"


def get_palette(theme: str) -> dict:
    if theme == "auto":
        theme = detect_system_theme()
    return LIGHT_PALETTE if theme == "light" else DARK_PALETTE


FONT_FAMILY = '"Segoe UI", "Segoe UI Variable Text", "Arial", sans-serif'


def get_stylesheet(theme: str = "dark") -> str:
    p = get_palette(theme)
    return f"""
    * {{
        font-family: {FONT_FAMILY};
        font-size: 13px;
        color: {p["TEXT"]};
    }}
    
    QMainWindow, QDialog {{
        background-color: {p["BG"]};
    }}

    QFrame#NavSidebar {{
        background-color: {p["PANEL"]};
        border-right: 1px solid {p["BORDER"]};
    }}

    QFrame#HeaderBar {{
        background-color: {p["HEADER"]};
        border-bottom: 1px solid {p["BORDER"]};
    }}

    QFrame#Card {{
        background-color: {p["CARD"]};
        border: 1px solid {p["BORDER"]};
        border-radius: 12px;
    }}

    QLabel#Brand {{
        font-size: 18px;
        font-weight: bold;
        color: {p["AMBER"]};
        background: transparent;
    }}

    QLabel#Tagline {{
        font-size: 11px;
        color: {p["MUTED"]};
        background: transparent;
    }}

    QLabel#SectionLabel {{
        font-size: 14px;
        font-weight: bold;
        color: {p["AMBER"]};
        margin-top: 10px;
        background: transparent;
    }}

    QPushButton#NavBtn {{
        background-color: transparent;
        border: none;
        border-radius: 8px;
        padding: 8px 12px;
        text-align: left;
        font-size: 13px;
        font-weight: 500;
        color: {p["MUTED"]};
    }}

    QPushButton#NavBtn:hover {{
        background-color: {p["CARD_HOVER"]};
        color: {p["TEXT"]};
    }}

    QPushButton#NavBtn:checked {{
        background-color: {p["CARD_HOVER"]};
        color: {p["AMBER"]};
        font-weight: bold;
    }}

    QPushButton {{
        background-color: {p["CARD"]};
        border: 1px solid {p["BORDER"]};
        border-radius: 8px;
        padding: 6px 14px;
        color: {p["TEXT"]};
        font-weight: 500;
    }}

    QPushButton:hover {{
        background-color: {p["CARD_HOVER"]};
        border-color: {p["BORDER_LIGHT"]};
    }}

    QPushButton#PrimaryBtn, QPushButton#Solve {{
        background-color: {p["AMBER"]};
        color: #ffffff;
        font-weight: bold;
        border: none;
    }}

    QPushButton#PrimaryBtn:hover, QPushButton#Solve:hover {{
        background-color: {p["AMBER_HOVER"]};
    }}

    QPushButton#Listen {{
        background-color: {p["TEAL"]};
        color: #ffffff;
        font-weight: bold;
        border: none;
    }}

    QPushButton#Send {{
        background-color: {p["AMBER"]};
        color: #ffffff;
        font-weight: bold;
        font-size: 14px;
        border: none;
        border-radius: 10px;
    }}

    QPushButton#Send:hover {{
        background-color: {p["AMBER_HOVER"]};
    }}

    QLineEdit, QPlainTextEdit, QComboBox {{
        background-color: {p["INPUT_BG"]};
        border: 1px solid {p["BORDER"]};
        border-radius: 8px;
        padding: 6px 10px;
        color: {p["TEXT"]};
    }}

    QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
        border-color: {p["AMBER"]};
    }}

    QComboBox::drop-down {{
        border: none;
    }}

    QTextBrowser#Chat {{
        background-color: {p["PANEL"]};
        border: 1px solid {p["BORDER"]};
        border-radius: 12px;
        padding: 12px;
    }}

    QListWidget {{
        background-color: {p["PANEL"]};
        border: 1px solid {p["BORDER"]};
        border-radius: 10px;
    }}

    QListWidget::item {{
        padding: 8px 10px;
        border-bottom: 1px solid {p["BORDER"]};
        border-radius: 6px;
    }}

    QListWidget::item:selected {{
        background-color: {p["CARD_HOVER"]};
        color: {p["AMBER"]};
    }}

    QProgressBar {{
        border: 1px solid {p["BORDER"]};
        border-radius: 4px;
        background-color: {p["INPUT_BG"]};
        height: 6px;
    }}

    QProgressBar::chunk {{
        background-color: {p["AMBER"]};
        border-radius: 3px;
    }}

    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 8px;
    }}

    QScrollBar::handle:vertical {{
        background: {p["BORDER"]};
        border-radius: 4px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {p["BORDER_LIGHT"]};
    }}
    """


def get_compact_stylesheet(theme: str = "dark") -> str:
    p = get_palette(theme)
    return f"""
    QWidget#CompactRoot {{
        background-color: {p["PANEL_SOLID"]};
    }}
    QWidget#CompactTitleBar {{
        background-color: {p["HEADER"]};
        border-bottom: 1px solid {p["BORDER"]};
    }}
    QLabel#CompactTitle {{
        font-weight: bold;
        font-size: 12px;
        color: {p["AMBER"]};
        background: transparent;
    }}
    QPushButton#ToolbarBtn {{
        background-color: {p["CARD"]};
        border: 1px solid {p["BORDER"]};
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 12px;
    }}
    QPushButton#ToolbarBtn:hover {{
        background-color: {p["CARD_HOVER"]};
    }}
    QPushButton#CaptionBtn {{
        background: transparent;
        border: none;
        border-radius: 4px;
    }}
    QPushButton#CaptionBtn:hover {{
        background-color: {p["CARD_HOVER"]};
    }}
    QPushButton#CaptionBtnClose:hover {{
        background-color: {p["RED"]};
    }}
    """


def get_busy_stylesheet(theme: str = "dark") -> str:
    p = get_palette(theme)
    return f"""
    QWidget#BusyRoot {{
        background-color: {p["PANEL_SOLID"]};
    }}
    QLabel#BusyLabel {{
        color: {p["TEXT"]};
        font-size: 13px;
        font-weight: bold;
    }}
    """


def get_chat_css(theme: str = "dark") -> str:
    p = get_palette(theme)
    return f"""
    body {{
        font-family: {FONT_FAMILY};
        font-size: 13px;
        color: {p["TEXT"]};
        line-height: 1.6;
        margin: 0;
        padding: 0;
    }}
    h1, h2, h3, h4 {{
        color: {p["AMBER"]};
        margin-top: 14px;
        margin-bottom: 8px;
    }}
    code {{
        font-family: "Consolas", "Courier New", monospace;
        background-color: {p["INPUT_BG"]};
        color: {p["TEAL"]};
        padding: 2px 5px;
        border-radius: 4px;
    }}
    pre {{
        background-color: {p["INPUT_BG"]};
        border: 1px solid {p["BORDER"]};
        border-radius: 8px;
        padding: 10px;
        overflow-x: auto;
    }}
    pre code {{
        background: none;
        padding: 0;
    }}
    table {{
        border-collapse: collapse;
        width: 100%;
        margin: 10px 0;
    }}
    th, td {{
        border: 1px solid {p["BORDER"]};
        padding: 6px 10px;
        text-align: left;
    }}
    th {{
        background-color: {p["CARD"]};
        color: {p["AMBER"]};
    }}
    img.question-img {{
        border: 1px solid {p["BORDER"]};
        border-radius: 8px;
        margin-top: 6px;
    }}
    """
