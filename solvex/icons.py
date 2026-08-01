"""Bộ vẽ Vector Icon chuẩn 100% cho SolveX bằng QPainter và QPainterPath.
Sử dụng hình vẽ vector sắc nét trên mọi DPI — Tuyệt đối không dùng emoji.
"""

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap

from . import style


class IconFactory:
    """Tạo QIcon dạng vector với màu sắc và kích thước tuỳ chỉnh."""

    @staticmethod
    def draw_icon(name: str, color_hex: str = style.TEXT, size: int = 24) -> QIcon:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        color = QColor(color_hex)
        pen = QPen(color, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        s = float(size)
        pad = s * 0.15
        rect = QRectF(pad, pad, s - 2 * pad, s - 2 * pad)

        if name == "camera":
            # Icon máy ảnh
            path = QPainterPath()
            rw, rh = rect.width(), rect.height() * 0.75
            rx, ry = rect.x(), rect.y() + rect.height() * 0.2
            path.addRoundedRect(QRectF(rx, ry, rw, rh), 3, 3)
            cx, cy = rect.center().x(), ry + rh / 2
            path.addEllipse(QPointF(cx, cy), rw * 0.22, rw * 0.22)
            path.moveTo(rx + rw * 0.25, ry)
            path.lineTo(rx + rw * 0.35, rect.y() + 2)
            path.lineTo(rx + rw * 0.65, rect.y() + 2)
            path.lineTo(rx + rw * 0.75, ry)
            painter.drawPath(path)

        elif name in ("solve", "sparkle"):
            # Icon ngôi sao phép thuật (AI Sparkle)
            path = QPainterPath()
            cx, cy = s * 0.5, s * 0.5
            r1, r2 = s * 0.38, s * 0.12
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
            painter.setBrush(color)
            painter.drawPath(path)

        elif name in ("headphones", "listen"):
            # Icon tai nghe
            path = QPainterPath()
            cx, cy = s * 0.5, s * 0.52
            r = s * 0.32
            path.arcMoveTo(QRectF(cx - r, cy - r, 2 * r, 2 * r), 0)
            path.arcTo(QRectF(cx - r, cy - r, 2 * r, 2 * r), 0, 180)
            painter.drawPath(path)
            painter.setBrush(color)
            painter.drawRoundedRect(QRectF(cx - r - 2, cy - 2, 5, r * 0.75), 2, 2)
            painter.drawRoundedRect(QRectF(cx + r - 3, cy - 2, 5, r * 0.75), 2, 2)

        elif name == "history":
            # Icon đồng hồ lịch sử
            path = QPainterPath()
            path.addEllipse(rect)
            cx, cy = rect.center().x(), rect.center().y()
            path.moveTo(cx, cy - rect.height() * 0.3)
            path.lineTo(cx, cy)
            path.lineTo(cx + rect.width() * 0.25, cy)
            painter.drawPath(path)

        elif name == "settings":
            # Icon bánh răng cài đặt
            cx, cy = rect.center().x(), rect.center().y()
            r_out, r_in = rect.width() * 0.42, rect.width() * 0.24
            path = QPainterPath()
            import math
            n_teeth = 6
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
            painter.drawEllipse(QPointF(cx, cy), r_in * 0.5, r_in * 0.5)

        elif name == "guide":
            # Icon cuốn sách hướng dẫn
            path = QPainterPath()
            w, h = rect.width(), rect.height()
            x, y = rect.x(), rect.y()
            path.moveTo(x, y + h * 0.1)
            path.lineTo(x + w * 0.5, y + h * 0.25)
            path.lineTo(x + w, y + h * 0.1)
            path.lineTo(x + w, y + h * 0.85)
            path.lineTo(x + w * 0.5, y + h)
            path.lineTo(x, y + h * 0.85)
            path.closeSubpath()
            path.moveTo(x + w * 0.5, y + h * 0.25)
            path.lineTo(x + w * 0.5, y + h)
            painter.drawPath(path)

        elif name in ("changelog", "spark"):
            # Icon loa thông báo / tia sáng
            cx, cy = rect.center().x(), rect.center().y()
            path = QPainterPath()
            path.moveTo(rect.x(), cy - 3)
            path.lineTo(rect.x() + rect.width() * 0.4, cy - 3)
            path.lineTo(rect.x() + rect.width() * 0.75, rect.y())
            path.lineTo(rect.x() + rect.width() * 0.75, rect.bottom())
            path.lineTo(rect.x() + rect.width() * 0.4, cy + 3)
            path.lineTo(rect.x(), cy + 3)
            path.closeSubpath()
            painter.drawPath(path)

        elif name == "trash":
            # Icon thùng rác
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
            path = QPainterPath()
            path.moveTo(x, y + h * 0.2)
            path.lineTo(x + w, y + h * 0.2)
            path.moveTo(x + w * 0.2, y + h * 0.2)
            path.lineTo(x + w * 0.25, y + h)
            path.lineTo(x + w * 0.75, y + h)
            path.lineTo(x + w * 0.8, y + h * 0.2)
            path.moveTo(x + w * 0.35, y + h * 0.2)
            path.lineTo(x + w * 0.35, y)
            path.lineTo(x + w * 0.65, y)
            path.lineTo(x + w * 0.65, y + h * 0.2)
            painter.drawPath(path)

        elif name == "plus":
            # Icon dấu cộng
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.35
            painter.drawLine(QPointF(cx - r, cy), QPointF(cx + r, cy))
            painter.drawLine(QPointF(cx, cy - r), QPointF(cx, cy + r))

        elif name == "globe":
            # Icon quả địa cầu (ngôn ngữ)
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.45
            painter.drawEllipse(QPointF(cx, cy), r, r)
            painter.drawLine(QPointF(cx - r, cy), QPointF(cx + r, cy))
            painter.drawEllipse(QPointF(cx, cy), r * 0.5, r)

        elif name == "moon":
            # Icon mặt trăng (Dark mode)
            path = QPainterPath()
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.42
            path.arcMoveTo(QRectF(cx - r, cy - r, 2 * r, 2 * r), 30)
            path.arcTo(QRectF(cx - r, cy - r, 2 * r, 2 * r), 30, 280)
            path.quadTo(QPointF(cx + r * 0.3, cy), QPointF(cx + r * 0.35, cy - r * 0.85))
            painter.setBrush(color)
            painter.drawPath(path)

        elif name == "sun":
            # Icon mặt trời (Light mode)
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.22
            painter.setBrush(color)
            painter.drawEllipse(QPointF(cx, cy), r, r)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            import math
            for i in range(8):
                angle = i * math.pi / 4
                x1 = cx + (r + 3) * math.cos(angle)
                y1 = cy + (r + 3) * math.sin(angle)
                x2 = cx + (r + 7) * math.cos(angle)
                y2 = cy + (r + 7) * math.sin(angle)
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        elif name in ("update", "sync"):
            # Icon mũi tên xoay tròn (Cập nhật)
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.38
            path = QPainterPath()
            path.arcMoveTo(QRectF(cx - r, cy - r, 2 * r, 2 * r), 45)
            path.arcTo(QRectF(cx - r, cy - r, 2 * r, 2 * r), 45, 270)
            painter.drawPath(path)
            # Đầu mũi tên
            import math
            ax = cx + r * math.cos(math.pi / 4)
            ay = cy - r * math.sin(math.pi / 4)
            path_arrow = QPainterPath()
            path_arrow.moveTo(ax - 4, ay - 4)
            path_arrow.lineTo(ax + 3, ay)
            path_arrow.lineTo(ax - 4, ay + 4)
            painter.drawPath(path_arrow)

        elif name == "tray":
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
            path = QPainterPath()
            path.moveTo(x, y + h * 0.3)
            path.lineTo(x, y + h)
            path.lineTo(x + w, y + h)
            path.lineTo(x + w, y + h * 0.3)
            path.moveTo(x + w * 0.2, y + h * 0.3)
            path.lineTo(x + w * 0.35, y + h * 0.6)
            path.lineTo(x + w * 0.65, y + h * 0.6)
            path.lineTo(x + w * 0.8, y + h * 0.3)
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
