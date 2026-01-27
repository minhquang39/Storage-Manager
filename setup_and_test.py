"""
Setup and Test Script for Storage Manager

This script helps you:
1. Verify Python version
2. Install dependencies
3. Test core functionality
4. Launch the application
"""

import sys
import subprocess
import os


def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python {version.major}.{version.minor} detected")
        print("❌ Python 3.7 or higher is required")
        return False
    else:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
        return True


def install_dependencies():
    """Install required dependencies"""
    print("\nInstalling dependencies...")
    
    try:
        # Read requirements
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip().split('\n')
        
        print(f"Dependencies to install: {', '.join(requirements)}")
        
        # Install using pip
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def test_imports():
    """Test if all modules can be imported"""
    print("\nTesting imports...")
    
    tests = [
        ("send2trash", "send2trash"),
        ("Tkinter", "tkinter"),
        ("Core modules", "core.duplicate_finder"),
        ("Core modules", "core.size_filter"),
        ("Utils", "utils.file_scanner"),
        ("Utils", "utils.hash_calculator"),
        ("GUI", "gui.duplicate_finder_tab"),
        ("GUI", "gui.size_filter_tab"),
    ]
    
    all_passed = True
    for name, module in tests:
        try:
            __import__(module)
            print(f"✓ {name}: OK")
        except ImportError as e:
            print(f"❌ {name}: FAILED - {e}")
            all_passed = False
    
    return all_passed


def test_basic_functionality():
    """Test basic functionality without GUI"""
    print("\nTesting basic functionality...")
    
    try:
        # Test FileScanner
        from utils.file_scanner import FileScanner
        scanner = FileScanner()
        print("✓ FileScanner: OK")
        
        # Test HashCalculator
        from utils.hash_calculator import HashCalculator
        hasher = HashCalculator()
        print("✓ HashCalculator: OK")
        
        # Test DuplicateFinder
        from core.duplicate_finder import DuplicateFinder
        finder = DuplicateFinder()
        print("✓ DuplicateFinder: OK")
        
        # Test SizeFilter
        from core.size_filter import SizeFilter
        size_filter = SizeFilter()
        print("✓ SizeFilter: OK")
        
        # Test size formatting
        formatted = SizeFilter.format_size(1536000)
        assert "MB" in formatted or "KB" in formatted
        print(f"✓ Size formatting: {formatted}")
        
        # Test safe directory check
        is_safe = scanner.is_safe_directory("C:\\Users\\Public")
        print(f"✓ Safe directory check: {is_safe}")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_project_info():
    """Display project information"""
    print("\n" + "=" * 60)
    print("STORAGE MANAGER - Setup Complete")
    print("=" * 60)
    print("\nProject Structure:")
    print("  main.py              - Start GUI application")
    print("  config.py            - Configuration settings")
    print("  core/                - Business logic")
    print("  gui/                 - User interface")
    print("  utils/               - Utilities")
    print("  examples/            - Usage examples")
    print("\nDocumentation:")
    print("  README.md            - Complete documentation")
    print("  QUICKSTART.md        - 5-minute guide")
    print("  ARCHITECTURE.md      - System design")
    print("  PROJECT_STRUCTURE.txt - File organization")
    print("\nNext Steps:")
    print("  1. Run: python main.py")
    print("  2. Or read: QUICKSTART.md")
    print("  3. Or try: python examples/programmatic_usage.py")
    print("=" * 60)


def launch_application():
    """Launch the main application"""
    print("\nWould you like to launch the application now? (y/n): ", end='')
    choice = input().strip().lower()
    
    if choice == 'y':
        print("\nLaunching Storage Manager...")
        try:
            import main
            main.main()
        except Exception as e:
            print(f"Error launching application: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main setup and test workflow"""
    print("=" * 60)
    print("STORAGE MANAGER - Setup and Test")
    print("=" * 60)
    
    # Step 1: Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Install dependencies
    print("\nWould you like to install dependencies? (y/n): ", end='')
    choice = input().strip().lower()
    
    if choice == 'y':
        if not install_dependencies():
            print("\n❌ Setup failed at dependency installation")
            sys.exit(1)
    else:
        print("Skipping dependency installation")
    
    # Step 3: Test imports
    if not test_imports():
        print("\n❌ Some imports failed")
        print("Try running: pip install -r requirements.txt")
        sys.exit(1)
    
    # Step 4: Test basic functionality
    if not test_basic_functionality():
        print("\n❌ Functionality tests failed")
        sys.exit(1)
    
    # Step 5: Show success message
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)
    
    show_project_info()
    
    # Step 6: Optionally launch application
    launch_application()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
