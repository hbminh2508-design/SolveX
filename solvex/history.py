"""Quản lý lịch sử hội thoại và lưu trữ dữ liệu vào hệ thống (local storage).
Lưu trữ các phiên làm việc (sessions) và hình ảnh câu hỏi tại %APPDATA%/SolveX/history/
"""

import json
import os
import time
from pathlib import Path
from typing import List, Dict, Optional

from .config import config_dir


def get_history_dir() -> Path:
    h_dir = config_dir() / "history"
    h_dir.mkdir(parents=True, exist_ok=True)
    return h_dir


def get_images_dir() -> Path:
    img_dir = get_history_dir() / "images"
    img_dir.mkdir(parents=True, exist_ok=True)
    return img_dir


class HistoryManager:
    """Quản lý đọc/ghi danh sách hội thoại và lưu ảnh từng câu hỏi vào đĩa."""

    def __init__(self):
        self.history_dir = get_history_dir()
        self.images_dir = get_images_dir()

    def create_session(self, title: str = "") -> dict:
        session_id = f"session_{int(time.time() * 1000)}"
        timestamp_str = time.strftime("%H:%M:%S - %d/%m/%Y")
        session = {
            "id": session_id,
            "title": title or "Hội thoại mới",
            "timestamp": timestamp_str,
            "updated_at": time.time(),
            "messages": [],
            "gemini_history": [],  # nội dung thô gửi cho Gemini API
        }
        self.save_session(session)
        return session

    def save_session(self, session: dict):
        if not session.get("id"):
            return
        session["updated_at"] = time.time()
        filepath = self.history_dir / f"{session['id']}.json"
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(session, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def list_sessions(self) -> List[dict]:
        sessions = []
        for file in self.history_dir.glob("session_*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    sessions.append({
                        "id": data.get("id"),
                        "title": data.get("title", "Hội thoại"),
                        "timestamp": data.get("timestamp", ""),
                        "updated_at": data.get("updated_at", 0),
                        "msg_count": len(data.get("messages", [])),
                    })
            except (OSError, json.JSONDecodeError):
                continue
        # Sắp xếp từ mới nhất tới cũ nhất
        sessions.sort(key=lambda x: x["updated_at"], reverse=True)
        return sessions

    def load_session(self, session_id: str) -> Optional[dict]:
        filepath = self.history_dir / f"{session_id}.json"
        if not filepath.exists():
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return None

    def delete_session(self, session_id: str):
        filepath = self.history_dir / f"{session_id}.json"
        if filepath.exists():
            try:
                filepath.unlink()
            except OSError:
                pass
        # Xoá các ảnh thuộc về session này
        for img in self.images_dir.glob(f"{session_id}_*.png"):
            try:
                img.unlink()
            except OSError:
                pass

    def clear_all(self):
        for file in self.history_dir.glob("session_*.json"):
            try:
                file.unlink()
            except OSError:
                pass
        for img in self.images_dir.glob("*.png"):
            try:
                img.unlink()
            except OSError:
                pass

    def save_image_for_session(self, session_id: str, png_bytes: bytes) -> str:
        filename = f"{session_id}_{int(time.time() * 1000)}.png"
        filepath = self.images_dir / filename
        try:
            with open(filepath, "wb") as f:
                f.write(png_bytes)
            return str(filepath.resolve())
        except OSError:
            return ""
