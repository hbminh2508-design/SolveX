"""Quản lý danh sách Câu Hỏi Khó đã lưu (Saved Difficult Questions Bookmark Manager).
Lưu trữ dữ liệu vào local storage persistent: APPDATA/SolveX/saved_questions.json
"""

import json
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from .config import config_dir


class SavedQuestionsManager:
    def __init__(self):
        self.dir_path = config_dir()
        self.file_path = self.dir_path / "saved_questions.json"
        self.data: List[Dict] = []
        self.load()

    def load(self):
        if not self.file_path.exists():
            self.data = []
            return
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = json.load(f)
            if isinstance(content, list):
                self.data = content
            else:
                self.data = []
        except Exception:
            self.data = []

    def save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def add_question(self, title: str, markdown: str, image_path: Optional[str] = None) -> str:
        qid = str(uuid.uuid4())
        item = {
            "id": qid,
            "title": title[:100] if title else "Câu hỏi khó chưa đặt tên",
            "markdown": markdown,
            "image_path": image_path,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "is_starred": True,
        }
        # Avoid duplicate markdown
        for existing in self.data:
            if existing.get("markdown") == markdown:
                return existing["id"]

        self.data.insert(0, item)
        self.save()
        return qid

    def remove_question(self, qid: str) -> bool:
        initial_len = len(self.data)
        self.data = [item for item in self.data if item.get("id") != qid]
        if len(self.data) < initial_len:
            self.save()
            return True
        return False

    def is_saved(self, markdown: str) -> bool:
        for item in self.data:
            if item.get("markdown") == markdown:
                return True
        return False

    def list_saved(self) -> List[Dict]:
        return list(self.data)

    def clear_all(self):
        self.data = []
        self.save()
