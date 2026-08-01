"""Bộ vẽ Vector Icon v2.0 Sang Trọng (Luxury Minimalist 2026) cho SolveX.
Vẽ bằng QPainter và QPainterPath với đường nét 1.75px tinh xảo, hình học chuẩn mực — Không dùng emoji.
"""

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap

from . import style


class IconFactory:
    """Tạo QIcon dạng vector v2.0 sang trọng với đường nét tinh xảo."""

    @staticmethod
    def draw_icon(name: str, color_hex: str = style.TEXT, size: int = 24) -> QIcon:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        color = QColor(color_hex)
        pen = QPen(color, 1.75, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        s = float(size)
        pad = s * 0.15
        rect = QRectF(pad, pad, s - 2 * pad, s - 2 * pad)

        if name == "camera":
            # Icon máy ảnh sang trọng
            path = QPainterPath()
            rw, rh = rect.width(), rect.height() * 0.72
            rx, ry = rect.x(), rect.y() + rect.height() * 0.22
            path.addRoundedRect(QRectF(rx, ry, rw, rh), 4, 4)
            # Ống kính kép
            cx, cy = rect.center().x(), ry + rh / 2
            path.addEllipse(QPointF(cx, cy), rw * 0.22, rw * 0.22)
            path.addEllipse(QPointF(cx, cy), rw * 0.08, rw * 0.08)
            # Nút shutter mỏng
            path.moveTo(rx + rw * 0.28, ry)
            path.lineTo(rx + rw * 0.38, rect.y() + 1)
            path.lineTo(rx + rw * 0.62, rect.y() + 1)
            path.lineTo(rx + rw * 0.72, ry)
            painter.drawPath(path)

        elif name in ("solve", "sparkle"):
            # Icon ngôi sao AI 4 cánh hình học (Geometric Diamond Sparkle)
            path = QPainterPath()
            cx, cy = s * 0.5, s * 0.5
            r1, r2 = s * 0.4, s * 0.11
            import math
            for i in range(8):
                r = r1 if i % 2 == 0 else r2
                angle = i * math.pi / 4 - math.pi / 2
                x = cx + r * math.cos(angle)
                y = cy + r * math.sin(angle)
                if i == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
            path.closeSubpath()
            painter.drawPath(path)
            # Chấm sáng nhỏ phụ
            painter.setBrush(color)
            painter.drawEllipse(QPointF(cx + r1 * 0.6, cy - r1 * 0.6), 1.2, 1.2)
            painter.drawEllipse(QPointF(cx - r1 * 0.6, cy + r1 * 0.6), 1.2, 1.2)

        elif name in ("headphones", "listen"):
            # Icon tai nghe tối giản
            path = QPainterPath()
            cx, cy = s * 0.5, s * 0.52
            r = s * 0.34
            path.arcMoveTo(QRectF(cx - r, cy - r, 2 * r, 2 * r), 0)
            path.arcTo(QRectF(cx - r, cy - r, 2 * r, 2 * r), 0, 180)
            painter.drawPath(path)
            # Ốp tai bo góc 4px
            painter.setBrush(color)
            painter.drawRoundedRect(QRectF(cx - r - 2, cy - 2, 4.5, r * 0.8), 2, 2)
            painter.drawRoundedRect(QRectF(cx + r - 2.5, cy - 2, 4.5, r * 0.8), 2, 2)

        elif name == "history":
            # Icon đồng hồ tinh xảo
            path = QPainterPath()
            path.addEllipse(rect)
            cx, cy = rect.center().x(), rect.center().y()
            path.moveTo(cx, cy - rect.height() * 0.32)
            path.lineTo(cx, cy)
            path.lineTo(cx + rect.width() * 0.24, cy)
            painter.drawPath(path)
            painter.setBrush(color)
            painter.drawEllipse(QPointF(cx, cy), 1.5, 1.5)

        elif name == "settings":
            # Icon bánh răng kỹ thuật 8 răng độ nét cao
            cx, cy = rect.center().x(), rect.center().y()
            r_out, r_in = rect.width() * 0.42, rect.width() * 0.26
            path = QPainterPath()
            import math
            n_teeth = 8
            for i in range(n_teeth * 2):
                angle = i * math.pi / n_teeth
                r = r_out if i % 2 == 0 else r_in
                x = cx + r * math.cos(angle)
                y = cy + r * math.sin(angle)
                if i == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
            path.closeSubpath()
            painter.drawPath(path)
            painter.drawEllipse(QPointF(cx, cy), r_in * 0.48, r_in * 0.48)

        elif name == "guide":
            # Icon cuốn sách tối giản mở phẳng
            path = QPainterPath()
            w, h = rect.width(), rect.height()
            x, y = rect.x(), rect.y()
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
            # Icon tín hiệu / loa phát thông báo
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
            cy = rect.center().y()
            path = QPainterPath()
            path.moveTo(x, cy - 3)
            path.lineTo(x + w * 0.35, cy - 3)
            path.lineTo(x + w * 0.72, y + 2)
            path.lineTo(x + w * 0.72, y + h - 2)
            path.lineTo(x + w * 0.35, cy + 3)
            path.lineTo(x, cy + 3)
            path.closeSubpath()
            painter.drawPath(path)
            # Sóng âm thanh
            painter.drawArc(QRectF(x + w * 0.78, cy - 6, 10, 12), -60 * 16, 120 * 16)

        elif name == "globe":
            # Icon quả địa cầu sang trọng
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.44
            painter.drawEllipse(QPointF(cx, cy), r, r)
            painter.drawLine(QPointF(cx - r, cy), QPointF(cx + r, cy))
            painter.drawEllipse(QPointF(cx, cy), r * 0.45, r)

        elif name == "moon":
            # Icon mặt trăng lưỡi liềm kèm sao
            path = QPainterPath()
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.42
            path.arcMoveTo(QRectF(cx - r, cy - r, 2 * r, 2 * r), 40)
            path.arcTo(QRectF(cx - r, cy - r, 2 * r, 2 * r), 40, 270)
            path.quadTo(QPointF(cx + r * 0.25, cy), QPointF(cx + r * 0.3, cy - r * 0.85))
            painter.drawPath(path)

        elif name == "sun":
            # Icon mặt trời 8 tia
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
            # Icon cung xoay cập nhật
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.38
            path = QPainterPath()
            path.arcMoveTo(QRectF(cx - r, cy - r, 2 * r, 2 * r), 40)
            path.arcTo(QRectF(cx - r, cy - r, 2 * r, 2 * r), 40, 270)
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
            # Icon thùng rác mảnh
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
            path = QPainterPath()
            path.moveTo(x, y + h * 0.22)
            path.lineTo(x + w, y + h * 0.22)
            path.moveTo(x + w * 0.2, y + h * 0.22)
            path.lineTo(x + w * 0.25, y + h)
            path.lineTo(x + w * 0.75, y + h)
            path.lineTo(x + w * 0.8, y + h * 0.22)
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
            # Icon chìa khoá tinh tế
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
            path = QPainterPath()
            path.addEllipse(QPointF(x + w * 0.32, y + h * 0.32), w * 0.25, w * 0.25)
            path.moveTo(x + w * 0.5, y + h * 0.5)
            path.lineTo(x + w * 0.88, y + h * 0.88)
            path.lineTo(x + w * 0.88, y + h * 0.75)
            path.moveTo(x + w * 0.75, y + h * 0.75)
            path.lineTo(x + w * 0.75, y + h * 0.65)
            painter.drawPath(path)

        elif name == "tray":
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
            path = QPainterPath()
            path.moveTo(x, y + h * 0.35)
            path.lineTo(x, y + h)
            path.lineTo(x + w, y + h)
            path.lineTo(x + w, y + h * 0.35)
            path.moveTo(x + w * 0.2, y + h * 0.35)
            path.lineTo(x + w * 0.35, y + h * 0.62)
            path.lineTo(x + w * 0.65, y + h * 0.62)
            path.lineTo(x + w * 0.8, y + h * 0.35)
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
