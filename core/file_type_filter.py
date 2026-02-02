"""
File type filter module
"""

import os
from typing import List, Dict, Set, Callable, Optional
from utils.file_scanner import FileScanner


class FileTypeFilter:
    """Filter files based on file type/extension"""
    
    # Define file type groups
    FILE_TYPE_GROUPS = {
        'documents': {
            'name': '📄 Tài liệu',
            'extensions': {'.pdf', '.doc', '.docx', '.xls', '.xlsx', 
                          '.ppt', '.pptx', '.txt', '.rtf', '.odt', '.ods'}
        },
        'images': {
            'name': '🖼 Hình ảnh',
            'extensions': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', 
                          '.webp', '.heic', '.svg', '.ico', '.tiff'}
        },
        'videos': {
            'name': '🎥 Video',
            'extensions': {'.mp4', '.mkv', '.avi', '.mov', '.wmv', 
                          '.flv', '.webm', '.m4v', '.mpg', '.mpeg'}
        },
        'audio': {
            'name': '🎵 Âm thanh',
            'extensions': {'.mp3', '.wav', '.flac', '.m4a', '.aac', 
                          '.ogg', '.wma', '.opus'}
        },
        'archives': {
            'name': '🗜 File nén',
            'extensions': {'.zip', '.rar', '.7z', '.tar', '.gz', 
                          '.bz2', '.xz', '.iso'}
        },
        'executables': {
            'name': '⚙ File cài đặt',
            'extensions': {'.exe', '.msi', '.apk', '.dmg', '.deb', '.rpm'}
        },
        'temporary': {
            'name': '🧹 File tạm (Nâng cao ⚠️)',
            'extensions': {'.tmp', '.temp', '.log', '.bak', '.cache', 
                          '.old', '~'}
        }
    }
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        """
        Initialize file type filter
        
        Args:
            progress_callback: Optional callback for progress updates
        """
        self.scanner = FileScanner(progress_callback)
        self.cancelled = False
    
    def cancel(self):
        """Cancel the current operation"""
        self.cancelled = True
        self.scanner.cancel()
    
    def find_files_by_types(self, directories: List[str],
                           selected_groups: Set[str]) -> List[dict]:
        """
        Find files matching selected type groups
        
        Args:
            directories: List of directory paths to scan
            selected_groups: Set of group keys (e.g., {'images', 'videos'})
            
        Returns:
            List of file info dictionaries matching criteria
        """
        # Collect all extensions from selected groups
        target_extensions = set()
        for group_key in selected_groups:
            if group_key in self.FILE_TYPE_GROUPS:
                target_extensions.update(
                    self.FILE_TYPE_GROUPS[group_key]['extensions']
                )
        
        if not target_extensions:
            return []
        
        # Scan and collect matching files (use optimized method with cached stat)
        matched_files = []
        
        for directory in directories:
            if self.cancelled:
                break
            
            # Use scan_directory_with_stat to avoid double os.stat() call
            for filepath, stat in self.scanner.scan_directory_with_stat(directory):
                if self.cancelled:
                    break
                
                # Get extension directly (faster than full get_file_info for filtering)
                extension = os.path.splitext(filepath)[1].lower()
                
                if extension in target_extensions:
                    # Only get full file_info for matching files
                    file_info = self.scanner.get_file_info(filepath, cached_stat=stat)
                    file_info['group'] = self._get_group_for_extension(extension)
                    matched_files.append(file_info)
        
        return matched_files
    
    def _get_group_for_extension(self, extension: str) -> str:
        """Get group name for an extension"""
        for group_key, group_data in self.FILE_TYPE_GROUPS.items():
            if extension in group_data['extensions']:
                return group_data['name']
        return '❓ Khác'
    
    @staticmethod
    def get_group_display_info(group_key: str) -> Dict[str, any]:
        """
        Get display information for a group
        
        Args:
            group_key: Group key (e.g., 'images')
            
        Returns:
            Dictionary with name and extension count
        """
        if group_key in FileTypeFilter.FILE_TYPE_GROUPS:
            group = FileTypeFilter.FILE_TYPE_GROUPS[group_key]
            ext_list = ', '.join(sorted(group['extensions']))
            return {
                'name': group['name'],
                'extensions': ext_list,
                'count': len(group['extensions'])
            }
        return {'name': '❓ Khác', 'extensions': '', 'count': 0}
