<p align="center">
  <img src="assets/logo_256.png" width="96" height="96" alt="Logo SolveX">
</p>

<h1 align="center">SolveX</h1>

<p align="center">
  Trợ lý làm bài tập chạy trên desktop Windows — chụp đề trên màn hình, để
  Gemini giải và giảng lại từng bước, không cần rời khỏi bài đang làm.
</p>

---

## Tính năng

- **Chụp & giải bài thường** — chọn vùng màn hình chứa đề (PDF, trang web,
  phần mềm luyện đề...), SolveX chụp và gửi cho Gemini, trả lời kèm giải
  thích từng bước chứ không chỉ đưa đáp án.
- **Giải bài Listening** — thu trực tiếp tiếng phát ra loa (không lẫn tạp âm
  phòng), chép transcript rồi trả lời câu hỏi kèm ảnh đề.
- **Hỏi thêm trong lúc làm bài** — khung chat riêng để hỏi lại những chỗ
  chưa hiểu trong lời giải vừa nhận.
- **Sống ở khay hệ thống** — mặc định SolveX chỉ hiện một bảng điều khiển nhỏ
  gọn (Chụp / Giải thường / Giải Listening) theo phong cách Fluent/WinUI3 của
  Windows 11; đóng nó lại thì thu gọn xuống tray icon, không chiếm chỗ trên
  màn hình hay taskbar.
- **Popup kết quả** — giải xong tự bật cửa sổ hiện đáp án, kèm ô "Đang giải…"
  nhỏ báo tiến trình nếu bạn đang ở chế độ tray.
- **Nhật ký cập nhật** — nút 🆕 trên bảng điều khiển (hoặc menu chuột phải ở
  tray icon) cho xem có gì mới ở từng phiên bản.

## Cài đặt & chạy thử

```bash
pip install -r requirements.txt
python main.py
```

Ứng dụng mở lên là một bảng điều khiển nhỏ nổi giữa màn hình, có icon khay hệ
thống đi kèm. Chuột phải vào bảng điều khiển (hoặc vào icon khay) để vào
**Cài đặt…** — nơi nhập API key, đổi model, sửa prompt và xem lại toàn bộ hội
thoại.

## Lấy API key

Vào **Google AI Studio** → *Get API key* → tạo key mới. Mở **Cài đặt…**, dán
vào ô "API key" rồi bấm **Lưu**. Key được ghi vào:

- Windows: `%APPDATA%\SolveX\config.json`
- Linux: `~/.config/SolveX/config.json`

Đây là file văn bản thường, không mã hoá — đừng chia sẻ máy hoặc file này cho
người khác.

## Cách dùng

**Bảng điều khiển (mặc định khi mở app):**

| Nút | Việc xảy ra |
|---|---|
| 📷 Chụp | Mở lớp phủ để kéo chuột chọn vùng màn hình cần chụp |
| 📝 Giải thường · `F2` | Chụp đề đang hiện → gửi Gemini → lời giải từng bước |
| 🎧 Giải Listening · `F3` | Bấm lần 1: chụp câu hỏi + bắt đầu thu; bấm lần 2: dừng và gửi |
| 🆕 | Xem nhật ký cập nhật (release notes) |
| 🗂 | Thu bảng điều khiển xuống chỉ còn icon khay hệ thống |
| ─ / ▢ / ✕ | Thu nhỏ / phóng to / đóng (đóng cũng chỉ ẩn xuống khay, không thoát app) |

Trong lúc chụp, SolveX tự ẩn bảng điều khiển đi để không bị lẫn vào ảnh chụp,
rồi hiện lại ngay sau đó.

Bấm đúp icon khay hệ thống (hoặc chuột phải → **Hiện bảng điều khiển**) để
lấy lại bảng điều khiển nếu đã ẩn. Chuột phải → **Cài đặt…** để mở cửa sổ đầy
đủ (API key, model, prompt, lịch sử chat). Đóng cửa sổ Cài đặt cũng chỉ ẩn nó
đi — thoát hẳn ứng dụng thì chọn **Thoát SolveX** trong menu khay.

**Nguồn chụp:** trong Cài đặt, chọn màn hình cụ thể hoặc bấm *Chọn vùng…* rồi
kéo chuột quanh đúng phần đề bài. Chọn vùng cho kết quả tốt hơn nhiều so với
chụp cả màn hình, vì AI không bị nhiễu bởi taskbar và các cửa sổ khác.

**Hướng dẫn AI:** trong Cài đặt, nút này cho phép sửa prompt. Ví dụ thêm "chỉ
gợi ý hướng làm, đừng đưa đáp án ngay" nếu bạn muốn tự làm trước rồi mới đối
chiếu.

## Build ra file .exe

Phải build **trên chính máy Windows** — PyInstaller không cross-compile được
từ Linux sang Windows.

Chép cả thư mục sang máy Windows, rồi bấm đúp `build.bat`. Hoặc gõ tay:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --clean solvex.spec
```

File kết quả: `dist\SolveX.exe` — chạy độc lập, không cần cài Python, dùng
sẵn icon SolveX trong `assets/icon.ico`.

> **Nếu exe mở lên rồi tắt ngay:** sửa `console=False` thành `console=True`
> trong `solvex.spec`, build lại, chạy từ cmd để đọc thông báo lỗi.

> **Windows Defender báo virus:** đây là false positive rất phổ biến với file
> PyInstaller onefile. Thêm ngoại lệ cho thư mục `dist`, hoặc bỏ dòng
> `runtime_tmpdir=None` và build dạng thư mục thay vì onefile.

## Về phần thu âm

Mặc định ứng dụng thu **tiếng phát ra loa** chứ không phải tiếng micro, nên
chất lượng audio sạch và không lẫn tiếng ồn phòng.

- **Windows:** dùng WASAPI loopback, chạy được ngay. Nếu báo lỗi không tìm
  thấy thiết bị loopback, bật *Stereo Mix* trong Control Panel → Sound →
  Recording.
- **Linux:** cần PulseAudio hoặc PipeWire (Ubuntu có sẵn). Thu qua monitor
  source.
- **macOS:** hệ điều hành không cho loopback trực tiếp, phải cài BlackHole
  rồi đặt làm output mặc định.

Nếu vẫn không được, bỏ tick "Thu tiếng loa" trong Cài đặt để chuyển sang mic.

Giới hạn: audio gửi kèm trong request nên giữ dưới ~7 phút. Bài dài hơn thì
chia thành nhiều lần thu.

## Tên model

Ô **Model** trong Cài đặt để trống cho bạn sửa. Mặc định là
`gemini-3.5-flash-lite`. Tên model Gemini thay đổi khá thường xuyên — nếu gặp
lỗi *404 không tìm thấy model*, mở Google AI Studio xem tên chính xác hiện
hành rồi dán lại vào ô đó. Không cần build lại exe.

## Có gì mới

Bấm nút **🆕** trên bảng điều khiển (hoặc chuột phải icon khay →
**Xem có gì mới…**) để xem nhật ký cập nhật ngay trong ứng dụng. Nội dung
được quản lý tại [`solvex/version.py`](solvex/version.py).

## Cấu trúc dự án

```
SolveX/
├── main.py               # khởi động ứng dụng
├── requirements.txt
├── solvex.spec           # cấu hình đóng gói .exe
├── build.bat             # script build tự động (Windows)
├── assets/
│   ├── icon.ico          # icon ứng dụng (đa kích thước, dùng cho .exe/tray)
│   └── icon.png / logo_256.png
└── solvex/
    ├── config.py         # lưu API key, model, prompt
    ├── capture.py        # chụp màn hình (mss + Pillow)
    ├── audio.py          # thu tiếng loa qua WASAPI loopback
    ├── gemini.py         # gọi Gemini API
    ├── workers.py        # thread nền, chống đơ giao diện
    ├── style.py          # bảng màu + stylesheet Fluent/WinUI3
    ├── fluent.py         # bật hiệu ứng Mica/tiêu đề tối trên Windows 11
    ├── version.py         # số phiên bản + nhật ký cập nhật
    └── ui.py             # giao diện: bảng điều khiển, cài đặt, popup...
```

## Vài lưu ý khi dùng

Công cụ này hợp lý nhất khi bạn dùng nó để **hiểu bài**: đọc lời giải, hỏi lại
những chỗ chưa rõ trong ô chat, rồi tự làm lại. Prompt mặc định được viết
theo hướng đó — luôn yêu cầu AI giải thích lý do từng bước thay vì đưa đáp án
suông.

AI vẫn sai, nhất là với bài toán nhiều bước và bài nghe có tạp âm. Luôn kiểm
tra lại đáp án thay vì tin tuyệt đối. Và tất nhiên, đừng dùng trong kỳ thi hay
bài kiểm tra có giám sát — vừa vi phạm quy chế, vừa mất luôn cái lợi ích học
tập mà công cụ sinh ra để phục vụ.

## Giấy phép

Repo này chưa kèm giấy phép mã nguồn mở chính thức. Nếu bạn định chia sẻ công
khai, cân nhắc thêm file `LICENSE` (MIT/Apache-2.0...) phù hợp với ý định sử
dụng của bạn.
