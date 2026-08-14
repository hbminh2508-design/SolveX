# -*- coding: utf-8 -*-
"""Bộ vẽ Vector Icon WinUI 3 Chuẩn Tối Giản & Đồng Bộ Màu Sắc (v1.16.0).
Vẽ bằng QPainter nét 1.6px thanh lịch, sắc nét, đồng bộ màu sắc thương hiệu WinUI 3 Fluent.
"""

import math
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap

from . import style

UNIFIED_ACCENT_COLOR = "#0ea5e9"  # Màu thương hiệu xanh Teal/Blue đồng bộ


class IconFactory:
    """Tạo QIcon WinUI 3 nét mảnh 1.6px tối giản, sang trọng và đồng bộ màu sắc."""

    @staticmethod
    def draw_icon(name: str, color_hex: str = None, size: int = 24) -> QIcon:
        if color_hex is None:
            color_hex = UNIFIED_ACCENT_COLOR

        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        color = QColor(color_hex)
        pen = QPen(color, 1.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        s = float(size)
        pad = s * 0.16
        rect = QRectF(pad, pad, s - 2 * pad, s - 2 * pad)

        if name == "star":
            cx, cy = rect.center().x(), rect.center().y()
            r_out, r_in = rect.width() * 0.44, rect.width() * 0.18
            path = QPainterPath()
            for i in range(10):
                r = r_out if i % 2 == 0 else r_in
                angle = i * math.pi / 5 - math.pi / 2
                px = cx + r * math.cos(angle)
                py = cy + r * math.sin(angle)
                if i == 0:
                    path.moveTo(px, py)
                else:
                    path.lineTo(px, py)
            path.closeSubpath()
            painter.drawPath(path)

        elif name == "settings":
            cx, cy = rect.center().x(), rect.center().y()
            r_out, r_in, r_hole = rect.width() * 0.44, rect.width() * 0.32, rect.width() * 0.18
            path = QPainterPath()
            n_teeth = 6
            tooth_width_angle = math.pi / (n_teeth * 3)

            for i in range(n_teeth):
                center_angle = i * (2 * math.pi / n_teeth) - math.pi / 2
                a1 = center_angle - tooth_width_angle * 1.2
                a2 = center_angle - tooth_width_angle * 0.6
                a3 = center_angle + tooth_width_angle * 0.6
                a4 = center_angle + tooth_width_angle * 1.2

                p1 = QPointF(cx + r_in * math.cos(a1), cy + r_in * math.sin(a1))
                p2 = QPointF(cx + r_out * math.cos(a2), cy + r_out * math.sin(a2))
                p3 = QPointF(cx + r_out * math.cos(a3), cy + r_out * math.sin(a3))
                p4 = QPointF(cx + r_in * math.cos(a4), cy + r_in * math.sin(a4))

                if i == 0:
                    path.moveTo(p1)
                else:
                    path.lineTo(p1)
                path.lineTo(p2)
                path.lineTo(p3)
                path.lineTo(p4)

            path.closeSubpath()
            path.addEllipse(QPointF(cx, cy), r_hole, r_hole)
            painter.drawPath(path)

        elif name == "camera":
            x, y, w, h = rect.x(), rect.y() + rect.height() * 0.15, rect.width(), rect.height() * 0.75
            path = QPainterPath()
            path.addRoundedRect(QRectF(x, y, w, h), 4, 4)
            path.moveTo(x + w * 0.18, y)
            path.lineTo(x + w * 0.32, y)
            path.moveTo(x + w * 0.62, y)
            path.lineTo(x + w * 0.72, y - 2)
            path.lineTo(x + w * 0.84, y - 2)
            path.lineTo(x + w * 0.88, y)
            cx, cy = rect.center().x(), y + h * 0.52
            path.addEllipse(QPointF(cx, cy), w * 0.28, w * 0.28)
            path.addEllipse(QPointF(cx, cy), w * 0.14, w * 0.14)
            painter.drawPath(path)

        elif name in ("compact", "topbar"):
            cx, cy = rect.center().x(), rect.center().y()
            w, h = rect.width(), rect.height()
            path = QPainterPath()
            path.moveTo(rect.x(), rect.y() + h * 0.88)
            path.lineTo(rect.x() + w, rect.y() + h * 0.88)
            path.moveTo(cx, rect.y() + h * 0.74)
            path.lineTo(cx, rect.y() + h * 0.08)
            path.moveTo(cx - w * 0.28, rect.y() + h * 0.36)
            path.lineTo(cx, rect.y() + h * 0.08)
            path.lineTo(cx + w * 0.28, rect.y() + h * 0.36)
            painter.drawPath(path)

        elif name in ("solve", "sparkle", "spark"):
            cx, cy = s * 0.5, s * 0.5
            r_out, r_in = s * 0.38, s * 0.12
            path = QPainterPath()
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

        elif name in ("headphones", "listen", "speaker"):
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
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.44
            path = QPainterPath()
            path.addEllipse(QPointF(cx, cy), r, r)
            path.moveTo(cx, cy - r * 0.55)
            path.lineTo(cx, cy)
            path.lineTo(cx + r * 0.45, cy)
            painter.drawPath(path)

        elif name == "guide":
            w, h = rect.width(), rect.height()
            x, y = rect.x(), rect.y()
            path = QPainterPath()
            path.addRoundedRect(QRectF(x, y, w, h), 3, 3)
            path.moveTo(x + w * 0.25, y + h * 0.3)
            path.lineTo(x + w * 0.75, y + h * 0.3)
            path.moveTo(x + w * 0.25, y + h * 0.5)
            path.lineTo(x + w * 0.75, y + h * 0.5)
            path.moveTo(x + w * 0.25, y + h * 0.7)
            path.lineTo(x + w * 0.55, y + h * 0.7)
            painter.drawPath(path)

        elif name == "trash":
            w, h = rect.width(), rect.height()
            x, y = rect.x(), rect.y()
            path = QPainterPath()
            path.moveTo(x + w * 0.1, y + h * 0.2)
            path.lineTo(x + w * 0.9, y + h * 0.2)
            path.moveTo(x + w * 0.35, y + h * 0.2)
            path.lineTo(x + w * 0.38, y + h * 0.08)
            path.lineTo(x + w * 0.62, y + h * 0.08)
            path.lineTo(x + w * 0.65, y + h * 0.2)
            path.addRoundedRect(QRectF(x + w * 0.2, y + h * 0.25, w * 0.6, h * 0.7), 2, 2)
            path.moveTo(x + w * 0.4, y + h * 0.4)
            path.lineTo(x + w * 0.4, y + h * 0.75)
            path.moveTo(x + w * 0.6, y + h * 0.4)
            path.lineTo(x + w * 0.6, y + h * 0.75)
            painter.drawPath(path)

        elif name in ("plus", "add"):
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.38
            path = QPainterPath()
            path.moveTo(cx - r, cy)
            path.lineTo(cx + r, cy)
            path.moveTo(cx, cy - r)
            path.lineTo(cx, cy + r)
            painter.drawPath(path)

        elif name == "close":
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.35
            path = QPainterPath()
            path.moveTo(cx - r, cy - r)
            path.lineTo(cx + r, cy + r)
            path.moveTo(cx + r, cy - r)
            path.lineTo(cx - r, cy + r)
            painter.drawPath(path)

        elif name in ("moon", "dark"):
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.42
            path = QPainterPath()
            path.addEllipse(QPointF(cx - r * 0.1, cy), r, r)
            sub_path = QPainterPath()
            sub_path.addEllipse(QPointF(cx + r * 0.3, cy - r * 0.2), r * 0.88, r * 0.88)
            path = path.subtracted(sub_path)
            painter.drawPath(path)

        elif name in ("sun", "light"):
            cx, cy = rect.center().x(), rect.center().y()
            r_center = rect.width() * 0.22
            r_ray = rect.width() * 0.44
            path = QPainterPath()
            path.addEllipse(QPointF(cx, cy), r_center, r_center)
            for i in range(8):
                angle = i * math.pi / 4
                p1 = QPointF(cx + r_center * 1.4 * math.cos(angle), cy + r_center * 1.4 * math.sin(angle))
                p2 = QPointF(cx + r_ray * math.cos(angle), cy + r_ray * math.sin(angle))
                path.moveTo(p1)
                path.lineTo(p2)
            painter.drawPath(path)

        elif name in ("update", "refresh"):
            cx, cy = rect.center().x(), rect.center().y()
            r = rect.width() * 0.38
            path = QPainterPath()
            path.arcMoveTo(QRectF(cx - r, cy - r, 2 * r, 2 * r), 45)
            path.arcTo(QRectF(cx - r, cy - r, 2 * r, 2 * r), 45, 270)
            end_x = cx + r * math.cos(45 * math.pi / 180)
            end_y = cy - r * math.sin(45 * math.pi / 180)
            path.moveTo(end_x - 4, end_y - 2)
            path.lineTo(end_x, end_y)
            path.lineTo(end_x - 2, end_y + 4)
            painter.drawPath(path)

        else:  # Icon mặc định (Sparkle)
            cx, cy = s * 0.5, s * 0.5
            r_out, r_in = s * 0.38, s * 0.12
            path = QPainterPath()
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

        painter.end()
        return QIcon(pixmap)
