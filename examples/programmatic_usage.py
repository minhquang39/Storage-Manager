"""
Example: Using Storage Manager components programmatically

This demonstrates how to use the core modules without the GUI
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.duplicate_finder import DuplicateFinder
from core.size_filter import SizeFilter
from utils.file_scanner import FileScanner
from utils.hash_calculator import HashCalculator


def example_1_find_duplicates():
    """Example 1: Find duplicate files in a directory"""
    print("=" * 60)
    print("Example 1: Finding Duplicate Files")
    print("=" * 60)
    
    # Create duplicate finder
    def progress_callback(count, filepath):
        """Show progress every 100 files"""
        if count % 100 == 0:
            print(f"Scanned {count} files...")
    
    finder = DuplicateFinder(progress_callback)
    
    # Specify directories to scan (change these to your directories)
    directories = [
        r"C:\Users\Public\Documents",  # Example path
        # Add more directories here
    ]
    
    print(f"\nScanning directories: {directories}")
    print("This may take a few minutes...\n")
    
    # Find duplicates (minimum 1KB size)
    duplicates = finder.find_duplicates(directories, min_size=1024)
    
    # Display results
    print(f"\nFound {len(duplicates)} groups of duplicates\n")
    
    total_wasted_space = 0
    for hash_value, files in duplicates.items():
        print(f"\nDuplicate Group ({len(files)} files):")
        print(f"Hash: {hash_value[:16]}...")
        
        for file_info in files:
            size_mb = file_info['size'] / (1024 * 1024)
            print(f"  - {file_info['name']} ({size_mb:.2f} MB)")
            print(f"    Path: {file_info['path']}")
        
        # Calculate wasted space (all but one copy)
        wasted = sum(f['size'] for f in files[1:])
        total_wasted_space += wasted
        print(f"  Wasted space: {wasted / (1024*1024):.2f} MB")
    
    print(f"\n{'='*60}")
    print(f"Total wasted space: {total_wasted_space / (1024*1024):.2f} MB")
    print(f"{'='*60}")


def example_2_find_large_files():
    """Example 2: Find files larger than specified size"""
    print("\n" + "=" * 60)
    print("Example 2: Finding Large Files")
    print("=" * 60)
    
    # Create size filter
    size_filter = SizeFilter()
    
    # Specify directories
    directories = [
        r"C:\Users\Public\Videos",  # Example path
    ]
    
    print(f"\nScanning for files larger than 100 MB...")
    print(f"Directories: {directories}\n")
    
    # Find files larger than 100 MB
    large_files = size_filter.find_files_by_size(
        directories,
        size_condition='larger_than',
        size_value=100,
        size_unit='MB'
    )
    
    # Sort by size (largest first)
    large_files.sort(key=lambda x: x['size'], reverse=True)
    
    # Display results
    print(f"Found {len(large_files)} large files:\n")
    
    total_size = 0
    for i, file_info in enumerate(large_files[:10], 1):  # Show top 10
        size_str = SizeFilter.format_size(file_info['size'])
        print(f"{i}. {file_info['name']}")
        print(f"   Size: {size_str}")
        print(f"   Path: {file_info['path']}\n")
        total_size += file_info['size']
    
    if len(large_files) > 10:
        print(f"... and {len(large_files) - 10} more files")
    
    print(f"\nTotal size of all large files: {SizeFilter.format_size(sum(f['size'] for f in large_files))}")


def example_3_custom_file_scanning():
    """Example 3: Custom file scanning with filters"""
    print("\n" + "=" * 60)
    print("Example 3: Custom File Scanning")
    print("=" * 60)
    
    # Create scanner
    scanner = FileScanner()
    
    # Scan directory
    directory = r"C:\Users\Public\Pictures"  # Example path
    
    print(f"\nScanning: {directory}")
    print("Finding image files larger than 1 MB...\n")
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    images = []
    
    # Scan with minimum size of 1 MB
    for filepath in scanner.scan_directory(directory, min_size=1024*1024):
        ext = os.path.splitext(filepath)[1].lower()
        if ext in image_extensions:
            file_info = scanner.get_file_info(filepath)
            images.append(file_info)
    
    print(f"Found {len(images)} large images:\n")
    
    for img in images[:5]:  # Show first 5
        size_str = SizeFilter.format_size(img['size'])
        print(f"- {img['name']} ({size_str})")
    
    if len(images) > 5:
        print(f"... and {len(images) - 5} more")


def example_4_hash_calculation():
    """Example 4: Calculate file hashes"""
    print("\n" + "=" * 60)
    print("Example 4: Hash Calculation")
    print("=" * 60)
    
    # Get a file path (use your own file)
    filepath = r"C:\Windows\System32\notepad.exe"  # Example file
    
    if not os.path.exists(filepath):
        print(f"\nFile not found: {filepath}")
        print("Please update the filepath in the example")
        return
    
    print(f"\nCalculating hashes for: {filepath}\n")
    
    hash_calc = HashCalculator()
    
    # Calculate different hashes
    print("Full SHA-256 hash:")
    sha256 = hash_calc.calculate_file_hash(filepath, 'sha256')
    print(f"  {sha256}\n")
    
    print("Full MD5 hash (faster but less secure):")
    md5 = hash_calc.calculate_file_hash(filepath, 'md5')
    print(f"  {md5}\n")
    
    print("Quick hash (for pre-filtering):")
    quick = hash_calc.calculate_quick_hash(filepath)
    print(f"  {quick}\n")
    
    # File info
    size = os.path.getsize(filepath)
    print(f"File size: {SizeFilter.format_size(size)}")


def example_5_safe_deletion():
    """Example 5: Safe file deletion to Recycle Bin"""
    print("\n" + "=" * 60)
    print("Example 5: Safe File Deletion")
    print("=" * 60)
    
    print("\nThis example demonstrates safe deletion using send2trash")
    print("Files are moved to Recycle Bin, not permanently deleted\n")
    
    # Example code (don't actually run without user confirmation)
    print("Example code:")
    print("-" * 40)
    print("""
from send2trash import send2trash

# Delete a single file
send2trash('path/to/file.txt')

# Delete multiple files
files_to_delete = [
    'duplicate1.txt',
    'duplicate2.txt',
    'large_file.mp4'
]

for filepath in files_to_delete:
    try:
        send2trash(filepath)
        print(f"Moved to Recycle Bin: {filepath}")
    except Exception as e:
        print(f"Error deleting {filepath}: {e}")
    """)
    print("-" * 40)
    print("\nNote: Always confirm with users before deleting files!")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("STORAGE MANAGER - Programmatic Usage Examples")
    print("=" * 60)
    print("\nNOTE: Update the directory paths in each example")
    print("to match your system before running.\n")
    
    # Choose which examples to run
    examples = {
        '1': ('Find Duplicate Files', example_1_find_duplicates),
        '2': ('Find Large Files', example_2_find_large_files),
        '3': ('Custom File Scanning', example_3_custom_file_scanning),
        '4': ('Hash Calculation', example_4_hash_calculation),
        '5': ('Safe Deletion (demo only)', example_5_safe_deletion),
    }
    
    print("Available examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print("  0. Run all examples")
    print("  q. Quit")
    
    choice = input("\nEnter your choice: ").strip()
    
    if choice == 'q':
        return
    elif choice == '0':
        for _, func in examples.values():
            func()
            input("\nPress Enter to continue to next example...")
    elif choice in examples:
        _, func = examples[choice]
        func()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    # Note: Make sure to install dependencies first:
    # pip install send2trash
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
