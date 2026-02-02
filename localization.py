"""
Localization module for Storage Manager
Supports English and Vietnamese
"""

# All translatable strings
TRANSLATIONS = {
    'vi': {
        # Window title
        'app_title': 'Storage Manager - Quản lý File Trùng lặp & Kích thước',
        
        # Menu
        'menu_file': 'File',
        'menu_exit': 'Thoát',
        'menu_theme': '🎨 Giao diện',
        'menu_language': '🌐 Ngôn ngữ',
        'menu_help': 'Trợ giúp',
        'menu_about': 'Giới thiệu',
        'menu_instructions': 'Hướng dẫn',
        
        # Language options
        'lang_vietnamese': '🇻🇳 Tiếng Việt',
        'lang_english': '🇺🇸 English',
        
        # Theme options
        'theme_light': '☀️ Sáng',
        'theme_dark': '🌙 Tối',
        
        # Tab names
        'tab_duplicate': '🔍 Tìm File Trùng Lặp',
        'tab_size_filter': '📊 Lọc Theo Kích Thước',
        'tab_file_type': '📁 Phân Loại Định Dạng',
        
        # Common buttons
        'btn_add_folder': 'Thêm Thư Mục',
        'btn_scan_all_drives': 'Quét Tất Cả Ổ',
        'btn_remove_folder': 'Xóa Thư Mục',
        'btn_clear_all': 'Xóa Tất Cả',
        'btn_start_scan': 'Bắt Đầu Quét',
        'btn_cancel_scan': 'Hủy Quét',
        'btn_select_all': 'Chọn Tất Cả',
        'btn_deselect_all': 'Bỏ Chọn Tất Cả',
        'btn_delete_selected': 'Xóa Đã Chọn',
        'btn_auto_select': 'Tự Động Chọn (Giữ Mới Nhất)',
        
        # File search tab
        'lbl_search_scope': 'Phạm Vi Tìm Kiếm',
        'lbl_search_options': 'Tùy Chọn Tìm Kiếm',
        'lbl_filename': 'Tên file:',
        'lbl_search_help': '💡 Nhập một phần tên file (không phân biệt hoa/thường)',
        'btn_start_search': 'Bắt Đầu Tìm Kiếm',
        'btn_cancel_search': 'Hủy Tìm Kiếm',
        'lbl_files_searched': 'Đã quét {scanned} files, tìm thấy {found}',
        'lbl_search_complete': '✓ Hoàn thành! Tìm thấy {count} files. Tổng dung lượng: {size} ({time}s)',
        'dlg_enter_filename': 'Vui lòng nhập tên file cần tìm',
        'dlg_select_search_folder': 'Vui lòng chọn thư mục để tìm kiếm',
        'lbl_total_files': 'Tổng: {count} files - {size}',
        
        # Labels
        'lbl_scan_scope': 'Phạm Vi Quét',
        'lbl_progress': 'Tiến Trình',
        'lbl_min_size': 'Kích Thước Tối Thiểu:',
        'lbl_ready': 'Sẵn sàng quét',
        'lbl_filter_options': 'Tùy Chọn Lọc',
        'lbl_find_file': 'Tìm file:',
        'lbl_larger_than': 'Lớn hơn',
        'lbl_smaller_than': 'Nhỏ hơn',
        'lbl_size': 'Kích thước:',
        'lbl_file_types': 'Loại File',
        
        # Duplicate finder
        'lbl_duplicates': 'File Trùng Lặp',
        'lbl_no_duplicates': 'Chưa tìm thấy file trùng lặp',
        'lbl_found_groups': 'Tìm thấy {groups} nhóm trùng lặp với {files} file tổng cộng',
        'lbl_found_duplicates': 'Tìm thấy {groups} nhóm trùng lặp ({files} file). Dung lượng có thể giải phóng: {size}',
        
        # Size filter
        'lbl_files_found': 'File Tìm Thấy',
        'lbl_no_files': 'Chưa tìm thấy file',
        'lbl_found_files': 'Tìm thấy {count} file. Tổng dung lượng: {size}',
        'lbl_total': 'Tổng: {count} file, {size}',
        'lbl_selected': 'Chọn: {count} file, {size}',
        
        # File type filter
        'lbl_file_type_results': 'Kết Quả Phân Loại',
        
        # Table headers
        'col_select': 'Chọn',
        'col_group': 'Nhóm',
        'col_type': 'Loại',
        'col_name': 'Tên File',
        'col_size': 'Kích Thước',
        'col_modified': 'Ngày Sửa',
        'col_path': 'Đường Dẫn',
        
        # File types
        'type_images': '🖼️ Hình ảnh',
        'type_videos': '🎬 Video',
        'type_audio': '🎵 Âm thanh',
        'type_documents': '📄 Tài liệu',
        'type_archives': '📦 File nén',
        'type_code': '💻 Code',
        'type_others': '📎 Khác',
        'type_installers': '⚙️ File cài đặt',
        'type_temp': '🗑️ File tạm (Nâng cao ⚠️)',
        'type_count': 'loại',
        
        # Progress messages
        'progress_scanning': 'Đang quét: {path}',
        'progress_found_files': 'Tìm thấy {count} file...',
        'progress_grouping': 'Đang nhóm theo kích thước...',
        'progress_quick_hash': 'Đang tính quick hash ({current}/{total})...',
        'progress_full_hash': 'Đang tính full hash ({current}/{total})...',
        'progress_complete': 'Hoàn tất! Tìm thấy {groups} nhóm trùng lặp',
        'progress_cancelled': 'Đã hủy quét',
        'progress_found_size': 'Tìm thấy {count} file. Tổng dung lượng: {size}',
        'progress_no_match': 'Không tìm thấy file phù hợp',
        'progress_quick_compare': 'So sánh nhanh',
        'progress_detailed_check': 'Kiểm tra chi tiết',
        
        # Messages
        'msg_no_groups': 'Không có nhóm trùng lặp để chọn',
        'msg_select_file_type': 'Vui lòng chọn ít nhất một loại file để quét',
        'msg_confirm_scan_all': 'Đồng ý quét tất cả ổ đĩa?',
        
        # Dialogs
        'dlg_confirm_delete': 'Xác nhận xóa',
        'dlg_delete_count': 'Chuyển {count} file vào Thùng Rác?',
        'dlg_delete_success': '✓ Đã chuyển {count} file vào Thùng Rác',
        'dlg_delete_skipped': '⚠ Bỏ qua {count} file (đã bị xóa hoặc di chuyển)',
        'dlg_delete_failed': '✗ Không thể xóa {count} file',
        'dlg_no_selection': 'Vui lòng chọn file để xóa',
        'dlg_no_selection_title': 'Chưa Chọn File',
        'dlg_no_folders': 'Vui lòng chọn thư mục để quét',
        'dlg_no_folders_title': 'Chưa Chọn Thư Mục',
        'dlg_invalid_input': 'Vui lòng nhập số hợp lệ cho kích thước',
        'dlg_invalid_input_title': 'Đầu Vào Không Hợp Lệ',
        'dlg_select_folder': 'Vui lòng chọn thư mục để xóa',
        'dlg_success': 'Thành Công',
        'dlg_partial_success': 'Thành Công Một Phần',
        'dlg_failed': 'Thất Bại',
        'dlg_error': 'Lỗi',
        'dlg_info': 'Thông báo',
        'dlg_warning': 'Cảnh báo',
        
        # Total/Selected labels
        'lbl_total_selected': 'Tổng: {total_count} file, {total_size} | Chọn: {sel_count} file, {sel_size}',
        
        # Status bar
        'status_ready': 'Sẵn sàng',
        'status_scanning': 'Đang quét...',
        'status_cache_cleanup': 'Đã dọn dẹp cache: xóa {count} mục cũ',
        
        # About dialog
        'about_title': 'Giới thiệu Storage Manager',
        'about_text': '''Storage Manager v2.0

Công cụ quét và dọn dẹp file hệ thống.

Tính năng:
• Quét tự động toàn bộ hệ thống
• Tìm file lớn trên tất cả ổ đĩa
• Bảo vệ thư mục hệ thống
• Xóa an toàn (vào Thùng rác)

Thư mục được bảo vệ:
✓ Windows (System32, DLLs)
✓ Program Files (ứng dụng đã cài)
✓ AppData (cài đặt & save game)
✓ Thư mục khôi phục hệ thống

Phát triển với Python và Tkinter

© 2026''',

        # Instructions dialog
        'instructions_title': 'Hướng dẫn sử dụng',
        'instructions_text': '''Cách sử dụng Storage Manager:

QUÉT TỰ ĐỘNG HỆ THỐNG:
• Tất cả ổ đĩa được tải tự động (C:/, D:/, v.v.)
• Thư mục hệ thống được bảo vệ và loại trừ
• Sẵn sàng quét ngay khi mở!

TÌM FILE THEO KÍCH THƯỚC:
1. Chọn điều kiện: "Lớn hơn" hoặc "Nhỏ hơn"
2. Nhập kích thước (vd: 100) và đơn vị (MB, GB)
3. Nhấn "Bắt Đầu Quét" - quét toàn bộ hệ thống
4. Xem kết quả sắp xếp theo kích thước
5. Chọn file muốn xóa
6. Nhấn "Xóa Đã Chọn"

THƯ MỤC ĐƯỢC BẢO VỆ (Không quét):
✓ C:/Windows - File hệ điều hành
✓ Program Files - Ứng dụng đã cài
✓ AppData - Cài đặt ứng dụng và save game
✓ Thư mục khôi phục hệ thống

THƯ MỤC AN TOÀN (Sẽ được quét):
✓ Desktop, Documents, Downloads
✓ Pictures, Videos, Music
✓ Các thư mục do người dùng tạo

TÍNH NĂNG AN TOÀN:
• Tất cả xóa đều vào Thùng rác (khôi phục được)
• Thư mục hệ thống quan trọng tự động loại trừ
• Xác nhận trước khi xóa
• Hủy quét bất cứ lúc nào'''
    },
    
    'en': {
        # Window title
        'app_title': 'Storage Manager - Duplicate & Size File Manager',
        
        # Menu
        'menu_file': 'File',
        'menu_exit': 'Exit',
        'menu_theme': '🎨 Theme',
        'menu_language': '🌐 Language',
        'menu_help': 'Help',
        'menu_about': 'About',
        'menu_instructions': 'Instructions',
        
        # Language options
        'lang_vietnamese': '🇻🇳 Tiếng Việt',
        'lang_english': '🇺🇸 English',
        
        # Theme options
        'theme_light': '☀️ Light',
        'theme_dark': '🌙 Dark',
        
        # Tab names
        'tab_duplicate': '🔍 Find Duplicates',
        'tab_size_filter': '📊 Filter by Size',
        'tab_file_type': '📁 File Types',
        
        # Common buttons
        'btn_add_folder': 'Add Folder',
        'btn_scan_all_drives': 'Scan All Drives',
        'btn_remove_folder': 'Remove Folder',
        'btn_clear_all': 'Clear All',
        'btn_start_scan': 'Start Scan',
        'btn_cancel_scan': 'Cancel Scan',
        'btn_select_all': 'Select All',
        'btn_deselect_all': 'Deselect All',
        'btn_delete_selected': 'Delete Selected',
        'btn_auto_select': 'Auto Select (Keep Newest)',
        
        # File search tab
        'lbl_search_scope': 'Search Scope',
        'lbl_search_options': 'Search Options',
        'lbl_filename': 'Filename:',
        'lbl_search_help': '💡 Enter part of file name (case-insensitive)',
        'btn_start_search': 'Start Search',
        'btn_cancel_search': 'Cancel Search',
        'lbl_files_searched': 'Scanned {scanned} files, found {found}',
        'lbl_search_complete': '✓ Complete! Found {count} files. Total size: {size} ({time}s)',
        'dlg_enter_filename': 'Please enter a filename to search',
        'dlg_select_search_folder': 'Please select a folder to search',
        'lbl_total_files': 'Total: {count} files - {size}',
        
        # Labels
        'lbl_scan_scope': 'Scan Scope',
        'lbl_progress': 'Progress',
        'lbl_min_size': 'Minimum Size:',
        'lbl_ready': 'Ready to scan',
        'lbl_filter_options': 'Filter Options',
        'lbl_find_file': 'Find files:',
        'lbl_larger_than': 'Larger than',
        'lbl_smaller_than': 'Smaller than',
        'lbl_size': 'Size:',
        'lbl_file_types': 'File Types',
        
        # Duplicate finder
        'lbl_duplicates': 'Duplicate Files',
        'lbl_no_duplicates': 'No duplicate files found',
        'lbl_found_groups': 'Found {groups} duplicate groups with {files} files total',
        'lbl_found_duplicates': 'Found {groups} duplicate groups ({files} files). Space to free: {size}',
        
        # Size filter
        'lbl_files_found': 'Files Found',
        'lbl_no_files': 'No files found',
        'lbl_found_files': 'Found {count} files. Total size: {size}',
        'lbl_total': 'Total: {count} files, {size}',
        'lbl_selected': 'Selected: {count} files, {size}',
        
        # File type filter
        'lbl_file_type_results': 'File Type Results',
        
        # Table headers
        'col_select': 'Select',
        'col_group': 'Group',
        'col_type': 'Type',
        'col_name': 'File Name',
        'col_size': 'Size',
        'col_modified': 'Modified',
        'col_path': 'Path',
        
        # File types
        'type_images': '🖼️ Images',
        'type_videos': '🎬 Videos',
        'type_audio': '🎵 Audio',
        'type_documents': '📄 Documents',
        'type_archives': '📦 Archives',
        'type_code': '💻 Code',
        'type_others': '📎 Others',
        'type_installers': '⚙️ Installers',
        'type_temp': '🗑️ Temp Files (Advanced ⚠️)',
        'type_count': 'types',
        
        # Progress messages
        'progress_scanning': 'Scanning: {path}',
        'progress_found_files': 'Found {count} files...',
        'progress_grouping': 'Grouping by size...',
        'progress_quick_hash': 'Calculating quick hash ({current}/{total})...',
        'progress_full_hash': 'Calculating full hash ({current}/{total})...',
        'progress_complete': 'Complete! Found {groups} duplicate groups',
        'progress_cancelled': 'Scan cancelled',
        'progress_found_size': 'Found {count} files. Total size: {size}',
        'progress_no_match': 'No matching files found',
        'progress_quick_compare': 'Quick compare',
        'progress_detailed_check': 'Detailed check',
        
        # Messages
        'msg_no_groups': 'No duplicate groups to select',
        'msg_select_file_type': 'Please select at least one file type to scan',
        'msg_confirm_scan_all': 'Scan all drives?',
        
        # Dialogs
        'dlg_confirm_delete': 'Confirm Delete',
        'dlg_delete_count': 'Move {count} files to Recycle Bin?',
        'dlg_delete_success': '✓ Moved {count} files to Recycle Bin',
        'dlg_delete_skipped': '⚠ Skipped {count} files (deleted or moved)',
        'dlg_delete_failed': '✗ Failed to delete {count} files',
        'dlg_no_selection': 'Please select files to delete',
        'dlg_no_selection_title': 'No Selection',
        'dlg_no_folders': 'Please select folders to scan',
        'dlg_no_folders_title': 'No Folders Selected',
        'dlg_invalid_input': 'Please enter a valid number for size',
        'dlg_invalid_input_title': 'Invalid Input',
        'dlg_select_folder': 'Please select a folder to remove',
        'dlg_success': 'Success',
        'dlg_partial_success': 'Partial Success',
        'dlg_failed': 'Failed',
        'dlg_error': 'Error',
        'dlg_info': 'Information',
        'dlg_warning': 'Warning',
        
        # Total/Selected labels
        'lbl_total_selected': 'Total: {total_count} files, {total_size} | Selected: {sel_count} files, {sel_size}',
        
        # Status bar
        'status_ready': 'Ready',
        'status_scanning': 'Scanning...',
        'status_cache_cleanup': 'Cache cleanup: removed {count} old entries',
        
        # About dialog
        'about_title': 'About Storage Manager',
        'about_text': '''Storage Manager v2.0

System-wide file scanner and cleanup tool.

Features:
• Automatic full system scan
• Find large files across all drives
• Protected system folders
• Safe deletion (Recycle Bin)

Protected Folders:
✓ Windows (System32, DLLs)
✓ Program Files (installed apps)
✓ AppData (app settings & saves)
✓ System recovery folders

Developed with Python and Tkinter

© 2026''',

        # Instructions dialog
        'instructions_title': 'Instructions',
        'instructions_text': '''How to Use Storage Manager:

AUTOMATIC SYSTEM SCAN:
• All drives are loaded automatically (C:/, D:/, etc.)
• System folders are protected and excluded
• Ready to scan on startup!

FIND FILES BY SIZE:
1. Choose condition: "Larger than" or "Smaller than"
2. Enter size value (e.g., 100) and unit (MB, GB)
3. Click "Start Scan" - scans entire system
4. Review results sorted by size
5. Select files you want to remove
6. Click "Delete Selected"

PROTECTED FOLDERS (Never Scanned):
✓ C:/Windows - Operating system files
✓ Program Files - Installed applications
✓ AppData - App settings and game saves
✓ System recovery folders

SAFE USER FOLDERS (Will Be Scanned):
✓ Desktop, Documents, Downloads
✓ Pictures, Videos, Music
✓ Other user-created folders

SAFETY FEATURES:
• All deletions go to Recycle Bin (reversible)
• System-critical folders automatically excluded
• Confirmation before deletion
• Cancel scan anytime'''
    }
}


class Localization:
    """Localization manager"""
    
    _current_lang = 'vi'
    _listeners = []
    
    @classmethod
    def get_lang(cls) -> str:
        return cls._current_lang
    
    @classmethod
    def set_lang(cls, lang: str):
        if lang in TRANSLATIONS:
            cls._current_lang = lang
            # Notify all listeners
            for listener in cls._listeners:
                try:
                    listener()
                except:
                    pass
    
    @classmethod
    def add_listener(cls, callback):
        """Add a callback to be called when language changes"""
        if callback not in cls._listeners:
            cls._listeners.append(callback)
    
    @classmethod
    def remove_listener(cls, callback):
        """Remove a language change listener"""
        if callback in cls._listeners:
            cls._listeners.remove(callback)
    
    @classmethod
    def get(cls, key: str, **kwargs) -> str:
        """Get translated string by key"""
        text = TRANSLATIONS.get(cls._current_lang, {}).get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except:
                pass
        return text


# Shortcut function
def t(key: str, **kwargs) -> str:
    """Translate shortcut"""
    return Localization.get(key, **kwargs)
