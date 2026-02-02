"""
GUI tab for file size filter
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from datetime import datetime
from send2trash import send2trash
import os
import subprocess

from core.size_filter import SizeFilter
from localization import t


class SizeFilterTab(ttk.Frame):
    """Tab for finding and managing files by size"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.size_filter = SizeFilter(self.update_progress)
        self.selected_directories = []
        self.matched_files = []
        self.scanning = False
        self.start_time = None  # Track scan start time
        
        self.create_widgets()
        
        # Auto-load all drives on startup
        self.auto_load_all_drives()
    
    def create_widgets(self):
        """Create all widgets for this tab"""
        
        # Top section - Directory selection
        top_frame = ttk.LabelFrame(self, text=t('lbl_scan_scope'), padding=10)
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
        
        # Size filter options
        options_frame = ttk.LabelFrame(self, text=t('lbl_filter_options'), padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Condition row
        condition_frame = ttk.Frame(options_frame)
        condition_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(condition_frame, text=t('lbl_find_file')).pack(side=tk.LEFT, padx=5)
        
        self.condition_var = tk.StringVar(value="larger_than")
        conditions = [
            (t('lbl_larger_than'), "larger_than"),
            (t('lbl_smaller_than'), "smaller_than"),
        ]
        for text, value in conditions:
            ttk.Radiobutton(condition_frame, text=text, 
                          variable=self.condition_var, 
                          value=value).pack(side=tk.LEFT, padx=5)
        
        # Size input row
        size_frame = ttk.Frame(options_frame)
        size_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(size_frame, text=t('lbl_size')).pack(side=tk.LEFT, padx=5)
        self.size_value_var = tk.StringVar(value="100")
        ttk.Entry(size_frame, textvariable=self.size_value_var, 
                 width=15).pack(side=tk.LEFT, padx=5)
        
        self.size_unit_var = tk.StringVar(value="MB")
        units = ["B", "KB", "MB", "GB"]
        ttk.Combobox(size_frame, textvariable=self.size_unit_var, 
                    values=units, state='readonly', 
                    width=5).pack(side=tk.LEFT, padx=5)
        
        # Scan button
        self.scan_btn = ttk.Button(options_frame, text=t('btn_start_scan'), 
                                   command=self.start_scan)
        self.scan_btn.pack(pady=5)
        
        self.cancel_btn = ttk.Button(options_frame, text=t('btn_cancel_scan'), 
                                     command=self.cancel_scan, state=tk.DISABLED)
        self.cancel_btn.pack(pady=5)
        
        # Progress section
        progress_frame = ttk.LabelFrame(self, text=t('lbl_progress'), padding=10)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text=t('lbl_ready'))
        self.progress_label.pack()
        
        # Create custom style for progress bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.Horizontal.TProgressbar",
                       troughcolor='#e0e0e0',
                       background='#4CAF50',
                       darkcolor='#388E3C',
                       lightcolor='#66BB6A',
                       bordercolor='#cccccc',
                       borderwidth=1)
        
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                           mode='indeterminate',
                                           style='Custom.Horizontal.TProgressbar')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Results section
        results_frame = ttk.LabelFrame(self, text=t('lbl_files_found'), padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Action buttons (pack first at bottom to ensure visibility)
        action_frame = ttk.Frame(results_frame)
        action_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        
        ttk.Button(action_frame, text=t('btn_select_all'), 
                  command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text=t('btn_deselect_all'), 
                  command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        
        self.total_label = ttk.Label(action_frame, text="")
        self.total_label.pack(side=tk.LEFT, padx=20)
        
        ttk.Button(action_frame, text=t('btn_delete_selected'), 
                  command=self.delete_selected,
                  style='Accent.TButton').pack(side=tk.RIGHT, padx=5)
        
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
        
        self.file_tree.column('#0', width=60, anchor='center')
        self.file_tree.column('Name', width=200)
        self.file_tree.column('Size', width=100, anchor='center')
        self.file_tree.column('Modified', width=150, anchor='center')
        self.file_tree.column('Path', width=300)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_tree.yview)
        
        # Bind double-click to open in explorer
        self.file_tree.bind("<Double-Button-1>", self.on_file_double_click)
        
        # Bind click event for checkboxes
        self.file_tree.bind('<Button-1>', self.on_tree_click)
        
        # Bind checkbox toggle to update total
        self.file_tree.bind('<<TreeviewSelect>>', self.update_selected_total)
    
    def add_directory(self):
        """Add directory to scan list"""
        directory = filedialog.askdirectory()
        if directory and directory not in self.selected_directories:
            self.selected_directories.append(directory)
            self.dir_listbox.insert(tk.END, directory)
    
    def auto_load_all_drives(self):
        """Automatically load all drives on startup (silent)"""
        from utils.file_scanner import FileScanner
        
        # Get all drives
        drives = FileScanner.get_all_drives()
        
        # Clear existing and add all drives
        self.selected_directories.clear()
        self.dir_listbox.delete(0, tk.END)
        
        for drive in drives:
            self.selected_directories.append(drive)
            self.dir_listbox.insert(tk.END, drive)
    
    def scan_all_drives(self):
        """Add all available drives to scan list"""
        from utils.file_scanner import FileScanner
        
        # Get all drives
        drives = FileScanner.get_all_drives()
        
        # Confirm with user
        drive_list = ", ".join(drives)
        result = messagebox.askyesno(
            "Scan All Drives",
            f"This will scan all available drives:\n{drive_list}\n\n"
            f"System folders (Windows, Program Files, AppData) will be automatically excluded.\n\n"
            f"This may take a long time. Continue?",
            icon='warning'
        )
        
        if result:
            # Clear existing and add all drives
            self.selected_directories.clear()
            self.dir_listbox.delete(0, tk.END)
            
            for drive in drives:
                self.selected_directories.append(drive)
                self.dir_listbox.insert(tk.END, drive)
    
    def remove_directory(self):
        """Remove selected directory from scan list"""
        selection = self.dir_listbox.curselection()
        if not selection:
            messagebox.showinfo("Chưa Chọn", "Vui lòng chọn thư mục để xóa")
            return
        
        # Get selected index
        index = selection[0]
        # Remove from list and listbox
        removed_dir = self.selected_directories.pop(index)
        self.dir_listbox.delete(index)
    
    def clear_directories(self):
        """Clear all selected directories"""
        self.selected_directories.clear()
        self.dir_listbox.delete(0, tk.END)
    
    def update_progress(self, files_count, current_file):
        """Update progress display"""
        # Calculate elapsed time
        if hasattr(self, 'start_time') and self.start_time:
            elapsed = int(time.time() - self.start_time)
            time_str = f" - {elapsed}s"
        else:
            time_str = ""
        
        self.progress_label.config(
            text=t('progress_scanning', path=f"{files_count:,} files{time_str}...")
        )
    
    def start_scan(self):
        """Start scanning for files matching size criteria"""
        if not self.selected_directories:
            messagebox.showwarning(t('dlg_no_folders_title'), t('dlg_no_folders'))
            return
        
        try:
            size_value = float(self.size_value_var.get())
            if size_value <= 0:
                raise ValueError("Size must be positive")
        except ValueError as e:
            messagebox.showerror(t('dlg_invalid_input_title'), 
                               t('dlg_invalid_input'))
            return
        
        size_unit = self.size_unit_var.get()
        condition = self.condition_var.get()
        
        self.scanning = True
        self.start_time = time.time()  # Start timer
        self.size_filter.cancelled = False  # Reset cancelled flag
        self.scan_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.progress_bar.start()
        self.matched_files.clear()
        
        # Clear previous results
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Run scan in separate thread
        thread = threading.Thread(
            target=self.run_scan,
            args=(condition, size_value, size_unit),
            daemon=True
        )
        thread.start()
    
    def run_scan(self, condition, size_value, size_unit):
        """Run the scan in background thread"""
        try:
            self.matched_files = self.size_filter.find_files_by_size(
                self.selected_directories,
                condition,
                size_value,
                size_unit
            )
            # Only update UI if scan wasn't cancelled
            if self.scanning:
                self.after(0, self.scan_complete)
        except Exception as e:
            # Only show error if scan wasn't cancelled
            if self.scanning:
                self.after(0, lambda: self.scan_error(str(e)))
    
    def scan_complete(self):
        """Handle scan completion"""
        # Don't do anything if scan was cancelled
        if not self.scanning:
            return
        
        self.scanning = False
        self.scan_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress_bar.stop()
        if self.matched_files:
            self.display_results()
            total_size = sum(f['size'] for f in self.matched_files)
            size_str = SizeFilter.format_size(total_size)
            self.progress_label.config(
                text=t('progress_found_size', count=len(self.matched_files), size=size_str)
            )
        else:
            self.progress_label.config(text=t('progress_no_match'))
    
    def scan_error(self, error_msg):
        """Handle scan error"""
        # Don't do anything if scan was cancelled
        if not self.scanning:
            return
        
        self.scanning = False
        self.scan_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress_bar.stop()
        self.progress_label.config(text=f"{t('dlg_error')}: {error_msg}")
        messagebox.showerror(t('dlg_error'), f"{t('dlg_error')}: {error_msg}")
    
    def cancel_scan(self):
        """Cancel ongoing scan"""
        self.size_filter.cancel()
        self.scanning = False
        self.scan_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress_bar.stop()
        self.progress_label.config(text=t('progress_cancelled'))
    
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
            messagebox.showerror("Lỗi", f"Không thể mở file explorer: {e}")
    
    def display_results(self):
        """Display scan results (optimized for large datasets)"""
        # Clear tree
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Sort by size (descending) - largest files first
        sorted_files = sorted(self.matched_files, 
                            key=lambda x: x['size'], 
                            reverse=True)
        
        # Limit display to top 1000 files for performance
        MAX_DISPLAY = 1000
        display_files = sorted_files[:MAX_DISPLAY]
        hidden_count = len(sorted_files) - MAX_DISPLAY if len(sorted_files) > MAX_DISPLAY else 0
        
        # Add files to tree
        for file_info in display_files:
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
        
        # Show warning if truncated
        if hidden_count > 0:
            self.file_tree.insert('', tk.END,
                                 text='⚠',
                                 values=(f'... và {hidden_count} file khác (ẩn để tăng tốc)', '', '', ''),
                                 tags=('info',))
        
        # Update totals
        self.update_total_display()
    
    def on_tree_click(self, event):
        """Handle tree item click for checkbox"""
        region = self.file_tree.identify_region(event.x, event.y)
        # Allow clicking anywhere on the row (tree, cell) to toggle checkbox
        if region in ("tree", "cell"):
            item = self.file_tree.identify_row(event.y)
            if item:
                # Skip info rows (truncation warning)
                values = self.file_tree.item(item, 'values')
                if values and values[0] and not values[0].startswith('...'):
                    self.toggle_checkbox(item)
                    self.update_total_display()
    
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
        self.update_total_display()
    
    def deselect_all(self):
        """Deselect all files"""
        for item in self.file_tree.get_children():
            self.file_tree.item(item, text='☐', tags=('unchecked',))
        self.update_total_display()
    
    def update_selected_total(self, event=None):
        """Update total for selected files"""
        self.update_total_display()
    
    def update_total_display(self):
        """Update the total size display"""
        total_count = len(self.matched_files)
        total_size = sum(f['size'] for f in self.matched_files)
        
        # Calculate selected
        selected_count = 0
        selected_size = 0
        
        for item in self.file_tree.get_children():
            if self.file_tree.item(item, 'text') == '☑':
                selected_count += 1
                # Find matching file
                path = self.file_tree.item(item, 'values')[3]
                for f in self.matched_files:
                    if f['path'] == path:
                        selected_size += f['size']
                        break
        
        total_str = SizeFilter.format_size(total_size)
        selected_str = SizeFilter.format_size(selected_size)
        
        self.total_label.config(
            text=t('lbl_total_selected', total_count=total_count, total_size=total_str, sel_count=selected_count, sel_size=selected_str)
        )
    
    def delete_selected(self):
        """Delete selected files"""
        selected_files = []
        for item in self.file_tree.get_children():
            if self.file_tree.item(item, 'text') == '☑':
                filepath = self.file_tree.item(item, 'values')[3]
                selected_files.append(filepath)
        
        if not selected_files:
            messagebox.showinfo(t('dlg_no_selection_title'), t('dlg_no_selection'))
            return
        
        # Calculate total size to delete
        total_size = 0
        for filepath in selected_files:
            for f in self.matched_files:
                if f['path'] == filepath:
                    total_size += f['size']
                    break
        
        size_str = SizeFilter.format_size(total_size)
        
        # Confirm deletion
        result = messagebox.askyesno(
            t('dlg_confirm_delete'),
            t('dlg_delete_count', count=f"{len(selected_files)} ({size_str})")
        )
        
        if result:
            failed = []
            skipped = []
            success_count = 0
            
            for filepath in selected_files:
                # Normalize path to Windows format (convert / to \)
                filepath = os.path.normpath(filepath)
                
                # Check if file still exists
                if not os.path.exists(filepath):
                    skipped.append(filepath)
                    continue
                
                try:
                    send2trash(filepath)
                    success_count += 1
                except Exception as e:
                    failed.append((filepath, str(e)))
            
            # Build result message
            messages = []
            if success_count > 0:
                messages.append(t('dlg_delete_success', count=success_count))
            
            if skipped:
                messages.append(t('dlg_delete_skipped', count=len(skipped)))
            
            if failed:
                error_details = "\n".join([f"  • {os.path.basename(f)}: {e}" 
                                          for f, e in failed[:3]])
                if len(failed) > 3:
                    error_details += f"\n  • ... and {len(failed) - 3} more"
                messages.append(f"{t('dlg_delete_failed', count=len(failed))}:\n{error_details}")
            
            # Show appropriate message
            if failed and success_count == 0:
                messagebox.showerror(t('dlg_failed'), "\n\n".join(messages))
            elif failed or skipped:
                messagebox.showwarning(t('dlg_partial_success'), "\n\n".join(messages))
            else:
                messagebox.showinfo(t('dlg_success'), "\n\n".join(messages))
            
            # Remove deleted and skipped files from list and refresh display
            deleted_paths = set(selected_files) - {f for f, _ in failed}
            self.matched_files = [f for f in self.matched_files 
                                if f['path'] not in deleted_paths]
            self.display_results()
