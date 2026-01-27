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
        Check if directory is safe to scan
        
        Args:
            path: Directory path to check
            
        Returns:
            True if safe to scan, False otherwise
        """
        path_lower = path.lower()
        
        # Check against excluded directories
        for excluded in config.EXCLUDED_DIRS:
            if excluded in path_lower:
                return False
        
        # Check if path is accessible
        try:
            os.listdir(path)
            return True
        except (PermissionError, OSError):
            return False
    
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
                        
                        if file_size < min_size:
                            continue
                        
                        if max_size is not None and file_size > max_size:
                            continue
                        
                        self.files_scanned += 1
                        
                        if self.progress_callback and self.files_scanned % 100 == 0:
                            self.progress_callback(self.files_scanned, filepath)
                        
                        yield filepath
                        
                    except (OSError, PermissionError):
                        # Skip files we can't access
                        continue
                        
        except Exception as e:
            print(f"Error scanning {root_path}: {e}")
    
    def get_file_info(self, filepath: str) -> dict:
        """
        Get detailed file information
        
        Args:
            filepath: Path to file
            
        Returns:
            Dictionary with file information
        """
        try:
            stat = os.stat(filepath)
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
