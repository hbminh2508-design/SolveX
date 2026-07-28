# SolveX

Trợ lý làm bài tập chạy trên desktop: chụp đề bài trên màn hình (PDF, trang web,
phần mềm luyện đề), gửi cho Gemini, nhận lời giải có giải thích từng bước. Có
chế độ riêng cho bài **listening** — thu trực tiếp tiếng phát ra loa, chép
transcript rồi trả lời câu hỏi.

---

## 1. Cấu trúc

```
SolveX/
├── main.py              # khởi động ứng dụng
├── requirements.txt
├── solvex.spec          # cấu hình đóng gói .exe
├── build.bat            # script build tự động (Windows)
└── solvex/
    ├── config.py        # lưu API key, model, prompt
    ├── capture.py       # chụp màn hình (mss + Pillow)
    ├── audio.py         # thu tiếng loa qua WASAPI loopback
    ├── gemini.py        # gọi Gemini API
    ├── workers.py       # thread nền, chống đơ giao diện
    ├── style.py         # bảng màu + stylesheet
    └── ui.py            # giao diện chính
```

## 2. Lấy API key

Vào **Google AI Studio** → *Get API key* → tạo key mới. Dán vào ô "API key" ở
góc trên ứng dụng rồi bấm **Lưu**. Key được ghi vào:

- Windows: `%APPDATA%\SolveX\config.json`
- Linux: `~/.config/SolveX/config.json`

Đây là file văn bản thường, không mã hoá — đừng chia sẻ máy hoặc file này cho
người khác.

## 3. Chạy thử (chưa cần build)

```bash
pip install -r requirements.txt
python main.py
```

## 4. Build ra file .exe

Phải build **trên chính máy Windows** — PyInstaller không cross-compile được từ
Linux sang Windows.

Chép cả thư mục sang máy Windows, rồi bấm đúp `build.bat`. Hoặc gõ tay:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --clean solvex.spec
```

File kết quả: `dist\SolveX.exe` — chạy độc lập, không cần cài Python.

> **Nếu exe mở lên rồi tắt ngay:** sửa `console=False` thành `console=True`
> trong `solvex.spec`, build lại, chạy từ cmd để đọc thông báo lỗi.

> **Windows Defender báo virus:** đây là false positive rất phổ biến với file
> PyInstaller onefile. Thêm ngoại lệ cho thư mục `dist`, hoặc bỏ dòng
> `runtime_tmpdir=None` và build dạng thư mục thay vì onefile.

## 5. Cách dùng

| Thao tác | Phím tắt | Việc xảy ra |
|---|---|---|
| Giải thường | `F2` | Chụp màn hình → gửi Gemini → lời giải từng bước |
| Giải Listening | `F3` | Bấm lần 1 chụp câu hỏi + bắt đầu thu; bấm lần 2 dừng và gửi |
| Gửi tin nhắn | `Ctrl+Enter` | Hỏi thêm về bài vừa giải |

**Nguồn chụp:** chọn màn hình cụ thể, hoặc bấm *Chọn vùng…* rồi kéo chuột quanh
đúng phần đề bài. Chọn vùng cho kết quả tốt hơn nhiều so với chụp cả màn hình,
vì AI không bị nhiễu bởi thanh taskbar và các cửa sổ khác.

**Ẩn cửa sổ khi chụp:** bật tuỳ chọn này nếu SolveX đang che mất đề bài.

**Hướng dẫn AI:** nút này cho phép sửa prompt. Ví dụ thêm "chỉ gợi ý hướng làm,
đừng đưa đáp án ngay" nếu bạn muốn tự làm trước rồi mới đối chiếu.

## 6. Về phần thu âm

Mặc định ứng dụng thu **tiếng phát ra loa** chứ không phải tiếng micro, nên chất
lượng audio sạch và không lẫn tiếng ồn phòng.

- **Windows:** dùng WASAPI loopback, chạy được ngay. Nếu báo lỗi không tìm thấy
  thiết bị loopback, bật *Stereo Mix* trong Control Panel → Sound → Recording.
- **Linux:** cần PulseAudio hoặc PipeWire (Ubuntu có sẵn). Thu qua monitor source.
- **macOS:** hệ điều hành không cho loopback trực tiếp, phải cài BlackHole rồi
  đặt làm output mặc định.

Nếu vẫn không được, bỏ tick "Thu tiếng loa" để chuyển sang micro.

Giới hạn: audio gửi kèm trong request nên nên giữ dưới ~7 phút. Bài dài hơn thì
chia thành nhiều lần thu.

## 7. Tên model

Ô **Model** ở góc trên để trống cho bạn sửa. Mặc định là
`gemini-3.5-flash-lite`. Tên model Gemini thay đổi khá thường xuyên — nếu gặp
lỗi *404 không tìm thấy model*, mở Google AI Studio xem tên chính xác hiện hành
rồi dán lại vào ô đó. Không cần build lại exe.

## 8. Vài lưu ý khi dùng

Công cụ này hợp lý nhất khi bạn dùng nó để **hiểu bài**: đọc lời giải, hỏi lại
những chỗ chưa rõ trong ô chat, rồi tự làm lại. Prompt mặc định được viết theo
hướng đó — luôn yêu cầu AI giải thích lý do từng bước thay vì đưa đáp án suông.

AI vẫn sai, nhất là với bài toán nhiều bước và bài nghe có tạp âm. Luôn kiểm tra
lại đáp án thay vì tin tuyệt đối. Và tất nhiên, đừng dùng trong kỳ thi hay bài
kiểm tra có giám sát — vừa vi phạm quy chế, vừa mất luôn cái lợi ích học tập mà
công cụ sinh ra để phục vụ.
