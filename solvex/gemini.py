"""Client gọi Gemini API (endpoint generateContent)."""

import base64

import requests

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
TIMEOUT = 180

# Giới hạn thực tế của inline_data trong 1 request (~20MB kể cả base64).
MAX_INLINE_BYTES = 14 * 1024 * 1024


class GeminiError(Exception):
    pass


def image_part(png_bytes: bytes) -> dict:
    return {
        "inline_data": {
            "mime_type": "image/png",
            "data": base64.b64encode(png_bytes).decode("ascii"),
        }
    }


def audio_part(wav_bytes: bytes) -> dict:
    if len(wav_bytes) > MAX_INLINE_BYTES:
        raise GeminiError(
            f"Đoạn ghi âm quá dài ({len(wav_bytes) / 1024 / 1024:.1f} MB). "
            "Hãy thu ngắn hơn (dưới ~7 phút) rồi thử lại."
        )
    return {
        "inline_data": {
            "mime_type": "audio/wav",
            "data": base64.b64encode(wav_bytes).decode("ascii"),
        }
    }


def text_part(text: str) -> dict:
    return {"text": text}


class GeminiClient:
    def __init__(self, api_key: str, model: str, temperature: float = 0.2):
        self.api_key = (api_key or "").strip()
        self.model = (model or "").strip()
        self.temperature = temperature

    def generate(self, contents: list, system_instruction: str = None) -> str:
        if not self.api_key:
            raise GeminiError("Chưa nhập API key. Dán key vào ô ở góc trên rồi bấm Lưu.")
        if not self.model:
            raise GeminiError("Chưa chọn model.")

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": 8192,
            },
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        url = f"{BASE_URL}/{self.model}:generateContent"
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
        except requests.Timeout:
            raise GeminiError("Hết thời gian chờ. Mạng chậm hoặc file audio quá lớn.")
        except requests.RequestException as exc:
            raise GeminiError(f"Không kết nối được tới Gemini: {exc}")

        if response.status_code != 200:
            raise GeminiError(self._explain_http_error(response))

        try:
            data = response.json()
        except ValueError:
            raise GeminiError("Gemini trả về dữ liệu không đọc được.")

        return self._extract_text(data)

    def _explain_http_error(self, response) -> str:
        try:
            detail = response.json().get("error", {}).get("message", "")
        except ValueError:
            detail = response.text[:400]

        code = response.status_code
        if code == 400 and "API key" in detail:
            return "API key không hợp lệ. Kiểm tra lại key ở Google AI Studio."
        if code == 400:
            return f"Yêu cầu bị từ chối (400).\n{detail}"
        if code in (401, 403):
            return (
                "API key sai hoặc chưa được cấp quyền.\n"
                f"{detail}"
            )
        if code == 404:
            return (
                f"Không tìm thấy model '{self.model}'.\n"
                "Sửa tên model trong ô Model ở góc trên (tên model thay đổi theo "
                "thời gian, xem danh sách hiện hành ở Google AI Studio).\n"
                f"{detail}"
            )
        if code == 429:
            return "Vượt hạn mức (429). Chờ một lát rồi thử lại."
        if code >= 500:
            return f"Máy chủ Gemini đang lỗi ({code}). Thử lại sau ít phút."
        return f"Lỗi HTTP {code}.\n{detail}"

    def _extract_text(self, data: dict) -> str:
        feedback = data.get("promptFeedback", {})
        if feedback.get("blockReason"):
            raise GeminiError(
                f"Nội dung bị chặn bởi bộ lọc an toàn ({feedback['blockReason']})."
            )

        candidates = data.get("candidates") or []
        if not candidates:
            raise GeminiError("Gemini không trả về nội dung nào.")

        candidate = candidates[0]
        parts = candidate.get("content", {}).get("parts") or []
        text = "".join(p.get("text", "") for p in parts).strip()

        if not text:
            reason = candidate.get("finishReason", "")
            if reason == "MAX_TOKENS":
                raise GeminiError("Câu trả lời bị cắt vì quá dài. Thử hỏi từng phần nhỏ hơn.")
            if reason == "SAFETY":
                raise GeminiError("Câu trả lời bị bộ lọc an toàn chặn.")
            raise GeminiError(f"Câu trả lời rỗng (finishReason={reason or 'không rõ'}).")

        return text
