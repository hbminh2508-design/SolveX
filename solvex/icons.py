"""Bộ vẽ Vector Icon v3.0 Masterwork (Liquid Glass & WinUI 3 Modern Luxury) cho SolveX.
Vẽ bằng QPainter và QPainterPath với đường nét hình học 1.75px tỉ mỉ, tỉ lệ hoàn hảo — Không dùng emoji.
"""

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap

from . import style


class IconFactory:
    """Tạo QIcon dạng Master Vector v3.0 sang trọng với thiết kế tinh xảo cao cấp."""

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
        pad = s * 0.14
        rect = QRectF(pad, pad, s - 2 * pad, s - 2 * pad)

        if name == "camera":
            # Icon máy ảnh chuyên nghiệp DSLR / Mirrorless masterwork
            x, y, w, h = rect.x(), rect.y() + rect.height() * 0.18, rect.width(), rect.height() * 0.74
            path = QPainterPath()
            path.addRoundedRect(QRectF(x, y, w, h), 6, 6)
            
            # Thang kính ngắm & Nút chụp đỉnh
            path.moveTo(x + w * 0.28, y)
            path.lineTo(x + w * 0.36, rect.y() + 2)
            path.lineTo(x + w * 0.64, rect.y() + 2)
            path.lineTo(x + w * 0.72, y)
            
            # Vòng ống kính kép xa xỉ
            cx, cy = rect.center().x(), y + h * 0.5
            path.addEllipse(QPointF(cx, cy), w * 0.25, w * 0.25)
            path.addEllipse(QPointF(cx, cy), w * 0.12, w * 0.12)
            
            # Đèn cảm biến / Flash phụ
            path.addEllipse(QPointF(x + w * 0.82, y + h * 0.25), 1.2, 1.2)
            painter.drawPath(path)

        elif name in ("solve", "sparkle"):
            # Icon Ngôi sao AI Diamond Sparkle Masterwork 4 cánh & sao vệ tinh
            cx, cy = s * 0.5, s * 0.5
            r_out, r_in = s * 0.42, s * 0.12
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
            
            # Nhân nhụy tâm sáng
            path.addEllipse(QPointF(cx, cy), 1.8, 1.8)
            painter.drawPath(path)

            # Sao vệ tinh phát quang
            painter.setBrush(color)
            painter.drawEllipse(QPointF(cx + r_out * 0.58, cy - r_out * 0.58), 1.4, 1.4)
            painter.drawEllipse(QPointF(cx - r_out * 0.58, cy + r_out * 0.58), 1.4, 1.4)

        elif name in ("headphones", "listen"):
            # Icon Tai nghe Studio Monitor cao cấp
            cx, cy = s * 0.5, s * 0.5
            r = s * 0.35
            path = QPainterPath()
            path.arcMoveTo(QRectF(cx - r, cy - r, 2 * r, 2 * r), -10)
            path.arcTo(QRectF(cx - r, cy - r, 2 * r, 2 * r), -10, 200)
            painter.drawPath(path)
            
            # Ốp tai đệm da bo góc mượt
            painter.setBrush(color)
            painter.drawRoundedRect(QRectF(cx - r - 3, cy - 2, 5, r * 0.85), 2.5, 2.5)
            painter.drawRoundedRect(QRectF(cx + r - 2, cy - 2, 5, r * 0.85), 2.5, 2.5)
            
            # Khớp nối kim loại
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawLine(QPointF(cx - r - 0.5, cy - 2), QPointF(cx - r - 0.5, cy - 6))
            painter.drawLine(QPointF(cx + r + 0.5, cy - 2), QPointF(cx + r + 0.5, cy - 6))

        elif name == "history":
            # Icon Đồng hồ Chronometer tinh xảo
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.44
            path = QPainterPath()
            path.addEllipse(QPointF(cx, cy), r, r)
            
            # Kim chỉ giờ 10:10 sang trọng
            path.moveTo(cx, cy)
            path.lineTo(cx - r * 0.35, cy - r * 0.35)
            path.moveTo(cx, cy)
            path.lineTo(cx + r * 0.45, cy - r * 0.2)
            
            painter.drawPath(path)
            painter.setBrush(color)
            painter.drawEllipse(QPointF(cx, cy), 1.8, 1.8)

        elif name == "settings":
            # Icon Bánh răng kỹ thuật Masterwork 8 răng độ nét cao
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
            # Icon Cuốn sách phẳng Masterwork mở đôi
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
            
            # Gáy sách & Dải trang trí
            path.moveTo(x + w * 0.5, y + h * 0.28)
            path.lineTo(x + w * 0.5, y + h * 0.95)
            painter.drawPath(path)

        elif name in ("changelog", "spark"):
            # Icon Tên lửa / Huy hiệu thông báo phát sáng
            cx, cy = rect.center().x(), rect.center().y()
            w, h = rect.width(), rect.height()
            path = QPainterPath()
            path.moveTo(cx, rect.y())
            path.quadTo(QPointF(rect.right(), cy), QPointF(cx, rect.bottom()))
            path.quadTo(QPointF(rect.x(), cy), QPointF(cx, rect.y()))
            painter.drawPath(path)
            painter.setBrush(color)
            painter.drawEllipse(QPointF(cx, cy), w * 0.15, w * 0.15)

        elif name == "globe":
            # Icon Quả địa cầu 3D Wireframe Masterwork
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.44
            painter.drawEllipse(QPointF(cx, cy), r, r)
            painter.drawLine(QPointF(cx - r, cy), QPointF(cx + r, cy))
            painter.drawEllipse(QPointF(cx, cy), r * 0.45, r)
            painter.drawEllipse(QPointF(cx, cy), r, r * 0.45)

        elif name == "moon":
            # Icon Mặt trăng lưỡi liềm xa xỉ kèm 2 sao sáng
            path = QPainterPath()
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.44
            path.arcMoveTo(QRectF(cx - r, cy - r, 2 * r, 2 * r), 45)
            path.arcTo(QRectF(cx - r, cy - r, 2 * r, 2 * r), 45, 260)
            path.quadTo(QPointF(cx + r * 0.2, cy), QPointF(cx + r * 0.32, cy - r * 0.85))
            painter.drawPath(path)
            
            painter.setBrush(color)
            painter.drawEllipse(QPointF(cx + r * 0.45, cy - r * 0.35), 1.2, 1.2)
            painter.drawEllipse(QPointF(cx + r * 0.2, cy + r * 0.5), 1.2, 1.2)

        elif name == "sun":
            # Icon Mặt trời Vương miện 8 tia tapered
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.24
            painter.drawEllipse(QPointF(cx, cy), r, r)
            import math
            for i in range(8):
                angle = i * math.pi / 4
                x1 = cx + (r + 3) * math.cos(angle)
                y1 = cy + (r + 3) * math.sin(angle)
                x2 = cx + (r + 8) * math.cos(angle)
                y2 = cy + (r + 8) * math.sin(angle)
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        elif name in ("update", "sync"):
            # Icon Vòng lặp đồng bộ Masterwork
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
            # Icon Thùng rác masterwork mảnh
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
            
            # Gân hủy rác dọc
            path.moveTo(x + w * 0.42, y + h * 0.38)
            path.lineTo(x + w * 0.42, y + h * 0.82)
            path.moveTo(x + w * 0.58, y + h * 0.38)
            path.lineTo(x + w * 0.58, y + h * 0.82)
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
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
            path = QPainterPath()
            path.moveTo(x, y + h * 0.35)
            path.lineTo(x, y + h)
            path.lineTo(x + w, y + h)
            path.lineTo(x + w, y + h * 0.35)
            path.moveTo(x + w * 0.18, y + h * 0.35)
            path.lineTo(x + w * 0.32, y + h * 0.62)
            path.lineTo(x + w * 0.68, y + h * 0.62)
            path.lineTo(x + w * 0.82, y + h * 0.35)
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
