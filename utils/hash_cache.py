"""
Hash cache manager using SQLite for persistent storage
Caches file hashes based on path, size, and mtime
"""

import sqlite3
import os
import time
import threading
from typing import Optional, Tuple
from pathlib import Path


class HashCache:
    """Manages persistent hash cache using SQLite"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize hash cache
        
        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            # Default location: AppData/StorageManager/hash_cache.db
            app_data = os.getenv('APPDATA', os.path.expanduser('~'))
            cache_dir = os.path.join(app_data, 'StorageManager')
            os.makedirs(cache_dir, exist_ok=True)
            db_path = os.path.join(cache_dir, 'hash_cache.db')
        
        self.db_path = db_path
        self.conn = None
        self.db_lock = threading.Lock()  # Thread-safe database access
        self._init_database()
    
    def _init_database(self):
        """Initialize database and create tables"""
        # Allow multi-threaded access (we handle thread safety with locks)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Create cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_cache (
                path TEXT PRIMARY KEY,
                size INTEGER NOT NULL,
                mtime REAL NOT NULL,
                quick_hash TEXT,
                full_hash TEXT,
                last_checked REAL NOT NULL
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_size_mtime 
            ON file_cache(size, mtime)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_last_checked 
            ON file_cache(last_checked)
        ''')
        
        self.conn.commit()
    
    def get_cached_hash(self, filepath: str) -> Optional[Tuple[str, str]]:
        """
        Get cached hash if file hasn't changed
        
        Args:
            filepath: Path to file
            
        Returns:
            Tuple of (quick_hash, full_hash) if cache hit, None if miss
        """
        try:
            # Get current file stats
            stat = os.stat(filepath)
            file_size = stat.st_size
            file_mtime = stat.st_mtime
            
            with self.db_lock:  # Thread-safe access
                cursor = self.conn.cursor()
                cursor.execute('''
                    SELECT quick_hash, full_hash 
                    FROM file_cache 
                    WHERE path = ? AND size = ? AND mtime = ?
                ''', (filepath, file_size, file_mtime))
                
                result = cursor.fetchone()
            
            if result:
                # Cache HIT - return cached hashes
                return (result[0], result[1])
            else:
                # Cache MISS
                return None
                
        except (OSError, sqlite3.Error):
            return None
    
    def update_cache(self, filepath: str, quick_hash: str, full_hash: Optional[str] = None):
        """
        Update cache with new hash values (batched - call flush() when done)
        
        Args:
            filepath: Path to file
            quick_hash: Quick hash value
            full_hash: Full hash value (optional for small files)
        """
        try:
            # Get current file stats
            stat = os.stat(filepath)
            file_size = stat.st_size
            file_mtime = stat.st_mtime
            current_time = time.time()
            
            with self.db_lock:  # Thread-safe access
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO file_cache 
                    (path, size, mtime, quick_hash, full_hash, last_checked)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (filepath, file_size, file_mtime, quick_hash, full_hash, current_time))
                # NO commit here - batched for performance
            
        except (OSError, sqlite3.Error) as e:
            # Silently fail - cache is optional
            pass
    
    def flush(self):
        """Commit all pending cache updates to database"""
        try:
            with self.db_lock:
                self.conn.commit()
        except sqlite3.Error:
            pass
    
    def cleanup_stale(self, max_age_days: int = 30):
        """
        Remove cache entries older than max_age_days
        
        Args:
            max_age_days: Maximum age in days
        """
        try:
            cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
            
            cursor = self.conn.cursor()
            cursor.execute('''
                DELETE FROM file_cache 
                WHERE last_checked < ?
            ''', (cutoff_time,))
            
            deleted_count = cursor.rowcount
            self.conn.commit()
            
            return deleted_count
            
        except sqlite3.Error as e:
            print(f"Cache cleanup error: {e}")
            return 0
    
    def cleanup_orphaned(self, batch_size: int = 1000):
        """
        Remove cache entries for files that no longer exist
        
        Args:
            batch_size: Number of entries to check per batch
            
        Returns:
            Number of deleted entries
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT path FROM file_cache')
            
            orphaned_paths = []
            for (file_path,) in cursor.fetchall():
                if not os.path.exists(file_path):
                    orphaned_paths.append(file_path)
            
            if orphaned_paths:
                # Delete in batches
                for i in range(0, len(orphaned_paths), batch_size):
                    batch = orphaned_paths[i:i + batch_size]
                    placeholders = ','.join('?' * len(batch))
                    cursor.execute(f'''
                        DELETE FROM file_cache 
                        WHERE path IN ({placeholders})
                    ''', batch)
                self.conn.commit()
            
            return len(orphaned_paths)
            
        except sqlite3.Error as e:
            print(f"Orphan cleanup error: {e}")
            return 0
    
    def vacuum(self):
        """Compact database to reclaim space"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('VACUUM')
        except sqlite3.Error as e:
            print(f"Vacuum error: {e}")
    
    def get_stats(self) -> dict:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        try:
            cursor = self.conn.cursor()
            
            # Total entries
            cursor.execute('SELECT COUNT(*) FROM file_cache')
            total_entries = cursor.fetchone()[0]
            
            # Cache size
            cursor.execute('SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()')
            cache_size = cursor.fetchone()[0]
            
            return {
                'total_entries': total_entries,
                'cache_size_mb': cache_size / (1024 * 1024),
                'db_path': self.db_path
            }
            
        except sqlite3.Error:
            return {
                'total_entries': 0,
                'cache_size_mb': 0,
                'db_path': self.db_path
            }
    
    def clear_all(self):
        """Clear entire cache"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM file_cache')
            self.conn.commit()
            
            # Vacuum to reclaim space
            cursor.execute('VACUUM')
            
        except sqlite3.Error as e:
            print(f"Cache clear error: {e}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __del__(self):
        """Destructor - ensure connection is closed"""
        self.close()
