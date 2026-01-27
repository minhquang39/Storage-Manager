"""
Configuration file for Storage Manager application
"""

# Excluded directories for safety (system-critical folders)
# These folders will NEVER be scanned to prevent system damage
EXCLUDED_DIRS = {
    # === CRITICAL: Windows System Folders ===
    # C:\Windows - Contains all Windows operating system files
    'windows', 'system32', 'syswow64', 'winnt',
    
    # === CRITICAL: Installed Programs ===
    # Deleting files here will remove/break installed software
    'program files', 'program files (x86)', 'programdata',
    
    # === CRITICAL: User Application Data ===
    # Contains app settings, configurations, and game saves
    'appdata',  # Entire AppData folder protected
    
    # === System Recovery and Backup ===
    '$recycle.bin', 'system volume information', 'recovery', 
    'boot', 'windows.old', 'perflogs', '$windows.~bt', '$windows.~ws',
    
    # === Temporary and Cache Folders ===
    'windows\\temp', 'temp',
    
    # === Virtual Memory Files ===
    'pagefile.sys', 'hiberfil.sys', 'swapfile.sys',
    
    # === Development Folders (safe to exclude) ===
    'node_modules', '.git', '.svn', '.hg', '__pycache__',
    
    # === macOS/Linux System Folders ===
    'system', 'library', 'bin', 'sbin', 'usr', 'dev', 'proc', 'sys',
    'var', 'tmp', 'etc', 'opt', 'root'
}

# Safe user folders that WILL be scanned (relative to Users folder)
# These typically contain user files like documents, photos, videos
SAFE_USER_FOLDERS = {
    'desktop', 'documents', 'downloads', 'pictures', 
    'videos', 'music', 'public'
}

# Auto-scan settings
AUTO_SCAN_ALL_DRIVES = True  # Automatically scan all drives
AUTO_EXCLUDE_USERS_APPDATA = True  # Exclude Users\*\AppData automatically

# File scanning settings
CHUNK_SIZE = 8192  # Bytes to read at a time for hashing
MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024  # 10GB max file size to process
MIN_FILE_SIZE = 1  # 1 byte minimum

# GUI settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
PREVIEW_IMAGE_SIZE = (200, 200)

# Hash algorithm
HASH_ALGORITHM = 'md5'  # Fast and sufficient for duplicate detection

# File extensions for preview
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.tiff', '.webp'}
TEXT_EXTENSIONS = {'.txt', '.log', '.md', '.json', '.xml', '.csv', '.ini', '.cfg', '.conf'}
