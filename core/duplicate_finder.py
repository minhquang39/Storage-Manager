"""
Duplicate file finder module
"""

import os
from collections import defaultdict
from typing import Dict, List, Callable, Optional
from utils.file_scanner import FileScanner
from utils.hash_calculator import HashCalculator


class DuplicateFinder:
    """Find duplicate files based on content hash"""
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        """
        Initialize duplicate finder
        
        Args:
            progress_callback: Optional callback for progress updates
        """
        self.scanner = FileScanner(progress_callback)
        self.hash_calculator = HashCalculator()
        self.cancelled = False
    
    def cancel(self):
        """Cancel the current operation"""
        self.cancelled = True
        self.scanner.cancel()
    
    
    def find_duplicates(self, directories: List[str], 
                       min_size: int = 0,
                       hash_progress_callback=None) -> Dict[str, List[dict]]:
        """
        Find duplicate files in given directories
        
        Args:
            directories: List of directory paths to scan
            min_size: Minimum file size to consider (in bytes)
            hash_progress_callback: Optional callback(phase, current, total, message)
            
        Returns:
            Dictionary mapping hash to list of duplicate file info
        """
        # Step 1: Group files by size (quick pre-filter)
        size_groups = defaultdict(list)
        
        for directory in directories:
            if self.cancelled:
                break
            
            for filepath in self.scanner.scan_directory(directory, min_size=min_size):
                if self.cancelled:
                    break
                
                try:
                    file_size = os.path.getsize(filepath)
                    size_groups[file_size].append(filepath)
                except OSError:
                    continue
        
        # Step 2: For files with same size, calculate quick hash
        quick_hash_groups = defaultdict(list)
        
        # Count files that need quick hashing
        files_to_quick_hash = []
        for size, filepaths in size_groups.items():
            if len(filepaths) >= 2:
                files_to_quick_hash.extend(filepaths)
        
        total_quick_hash = len(files_to_quick_hash)
        processed_quick = 0
        
        for size, filepaths in size_groups.items():
            if self.cancelled:
                break
            
            # Only process if there are multiple files with same size
            if len(filepaths) < 2:
                continue
            
            for filepath in filepaths:
                if self.cancelled:
                    break
                
                quick_hash = self.hash_calculator.calculate_quick_hash(filepath)
                if quick_hash:
                    quick_hash_groups[(size, quick_hash)].append(filepath)
                
                # Report progress
                processed_quick += 1
                if hash_progress_callback and processed_quick % 10 == 0:
                    hash_progress_callback("quick_hash", processed_quick, total_quick_hash, 
                                          os.path.basename(filepath))
        
        # Step 3: For files with same quick hash, calculate full hash
        full_hash_groups = defaultdict(list)
        
        # Count files that need full hashing
        files_to_full_hash = []
        for (size, quick_hash), filepaths in quick_hash_groups.items():
            if len(filepaths) >= 2:
                files_to_full_hash.extend(filepaths)
        
        total_full_hash = len(files_to_full_hash)
        processed_full = 0
        
        for (size, quick_hash), filepaths in quick_hash_groups.items():
            if self.cancelled:
                break
            
            # Only process if there are multiple files with same quick hash
            if len(filepaths) < 2:
                continue
            
            for filepath in filepaths:
                if self.cancelled:
                    break
                
                full_hash = self.hash_calculator.calculate_file_hash(filepath)
                if full_hash:
                    file_info = self.scanner.get_file_info(filepath)
                    file_info['hash'] = full_hash
                    full_hash_groups[full_hash].append(file_info)
                
                # Report progress
                processed_full += 1
                if hash_progress_callback and processed_full % 10 == 0:
                    hash_progress_callback("full_hash", processed_full, total_full_hash,
                                          os.path.basename(filepath))
        
        # Step 4: Filter out groups with only one file
        duplicates = {
            hash_val: files 
            for hash_val, files in full_hash_groups.items() 
            if len(files) > 1
        }
        
        return duplicates
    
    def select_files_to_keep(self, duplicate_group: List[dict], 
                            strategy: str = 'newest') -> List[str]:
        """
        Select which files to keep based on strategy
        
        Args:
            duplicate_group: List of duplicate file info dictionaries
            strategy: Selection strategy ('newest', 'oldest', 'first_path')
            
        Returns:
            List of file paths to DELETE (keeping one based on strategy)
        """
        if len(duplicate_group) <= 1:
            return []
        
        # Sort based on strategy
        if strategy == 'newest':
            sorted_files = sorted(duplicate_group, 
                                key=lambda x: x.get('modified', 0), 
                                reverse=True)
        elif strategy == 'oldest':
            sorted_files = sorted(duplicate_group, 
                                key=lambda x: x.get('modified', 0))
        elif strategy == 'first_path':
            sorted_files = sorted(duplicate_group, 
                                key=lambda x: x.get('path', ''))
        else:
            sorted_files = duplicate_group
        
        # Keep the first one, delete the rest
        files_to_delete = [f['path'] for f in sorted_files[1:]]
        return files_to_delete
