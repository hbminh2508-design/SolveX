"""Số phiên bản và nhật ký cập nhật (release notes) của SolveX."""

APP_VERSION = "1.1.0"

# Mỗi mục: (phiên bản, ngày phát hành, [danh sách thay đổi])
CHANGELOG = [
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
