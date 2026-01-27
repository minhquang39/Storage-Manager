"""
Enhanced Configuration with Safe Cleanup Categories
Based on Windows File Cleanup Safety Specification
"""

# === CRITICAL: Never Delete These Folders ===
EXCLUDED_DIRS = {
    # Windows System Folders
    'windows', 'system32', 'syswow64', 'winnt',
    'program files', 'program files (x86)', 'programdata',
    
    # System Recovery
    '$recycle.bin', 'system volume information', 'recovery', 
    'boot', 'windows.old', 'perflogs',
    
    # User Application Data (settings, game saves, configs)
    'appdata',
    
    # Development
    'node_modules', '.git', '.svn', '__pycache__',
}

# === SAFE TO DELETE: File Categories ===

# Temporary Files (Safe to Delete)
SAFE_TEMP_EXTENSIONS = {
    '.tmp', '.temp', '.bak', '.old', '~', '.cache'
}

SAFE_TEMP_FOLDERS = {
    'windows\\temp',
    'appdata\\local\\temp',
    'temp', 'tmp'
}

# Installer Files (After Installation)
INSTALLER_EXTENSIONS = {
    '.exe', '.msi', '.cab', '.msp'
}

# Compressed Files (After Extraction)
ARCHIVE_EXTENSIONS = {
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.iso'
}

# Log Files (Old Logs)
LOG_EXTENSIONS = {
    '.log', '.dmp', '.etl'
}

# Cache Folders (Browser & App Cache)
CACHE_FOLDERS = {
    'cache', 'cache2', 'caches',
    'appdata\\local\\google\\chrome\\user data\\default\\cache',
    'appdata\\local\\microsoft\\edge\\user data\\default\\cache',
    'appdata\\local\\mozilla\\firefox\\profiles',
}

# Downloads Folder Patterns
DOWNLOADS_FOLDERS = {
    'downloads', 'desktop\\downloads'
}

# === NEVER DELETE: Critical System Files ===
NEVER_DELETE_FILES = {
    'pagefile.sys',      # Virtual memory
    'swapfile.sys',      # Virtual memory
    'hiberfil.sys',      # Hibernation (conditional)
    'bootmgr',           # Boot manager
    'ntldr',             # Legacy boot
    'system.ini',        # System config
    'win.ini',           # Windows config
}

NEVER_DELETE_EXTENSIONS = {
    '.sys',    # System drivers
    '.dll',    # Dynamic libraries
    '.efi',    # UEFI files
    '.drv',    # Drivers
    '.ocx',    # ActiveX controls
}

# === SIZE FILTERING ===
DEFAULT_MIN_SIZE_MB = 50  # Only show files >= 50 MB by default

# === CLEANUP CATEGORIES ===
CLEANUP_CATEGORIES = {
    'temp_files': {
        'name': 'Temporary Files',
        'description': 'Temp files safe to delete',
        'extensions': SAFE_TEMP_EXTENSIONS,
        'folders': SAFE_TEMP_FOLDERS,
        'safe_level': 'high',  # High = Very safe
    },
    'installers': {
        'name': 'Installer Files',
        'description': 'Setup files after installation',
        'extensions': INSTALLER_EXTENSIONS,
        'folders': DOWNLOADS_FOLDERS,
        'safe_level': 'medium',  # Medium = Check before delete
    },
    'archives': {
        'name': 'Compressed Archives',
        'description': 'Zip/Rar files (check if extracted)',
        'extensions': ARCHIVE_EXTENSIONS,
        'folders': DOWNLOADS_FOLDERS,
        'safe_level': 'medium',
    },
    'logs': {
        'name': 'Log Files',
        'description': 'Application log files',
        'extensions': LOG_EXTENSIONS,
        'safe_level': 'high',
    },
    'large_files': {
        'name': 'Large Files',
        'description': 'Files over specified size',
        'safe_level': 'low',  # Low = Review carefully
    },
}

# === SAFETY SETTINGS ===
REQUIRE_CONFIRMATION = True          # Always confirm before deletion
USE_RECYCLE_BIN = True              # Never permanent delete
SHOW_DRY_RUN_FIRST = True           # List files before allowing deletion
MAX_FILES_PER_BATCH = 100           # Limit batch deletion size

# === FILE CLASSIFICATION ===
def classify_file_safety(filepath: str, file_size: int) -> dict:
    """
    Classify file safety level
    
    Returns:
        {
            'safe': bool,
            'category': str,
            'reason': str,
            'safety_level': str  # 'high', 'medium', 'low', 'never'
        }
    """
    import os
    
    path_lower = filepath.lower()
    filename = os.path.basename(filepath)
    extension = os.path.splitext(filename)[1].lower()
    
    # NEVER DELETE: Critical system files
    if filename.lower() in NEVER_DELETE_FILES:
        return {
            'safe': False,
            'category': 'system_critical',
            'reason': 'Critical system file - NEVER delete',
            'safety_level': 'never'
        }
    
    if extension in NEVER_DELETE_EXTENSIONS:
        return {
            'safe': False,
            'category': 'system_file',
            'reason': f'System file ({extension}) - NEVER delete',
            'safety_level': 'never'
        }
    
    # Check if in protected folder
    for excluded in EXCLUDED_DIRS:
        if excluded in path_lower:
            return {
                'safe': False,
                'category': 'protected_folder',
                'reason': f'In protected folder: {excluded}',
                'safety_level': 'never'
            }
    
    # SAFE: Temporary files
    if extension in SAFE_TEMP_EXTENSIONS:
        return {
            'safe': True,
            'category': 'temporary',
            'reason': f'Temporary file ({extension}) - Safe to delete',
            'safety_level': 'high'
        }
    
    # SAFE: Temp folders
    for temp_folder in SAFE_TEMP_FOLDERS:
        if temp_folder in path_lower:
            return {
                'safe': True,
                'category': 'temporary',
                'reason': f'In temp folder: {temp_folder}',
                'safety_level': 'high'
            }
    
    # CONDITIONAL: Installers in Downloads
    if extension in INSTALLER_EXTENSIONS:
        if any(folder in path_lower for folder in DOWNLOADS_FOLDERS):
            return {
                'safe': True,
                'category': 'installer',
                'reason': 'Installer in Downloads - Safe if already installed',
                'safety_level': 'medium'
            }
    
    # CONDITIONAL: Archives
    if extension in ARCHIVE_EXTENSIONS:
        return {
            'safe': True,
            'category': 'archive',
            'reason': 'Compressed archive - Safe if already extracted',
            'safety_level': 'medium'
        }
    
    # CONDITIONAL: Logs
    if extension in LOG_EXTENSIONS:
        return {
            'safe': True,
            'category': 'log',
            'reason': 'Log file - Safe to delete',
            'safety_level': 'high'
        }
    
    # UNKNOWN: Large file
    if file_size > DEFAULT_MIN_SIZE_MB * 1024 * 1024:
        if 'c:\\' in path_lower and 'users' not in path_lower:
            return {
                'safe': False,
                'category': 'unknown_system',
                'reason': 'Large file in system area - Review carefully',
                'safety_level': 'low'
            }
        else:
            return {
                'safe': True,
                'category': 'large_user_file',
                'reason': 'Large file in user area - Review before delete',
                'safety_level': 'low'
            }
    
    # DEFAULT: Unknown file
    return {
        'safe': False,
        'category': 'unknown',
        'reason': 'Unknown file type - Skip for safety',
        'safety_level': 'never'
    }


# === HASH ALGORITHM ===
HASH_ALGORITHM = 'sha256'

# === CHUNK SIZE ===
CHUNK_SIZE = 8192

# === GUI SETTINGS ===
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
PREVIEW_IMAGE_SIZE = (200, 200)

# === FILE EXTENSIONS ===
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.tiff', '.webp'}
TEXT_EXTENSIONS = {'.txt', '.log', '.md', '.json', '.xml', '.csv', '.ini', '.cfg', '.conf'}
