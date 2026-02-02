"""
Duplicate file finder module
"""

import os
from collections import defaultdict
from typing import Dict, List, Callable, Optional

import config
from utils.file_scanner import FileScanner
from utils.hash_calculator import HashCalculator
from utils.hash_cache import HashCache


class DuplicateFinder:
    """Find duplicate files based on content hash"""
    
    def __init__(self, progress_callback: Optional[Callable] = None, enable_cache: bool = True):
        """
        Initialize duplicate finder
        
        Args:
            progress_callback: Optional callback for progress updates
            enable_cache: Enable persistent hash caching (default: True)
        """
        self.scanner = FileScanner(progress_callback)
        self.hash_calculator = HashCalculator()
        self.cancelled = False
        
        # Initialize hash cache
        self.cache_enabled = enable_cache
        self.cache = HashCache() if enable_cache else None
    
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
        
        # Step 2: For files with same size, calculate quick hash (MULTI-THREADED)
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import threading
        
        quick_hash_groups = defaultdict(list)
        quick_hash_lock = threading.Lock()
        
        # Collect files that need quick hashing (size >= 2 files)
        files_to_quick_hash = []
        for size, filepaths in size_groups.items():
            if len(filepaths) >= 2:
                for fp in filepaths:
                    files_to_quick_hash.append((size, fp))
        
        total_quick_hash = len(files_to_quick_hash)
        processed_quick = [0]  # Use list for mutable in closure
        processed_lock = threading.Lock()
        
        def process_quick_hash(size_filepath):
            """Process single file for quick hash - thread worker"""
            size, filepath = size_filepath
            if self.cancelled:
                return None
            
            quick_hash = None
            
            # Try cache first
            if self.cache_enabled and self.cache:
                cached = self.cache.get_cached_hash(filepath)
                if cached:
                    quick_hash, _ = cached
            
            # Calculate if not in cache
            if not quick_hash:
                quick_hash = self.hash_calculator.calculate_quick_hash(filepath)
                
                # Update cache (thread-safe via db_lock in HashCache)
                if quick_hash and self.cache_enabled and self.cache:
                    self.cache.update_cache(filepath, quick_hash, None)
            
            return (size, quick_hash, filepath) if quick_hash else None
        
        # Use 8 workers for quick hash (I/O bound - more threads = better)
        max_workers = min(8, len(files_to_quick_hash) or 1)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_quick_hash, item): item 
                      for item in files_to_quick_hash}
            
            for future in as_completed(futures):
                if self.cancelled:
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                
                try:
                    result = future.result()
                    if result:
                        size, quick_hash, filepath = result
                        
                        # Thread-safe append
                        with quick_hash_lock:
                            quick_hash_groups[(size, quick_hash)].append(filepath)
                        
                        # Thread-safe progress update
                        with processed_lock:
                            processed_quick[0] += 1
                            if hash_progress_callback and processed_quick[0] % 100 == 0:
                                hash_progress_callback("quick_hash", processed_quick[0], 
                                                      total_quick_hash, os.path.basename(filepath))
                except Exception:
                    continue
        
        # Flush quick hash cache updates
        if self.cache_enabled and self.cache:
            self.cache.flush()
        
        # Step 3: For files with same quick hash, calculate full hash (MULTI-THREADED)
        full_hash_groups = defaultdict(list)
        full_hash_groups_lock = threading.Lock()  # Thread-safe access
        
        # Count files that need full hashing
        files_to_full_hash = []
        for (size, quick_hash), filepaths in quick_hash_groups.items():
            if len(filepaths) >= 2:
                files_to_full_hash.extend([(size, quick_hash, fp) for fp in filepaths])
        
        total_full_hash = len(files_to_full_hash)
        processed_full = 0
        processed_lock = threading.Lock()
        
        def process_file(size, quick_hash, filepath):
            """Process single file - thread worker function"""
            if self.cancelled:
                return None
            
            # Optimization: Skip full hash for small files (quick hash is sufficient)
            if size < config.SMALL_FILE_THRESHOLD:
                # For small files, use quick_hash as the "full" hash
                file_info = self.scanner.get_file_info(filepath)
                file_info['hash'] = quick_hash  # Reuse quick hash
                
                # Update cache (small files don't need full hash)
                if self.cache_enabled and self.cache:
                    self.cache.update_cache(filepath, quick_hash, quick_hash)
                
                return (quick_hash, file_info, False)  # False = skipped full hash
            else:
                # Check cache for full hash first
                full_hash = None
                if self.cache_enabled and self.cache:
                    cached = self.cache.get_cached_hash(filepath)
                    if cached and cached[1]:  # cached[1] is full_hash
                        full_hash = cached[1]
                
                # Calculate full hash if not in cache
                if not full_hash:
                    full_hash = self.hash_calculator.calculate_file_hash(filepath)
                    
                    # Update cache with full hash
                    if full_hash and self.cache_enabled and self.cache:
                        self.cache.update_cache(filepath, quick_hash, full_hash)
                
                if full_hash:
                    file_info = self.scanner.get_file_info(filepath)
                    file_info['hash'] = full_hash
                    return (full_hash, file_info, True)  # True = calculated full hash
            return None
        
        # Use ThreadPoolExecutor for parallel processing (4 workers)
        max_workers = min(4, len(files_to_full_hash) or 1)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            futures = {
                executor.submit(process_file, size, qh, fp): (size, qh, fp)
                for size, qh, fp in files_to_full_hash
            }
            
            # Process completed futures
            for future in as_completed(futures):
                if self.cancelled:
                    # Cancel all remaining tasks
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                
                try:
                    result = future.result()
                    if result:
                        hash_val, file_info, was_full_hash = result
                        
                        # Thread-safe append
                        with full_hash_groups_lock:
                            full_hash_groups[hash_val].append(file_info)
                        
                        # Thread-safe progress update
                        with processed_lock:
                            processed_full += 1
                            
                            if hash_progress_callback and processed_full % 10 == 0:
                                phase_name = "full_hash" if was_full_hash else "small_file"
                                hash_progress_callback(phase_name, processed_full, total_full_hash,
                                                      os.path.basename(file_info['path']))
                
                except Exception as e:
                    # Handle any errors in thread
                    print(f"Error processing file: {e}")
                    continue
        
        # Flush cache to disk (batch commit)
        if self.cache_enabled and self.cache:
            self.cache.flush()
        
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
