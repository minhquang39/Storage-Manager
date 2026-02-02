"""
GUI tab for file search by name
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import os
import string
from datetime import datetime
from send2trash import send2trash
import subprocess

from utils.file_scanner import FileScanner
from core.size_filter import SizeFilter
from localization import t


class FileSearchTab(ttk.Frame):
    """Tab for searching files by name pattern"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.file_scanner = FileScanner(self.update_progress)
        self.selected_directories = []
        self.matched_files = []
        self.scanning = False
        self.start_time = None
        
        self.create_widgets()
        
        # Auto-load all drives on startup
        self.auto_load_all_drives()
    
    def create_widgets(self):
        """Create all widgets for this tab"""
        
        # Top section - Directory selection
        top_frame = ttk.LabelFrame(self, text=t('lbl_search_scope'), padding=10)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text=t('btn_add_folder'), 
                  command=self.add_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=t('btn_scan_all_drives'), 
                  command=self.scan_all_drives).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=t('btn_remove_folder'), 
                  command=self.remove_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=t('btn_clear_all'), 
                  command=self.clear_directories).pack(side=tk.LEFT, padx=5)
        
        # Directory list
        self.dir_listbox = tk.Listbox(top_frame, height=3)
        self.dir_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Search options
        options_frame = ttk.LabelFrame(self, text=t('lbl_search_options'), padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Search pattern row
        pattern_frame = ttk.Frame(options_frame)
        pattern_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(pattern_frame, text=t('lbl_filename')).pack(side=tk.LEFT, padx=5)
        self.search_pattern = tk.StringVar()
        self.search_entry = ttk.Entry(pattern_frame, textvariable=self.search_pattern, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.search_entry.bind('<Return>', lambda e: self.start_scan())
        
        # Help text
        help_label = ttk.Label(options_frame, 
                              text=t('lbl_search_help'),
                              font=('Arial', 9, 'italic'),
                              foreground='gray')
        help_label.pack(pady=(0, 5))
        
        # Scan button
        self.scan_btn = ttk.Button(options_frame, text=t('btn_start_search'), 
                                   command=self.start_scan)
        self.scan_btn.pack(pady=5)
        
        self.cancel_btn = ttk.Button(options_frame, text=t('btn_cancel_search'), 
                                     command=self.cancel_scan, state=tk.DISABLED)
        self.cancel_btn.pack(pady=5)
        
        # Progress section
        progress_frame = ttk.LabelFrame(self, text=t('lbl_progress'), padding=10)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text=t('lbl_ready'))
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Results section
        results_frame = ttk.LabelFrame(self, text=t('lbl_files_found'), padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # File list with checkboxes
        list_frame = ttk.Frame(results_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_tree = ttk.Treeview(list_frame, 
                                     columns=('Name', 'Size', 'Modified', 'Path'),
                                     show='tree headings', 
                                     yscrollcommand=scrollbar.set)
        self.file_tree.heading('#0', text=t('col_select'))
        self.file_tree.heading('Name', text=t('col_name'))
        self.file_tree.heading('Size', text=t('col_size'))
        self.file_tree.heading('Modified', text=t('col_modified'))
        self.file_tree.heading('Path', text=t('col_path'))
        
        self.file_tree.column('#0', width=60)
        self.file_tree.column('Name', width=200)
        self.file_tree.column('Size', width=100)
        self.file_tree.column('Modified', width=150)
        self.file_tree.column('Path', width=300)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_tree.yview)
        
        # Bind double-click to open in explorer
        self.file_tree.bind("<Double-Button-1>", self.on_file_double_click)
        
        # Bind click for checkbox
        self.file_tree.bind('<Button-1>', self.on_tree_click)
        
        # Action buttons
        action_frame = ttk.Frame(results_frame)
        action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(action_frame, text=t('btn_select_all'), 
                  command=self.select_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text=t('btn_deselect_all'), 
                  command=self.deselect_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text=t('btn_delete_selected'), 
                  command=self.delete_selected, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=2)
        
        # Total info label
        self.total_label = ttk.Label(results_frame, text="")
        self.total_label.pack(pady=5)
    
    def auto_load_all_drives(self):
        """Automatically load all drives on startup"""
        drives = FileScanner.get_all_drives()
        for drive in drives:
            self.selected_directories.append(drive)
            self.dir_listbox.insert(tk.END, drive)
    
    def add_directory(self):
        """Add directory to scan list"""
        directory = filedialog.askdirectory()
        if directory and directory not in self.selected_directories:
            self.selected_directories.append(directory)
            self.dir_listbox.insert(tk.END, directory)
    
    def scan_all_drives(self):
        """Add all available drives"""
        self.clear_directories()
        self.auto_load_all_drives()
    
    def remove_directory(self):
        """Remove selected directory from list"""
        selection = self.dir_listbox.curselection()
        if selection:
            index = selection[0]
            self.dir_listbox.delete(index)
            self.selected_directories.pop(index)
    
    def clear_directories(self):
        """Clear all directories"""
        self.dir_listbox.delete(0, tk.END)
        self.selected_directories.clear()
    
    def update_progress(self, files_count, current_file):
        """Update progress display"""
        if hasattr(self, 'start_time') and self.start_time:
            elapsed = int(time.time() - self.start_time)
            time_str = f" - {elapsed}s"
        else:
            time_str = ""
        
        self.progress_label.config(
            text=t('lbl_files_searched', scanned=f"{files_count:,}", found=f"{len(self.matched_files):,}{time_str}")
        )
    
    def start_scan(self):
        """Start file search"""
        if self.scanning:
            return
        
        # Get search pattern
        pattern = self.search_pattern.get().strip()
        if not pattern:
            messagebox.showwarning(t('dlg_warning'), t('dlg_enter_filename'))
            return
        
        if not self.selected_directories:
            messagebox.showwarning(t('dlg_warning'), t('dlg_select_search_folder'))
            return
        
        # Start scan (no size filter)
        self.scanning = True
        self.start_time = time.time()
        self.file_scanner.cancelled = False
        self.scan_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.progress_bar.start()
        self.matched_files.clear()
        
        # Run scan in separate thread
        thread = threading.Thread(
            target=self.run_scan,
            args=(pattern,),
            daemon=True
        )
        thread.start()
    
    def run_scan(self, pattern):
        """Run the scan in background thread"""
        try:
            # Always case-insensitive, partial match
            pattern = pattern.lower()
            
            # Scan directories
            for directory in self.selected_directories:
                if self.file_scanner.cancelled:
                    break
                
                for filepath in self.file_scanner.scan_directory(directory):
                    if self.file_scanner.cancelled:
                        break
                    
                    # Check if filename matches pattern (case-insensitive, partial)
                    filename = os.path.basename(filepath)
                    
                    if pattern in filename.lower():
                        file_info = self.file_scanner.get_file_info(filepath)
                        self.matched_files.append(file_info)
            
            # Scan complete
            if self.scanning:
                self.after(0, self.scan_complete)
                
        except Exception as e:
            if self.scanning:
                self.after(0, lambda: self.scan_error(str(e)))
    
    def scan_complete(self):
        """Handle scan completion"""
        if not self.scanning:
            return
        
        self.scanning = False
        self.scan_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress_bar.stop()
        
        # Calculate elapsed time
        elapsed = int(time.time() - self.start_time)
        
        # Display results
        self.display_results()
        
        # Update progress label
        total_size = sum(f['size'] for f in self.matched_files)
        size_str = SizeFilter.format_size(total_size)
        
        self.progress_label.config(
            text=t('lbl_search_complete', count=f"{len(self.matched_files):,}", size=size_str, time=elapsed)
        )
    
    def scan_error(self, error_msg):
        """Handle scan error"""
        self.scanning = False
        self.scan_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress_bar.stop()
        self.progress_label.config(text=f"{t('dlg_error')}: {error_msg}")
        messagebox.showerror(t('dlg_error'), f"{t('dlg_error')}: {error_msg}")
    
    def cancel_scan(self):
        """Cancel ongoing scan"""
        self.file_scanner.cancel()
        self.scanning = False
        self.scan_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress_bar.stop()
        self.progress_label.config(text=t('progress_cancelled'))
    
    def display_results(self):
        """Display scan results"""
        # Clear tree
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Add files to tree
        for file_info in self.matched_files:
            name = file_info['name']
            size_str = SizeFilter.format_size(file_info['size'])
            modified_str = datetime.fromtimestamp(
                file_info['modified']
            ).strftime('%Y-%m-%d %H:%M:%S')
            path = file_info['path']
            
            self.file_tree.insert('', tk.END,
                                 text='☐',
                                 values=(name, size_str, modified_str, path),
                                 tags=('unchecked',))
        
        # Update totals
        self.update_total_display()
    
    def update_total_display(self):
        """Update total files and size display"""
        total_files = len(self.matched_files)
        total_size = sum(f['size'] for f in self.matched_files)
        size_str = SizeFilter.format_size(total_size)
        
        self.total_label.config(
            text=t('lbl_total_files', count=f"{total_files:,}", size=size_str)
        )
    
    def on_file_double_click(self, event):
        """Handle double-click on file to open in explorer"""
        selection = self.file_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.file_tree.item(item, 'values')
        
        # Check if it's a file row (has path)
        if values and len(values) > 3:
            filepath = values[3]  # Path is in 4th column (index 3)
            if filepath and os.path.exists(filepath):
                self.open_in_explorer(filepath)
    
    def open_in_explorer(self, filepath):
        """Open file location in Windows Explorer and select the file"""
        try:
            normalized_path = os.path.normpath(filepath)
            subprocess.run(['explorer', '/select,', normalized_path])
        except Exception as e:
            messagebox.showerror(t('dlg_error'), f"{t('dlg_error')}: {e}")
    
    def on_tree_click(self, event):
        """Handle tree item click for checkbox"""
        region = self.file_tree.identify('region', event.x, event.y)
        if region == 'tree':
            item = self.file_tree.identify_row(event.y)
            if item:
                self.toggle_checkbox(item)
    
    def toggle_checkbox(self, item):
        """Toggle checkbox state"""
        current_text = self.file_tree.item(item, 'text')
        if current_text == '☐':
            self.file_tree.item(item, text='☑', tags=('checked',))
        else:
            self.file_tree.item(item, text='☐', tags=('unchecked',))
    
    def select_all(self):
        """Select all files"""
        for item in self.file_tree.get_children():
            self.file_tree.item(item, text='☑', tags=('checked',))
    
    def deselect_all(self):
        """Deselect all files"""
        for item in self.file_tree.get_children():
            self.file_tree.item(item, text='☐', tags=('unchecked',))
    
    def delete_selected(self):
        """Delete selected files"""
        # Get selected files
        selected_files = []
        for item in self.file_tree.get_children():
            if self.file_tree.item(item, 'text') == '☑':
                values = self.file_tree.item(item, 'values')
                if values and len(values) > 3:
                    filepath = values[3]
                    selected_files.append(filepath)
        
        if not selected_files:
            messagebox.showinfo(t('dlg_no_selection_title'), t('dlg_no_selection'))
            return
        
        # Confirm deletion
        total_size = sum(
            os.path.getsize(f) for f in selected_files 
            if os.path.exists(f)
        )
        size_str = SizeFilter.format_size(total_size)
        
        if not messagebox.askyesno(t('dlg_confirm_delete'), 
                                    t('dlg_delete_count', count=f"{len(selected_files)} ({size_str})")):
            return
        
        # Delete files
        deleted_count = 0
        errors = []
        
        for filepath in selected_files:
            try:
                if os.path.exists(filepath):
                    send2trash(filepath)
                    deleted_count += 1
            except Exception as e:
                errors.append(f"{os.path.basename(filepath)}: {e}")
        
        # Show results
        if errors:
            error_msg = t('dlg_delete_success', count=deleted_count) + f"/{len(selected_files)}.\n\n"
            error_msg += f"{t('dlg_error')}:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                error_msg += f"\n... and {len(errors)-5} more"
            messagebox.showwarning(t('dlg_partial_success'), error_msg)
        else:
            messagebox.showinfo(t('dlg_success'), t('dlg_delete_success', count=deleted_count))
        
        # Remove deleted files from list
        self.matched_files = [
            f for f in self.matched_files 
            if f['path'] not in selected_files
        ]
        
        # Refresh display
        self.display_results()
