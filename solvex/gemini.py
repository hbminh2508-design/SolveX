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

        # Tự động thử lại tối đa 2 lần khi gặp sự cố mạng chập chờn
        response = None
        last_exc = None
        for attempt in range(2):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
                break
            except requests.Timeout:
                last_exc = "Hết thời gian chờ. Mạng chậm hoặc file audio quá lớn."
            except requests.RequestException as exc:
                last_exc = f"Không kết nối được tới Gemini: {exc}"
            import time
            time.sleep(1.0)

        if response is None:
            raise GeminiError(last_exc or "Không thể kết nối đến máy chủ Gemini.")

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

        from solvex.security import sanitize_log_message
        detail = sanitize_log_message(detail)

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


class DualGeminiClient:
    """Client hỗ trợ chạy đồng thời / kết hợp 2 AI Models (Chế độ Turbo & Turbo+)."""

    def __init__(self, client1: GeminiClient, client2: GeminiClient = None, mode: str = "standard"):
        self.client1 = client1
        self.client2 = client2
        self.mode = mode  # "standard", "turbo", "turbo_plus"

    def generate(self, contents: list, system_instruction: str = None) -> str:
        if self.mode == "standard" or not self.client2 or not self.client2.api_key:
            return self.client1.generate(contents, system_instruction)

        if self.mode == "turbo":
            # 1. Chế độ Turbo: Gọi song song cả 2 Model và dùng Model 2 đối chiếu tổng hợp kết quả chính xác nhất
            import concurrent.futures

            res1, res2 = None, None
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                f1 = executor.submit(self.client1.generate, contents, system_instruction)
                f2 = executor.submit(self.client2.generate, contents, system_instruction)

                try:
                    res1 = f1.result()
                except Exception as e:
                    res1 = f"Model 1 error: {e}"

                try:
                    res2 = f2.result()
                except Exception as e:
                    res2 = f"Model 2 error: {e}"

            if res1 and not res1.startswith("Model 1 error") and res2 and not res2.startswith("Model 2 error"):
                synthesis_prompt = [
                    text_part(
                        f"Dưới đây là 2 bài giải độc lập cho cùng một đề bài từ 2 Model AI khác nhau:\n\n"
                        f"--- LỜI GIẢI 1 (Model: {self.client1.model}) ---\n{res1}\n\n"
                        f"--- LỜI GIẢI 2 (Model: {self.client2.model}) ---\n{res2}\n\n"
                        f"Nhiệm vụ của bạn:\n"
                        f"1. Đối chiếu kết quả của 2 bài giải trên.\n"
                        f"2. Loại bỏ các bước giải sai hoặc nhầm lẫn (nếu có).\n"
                        f"3. Tổng hợp thành LỜI GIẢI HOÀN CHỈNH, RÕ RÀNG VÀ CHÍNH XÁC 100% BẰNG TIẾNG VIỆT MARKDOWN.\n"
                        f"4. Giữ nguyên mục **ĐÁP ÁN** ở cuối."
                    )
                ]
                try:
                    synthesis_res = self.client2.generate(synthesis_prompt)
                    return f"⚡ **[Chế độ Turbo — Song Song 2 Model AI]**\n*Đối chiếu & Tổng hợp từ `{self.client1.model}` & `{self.client2.model}`*\n\n{synthesis_res}"
                except Exception:
                    return res2
            elif res2 and not res2.startswith("Model 2 error"):
                return res2
            elif res1 and not res1.startswith("Model 1 error"):
                return res1
            else:
                raise GeminiError(f"Cả hai Model AI đều gặp sự cố:\n- {res1}\n- {res2}")

        elif self.mode == "turbo_plus":
            # 2. Chế độ Turbo+: Model 1 tạo đáp án sơ bộ -> Model 2 (thông minh hơn) kiểm chứng & tối ưu hóa bài giải
            initial_sol = self.client1.generate(contents, system_instruction)

            refine_prompt = [
                text_part(
                    f"Bạn là chuyên gia kiểm định toán học & khoa học cấp cao. Dưới đây là kết quả giải bài từ Model 1 ({self.client1.model}):\n\n"
                    f"{initial_sol}\n\n"
                    f"Hãy:\n"
                    f"1. Kiểm tra lại từng phép tính, công thức toán/lý và lập luận logic.\n"
                    f"2. Sửa lại tất cả các chỗ nhầm lẫn hoặc chưa tối ưu.\n"
                    f"3. Trình bày lại bài giải thật đẹp mắt, dùng định dạng toán học LaTeX chuẩn xác.\n"
                    f"4. Đảm bảo phần **ĐÁP ÁN** cuối cùng hoàn toàn đúng đắn."
                )
            ]
            try:
                perfected_sol = self.client2.generate(refine_prompt)
                return f"🚀 **[Chế độ Turbo+ — Dual-Model AI Kiểm Chứng & Tối Ưu]**\n*Giải bởi `{self.client1.model}` — Kiểm chứng & Tối ưu bởi `{self.client2.model}`*\n\n{perfected_sol}"
            except Exception:
                return initial_sol

        return self.client1.generate(contents, system_instruction)
