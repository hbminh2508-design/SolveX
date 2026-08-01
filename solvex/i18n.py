"""Hệ thống đa ngôn ngữ (Internationalization / i18n) cho SolveX.
Hỗ trợ Tiếng Việt (vi) và English (en).
"""

from PyQt6.QtCore import QObject, pyqtSignal

TRANSLATIONS = {
    "vi": {
        # Menu Bar
        "menu_file": "Tệp",
        "menu_view": "Giao diện",
        "menu_language": "Ngôn ngữ",
        "menu_settings": "Cài đặt",
        "menu_help": "Trợ giúp",
        "menu_exit": "Thoát ứng dụng",

        # Navigation & Tab Titles
        "nav_chat": "Chat & Giải bài",
        "nav_history": "Lịch sử trò chuyện",
        "nav_settings": "Cài đặt hệ thống",
        "nav_guide": "Hướng dẫn sử dụng",
        "nav_changelog": "Có gì mới (v1.3.0)",
        
        # Header & Brand
        "app_title": "SolveX",
        "app_tagline": "Trợ lý làm bài tập AI",
        "status_ready": "Sẵn sàng. Nhập API key để bắt đầu.",
        
        # Header Quick Action Toolbar
        "quick_theme": "Chủ đề",
        "quick_theme_dark": "Dark Mode",
        "quick_theme_light": "Light Mode",
        "quick_lang": "Ngôn ngữ",
        "quick_compact": "Top Bar nổi",
        "quick_update": "Cập nhật GitHub",
        
        # Action Buttons
        "btn_capture": "Chụp màn hình",
        "btn_solve_normal": "Giải bài",
        "btn_solve_listening": "Giải Listening",
        "btn_stop_listen": "Dừng & Giải",
        "btn_recording": "Đang thu audio...",
        "btn_send": "Gửi",
        "btn_new_chat": "Hội thoại mới",
        "btn_save": "Lưu cài đặt",
        "btn_test_api": "Kiểm tra API",
        "btn_check_update": "Kiểm tra GitHub Update",
        "btn_build_exe": "Tự động Build .exe",
        "btn_edit_prompts": "Hướng dẫn AI...",
        "btn_pick_region": "Chọn vùng...",
        "btn_show": "Hiện",
        "btn_hide": "Ẩn",
        "btn_close": "Đóng",
        "btn_delete": "Xoá",
        "btn_clear_all": "Xoá tất cả",
        "btn_view_full": "Xem ảnh lớn",
        
        # Compact Toolbar Tooltips
        "tip_capture": "Chọn vùng màn hình cần chụp",
        "tip_solve": "Chụp đề đang hiện và giải (F2)",
        "tip_listen": "Thu âm bài nghe rồi giải (F3)",
        "tip_history": "Mở lịch sử trò chuyện",
        "tip_settings": "Mở cài đặt",
        "tip_guide": "Mở hướng dẫn sử dụng",
        "tip_changelog": "Xem nhật ký cập nhật v1.3.0",
        "tip_tray": "Thu xuống khay hệ thống",
        
        # Settings UI
        "st_section_general": "CÀI ĐẶT CHUNG & GIAO DIỆN",
        "st_theme": "Chủ đề giao diện (Theme)",
        "st_theme_dark": "Giao diện Tối (Dark Mode)",
        "st_theme_light": "Giao diện Sáng (Light Mode)",
        "st_language": "Ngôn ngữ giao diện",
        "st_startup_mode": "Chế độ hiển thị khi khởi động",
        "st_startup_full": "Cửa sổ đầy đủ (Main Window)",
        "st_startup_compact": "Thanh thu gọn trên Top (Compact Bar)",
        "st_startup_tray": "Thu gọn vào khay hệ thống (System Tray)",
        
        "st_section_api": "CẤU HÌNH GEMINI API",
        "st_api_key": "Gemini API Key",
        "st_api_key_ph": "Dán Gemini API key từ Google AI Studio vào đây",
        "st_model": "Gemini Model",
        "st_test_success": "Kết nối thành công! API Key hoạt động bình thường.",
        "st_test_failed": "Kết nối thất bại: ",
        "st_testing": "Đang kiểm tra kết nối API...",
        
        "st_section_capture": "NGUỒN CHỤP & ÂM THANH",
        "st_capture_source": "Nguồn chụp màn hình",
        "st_monitor_primary": "Màn hình chính",
        "st_monitor_all": "Tất cả màn hình",
        "st_monitor_region": "Vùng chọn tuỳ ý",
        "st_monitor_num": "Màn hình {}",
        "st_region_none": "chưa chọn",
        "st_hide_on_capture": "Luôn tự động ẩn SolveX khi bấm chụp màn hình",
        "st_loopback": "Thu âm từ hệ thống / loa (bỏ tick để thu Micro)",
        
        "st_section_prompts": "HƯỚNG DẪN DÀNH CHO AI (PROMPTS)",
        "st_prompt_normal_lbl": "Prompt cho nút Giải thường:",
        "st_prompt_listen_lbl": "Prompt cho nút Giải Listening:",
        "st_restore_defaults": "Khôi phục mặc định",
        
        "st_section_update": "CẬP NHẬT ONLINE GITHUB & BUILD",
        "st_update_status": "Trạng thái cập nhật GitHub (hbminh2508-design/SolveX)",
        "st_latest_ver": "Phiên bản hiện tại ({}) là mới nhất trên GitHub!",
        
        # History UI
        "hist_title": "Lịch sử trò chuyện",
        "hist_empty": "Chưa có hội thoại nào được lưu.",
        "hist_search_ph": "Tìm kiếm hội thoại...",
        "hist_delete_confirm": "Bạn có chắc muốn xoá hội thoại này?",
        "hist_clear_confirm": "Bạn có chắc muốn xoá TOÀN BỘ lịch sử trò chuyện?",
        "hist_question_img": "Ảnh đề bài đã chụp:",
        "hist_no_title": "Hội thoại không tên",
        
        # Chat UI
        "chat_welcome_title": "Chào mừng bạn đến với SolveX v1.3.0",
        "chat_welcome_desc": "1. Dán Gemini API key trong phần Cài đặt.<br>2. Bấm <b>Giải bài (F2)</b> hoặc <b>Giải Listening (F3)</b>.<br>3. Cửa sổ SolveX sẽ tự động ẩn để bạn nhìn rõ đề bài trên màn hình.<br>4. Lời giải và ảnh chụp sẽ hiển thị ngay tại đây.",
        "chat_input_ph": "Hỏi thêm về bài vừa giải... (Ctrl+Enter để gửi)",
        "chat_user_label": "Bạn",
        "chat_solvex_label": "SolveX",
        "chat_thinking": "SolveX đang đọc đề và suy nghĩ...",
        "chat_listening_thinking": "SolveX đang nghe audio và giải bài...",
        "chat_user_captured": "Đã chụp đề bài — đang giải...",
        "chat_user_listened": "Đã thu {} giây audio + ảnh câu hỏi — đang xử lý...",
        
        # User Guide
        "guide_title": "Hướng dẫn sử dụng SolveX v1.3.0",
        "guide_step1_title": "1. Nhập API Key",
        "guide_step1_desc": "Vào phần <b>Cài đặt</b>, dán API key lấy miễn phí tại <i>Google AI Studio</i> và bấm <b>Kiểm tra API</b>.",
        "guide_step2_title": "2. Giải bài tập qua ảnh (F2)",
        "guide_step2_desc": "Mở đề bài trên màn hình, bấm nút <b>Giải bài</b> hoặc phím <code>F2</code>. Cửa sổ ứng dụng sẽ tự động ẩn đi để bạn chụp chính xác góc đề bài.",
        "guide_step3_title": "3. Giải bài nghe Listening (F3)",
        "guide_step3_desc": "Bấm nút <b>Giải Listening</b> hoặc phím <code>F3</code> để bắt đầu thu âm tiếng loa hoặc micro. Bấm lần nữa để dừng thu và gửi audio cho SolveX dịch & làm bài.",
        "guide_step4_title": "4. Menu Bar & Floating Sidebar 2026",
        "guide_step4_desc": "Dùng Menu Bar trên cùng hoặc thanh Sidebar nổi bo góc 14px hiện đại để mở nhanh Cài đặt, Lịch sử, đổi Dark/Light theme và Kiểm tra GitHub Update.",
        "guide_shortcuts": "Bảng phím tắt nhanh",
        "guide_sc_f2": "F2: Chụp & Giải bài thường",
        "guide_sc_f3": "F3: Bắt đầu / Dừng thu âm Listening",
        "guide_sc_ctrl_enter": "Ctrl + Enter: Gửi tin nhắn hỏi thêm",
    },

    "en": {
        # Menu Bar
        "menu_file": "File",
        "menu_view": "View",
        "menu_language": "Language",
        "menu_settings": "Settings",
        "menu_help": "Help",
        "menu_exit": "Exit Application",

        # Navigation & Tab Titles
        "nav_chat": "Chat & Solve",
        "nav_history": "History",
        "nav_settings": "Settings",
        "nav_guide": "User Guide",
        "nav_changelog": "What's New (v1.3.0)",
        
        # Header & Brand
        "app_title": "SolveX",
        "app_tagline": "AI Homework Assistant",
        "status_ready": "Ready. Enter API key to start.",
        
        # Header Quick Action Toolbar
        "quick_theme": "Theme",
        "quick_theme_dark": "Dark Mode",
        "quick_theme_light": "Light Mode",
        "quick_lang": "Language",
        "quick_compact": "Top Bar",
        "quick_update": "GitHub Update",
        
        # Action Buttons
        "btn_capture": "Capture Screen",
        "btn_solve_normal": "Solve Homework",
        "btn_solve_listening": "Solve Listening",
        "btn_stop_listen": "Stop & Solve",
        "btn_recording": "Recording audio...",
        "btn_send": "Send",
        "btn_new_chat": "New Chat",
        "btn_save": "Save Settings",
        "btn_test_api": "Test API Key",
        "btn_check_update": "Check GitHub Update",
        "btn_build_exe": "Auto Build .exe",
        "btn_edit_prompts": "AI Prompts...",
        "btn_pick_region": "Select Region...",
        "btn_show": "Show",
        "btn_hide": "Hide",
        "btn_close": "Close",
        "btn_delete": "Delete",
        "btn_clear_all": "Clear All",
        "btn_view_full": "View Full Image",
        
        # Compact Toolbar Tooltips
        "tip_capture": "Select screen region to capture",
        "tip_solve": "Capture current screen and solve (F2)",
        "tip_listen": "Record audio and solve listening (F3)",
        "tip_history": "Open conversation history",
        "tip_settings": "Open settings",
        "tip_guide": "Open user guide",
        "tip_changelog": "View v1.3.0 release notes",
        "tip_tray": "Minimize to system tray",
        
        # Settings UI
        "st_section_general": "GENERAL & THEME",
        "st_theme": "UI Theme",
        "st_theme_dark": "Dark Mode",
        "st_theme_light": "Light Mode",
        "st_language": "Interface Language",
        "st_startup_mode": "Startup Mode",
        "st_startup_full": "Full Application Window",
        "st_startup_compact": "Compact Floating Top Bar",
        "st_startup_tray": "System Tray Only",
        
        # API Section
        "st_section_api": "GEMINI API CONFIGURATION",
        "st_api_key": "Gemini API Key",
        "st_api_key_ph": "Paste Gemini API key from Google AI Studio here",
        "st_model": "Gemini Model",
        "st_test_success": "Connection successful! API Key is working properly.",
        "st_test_failed": "Connection failed: ",
        "st_testing": "Testing API connection...",
        
        # Capture Section
        "st_section_capture": "CAPTURE SOURCE & AUDIO",
        "st_capture_source": "Capture Source",
        "st_monitor_primary": "Primary Monitor",
        "st_monitor_all": "All Monitors",
        "st_monitor_region": "Custom Selected Region",
        "st_monitor_num": "Monitor {}",
        "st_region_none": "not selected",
        "st_hide_on_capture": "Always automatically hide SolveX during capture",
        "st_loopback": "Record System Audio / Speaker (uncheck for Microphone)",
        
        # Prompts Section
        "st_section_prompts": "AI SYSTEM INSTRUCTIONS (PROMPTS)",
        "st_prompt_normal_lbl": "Instruction for Normal Solver:",
        "st_prompt_listen_lbl": "Instruction for Listening Solver:",
        "st_restore_defaults": "Restore Defaults",
        
        "st_section_update": "ONLINE GITHUB UPDATE & BUILD",
        "st_update_status": "GitHub Update Status (hbminh2508-design/SolveX)",
        "st_latest_ver": "Current version ({}) is up to date on GitHub!",
        
        # History UI
        "hist_title": "Conversation History",
        "hist_empty": "No saved conversations yet.",
        "hist_search_ph": "Search conversations...",
        "hist_delete_confirm": "Are you sure you want to delete this conversation?",
        "hist_clear_confirm": "Are you sure you want to clear ALL conversation history?",
        "hist_question_img": "Captured Question Screenshot:",
        "hist_no_title": "Untitled Chat",
        
        # Chat UI
        "chat_welcome_title": "Welcome to SolveX v1.3.0",
        "chat_welcome_desc": "1. Enter your Gemini API key in <b>Settings</b>.<br>2. Click <b>Solve Homework (F2)</b> or <b>Solve Listening (F3)</b>.<br>3. SolveX will automatically hide so you can clearly see the problem.<br>4. Solutions and screenshots will appear here.",
        "chat_input_ph": "Ask follow-up questions about the solution... (Ctrl+Enter to send)",
        "chat_user_label": "You",
        "chat_solvex_label": "SolveX",
        "chat_thinking": "SolveX is reading the problem and thinking...",
        "chat_listening_thinking": "SolveX is listening to audio and solving...",
        "chat_user_captured": "Captured screen — solving...",
        "chat_user_listened": "Recorded {} seconds of audio + question image — processing...",
        
        # User Guide
        "guide_title": "SolveX User Guide v1.3.0",
        "guide_step1_title": "1. Enter API Key",
        "guide_step1_desc": "Go to <b>Settings</b>, paste your free API key from <i>Google AI Studio</i>, and click <b>Test API Key</b>.",
        "guide_step2_title": "2. Solve Homework via Image (F2)",
        "guide_step2_desc": "Open problem on screen, press <b>Solve Homework</b> or <code>F2</code>. The app window automatically hides so you can select the exact region.",
        "guide_step3_title": "3. Solve Listening Exercises (F3)",
        "guide_step3_desc": "Press <b>Solve Listening</b> or <code>F3</code> to start recording speaker audio. Press again to stop and submit.",
        "guide_step4_title": "4. Menu Bar & Floating Sidebar 2026",
        "guide_step4_desc": "Use the top Menu Bar or 2026 floating sidebar to quickly open settings, history, toggle themes, or check for GitHub updates.",
        "guide_shortcuts": "Keyboard Shortcuts",
        "guide_sc_f2": "F2: Capture & Solve normal exercise",
        "guide_sc_f3": "F3: Start / Stop listening recording",
        "guide_sc_ctrl_enter": "Ctrl + Enter: Send follow-up question",
    }
}


class I18nManager(QObject):
    language_changed = pyqtSignal(str)

    def __init__(self, current_lang="vi"):
        super().__init__()
        self.lang = current_lang if current_lang in TRANSLATIONS else "vi"

    def set_language(self, lang_code: str):
        if lang_code in TRANSLATIONS and lang_code != self.lang:
            self.lang = lang_code
            self.language_changed.emit(self.lang)

    def t(self, key: str, *args) -> str:
        text = TRANSLATIONS.get(self.lang, {}).get(key) or TRANSLATIONS["vi"].get(key, key)
        if args and "{}" in text:
            return text.format(*args)
        return text


i18n = I18nManager("vi")
