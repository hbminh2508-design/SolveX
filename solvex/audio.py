"""Thu âm cho chế độ Listening.

Mặc định thu **tiếng phát ra loa** (loopback) chứ không phải tiếng micro, để
bắt được đúng audio của bài nghe đang chạy trên máy.

- Windows: dùng WASAPI loopback (soundcard hỗ trợ sẵn).
- Linux/PulseAudio: dùng monitor source của output device.
- macOS: hệ điều hành không cho loopback trực tiếp, cần cài BlackHole /
  Loopback rồi chọn thiết bị đó; nếu không sẽ tự chuyển sang micro.
"""

import io
import wave

import numpy as np

try:
    import soundcard as sc

    SOUNDCARD_AVAILABLE = True
    SOUNDCARD_ERROR = ""
except Exception as exc:  # pragma: no cover
    sc = None
    SOUNDCARD_AVAILABLE = False
    SOUNDCARD_ERROR = str(exc)

SAMPLE_RATE = 16000  # đủ cho giọng nói, giữ file nhỏ
BLOCK = 2048


class AudioError(Exception):
    pass


def _open_recorder(use_loopback: bool):
    """Chọn thiết bị thu và trả về context manager của soundcard."""
    if not SOUNDCARD_AVAILABLE:
        raise AudioError(
            "Không nạp được thư viện soundcard.\n"
            f"Chi tiết: {SOUNDCARD_ERROR}\n"
            "Thử: pip install soundcard"
        )

    if use_loopback:
        try:
            speaker = sc.default_speaker()
            mic = sc.get_microphone(id=str(speaker.name), include_loopback=True)
            return mic
        except Exception:
            # Không có loopback: tìm thủ công trong danh sách monitor
            try:
                for device in sc.all_microphones(include_loopback=True):
                    if getattr(device, "isloopback", False):
                        return device
            except Exception:
                pass
            raise AudioError(
                "Không tìm được thiết bị thu tiếng loa (loopback).\n"
                "Trên Windows: bật 'Stereo Mix' hoặc cập nhật driver âm thanh.\n"
                "Trên Linux: cần PulseAudio/PipeWire với monitor source.\n"
                "Hoặc bỏ tick 'Thu tiếng loa' để thu bằng micro."
            )

    try:
        return sc.default_microphone()
    except Exception as exc:
        raise AudioError(f"Không mở được micro: {exc}")


def to_wav_bytes(samples: np.ndarray, samplerate: int = SAMPLE_RATE) -> bytes:
    """Chuyển mảng float32 mono [-1, 1] thành file WAV 16-bit trong bộ nhớ."""
    if samples.size == 0:
        raise AudioError("Không thu được dữ liệu âm thanh nào.")
    clipped = np.clip(samples, -1.0, 1.0)
    pcm = (clipped * 32767.0).astype("<i2")

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(samplerate)
        wav.writeframes(pcm.tobytes())
    return buffer.getvalue()


class Recorder:
    """Thu âm theo từng block, gọi từ một thread riêng."""

    def __init__(self, use_loopback: bool = True, max_seconds: int = 300):
        self.use_loopback = use_loopback
        self.max_seconds = max_seconds
        self._chunks = []
        self._stop = False
        self.level = 0.0

    def stop(self):
        self._stop = True

    def run(self, on_level=None):
        """Vòng lặp thu. Chạy tới khi stop() được gọi hoặc chạm giới hạn thời gian."""
        device = _open_recorder(self.use_loopback)
        self._chunks = []
        self._stop = False
        max_frames = self.max_seconds * SAMPLE_RATE
        total = 0

        try:
            with device.recorder(samplerate=SAMPLE_RATE, blocksize=BLOCK) as rec:
                while not self._stop and total < max_frames:
                    data = rec.record(numframes=BLOCK)
                    if data.ndim > 1:
                        data = data.mean(axis=1)  # gộp về mono
                    self._chunks.append(data.astype(np.float32))
                    total += len(data)

                    if on_level is not None:
                        rms = float(np.sqrt(np.mean(np.square(data)))) if len(data) else 0.0
                        self.level = min(1.0, rms * 6.0)
                        on_level(self.level)
        except AudioError:
            raise
        except Exception as exc:
            raise AudioError(f"Lỗi khi thu âm: {exc}")

    def result_wav(self) -> bytes:
        if not self._chunks:
            raise AudioError(
                "Không thu được âm thanh.\n"
                "Kiểm tra: audio có đang thực sự phát ra loa không, "
                "và thiết bị loa mặc định có đúng không."
            )
        samples = np.concatenate(self._chunks)
        return to_wav_bytes(samples)

    @property
    def duration(self) -> float:
        frames = sum(len(c) for c in self._chunks)
        return frames / SAMPLE_RATE
