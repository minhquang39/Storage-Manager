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
    
    # === Development Folders (safe to exclude) ===
    'node_modules', '.git', '.svn', '.hg', '__pycache__',
    
    # === macOS/Linux System Folders ===
    'system', 'library', 'bin', 'sbin', 'usr', 'dev', 'proc', 'sys',
    'var', 'tmp', 'etc', 'opt', 'root'
}

# Excluded FILES for safety (system-critical files)
# These files will NEVER be shown in results to prevent accidental deletion
EXCLUDED_FILES = {
    # === Windows Virtual Memory & Hibernate ===
    'pagefile.sys',      # Virtual memory - XÓA = crash Windows
    'hiberfil.sys',      # Hibernate file - XÓA = mất hibernate  
    'swapfile.sys',      # Swap file cho Windows apps
    
    # === Windows Boot Files ===
    'bootmgr',           # Boot manager - XÓA = không boot được
    'bootmgr.efi',       # UEFI boot manager
    'ntldr',             # NT Loader (legacy)
    'ntdetect.com',      # Hardware detection (legacy)
    'boot.ini',          # Boot config (legacy)
    'bootsect.bak',      # Boot sector backup
    
    # === Windows Core System ===
    'ntoskrnl.exe',      # Windows kernel
    'hal.dll',           # Hardware Abstraction Layer
    'winload.exe',       # Windows loader
    'winload.efi',       # UEFI Windows loader
    'winresume.exe',     # Resume from hibernate
    
    # === NTFS System Files ===
    '$mft',              # Master File Table
    '$mftmirr',          # MFT Mirror
    '$logfile',          # NTFS Log
    '$volume',           # Volume info
    '$attrdef',          # Attribute definitions
    '$bitmap',           # Cluster bitmap
    '$boot',             # Boot sector
    '$badclus',          # Bad clusters
    '$secure',           # Security descriptors
    '$upcase',           # Uppercase table
    '$extend',           # Extended attributes
    
    # === Windows Registry Hives ===
    'sam',               # Security Account Manager
    'security',          # Security policies
    'software',          # Software settings
    'system',            # System settings
    'default',           # Default user profile
    'ntuser.dat',        # User registry
    'usrclass.dat',      # User class registry
    
    # === System Metadata ===
    'desktop.ini',       # Folder customization
    'thumbs.db',         # Thumbnail cache
    'iconcache.db',      # Icon cache
    
    # === Windows Installer ===
    'msi.dll',           # Windows Installer
    'msiexec.exe',       # Installer executable
}

# Excluded file EXTENSIONS (dangerous to delete)
EXCLUDED_EXTENSIONS = {
    '.sys',              # System drivers - QUAN TRỌNG
    '.drv',              # Driver files
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
CHUNK_SIZE = 65536  # 64KB - Faster disk I/O (was 8KB)
MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024  # 10GB max file size to process
MIN_FILE_SIZE = 1  # 1 byte minimum

# GUI settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
PREVIEW_IMAGE_SIZE = (200, 200)

# Hash algorithm
HASH_ALGORITHM = 'xxh64'  # Ultra-fast hash for duplicate detection (25x faster than MD5)

# Small file optimization
SMALL_FILE_THRESHOLD = 1024 * 1024  # 1MB - Files smaller than this skip full hash

# File extensions for preview
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.tiff', '.webp'}
TEXT_EXTENSIONS = {'.txt', '.log', '.md', '.json', '.xml', '.csv', '.ini', '.cfg', '.conf'}
