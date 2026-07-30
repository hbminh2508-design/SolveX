"""Giao diện SolveX."""

import html as html_lib
import os
import sys

from PyQt6.QtCore import QPoint, QRect, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QGuiApplication, QIcon, QKeySequence, QPainter, QPen, QPixmap, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QSystemTrayIcon,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from . import capture, fluent, style
from .config import Config
from .gemini import GeminiClient, audio_part, image_part, text_part
from .version import APP_VERSION, changelog_markdown
from .workers import AskWorker, RecordWorker

try:
    import markdown as md_lib
except Exception:
    md_lib = None


def render_markdown(text: str) -> str:
    if md_lib is None:
        return "<pre>" + html_lib.escape(text) + "</pre>"
    try:
        return md_lib.markdown(
            text, extensions=["fenced_code", "tables", "nl2br", "sane_lists"]
        )
    except Exception:
        return "<pre>" + html_lib.escape(text) + "</pre>"


def _resource_path(*parts) -> str:
    """Đường dẫn tới thư mục assets/, xử lý cả khi đã đóng gói bằng PyInstaller."""
    base = getattr(sys, "_MEIPASS", None)
    if base is None:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *parts)


def build_app_icon() -> QIcon:
    """Logo nhận diện của SolveX (kính lúp + tia sáng). Có file asset thì dùng
    file, không có (ví dụ chạy từ mã nguồn thiếu assets/) thì vẽ tạm bằng code."""
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
    painter.setPen(QColor(style.INK))
    font = painter.font()
    font.setBold(True)
    font.setPointSize(26)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "S")
    painter.end()
    return QIcon(pixmap)


# --------------------------------------------------------------------------
# Chọn vùng màn hình
# --------------------------------------------------------------------------
class RegionSelector(QWidget):
    """Lớp phủ toàn màn hình cho phép kéo chọn một vùng chữ nhật."""

    region_selected = pyqtSignal(int, int, int, int)  # toạ độ pixel vật lý

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

        hint = "Kéo chuột để chọn vùng đề bài  ·  Esc để huỷ"
        painter.setPen(QColor(style.TEXT))
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

        # Qt dùng pixel logic, mss dùng pixel vật lý -> nhân theo tỉ lệ DPI.
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


# --------------------------------------------------------------------------
# Hộp thoại chỉnh prompt
# --------------------------------------------------------------------------
class PromptDialog(QDialog):
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Chỉnh hướng dẫn cho AI")
        self.resize(640, 540)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Hướng dẫn cho nút <b>Giải thường</b>:"))
        self.normal = QPlainTextEdit(config.get("prompt_normal"))
        layout.addWidget(self.normal)

        layout.addWidget(QLabel("Hướng dẫn cho nút <b>Giải Listening</b>:"))
        self.listening = QPlainTextEdit(config.get("prompt_listening"))
        layout.addWidget(self.listening)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.RestoreDefaults
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(
            self.restore
        )
        layout.addWidget(buttons)

    def restore(self):
        self.config.reset_prompts()
        self.normal.setPlainText(self.config.get("prompt_normal"))
        self.listening.setPlainText(self.config.get("prompt_listening"))

    def apply(self):
        self.config.set("prompt_normal", self.normal.toPlainText().strip())
        self.config.set("prompt_listening", self.listening.toPlainText().strip())
        self.config.save()


class CaptionButton(QPushButton):
    """Nút kiểu nút điều khiển cửa sổ Windows 11 (Fluent caption button)."""

    def __init__(self, text: str, tooltip: str = "", close_style: bool = False, parent=None):
        super().__init__(text, parent)
        self.setObjectName("CaptionBtnClose" if close_style else "CaptionBtn")
        self.setFixedSize(34, 28)
        self.setToolTip(tooltip)
        self.setCursor(Qt.CursorShape.ArrowCursor)


# --------------------------------------------------------------------------
# Bảng điều khiển thu nhỏ — một cửa sổ thật, chỉ có 3 nút:
# Chụp, Giải thường, Giải Listening. Thanh tiêu đề tự vẽ theo phong cách
# Fluent/WinUI3, có thêm nút "Thu xuống khay" bên cạnh 3 nút cổ điển
# (thu nhỏ / phóng to / đóng).
# --------------------------------------------------------------------------
class CompactWindow(QWidget):
    """Mặt hiển thị mặc định của SolveX — cửa sổ đầy đủ (cài đặt, hội thoại)
    chỉ mở khi cần, còn lại app sống ở đây + tray icon."""

    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.setObjectName("CompactRoot")
        self.setWindowTitle("SolveX")
        self.setWindowIcon(build_app_icon())
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(style.COMPACT_STYLESHEET)
        self._drag_offset = None
        self._normal_geometry = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(1, 1, 1, 10)
        outer.setSpacing(6)
        outer.addWidget(self._build_titlebar())

        row = QHBoxLayout()
        row.setContentsMargins(10, 0, 10, 0)
        row.setSpacing(8)

        self.capture_btn = QPushButton("📷 Chụp")
        self.capture_btn.setObjectName("ToolbarBtn")
        self.capture_btn.setToolTip("Chọn vùng màn hình cần chụp")
        self.capture_btn.clicked.connect(self.main.on_pick_region)
        row.addWidget(self.capture_btn)

        self.solve_btn = QPushButton("📝 Giải thường")
        self.solve_btn.setObjectName("ToolbarBtn")
        self.solve_btn.setToolTip("Chụp đề đang hiện và giải  (F2)")
        self.solve_btn.clicked.connect(self.main.on_solve_normal)
        row.addWidget(self.solve_btn)

        self.listen_btn = QPushButton("🎧 Giải Listening")
        self.listen_btn.setObjectName("ToolbarBtn")
        self.listen_btn.setToolTip("Thu âm bài nghe rồi giải  (F3)")
        self.listen_btn.clicked.connect(self.main.on_listening_clicked)
        row.addWidget(self.listen_btn)
        outer.addLayout(row)

        self.adjustSize()
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.move(screen.center().x() - self.width() // 2, screen.top() + 24)

    def _build_titlebar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("CompactTitleBar")
        bar.setFixedHeight(34)
        self._titlebar = bar

        row = QHBoxLayout(bar)
        row.setContentsMargins(10, 4, 6, 0)
        row.setSpacing(6)

        logo = QLabel()
        logo.setPixmap(build_app_icon().pixmap(18, 18))
        row.addWidget(logo)

        title = QLabel("SolveX")
        title.setObjectName("CompactTitle")
        row.addWidget(title)
        row.addStretch(1)

        whats_new = CaptionButton("🆕", "Xem có gì mới")
        whats_new.clicked.connect(self.main.show_release_notes)
        row.addWidget(whats_new)

        tray_btn = CaptionButton("🗂", "Thu xuống khay hệ thống")
        tray_btn.clicked.connect(self.main.minimize_to_tray)
        row.addWidget(tray_btn)

        min_btn = CaptionButton("─", "Thu nhỏ")
        min_btn.clicked.connect(self.showMinimized)
        row.addWidget(min_btn)

        self._max_btn = CaptionButton("▢", "Phóng to")
        self._max_btn.clicked.connect(self._toggle_maximize)
        row.addWidget(self._max_btn)

        close_btn = CaptionButton("✕", "Đóng (thu xuống khay)", close_style=True)
        close_btn.clicked.connect(self.main.minimize_to_tray)
        row.addWidget(close_btn)

        return bar

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self._max_btn.setText("▢")
            self._max_btn.setToolTip("Phóng to")
        else:
            self.showMaximized()
            self._max_btn.setText("❐")
            self._max_btn.setToolTip("Khôi phục")

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.addAction("Xem có gì mới…", self.main.show_release_notes)
        menu.addAction("Cài đặt…", self.main.show_full_window)
        menu.addSeparator()
        menu.addAction("Thu xuống khay", self.main.minimize_to_tray)
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

    def mouseDoubleClickEvent(self, event):
        if self._in_titlebar(event.position().toPoint()):
            self._toggle_maximize()

    def paintEvent(self, event):
        # QWidget thường (khác QFrame/QDialog) không tự vẽ nền theo QSS khi
        # kết hợp WA_TranslucentBackground — tự vẽ thẻ bo góc để chắc ăn.
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(style.BORDER), 1))
        painter.setBrush(QColor(style.PANEL))
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 10, 10)
        painter.end()

    def showEvent(self, event):
        super().showEvent(event)
        fluent.apply_mica(self)


# --------------------------------------------------------------------------
# Cửa sổ popup hiện đáp án sau khi giải
# --------------------------------------------------------------------------
class AnswerWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SolveX — Kết quả")
        self.setWindowIcon(build_app_icon())
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.resize(640, 560)
        self.setStyleSheet(style.STYLESHEET)

        layout = QVBoxLayout(self)
        self.browser = QTextBrowser()
        self.browser.setObjectName("Chat")
        self.browser.setOpenExternalLinks(True)
        layout.addWidget(self.browser, 1)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(self.close)
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)

    def show_answer(self, markdown_text: str):
        self.browser.setHtml(f"<style>{style.CHAT_CSS}</style>{render_markdown(markdown_text)}")
        self.show()
        self.raise_()
        self.activateWindow()


# --------------------------------------------------------------------------
# Nhật ký cập nhật (Release notes)
# --------------------------------------------------------------------------
class ReleaseNotesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"SolveX — Có gì mới (v{APP_VERSION})")
        self.setWindowIcon(build_app_icon())
        self.resize(560, 520)
        self.setStyleSheet(style.STYLESHEET)

        layout = QVBoxLayout(self)
        browser = QTextBrowser()
        browser.setObjectName("Chat")
        browser.setOpenExternalLinks(True)
        browser.setHtml(f"<style>{style.CHAT_CSS}</style>{render_markdown(changelog_markdown())}")
        layout.addWidget(browser, 1)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(self.close)
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)


# --------------------------------------------------------------------------
# Ô nhỏ báo "đang giải…" — hiện khi người dùng ở chế độ khay hệ thống nên
# không thấy khung chat để biết ứng dụng đang xử lý.
# --------------------------------------------------------------------------
class BusyIndicator(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("BusyRoot")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(style.BUSY_STYLESHEET)

        row = QHBoxLayout(self)
        row.setContentsMargins(14, 10, 14, 10)
        row.setSpacing(10)

        spinner = QProgressBar()
        spinner.setRange(0, 0)  # indeterminate — Qt tự chạy hiệu ứng marquee
        spinner.setFixedWidth(60)
        spinner.setTextVisible(False)
        row.addWidget(spinner)

        self.label = QLabel("SolveX đang giải…")
        self.label.setObjectName("BusyLabel")
        row.addWidget(self.label)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(style.BORDER), 1))
        painter.setBrush(QColor(style.PANEL))
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
# Cửa sổ chính
# --------------------------------------------------------------------------
class MainWindow(QMainWindow):
    SYSTEM_INSTRUCTION = (
        "Bạn là trợ lý học tập tên SolveX. Bạn giúp người học hiểu và làm bài tập. "
        "Luôn giải thích cách làm chứ không chỉ đưa đáp án trống không. "
        "Nếu không chắc chắn, hãy nói rõ là không chắc thay vì bịa ra đáp án. "
        "Trả lời bằng tiếng Việt, trình bày bằng Markdown."
    )

    def __init__(self):
        super().__init__()
        self.config = Config()
        self.history = []          # định dạng contents của Gemini API
        self.messages = []         # [(role, markdown)] để hiển thị
        self.ask_worker = None
        self.record_worker = None
        self.pending_shot = None   # ảnh chụp kèm theo phiên listening
        self.record_seconds = 0

        self.setWindowTitle("SolveX")
        self.setWindowIcon(build_app_icon())
        self.resize(1180, 760)
        self.setStyleSheet(style.STYLESHEET)

        self._build_ui()
        self._load_config_into_ui()
        self._render_chat()

        self.record_timer = QTimer(self)
        self.record_timer.timeout.connect(self._tick_record)

        self.answer_window = None
        self.release_notes = None
        self.busy_indicator = BusyIndicator()
        self.toolbar = CompactWindow(self)
        self._setup_tray()
        self.toolbar.show()

    def showEvent(self, event):
        super().showEvent(event)
        fluent.apply_mica(self)

    # ---------------- tray icon & bảng điều khiển nổi ----------------
    def _setup_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.tray = None
            return

        self.tray = QSystemTrayIcon(build_app_icon(), self)
        self.tray.setToolTip("SolveX")

        menu = QMenu()
        self.toggle_toolbar_action = menu.addAction(
            "Ẩn bảng điều khiển", self._toggle_toolbar
        )
        menu.addAction("Cài đặt…", self.show_full_window)
        menu.addAction("Xem có gì mới…", self.show_release_notes)
        menu.addSeparator()
        menu.addAction("Thoát SolveX", self.quit_app)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._toggle_toolbar()

    def _toggle_toolbar(self):
        if self.toolbar.isVisible():
            self.minimize_to_tray()
        else:
            self.toolbar.show()
            self.toolbar.raise_()
            if self.tray is not None:
                self.toggle_toolbar_action.setText("Ẩn bảng điều khiển")

    def minimize_to_tray(self):
        """Thu bảng điều khiển xuống chỉ còn icon khay hệ thống."""
        if self.toolbar.isMaximized():
            self.toolbar.showNormal()
        self.toolbar.hide()
        if self.tray is not None:
            self.toggle_toolbar_action.setText("Hiện bảng điều khiển")

    def show_full_window(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def show_release_notes(self):
        if self.release_notes is None:
            self.release_notes = ReleaseNotesDialog()
        self.release_notes.show()
        self.release_notes.raise_()
        self.release_notes.activateWindow()

    def quit_app(self):
        self._shutdown()
        QApplication.instance().quit()

    def _popup_answer(self, text: str):
        self.busy_indicator.hide()
        if self.answer_window is None:
            self.answer_window = AnswerWindow()
        self.answer_window.show_answer(text)

    # ---------------- ẩn/hiện khi chụp màn hình ----------------
    def _hide_for_capture(self) -> list:
        """Ẩn mọi cửa sổ của SolveX đang hiện, để chúng không lọt vào ảnh chụp."""
        hidden = []
        if self.isVisible():
            self.hide()
            hidden.append(self)
        if self.toolbar.isVisible():
            self.toolbar.hide()
            hidden.append(self.toolbar)
        if hidden:
            # Đẩy nốt các sự kiện ẩn/vẽ lại đang chờ, để màn hình thật sự
            # cập nhật trước khi chụp — tránh chụp nhầm ảnh cửa sổ cũ.
            for _ in range(4):
                QApplication.processEvents()
        return hidden

    def _restore_after_capture(self, hidden: list):
        for widget in hidden:
            widget.show()
        if self.toolbar in hidden:
            self.toolbar.raise_()

    # ---------------- xây dựng giao diện ----------------
    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(14, 12, 14, 8)
        outer.setSpacing(10)

        outer.addWidget(self._build_header())

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._build_sidebar())
        splitter.addWidget(self._build_chat_panel())
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([340, 820])
        outer.addWidget(splitter, 1)

        self.status = self.statusBar()
        self.status.showMessage("Sẵn sàng. Nhập API key để bắt đầu.")

        QShortcut(QKeySequence("F2"), self, self.on_solve_normal)
        QShortcut(QKeySequence("F3"), self, self.on_listening_clicked)
        QShortcut(QKeySequence("Ctrl+Return"), self, self.on_send_chat)

    def _build_header(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("Panel")
        row = QHBoxLayout(frame)
        row.setContentsMargins(14, 10, 14, 10)
        row.setSpacing(10)

        brand_box = QVBoxLayout()
        brand_box.setSpacing(0)
        brand = QLabel("SolveX")
        brand.setObjectName("Brand")
        tagline = QLabel("Trợ lý làm bài tập")
        tagline.setObjectName("Tagline")
        brand_box.addWidget(brand)
        brand_box.addWidget(tagline)
        row.addLayout(brand_box)
        row.addSpacing(18)

        row.addWidget(QLabel("API key"))
        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setPlaceholderText("Dán Gemini API key vào đây")
        self.key_input.setMinimumWidth(240)
        row.addWidget(self.key_input, 1)

        self.show_key = QPushButton("Hiện")
        self.show_key.setCheckable(True)
        self.show_key.setFixedWidth(52)
        self.show_key.toggled.connect(self._toggle_key_visibility)
        row.addWidget(self.show_key)

        row.addWidget(QLabel("Model"))
        self.model_input = QLineEdit()
        self.model_input.setMinimumWidth(180)
        row.addWidget(self.model_input)

        save = QPushButton("Lưu")
        save.clicked.connect(self.on_save_settings)
        row.addWidget(save)

        return frame

    def _build_sidebar(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("Panel")
        frame.setMinimumWidth(310)
        frame.setMaximumWidth(430)
        box = QVBoxLayout(frame)
        box.setContentsMargins(14, 12, 14, 14)
        box.setSpacing(8)

        box.addWidget(self._section("NGUỒN CHỤP"))
        self.monitor_combo = QComboBox()
        self._populate_monitors()
        self.monitor_combo.currentIndexChanged.connect(self._on_source_changed)
        box.addWidget(self.monitor_combo)

        region_row = QHBoxLayout()
        pick = QPushButton("Chọn vùng…")
        pick.clicked.connect(self.on_pick_region)
        region_row.addWidget(pick)
        self.region_label = QLabel("chưa chọn")
        self.region_label.setStyleSheet(f"color:{style.MUTED};")
        region_row.addWidget(self.region_label, 1)
        box.addLayout(region_row)

        self.hide_check = QCheckBox("Ẩn cửa sổ & bảng điều khiển SolveX khi chụp")
        box.addWidget(self.hide_check)

        self.preview = QLabel("Ảnh chụp sẽ hiện ở đây")
        self.preview.setObjectName("Preview")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumHeight(150)
        self.preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        box.addWidget(self.preview, 1)

        box.addWidget(self._section("GIẢI BÀI"))
        self.solve_btn = QPushButton("Giải thường   ·   F2")
        self.solve_btn.setObjectName("Solve")
        self.solve_btn.clicked.connect(self.on_solve_normal)
        box.addWidget(self.solve_btn)

        self.listen_btn = QPushButton("Giải Listening   ·   F3")
        self.listen_btn.setObjectName("Listen")
        self.listen_btn.clicked.connect(self.on_listening_clicked)
        box.addWidget(self.listen_btn)

        self.loopback_check = QCheckBox("Thu tiếng loa (bỏ tick = thu micro)")
        box.addWidget(self.loopback_check)

        self.level_bar = QProgressBar()
        self.level_bar.setRange(0, 100)
        self.level_bar.setTextVisible(False)
        self.level_bar.setVisible(False)
        box.addWidget(self.level_bar)

        self.record_label = QLabel("")
        self.record_label.setStyleSheet(f"color:{style.MUTED};")
        self.record_label.setVisible(False)
        box.addWidget(self.record_label)

        box.addSpacing(4)
        bottom = QHBoxLayout()
        new_chat = QPushButton("Hội thoại mới")
        new_chat.clicked.connect(self.on_new_chat)
        bottom.addWidget(new_chat)
        prompts = QPushButton("Hướng dẫn AI…")
        prompts.clicked.connect(self.on_edit_prompts)
        bottom.addWidget(prompts)
        box.addLayout(bottom)

        return frame

    def _build_chat_panel(self) -> QWidget:
        container = QWidget()
        box = QVBoxLayout(container)
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(8)

        self.chat = QTextBrowser()
        self.chat.setObjectName("Chat")
        self.chat.setOpenExternalLinks(True)
        box.addWidget(self.chat, 1)

        input_row = QHBoxLayout()
        self.chat_input = QPlainTextEdit()
        self.chat_input.setPlaceholderText(
            "Hỏi thêm về bài vừa giải… (Ctrl+Enter để gửi)"
        )
        self.chat_input.setFixedHeight(78)
        input_row.addWidget(self.chat_input, 1)

        self.send_btn = QPushButton("Gửi")
        self.send_btn.setObjectName("Send")
        self.send_btn.setFixedWidth(84)
        self.send_btn.setFixedHeight(78)
        self.send_btn.clicked.connect(self.on_send_chat)
        input_row.addWidget(self.send_btn)
        box.addLayout(input_row)

        return container

    def _section(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("SectionLabel")
        return label

    # ---------------- cấu hình ----------------
    def _populate_monitors(self):
        self.monitor_combo.clear()
        try:
            monitors = capture.list_monitors()
        except Exception:
            monitors = []
        if len(monitors) > 1:
            for index, mon in enumerate(monitors[1:], start=1):
                self.monitor_combo.addItem(
                    f"Màn hình {index}  ({mon['width']}×{mon['height']})", index
                )
        else:
            self.monitor_combo.addItem("Màn hình chính", 1)
        if len(monitors) > 2:
            self.monitor_combo.addItem("Tất cả màn hình", 0)
        self.monitor_combo.addItem("Vùng đã chọn", -1)

    def _load_config_into_ui(self):
        self.key_input.setText(self.config.get("api_key"))
        self.model_input.setText(self.config.get("model"))
        self.hide_check.setChecked(bool(self.config.get("hide_window_on_capture")))
        self.loopback_check.setChecked(bool(self.config.get("use_loopback")))

        region = self.config.get("region")
        if region:
            self.region_label.setText(f"{region[2]}×{region[3]}")

        if self.config.get("capture_mode") == "region":
            index = self.monitor_combo.findData(-1)
            if index >= 0:
                self.monitor_combo.setCurrentIndex(index)

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
        self.show_key.setText("Ẩn" if shown else "Hiện")

    def on_save_settings(self):
        self.config.set("api_key", self.key_input.text().strip())
        self.config.set("model", self.model_input.text().strip())
        self.config.set("hide_window_on_capture", self.hide_check.isChecked())
        self.config.set("use_loopback", self.loopback_check.isChecked())
        self._on_source_changed()
        self.config.save()
        self.status.showMessage(f"Đã lưu vào {self.config.path}", 6000)

    def on_edit_prompts(self):
        dialog = PromptDialog(self.config, self)
        if dialog.exec():
            dialog.apply()
            self.status.showMessage("Đã cập nhật hướng dẫn cho AI.", 4000)

    def _client(self) -> GeminiClient:
        return GeminiClient(
            self.key_input.text().strip(),
            self.model_input.text().strip(),
            float(self.config.get("temperature", 0.2)),
        )

    # ---------------- chụp màn hình ----------------
    def on_pick_region(self):
        self.selector = RegionSelector()
        self.selector.region_selected.connect(self._on_region_selected)
        hidden = self._hide_for_capture()
        QTimer.singleShot(220, self.selector.showFullScreen)
        QTimer.singleShot(240, lambda: self._restore_after_capture(hidden))

    def _on_region_selected(self, x, y, w, h):
        self.config.set("region", [x, y, w, h])
        self.config.set("capture_mode", "region")
        self.config.save()
        self.region_label.setText(f"{w}×{h}")
        index = self.monitor_combo.findData(-1)
        if index >= 0:
            self.monitor_combo.setCurrentIndex(index)
        self.status.showMessage(f"Đã chọn vùng {w}×{h} tại ({x}, {y}).", 5000)

    def _take_screenshot(self):
        """Chụp theo cấu hình hiện tại. Trả về PNG bytes hoặc None nếu lỗi."""
        source = self.monitor_combo.currentData()
        try:
            if source == -1:
                region = self.config.get("region")
                if not region:
                    raise capture.CaptureError(
                        "Chưa chọn vùng nào. Bấm 'Chọn vùng…' rồi kéo chuột quanh đề bài."
                    )
                png = capture.grab_region(*region)
            else:
                png = capture.grab_monitor(source)
        except Exception as exc:
            self._error("Không chụp được màn hình", str(exc))
            return None

        self._show_preview(png)
        return png

    def _show_preview(self, png: bytes):
        pixmap = QPixmap()
        if pixmap.loadFromData(png, "PNG"):
            # Xoá ảnh cũ trước rồi vẽ lại ngay, để không bị kẹt hình chụp trước
            # trong lúc cửa sổ vừa ẩn/hiện xong.
            self.preview.setPixmap(QPixmap())
            self.preview.setPixmap(
                pixmap.scaled(
                    max(1, self.preview.width() - 8),
                    max(1, self.preview.height() - 8),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            self.preview.repaint()

    # ---------------- giải thường ----------------
    def on_solve_normal(self):
        if self._busy():
            return
        if self.hide_check.isChecked():
            hidden = self._hide_for_capture()
            QTimer.singleShot(260, lambda: self._solve_normal_step2(hidden))
        else:
            self._solve_normal_step2([])

    def _solve_normal_step2(self, hidden):
        png = self._take_screenshot()
        self._restore_after_capture(hidden)
        if png is None:
            return

        prompt = self.config.get("prompt_normal")
        self.history.append({"role": "user", "parts": [text_part(prompt), image_part(png)]})
        self.messages.append(("user", "**Đã chụp đề bài — đang giải…**"))
        self._render_chat()
        self._send_to_gemini("Đang đọc đề và giải…")

    # ---------------- giải listening ----------------
    def on_listening_clicked(self):
        if self.record_worker is not None and self.record_worker.isRunning():
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        if self._busy():
            return
        if self.hide_check.isChecked():
            hidden = self._hide_for_capture()
            QTimer.singleShot(260, lambda: self._begin_recording(hidden))
        else:
            self._begin_recording([])

    def _begin_recording(self, hidden):
        # Chụp màn hình trước để lấy phần câu hỏi, rồi mới bắt đầu thu.
        self.pending_shot = self._take_screenshot()
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
        self.record_label.setText("Đang thu 00:00")
        self.status.showMessage("Đang thu âm. Bấm lại nút đỏ khi audio kết thúc.")

    def _stop_recording(self):
        if self.record_worker is not None:
            self.record_worker.stop()
        self.record_timer.stop()
        self.listen_btn.setEnabled(False)
        self.listen_btn.setText("Đang xử lý…")
        self.toolbar.listen_btn.setEnabled(False)
        self.toolbar.listen_btn.setText("⏳ Đang xử lý…")
        self.status.showMessage("Đang chuẩn bị gửi audio…")

    def _tick_record(self):
        self.record_seconds += 1
        minutes, seconds = divmod(self.record_seconds, 60)
        self.record_label.setText(f"Đang thu {minutes:02d}:{seconds:02d}")

    def _on_level(self, level: float):
        self.level_bar.setValue(int(level * 100))

    def _set_recording_ui(self, recording: bool):
        """Đồng bộ nút Giải Listening ở cả sidebar và bảng điều khiển nổi."""
        self.listen_btn.setEnabled(True)
        self.listen_btn.setText("Dừng & giải   ·   F3" if recording else "Giải Listening   ·   F3")
        self.listen_btn.setObjectName("Listening" if recording else "Listen")
        self._restyle(self.listen_btn)
        self.solve_btn.setEnabled(not recording)

        self.toolbar.listen_btn.setEnabled(True)
        self.toolbar.listen_btn.setText("⏹ Dừng & giải" if recording else "🎧 Giải Listening")
        self.toolbar.listen_btn.setObjectName(
            "ToolbarBtnListening" if recording else "ToolbarBtn"
        )
        self._restyle(self.toolbar.listen_btn)
        self.toolbar.solve_btn.setEnabled(not recording)
        self.toolbar.capture_btn.setEnabled(not recording)

    def _reset_listen_button(self):
        self.record_timer.stop()
        self._set_recording_ui(False)
        self.level_bar.setVisible(False)
        self.record_label.setVisible(False)
        self.record_worker = None

    def _on_record_failed(self, message: str):
        self._reset_listen_button()
        self.pending_shot = None
        self._error("Lỗi thu âm", message)

    def _on_record_done(self, wav: bytes, duration: float):
        self._reset_listen_button()

        parts = [text_part(self.config.get("prompt_listening"))]
        if self.pending_shot:
            parts.append(image_part(self.pending_shot))
        self.pending_shot = None

        try:
            parts.append(audio_part(wav))
        except Exception as exc:
            self._error("Audio không gửi được", str(exc))
            return

        self.history.append({"role": "user", "parts": parts})
        self.messages.append(
            ("user", f"**Đã thu {duration:.0f} giây audio + ảnh câu hỏi — đang xử lý…**")
        )
        self._render_chat()
        self._send_to_gemini("Đang nghe và trả lời…")

    # ---------------- chat ----------------
    def on_send_chat(self):
        if self._busy():
            return
        text = self.chat_input.toPlainText().strip()
        if not text:
            return
        self.chat_input.clear()
        self.history.append({"role": "user", "parts": [text_part(text)]})
        self.messages.append(("user", text))
        self._render_chat()
        self._send_to_gemini("Đang trả lời…")

    def on_new_chat(self):
        self.history = []
        self.messages = []
        self.pending_shot = None
        self._render_chat()
        self.status.showMessage("Đã bắt đầu hội thoại mới.", 4000)

    # ---------------- gọi API ----------------
    def _busy(self) -> bool:
        if self.ask_worker is not None and self.ask_worker.isRunning():
            self.status.showMessage("Đang chờ câu trả lời trước, đợi một chút…", 3000)
            return True
        return False

    def _trim_history(self):
        """Chỉ giữ ảnh/audio của 2 lượt gần nhất, để request không phình to."""
        heavy_seen = 0
        for message in reversed(self.history):
            parts = message.get("parts", [])
            has_media = any("inline_data" in p for p in parts)
            if not has_media:
                continue
            heavy_seen += 1
            if heavy_seen > 2:
                message["parts"] = [p for p in parts if "inline_data" not in p] or [
                    text_part("(ảnh/audio của lượt trước đã được lược bỏ)")
                ]

    def _send_to_gemini(self, status_text: str):
        self._trim_history()
        self.send_btn.setEnabled(False)
        self.solve_btn.setEnabled(False)
        self.toolbar.solve_btn.setEnabled(False)
        self.toolbar.listen_btn.setEnabled(False)
        self.status.showMessage(status_text)
        self.messages.append(("pending", "…"))
        self._render_chat()

        # Cửa sổ đầy đủ đang ẩn (đang ở chế độ khay hệ thống) thì khung chat
        # "đang suy nghĩ…" cũng ẩn theo — cần một ô nhỏ riêng báo cho người
        # dùng biết SolveX đang xử lý chứ không phải bị treo.
        if not self.isVisible():
            self.busy_indicator.set_text(status_text)
            self.busy_indicator.show_near(self.toolbar)

        self.ask_worker = AskWorker(
            self._client(), list(self.history), self.SYSTEM_INSTRUCTION
        )
        self.ask_worker.succeeded.connect(self._on_answer)
        self.ask_worker.failed.connect(self._on_answer_failed)
        self.ask_worker.start()

    def _drop_pending(self):
        if self.messages and self.messages[-1][0] == "pending":
            self.messages.pop()

    def _on_answer(self, text: str):
        self._drop_pending()
        self.messages.append(("model", text))
        self.history.append({"role": "model", "parts": [text_part(text)]})
        self._render_chat()
        self._unlock()
        self.status.showMessage("Xong.", 4000)
        self._popup_answer(text)

    def _on_answer_failed(self, message: str):
        self._drop_pending()
        self.messages.append(("error", message))
        # Bỏ lượt hỏi lỗi ra khỏi lịch sử để lần sau không gửi lại
        if self.history and self.history[-1]["role"] == "user":
            self.history.pop()
        self._render_chat()
        self._unlock()
        self.status.showMessage("Có lỗi xảy ra.", 6000)

        self.busy_indicator.hide()
        if not self.isVisible() and self.tray is not None:
            self.tray.showMessage(
                "SolveX — có lỗi xảy ra", message, QSystemTrayIcon.MessageIcon.Warning, 6000
            )

    def _unlock(self):
        self.send_btn.setEnabled(True)
        self.solve_btn.setEnabled(True)
        self.toolbar.solve_btn.setEnabled(True)
        self.toolbar.listen_btn.setEnabled(True)
        self.ask_worker = None

    # ---------------- hiển thị ----------------
    def _render_chat(self):
        if not self.messages:
            body = (
                f"<div style='color:{style.MUTED}; padding:24px 14px;'>"
                "<p style='font-size:15px;'><b>Bắt đầu thế nào</b></p>"
                "<p>1. Dán Gemini API key ở góc trên rồi bấm <b>Lưu</b>.</p>"
                "<p>2. Mở file PDF hoặc trang bài tập, chọn nguồn chụp bên trái.</p>"
                "<p>3. Bấm <b>Giải thường</b> (F2) để chụp và giải đề trên màn hình.</p>"
                "<p>4. Với bài nghe: bấm <b>Giải Listening</b> (F3), phát audio, "
                "bấm lại để dừng và gửi.</p>"
                "<p>5. Dùng ô chat bên dưới để hỏi thêm về lời giải.</p>"
                "</div>"
            )
        else:
            blocks = []
            for role, text in self.messages:
                if role == "user":
                    blocks.append(
                        f"<div style='margin:10px 0;'>"
                        f"<div style='color:{style.AMBER}; font-weight:bold;'>Bạn</div>"
                        f"<div>{render_markdown(text)}</div></div>"
                    )
                elif role == "model":
                    blocks.append(
                        f"<div style='margin:10px 0;'>"
                        f"<div style='color:{style.TEAL}; font-weight:bold;'>SolveX</div>"
                        f"<div>{render_markdown(text)}</div></div>"
                    )
                elif role == "pending":
                    blocks.append(
                        f"<div style='margin:10px 0; color:{style.MUTED};'>"
                        "SolveX đang suy nghĩ…</div>"
                    )
                else:
                    blocks.append(
                        f"<div style='margin:10px 0; padding:8px; "
                        f"border-left:3px solid {style.RED}; color:{style.RED};'>"
                        f"<b>Lỗi</b><br>{html_lib.escape(text).replace(chr(10), '<br>')}"
                        "</div>"
                    )
            body = "".join(blocks)

        self.chat.setHtml(f"<style>{style.CHAT_CSS}</style>{body}")
        scrollbar = self.chat.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _restyle(self, widget):
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def _error(self, title: str, message: str):
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle(title)
        box.setText(message)
        box.exec()
        self.status.showMessage(title, 6000)

    def closeEvent(self, event):
        # Đóng cửa sổ đầy đủ chỉ ẩn nó đi — SolveX vẫn sống ở tray/bảng điều
        # khiển nổi. Chỉ thoát thật khi chọn "Thoát SolveX" từ tray.
        self.on_save_settings()
        event.ignore()
        self.hide()

    def _shutdown(self):
        if self.record_worker is not None and self.record_worker.isRunning():
            self.record_worker.stop()
            self.record_worker.wait(2000)
        self.on_save_settings()
