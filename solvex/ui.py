"""Giao diện SolveX v1.8.0 — WinUI 3 Modern Friendly UI, App Logo Tray Icon,
In-App Direct Update Downloader, Exquisite Settings Icon & Speech TTS Voice Reader.
"""

import html as html_lib
import os
import re
import subprocess
import sys
from pathlib import Path

from PyQt6.QtCore import QPoint, QRect, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QGuiApplication, QIcon, QKeySequence, QPainter, QPen, QPixmap, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QSystemTrayIcon,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from . import capture, fluent, style
from .config import Config
from .gemini import DualGeminiClient, GeminiClient, audio_part, image_part, text_part
from .history import HistoryManager
from .i18n import i18n
from .icons import IconFactory
from .saved_questions import SavedQuestionsManager
from .security import SecuritySentinel, deobfuscate_secret, mask_api_key, obfuscate_secret
from .updater import BuildExeWorker, CheckUpdateWorker, DownloadUpdateWorker, launch_standalone_updater
from .version import APP_VERSION, changelog_markdown
from .workers import AskWorker, CaptureWorker, RecordWorker, TestApiWorker

try:
    import markdown as md_lib
except Exception:
    md_lib = None


def _simple_markdown_parse(text: str) -> str:
    """Fall-back Markdown & Math parser converting Markdown blocks to clean HTML."""
    lines = text.split("\n")
    html_lines = []
    in_code = False
    code_block = []

    for line in lines:
        if line.strip().startswith("```"):
            if in_code:
                in_code = False
                code_text = html_lib.escape("\n".join(code_block))
                html_lines.append(f"<pre><code>{code_text}</code></pre>")
                code_block = []
            else:
                in_code = True
            continue

        if in_code:
            code_block.append(line)
            continue

        if line.startswith("### "):
            html_lines.append(f"<h3>{html_lib.escape(line[4:])}</h3>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{html_lib.escape(line[3:])}</h2>")
        elif line.startswith("# "):
            html_lines.append(f"<h1>{html_lib.escape(line[2:])}</h1>")
        elif line.strip().startswith("- ") or line.strip().startswith("* "):
            item_text = line.strip()[2:]
            html_lines.append(f"<li>{item_text}</li>")
        elif not line.strip():
            html_lines.append("<br>")
        else:
            html_lines.append(f"<p>{line}</p>")

    parsed = "\n".join(html_lines)
    parsed = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', parsed)
    parsed = re.sub(r'\*(.*?)\*', r'<i>\1</i>', parsed)
    parsed = re.sub(r'`(.*?)`', r'<code>\1</code>', parsed)
    return parsed


GREEK_MAP = {
    # Lowercase Greek
    r"\alpha": "α", r"\beta": "β", r"\gamma": "γ", r"\delta": "δ",
    r"\epsilon": "ε", r"\varepsilon": "ε", r"\zeta": "ζ", r"\eta": "η",
    r"\theta": "θ", r"\vartheta": "ϑ", r"\iota": "ι", r"\kappa": "κ",
    r"\lambda": "λ", r"\mu": "μ", r"\nu": "ν", r"\xi": "ξ",
    r"\pi": "π", r"\varpi": "ϖ", r"\rho": "ρ", r"\varrho": "ϱ",
    r"\sigma": "σ", r"\varsigma": "ς", r"\tau": "τ", r"\upsilon": "υ",
    r"\phi": "φ", r"\varphi": "φ", r"\chi": "χ", r"\psi": "ψ",
    r"\omega": "ω",
    # Uppercase Greek
    r"\Gamma": "Γ", r"\Delta": "Δ", r"\Theta": "Θ", r"\Lambda": "Λ",
    r"\Xi": "Ξ", r"\Pi": "Π", r"\Sigma": "Σ", r"\Upsilon": "Υ",
    r"\Phi": "Φ", r"\Psi": "Ψ", r"\Omega": "Ω",
}

MATH_SYMBOLS = {
    # Binary operators
    r"\cdot": " · ", r"\times": " × ", r"\div": " ÷ ",
    r"\pm": " ± ", r"\mp": " ∓ ", r"\ast": " ∗ ", r"\star": " ⋆ ",
    r"\bullet": " • ", r"\oplus": " ⊕ ", r"\otimes": " ⊗ ",
    # Relations
    r"\le": " ≤ ", r"\leq": " ≤ ", r"\ge": " ≥ ", r"\geq": " ≥ ",
    r"\neq": " ≠ ", r"\ne": " ≠ ", r"\approx": " ≈ ", r"\equiv": " ≡ ",
    r"\sim": " ∼ ", r"\simeq": " ≃ ", r"\cong": " ≅ ",
    r"\propto": " ∝ ", r"\ll": " ≪ ", r"\gg": " ≫ ",
    r"\subset": " ⊂ ", r"\supset": " ⊃ ", r"\subseteq": " ⊆ ", r"\supseteq": " ⊇ ",
    r"\in": " ∈ ", r"\notin": " ∉ ", r"\ni": " ∋ ",
    r"\cup": " ∪ ", r"\cap": " ∩ ",
    # Arrows
    r"\rightarrow": " → ", r"\to": " → ", r"\leftarrow": " ← ",
    r"\Rightarrow": " ⇒ ", r"\Leftarrow": " ⇐ ",
    r"\leftrightarrow": " ↔ ", r"\Leftrightarrow": " ⇔ ",
    r"\implies": " ⟹ ", r"\iff": " ⟺ ",
    r"\uparrow": " ↑ ", r"\downarrow": " ↓ ",
    r"\mapsto": " ↦ ",
    # Big operators
    r"\sum": "∑", r"\prod": "∏", r"\coprod": "∐",
    r"\int": "∫", r"\iint": "∬", r"\iiint": "∭", r"\oint": "∮",
    r"\bigcup": "⋃", r"\bigcap": "⋂",
    # Misc symbols
    r"\infty": "∞", r"\partial": "∂", r"\nabla": "∇",
    r"\forall": "∀", r"\exists": "∃", r"\nexists": "∄",
    r"\emptyset": "∅", r"\varnothing": "∅",
    r"\degree": "°", r"\circ": "°",
    r"\angle": "∠", r"\measuredangle": "∡",
    r"\triangle": "△", r"\square": "□",
    r"\perp": " ⊥ ", r"\parallel": " ∥ ",
    r"\hbar": "ℏ", r"\ell": "ℓ", r"\Re": "ℜ", r"\Im": "ℑ",
    r"\aleph": "ℵ",
    r"\neg": "¬", r"\lnot": "¬",
    r"\wedge": " ∧ ", r"\land": " ∧ ",
    r"\vee": " ∨ ", r"\lor": " ∨ ",
    r"\ldots": "…", r"\cdots": "⋯", r"\vdots": "⋮", r"\ddots": "⋱", r"\dots": "…",
    r"\therefore": "∴", r"\because": "∵",
    # Spacing & decorators
    r"\quad": "  ", r"\qquad": "    ",
    r"\,": " ", r"\;": " ", r"\:": " ", r"\ ": " ",
    # Delimiters
    r"\lbrace": "{", r"\rbrace": "}", r"\{": "{", r"\}": "}",
    r"\langle": "⟨", r"\rangle": "⟩",
    r"\lfloor": "⌊", r"\rfloor": "⌋", r"\lceil": "⌈", r"\rceil": "⌉",
    r"\vert": "|", r"\Vert": "‖", r"\|": "‖",
}

# Functions that should be rendered in upright/roman style
MATH_FUNCTIONS = [
    "cos", "sin", "tan", "cot", "sec", "csc",
    "arccos", "arcsin", "arctan", "arccot",
    "cosh", "sinh", "tanh", "coth",
    "log", "ln", "lg", "exp",
    "lim", "limsup", "liminf",
    "max", "min", "sup", "inf",
    "det", "dim", "ker", "arg",
    "gcd", "lcm", "deg", "hom",
    "mod", "bmod", "pmod",
]

# mathcal character mapping (uppercase only)
MATHCAL_MAP = {
    "A": "𝒜", "B": "ℬ", "C": "𝒞", "D": "𝒟", "E": "ℰ", "F": "ℱ",
    "G": "𝒢", "H": "ℋ", "I": "ℐ", "J": "𝒥", "K": "𝒦", "L": "ℒ",
    "M": "ℳ", "N": "𝒩", "O": "𝒪", "P": "𝒫", "Q": "𝒬", "R": "ℛ",
    "S": "𝒮", "T": "𝒯", "U": "𝒰", "V": "𝒱", "W": "𝒲", "X": "𝒳",
    "Y": "𝒴", "Z": "𝒵",
}

# mathbb (blackboard bold) character mapping
MATHBB_MAP = {
    "A": "𝔸", "B": "𝔹", "C": "ℂ", "D": "𝔻", "E": "𝔼", "F": "𝔽",
    "G": "𝔾", "H": "ℍ", "I": "𝕀", "J": "𝕁", "K": "𝕂", "L": "𝕃",
    "M": "𝕄", "N": "ℕ", "O": "𝕆", "P": "ℙ", "Q": "ℚ", "R": "ℝ",
    "S": "𝕊", "T": "𝕋", "U": "𝕌", "V": "𝕍", "W": "𝕎", "X": "𝕏",
    "Y": "𝕐", "Z": "ℤ",
    "0": "𝟘", "1": "𝟙", "2": "𝟚", "3": "𝟛", "4": "𝟜",
    "5": "𝟝", "6": "𝟞", "7": "𝟟", "8": "𝟠", "9": "𝟡",
}


def _find_brace_group(expr: str, start: int) -> tuple:
    """Tìm cặp ngoặc nhọn {} cân bằng bắt đầu từ vị trí `start`.
    Trả về (nội dung bên trong, vị trí kết thúc sau '}'). Nếu không có, trả về (None, start)."""
    if start >= len(expr) or expr[start] != '{':
        return None, start
    depth = 0
    for i in range(start, len(expr)):
        if expr[i] == '{':
            depth += 1
        elif expr[i] == '}':
            depth -= 1
            if depth == 0:
                return expr[start + 1:i], i + 1
    return expr[start + 1:], len(expr)


def _convert_math_expr(expr: str) -> str:
    """Chuyển đổi một công thức LaTeX đầy đủ sang chuỗi HTML native cho QTextBrowser."""
    if not expr or not expr.strip():
        return ""

    # --- Pass 1: Process structural commands that require brace-group parsing ---
    # Process these iteratively because they can be nested

    MAX_PASSES = 10
    for _pass in range(MAX_PASSES):
        changed = False

        # \frac{num}{den} - fraction
        m = re.search(r'\\frac\s*\{', expr)
        if m:
            num_content, after_num = _find_brace_group(expr, m.end() - 1)
            if num_content is not None:
                den_content, after_den = _find_brace_group(expr, after_num)
                if den_content is not None:
                    num_html = _convert_math_expr(num_content)
                    den_html = _convert_math_expr(den_content)
                    frac_html = (
                        f"<span style='display:inline-block; vertical-align:middle; "
                        f"text-align:center; margin:0 2px;'>"
                        f"<span style='border-bottom:1px solid; display:block; padding:0 2px;'>"
                        f"{num_html}</span>"
                        f"<span style='display:block; padding:0 2px;'>{den_html}</span></span>"
                    )
                    expr = expr[:m.start()] + frac_html + expr[after_den:]
                    changed = True
                    continue

        # \sqrt[n]{content} or \sqrt{content}
        m = re.search(r'\\sqrt\s*(?:\[([^\]]*)\])?\s*\{', expr)
        if m:
            idx_content = m.group(1)
            inner, after = _find_brace_group(expr, m.end() - 1)
            if inner is not None:
                inner_html = _convert_math_expr(inner)
                if idx_content:
                    sqrt_html = f"<sup style='font-size:0.7em;'>{idx_content}</sup>√<span style='border-top:1px solid; padding:0 1px;'>{inner_html}</span>"
                else:
                    sqrt_html = f"√<span style='border-top:1px solid; padding:0 1px;'>{inner_html}</span>"
                expr = expr[:m.start()] + sqrt_html + expr[after:]
                changed = True
                continue

        # \text{...} - text mode
        m = re.search(r'\\text\s*\{', expr)
        if m:
            inner, after = _find_brace_group(expr, m.end() - 1)
            if inner is not None:
                expr = expr[:m.start()] + inner + expr[after:]
                changed = True
                continue

        # \textbf{...} - bold text
        m = re.search(r'\\textbf\s*\{', expr)
        if m:
            inner, after = _find_brace_group(expr, m.end() - 1)
            if inner is not None:
                expr = expr[:m.start()] + f"<b>{inner}</b>" + expr[after:]
                changed = True
                continue

        # \textit{...} - italic text
        m = re.search(r'\\textit\s*\{', expr)
        if m:
            inner, after = _find_brace_group(expr, m.end() - 1)
            if inner is not None:
                expr = expr[:m.start()] + f"<i>{inner}</i>" + expr[after:]
                changed = True
                continue

        # \mathrm{...} / \textrm{...} - roman/upright text in math
        m = re.search(r'\\(?:mathrm|textrm|operatorname)\s*\{', expr)
        if m:
            inner, after = _find_brace_group(expr, m.end() - 1)
            if inner is not None:
                expr = expr[:m.start()] + f"<span style='font-style:normal;'>{inner}</span>" + expr[after:]
                changed = True
                continue

        # \mathbf{...} / \boldsymbol{...} - bold math
        m = re.search(r'\\(?:mathbf|boldsymbol|bm)\s*\{', expr)
        if m:
            inner, after = _find_brace_group(expr, m.end() - 1)
            if inner is not None:
                inner_html = _convert_math_expr(inner)
                expr = expr[:m.start()] + f"<b>{inner_html}</b>" + expr[after:]
                changed = True
                continue

        # \mathcal{X} - calligraphic
        m = re.search(r'\\mathcal\s*\{', expr)
        if m:
            inner, after = _find_brace_group(expr, m.end() - 1)
            if inner is not None:
                cal_text = "".join(MATHCAL_MAP.get(c, c) for c in inner)
                expr = expr[:m.start()] + cal_text + expr[after:]
                changed = True
                continue

        # \mathbb{X} - blackboard bold
        m = re.search(r'\\mathbb\s*\{', expr)
        if m:
            inner, after = _find_brace_group(expr, m.end() - 1)
            if inner is not None:
                bb_text = "".join(MATHBB_MAP.get(c, c) for c in inner)
                expr = expr[:m.start()] + bb_text + expr[after:]
                changed = True
                continue

        # \mathit{...} - italic math (usually default, just strip command)
        m = re.search(r'\\mathit\s*\{', expr)
        if m:
            inner, after = _find_brace_group(expr, m.end() - 1)
            if inner is not None:
                inner_html = _convert_math_expr(inner)
                expr = expr[:m.start()] + f"<i>{inner_html}</i>" + expr[after:]
                changed = True
                continue

        # \vec{X} - vector arrow directly ABOVE symbol using combining right arrow above (\u20d7)
        # Triệt tiêu hoàn toàn lỗi nhảy dòng của HTML table trong QTextBrowser
        m = re.search(r'\\vec\s*\{', expr)
        if m:
            inner, after = _find_brace_group(expr, m.end() - 1)
            if inner is not None:
                inner_html = _convert_math_expr(inner)
                vec_str = "".join(c + "\u20d7" if c.isalpha() else c for c in inner_html)
                if not any("\u20d7" in c for c in vec_str):
                    vec_str = inner_html + "\u20d7"
                expr = expr[:m.start()] + vec_str + expr[after:]
                changed = True
                continue

        # \hat{X} - hat accent directly ABOVE symbol using combining circumflex accent (\u0302)
        m = re.search(r'\\hat\s*\{', expr)
        if m:
            inner, after = _find_brace_group(expr, m.end() - 1)
            if inner is not None:
                inner_html = _convert_math_expr(inner)
                hat_str = "".join(c + "\u0302" if c.isalpha() else c for c in inner_html)
                if not any("\u0302" in c for c in hat_str):
                    hat_str = inner_html + "\u0302"
                expr = expr[:m.start()] + hat_str + expr[after:]
                changed = True
                continue

        # \bar{X} / \overline{X} - bar/overline accent
        m = re.search(r'\\(?:bar|overline)\s*\{', expr)
        if m:
            inner, after = _find_brace_group(expr, m.end() - 1)
            if inner is not None:
                inner_html = _convert_math_expr(inner)
                expr = expr[:m.start()] + f"<span style='border-top:1px solid; padding-top:1px;'>{inner_html}</span>" + expr[after:]
                changed = True
                continue

        # \underline{X}
        m = re.search(r'\\underline\s*\{', expr)
        if m:
            inner, after = _find_brace_group(expr, m.end() - 1)
            if inner is not None:
                inner_html = _convert_math_expr(inner)
                expr = expr[:m.start()] + f"<u>{inner_html}</u>" + expr[after:]
                changed = True
                continue

        # \tilde{X} - tilde accent
        m = re.search(r'\\tilde\s*\{', expr)
        if m:
            inner, after = _find_brace_group(expr, m.end() - 1)
            if inner is not None:
                inner_html = _convert_math_expr(inner)
                expr = expr[:m.start()] + f"<span style='display:inline-block; text-align:center;'><span style='display:block; font-size:0.6em; line-height:0.8;'>~</span><span>{inner_html}</span></span>" + expr[after:]
                changed = True
                continue

        # \dot{X} - dot accent
        m = re.search(r'\\dot\s*\{', expr)
        if m:
            inner, after = _find_brace_group(expr, m.end() - 1)
            if inner is not None:
                inner_html = _convert_math_expr(inner)
                expr = expr[:m.start()] + f"<span style='display:inline-block; text-align:center;'><span style='display:block; font-size:0.6em; line-height:0.8;'>·</span><span>{inner_html}</span></span>" + expr[after:]
                changed = True
                continue

        # \ddot{X} - double dot
        m = re.search(r'\\ddot\s*\{', expr)
        if m:
            inner, after = _find_brace_group(expr, m.end() - 1)
            if inner is not None:
                inner_html = _convert_math_expr(inner)
                expr = expr[:m.start()] + f"<span style='display:inline-block; text-align:center;'><span style='display:block; font-size:0.6em; line-height:0.8;'>¨</span><span>{inner_html}</span></span>" + expr[after:]
                changed = True
                continue

        # \boxed{X} - box around expression
        m = re.search(r'\\boxed\s*\{', expr)
        if m:
            inner, after = _find_brace_group(expr, m.end() - 1)
            if inner is not None:
                inner_html = _convert_math_expr(inner)
                expr = expr[:m.start()] + f"<span style='border:1px solid; padding:2px 4px;'>{inner_html}</span>" + expr[after:]
                changed = True
                continue

        # \color{color}{content}
        m = re.search(r'\\color\s*\{', expr)
        if m:
            color_val, after_color = _find_brace_group(expr, m.end() - 1)
            if color_val is not None:
                content, after_content = _find_brace_group(expr, after_color)
                if content is not None:
                    inner_html = _convert_math_expr(content)
                    expr = expr[:m.start()] + f"<span style='color:{color_val};'>{inner_html}</span>" + expr[after_content:]
                    changed = True
                    continue

        # \underbrace{X}_{label}
        m = re.search(r'\\underbrace\s*\{', expr)
        if m:
            inner, after = _find_brace_group(expr, m.end() - 1)
            if inner is not None:
                inner_html = _convert_math_expr(inner)
                # Check for _{label} after
                label_m = re.match(r'\s*_\{([^{}]*)\}', expr[after:])
                if label_m:
                    label = _convert_math_expr(label_m.group(1))
                    total_end = after + label_m.end()
                    expr = expr[:m.start()] + (
                        f"<span style='display:inline-block; text-align:center;'>"
                        f"<span style='border-bottom:1px solid; display:block;'>{inner_html}</span>"
                        f"<span style='display:block; font-size:0.8em;'>{label}</span></span>"
                    ) + expr[total_end:]
                else:
                    expr = expr[:m.start()] + f"<span style='border-bottom:1px solid;'>{inner_html}</span>" + expr[after:]
                changed = True
                continue

        # \overbrace{X}^{label}
        m = re.search(r'\\overbrace\s*\{', expr)
        if m:
            inner, after = _find_brace_group(expr, m.end() - 1)
            if inner is not None:
                inner_html = _convert_math_expr(inner)
                label_m = re.match(r'\s*\^\{([^{}]*)\}', expr[after:])
                if label_m:
                    label = _convert_math_expr(label_m.group(1))
                    total_end = after + label_m.end()
                    expr = expr[:m.start()] + (
                        f"<span style='display:inline-block; text-align:center;'>"
                        f"<span style='display:block; font-size:0.8em;'>{label}</span>"
                        f"<span style='border-top:1px solid; display:block;'>{inner_html}</span></span>"
                    ) + expr[total_end:]
                else:
                    expr = expr[:m.start()] + f"<span style='border-top:1px solid;'>{inner_html}</span>" + expr[after:]
                changed = True
                continue

        if not changed:
            break

    # --- Pass 2: \begin{cases}...\end{cases} environment ---
    cases_pattern = re.compile(r'\\begin\{cases\}(.*?)\\end\{cases\}', re.DOTALL)
    def cases_repl(m):
        body = m.group(1).strip()
        rows = re.split(r'\\\\', body)
        html_rows = []
        for row in rows:
            row = row.strip()
            if not row:
                continue
            parts = row.split('&')
            expr_part = _convert_math_expr(parts[0].strip()) if parts else ""
            cond_part = _convert_math_expr(parts[1].strip()) if len(parts) > 1 else ""
            html_rows.append(
                f"<tr><td style='padding:2px 8px 2px 0;'>{expr_part}</td>"
                f"<td style='padding:2px 0;'>{cond_part}</td></tr>"
            )
        return (
            f"<span style='display:inline-block; vertical-align:middle; border-left:2px solid; padding-left:6px;'>"
            f"<table style='border-collapse:collapse;'>{''.join(html_rows)}</table></span>"
        )
    expr = cases_pattern.sub(cases_repl, expr)

    # --- Pass 2b: \begin{aligned}...\end{aligned} or \begin{align}...\end{align} ---
    aligned_pattern = re.compile(r'\\begin\{(?:aligned|align)\*?\}(.*?)\\end\{(?:aligned|align)\*?\}', re.DOTALL)
    def aligned_repl(m):
        body = m.group(1).strip()
        rows = re.split(r'\\\\', body)
        html_rows = []
        for row in rows:
            row = row.strip()
            if not row:
                continue
            parts = row.split('&')
            cells = [f"<td style='padding:2px 4px;'>{_convert_math_expr(p.strip())}</td>" for p in parts]
            html_rows.append(f"<tr>{''.join(cells)}</tr>")
        return f"<table style='border-collapse:collapse; margin:4px 0;'>{''.join(html_rows)}</table>"
    expr = aligned_pattern.sub(aligned_repl, expr)

    # --- Pass 2c: \begin{matrix/pmatrix/bmatrix}...\end{...} ---
    matrix_pattern = re.compile(r'\\begin\{(matrix|pmatrix|bmatrix|vmatrix)\}(.*?)\\end\{\1\}', re.DOTALL)
    def matrix_repl(m):
        mtype = m.group(1)
        body = m.group(2).strip()
        rows = re.split(r'\\\\', body)
        html_rows = []
        for row in rows:
            row = row.strip()
            if not row:
                continue
            cells = row.split('&')
            html_cells = [f"<td style='padding:2px 6px; text-align:center;'>{_convert_math_expr(c.strip())}</td>" for c in cells]
            html_rows.append(f"<tr>{''.join(html_cells)}</tr>")
        table = f"<table style='border-collapse:collapse; display:inline-table; vertical-align:middle;'>{''.join(html_rows)}</table>"
        if mtype == "pmatrix":
            return f"(<span style='display:inline-block; vertical-align:middle;'>{table}</span>)"
        elif mtype == "bmatrix":
            return f"[<span style='display:inline-block; vertical-align:middle;'>{table}</span>]"
        elif mtype == "vmatrix":
            return f"|<span style='display:inline-block; vertical-align:middle;'>{table}</span>|"
        return table
    expr = matrix_pattern.sub(matrix_repl, expr)

    # --- Pass 3: Greek letters (replace longer names first to avoid partial matches) ---
    sorted_greek = sorted(GREEK_MAP.items(), key=lambda x: -len(x[0]))
    for k, v in sorted_greek:
        expr = re.sub(re.escape(k) + r'(?![a-zA-Z])', v, expr)

    # --- Pass 4: Math symbols (replace longer names first) ---
    sorted_symbols = sorted(MATH_SYMBOLS.items(), key=lambda x: -len(x[0]))
    for k, v in sorted_symbols:
        expr = re.sub(re.escape(k) + r'(?![a-zA-Z])', v, expr)

    # --- Pass 5: Named math functions \cos, \sin, etc. ---
    sorted_funcs = sorted(MATH_FUNCTIONS, key=lambda x: -len(x))
    for func in sorted_funcs:
        expr = re.sub(r'\\' + func + r'(?![a-zA-Z])',
                       f"<span style='font-style:normal;'>{func}</span>", expr)

    # --- Pass 6: Superscripts and subscripts ---
    # ^{...} with brace groups
    expr = re.sub(r'\^\{([^{}]+)\}', lambda m: f"<sup>{_convert_math_expr(m.group(1))}</sup>", expr)
    # ^single_char (digit, letter, +, -)
    expr = re.sub(r'\^([0-9a-zA-Zα-ωΑ-Ω+\-])', r'<sup>\1</sup>', expr)
    # _{...} with brace groups
    expr = re.sub(r'_\{([^{}]+)\}', lambda m: f"<sub>{_convert_math_expr(m.group(1))}</sub>", expr)
    # _single_char
    expr = re.sub(r'_([0-9a-zA-Zα-ωΑ-Ω+\-])', r'<sub>\1</sub>', expr)

    # --- Pass 7: Cleanup remaining LaTeX artifacts ---
    # \left and \right delimiters (just remove the command, keep the delimiter)
    expr = re.sub(r'\\left\s*([(\[|.{\\])', r'\1', expr)
    expr = re.sub(r'\\right\s*([)\]|.}\\])', r'\1', expr)
    expr = re.sub(r'\\left\s*\\([{}|])', lambda m: {'|': '|', '{': '{', '}': '}'}.get(m.group(1), m.group(1)), expr)
    expr = re.sub(r'\\right\s*\\([{}|])', lambda m: {'|': '|', '{': '{', '}': '}'}.get(m.group(1), m.group(1)), expr)
    # \left. and \right. (invisible delimiter)
    expr = expr.replace(r'\left.', '').replace(r'\right.', '')

    # \! (negative thin space) — remove
    expr = expr.replace(r'\!', '')

    # Any remaining \commandname{content} — just show the content
    expr = re.sub(r'\\[a-zA-Z]+\{([^{}]*)\}', r'\1', expr)

    # Any remaining unknown \command — remove the backslash
    expr = re.sub(r'\\([a-zA-Z]+)', r'\1', expr)

    # Clean up stray braces that remain
    expr = expr.replace('{', '').replace('}', '')

    # Clean up multiple spaces
    expr = re.sub(r'  +', ' ', expr)

    return expr.strip()


def render_latex_math(text: str) -> str:
    """Tự động phát hiện và chuyển đổi toàn bộ công thức LaTeX sang HTML native.
    Hỗ trợ: $...$, $$...$$, \\(...\\), \\[...\\]"""
    if not text:
        return ""

    MATH_STYLE_INLINE = (
        "font-family:\"Cambria Math\", \"Times New Roman\", serif; "
        "font-size:14px; color:#0ea5e9; font-weight:600;"
    )
    MATH_STYLE_DISPLAY = (
        "text-align:center; margin:10px 0; "
        "font-family:\"Cambria Math\", \"Times New Roman\", serif; "
        "font-size:15px; color:#0ea5e9; font-weight:bold;"
    )

    # Display math: $$...$$ (multiline)
    def display_repl(match):
        inner = match.group(1)
        conv = _convert_math_expr(inner)
        return f"<div style='{MATH_STYLE_DISPLAY}'>{conv}</div>"

    text = re.sub(r'\$\$(.*?)\$\$', display_repl, text, flags=re.DOTALL)

    # Display math: \[...\] (multiline)
    text = re.sub(r'\\\[(.*?)\\\]', display_repl, text, flags=re.DOTALL)

    # Inline math: $...$
    def inline_repl(match):
        inner = match.group(1)
        conv = _convert_math_expr(inner)
        return f"<span style='{MATH_STYLE_INLINE}'>{conv}</span>"

    text = re.sub(r'\$([^\$\n]+?)\$', inline_repl, text)

    # Inline math: \(...\)
    text = re.sub(r'\\\((.+?)\\\)', inline_repl, text)

    return text


def render_markdown(text: str) -> str:
    if not text:
        return ""
    
    text_with_math = render_latex_math(text)

    if md_lib is not None:
        try:
            return md_lib.markdown(
                text_with_math, extensions=["fenced_code", "tables", "nl2br", "sane_lists"]
            )
        except Exception:
            pass
    return _simple_markdown_parse(text_with_math)


MATHJAX_SCRIPT = """
<script>
window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']]
  },
  svg: { fontCache: 'global' }
};
</script>
<script type="text/javascript" id="MathJax-script" async
  src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js">
</script>
"""


def wrap_html_page(body_html: str, theme: str = "dark") -> str:
    css = style.get_chat_css(theme)
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>{css}</style>
{MATHJAX_SCRIPT}
</head>
<body>
{body_html}
</body>
</html>"""


def _resource_path(*parts) -> str:
    base = getattr(sys, "_MEIPASS", None)
    if base is None:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *parts)


def build_app_icon() -> QIcon:
    for name in ("icon.ico", "icon.png"):
        path = _resource_path("assets", name)
        if os.path.exists(path):
            icon = QIcon(path)
            if not icon.isNull():
                return icon
    return _draw_fallback_icon()


def _draw_fallback_icon() -> QIcon:
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(style.AMBER))
    painter.drawRoundedRect(2, 2, 60, 60, 14, 14)
    painter.setPen(QColor("#ffffff"))
    font = painter.font()
    font.setBold(True)
    font.setPointSize(26)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "S")
    painter.end()
    return QIcon(pixmap)


# --------------------------------------------------------------------------
# Update Progress Dialog (Hiển thị % tiến độ, Tốc độ MB/s, Thời gian ETA)
# --------------------------------------------------------------------------
class UpdateProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tải Bản Cập Nhật SolveX")
        self.setWindowIcon(build_app_icon())
        self.setFixedSize(450, 180)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        self.title_label = QLabel("Đang tải xuống phiên bản mới nhất...")
        self.title_label.setStyleSheet("font-size:14px; font-weight:bold; color:" + style.AMBER + ";")
        layout.addWidget(self.title_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(18)
        layout.addWidget(self.progress_bar)

        info_row = QHBoxLayout()
        self.speed_label = QLabel("Tốc độ: 0 KB/s")
        self.speed_label.setStyleSheet("color:" + style.MUTED + ";")
        self.eta_label = QLabel("Thời gian còn lại: --:--")
        self.eta_label.setStyleSheet("color:" + style.MUTED + ";")
        info_row.addWidget(self.speed_label)
        info_row.addStretch(1)
        info_row.addWidget(self.eta_label)
        layout.addLayout(info_row)

        self.detail_label = QLabel("0 MB / 0 MB (0%)")
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.detail_label)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self.cancel_btn = QPushButton("Hủy tải")
        btn_row.addWidget(self.cancel_btn)
        layout.addLayout(btn_row)

    def update_progress(self, percent: float, speed_str: str, eta_str: str, downloaded: int, total: int):
        self.progress_bar.setValue(int(percent))
        self.speed_label.setText(f"Tốc độ: {speed_str}")
        self.eta_label.setText(f"Thời gian còn lại: {eta_str}")
        down_mb = downloaded / (1024 * 1024)
        total_mb = total / (1024 * 1024)
        if total > 0:
            self.detail_label.setText(f"{down_mb:.1f} MB / {total_mb:.1f} MB ({int(percent)}%)")
        else:
            self.detail_label.setText(f"{down_mb:.1f} MB đã tải")


# --------------------------------------------------------------------------
# Region Selector Overlay
# --------------------------------------------------------------------------
class RegionSelector(QWidget):
    region_selected = pyqtSignal(int, int, int, int)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)
        geo = QGuiApplication.primaryScreen().virtualGeometry()
        self.setGeometry(geo)
        self.origin = QPoint()
        self.current = QPoint()
        self.dragging = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(10, 12, 17, 140))
        hint = i18n.t("st_monitor_region") + "  ·  Esc to Cancel"
        painter.setPen(QColor("#ffffff"))
        painter.drawText(
            self.rect().adjusted(0, 28, 0, 0),
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,
            hint,
        )

        if self.dragging:
            rect = QRect(self.origin, self.current).normalized()
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(rect, Qt.GlobalColor.transparent)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            painter.setPen(QPen(QColor(style.AMBER), 2))
            painter.drawRect(rect)
            painter.drawText(
                rect.adjusted(4, -20, 0, 0),
                Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                f"{rect.width()} × {rect.height()}",
            )
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.origin = event.position().toPoint()
            self.current = self.origin
            self.dragging = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.current = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if not self.dragging:
            return
        self.dragging = False
        rect = QRect(self.origin, self.current).normalized()
        self.close()
        if rect.width() < 5 or rect.height() < 5:
            return
        ratio = self.devicePixelRatioF()
        offset = self.geometry().topLeft()
        x = int((rect.x() + offset.x()) * ratio)
        y = int((rect.y() + offset.y()) * ratio)
        w = int(rect.width() * ratio)
        h = int(rect.height() * ratio)
        self.region_selected.emit(x, y, w, h)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()


class CaptionButton(QPushButton):
    def __init__(self, icon_name: str, tooltip: str = "", close_style: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("CaptionBtnClose" if close_style else "CaptionBtn")
        self.setFixedSize(34, 28)
        color = style.RED if close_style else style.TEXT
        self.setIcon(IconFactory.draw_icon(icon_name, color, 14))
        self.setToolTip(tooltip)
        self.setCursor(Qt.CursorShape.ArrowCursor)


# --------------------------------------------------------------------------
# Compact Top Bar Window (Nâng cấp Bộ Chọn Chế Độ Giải Bài Mode Combo)
# --------------------------------------------------------------------------
class CompactWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.setObjectName("CompactRoot")
        self.setWindowTitle("SolveX")
        self.setWindowIcon(build_app_icon())
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(style.get_compact_stylesheet(self.main.config.get("theme", "dark")))
        self._drag_offset = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(2, 2, 2, 8)
        outer.setSpacing(6)
        outer.addWidget(self._build_titlebar())

        row = QHBoxLayout()
        row.setContentsMargins(8, 0, 8, 0)
        row.setSpacing(6)

        self.capture_btn = QPushButton(i18n.t("btn_capture"))
        self.capture_btn.setIcon(IconFactory.draw_icon("camera", style.TEXT, 16))
        self.capture_btn.setObjectName("ToolbarBtn")
        self.capture_btn.setToolTip(i18n.t("tip_capture"))
        self.capture_btn.clicked.connect(self.main.on_pick_region)
        row.addWidget(self.capture_btn)

        self.solve_btn = QPushButton(i18n.t("btn_solve_normal"))
        self.solve_btn.setIcon(IconFactory.draw_icon("solve", style.AMBER, 16))
        self.solve_btn.setObjectName("ToolbarBtn")
        self.solve_btn.setToolTip(i18n.t("tip_solve"))
        self.solve_btn.clicked.connect(self.main.on_solve_normal)
        row.addWidget(self.solve_btn)

        self.listen_btn = QPushButton(i18n.t("btn_solve_listening"))
        self.listen_btn.setIcon(IconFactory.draw_icon("headphones", style.TEAL, 16))
        self.listen_btn.setObjectName("ToolbarBtn")
        self.listen_btn.setToolTip(i18n.t("tip_listen"))
        self.listen_btn.clicked.connect(self.main.on_listening_clicked)
        row.addWidget(self.listen_btn)

        self.top_mode_combo = QComboBox()
        self.top_mode_combo.addItem(i18n.t("mode_step"), "step")
        self.top_mode_combo.addItem(i18n.t("mode_mcq"), "mcq")
        self.top_mode_combo.addItem(i18n.t("mode_similar"), "similar")
        self.top_mode_combo.addItem(i18n.t("mode_concept"), "concept")
        self.top_mode_combo.setFixedWidth(160)
        self.top_mode_combo.currentIndexChanged.connect(self._sync_mode_from_top)
        row.addWidget(self.top_mode_combo)

        self.history_btn = QPushButton()
        self.history_btn.setIcon(IconFactory.draw_icon("history", style.TEXT, 16))
        self.history_btn.setObjectName("ToolbarBtn")
        self.history_btn.setToolTip(i18n.t("tip_history"))
        self.history_btn.clicked.connect(lambda: self.main.show_tab("history"))
        row.addWidget(self.history_btn)

        self.settings_btn = QPushButton()
        self.settings_btn.setIcon(IconFactory.draw_icon("settings", style.TEXT, 16))
        self.settings_btn.setObjectName("ToolbarBtn")
        self.settings_btn.setToolTip(i18n.t("tip_settings"))
        self.settings_btn.clicked.connect(lambda: self.main.show_tab("settings"))
        row.addWidget(self.settings_btn)

        outer.addLayout(row)
        self.adjustSize()

        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.move(screen.center().x() - self.width() // 2, screen.top() + 20)
        i18n.language_changed.connect(self.update_strings)

    def _sync_mode_from_top(self, index: int):
        if hasattr(self.main, "mode_combo") and self.main.mode_combo:
            self.main.mode_combo.blockSignals(True)
            self.main.mode_combo.setCurrentIndex(index)
            self.main.mode_combo.blockSignals(False)

    def sync_mode_from_main(self, index: int):
        self.top_mode_combo.blockSignals(True)
        self.top_mode_combo.setCurrentIndex(index)
        self.top_mode_combo.blockSignals(False)

    def update_strings(self):
        self.capture_btn.setText(i18n.t("btn_capture"))
        self.solve_btn.setText(i18n.t("btn_solve_normal"))
        if not (self.main.record_worker and self.main.record_worker.isRunning()):
            self.listen_btn.setText(i18n.t("btn_solve_listening"))

    def _build_titlebar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("CompactTitleBar")
        bar.setFixedHeight(30)
        self._titlebar = bar

        row = QHBoxLayout(bar)
        row.setContentsMargins(8, 2, 4, 0)
        row.setSpacing(4)

        logo = QLabel()
        logo.setPixmap(build_app_icon().pixmap(16, 16))
        row.addWidget(logo)

        title = QLabel("SolveX")
        title.setObjectName("CompactTitle")
        row.addWidget(title)
        row.addStretch(1)

        whats_new = CaptionButton("spark", i18n.t("tip_changelog"))
        whats_new.clicked.connect(self.main.show_release_notes)
        row.addWidget(whats_new)

        tray_btn = CaptionButton("tray", i18n.t("tip_tray"))
        tray_btn.clicked.connect(self.main.minimize_to_tray)
        row.addWidget(tray_btn)

        min_btn = CaptionButton("minimize", i18n.t("btn_hide"))
        min_btn.clicked.connect(self.showMinimized)
        row.addWidget(min_btn)

        close_btn = CaptionButton("close", i18n.t("tip_tray"), close_style=True)
        close_btn.clicked.connect(self.main.minimize_to_tray)
        row.addWidget(close_btn)

        return bar

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.addAction(i18n.t("nav_changelog"), self.main.show_release_notes)
        menu.addAction(i18n.t("nav_settings"), lambda: self.main.show_tab("settings"))
        menu.addSeparator()
        menu.addAction(i18n.t("tip_tray"), self.main.minimize_to_tray)
        menu.addAction("Thoát SolveX", self.main.quit_app)
        menu.exec(event.globalPos())

    def _in_titlebar(self, pos: QPoint) -> bool:
        return self._titlebar.geometry().contains(pos)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._in_titlebar(event.position().toPoint()):
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, event):
        self._drag_offset = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        p = style.get_palette(self.main.config.get("theme", "dark"))
        painter.setPen(QPen(QColor(p["BORDER"]), 1))
        painter.setBrush(QColor(p["PANEL_SOLID"]))
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 10, 10)
        painter.end()

    def showEvent(self, event):
        super().showEvent(event)
        fluent.apply_mica(self, dark_mode=(self.main.config.get("theme", "dark") == "dark"), glass_mode=False)


# --------------------------------------------------------------------------
# Answer Window & Busy Indicator (Tích hợp Đọc Lời Giải Giọng Nói TTS)
# --------------------------------------------------------------------------
class AnswerWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SolveX — Đáp án")
        self.setWindowIcon(build_app_icon())
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.resize(640, 560)
        self.raw_markdown = ""

        layout = QVBoxLayout(self)
        self.browser = QTextBrowser()
        self.browser.setObjectName("Chat")
        self.browser.setOpenExternalLinks(True)
        layout.addWidget(self.browser, 1)

        buttons = QHBoxLayout()
        self.copy_btn = QPushButton(i18n.t("btn_copy_answer"))
        self.copy_btn.setIcon(IconFactory.draw_icon("solve", style.AMBER, 16))
        self.copy_btn.clicked.connect(self._copy_to_clipboard)
        buttons.addWidget(self.copy_btn)

        self.speak_btn = QPushButton("🔊 Đọc Lời Giải (TTS)")
        self.speak_btn.setIcon(IconFactory.draw_icon("speaker", style.TEAL, 16))
        self.speak_btn.clicked.connect(self._speak_answer)
        buttons.addWidget(self.speak_btn)

        self.save_star_btn = QPushButton("⭐ Lưu Câu Hỏi Khó")
        self.save_star_btn.setIcon(IconFactory.draw_icon("star", style.AMBER, 16))
        self.save_star_btn.clicked.connect(self._save_difficult_question)
        buttons.addWidget(self.save_star_btn)

        buttons.addStretch(1)
        close_btn = QPushButton(i18n.t("btn_close"))
        close_btn.clicked.connect(self.close)
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)

    def _save_difficult_question(self):
        parent = self.parent()
        if parent and hasattr(parent, "saved_questions_mgr"):
            title = parent._get_current_question_title()
            img_path = parent._get_current_question_img()
            parent.saved_questions_mgr.add_question(title, self.raw_markdown, img_path)
            self.save_star_btn.setText("Đã lưu ⭐")
            self.save_star_btn.setEnabled(False)

    def _copy_to_clipboard(self):
        cb = QApplication.clipboard()
        cb.setText(self.raw_markdown)
        self.copy_btn.setText("Đã sao chép! ✓")
        QTimer.singleShot(2000, lambda: self.copy_btn.setText(i18n.t("btn_copy_answer")))

    def _speak_answer(self):
        text_clean = re.sub(r'[*#_`\[\]()<=>\\]', ' ', self.raw_markdown)
        text_clean = re.sub(r'\s+', ' ', text_clean).strip()
        if not text_clean:
            return

        self.speak_btn.setEnabled(False)
        self.speak_btn.setText("Đang đọc...")

        def _tts_thread():
            try:
                if sys.platform == "win32":
                    powershell_script = f'''
                    Add-Type -AssemblyName System.Speech;
                    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer;
                    $synth.Rate = 0;
                    $synth.Speak('{text_clean[:600].replace("'", "''")}');
                    '''
                    subprocess.run(["powershell", "-Command", powershell_script], capture_output=True)
            except Exception:
                pass

        import threading
        t = threading.Thread(target=_tts_thread, daemon=True)
        t.start()

        QTimer.singleShot(4000, lambda: (self.speak_btn.setEnabled(True), self.speak_btn.setText("🔊 Đọc Lời Giải (TTS)")))

    def show_answer(self, markdown_text: str, theme: str = "dark", enable_tts: bool = True):
        self.raw_markdown = markdown_text
        self.setStyleSheet(style.get_stylesheet(theme))
        self.speak_btn.setVisible(enable_tts)
        body = render_markdown(markdown_text)
        self.browser.setHtml(wrap_html_page(body, theme))
        self.show()
        self.raise_()
        self.activateWindow()


class BusyIndicator(QWidget):
    def __init__(self, theme: str = "dark"):
        super().__init__()
        self.theme = theme
        self.setObjectName("BusyRoot")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(style.get_busy_stylesheet(theme))

        row = QHBoxLayout(self)
        row.setContentsMargins(14, 10, 14, 10)
        row.setSpacing(10)

        spinner = QProgressBar()
        spinner.setRange(0, 0)
        spinner.setFixedWidth(60)
        spinner.setTextVisible(False)
        row.addWidget(spinner)

        self.label = QLabel(i18n.t("chat_thinking"))
        self.label.setObjectName("BusyLabel")
        row.addWidget(self.label)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        p = style.get_palette(self.theme)
        painter.setPen(QPen(QColor(p["BORDER"]), 1))
        painter.setBrush(QColor(p["PANEL_SOLID"]))
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 10, 10)
        painter.end()

    def show_near(self, anchor: QWidget):
        self.adjustSize()
        if anchor is not None and anchor.isVisible():
            point = QPoint(
                anchor.geometry().center().x() - self.width() // 2,
                anchor.geometry().bottom() + 10,
            )
        else:
            screen = QGuiApplication.primaryScreen().availableGeometry()
            point = QPoint(screen.center().x() - self.width() // 2, screen.top() + 24)
        self.move(point)
        self.show()
        self.raise_()

    def set_text(self, text: str):
        self.label.setText(text)


# --------------------------------------------------------------------------
# Cửa sổ chính MainWindow (WinUI 3 Modern Friendly v1.8.0)
# --------------------------------------------------------------------------
class MainWindow(QMainWindow):
    SYSTEM_INSTRUCTION = (
        "Bạn là trợ lý học tập SolveX. Giải thích từng bước rõ ràng, chính xác. "
        "Dùng Markdown để trình bày."
    )

    def __init__(self):
        super().__init__()
        self.config = Config()
        self.history_mgr = HistoryManager()
        self.saved_questions_mgr = SavedQuestionsManager()
        self.current_session = None

        i18n.set_language(self.config.get("language", "vi"))

        self.history = []
        self.messages = []
        self.ask_worker = None
        self.capture_worker = None
        self.record_worker = None
        self.test_worker = None
        self.update_worker = None
        self.download_worker = None
        self.build_worker = None
        self.pending_shot = None
        self.record_seconds = 0

        self.setWindowTitle("SolveX")
        self.setWindowIcon(build_app_icon())
        self.resize(1200, 780)

        self._build_menu_bar()
        self._build_ui()
        self._load_config_into_ui()
        self.apply_theme(self.config.get("theme", "dark"))

        self.record_timer = QTimer(self)
        self.record_timer.timeout.connect(self._tick_record)

        self.answer_window = None
        self.busy_indicator = BusyIndicator(self.config.get("theme", "dark"))
        self.toolbar = CompactWindow(self)

        self._setup_tray()
        i18n.language_changed.connect(self.on_language_changed)

        # Khởi chạy Sentinel bảo mật chạy ngầm siêu nhẹ (<0.01% CPU, <1MB RAM)
        self.sec_sentinel = SecuritySentinel(self.config.path, self)
        self.sec_sentinel.start()

        self.on_new_chat()

    def showEvent(self, event):
        super().showEvent(event)
        is_dark = (self.config.get("theme", "dark") == "dark")
        fluent.apply_mica(self, dark_mode=is_dark, glass_mode=False)

    # ------------------ Native Menu Bar ------------------
    def _build_menu_bar(self):
        menubar = self.menuBar()
        menubar.clear()

        file_menu = menubar.addMenu(i18n.t("menu_file"))
        act_new = QAction(IconFactory.draw_icon("plus", style.TEXT, 16), i18n.t("btn_new_chat"), self)
        act_new.triggered.connect(self.on_new_chat)
        file_menu.addAction(act_new)

        act_export = QAction(IconFactory.draw_icon("guide", style.AMBER, 16), i18n.t("btn_export_hist"), self)
        act_export.triggered.connect(self.on_export_history)
        file_menu.addAction(act_export)

        act_clear_hist = QAction(IconFactory.draw_icon("trash", style.RED, 16), i18n.t("btn_clear_all"), self)
        act_clear_hist.triggered.connect(self.on_clear_history)
        file_menu.addAction(act_clear_hist)

        file_menu.addSeparator()
        act_tray = QAction(IconFactory.draw_icon("tray", style.TEXT, 16), i18n.t("tip_tray"), self)
        act_tray.triggered.connect(self.minimize_to_tray)
        file_menu.addAction(act_tray)

        act_exit = QAction(IconFactory.draw_icon("close", style.RED, 16), i18n.t("menu_exit"), self)
        act_exit.triggered.connect(self.quit_app)
        file_menu.addAction(act_exit)

        view_menu = menubar.addMenu(i18n.t("menu_view"))
        act_dark = QAction(IconFactory.draw_icon("moon", style.AMBER, 16), i18n.t("quick_theme_dark"), self)
        act_dark.triggered.connect(lambda: self.apply_theme("dark"))
        view_menu.addAction(act_dark)

        act_light = QAction(IconFactory.draw_icon("sun", style.AMBER, 16), i18n.t("quick_theme_light"), self)
        act_light.triggered.connect(lambda: self.apply_theme("light"))
        view_menu.addAction(act_light)

        act_auto = QAction(IconFactory.draw_icon("settings", style.TEAL, 16), "Tự động theo Hệ điều hành (Auto OS)", self)
        act_auto.triggered.connect(lambda: self.apply_theme("auto"))
        view_menu.addAction(act_auto)

        view_menu.addSeparator()
        act_topbar = QAction(IconFactory.draw_icon("topbar", style.TEXT, 16), i18n.t("quick_compact"), self)
        act_topbar.triggered.connect(self._toggle_toolbar)
        view_menu.addAction(act_topbar)

        lang_menu = menubar.addMenu(i18n.t("menu_language"))
        act_vi = QAction(IconFactory.draw_icon("globe", style.TEXT, 16), "Tiếng Việt", self)
        act_vi.triggered.connect(lambda: self._set_language_code("vi"))
        lang_menu.addAction(act_vi)

        act_en = QAction(IconFactory.draw_icon("globe", style.TEXT, 16), "English", self)
        act_en.triggered.connect(lambda: self._set_language_code("en"))
        lang_menu.addAction(act_en)

        set_menu = menubar.addMenu(i18n.t("menu_settings"))
        act_open_set = QAction(IconFactory.draw_icon("settings", style.TEXT, 16), i18n.t("nav_settings"), self)
        act_open_set.triggered.connect(lambda: self.show_tab("settings"))
        set_menu.addAction(act_open_set)

        act_test_key = QAction(IconFactory.draw_icon("key", style.AMBER, 16), i18n.t("btn_test_api"), self)
        act_test_key.triggered.connect(self.on_test_api_key)
        set_menu.addAction(act_test_key)

        help_menu = menubar.addMenu(i18n.t("menu_help"))
        act_guide = QAction(IconFactory.draw_icon("guide", style.TEXT, 16), i18n.t("nav_guide"), self)
        act_guide.triggered.connect(lambda: self.show_tab("guide"))
        help_menu.addAction(act_guide)

        act_change = QAction(IconFactory.draw_icon("spark", style.AMBER, 16), i18n.t("nav_changelog"), self)
        act_change.triggered.connect(self.show_release_notes)
        help_menu.addAction(act_change)

        help_menu.addSeparator()
        act_upd = QAction(IconFactory.draw_icon("update", style.TEAL, 16), i18n.t("btn_check_update"), self)
        act_upd.triggered.connect(self.on_check_update)
        help_menu.addAction(act_upd)

        act_build = QAction(IconFactory.draw_icon("settings", style.TEXT, 16), i18n.t("btn_build_exe"), self)
        act_build.triggered.connect(self.on_build_exe)
        help_menu.addAction(act_build)

    def _set_language_code(self, lang_code: str):
        i18n.set_language(lang_code)
        self.config.set("language", lang_code)
        self.config.save()
        self._load_config_into_ui()

    def apply_theme(self, theme_name: str):
        self.config.set("theme", theme_name)
        self.config.save()
        self.setStyleSheet(style.get_stylesheet(theme_name))
        if hasattr(self, "toolbar") and self.toolbar:
            self.toolbar.setStyleSheet(style.get_compact_stylesheet(theme_name))
        fluent.apply_mica(self, dark_mode=(theme_name == "dark"), glass_mode=False)
        self._load_config_into_ui()
        self._render_chat()

    def _setup_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.tray = None
            return
        self.tray = QSystemTrayIcon(build_app_icon(), self)
        self.tray.setToolTip("SolveX v" + APP_VERSION)

        menu = QMenu()
        menu.addAction("Ẩn/Hiện Top Bar Nổi", self._toggle_toolbar)
        menu.addAction(i18n.t("nav_settings"), lambda: self.show_tab("settings"))
        menu.addAction(i18n.t("nav_changelog"), self.show_release_notes)
        menu.addSeparator()
        menu.addAction("Thoát SolveX", self.quit_app)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_full_window()

    def _toggle_toolbar(self):
        if self.toolbar.isVisible():
            self.toolbar.hide()
        else:
            self.toolbar.show()
            self.toolbar.raise_()

    def minimize_to_tray(self):
        if self.toolbar.isMaximized():
            self.toolbar.showNormal()
        self.toolbar.hide()
        self.hide()

    def show_full_window(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def show_tab(self, tab_name: str):
        self.show_full_window()
        tab_map = {"chat": 0, "history": 1, "settings": 2, "guide": 3, "changelog": 4}
        idx = tab_map.get(tab_name, 0)
        self.nav_group.buttons()[idx].setChecked(True)
        self.stack.setCurrentIndex(idx)
        if tab_name == "settings":
            self._load_config_into_ui()
        elif tab_name == "history":
            self._refresh_history_list()

    def show_release_notes(self):
        self.show_tab("changelog")

    def quit_app(self):
        self._shutdown()
        QApplication.instance().quit()

    # ------------------ Xây dựng WinUI 3 UI v1.8.0 ------------------
    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("NavSidebar")
        sidebar.setFixedWidth(210)
        s_box = QVBoxLayout(sidebar)
        s_box.setContentsMargins(10, 16, 10, 16)
        s_box.setSpacing(6)

        brand_box = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(build_app_icon().pixmap(24, 24))
        logo.setStyleSheet("background: transparent;")
        brand_box.addWidget(logo)
        
        title_box = QVBoxLayout()
        brand_lbl = QLabel("SolveX")
        brand_lbl.setObjectName("Brand")
        tagline_lbl = QLabel(i18n.t("app_tagline"))
        tagline_lbl.setObjectName("Tagline")
        title_box.addWidget(brand_lbl)
        title_box.addWidget(tagline_lbl)
        brand_box.addLayout(title_box)
        s_box.addLayout(brand_box)
        s_box.addSpacing(16)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.btn_nav_chat = self._create_nav_btn("solve", i18n.t("nav_chat"), 0)
        self.btn_nav_hist = self._create_nav_btn("history", i18n.t("nav_history"), 1)
        self.btn_nav_set = self._create_nav_btn("settings", i18n.t("nav_settings"), 2)
        self.btn_nav_guide = self._create_nav_btn("guide", i18n.t("nav_guide"), 3)
        self.btn_nav_change = self._create_nav_btn("spark", i18n.t("nav_changelog"), 4)

        s_box.addWidget(self.btn_nav_chat)
        s_box.addWidget(self.btn_nav_hist)
        s_box.addWidget(self.btn_nav_set)
        s_box.addWidget(self.btn_nav_guide)
        s_box.addWidget(self.btn_nav_change)
        s_box.addStretch(1)

        layout.addWidget(sidebar)

        right_container = QWidget()
        r_layout = QVBoxLayout(right_container)
        r_layout.setContentsMargins(0, 0, 0, 0)
        r_layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("HeaderBar")
        header.setFixedHeight(40)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(16, 4, 16, 4)
        h_layout.setSpacing(10)

        page_title = QLabel("SolveX v" + APP_VERSION)
        page_title.setStyleSheet("font-weight:600; font-size:13px; background:transparent; color:" + style.MUTED + ";")
        h_layout.addWidget(page_title)
        h_layout.addStretch(1)

        r_layout.addWidget(header)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_chat_page())
        self.stack.addWidget(self._build_history_page())
        self.stack.addWidget(self._build_settings_page())
        self.stack.addWidget(self._build_guide_page())
        self.stack.addWidget(self._build_changelog_page())
        r_layout.addWidget(self.stack, 1)

        layout.addWidget(right_container, 1)
        self.btn_nav_chat.setChecked(True)

        self.status = self.statusBar()
        self.status.showMessage(i18n.t("status_ready"))

        QShortcut(QKeySequence("F2"), self, self.on_solve_normal)
        QShortcut(QKeySequence("F3"), self, self.on_listening_clicked)
        QShortcut(QKeySequence("Ctrl+Return"), self, self.on_send_chat)

    def _create_nav_btn(self, icon_name: str, text: str, index: int) -> QPushButton:
        btn = QPushButton(f"  {text}")
        btn.setObjectName("NavBtn")
        btn.setCheckable(True)
        btn.setIcon(IconFactory.draw_icon(icon_name, style.MUTED, 18))
        self.nav_group.addButton(btn, index)
        btn.clicked.connect(lambda: self.stack.setCurrentIndex(index))
        return btn

    # Tab 1: Chat Page
    def _build_chat_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        top_card = QFrame()
        top_card.setObjectName("Card")
        t_row = QHBoxLayout(top_card)
        t_row.setContentsMargins(12, 10, 12, 10)
        t_row.setSpacing(10)

        self.btn_solve_main = QPushButton(i18n.t("btn_solve_normal") + " (F2)")
        self.btn_solve_main.setObjectName("Solve")
        self.btn_solve_main.setIcon(IconFactory.draw_icon("solve", "#ffffff", 18))
        self.btn_solve_main.clicked.connect(self.on_solve_normal)
        t_row.addWidget(self.btn_solve_main)

        self.btn_listen_main = QPushButton(i18n.t("btn_solve_listening") + " (F3)")
        self.btn_listen_main.setObjectName("Listen")
        self.btn_listen_main.setIcon(IconFactory.draw_icon("headphones", "#ffffff", 18))
        self.btn_listen_main.clicked.connect(self.on_listening_clicked)
        t_row.addWidget(self.btn_listen_main)

        self.btn_capture_main = QPushButton(i18n.t("btn_pick_region"))
        self.btn_capture_main.setIcon(IconFactory.draw_icon("camera", style.TEXT, 16))
        self.btn_capture_main.clicked.connect(self.on_pick_region)
        t_row.addWidget(self.btn_capture_main)

        t_row.addSpacing(10)
        mode_lbl = QLabel(i18n.t("mode_label"))
        mode_lbl.setStyleSheet("background:transparent; font-weight:600;")
        t_row.addWidget(mode_lbl)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem(i18n.t("mode_step"), "step")
        self.mode_combo.addItem(i18n.t("mode_mcq"), "mcq")
        self.mode_combo.addItem(i18n.t("mode_similar"), "similar")
        self.mode_combo.addItem(i18n.t("mode_concept"), "concept")
        self.mode_combo.setMinimumWidth(180)
        self.mode_combo.currentIndexChanged.connect(self._sync_mode_from_main)
        t_row.addWidget(self.mode_combo)

        t_row.addStretch(1)

        new_btn = QPushButton(i18n.t("btn_new_chat"))
        new_btn.setIcon(IconFactory.draw_icon("plus", style.TEXT, 16))
        new_btn.clicked.connect(self.on_new_chat)
        t_row.addWidget(new_btn)

        layout.addWidget(top_card)

        self.level_bar = QProgressBar()
        self.level_bar.setRange(0, 100)
        self.level_bar.setTextVisible(False)
        self.level_bar.setVisible(False)
        layout.addWidget(self.level_bar)

        self.record_label = QLabel("")
        self.record_label.setStyleSheet(f"color:{style.RED}; font-weight:bold;")
        self.record_label.setVisible(False)
        layout.addWidget(self.record_label)

        self.chat = QTextBrowser()
        self.chat.setObjectName("Chat")
        self.chat.setOpenExternalLinks(True)
        layout.addWidget(self.chat, 1)

        input_row = QHBoxLayout()
        self.chat_input = QPlainTextEdit()
        self.chat_input.setPlaceholderText(i18n.t("chat_input_ph"))
        self.chat_input.setFixedHeight(72)
        input_row.addWidget(self.chat_input, 1)

        self.send_btn = QPushButton(i18n.t("btn_send"))
        self.send_btn.setObjectName("Send")
        self.send_btn.setFixedWidth(84)
        self.send_btn.setFixedHeight(72)
        self.send_btn.clicked.connect(self.on_send_chat)
        input_row.addWidget(self.send_btn)

        layout.addLayout(input_row)
        return page

    def _sync_mode_from_main(self, index: int):
        if hasattr(self, "toolbar") and self.toolbar:
            self.toolbar.sync_mode_from_main(index)

    # Tab 2: History Page
    def _build_history_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        header_row = QHBoxLayout()
        title = QLabel(i18n.t("hist_title"))
        title.setObjectName("Brand")
        header_row.addWidget(title)

        header_row.addSpacing(12)
        self.hist_mode_btn_all = QPushButton("🕒 Lịch Sử Trò Chuyện")
        self.hist_mode_btn_saved = QPushButton("⭐ Câu Hỏi Khó Saved")
        self.hist_mode_btn_all.setCheckable(True)
        self.hist_mode_btn_saved.setCheckable(True)
        self.hist_mode_btn_all.setChecked(True)

        self.hist_filter_group = QButtonGroup(self)
        self.hist_filter_group.addButton(self.hist_mode_btn_all, 0)
        self.hist_filter_group.addButton(self.hist_mode_btn_saved, 1)
        self.hist_filter_group.idClicked.connect(lambda: self._refresh_history_list())

        header_row.addWidget(self.hist_mode_btn_all)
        header_row.addWidget(self.hist_mode_btn_saved)
        header_row.addStretch(1)

        self.hist_search_input = QLineEdit()
        self.hist_search_input.setPlaceholderText(i18n.t("hist_search_ph"))
        self.hist_search_input.setFixedWidth(200)
        self.hist_search_input.textChanged.connect(self._filter_history_list)
        header_row.addWidget(self.hist_search_input)

        export_btn = QPushButton(i18n.t("btn_export_hist"))
        export_btn.setIcon(IconFactory.draw_icon("guide", style.AMBER, 16))
        export_btn.clicked.connect(self.on_export_history)
        header_row.addWidget(export_btn)

        clear_btn = QPushButton(i18n.t("btn_clear_all"))
        clear_btn.setIcon(IconFactory.draw_icon("trash", style.RED, 16))
        clear_btn.clicked.connect(self.on_clear_history)
        header_row.addWidget(clear_btn)
        layout.addLayout(header_row)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.hist_list = QListWidget()
        self.hist_list.itemClicked.connect(self.on_history_item_clicked)
        splitter.addWidget(self.hist_list)

        self.hist_preview = QTextBrowser()
        self.hist_preview.setObjectName("Chat")
        splitter.addWidget(self.hist_preview)
        splitter.setSizes([300, 600])

        layout.addWidget(splitter, 1)
        return page

    # Tab 3: Settings Page
    def _build_settings_page(self) -> QWidget:
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        box = QVBoxLayout(content)
        box.setContentsMargins(20, 16, 20, 20)
        box.setSpacing(16)

        box.addWidget(self._section_lbl("st_section_general"))
        gen_card = QFrame()
        gen_card.setObjectName("Card")
        g_layout = QVBoxLayout(gen_card)

        g_layout.addWidget(QLabel(i18n.t("st_theme")))
        theme_row = QHBoxLayout()
        self.theme_group = QButtonGroup(self)

        self.theme_dark_rad = QRadioButton(i18n.t("st_theme_dark"))
        self.theme_light_rad = QRadioButton(i18n.t("st_theme_light"))
        self.theme_auto_rad = QRadioButton("💻 Tự động theo Hệ điều hành (Auto OS)")

        self.theme_group.addButton(self.theme_dark_rad, 0)
        self.theme_group.addButton(self.theme_light_rad, 1)
        self.theme_group.addButton(self.theme_auto_rad, 2)

        self.theme_dark_rad.toggled.connect(self._on_live_theme_changed)
        self.theme_light_rad.toggled.connect(self._on_live_theme_changed)
        self.theme_auto_rad.toggled.connect(self._on_live_theme_changed)

        theme_row.addWidget(self.theme_dark_rad)
        theme_row.addWidget(self.theme_light_rad)
        theme_row.addWidget(self.theme_auto_rad)
        theme_row.addStretch(1)
        g_layout.addLayout(theme_row)
        g_layout.addSpacing(10)

        g_layout.addWidget(QLabel(i18n.t("st_language")))
        lang_row = QHBoxLayout()
        self.lang_group = QButtonGroup(self)

        self.lang_vi = QRadioButton("Tiếng Việt")
        self.lang_en = QRadioButton("English")

        self.lang_group.addButton(self.lang_vi, 0)
        self.lang_group.addButton(self.lang_en, 1)

        self.lang_vi.toggled.connect(self._on_live_lang_changed)
        self.lang_en.toggled.connect(self._on_live_lang_changed)

        lang_row.addWidget(self.lang_vi)
        lang_row.addWidget(self.lang_en)
        lang_row.addStretch(1)
        g_layout.addLayout(lang_row)

        g_layout.addSpacing(10)
        g_layout.addWidget(QLabel(i18n.t("st_startup_mode")))
        self.start_combo = QComboBox()
        self.start_combo.addItem(i18n.t("st_startup_full"), "full")
        self.start_combo.addItem(i18n.t("st_startup_compact"), "compact")
        self.start_combo.addItem(i18n.t("st_startup_tray"), "tray")
        g_layout.addWidget(self.start_combo)

        g_layout.addSpacing(10)
        self.enable_tts_check = QCheckBox("🔊 Bật nút đọc đáp án bằng giọng nói (TTS Reader)")
        self.auto_tts_check = QCheckBox("⚡ Tự động đọc đáp án ngay khi AI hoàn tất lời giải")
        g_layout.addWidget(self.enable_tts_check)
        g_layout.addWidget(self.auto_tts_check)

        box.addWidget(gen_card)

        box.addWidget(self._section_lbl("st_section_api"))
        api_card = QFrame()
        api_card.setObjectName("Card")
        a_layout = QVBoxLayout(api_card)
        a_layout.setSpacing(10)

        # Chế độ chạy Model AI (Standard / Turbo / Turbo+)
        a_layout.addWidget(QLabel("⚡ Chế độ AI (Model Execution Mode):"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("⚡ Standard (1 Model AI — Tiêu Chuẩn)", "standard")
        self.mode_combo.addItem("🔥 Turbo (Song Song 2 Model AI Đối Chiếu)", "turbo")
        self.mode_combo.addItem("🚀 Turbo+ (Dual-Model AI Kiểm Chứng & Tối Ưu Tận Cùng)", "turbo_plus")
        self.mode_combo.currentIndexChanged.connect(self._on_model_mode_changed)
        a_layout.addWidget(self.mode_combo)

        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        a_layout.addWidget(line1)

        # Cấu hình Model 1 (Model Chính)
        lbl_m1 = QLabel("🤖 Cấu Hình Model 1 (Model AI Chính):")
        lbl_m1.setStyleSheet("font-weight: bold;")
        a_layout.addWidget(lbl_m1)

        a_layout.addWidget(QLabel(i18n.t("st_api_key")))
        key_row = QHBoxLayout()
        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setPlaceholderText(i18n.t("st_api_key_ph"))
        key_row.addWidget(self.key_input, 1)

        self.show_key = QPushButton(i18n.t("btn_show"))
        self.show_key.setCheckable(True)
        self.show_key.toggled.connect(self._toggle_key_visibility)
        key_row.addWidget(self.show_key)

        self.test_api_btn = QPushButton(i18n.t("btn_test_api"))
        self.test_api_btn.clicked.connect(self.on_test_api_key)
        key_row.addWidget(self.test_api_btn)
        a_layout.addLayout(key_row)

        a_layout.addWidget(QLabel(i18n.t("st_model")))
        self.model_input = QLineEdit()
        a_layout.addWidget(self.model_input)

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        a_layout.addWidget(line2)

        # Cấu hình Model 2 (Dùng cho Turbo / Turbo+)
        self.lbl_m2 = QLabel("🤖 Cấu Hình Model 2 (Dùng Cho Chế Độ Turbo & Turbo+):")
        self.lbl_m2.setStyleSheet("font-weight: bold; color: #0ea5e9;")
        a_layout.addWidget(self.lbl_m2)

        key2_opt_layout = QHBoxLayout()
        self.key2_same_rad = QRadioButton("Dùng chung API Key cũ với Model 1")
        self.key2_sep_rad = QRadioButton("Dùng API Key riêng biệt cho Model 2")
        self.key2_same_rad.setChecked(True)
        self.key2_same_rad.toggled.connect(self._toggle_key2_enabled)
        self.key2_sep_rad.toggled.connect(self._toggle_key2_enabled)
        key2_opt_layout.addWidget(self.key2_same_rad)
        key2_opt_layout.addWidget(self.key2_sep_rad)
        key2_opt_layout.addStretch()
        a_layout.addLayout(key2_opt_layout)

        a_layout.addWidget(QLabel("API Key riêng biệt cho Model 2:"))
        key2_row = QHBoxLayout()
        self.key2_input = QLineEdit()
        self.key2_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key2_input.setPlaceholderText("Dán API Key riêng cho Model 2 tại đây...")
        key2_row.addWidget(self.key2_input, 1)

        self.show_key2 = QPushButton("Hiện")
        self.show_key2.setCheckable(True)
        self.show_key2.toggled.connect(self._toggle_key2_visibility)
        key2_row.addWidget(self.show_key2)

        self.test_api2_btn = QPushButton("Kiểm Tra Model 2")
        self.test_api2_btn.clicked.connect(self.on_test_api_key_2)
        key2_row.addWidget(self.test_api2_btn)
        a_layout.addLayout(key2_row)

        a_layout.addWidget(QLabel("Tên Model 2 (Nhập y hệt cách làm như model cũ, e.g. gemini-2.5-pro):"))
        self.model2_input = QLineEdit()
        self.model2_input.setPlaceholderText("gemini-2.5-pro")
        a_layout.addWidget(self.model2_input)

        box.addWidget(api_card)

        box.addWidget(self._section_lbl("st_section_capture"))
        cap_card = QFrame()
        cap_card.setObjectName("Card")
        c_layout = QVBoxLayout(cap_card)

        c_layout.addWidget(QLabel(i18n.t("st_capture_source")))
        self.monitor_combo = QComboBox()
        self._populate_monitors()
        self.monitor_combo.currentIndexChanged.connect(self._on_source_changed)
        c_layout.addWidget(self.monitor_combo)

        self.hide_check = QCheckBox(i18n.t("st_hide_on_capture"))
        c_layout.addWidget(self.hide_check)

        self.loopback_check = QCheckBox(i18n.t("st_loopback"))
        c_layout.addWidget(self.loopback_check)

        box.addWidget(cap_card)

        box.addWidget(self._section_lbl("st_section_prompts"))
        prompt_card = QFrame()
        prompt_card.setObjectName("Card")
        p_layout = QVBoxLayout(prompt_card)

        p_layout.addWidget(QLabel(i18n.t("st_prompt_normal_lbl")))
        self.prompt_normal_edit = QPlainTextEdit()
        self.prompt_normal_edit.setFixedHeight(90)
        p_layout.addWidget(self.prompt_normal_edit)

        p_layout.addWidget(QLabel(i18n.t("st_prompt_listen_lbl")))
        self.prompt_listen_edit = QPlainTextEdit()
        self.prompt_listen_edit.setFixedHeight(90)
        p_layout.addWidget(self.prompt_listen_edit)

        box.addWidget(prompt_card)

        box.addWidget(self._section_lbl("st_section_update"))
        upd_card = QFrame()
        upd_card.setObjectName("Card")
        u_layout = QVBoxLayout(upd_card)

        u_row = QHBoxLayout()
        chk_upd_btn = QPushButton(i18n.t("btn_check_update"))
        chk_upd_btn.setIcon(IconFactory.draw_icon("update", style.TEAL, 16))
        chk_upd_btn.clicked.connect(self.on_check_update)
        u_row.addWidget(chk_upd_btn)

        build_exe_btn = QPushButton(i18n.t("btn_build_exe"))
        build_exe_btn.setIcon(IconFactory.draw_icon("settings", style.TEXT, 16))
        build_exe_btn.clicked.connect(self.on_build_exe)
        u_row.addWidget(build_exe_btn)
        u_layout.addLayout(u_row)

        box.addWidget(upd_card)

        save_row = QHBoxLayout()
        save_row.addStretch(1)
        save_btn = QPushButton(i18n.t("btn_save"))
        save_btn.setObjectName("PrimaryBtn")
        save_btn.clicked.connect(self.on_save_settings)
        save_row.addWidget(save_btn)
        box.addLayout(save_row)

        scroll.setWidget(content)
        p_layout_outer = QVBoxLayout(page)
        p_layout_outer.setContentsMargins(0, 0, 0, 0)
        p_layout_outer.addWidget(scroll)
        return page

    def _on_live_theme_changed(self):
        if self.theme_auto_rad.isChecked():
            theme = "auto"
        elif self.theme_light_rad.isChecked():
            theme = "light"
        else:
            theme = "dark"
        self.apply_theme(theme)

    def _on_live_lang_changed(self):
        lang = "en" if self.lang_en.isChecked() else "vi"
        self._set_language_code(lang)

    # Tab 4: Guide Page
    def _build_guide_page(self) -> QWidget:
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        box = QVBoxLayout(content)
        box.setContentsMargins(20, 16, 20, 20)
        box.setSpacing(16)

        title = QLabel(i18n.t("guide_title"))
        title.setObjectName("Brand")
        box.addWidget(title)

        steps = [
            ("1. Nhập API Key Google Gemini (Miễn Phí)", "Vào Cài đặt -> Dán API Key lấy từ Google AI Studio (aistudio.google.com). Bấm 'Kiểm tra kết nối API Key' để xác nhận AI đã hoạt động.", "key"),
            ("2. Chụp & Giải Bài Thường Siêu Tốc (Phím F2)", "Bấm nút [Giải bài] hoặc nhấn phím F2. SolveX tự động ẩn đi, cho phép bạn kéo chọn vùng câu hỏi trên màn hình và nhận lời giải chi tiết từng bước.", "solve"),
            ("3. Giải Bài Nghe Tiếng Anh (Phím F3)", "Nhấn F3 để vừa chụp hình câu hỏi vừa thu âm đoạn hội thoại tiếng Anh. Bấm F3 lần nữa để kết thúc thu âm và nhận lời giải chính xác.", "headphones"),
            ("4. Chọn Chế Độ Học Tập Tối Ưu (Study Modes)", "Chọn từ bộ thả xuống [Chế độ giải bài] trên giao diện chính hoặc thanh Top Bar nổi: Giải chi tiết từng bước, Trắc nghiệm siêu tốc, Tạo bài tập tương tự, hoặc Giải thích lý thuyết.", "camera"),
            ("5. Xuất Lịch Sử Giải Bài Ra File Markdown (.md)", "Vào tab Lịch sử trò chuyện -> Bấm nút [Xuất File Markdown] để lưu toàn bộ danh sách câu hỏi và lời giải chi tiết ra file dạng .md hoặc .txt tiện cho việc in ấn.", "guide"),
        ]

        for st_title, st_desc, icon_name in steps:
            card = QFrame()
            card.setObjectName("Card")
            c_box = QHBoxLayout(card)
            ic_lbl = QLabel()
            ic_lbl.setPixmap(IconFactory.draw_icon(icon_name, style.AMBER, 32).pixmap(32, 32))
            c_box.addWidget(ic_lbl)
            text_box = QVBoxLayout()
            lbl_t = QLabel(st_title)
            lbl_t.setStyleSheet("font-size:15px; font-weight:bold; background:transparent;")
            lbl_d = QLabel(st_desc)
            lbl_d.setWordWrap(True)
            lbl_d.setStyleSheet("background:transparent;")
            text_box.addWidget(lbl_t)
            text_box.addWidget(lbl_d)
            c_box.addLayout(text_box, 1)
            box.addWidget(card)

        sc_card = QFrame()
        sc_card.setObjectName("Card")
        sc_layout = QVBoxLayout(sc_card)
        sc_title = QLabel(i18n.t("guide_shortcuts"))
        sc_title.setStyleSheet("font-size:15px; font-weight:bold; background:transparent; color:" + style.AMBER + ";")
        sc_layout.addWidget(sc_title)
        sc_layout.addWidget(QLabel(i18n.t("guide_sc_f2")))
        sc_layout.addWidget(QLabel(i18n.t("guide_sc_f3")))
        sc_layout.addWidget(QLabel(i18n.t("guide_sc_ctrl_enter")))
        box.addWidget(sc_card)

        scroll.setWidget(content)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        return page

    # Tab 5: Changelog Page
    def _build_changelog_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(14, 14, 14, 14)
        browser = QTextBrowser()
        browser.setObjectName("Chat")
        browser.setOpenExternalLinks(True)
        browser.setHtml(f"<style>{style.get_chat_css(self.config.get('theme', 'dark'))}</style>{render_markdown(changelog_markdown())}")
        layout.addWidget(browser)
        return page

    def _section_lbl(self, i18n_key: str) -> QLabel:
        lbl = QLabel(i18n.t(i18n_key))
        lbl.setObjectName("SectionLabel")
        return lbl

    # ------------------ Quản lý Config UI ------------------
    def _populate_monitors(self):
        self.monitor_combo.clear()
        try:
            monitors = capture.list_monitors()
        except Exception:
            monitors = []
        if len(monitors) > 1:
            for index, mon in enumerate(monitors[1:], start=1):
                self.monitor_combo.addItem(
                    f"{i18n.t('st_monitor_num', index)} ({mon['width']}×{mon['height']})", index
                )
        else:
            self.monitor_combo.addItem(i18n.t("st_monitor_primary"), 1)
        if len(monitors) > 2:
            self.monitor_combo.addItem(i18n.t("st_monitor_all"), 0)
        self.monitor_combo.addItem(i18n.t("st_monitor_region"), -1)

    def _load_config_into_ui(self):
        self.key_input.setText(self.config.get("api_key", ""))
        self.model_input.setText(self.config.get("model", ""))
        self.hide_check.setChecked(bool(self.config.get("hide_window_on_capture", True)))
        self.loopback_check.setChecked(bool(self.config.get("use_loopback", False)))
        self.prompt_normal_edit.setPlainText(self.config.get("prompt_normal", ""))
        self.prompt_listen_edit.setPlainText(self.config.get("prompt_listening", ""))

        theme = self.config.get("theme", "dark")
        if theme == "auto":
            self.theme_auto_rad.setChecked(True)
        elif theme == "light":
            self.theme_light_rad.setChecked(True)
        else:
            self.theme_dark_rad.setChecked(True)

        lang = self.config.get("language", "vi")
        if lang == "en":
            self.lang_en.setChecked(True)
        else:
            self.lang_vi.setChecked(True)

        mode = self.config.get("startup_mode", "compact")
        idx = self.start_combo.findData(mode)
        if idx >= 0:
            self.start_combo.setCurrentIndex(idx)

        self.enable_tts_check.setChecked(bool(self.config.get("enable_tts", True)))
        self.auto_tts_check.setChecked(bool(self.config.get("auto_tts", False)))

        model_mode = self.config.get("model_mode", "standard")
        idx_m = self.mode_combo.findData(model_mode)
        if idx_m >= 0:
            self.mode_combo.setCurrentIndex(idx_m)

        use_sep = bool(self.config.get("use_separate_api_key_2", False))
        if use_sep:
            self.key2_sep_rad.setChecked(True)
        else:
            self.key2_same_rad.setChecked(True)

        self.key2_input.setText(self.config.get("api_key_2", ""))
        self.model2_input.setText(self.config.get("model_2", "gemini-2.5-pro"))
        self._toggle_key2_enabled()
        self._on_model_mode_changed()

    def _on_source_changed(self):
        if self.monitor_combo.currentData() == -1:
            self.config.set("capture_mode", "region")
        else:
            self.config.set("capture_mode", "monitor")
            self.config.set("monitor_index", self.monitor_combo.currentData())

    def _toggle_key_visibility(self, shown: bool):
        self.key_input.setEchoMode(
            QLineEdit.EchoMode.Normal if shown else QLineEdit.EchoMode.Password
        )
        self.show_key.setText(i18n.t("btn_hide") if shown else i18n.t("btn_show"))

    def _toggle_key2_enabled(self):
        use_sep = self.key2_sep_rad.isChecked()
        self.key2_input.setEnabled(use_sep)
        self.show_key2.setEnabled(use_sep)

    def _toggle_key2_visibility(self, shown: bool):
        self.key2_input.setEchoMode(
            QLineEdit.EchoMode.Normal if shown else QLineEdit.EchoMode.Password
        )
        self.show_key2.setText("Ẩn" if shown else "Hiện")

    def _on_model_mode_changed(self):
        # Cho phép người dùng chỉnh sửa thông tin Model 2 (tên model, key riêng) bất cứ lúc nào
        self.lbl_m2.setEnabled(True)
        self.key2_same_rad.setEnabled(True)
        self.key2_sep_rad.setEnabled(True)
        self.model2_input.setEnabled(True)
        self.test_api2_btn.setEnabled(True)
        self._toggle_key2_enabled()

    def on_language_changed(self, lang_code: str):
        self._build_menu_bar()
        self.btn_nav_chat.setText(f"  {i18n.t('nav_chat')}")
        self.btn_nav_hist.setText(f"  {i18n.t('nav_history')}")
        self.btn_nav_set.setText(f"  {i18n.t('nav_settings')}")
        self.btn_nav_guide.setText(f"  {i18n.t('nav_guide')}")
        self.btn_nav_change.setText(f"  {i18n.t('nav_changelog')}")

        self.btn_solve_main.setText(i18n.t("btn_solve_normal") + " (F2)")
        self.btn_listen_main.setText(i18n.t("btn_solve_listening") + " (F3)")
        self.btn_capture_main.setText(i18n.t("btn_pick_region"))

        self._render_chat()

    def on_save_settings(self):
        if self.theme_auto_rad.isChecked():
            theme = "auto"
        elif self.theme_light_rad.isChecked():
            theme = "light"
        else:
            theme = "dark"
        self.apply_theme(theme)

        lang = "en" if self.lang_en.isChecked() else "vi"
        i18n.set_language(lang)
        self.config.set("language", lang)
        self.config.set("startup_mode", self.start_combo.currentData())

        self.config.set("enable_tts", self.enable_tts_check.isChecked())
        self.config.set("auto_tts", self.auto_tts_check.isChecked())

        self.config.set("api_key", self.key_input.text().strip())
        self.config.set("model", self.model_input.text().strip())
        self.config.set("model_mode", self.mode_combo.currentData())
        self.config.set("use_separate_api_key_2", self.key2_sep_rad.isChecked())
        self.config.set("api_key_2", self.key2_input.text().strip())
        self.config.set("model_2", self.model2_input.text().strip() or "gemini-2.5-pro")

        self.config.set("hide_window_on_capture", self.hide_check.isChecked())
        self.config.set("use_loopback", self.loopback_check.isChecked())
        self.config.set("prompt_normal", self.prompt_normal_edit.toPlainText().strip())
        self.config.set("prompt_listening", self.prompt_listen_edit.toPlainText().strip())

        self._on_source_changed()
        self.config.save()
        self.status.showMessage("Đã lưu cài đặt thành công.", 4000)

    def on_test_api_key_2(self):
        use_sep = self.key2_sep_rad.isChecked()
        key = self.key2_input.text().strip() if use_sep else self.key_input.text().strip()
        model = self.model2_input.text().strip() or "gemini-2.5-pro"
        if not key:
            self._error("Lỗi Model 2", "Vui lòng nhập API Key cho Model 2 trước khi kiểm tra.")
            return

        self.test_api2_btn.setEnabled(False)
        self.status.showMessage("Đang kiểm tra kết nối API Model 2...")

        client = GeminiClient(key, model)
        self.test_worker_2 = TestApiWorker(client)
        self.test_worker_2.succeeded.connect(
            lambda txt: (
                self.test_api2_btn.setEnabled(True),
                QMessageBox.information(self, "SolveX", f"Kết nối Model 2 ({model}) thành công!"),
                self.status.showMessage("Kết nối Model 2 thành công!", 5000),
            )
        )
        self.test_worker_2.failed.connect(
            lambda err: (
                self.test_api2_btn.setEnabled(True),
                self._error("Lỗi API Model 2", f"Kết nối Model 2 thất bại: {err}"),
            )
        )
        self.test_worker_2.start()

    def on_test_api_key(self):
        key = self.key_input.text().strip()
        model = self.model_input.text().strip()
        if not key:
            self._error("Lỗi", "Vui lòng nhập API Key trước khi kiểm tra.")
            return

        self.test_api_btn.setEnabled(False)
        self.status.showMessage(i18n.t("st_testing"))

        client = GeminiClient(key, model)
        self.test_worker = TestApiWorker(client)
        self.test_worker.succeeded.connect(self._on_test_api_success)
        self.test_worker.failed.connect(self._on_test_api_failed)
        self.test_worker.start()

    def _on_test_api_success(self, text: str):
        self.test_api_btn.setEnabled(True)
        QMessageBox.information(self, "SolveX", i18n.t("st_test_success"))
        self.status.showMessage(i18n.t("st_test_success"), 5000)

    def _on_test_api_failed(self, err: str):
        self.test_api_btn.setEnabled(True)
        self._error("Lỗi API Key", i18n.t("st_test_failed") + err)

    # ------------------ Kiểm Tra & Tải Cập Nhật Qua Ứng Dụng Độc Lập (v1.9.0) ------------------
    def on_check_update(self):
        """Mở ứng dụng kiểm tra cập nhật độc lập update.exe (v1.9.0)."""
        self.status.showMessage("Đang mở trình kiểm tra cập nhật độc lập SolveX Updater (update.exe)...")
        ok = launch_standalone_updater(APP_VERSION)
        if ok:
            self.status.showMessage("Đã mở trình kiểm tra cập nhật độc lập SolveX Updater (update.exe).", 5000)
        else:
            self._error("Lỗi Khởi Chạy", "Không thể mở ứng dụng cập nhật độc lập update.exe!")

    def _on_up_to_date(self, ver: str):
        msg = i18n.t("st_latest_ver", ver)
        QMessageBox.information(self, "SolveX GitHub Update", msg)
        self.status.showMessage(msg, 5000)

    def _on_update_available(self, ver: str, changelog: str, url: str):
        reply = QMessageBox.question(
            self,
            "SolveX — Có Phiên Bản Mới!",
            f"Đã có phiên bản mới SolveX v{ver} trên GitHub!\n\n"
            f"Nhật ký cập nhật:\n{changelog}\n\n"
            f"Bạn có muốn tải bản mới về máy ngay bây giờ không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._start_direct_download(ver, url)

    def _start_direct_download(self, ver: str, url: str):
        self.progress_dlg = UpdateProgressDialog(self)
        self.download_worker = DownloadUpdateWorker(url, f"SolveX_v{ver}.exe")

        self.progress_dlg.cancel_btn.clicked.connect(self._cancel_download)
        self.download_worker.progress_signal.connect(self.progress_dlg.update_progress)
        self.download_worker.download_finished.connect(self._on_download_finished)
        self.download_worker.no_asset_found.connect(self._on_no_asset_found)
        self.download_worker.failed.connect(self._on_download_failed)

        self.download_worker.start()
        self.progress_dlg.exec()

    def _cancel_download(self):
        if self.download_worker:
            self.download_worker.cancel()
        if hasattr(self, "progress_dlg"):
            self.progress_dlg.close()

    def _on_no_asset_found(self, web_url: str):
        if hasattr(self, "progress_dlg"):
            self.progress_dlg.close()

        reply = QMessageBox.question(
            self,
            "SolveX — GitHub Update",
            "Phiên bản mới đã có trên GitHub! Hiện chưa có file .exe đóng gói trên Releases Assets.\n\n"
            "Bạn có muốn mở trang GitHub Repository để xem mã nguồn mới hoặc tự động đóng gói (Build .exe) ngay trên máy không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            import webbrowser
            webbrowser.open(web_url)

    def _on_download_failed(self, err: str):
        if hasattr(self, "progress_dlg"):
            self.progress_dlg.close()
        self._error("Lỗi Tải Cập Nhật", err)

    def _on_download_finished(self, saved_file_path: str):
        if hasattr(self, "progress_dlg"):
            self.progress_dlg.close()

        reply = QMessageBox.question(
            self,
            "Tải Hoàn Tất — SolveX",
            f"Đã tải thành công file cài đặt mới tại:\n{saved_file_path}\n\n"
            f"Khi xác nhận cài đặt, ứng dụng sẽ kích hoạt kịch bản build.bat và tự đóng SolveX ngay lập tức để tiến trình build diễn ra mượt mà.\n\n"
            f"Bạn có muốn kích hoạt cài đặt phiên bản mới ngay bây giờ không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                build_bat = os.path.join(project_dir, "build.bat")
                if not os.path.exists(build_bat):
                    with open(build_bat, "w", encoding="utf-8") as f:
                        f.write(
                            "@echo off\ntitle SolveX Auto Update Build\n"
                            "echo Stopping old SolveX...\ntaskkill /F /IM SolveX.exe 2>nul\n"
                            "timeout /t 1 /nobreak >nul\n"
                            ".venv\\Scripts\\python.exe -m PyInstaller --noconfirm --clean solvex.spec\n"
                            "start \"\" dist\\SolveX.exe\n"
                        )

                if sys.platform == "win32":
                    subprocess.Popen(["cmd.exe", "/c", build_bat], creationflags=subprocess.CREATE_NEW_CONSOLE, cwd=project_dir)
                else:
                    subprocess.Popen([saved_file_path])
                self.quit_app()
            except Exception as exc:
                self._error("Khởi Chạy Cài Đặt Lỗi", f"Không thể kích hoạt kịch bản build.bat: {exc}")

    def on_build_exe(self):
        builder_script = _resource_path("solvex", "builder.py")
        if not os.path.exists(builder_script):
            builder_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "builder.py")

        try:
            if sys.platform == "win32":
                subprocess.Popen(
                    [sys.executable, builder_script],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                subprocess.Popen([sys.executable, builder_script])
            self.status.showMessage("Đã khởi chạy tiến trình SolveX Builder độc lập!", 5000)
            QMessageBox.information(
                self,
                "SolveX Standalone Builder",
                "Đã mở cửa sổ SolveX Builder độc lập!\n\n"
                "Tiến trình đóng gói file SolveX.exe đang tự chạy trong cửa sổ mới. "
                "Bạn có thể thoải mái sử dụng hoặc đóng SolveX mà không làm gián đoạn quá trình Build."
            )
        except Exception as exc:
            self._error("Lỗi Khởi Chạy Builder", str(exc))

    def _client(self) -> DualGeminiClient:
        key1 = self.key_input.text().strip() or self.config.get("api_key", "").strip()
        model1 = self.model_input.text().strip() or self.config.get("model", "gemini-3.5-flash-lite").strip()
        temp = float(self.config.get("temperature", 0.2))
        client1 = GeminiClient(key1, model1, temp)

        mode = self.mode_combo.currentData() if hasattr(self, "mode_combo") else self.config.get("model_mode", "standard")

        if mode in ("turbo", "turbo_plus"):
            use_sep = self.key2_sep_rad.isChecked() if hasattr(self, "key2_sep_rad") else self.config.get("use_separate_api_key_2", False)
            key2_val = self.key2_input.text().strip() if hasattr(self, "key2_input") else self.config.get("api_key_2", "")
            key2 = key2_val if use_sep and key2_val else key1
            model2_val = self.model2_input.text().strip() if hasattr(self, "model2_input") else self.config.get("model_2", "gemini-2.5-pro")
            model2 = model2_val or "gemini-2.5-pro"
            client2 = GeminiClient(key2, model2, temp)
            return DualGeminiClient(client1, client2, mode=mode)

        return DualGeminiClient(client1, None, mode="standard")

    # ------------------ Ẩn Cửa Sổ Khi Chụp Màn Hình ------------------
    def on_pick_region(self):
        hidden = self._hide_for_capture()
        self.selector = RegionSelector()
        self.selector.region_selected.connect(self._on_region_selected)
        QTimer.singleShot(300, self.selector.showFullScreen)
        QTimer.singleShot(350, lambda: self._restore_after_capture(hidden))

    def _on_region_selected(self, x, y, w, h):
        self.config.set("region", [x, y, w, h])
        self.config.set("capture_mode", "region")
        self.config.save()
        index = self.monitor_combo.findData(-1)
        if index >= 0:
            self.monitor_combo.setCurrentIndex(index)

    def _hide_for_capture(self) -> list:
        hidden = []
        if self.isVisible():
            self.hide()
            hidden.append(self)
        if self.toolbar.isVisible():
            self.toolbar.hide()
            hidden.append(self.toolbar)
        for _ in range(6):
            QApplication.processEvents()
        return hidden

    def _restore_after_capture(self, hidden: list):
        for widget in hidden:
            widget.show()
        if self.toolbar in hidden:
            self.toolbar.raise_()

    def _async_take_screenshot(self, callback):
        source = self.monitor_combo.currentData()
        mode = "region" if source == -1 else "monitor"
        region = self.config.get("region") if source == -1 else None

        self.capture_worker = CaptureWorker(mode, source, region)
        self.capture_worker.succeeded.connect(callback)
        self.capture_worker.failed.connect(lambda err: self._error("Chụp ảnh lỗi", err))
        self.capture_worker.start()

    # ------------------ Tự Động Tùy Chỉnh Prompt Theo Chế Độ Học Tập ------------------
    def _get_active_prompt(self, base_prompt: str) -> str:
        mode = self.mode_combo.currentData() if hasattr(self, "mode_combo") else "step"
        if mode == "mcq":
            return base_prompt + "\n\n[YÊU CẦU ĐẶC BIỆT]: Chỉ đưa ra đáp án đúng nhanh gọn nhất (ví dụ: A. B. C. D), kèm 1-2 câu giải thích ngắn gọn."
        elif mode == "similar":
            return base_prompt + "\n\n[YÊU CẦU ĐẶC BIỆT]: Giải bài toán này, sau đó tạo thêm 2 bài tập tương tự kèm đáp án để người học tự luyện tập."
        elif mode == "concept":
            return base_prompt + "\n\n[YÊU CẦU ĐẶC BIỆT]: Giải thích chi tiết các công thức, khái niệm lý thuyết và định lý được sử dụng trong bài tập này."
        return base_prompt

    # ------------------ Giải Bài Thường & Listening ------------------
    def on_solve_normal(self):
        if self._busy():
            return
        hidden = self._hide_for_capture()
        QTimer.singleShot(300, lambda: self._async_take_screenshot(
            lambda png: self._on_solve_normal_got_png(png, hidden)
        ))

    def _on_solve_normal_got_png(self, png: bytes, hidden: list):
        self._restore_after_capture(hidden)
        if not png:
            return

        img_path = self.history_mgr.save_image_for_session(self.current_session["id"], png)
        raw_prompt = self.config.get("prompt_normal")
        prompt = self._get_active_prompt(raw_prompt)

        self.history.append({"role": "user", "parts": [text_part(prompt), image_part(png)]})
        self.messages.append(("user", i18n.t("chat_user_captured"), img_path))
        self._render_chat()
        self._send_to_gemini(i18n.t("chat_thinking"))

    def on_listening_clicked(self):
        if self.record_worker is not None and self.record_worker.isRunning():
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        if self._busy():
            return
        hidden = self._hide_for_capture()
        QTimer.singleShot(300, lambda: self._begin_recording(hidden))

    def _begin_recording(self, hidden):
        self._async_take_screenshot(lambda png: self._on_listening_got_png(png, hidden))

    def _on_listening_got_png(self, png: bytes, hidden: list):
        self.pending_shot = png
        self._restore_after_capture(hidden)

        self.record_worker = RecordWorker(
            use_loopback=self.loopback_check.isChecked(),
            max_seconds=int(self.config.get("max_audio_seconds", 300)),
        )
        self.record_worker.level_changed.connect(self._on_level)
        self.record_worker.finished_ok.connect(self._on_record_done)
        self.record_worker.failed.connect(self._on_record_failed)
        self.record_worker.start()

        self.record_seconds = 0
        self.record_timer.start(1000)
        self._set_recording_ui(True)
        self.level_bar.setVisible(True)
        self.record_label.setVisible(True)

    def _stop_recording(self):
        if self.record_worker is not None:
            self.record_worker.stop()
        self.record_timer.stop()

    def _tick_record(self):
        self.record_seconds += 1
        m, s = divmod(self.record_seconds, 60)
        self.record_label.setText(f"Đang thu {m:02d}:{s:02d}")

    def _on_level(self, level: float):
        self.level_bar.setValue(int(level * 100))

    def _set_recording_ui(self, recording: bool):
        self.btn_listen_main.setText("Dừng & Giải (F3)" if recording else i18n.t("btn_solve_listening") + " (F3)")
        self.toolbar.listen_btn.setText("Dừng & Giải" if recording else i18n.t("btn_solve_listening"))

    def _on_record_failed(self, message: str):
        self._reset_listen_ui()
        self._error("Lỗi thu âm", message)

    def _reset_listen_ui(self):
        self.record_timer.stop()
        self._set_recording_ui(False)
        self.level_bar.setVisible(False)
        self.record_label.setVisible(False)
        self.record_worker = None

    def _on_record_done(self, wav: bytes, duration: float):
        self._reset_listen_ui()

        raw_prompt = self.config.get("prompt_listening")
        prompt = self._get_active_prompt(raw_prompt)
        parts = [text_part(prompt)]

        img_path = None
        if self.pending_shot:
            img_path = self.history_mgr.save_image_for_session(self.current_session["id"], self.pending_shot)
            parts.append(image_part(self.pending_shot))
            self.pending_shot = None

        try:
            parts.append(audio_part(wav))
        except Exception as exc:
            self._error("Audio Error", str(exc))
            return

        self.history.append({"role": "user", "parts": parts})
        self.messages.append(("user", i18n.t("chat_user_listened", int(duration)), img_path))
        self._render_chat()
        self._send_to_gemini(i18n.t("chat_listening_thinking"))

    # ------------------ Chat & History ------------------
    def on_send_chat(self):
        if self._busy():
            return
        text = self.chat_input.toPlainText().strip()
        if not text:
            return
        self.chat_input.clear()
        self.history.append({"role": "user", "parts": [text_part(text)]})
        self.messages.append(("user", text, None))
        self._render_chat()
        self._send_to_gemini(i18n.t("chat_thinking"))

    def on_new_chat(self):
        self.current_session = self.history_mgr.create_session()
        self.history = []
        self.messages = []
        self.pending_shot = None
        self._render_chat()
        self.status.showMessage("Đã tạo cuộc trò chuyện mới.", 3000)

    def _busy(self) -> bool:
        if self.ask_worker is not None and self.ask_worker.isRunning():
            return True
        return False

    def _send_to_gemini(self, status_text: str):
        self.send_btn.setEnabled(False)
        self.btn_solve_main.setEnabled(False)
        self.toolbar.solve_btn.setEnabled(False)
        self.status.showMessage(status_text)
        self.messages.append(("pending", "...", None))
        self._render_chat()

        if not self.isVisible():
            self.busy_indicator.set_text(status_text)
            self.busy_indicator.show_near(self.toolbar)

        self.ask_worker = AskWorker(
            self._client(), list(self.history), self.SYSTEM_INSTRUCTION
        )
        self.ask_worker.succeeded.connect(self._on_answer)
        self.ask_worker.failed.connect(self._on_answer_failed)
        self.ask_worker.start()

    def _on_answer(self, text: str):
        if self.messages and self.messages[-1][0] == "pending":
            self.messages.pop()
        self.messages.append(("model", text, None))
        self.history.append({"role": "model", "parts": [text_part(text)]})
        
        if self.current_session:
            self.current_session["messages"] = self.messages
            self.history_mgr.save_session(self.current_session)

        self._render_chat()
        self._unlock()
        self.busy_indicator.hide()
        self._popup_answer(text)

    def _on_answer_failed(self, message: str):
        if self.messages and self.messages[-1][0] == "pending":
            self.messages.pop()
        self.messages.append(("error", message, None))
        if self.history and self.history[-1]["role"] == "user":
            self.history.pop()
        self._render_chat()
        self._unlock()
        self.busy_indicator.hide()

    def _unlock(self):
        self.send_btn.setEnabled(True)
        self.btn_solve_main.setEnabled(True)
        self.toolbar.solve_btn.setEnabled(True)
        self.ask_worker = None

    def _get_current_question_title(self) -> str:
        for item in reversed(self.messages):
            if item[0] == "user":
                return item[1][:100]
        return "Câu hỏi khó SolveX"

    def _get_current_question_img(self) -> str:
        for item in reversed(self.messages):
            if item[0] == "user" and len(item) > 2 and item[2]:
                return item[2]
        return ""

    def _popup_answer(self, text: str):
        if self.answer_window is None:
            self.answer_window = AnswerWindow(self)
        enable_tts = bool(self.config.get("enable_tts", True))
        self.answer_window.show_answer(text, self.config.get("theme", "dark"), enable_tts)
        if enable_tts and self.config.get("auto_tts", False):
            QTimer.singleShot(500, self.answer_window._speak_answer)

    # ------------------ Hiển thị Chat ------------------
    def _render_chat(self):
        theme = self.config.get("theme", "dark")
        p = style.get_palette(theme)

        if not self.messages:
            body = (
                f"<div style='color:{p['MUTED']}; padding:24px 14px;'>"
                f"<p style='font-size:16px; font-weight:bold; color:{p['AMBER']};'>"
                f"{i18n.t('chat_welcome_title')}</p>"
                f"<p>{i18n.t('chat_welcome_desc')}</p>"
                "</div>"
            )
        else:
            blocks = []
            for item in self.messages:
                role, text = item[0], item[1]
                img_path = item[2] if len(item) > 2 else None

                img_html = ""
                if img_path and os.path.exists(img_path):
                    file_url = Path(img_path).as_uri()
                    img_html = f"<br><img class='question-img' src='{file_url}' width='320'/><br>"

                if role == "user":
                    blocks.append(
                        f"<div style='margin:12px 0;'>"
                        f"<div style='color:{p['AMBER']}; font-weight:bold;'>{i18n.t('chat_user_label')}</div>"
                        f"<div>{render_markdown(text)}{img_html}</div></div>"
                    )
                elif role == "model":
                    blocks.append(
                        f"<div style='margin:12px 0;'>"
                        f"<div style='color:{p['TEAL']}; font-weight:bold;'>{i18n.t('chat_solvex_label')}</div>"
                        f"<div>{render_markdown(text)}</div></div>"
                    )
                elif role == "pending":
                    blocks.append(
                        f"<div style='margin:12px 0; color:{p['MUTED']};'>"
                        f"{i18n.t('chat_thinking')}</div>"
                    )
                else:
                    blocks.append(
                        f"<div style='margin:12px 0; color:{p['RED']};'><b>Lỗi:</b> {html_lib.escape(text)}</div>"
                    )
            body = "".join(blocks)

        self.chat.setHtml(wrap_html_page(body, theme))
        scrollbar = self.chat.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    # ------------------ History Tab Actions & Search Filter & Markdown Export ------------------
    def _refresh_history_list(self):
        self.hist_list.clear()
        is_saved_tab = hasattr(self, "hist_mode_btn_saved") and self.hist_mode_btn_saved.isChecked()

        if is_saved_tab:
            items = self.saved_questions_mgr.list_saved()
            for q in items:
                title = q.get("title", "Câu hỏi khó")
                item = QListWidgetItem(f"⭐ {q.get('timestamp', '')}\n{title}")
                item.setData(Qt.ItemDataRole.UserRole, q)
                item.setData(Qt.ItemDataRole.UserRole + 1, title.lower())
                item.setData(Qt.ItemDataRole.UserRole + 2, "saved")
                self.hist_list.addItem(item)
        else:
            sessions = self.history_mgr.list_sessions()
            for s in sessions:
                title = s["title"] if s["title"] else i18n.t("hist_no_title")
                item = QListWidgetItem(f"🕒 {s['timestamp']}\n{title}")
                item.setData(Qt.ItemDataRole.UserRole, s["id"])
                item.setData(Qt.ItemDataRole.UserRole + 1, title.lower())
                item.setData(Qt.ItemDataRole.UserRole + 2, "session")
                self.hist_list.addItem(item)
        self._filter_history_list()

    def _filter_history_list(self):
        query = self.hist_search_input.text().strip().lower() if hasattr(self, "hist_search_input") else ""
        for i in range(self.hist_list.count()):
            item = self.hist_list.item(i)
            search_key = item.data(Qt.ItemDataRole.UserRole + 1) or ""
            item.setHidden(bool(query and query not in search_key))

    def on_history_item_clicked(self, item: QListWidgetItem):
        kind = item.data(Qt.ItemDataRole.UserRole + 2)
        theme = self.config.get("theme", "dark")
        p = style.get_palette(theme)

        if kind == "saved":
            qdata = item.data(Qt.ItemDataRole.UserRole)
            if not isinstance(qdata, dict):
                return
            title = qdata.get("title", "")
            markdown_text = qdata.get("markdown", "")
            img_path = qdata.get("image_path")
            img_html = f"<br><img class='question-img' src='{Path(img_path).as_uri()}' width='320'/><br>" if img_path and os.path.exists(img_path) else ""

            body = (
                f"<div style='margin:12px 0;'><b style='color:{p['AMBER']};'>⭐ CÂU HỎI KHÓ ĐÃ LƯU:</b><br>{html_lib.escape(title)}{img_html}</div>"
                f"<div style='margin:12px 0;'><b style='color:{p['TEAL']};'>🤖 LỜI GIẢI AI:</b><br>{render_markdown(markdown_text)}</div>"
            )
            self.hist_preview.setHtml(wrap_html_page(body, theme))
        else:
            sid = item.data(Qt.ItemDataRole.UserRole)
            session = self.history_mgr.load_session(sid)
            if not session:
                return
            self.current_session = session
            self.messages = session.get("messages", [])
            
            blocks = []
            for item in self.messages:
                role, text = item[0], item[1]
                img_path = item[2] if len(item) > 2 else None
                img_html = f"<br><img class='question-img' src='{Path(img_path).as_uri()}' width='320'/><br>" if img_path and os.path.exists(img_path) else ""
                
                lbl_color = p["AMBER"] if role == "user" else p["TEAL"]
                blocks.append(f"<div style='margin:8px 0;'><b style='color:{lbl_color};'>{role.upper()}:</b> {render_markdown(text)}{img_html}</div>")
            
            self.hist_preview.setHtml(wrap_html_page(''.join(blocks), theme))

    def on_export_history(self):
        if not self.messages:
            self._error("Xuất File", "Hiện chưa có câu hỏi hoặc đáp án nào để xuất.")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Xuất File Lịch Sử Trò Chuyện SolveX",
            f"SolveX_Solution_{self.current_session['id'][:8]}.md",
            "Markdown Files (*.md);;Text Files (*.txt)"
        )
        if not filename:
            return

        lines = [f"# SolveX AI Solution Export — {self.current_session.get('timestamp', '')}\n\n"]
        for item in self.messages:
            role, text = item[0], item[1]
            if role == "user":
                lines.append(f"### 👤 Người dùng:\n{text}\n\n")
            elif role == "model":
                lines.append(f"### 🤖 SolveX AI:\n{text}\n\n---\n\n")

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("".join(lines))
            QMessageBox.information(self, "SolveX Export", f"Đã xuất file thành công tại:\n{filename}")
            self.status.showMessage(f"Đã xuất file: {filename}", 5000)
        except Exception as exc:
            self._error("Lỗi Xuất File", str(exc))

    def on_clear_history(self):
        reply = QMessageBox.question(
            self, "SolveX", i18n.t("hist_clear_confirm"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.history_mgr.clear_all()
            self._refresh_history_list()
            self.hist_preview.clear()

    def _error(self, title: str, message: str):
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle(title)
        box.setText(message)
        box.exec()

    def closeEvent(self, event):
        self.on_save_settings()
        event.ignore()
        self.hide()

    def _shutdown(self):
        if self.record_worker is not None and self.record_worker.isRunning():
            self.record_worker.stop()
            self.record_worker.wait(2000)
        self.on_save_settings()
