"""Số phiên bản và nhật ký cập nhật (release notes) của SolveX."""

APP_VERSION = "1.8.5.95f08eb"

# Mỗi mục: (phiên bản, ngày phát hành, [danh sách thay đổi])
CHANGELOG = [
    (
        "1.8.5.95f08eb",
        "2026-08-13",
        [
            "Nâng cấp bộ chuyển đổi Markdown & tích hợp bộ dịch công thức toán học MathJax 3 cho tất cả các cửa sổ hiển thị (AnswerWindow, MainWindow Chat, Tab Lịch Sử).",
            "Khắc phục triệt để lỗi hiển thị code thô (raw code) trong cửa sổ đáp án.",
            "Tự động chuyển đổi các ký hiệu toán học LaTeX (phân số, căn thức, tích phân, ma trận...) dạng $inline$ và $$display$$ thành ký hiệu toán học chuẩn mực sắc nét như sách giáo khoa.",
        ],
    ),
    (
        "1.8.4.90cf404",
        "2026-08-13",
        [
            "Khắc phục triệt để lỗi Windows không tìm thấy file ('Windows cannot find SolveX Builder') khi mở cửa sổ Build .exe độc lập.",
            "Sử dụng cờ khởi tạo hệ thống CREATE_NEW_CONSOLE trực tiếp từ Python Subprocess giúp mở cửa sổ console build độc lập mượt mà 100%.",
        ],
    ),
    (
        "1.8.3.1cc391c",
        "2026-08-13",
        [
            "Tách tiến trình Build .exe tự động sang cửa sổ ứng dụng độc lập (solvex/builder.py), đảm bảo khi tắt SolveX chính thì việc Build file .exe vẫn tiếp diễn 100%.",
            "Bổ sung tính năng ⭐ Lưu Câu Hỏi Khó (Bookmark Difficult Questions): Thêm nút [⭐ Lưu Câu Hỏi Khó] trực tiếp trong cửa sổ hiển thị lời giải.",
            "Lưu trữ dữ liệu câu hỏi khó persistent vào local storage: APPDATA/SolveX/saved_questions.json.",
            "Bổ sung bộ lọc ⭐ Câu Hỏi Khó Saved trong Tab Lịch Sử cho phép bấm mở xem lại ảnh chụp & lời giải chi tiết bất cứ lúc nào.",
        ],
    ),
    (
        "1.8.2.248963c",
        "2026-08-13",
        [
            "Thêm 2 tuỳ chọn Cài đặt linh hoạt cho tính năng đọc đáp án giọng nói (TTS Reader):",
            "1. Checkbox [🔊 Bật/Tắt nút đọc đáp án giọng nói trong cửa sổ lời giải].",
            "2. Checkbox [⚡ Tự động đọc đáp án ngay khi AI giải xong].",
            "Cập nhật danh sách gợi ý tính năng đột phá đề xuất cho phiên bản v1.9 tiếp theo.",
        ],
    ),
    (
        "1.8.1.f3014a4",
        "2026-08-12",
        [
            "Khắc phục triệt để lỗi HTTP Error 404 khi tải file cập nhật bằng cơ chế thông minh nhận diện GitHub Release Assets.",
            "Tự động tìm kiếm file SolveX.exe đính kèm từ GitHub Releases hoặc nạp file build sẵn mượt mà không gây ngắt đoạn ứng dụng.",
            "Bổ sung luồng hỏi ý kiến người dùng để chuyển hướng tới GitHub Repository hoặc tự động Build file .exe nếu chưa có release binary.",
        ],
    ),
    (
        "1.8.0.2e29047",
        "2026-08-12",
        [
            "Tái thiết kế Icon Cài Đặt (bánh răng WinUI 3) 6 răng tỉ lệ chuẩn xa xỉ, đường nét thanh lịch và tinh tế.",
            "Bổ sung tính năng 🔊 Đọc Lời Giải Giọng Nói AI (Text-to-Speech Voice Reader) ngay trong cửa sổ hiển thị đáp án.",
            "Gợi ý các tính năng đột phá mới cho phiên bản v1.8: Trình soạn thảo công thức toán LaTeX 1-Click, Phím tắt Mini Floating Card toàn hệ thống, Xuất file PDF / HTML in ấn bài tập chuyên nghiệp.",
        ],
    ),
    (
        "1.7.3.7c70908",
        "2026-08-12",
        [
            "Bổ sung hệ thống Tải Bản Cập Nhật Trực Tiếp Trong Ứng Dụng (In-App Direct Update Downloader).",
            "Hiển thị tiến độ tải về thời gian thực: % phần trăm (0% -> 100%), dung lượng đã tải, tốc độ (MB/s) và thời gian còn lại (ETA).",
            "Hộp thoại hỏi cài đặt tự động khi tải hoàn tất: Khởi chạy file .exe mới và tự đóng ứng dụng cũ mượt mà.",
            "Tối ưu hóa hiệu năng tải file bằng tiến trình luồng ẩn bất đồng bộ.",
        ],
    ),
    (
        "1.7.2.3660273",
        "2026-08-12",
        [
            "Tái thiết kế Icon Máy Ảnh Chụp Đề sắc nét và chuẩn máy ảnh thật (Camera Body + Lens + Shutter button).",
            "Tái thiết kế Icon Nút Top Bar Nổi thành thanh ngang ở dưới có mũi tên chỉ lên (↑).",
            "Bổ sung bộ chọn Chế Độ Giải Bài (Mode Combo) trực tiếp trên Thanh Top Bar Nổi (Compact Bar).",
            "Tích hợp Chế độ Giao diện Tự động theo Hệ điều hành (Auto OS Theme) phát hiện chuẩn Windows Dark/Light.",
            "Đồng bộ Cài đặt Tức thì (Live Settings Sync): Chuyển chủ đề hoặc ngôn ngữ tự áp dụng lập tức.",
            "Tự động dừng tiến trình SolveX.exe cũ đang chạy để tránh lỗi khóa file khi build ứng dụng.",
            "Bổ sung trang Hướng Dẫn Sử Dụng chi tiết và minh họa dễ hiểu.",
        ],
    ),
    (
        "1.7.1.b599aee",
        "2026-08-12",
        [
            "Nâng cấp cấu trúc phiên bản & kiểm tra cập nhật online theo định dạng 'X.y.z.mã_build' (1.7.1.b599aee).",
            "Tự động so sánh số phiên bản chính (1.7.1) kết hợp mã Build Commit và Git Tag khi kiểm tra cập nhật online.",
            "Tái thiết kế Icon nút Thu Khay Hệ Thống hiển thị dưới dạng Mũi tên chỉ xuống (↓) tối giản chuẩn WinUI 3.",
            "Tái thiết kế Icon nút 'Có gì mới' hiển thị dưới dạng Dấu chấm than (!).",
            "Cải thiện độ phản hồi của giao diện người dùng trên Windows 11.",
        ],
    ),
    (
        "1.7",
        "2026-08-02",
        [
            "Đồng bộ biểu tượng khay hệ thống (System Tray Icon) sử dụng chính xác Logo thương hiệu SolveX cao cấp.",
            "Chuyển cơ chế Kiểm Tra Cập Nhật sang chế độ thông báo trực quan cho người dùng tự xem và tải về từ GitHub (không tự động đóng gói file background).",
            "Tái thiết kế giao diện WinUI 3 Modern & Friendly: Thẻ Card bo góc 16px mềm mại, độ tương phản dịu mắt, khoảng cách bố cục thoáng và thân thiện với người dùng.",
            "Tối ưu hoá hiệu năng phản hồi AI Gemini và làm mượt thao tác chuyển đổi các Tab chức năng.",
        ],
    ),
    (
        "1.6.8be0708",
        "2026-08-02",
        [
            "Cập nhật định dạng hiển thị phiên bản chính xác theo mã Git Commit Hash ngắn: '1.6.8be0708'.",
            "Tích hợp Bộ Chọn Chế Độ Học Tập AI (AI Study & Exam Modes): Giải chi tiết từng bước, Giải trắc nghiệm siêu tốc, Tạo bài tập luyện tập tương tự, Giải thích khái niệm lý thuyết.",
            "Bổ sung tính năng Xuất Lịch Sử Trò Chuyện & Lời Giải ra file Markdown (.md) và HTML tiện lợi cho việc in ấn hoặc lưu trữ tài liệu học tập.",
            "Nâng cấp giao diện người dùng WinUI 3 Ultra: Thẻ Card viền Specular Highlight thanh lịch, hiệu ứng active mượt mà và khoảng cách bố cục tối ưu.",
            "Cải thiện tốc độ phản hồi AI Gemini và tích hợp bộ lọc từ khoá thông minh trong tab Lịch Sử Trò Chuyện.",
        ],
    ),
    (
        "1.5.1",
        "2026-08-01",
        [
            "Khắc phục triệt để vệt đen đè lên các nhãn chữ (SolveX, Trợ lý AI, Header) trên giao diện ứng dụng.",
            "Tối ưu Font chữ đa ngôn ngữ chuẩn Unicode ('Segoe UI', 'Segoe UI Variable Text', 'Arial') mượt mà cho Tiếng Việt và Tiếng Anh.",
            "Tái thiết kế Icon Dark Mode (Mặt trăng khuyết) chính xác hình học và tinh tế hơn.",
            "Đổi tên mục điều hướng 'Có gì mới' gọn gàng (xoá số phiên bản 1.3.0 cũ trên nhãn nút).",
            "Bổ sung nút Sao Chép Đáp Án 1-Click trong cửa sổ hiển thị kết quả giải bài.",
            "Bổ sung ô Tìm kiếm từ khoá tức thì trong Lịch Sử Trò Chuyện.",
            "Tối ưu hiển thị Icon khay hệ thống (System Tray) nét căng chuẩn DPI.",
        ],
    ),
    (
        "1.5.0",
        "2026-08-01",
        [
            "Khắc phục triệt để lỗi không đồng bộ cài đặt (chủ đề giao diện, ngôn ngữ hiển thị) trên trang Cài Đặt Hệ Thống.",
            "Tối giản giao diện WinUI 3 Fluent tiêu chuẩn, thiết kế thanh lịch, hiển thị tiêu đề chuẩn 'SolveX v1.5.0'.",
            "Đưa bộ biểu tượng Vector Icons về thiết kế nét mảnh 1.5px phẳng WinUI 3 sang trọng, tinh tế.",
            "Tối ưu hoá tiến trình giải bài và phản hồi câu hỏi AI Gemini nhanh hơn, mượt hơn.",
            "Phát hành phiên bản 1.5.0 hoàn chỉnh và hỗ trợ cập nhật tự động.",
        ],
    ),
    (
        "1.4.0",
        "2026-08-01",
        [
            "Đập đi xây lại toàn bộ UI/UX theo phong cách Liquid Glass 3.0 (WinUI 3 Liquid Acrylic) siêu sang trọng.",
            "Tái thiết kế 100% bộ Master Icons v3.0 vẽ nét đồ hoạ kỹ thuật cao cấp, tỉ lệ hình học xa xỉ chuẩn thiết kế 2026.",
            "Loại bỏ nhóm nút bấm trùng lặp trên thanh HeaderBar (Dark/Light, Ngôn ngữ, Top Bar nổi, Cập nhật GitHub) giúp giao diện gọn gàng, tinh tế hơn.",
            "Nâng cấp độ bo góc 18px mềm mại trên toàn bộ thẻ Card, Sidebar nổi và khung trò chuyện.",
            "Cải thiện hiệu năng xử lý đồ hoạ QSS và hỗ trợ kiểm tra cập nhật online lên v1.4.0.",
        ],
    ),
    (
        "1.3.1",
        "2026-08-01",
        [
            "Làm mới giao diện theo phong cách Kính Mờ (Glassmorphism & Windows 11 Acrylic) siêu sang trọng, tối ưu hiệu năng mượt mà.",
            "Tái thiết kế 100% bộ Vector Icons 2.0 theo phong cách đường nét nét mảnh tỉ lệ 1.75px cao cấp, hiện đại.",
            "Nâng cấp bo góc 16px vô cùng mềm mại trên toàn bộ Floating Sidebar, Thẻ điều khiển (Cards) và Khung hội thoại.",
            "Tối ưu hoá hiệu ứng chuyển trang và làm mới giao diện kính mờ cả ở Dark Mode và Light Mode.",
            "Tích hợp sẵn sàng cho hệ thống Cập nhật Online trực tiếp thông qua ứng dụng.",
        ],
    ),
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
            "Bảng điều khiển giờ là một cửa sổ thật: có nút riêng để thu xuống khay hệ thống.",
        ],
    ),
    (
        "1.0.0",
        "2026-07-29",
        [
            "Phát hành SolveX: chụp đề bài, giải bài thường và giải bài nghe (Listening) bằng Gemini API.",
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
