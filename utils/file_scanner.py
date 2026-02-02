"""
File scanner utility for traversing directories safely
"""

import os
import string
from pathlib import Path
from typing import Generator, Callable, Optional, List
import config


class FileScanner:
    """Safe file scanner that respects system boundaries"""
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        """
        Initialize file scanner
        
        Args:
            progress_callback: Optional callback function for progress updates
        """
        self.progress_callback = progress_callback
        self.files_scanned = 0
        self.cancelled = False
        # Pre-compute lowercase excluded dirs for faster matching
        self._excluded_lower = {ex.lower() for ex in config.EXCLUDED_DIRS}
    
    @staticmethod
    def get_all_drives() -> List[str]:
        """
        Get all available drives on the system
        
        Returns:
            List of drive paths (e.g., ['C:\\', 'D:\\'])
        """
        drives = []
        
        # For Windows
        if os.name == 'nt':
            # Check all possible drive letters
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    drives.append(drive)
        else:
            # For Unix-like systems (Linux, macOS)
            # Start from root
            drives.append('/')
        
        return drives
    
    def cancel(self):
        """Cancel the current scanning operation"""
        self.cancelled = True
    
    def is_safe_directory(self, path: str) -> bool:
        """
        Check if directory is safe to scan (optimized)
        
        Args:
            path: Directory path to check
            
        Returns:
            True if safe to scan, False otherwise
        """
        path_lower = path.lower()
        
        # Fast check: match any part of path against excluded dirs
        path_parts = path_lower.replace('/', '\\').split('\\')
        for part in path_parts:
            if part in self._excluded_lower:
                return False
        
        # Note: Removed os.listdir() check - let os.walk handle permissions
        # This is much faster as we don't pre-read directory contents
        return True
    
    def scan_directory(self, root_path: str, 
                      min_size: int = 0, 
                      max_size: Optional[int] = None) -> Generator[str, None, None]:
        """
        Scan directory and yield file paths
        
        Args:
            root_path: Root directory to scan
            min_size: Minimum file size in bytes
            max_size: Maximum file size in bytes (None for no limit)
            
        Yields:
            Full file paths
        """
        self.files_scanned = 0
        self.cancelled = False
        
        if not self.is_safe_directory(root_path):
            return
        
        try:
            for dirpath, dirnames, filenames in os.walk(root_path):
                if self.cancelled:
                    break
                
                # Filter out unsafe directories
                dirnames[:] = [d for d in dirnames 
                             if self.is_safe_directory(os.path.join(dirpath, d))]
                
                for filename in filenames:
                    if self.cancelled:
                        break
                    
                    filepath = os.path.join(dirpath, filename)
                    
                    try:
                        # Check if file is accessible and meets size criteria
                        stat = os.stat(filepath)
                        file_size = stat.st_size
                        
                        # Count ALL files scanned (before filtering)
                        self.files_scanned += 1
                        
                        # Report progress every 500 files (reduced overhead)
                        if self.progress_callback and self.files_scanned % 500 == 0:
                            self.progress_callback(self.files_scanned, filepath)
                        
                        # Filter by size
                        if file_size < min_size:
                            continue
                        
                        if max_size is not None and file_size > max_size:
                            continue
                        
                        yield filepath
                        
                    except (OSError, PermissionError):
                        # Skip files we can't access
                        continue
                        
        except Exception as e:
            print(f"Error scanning {root_path}: {e}")
    
    def scan_directory_with_stat(self, root_path: str, 
                                  min_size: int = 0, 
                                  max_size: Optional[int] = None) -> Generator[tuple, None, None]:
        """
        Scan directory and yield file paths WITH stat result (optimized).
        Use this to avoid calling os.stat() twice.
        
        Yields:
            Tuple of (filepath, stat_result)
        """
        self.files_scanned = 0
        self.cancelled = False
        
        if not self.is_safe_directory(root_path):
            return
        
        try:
            for dirpath, dirnames, filenames in os.walk(root_path):
                if self.cancelled:
                    break
                
                # Filter out unsafe directories (in-place modification)
                dirnames[:] = [d for d in dirnames 
                             if self.is_safe_directory(os.path.join(dirpath, d))]
                
                for filename in filenames:
                    if self.cancelled:
                        break
                    
                    filepath = os.path.join(dirpath, filename)
                    
                    try:
                        stat = os.stat(filepath)
                        file_size = stat.st_size
                        
                        self.files_scanned += 1
                        
                        if self.progress_callback and self.files_scanned % 500 == 0:
                            self.progress_callback(self.files_scanned, filepath)
                        
                        if file_size < min_size:
                            continue
                        if max_size is not None and file_size > max_size:
                            continue
                        
                        yield (filepath, stat)
                        
                    except (OSError, PermissionError):
                        continue
                        
        except Exception as e:
            print(f"Error scanning {root_path}: {e}")
    
    def get_file_info(self, filepath: str, cached_stat: Optional[os.stat_result] = None) -> dict:
        """
        Get detailed file information
        
        Args:
            filepath: Path to file
            cached_stat: Optional pre-fetched stat result to avoid duplicate syscall
            
        Returns:
            Dictionary with file information
        """
        try:
            stat = cached_stat if cached_stat else os.stat(filepath)
            return {
                'path': filepath,
                'name': os.path.basename(filepath),
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'created': stat.st_ctime,
                'extension': os.path.splitext(filepath)[1].lower()
            }
        except (OSError, PermissionError) as e:
            return {
                'path': filepath,
                'error': str(e)
            }
