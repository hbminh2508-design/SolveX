"""Các thread nền, để giao diện không bị đơ khi gọi API, chụp màn hình hoặc thu âm."""

from PyQt6.QtCore import QThread, pyqtSignal

from . import capture
from .audio import AudioError, Recorder
from .gemini import GeminiClient, GeminiError


class CaptureWorker(QThread):
    """Chụp màn hình bất đồng bộ ở background thread — triệt tiêu stuttering trên UI thread."""

    succeeded = pyqtSignal(bytes)
    failed = pyqtSignal(str)

    def __init__(self, mode: str, monitor_index: int = 1, region=None, parent=None):
        super().__init__(parent)
        self.mode = mode
        self.monitor_index = monitor_index
        self.region = region

    def run(self):
        try:
            png_bytes = capture.capture(self.mode, self.monitor_index, self.region)
            self.succeeded.emit(png_bytes)
        except Exception as exc:
            self.failed.emit(str(exc))


class AskWorker(QThread):
    """Gửi hội thoại lên Gemini và trả kết quả về."""

    succeeded = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, client, contents, system_instruction=None, parent=None):
        super().__init__(parent)
        self.client = client
        self.contents = contents
        self.system_instruction = system_instruction

    def run(self):
        try:
            text = self.client.generate(self.contents, self.system_instruction)
            self.succeeded.emit(text)
        except GeminiError as exc:
            self.failed.emit(str(exc))
        except Exception as exc:  # phòng lỗi không lường trước
            self.failed.emit(f"Lỗi không xác định: {exc}")


class TestApiWorker(QThread):
    """Kiểm tra kết nối API Key mà không làm đứng giao diện."""

    succeeded = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client

    def run(self):
        try:
            # Gửi tin nhắn ngắn "Hello" để kiểm tra API key
            res = self.client.generate([{"role": "user", "parts": [{"text": "Ping"}]}])
            self.succeeded.emit(res)
        except Exception as exc:
            self.failed.emit(str(exc))


class RecordWorker(QThread):
    """Thu âm cho tới khi được yêu cầu dừng."""

    level_changed = pyqtSignal(float)
    finished_ok = pyqtSignal(bytes, float)
    failed = pyqtSignal(str)

    def __init__(self, use_loopback=True, max_seconds=300, parent=None):
        super().__init__(parent)
        self.recorder = Recorder(use_loopback=use_loopback, max_seconds=max_seconds)

    def stop(self):
        self.recorder.stop()

    def run(self):
        try:
            self.recorder.run(on_level=self.level_changed.emit)
            wav = self.recorder.result_wav()
            self.finished_ok.emit(wav, self.recorder.duration)
        except AudioError as exc:
            self.failed.emit(str(exc))
        except Exception as exc:
            self.failed.emit(f"Lỗi thu âm: {exc}")
