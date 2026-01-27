"""
Build script to create executable for Storage Manager

This script uses PyInstaller to create a standalone .exe file
that users can run without installing Python.

Usage:
    python build_exe.py
"""

import subprocess
import sys
import os
import shutil

print("=" * 60)
print("Storage Manager - Build Executable")
print("=" * 60)

# Check if PyInstaller is installed
print("\n[1/5] Checking PyInstaller...")
try:
    import PyInstaller
    print("✓ PyInstaller is installed")
except ImportError:
    print("✗ PyInstaller not found. Installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("✓ PyInstaller installed")

# Clean previous builds
print("\n[2/5] Cleaning previous builds...")
folders_to_clean = ['build', 'dist', '__pycache__']
for folder in folders_to_clean:
    if os.path.exists(folder):
        shutil.rmtree(folder)
        print(f"✓ Removed {folder}/")

# Remove .spec file if exists
if os.path.exists('StorageManager.spec'):
    os.remove('StorageManager.spec')
    print("✓ Removed old .spec file")

# Build executable
print("\n[3/5] Building executable...")
print("This may take 2-5 minutes...\n")

# PyInstaller command
# Use python -m PyInstaller instead of pyinstaller directly
cmd = [
    sys.executable,                 # Python executable
    '-m',                           # Run module
    'PyInstaller',                  # PyInstaller module
    '--name=StorageManager',
    '--onefile',                    # Single executable file
    '--windowed',                   # No console window
    '--clean',                      # Clean cache
    '--noconfirm',                  # Replace without asking
    
    # Hidden imports (ensure all dependencies are included)
    '--hidden-import=send2trash',
    '--hidden-import=PIL',
    '--hidden-import=tkinter',
    
    # Add data files if needed
    # '--add-data=README.md;.',     # Uncomment to include README
    
    # Icon (if you have one)
    # '--icon=icon.ico',            # Uncomment if you have icon.ico
    
    # Main script
    'main.py'
]

result = subprocess.run(cmd)

if result.returncode != 0:
    print("\n✗ Build failed!")
    sys.exit(1)

print("\n✓ Build successful!")

# Check output
print("\n[4/5] Verifying output...")
exe_path = os.path.join('dist', 'StorageManager.exe')
if os.path.exists(exe_path):
    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
    print(f"✓ Executable created: {exe_path}")
    print(f"✓ File size: {size_mb:.2f} MB")
else:
    print("✗ Executable not found!")
    sys.exit(1)

# Create distribution package
print("\n[5/5] Creating distribution package...")

# Create a README for users
user_readme = """STORAGE MANAGER v2.0
=====================

QUICK START:
1. Double-click StorageManager.exe to run
2. No installation needed!

WHAT IT DOES:
- Scans your entire computer for large files
- Automatically excludes system folders (Windows, Program Files, AppData)
- Safely delete files to Recycle Bin

HOW TO USE:
1. App opens with all drives loaded
2. Choose "Larger than" or "Smaller than"
3. Enter file size (e.g., 500 MB)
4. Click "Start Scan"
5. Select files to delete
6. Click "Delete Selected" (files go to Recycle Bin)

SYSTEM REQUIREMENTS:
- Windows 10 or 11
- 100 MB free disk space
- No Python installation needed

PROTECTED FOLDERS (Never Scanned):
✓ C:\\Windows - Operating system files
✓ Program Files - Installed applications
✓ AppData - Application settings and game saves

SAFE TO SCAN:
✓ Desktop, Documents, Downloads
✓ Pictures, Videos, Music
✓ Other user folders

SAFETY:
- All deletions go to Recycle Bin (reversible!)
- System files are automatically protected
- You can cancel scans anytime

SUPPORT:
- GitHub: https://github.com/YOUR_USERNAME/storage-manager
- Email: your-email@example.com

LICENSE: MIT (Free to use)
VERSION: 2.0
"""

readme_path = os.path.join('dist', 'README.txt')
with open(readme_path, 'w', encoding='utf-8') as f:
    f.write(user_readme)
print(f"✓ Created user README: {readme_path}")

# Create zip file
try:
    zip_name = 'StorageManager-v2.0-Windows'
    shutil.make_archive(zip_name, 'zip', 'dist')
    print(f"✓ Created distribution zip: {zip_name}.zip")
except Exception as e:
    print(f"✗ Could not create zip: {e}")
    print("  (You can manually zip the dist/ folder)")

# Summary
print("\n" + "=" * 60)
print("BUILD COMPLETE! ✓")
print("=" * 60)
print("\nYour executable is ready:")
print(f"  📁 dist/StorageManager.exe ({size_mb:.2f} MB)")
print(f"  📁 dist/README.txt")
print(f"  📦 {zip_name}.zip")

print("\nNEXT STEPS:")
print("  1. Test the executable:")
print("     cd dist")
print("     .\\StorageManager.exe")
print()
print("  2. Distribute:")
print(f"     Share {zip_name}.zip with users")
print()
print("  3. Optional:")
print("     - Add icon.ico and rebuild with icon")
print("     - Sign the .exe for Windows SmartScreen")
print("     - Create installer with Inno Setup")
print()
print("Happy distributing! 🚀")
