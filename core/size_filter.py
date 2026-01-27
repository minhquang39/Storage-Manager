"""
File size filter module
"""

from typing import List, Callable, Optional, Tuple
from utils.file_scanner import FileScanner


class SizeFilter:
    """Filter files based on size criteria"""
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        """
        Initialize size filter
        
        Args:
            progress_callback: Optional callback for progress updates
        """
        self.scanner = FileScanner(progress_callback)
        self.cancelled = False
    
    def cancel(self):
        """Cancel the current operation"""
        self.cancelled = True
        self.scanner.cancel()
    
    def find_files_by_size(self, directories: List[str],
                          size_condition: str,
                          size_value: float,
                          size_unit: str = 'MB') -> List[dict]:
        """
        Find files matching size criteria
        
        Args:
            directories: List of directory paths to scan
            size_condition: Condition type ('larger_than', 'smaller_than', 'exactly')
            size_value: Size value in specified unit
            size_unit: Size unit ('B', 'KB', 'MB', 'GB')
            
        Returns:
            List of file info dictionaries matching criteria
        """
        # Convert size to bytes
        size_bytes = self._convert_to_bytes(size_value, size_unit)
        
        # Determine min and max size for scanning
        if size_condition == 'larger_than':
            min_size = size_bytes + 1
            max_size = None
        elif size_condition == 'smaller_than':
            min_size = 0
            max_size = size_bytes - 1
        elif size_condition == 'exactly':
            min_size = size_bytes
            max_size = size_bytes
        else:
            min_size = 0
            max_size = None
        
        # Scan and collect files
        matched_files = []
        
        for directory in directories:
            if self.cancelled:
                break
            
            for filepath in self.scanner.scan_directory(directory, min_size, max_size):
                if self.cancelled:
                    break
                
                file_info = self.scanner.get_file_info(filepath)
                
                # Double-check the condition
                if self._matches_condition(file_info.get('size', 0), 
                                          size_condition, 
                                          size_bytes):
                    matched_files.append(file_info)
        
        return matched_files
    
    @staticmethod
    def _convert_to_bytes(value: float, unit: str) -> int:
        """Convert size value to bytes"""
        units = {
            'B': 1,
            'KB': 1024,
            'MB': 1024 ** 2,
            'GB': 1024 ** 3,
            'TB': 1024 ** 4
        }
        return int(value * units.get(unit, 1))
    
    @staticmethod
    def _matches_condition(file_size: int, condition: str, target_size: int) -> bool:
        """Check if file size matches condition"""
        if condition == 'larger_than':
            return file_size > target_size
        elif condition == 'smaller_than':
            return file_size < target_size
        elif condition == 'exactly':
            return file_size == target_size
        return True
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """
        Format byte size to human-readable string
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted string (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
