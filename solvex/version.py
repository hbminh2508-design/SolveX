"""Số phiên bản và nhật ký cập nhật (release notes) của SolveX."""

APP_VERSION = "1.3.0"

# Mỗi mục: (phiên bản, ngày phát hành, [danh sách thay đổi])
CHANGELOG = [
    (
        "1.3.0",
        "2026-08-01",
        [
            "Tải lại toàn bộ giao diện theo chuẩn thiết kế 2026 với thanh Sidebar nổi (Floating Sidebar) bo góc 14px mềm mại.",
            "Bổ sung thanh Menu Bar chuẩn trên cùng (Tệp, Giao diện, Ngôn ngữ, Cài đặt, Trợ giúp).",
            "Tích hợp hệ thống Kiểm tra Cập nhật Online từ GitHub Repository chính thức: hbminh2508-design/SolveX.",
            "Thay thế 100% biểu tượng trong toàn bộ ứng dụng bằng bộ Vector Icon vẽ bằng mã code QPainterPath sắc nét, hoàn toàn không dùng emoji.",
            "Tích hợp tiến trình tự động đóng gói ứng dụng .exe qua PyInstaller khi phát hiện bản mới.",
        ],
    ),
    (
        "1.2.0",
        "2026-08-01",
        [
            "Thêm phần Cài đặt hoàn chỉnh hỗ trợ 2 thứ tiếng: Tiếng Việt và Tiếng Anh (English).",
            "Thêm tuỳ chọn Chế độ hiển thị mặc định khi khởi động: Cửa sổ đầy đủ, Thanh Top Bar thu gọn, hoặc Khay hệ thống.",
            "Tích hợp nút 'Kiểm tra kết nối' Gemini API Key trực tiếp trong mục Cài đặt.",
            "Thêm mục 'Hướng dẫn sử dụng' ứng dụng chi tiết với sơ đồ làm bài, bảng phím tắt và mẹo hỏi AI.",
            "Triệt tiêu hoàn toàn hiện tượng khựng/lag (stuttering) khi bấm giải bài bằng tiến trình xử lý chụp màn hình bất đồng bộ.",
            "Thêm Lịch sử trò chuyện và lưu vào dữ liệu hệ thống (JSON) kèm theo lưu trữ ảnh chụp từng câu hỏi.",
            "Hiển thị thumbnail ảnh chụp đính kèm trực tiếp trong ô câu hỏi của người dùng và cho phép bấm phóng to xem chi tiết.",
            "Đập đi xây lại giao diện chính theo chuẩn WinUI 3 Fluent Design với thanh điều hướng Sidebar hiện đại.",
            "Thay thế toàn bộ emoji bằng bộ Vector Icon WinUI 3 vẽ bằng mã code sắc nét trên thanh Top Bar và bảng điều khiển.",
        ],
    ),
    (
        "1.1.0",
        "2026-07-30",
        [
            "Giao diện làm mới theo phong cách Fluent/WinUI3, đồng bộ với Windows 11.",
            "Thêm logo nhận diện riêng cho SolveX — dùng làm icon ứng dụng và icon khay hệ thống.",
            "Bảng điều khiển giờ là một cửa sổ thật: có nút riêng để thu xuống khay hệ "
            "thống, đặt cạnh 3 nút thu nhỏ / phóng to / đóng quen thuộc.",
            "Thêm ô 'Đang giải…' hiện góc màn hình khi bấm giải bài lúc đang ở chế độ "
            "khay hệ thống, để biết ứng dụng đang xử lý chứ không phải bị treo.",
            "Sửa lỗi ẩn cửa sổ trước khi chụp bị trễ khiến ảnh chụp dính cả cửa sổ SolveX.",
            "Sửa lỗi ảnh xem trước đôi khi không cập nhật sau mỗi lần chụp.",
            "Thêm cửa sổ popup hiện đáp án ngay sau khi giải xong.",
            "Thêm mục xem Nhật ký cập nhật (Release Notes) ngay trong ứng dụng.",
        ],
    ),
    (
        "1.0.0",
        "2026-07-29",
        [
            "Phát hành SolveX: chụp đề bài, giải bài thường và giải bài nghe (Listening) "
            "bằng Gemini API.",
            "Chọn vùng chụp tuỳ ý hoặc chụp theo từng màn hình.",
            "Chat hỏi thêm về lời giải ngay trong ứng dụng.",
        ],
    ),
]


def changelog_markdown() -> str:
    blocks = []
    for version, date, notes in CHANGELOG:
        lines = [f"## SolveX {version} — {date}"]
        lines += [f"- {note}" for note in notes]
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)
