"""Chụp màn hình: toàn màn hình, một monitor, hoặc một vùng do người dùng chọn."""

import io

import mss
from PIL import Image

MAX_WIDTH = 1600  # thu nhỏ ảnh lớn để gửi API nhanh và rẻ hơn


class CaptureError(Exception):
    pass


def list_monitors():
    """Trả về danh sách monitor. Phần tử 0 là 'tất cả màn hình gộp lại'."""
    with mss.mss() as sct:
        return [dict(m) for m in sct.monitors]


def _to_png(raw, size, downscale=True) -> bytes:
    img = Image.frombytes("RGB", size, raw, "raw", "BGRX")
    if downscale and img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / img.width
        img = img.resize(
            (MAX_WIDTH, max(1, int(img.height * ratio))),
            Image.LANCZOS,
        )
    buffer = io.BytesIO()
    img.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def grab_monitor(index: int = 1) -> bytes:
    """Chụp toàn bộ một màn hình. index=0 nghĩa là gộp mọi màn hình."""
    with mss.mss() as sct:
        if index < 0 or index >= len(sct.monitors):
            index = 1 if len(sct.monitors) > 1 else 0
        shot = sct.grab(sct.monitors[index])
        return _to_png(shot.bgra, shot.size)


def grab_region(x: int, y: int, width: int, height: int) -> bytes:
    """Chụp một vùng chữ nhật theo toạ độ pixel vật lý."""
    if width < 2 or height < 2:
        raise CaptureError("Vùng chọn quá nhỏ.")
    box = {"left": int(x), "top": int(y), "width": int(width), "height": int(height)}
    with mss.mss() as sct:
        shot = sct.grab(box)
        return _to_png(shot.bgra, shot.size)


def capture(mode: str, monitor_index: int = 1, region=None) -> bytes:
    """Điểm vào chung. mode là 'monitor' hoặc 'region'."""
    if mode == "region":
        if not region or len(region) != 4:
            raise CaptureError("Chưa chọn vùng chụp. Bấm 'Chọn vùng' trước.")
        return grab_region(*region)
    return grab_monitor(monitor_index)
