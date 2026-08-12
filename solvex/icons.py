"""Bộ vẽ Vector Icon WinUI 3 Chuẩn Tối Giản (Classic Clean Icons) cho SolveX.
Vẽ bằng QPainter nét 1.5px thanh lịch, dễ nhìn, chuẩn mực WinUI 3 — Không dùng emoji.
"""

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap

from . import style


class IconFactory:
    """Tạo QIcon WinUI 3 nét mảnh 1.5px tối giản, sang trọng."""

    @staticmethod
    def draw_icon(name: str, color_hex: str = style.TEXT, size: int = 24) -> QIcon:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        color = QColor(color_hex)
        pen = QPen(color, 1.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        s = float(size)
        pad = s * 0.16
        rect = QRectF(pad, pad, s - 2 * pad, s - 2 * pad)

        if name == "camera":
            # Icon máy ảnh WinUI 3 cổ điển
            x, y, w, h = rect.x(), rect.y() + rect.height() * 0.18, rect.width(), rect.height() * 0.74
            path = QPainterPath()
            path.addRoundedRect(QRectF(x, y, w, h), 4, 4)
            path.moveTo(x + w * 0.3, y)
            path.lineTo(x + w * 0.4, rect.y() + 2)
            path.lineTo(x + w * 0.6, rect.y() + 2)
            path.lineTo(x + w * 0.7, y)
            cx, cy = rect.center().x(), y + h * 0.5
            path.addEllipse(QPointF(cx, cy), w * 0.22, w * 0.22)
            painter.drawPath(path)

        elif name in ("solve", "sparkle"):
            # Icon ngôi sao AI WinUI 3
            cx, cy = s * 0.5, s * 0.5
            r_out, r_in = s * 0.38, s * 0.12
            path = QPainterPath()
            import math
            for i in range(8):
                r = r_out if i % 2 == 0 else r_in
                angle = i * math.pi / 4 - math.pi / 2
                px = cx + r * math.cos(angle)
                py = cy + r * math.sin(angle)
                if i == 0:
                    path.moveTo(px, py)
                else:
                    path.lineTo(px, py)
            path.closeSubpath()
            painter.drawPath(path)

        elif name in ("headphones", "listen"):
            # Icon tai nghe thanh lịch
            cx, cy = s * 0.5, s * 0.5
            r = s * 0.34
            path = QPainterPath()
            path.arcMoveTo(QRectF(cx - r, cy - r, 2 * r, 2 * r), 0)
            path.arcTo(QRectF(cx - r, cy - r, 2 * r, 2 * r), 0, 180)
            painter.drawPath(path)
            painter.setBrush(color)
            painter.drawRoundedRect(QRectF(cx - r - 2, cy - 1, 4, r * 0.8), 2, 2)
            painter.drawRoundedRect(QRectF(cx + r - 2, cy - 1, 4, r * 0.8), 2, 2)

        elif name == "history":
            # Icon đồng hồ WinUI 3
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.44
            path = QPainterPath()
            path.addEllipse(QPointF(cx, cy), r, r)
            path.moveTo(cx, cy - r * 0.55)
            path.lineTo(cx, cy)
            path.lineTo(cx + r * 0.45, cy)
            painter.drawPath(path)

        elif name == "settings":
            # Icon bánh răng WinUI 3
            cx, cy = rect.center().x(), rect.center().y()
            r_out, r_in = rect.width() * 0.44, rect.width() * 0.28
            path = QPainterPath()
            import math
            n_teeth = 8
            for i in range(n_teeth * 2):
                angle = i * math.pi / n_teeth
                r = r_out if i % 2 == 0 else r_in
                px = cx + r * math.cos(angle)
                py = cy + r * math.sin(angle)
                if i == 0:
                    path.moveTo(px, py)
                else:
                    path.lineTo(px, py)
            path.closeSubpath()
            path.addEllipse(QPointF(cx, cy), r_in * 0.5, r_in * 0.5)
            painter.drawPath(path)

        elif name == "guide":
            # Icon cuốn sách WinUI 3
            w, h = rect.width(), rect.height()
            x, y = rect.x(), rect.y()
            path = QPainterPath()
            path.moveTo(x, y + h * 0.15)
            path.lineTo(x + w * 0.5, y + h * 0.28)
            path.lineTo(x + w, y + h * 0.15)
            path.lineTo(x + w, y + h * 0.82)
            path.lineTo(x + w * 0.5, y + h * 0.95)
            path.lineTo(x, y + h * 0.82)
            path.closeSubpath()
            path.moveTo(x + w * 0.5, y + h * 0.28)
            path.lineTo(x + w * 0.5, y + h * 0.95)
            painter.drawPath(path)

        elif name in ("changelog", "spark"):
            # Icon Dấu Chấm Than (!) Thông Tin cho nút "Có gì mới"
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.44
            path = QPainterPath()
            path.addEllipse(QPointF(cx, cy), r, r)
            # Thân dấu chấm than
            path.moveTo(cx, cy - r * 0.48)
            path.lineTo(cx, cy + r * 0.1)
            # Dấu chấm ở dưới
            path.moveTo(cx, cy + r * 0.42)
            path.lineTo(cx, cy + r * 0.52)
            painter.drawPath(path)

        elif name == "globe":
            # Icon quả địa cầu WinUI 3
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.44
            painter.drawEllipse(QPointF(cx, cy), r, r)
            painter.drawLine(QPointF(cx - r, cy), QPointF(cx + r, cy))
            painter.drawEllipse(QPointF(cx, cy), r * 0.45, r)

        elif name == "moon":
            # Icon mặt trăng lưỡi liềm (Dark Mode)
            path = QPainterPath()
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.42
            path.addEllipse(QPointF(cx, cy), r, r)
            cut_path = QPainterPath()
            cut_path.addEllipse(QPointF(cx + r * 0.42, cy - r * 0.2), r * 0.88, r * 0.88)
            moon_path = path.subtracted(cut_path)
            painter.drawPath(moon_path)

        elif name == "sun":
            # Icon mặt trời WinUI 3
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.22
            painter.drawEllipse(QPointF(cx, cy), r, r)
            import math
            for i in range(8):
                angle = i * math.pi / 4
                x1 = cx + (r + 3) * math.cos(angle)
                y1 = cy + (r + 3) * math.sin(angle)
                x2 = cx + (r + 7) * math.cos(angle)
                y2 = cy + (r + 7) * math.sin(angle)
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        elif name in ("update", "sync"):
            # Icon lặp đồng bộ WinUI 3
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.38
            path = QPainterPath()
            path.arcMoveTo(QRectF(cx - r, cy - r, 2 * r, 2 * r), 35)
            path.arcTo(QRectF(cx - r, cy - r, 2 * r, 2 * r), 35, 280)
            painter.drawPath(path)
            import math
            ax = cx + r * math.cos(math.pi / 4)
            ay = cy - r * math.sin(math.pi / 4)
            path_arrow = QPainterPath()
            path_arrow.moveTo(ax - 4, ay - 4)
            path_arrow.lineTo(ax + 3, ay)
            path_arrow.lineTo(ax - 4, ay + 4)
            painter.drawPath(path_arrow)

        elif name == "trash":
            # Icon thùng rác WinUI 3
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
            path = QPainterPath()
            path.moveTo(x, y + h * 0.22)
            path.lineTo(x + w, y + h * 0.22)
            path.moveTo(x + w * 0.22, y + h * 0.22)
            path.lineTo(x + w * 0.26, y + h)
            path.lineTo(x + w * 0.74, y + h)
            path.lineTo(x + w * 0.78, y + h * 0.22)
            path.moveTo(x + w * 0.35, y + h * 0.22)
            path.lineTo(x + w * 0.35, y + 2)
            path.lineTo(x + w * 0.65, y + 2)
            path.lineTo(x + w * 0.65, y + h * 0.22)
            painter.drawPath(path)

        elif name == "plus":
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.35
            painter.drawLine(QPointF(cx - r, cy), QPointF(cx + r, cy))
            painter.drawLine(QPointF(cx, cy - r), QPointF(cx, cy + r))

        elif name == "key":
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
            path = QPainterPath()
            path.addEllipse(QPointF(x + w * 0.32, y + h * 0.32), w * 0.24, w * 0.24)
            path.moveTo(x + w * 0.48, y + h * 0.48)
            path.lineTo(x + w * 0.88, y + h * 0.88)
            path.lineTo(x + w * 0.88, y + h * 0.74)
            path.moveTo(x + w * 0.74, y + h * 0.74)
            path.lineTo(x + w * 0.74, y + h * 0.62)
            painter.drawPath(path)

        elif name == "tray":
            # Icon Nút Thu Xuống Khay: Mũi Tên Hướng Xuống Dưới (↓)
            cx, cy = rect.center().x(), rect.center().y()
            w, h = rect.width(), rect.height()
            path = QPainterPath()
            # Thân mũi tên thẳng đứng
            path.moveTo(cx, rect.y() + h * 0.12)
            path.lineTo(cx, rect.y() + h * 0.82)
            # Đầu mũi tên chĩa xuống dưới (↓)
            path.moveTo(cx - w * 0.3, rect.y() + h * 0.52)
            path.lineTo(cx, rect.y() + h * 0.82)
            path.lineTo(cx + w * 0.3, rect.y() + h * 0.52)
            painter.drawPath(path)

        elif name == "minimize":
            cy = s * 0.5
            painter.drawLine(QPointF(s * 0.25, cy), QPointF(s * 0.75, cy))

        elif name == "maximize":
            x, y, w, h = s * 0.25, s * 0.25, s * 0.5, s * 0.5
            painter.drawRect(QRectF(x, y, w, h))

        elif name == "restore":
            x, y, w, h = s * 0.22, s * 0.35, s * 0.42, s * 0.42
            painter.drawRect(QRectF(x, y, w, h))
            painter.drawRect(QRectF(x + 5, y - 5, w, h))

        elif name == "close":
            x1, y1, x2, y2 = s * 0.28, s * 0.28, s * 0.72, s * 0.72
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            painter.drawLine(QPointF(x2, y1), QPointF(x1, y2))

        painter.end()
        return QIcon(pixmap)
