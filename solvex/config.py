"""Lưu và đọc cấu hình của SolveX (API key, model, prompt...)."""

import json
import os
import sys
from pathlib import Path

APP_NAME = "SolveX"

DEFAULT_MODEL = "gemini-3.5-flash-lite"

PROMPT_NORMAL = (
    "Bạn là trợ lý học tập. Ảnh dưới đây là đề bài mà người học đang làm.\n\n"
    "Hãy:\n"
    "1. Đọc và chép lại đề bài (nếu ảnh mờ hoặc thiếu, nói rõ chỗ nào không đọc được).\n"
    "2. Xác định dạng bài và kiến thức cần dùng.\n"
    "3. Giải từng bước, giải thích lý do của mỗi bước để người học hiểu cách làm.\n"
    "4. Kết thúc bằng mục **ĐÁP ÁN** ngắn gọn, rõ ràng.\n\n"
    "Nếu có nhiều câu hỏi trong ảnh, giải lần lượt từng câu. "
    "Trả lời bằng tiếng Việt, dùng Markdown."
)

PROMPT_LISTENING = (
    "Bạn là trợ lý luyện nghe. Bạn nhận được một đoạn audio và (có thể) một ảnh chụp "
    "màn hình chứa câu hỏi.\n\n"
    "Hãy:\n"
    "1. Chép lại **transcript** đoạn audio càng chính xác càng tốt.\n"
    "2. Dịch nghĩa transcript sang tiếng Việt.\n"
    "3. Trả lời các câu hỏi trong ảnh, mỗi câu chỉ rõ **câu nào trong transcript** "
    "chứa thông tin dẫn tới đáp án.\n"
    "4. Liệt kê từ vựng / cấu trúc đáng chú ý xuất hiện trong bài.\n\n"
    "Nếu audio không nghe rõ, nói thẳng phần nào không nghe được thay vì đoán bừa. "
    "Trả lời bằng tiếng Việt, dùng Markdown."
)

DEFAULTS = {
    "api_key": "",
    "model": DEFAULT_MODEL,
    "prompt_normal": PROMPT_NORMAL,
    "prompt_listening": PROMPT_LISTENING,
    "capture_mode": "monitor",      # "monitor" hoặc "region"
    "monitor_index": 1,
    "region": None,                  # [x, y, w, h] theo pixel vật lý
    "hide_window_on_capture": True,
    "use_loopback": True,            # thu tiếng loa (True) hay tiếng mic (False)
    "max_audio_seconds": 300,
    "temperature": 0.2,
    "language": "vi",                # "vi" hoặc "en"
    "startup_mode": "compact",       # "full", "compact", hoặc "tray"
    "theme": "dark",                 # "dark" hoặc "light"
    "enable_tts": True,              # Cho phép tính năng đọc đáp án bằng giọng nói
    "auto_tts": False,               # Tự động phát âm thanh đọc đáp án khi AI giải xong
}


def config_dir() -> Path:
    """Thư mục lưu cấu hình, theo chuẩn từng hệ điều hành."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or Path.home())
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config"))
    path = base / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


class Config:
    def __init__(self):
        self.path = config_dir() / "config.json"
        self.data = dict(DEFAULTS)
        self.load()

    def load(self):
        if not self.path.exists():
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                saved = json.load(f)
            if isinstance(saved, dict):
                for key, value in saved.items():
                    if key in DEFAULTS:
                        self.data[key] = value
        except (OSError, json.JSONDecodeError):
            self.data = dict(DEFAULTS)

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            if sys.platform != "win32":
                os.chmod(self.path, 0o600)
        except OSError:
            pass

    def get(self, key, default=None):
        return self.data.get(key, DEFAULTS.get(key, default))

    def set(self, key, value):
        self.data[key] = value

    def reset_prompts(self):
        self.data["prompt_normal"] = PROMPT_NORMAL
        self.data["prompt_listening"] = PROMPT_LISTENING
