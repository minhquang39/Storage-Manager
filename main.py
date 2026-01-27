"""
Storage Manager - Desktop Application for Managing Computer Storage

Main application entry point
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# from gui.duplicate_finder_tab import DuplicateFinderTab  # Disabled
from gui.size_filter_tab import SizeFilterTab
import config


class StorageManagerApp(tk.Tk):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Storage Manager - System-Wide File Scanner")
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        
        # Set minimum window size
        self.minsize(800, 600)
        
        # Configure style
        self.setup_style()
        
        # Create menu bar
        self.create_menu()
        
        # Main content frame (no tabs needed - single feature)
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add Size Filter (main and only feature)
        self.size_tab = SizeFilterTab(main_frame)
        self.size_tab.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.create_status_bar()
        
        # Set icon (if available)
        self.set_icon()
        
        # Handle window closing
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_style(self):
        """Configure application style"""
        style = ttk.Style()
        
        # Use a modern theme
        try:
            style.theme_use('clam')  # Modern, cross-platform theme
        except:
            style.theme_use('default')
        
        # Configure colors
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0')
        style.configure('TLabelframe', background='#f0f0f0')
        style.configure('TLabelframe.Label', background='#f0f0f0', font=('Arial', 10, 'bold'))
        
        # Configure button style
        style.configure('TButton', padding=6, relief="flat", background="#0078D4")
        style.map('TButton', background=[('active', '#106EBE')])
        
        # Configure accent button
        style.configure('Accent.TButton', 
                       padding=6, 
                       relief="flat", 
                       background="#D13438",
                       foreground="white")
        style.map('Accent.TButton', 
                 background=[('active', '#A02024')])
    
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Instructions", command=self.show_instructions)
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        status_frame = ttk.Frame(self, relief=tk.SUNKEN)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(
            status_frame, 
            text="Ready  |  Storage Manager v2.0 - System Scanner", 
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
    
    def set_icon(self):
        """Set application icon if available"""
        try:
            # Try to set icon (you can add your own icon file)
            icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except:
            pass
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Storage Manager v2.0

System-wide file scanner and cleanup tool.

Features:
• Automatic full system scan
• Find large files across all drives
• Protected system folders
• Safe deletion (Recycle Bin)

Protected Folders:
✓ Windows (System32, DLLs)
✓ Program Files (installed apps)
✓ AppData (app settings & saves)
✓ System recovery folders

Developed with Python and Tkinter

© 2026"""
        
        from tkinter import messagebox
        messagebox.showinfo("About Storage Manager", about_text)
    
    def show_instructions(self):
        """Show instructions dialog"""
        instructions = """How to Use Storage Manager:

AUTOMATIC SYSTEM SCAN:
• All drives are loaded automatically (C:\, D:\, etc.)
• System folders are protected and excluded
• Ready to scan on startup!

FIND FILES BY SIZE:
1. Choose condition: "Larger than" or "Smaller than"
2. Enter size value (e.g., 100) and unit (MB, GB)
3. Click "Start Scan" - scans entire system
4. Review results sorted by size
5. Select files you want to remove
6. Click "Delete Selected"

PROTECTED FOLDERS (Never Scanned):
✓ C:\Windows - Operating system files
✓ Program Files - Installed applications
✓ AppData - App settings and game saves
✓ System recovery folders

SAFE USER FOLDERS (Will Be Scanned):
✓ Desktop, Documents, Downloads
✓ Pictures, Videos, Music
✓ Other user-created folders

SAFETY FEATURES:
• All deletions go to Recycle Bin (reversible)
• System-critical folders automatically excluded
• Confirmation before deletion
• Cancel scan anytime"""
        
        from tkinter import messagebox
        messagebox.showinfo("Instructions", instructions)
    
    def on_closing(self):
        """Handle window closing"""
        # Cancel any ongoing operations
        try:
            self.size_tab.cancel_scan()
        except:
            pass
        
        self.destroy()


def main():
    """Main entry point"""
    # Check if send2trash is installed
    try:
        import send2trash
    except ImportError:
        print("Error: Required package 'send2trash' is not installed.")
        print("Please run: pip install send2trash")
        sys.exit(1)
    
    # Create and run application
    app = StorageManagerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
