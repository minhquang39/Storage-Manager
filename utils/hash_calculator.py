"""
Hash calculator for file comparison
"""

import hashlib
import os
from typing import Optional
import config


class HashCalculator:
    """Calculate file hashes for duplicate detection"""
    
    @staticmethod
    def calculate_file_hash(filepath: str, 
                           algorithm: str = config.HASH_ALGORITHM,
                           chunk_size: int = config.CHUNK_SIZE) -> Optional[str]:
        """
        Calculate hash of file content
        
        Args:
            filepath: Path to file
            algorithm: Hash algorithm to use (sha256, md5, etc.)
            chunk_size: Size of chunks to read
            
        Returns:
            Hash string or None if error
        """
        try:
            hash_obj = hashlib.new(algorithm)
            
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
        except (OSError, PermissionError, IOError):
            return None
    
    @staticmethod
    def calculate_quick_hash(filepath: str, 
                            sample_size: int = 1024) -> Optional[str]:
        """
        Calculate quick hash using file size and first/last bytes
        Useful for fast pre-filtering before full hash
        
        Args:
            filepath: Path to file
            sample_size: Number of bytes to sample from start and end
            
        Returns:
            Quick hash string or None if error
        """
        try:
            file_size = os.path.getsize(filepath)
            
            with open(filepath, 'rb') as f:
                # Read first bytes
                first_bytes = f.read(sample_size)
                
                # Read last bytes if file is large enough
                if file_size > sample_size:
                    f.seek(-sample_size, os.SEEK_END)
                    last_bytes = f.read(sample_size)
                else:
                    last_bytes = b''
            
            # Combine size and samples for quick hash
            hash_obj = hashlib.sha256()
            hash_obj.update(str(file_size).encode())
            hash_obj.update(first_bytes)
            hash_obj.update(last_bytes)
            
            return hash_obj.hexdigest()
        except (OSError, PermissionError, IOError):
            return None
