"""
Storage Manager - Desktop Application for Managing Computer Storage

Main application entry point
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
import json

# Try to use ttkbootstrap for modern UI
try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.constants import *
    USE_BOOTSTRAP = True
except ImportError:
    USE_BOOTSTRAP = False

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.duplicate_finder_tab import DuplicateFinderTab
from gui.size_filter_tab import SizeFilterTab
from gui.file_type_filter_tab import FileTypeFilterTab
# from gui.file_search_tab import FileSearchTab  # Temporarily hidden
from localization import Localization, t
import config


class StorageManagerApp(ttkb.Window if USE_BOOTSTRAP else tk.Tk):
    """Main application window"""
    
    # Settings file path
    SETTINGS_DIR = os.path.join(os.getenv('APPDATA', os.path.expanduser('~')), 'StorageManager')
    SETTINGS_FILE = os.path.join(SETTINGS_DIR, 'settings.json')
    
    @staticmethod
    def _load_settings_static() -> dict:
        """Load settings from file (static method for use before __init__)"""
        settings_file = os.path.join(
            os.getenv('APPDATA', os.path.expanduser('~')), 
            'StorageManager', 
            'settings.json'
        )
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {'theme': 'darkly', 'language': 'vi'}  # Defaults
    
    def __init__(self):
        # Load saved settings
        settings = StorageManagerApp._load_settings_static()
        saved_theme = settings.get('theme', 'darkly')
        saved_lang = settings.get('language', 'vi')
        
        # Set language before creating UI
        Localization.set_lang(saved_lang)
        
        if USE_BOOTSTRAP:
            super().__init__(themename=saved_theme)
        else:
            super().__init__()
        
        self.current_theme = saved_theme
        self.current_lang = saved_lang
        
        self.title(t('app_title'))
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        
        # Set minimum window size
        
        # Set minimum window size
        self.minsize(800, 600)
        
        # Configure style
        self.setup_style()
        
        # Create menu bar
        self.create_menu()
        
        # Create notebook (tab container) for two features
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: Duplicate Finder
        self.duplicate_tab = DuplicateFinderTab(self.notebook)
        self.notebook.add(self.duplicate_tab, text=t('tab_duplicate'))
        
        # Tab 2: Size Filter
        self.size_tab = SizeFilterTab(self.notebook)
        self.notebook.add(self.size_tab, text=t('tab_size_filter'))
        
        # Tab 3: File Type Filter
        self.file_type_tab = FileTypeFilterTab(self.notebook)
        self.notebook.add(self.file_type_tab, text=t('tab_file_type'))
        
        # Tab 4: File Search (Temporarily hidden)
        # self.search_tab = FileSearchTab(self.notebook)
        # self.notebook.add(self.search_tab, text="🔍 Tìm Kiếm File")
        
        # Status bar
        self.create_status_bar()
        
        # Set icon (if available)
        self.set_icon()
        
        # Handle window closing
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Auto-cleanup cache on startup (runs in background)
        self.after(1000, self._auto_cleanup_cache)
        
        # Apply saved theme styles (Treeview colors, etc.) after window is ready
        if USE_BOOTSTRAP:
            self.after(100, lambda: self.change_theme(self.current_theme, save=False))
    
    def _save_setting(self, key: str, value):
        """Save a setting to settings file"""
        try:
            os.makedirs(self.SETTINGS_DIR, exist_ok=True)
            
            # Load existing settings or create new
            settings = {}
            if os.path.exists(self.SETTINGS_FILE):
                try:
                    with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                except Exception:
                    pass
            
            # Update setting
            settings[key] = value
            
            # Save
            with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
        except Exception:
            pass  # Silent failure
    
    def change_language(self, lang: str):
        """Change application language"""
        if lang != self.current_lang:
            self.current_lang = lang
            Localization.set_lang(lang)
            self._save_setting('language', lang)
            
            # Show message that restart is needed for full effect
            from tkinter import messagebox
            if lang == 'vi':
                messagebox.showinfo(
                    "Đổi ngôn ngữ",
                    "Đã chuyển sang Tiếng Việt.\n\n"
                    "Vui lòng khởi động lại ứng dụng để áp dụng hoàn toàn."
                )
            else:
                messagebox.showinfo(
                    "Language Changed", 
                    "Switched to English.\n\n"
                    "Please restart the application for full effect."
                )
    
    def setup_style(self):
        """Configure application style"""
        if USE_BOOTSTRAP:
            # Configure styles for better readability
            style = ttk.Style()
            
            # Button fonts
            style.configure('TButton', font=('Segoe UI', 10, 'normal'))
            style.configure('primary.TButton', font=('Segoe UI', 10, 'normal'))
            style.configure('danger.TButton', font=('Segoe UI', 10, 'normal'))
            style.configure('success.TButton', font=('Segoe UI', 10, 'normal'))
            style.configure('info.TButton', font=('Segoe UI', 10, 'normal'))
            style.configure('warning.TButton', font=('Segoe UI', 10, 'normal'))
            style.configure('secondary.TButton', font=('Segoe UI', 10, 'normal'))
            
            # Improve Treeview text contrast for dark themes
            style.configure('Treeview', 
                          font=('Segoe UI', 10),
                          rowheight=28)
            style.configure('Treeview.Heading', 
                          font=('Segoe UI', 10, 'bold'))
            
            # High contrast text for labels
            style.configure('TLabel', font=('Segoe UI', 10))
            style.configure('TLabelframe.Label', font=('Segoe UI', 11, 'bold'))
            
            # Make Treeview selection more visible
            style.map('Treeview',
                     background=[('selected', '#0078D4')],
                     foreground=[('selected', 'white')])
            return
        
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
        
        # Theme menu (only if ttkbootstrap is available)
        if USE_BOOTSTRAP:
            theme_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="🎨 Theme", menu=theme_menu)
            
            # Light themes
            theme_menu.add_command(label="☀️ Cosmo (Light)", command=lambda: self.change_theme("cosmo"))
            theme_menu.add_command(label="☀️ Flatly (Light)", command=lambda: self.change_theme("flatly"))
            theme_menu.add_command(label="☀️ Journal (Light)", command=lambda: self.change_theme("journal"))
            theme_menu.add_command(label="☀️ Litera (Light)", command=lambda: self.change_theme("litera"))
            theme_menu.add_separator()
            # Dark themes
            theme_menu.add_command(label="🌙 Darkly (Dark)", command=lambda: self.change_theme("darkly"))
            theme_menu.add_command(label="🌙 Solar (Dark)", command=lambda: self.change_theme("solar"))
            theme_menu.add_command(label="🌙 Superhero (Dark)", command=lambda: self.change_theme("superhero"))
            theme_menu.add_command(label="🌙 Cyborg (Dark)", command=lambda: self.change_theme("cyborg"))
        
        # Language menu
        lang_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=t('menu_language'), menu=lang_menu)
        lang_menu.add_command(label=t('lang_vietnamese'), command=lambda: self.change_language('vi'))
        lang_menu.add_command(label=t('lang_english'), command=lambda: self.change_language('en'))
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=t('menu_help'), menu=help_menu)
        help_menu.add_command(label=t('menu_about'), command=self.show_about)
        help_menu.add_command(label=t('menu_instructions'), command=self.show_instructions)
    
    def change_theme(self, theme_name, save=True):
        """Change application theme"""
        if USE_BOOTSTRAP:
            self.style.theme_use(theme_name)
            self.current_theme = theme_name
            
            # Save theme preference (skip when loading on startup)
            if save:
                self._save_setting('theme', theme_name)
            
            # Adjust text contrast based on theme type
            dark_themes = {'darkly', 'solar', 'superhero', 'cyborg', 'vapor', 'slate'}
            is_dark = theme_name.lower() in dark_themes
            
            style = ttk.Style()
            if is_dark:
                # High contrast for dark themes - white/light text
                style.configure('Treeview', 
                              foreground='#FFFFFF',
                              background='#2b3e50',
                              fieldbackground='#2b3e50',
                              font=('Segoe UI', 10),
                              rowheight=28)
                style.configure('Treeview.Heading',
                              foreground='#FFFFFF', 
                              background='#1a252f',
                              font=('Segoe UI', 10, 'bold'))
                style.map('Treeview',
                         background=[('selected', '#0078D4')],
                         foreground=[('selected', '#FFFFFF')])
                
                # Update duplicate finder tab row colors for dark theme
                self._update_duplicate_tab_colors(is_dark=True)
            else:
                # Normal contrast for light themes
                style.configure('Treeview',
                              foreground='#212529',
                              background='#ffffff',
                              fieldbackground='#ffffff', 
                              font=('Segoe UI', 10),
                              rowheight=28)
                style.configure('Treeview.Heading',
                              foreground='#212529',
                              background='#e9ecef',
                              font=('Segoe UI', 10, 'bold'))
                style.map('Treeview',
                         background=[('selected', '#0078D4')],
                         foreground=[('selected', '#FFFFFF')])
                
                # Update duplicate finder tab row colors for light theme
                self._update_duplicate_tab_colors(is_dark=False)
    
    def _update_duplicate_tab_colors(self, is_dark: bool):
        """Update duplicate finder tab alternating row colors based on theme"""
        try:
            if hasattr(self, 'duplicate_tab') and hasattr(self.duplicate_tab, 'file_tree'):
                tree = self.duplicate_tab.file_tree
                if is_dark:
                    # Dark theme - darker alternating colors
                    tree.tag_configure('group0', background='#1a252f', foreground='#FFFFFF')
                    tree.tag_configure('group1', background='#2b3e50', foreground='#FFFFFF')
                    tree.tag_configure('checked', background='#375a7f', foreground='#FFFFFF')
                    tree.tag_configure('unchecked', foreground='#FFFFFF')
                else:
                    # Light theme - light alternating colors
                    tree.tag_configure('group0', background='#f0f0f0', foreground='#212529')
                    tree.tag_configure('group1', background='#ffffff', foreground='#212529')
                    tree.tag_configure('checked', background='#cce5ff', foreground='#212529')
                    tree.tag_configure('unchecked', foreground='#212529')
        except Exception:
            pass  # Ignore errors if tab not ready
    
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
        from tkinter import messagebox
        messagebox.showinfo(t('about_title'), t('about_text'))
    
    def show_instructions(self):
        """Show instructions dialog"""
        from tkinter import messagebox
        messagebox.showinfo(t('instructions_title'), t('instructions_text'))
    
    def _get_cache(self):
        """Get or create hash cache instance"""
        from utils.hash_cache import HashCache
        return HashCache()
    
    def _auto_cleanup_cache(self):
        """Auto cleanup cache on startup (runs silently in background)"""
        import threading
        
        def cleanup_task():
            try:
                cache = self._get_cache()
                
                # Cleanup orphaned entries (files that no longer exist)
                orphaned_deleted = cache.cleanup_orphaned()
                
                # Cleanup old entries (not accessed in 30+ days)
                old_deleted = cache.cleanup_stale(max_age_days=30)
                
                # Compact if anything was deleted
                if orphaned_deleted > 0 or old_deleted > 0:
                    cache.vacuum()
                    # Update status bar (schedule on main thread)
                    total = orphaned_deleted + old_deleted
                    self.after(0, lambda: self.update_status(
                        f"Cache auto-cleanup: removed {total:,} old entries"))
                
                cache.close()
            except Exception:
                pass  # Silent failure - don't bother user
        
        # Run in background thread to not block UI
        thread = threading.Thread(target=cleanup_task, daemon=True)
        thread.start()
    
    def show_cache_stats(self):
        """Show cache statistics"""
        from tkinter import messagebox
        try:
            cache = self._get_cache()
            stats = cache.get_stats()
            cache.close()
            
            msg = f"""📊 Cache Statistics

📁 Database: {stats['db_path']}

📈 Total Entries: {stats['total_entries']:,}
💾 Cache Size: {stats['cache_size_mb']:.2f} MB
📦 Avg per Entry: {(stats['cache_size_mb']*1024*1024/stats['total_entries']):.0f} bytes""" if stats['total_entries'] > 0 else f"""📊 Cache Statistics

📁 Database: {stats['db_path']}
📈 Cache is empty"""
            
            messagebox.showinfo("Cache Statistics", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get cache stats: {e}")
    
    def cleanup_orphaned_cache(self):
        """Remove cache entries for files that no longer exist"""
        from tkinter import messagebox
        try:
            cache = self._get_cache()
            self.update_status("Cleaning orphaned cache entries...")
            self.update_idletasks()
            
            deleted = cache.cleanup_orphaned()
            cache.vacuum()
            cache.close()
            
            messagebox.showinfo("Cleanup Complete", 
                              f"🧹 Removed {deleted:,} orphaned entries\n"
                              f"(Files that no longer exist)")
            self.update_status("Ready")
        except Exception as e:
            messagebox.showerror("Error", f"Cleanup failed: {e}")
            self.update_status("Ready")
    
    def cleanup_old_cache(self):
        """Remove cache entries older than 30 days"""
        from tkinter import messagebox
        try:
            cache = self._get_cache()
            deleted = cache.cleanup_stale(max_age_days=30)
            cache.vacuum()
            cache.close()
            
            messagebox.showinfo("Cleanup Complete", 
                              f"📆 Removed {deleted:,} old entries\n"
                              f"(Not accessed in 30+ days)")
        except Exception as e:
            messagebox.showerror("Error", f"Cleanup failed: {e}")
    
    def vacuum_cache(self):
        """Compact database to reclaim space"""
        from tkinter import messagebox
        try:
            cache = self._get_cache()
            
            # Get size before
            stats_before = cache.get_stats()
            
            cache.vacuum()
            
            # Get size after
            stats_after = cache.get_stats()
            cache.close()
            
            saved = stats_before['cache_size_mb'] - stats_after['cache_size_mb']
            messagebox.showinfo("Compact Complete", 
                              f"🗜️ Database compacted\n\n"
                              f"Before: {stats_before['cache_size_mb']:.2f} MB\n"
                              f"After: {stats_after['cache_size_mb']:.2f} MB\n"
                              f"Saved: {saved:.2f} MB")
        except Exception as e:
            messagebox.showerror("Error", f"Compact failed: {e}")
    
    def clear_all_cache(self):
        """Clear entire cache after confirmation"""
        from tkinter import messagebox
        if messagebox.askyesno("Confirm Clear Cache", 
                              "⚠️ This will delete ALL cached hashes.\n\n"
                              "Next scan will need to recalculate all hashes.\n\n"
                              "Continue?"):
            try:
                cache = self._get_cache()
                cache.clear_all()
                cache.close()
                messagebox.showinfo("Cache Cleared", "🗑️ All cache entries have been deleted.")
            except Exception as e:
                messagebox.showerror("Error", f"Clear failed: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        # Cancel any ongoing operations in all tabs
        try:
            self.duplicate_tab.cancel_scan()
        except:
            pass
        
        try:
            self.size_tab.cancel_scan()
        except:
            pass
        
        try:
            self.file_type_tab.cancel_scan()
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
