Dưới đây là toàn bộ mã Markdown chuẩn cho file `README.md` của bạn. Bạn chỉ cần sao chép toàn bộ khối mã dưới đây và dán trực tiếp vào file `README.md` trên repository GitHub:

```markdown
# 🚀 SolveX — Trợ Lý Giải Bài Tập & Listening Thông Minh Cho Desktop

**SolveX** là ứng dụng desktop hỗ trợ học tập và giải bài tập tự động dựa trên mô hình trí tuệ nhân tạo Google Gemini[cite: 1, 2]. Chỉ với một phím tắt, ứng dụng cho phép bạn chụp nhanh đề bài trên màn hình hoặc thu âm bài nghe (Listening) từ loa máy tính, gửi dữ liệu đến Gemini và nhận lại lời giải chi tiết từng bước[cite: 1, 2].

---

## ✨ Tính Năng Nổi Bật

- 📸 **Giải bài qua ảnh chụp màn hình (`F2`):** Chụp toàn màn hình hoặc khoanh vùng linh hoạt đề bài (PDF, website, ứng dụng luyện đề...) để nhận lời giải có giải thích chi tiết[cite: 1, 2].
- 🎧 **Chế độ Listening chuyên dụng (`F3`):** Thu âm trực tiếp luồng âm thanh phát ra từ loa (WASAPI Loopback), tự động chép transcript và trả lời câu hỏi bài nghe[cite: 1, 2].
- 💬 **Trò chuyện & Hỏi đáp mở rộng (`Ctrl + Enter`):** Tương tác với AI ngay trong giao diện để làm rõ các bước giải chưa hiểu hoặc yêu cầu đào sâu kiến thức[cite: 1, 2].
- ⚙️ **Tùy biến linh hoạt:** Dễ dàng tùy chỉnh Prompt hệ thống (ví dụ: chỉ đưa ra gợi ý/định hướng thay vì đáp án trực tiếp) và thay đổi linh hoạt tên mô hình Gemini (`gemini-3.5-flash-lite`, `gemini-1.5-pro`...)[cite: 1, 2].
- 🛡️ **Bảo mật & Tiện lợi:** API key được lưu cục bộ trên máy cá nhân, giao diện hỗ trợ ẩn cửa sổ thông minh khi chụp ảnh đề bài[cite: 1, 2].

---

## 🛠️ Cấu Trúc Dự Án

```text
SolveX/
├── main.py              # File khởi chạy chính của ứng dụng
├── requirements.txt     # Danh sách các thư viện phụ thuộc
├── solvex.spec          # Cấu hình đóng gói PyInstaller (.exe)
├── build.bat            # Script tự động hóa quá trình build trên Windows
└── solvex/              # Thư mục mã nguồn chính
    ├── config.py        # Quản lý cấu hình (API key, model, prompt)
    ├── capture.py       # Xử lý chụp màn hình (mss + Pillow)
    ├── audio.py         # Thu âm hệ thống (WASAPI loopback)
    ├── gemini.py        # Giao tiếp với Google Gemini API
    ├── workers.py       # Xử lý đa luồng (QThread) giữ giao diện mượt mà
    ├── style.py         # Bảng màu và giao diện CSS/QSS
    └── ui.py            # Thiết kế giao diện người dùng (PyQt/PySide)
```[cite: 1, 2]

---

## 🔑 1. Lấy và Cấu Hình API Key

1. Truy cập **[Google AI Studio](https://aistudio.google.com/)** → Chọn **Get API key** → Tạo key mới[cite: 1, 2].
2. Khởi động ứng dụng **SolveX**, dán API key vào ô **"API key"** ở góc trên cùng và bấm **Lưu**[cite: 1, 2].

> 📌 **Lưu ý về lưu trữ:** Key được lưu dưới dạng plain text tại cấu hình hệ thống:
> - **Windows:** `%APPDATA%\SolveX\config.json`[cite: 1, 2]
> - **Linux:** `~/.config/SolveX/config.json`[cite: 1, 2]
> 
> *Vui lòng giữ bảo mật file cấu hình này và không chia sẻ cho người khác.*[cite: 1, 2]

---

## 🚀 2. Hướng Dẫn Chạy Từ Mã Nguồn (Source Code)

Yêu cầu môi trường: **Python 3.9+**[cite: 1, 2]

```bash
# Clone repository
git clone [https://github.com/your-username/SolveX.git](https://github.com/your-username/SolveX.git)
cd SolveX

# Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt

# Khởi chạy ứng dụng
python main.py
```[cite: 1, 2]

---

## 📦 3. Đóng Gói Thành File Chạy `.exe` (Windows)

> ⚠️ PyInstaller không hỗ trợ cross-compile từ Linux sang Windows. Bạn cần thực hiện quá trình build trực tiếp trên hệ điều hành **Windows**[cite: 1, 2].

### Cách 1: Sử dụng Script Build tự động
Chỉ cần chạy file `build.bat` bằng cách đúp chuột hoặc thực thi qua CMD[cite: 1, 2].

### Cách 2: Thực hiện thủ công
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --clean solvex.spec
```[cite: 1, 2]
File thực thi hoàn chỉnh sẽ nằm trong thư mục **`dist\SolveX.exe`** (chạy độc lập, không cần cài đặt Python)[cite: 1, 2].

### 🛠️ Xử lý lỗi thường gặp khi Build:
* **Ứng dụng bật lên rồi tắt ngay:** Mở file `solvex.spec`, sửa `console=False` thành `console=True`, sau đó build lại và chạy từ Command Prompt để xem log lỗi[cite: 1, 2].
* **Windows Defender cảnh báo virus:** Đây là hiện tượng *False Positive* phổ biến của PyInstaller[cite: 1, 2]. Bạn có thể thêm thư mục `dist` vào danh sách ngoại lệ (Exclusion), hoặc bỏ dòng `runtime_tmpdir=None` trong spec file để build dưới dạng thư mục thay vì một file duy nhất[cite: 1, 2].

---

## 🎯 4. Hướng Dẫn Sử Dụng

### ⌨️ Bảng Phím Tắt Khởi Động

| Thao tác | Phím tắt | Quy trình xử lý |
|---|---|---|
| **Giải bài thường** | `F2` | Chụp màn hình → Gửi dữ liệu cho Gemini → Nhận lời giải từng bước |
| **Giải bài Listening** | `F3` | **Lần 1:** Chụp đề/câu hỏi + Bắt đầu thu âm loa<br>**Lần 2:** Dừng thu + Gửi Audio & Ảnh → Nhận transcript & lời giải |
| **Gửi câu hỏi phụ** | `Ctrl + Enter` | Gửi tin nhắn trong ô chat để giải đáp thắc mắc thêm |[cite: 1, 2]

### 💡 Mẹo sử dụng hiệu quả:
* **Khoanh vùng chụp đề bài:** Sử dụng tính năng *"Chọn vùng..."* thay vì chụp toàn màn hình để tránh nhiễu thông tin (như thanh Taskbar, các ứng dụng khác), giúp AI nhận diện đề bài chính xác nhất[cite: 1, 2].
* **Ẩn cửa sổ khi chụp:** Bật tùy chọn này nếu giao diện SolveX đang đè lên nội dung bài tập trên màn hình của bạn[cite: 1, 2].
* **Tùy chỉnh Prompt:** Bấm nút *"Hướng dẫn AI"* để thay đổi phong cách giải[cite: 1, 2]. Ví dụ: *"Chỉ đưa ra gợi ý cách làm và công thức liên quan, không cung cấp đáp án trực tiếp."*[cite: 1, 2]

---

## 🔊 5. Cấu Hình & Lưu Ý Về Thu Âm Audio (Listening)

Mặc định, SolveX thu âm **trực tiếp từ luồng phát ra loa (Loopback)** nhằm đảm bảo chất lượng âm thanh trong trẻo, không dính tiếng ồn môi trường[cite: 1, 2].

* **Windows:** Sử dụng chuẩn WASAPI loopback[cite: 1, 2]. Nếu gặp lỗi không tìm thấy thiết bị, hãy mở `Control Panel` → `Sound` → tab `Recording` và bật **Stereo Mix**[cite: 1, 2].
* **Linux:** Yêu cầu PulseAudio hoặc PipeWire (có sẵn trên Ubuntu/Debian)[cite: 1, 2]. Hệ thống tự thu qua monitor source[cite: 1, 2].
* **macOS:** Do hạn chế của macOS, bạn cần cài đặt driver ảo như **BlackHole** và đặt làm thiết bị đầu ra (Output) mặc định[cite: 1, 2].
* **Fallback:** Nếu không thu được tiếng loa, bạn có thể bỏ tích chọn *"Thu tiếng loa"* để chuyển sang thu qua Microphone[cite: 1, 2].

> ⏱️ **Giới hạn thời lượng:** Độ dài file âm thanh khuyến nghị cho mỗi lần gửi là **dưới 7 phút** để đảm bảo thời gian xử lý nhanh chóng và tối ưu hạn mức API[cite: 1, 2].

---

## 🤖 6. Quản Lý Mô Hình Gemini (Model Name)

Bạn có thể thay đổi tên mô hình AI trực tiếp tại ô **Model** trên giao diện ứng dụng (mặc định: `gemini-3.5-flash-lite`)[cite: 1, 2].

Do tên gọi các dòng mô hình của Google Gemini có thể được cập nhật theo thời gian, nếu bạn gặp lỗi **`404 Model Not Found`**, hãy truy cập [Google AI Studio](https://aistudio.google.com/) để lấy mã tên mô hình hiện hành và cập nhật vào ô này (không cần phải Rebuild file `.exe`)[cite: 1, 2].

---

## 📜 7. Tuyên Bố Miễn Trừ Trách Nhiệm & Khuyên Dùng

* **Mục đích học tập:** SolveX được phát triển với mục đích đóng vai trò là một **trợ lý học tập cá nhân**, giúp người học hiểu rõ tư duy giải toán và phương pháp làm bài[cite: 1, 2]. Khuyến khích người dùng đọc kĩ lời giải, tự đặt câu hỏi phản biện và tự giải lại bài tập[cite: 1, 2].
* **Độ chính xác:** Mô hình AI vẫn có thể mắc sai sót (đặc biệt đối với các bài toán tính toán phức tạp hoặc file audio nhiều tạp âm)[cite: 1, 2]. Người dùng nên chủ động kiểm tra lại kết quả[cite: 1, 2].
* **Tính liêm chính:** Vui lòng không sử dụng ứng dụng trong các kỳ thi, kiểm tra có giám sát dưới mọi hình thức[cite: 1, 2].

---

## 🤝 Trợ Giúp & Đóng Góp

Mọi góp ý, báo lỗi (Bug Report) hoặc yêu cầu tính năng mới (Feature Request), vui lòng mở một **Issue** hoặc tạo **Pull Request** trên GitHub repository này[cite: 1, 2].

---
*Chúc bạn có trải nghiệm học tập hiệu quả cùng SolveX!*[cite: 1, 2]

```
