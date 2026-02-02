"""
GUI tab for duplicate file finder
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

from core.duplicate_finder import DuplicateFinder
from core.size_filter import SizeFilter
from localization import t


class DuplicateFinderTab(ttk.Frame):
    """Tab for finding and managing duplicate files"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.duplicate_finder = DuplicateFinder(self.update_progress)
        self.selected_directories = []
        self.duplicate_groups = {}
        self.current_group_index = 0
        self.scanning = False
        self.current_scan_id = 0  # Track scan sessions
        self.start_time = None  # Track scan start time
        
        self.create_widgets()
    
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
        
        # Scan options
        options_frame = ttk.Frame(top_frame)
        options_frame.pack(fill=tk.X)
        
        
        ttk.Label(options_frame, text=t('lbl_min_size')).pack(side=tk.LEFT, padx=5)
        self.min_size_var = tk.StringVar(value="0")
        ttk.Entry(options_frame, textvariable=self.min_size_var, 
                 width=10).pack(side=tk.LEFT, padx=5)
        
        self.min_size_unit_var = tk.StringVar(value="KB")
        units = ["B", "KB", "MB", "GB"]
        ttk.Combobox(options_frame, textvariable=self.min_size_unit_var, 
                    values=units, state='readonly', 
                    width=5).pack(side=tk.LEFT, padx=5)
        
        # Scan button
        self.scan_btn = ttk.Button(top_frame, text=t('btn_start_scan'), 
                                   command=self.start_scan)
        self.scan_btn.pack(pady=5)
        
        self.cancel_btn = ttk.Button(top_frame, text=t('btn_cancel_scan'), 
                                     command=self.cancel_scan, state=tk.DISABLED)
        self.cancel_btn.pack(pady=5)
        
        # Progress section
        progress_frame = ttk.LabelFrame(self, text=t('lbl_progress'), padding=10)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text=t('lbl_ready'))
        self.progress_label.pack()
        
        # Create custom style for progress bar
        style = ttk.Style()
        style.theme_use('clam')  # Use clam theme for better customization
        style.configure("Custom.Horizontal.TProgressbar",
                       troughcolor='#e0e0e0',
                       background='#4CAF50',  # Green color
                       darkcolor='#388E3C',
                       lightcolor='#66BB6A',
                       bordercolor='#cccccc',
                       borderwidth=1)
        
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                           mode='indeterminate',
                                           style='Custom.Horizontal.TProgressbar')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Results section
        results_frame = ttk.LabelFrame(self, text=t('lbl_duplicates'), padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Summary label
        self.summary_label = ttk.Label(results_frame, text=t('lbl_no_duplicates'))
        self.summary_label.pack(fill=tk.X, pady=(0, 5))
        
        # File list with checkboxes
        list_frame = ttk.Frame(results_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_tree = ttk.Treeview(list_frame, columns=('Group', 'Name', 'Size', 'Modified', 'Path'),
                                     show='tree headings', yscrollcommand=scrollbar.set)
        self.file_tree.heading('#0', text=t('col_select'))
        self.file_tree.heading('Group', text=t('col_group'))
        self.file_tree.heading('Name', text=t('col_name'))
        self.file_tree.heading('Size', text=t('col_size'))
        self.file_tree.heading('Modified', text=t('col_modified'))
        self.file_tree.heading('Path', text=t('col_path'))
        
        self.file_tree.column('#0', width=60, anchor='center')
        self.file_tree.column('Group', width=80, anchor='center')
        self.file_tree.column('Name', width=180)
        self.file_tree.column('Size', width=100, anchor='center')
        self.file_tree.column('Modified', width=140, anchor='center')
        self.file_tree.column('Path', width=350)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_tree.yview)
        
        # Bind double-click to open in explorer
        self.file_tree.bind("<Double-Button-1>", self.on_file_double_click)
        
        # Action buttons
        action_frame = ttk.Frame(results_frame)
        action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(action_frame, text=t('btn_select_all'), 
                  command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text=t('btn_deselect_all'), 
                  command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text=t('btn_auto_select'), 
                  command=lambda: self.auto_select('newest')).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text=t('btn_delete_selected'), 
                  command=self.delete_selected, 
                  style='Accent.TButton').pack(side=tk.RIGHT, padx=5)
        
        # Bind click event for checkboxes
        self.file_tree.bind('<Button-1>', self.on_tree_click)
    
    def add_directory(self):
        """Add directory to scan list"""
        directory = filedialog.askdirectory()
        if directory and directory not in self.selected_directories:
            self.selected_directories.append(directory)
            self.dir_listbox.insert(tk.END, directory)
    
    def scan_all_drives(self):
        """Add all available drives to scan list"""
        from utils.file_scanner import FileScanner
        
        # Get all drives
        drives = FileScanner.get_all_drives()
        
        # Confirm with user
        drive_list = ", ".join(drives)
        result = messagebox.askyesno(
            t('dlg_confirm_delete'),
            t('msg_confirm_scan_all') + f"\n{drive_list}",
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
            messagebox.showinfo(t('dlg_no_selection_title'), t('dlg_select_folder'))
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
        """Start scanning for duplicates"""
        if not self.selected_directories:
            messagebox.showwarning(t('dlg_no_folders_title'), t('dlg_no_folders'))
            return
        
        # Get min file size
        try:
            min_size_value = float(self.min_size_var.get())
            min_size_unit = self.min_size_unit_var.get()
            
            # Convert to bytes based on unit
            unit_multipliers = {
                'B': 1,
                'KB': 1024,
                'MB': 1024 * 1024,
                'GB': 1024 * 1024 * 1024
            }
            min_size_bytes = int(min_size_value * unit_multipliers.get(min_size_unit, 1024))
        except ValueError:
            messagebox.showerror(t('dlg_invalid_input_title'), t('dlg_invalid_input'))
            return
        
        self.scanning = True
        self.start_time = time.time()  # Start timer
        self.current_scan_id += 1  # Increment scan ID
        scan_id = self.current_scan_id  # Capture current ID
        self.duplicate_finder.cancelled = False  # Reset cancelled flag
        self.scan_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.progress_bar.start()
        self.duplicate_groups.clear()
        
        # Run scan in separate thread
        thread = threading.Thread(
            target=self.run_scan,
            args=(min_size_bytes, scan_id),
            daemon=True
        )
        thread.start()
    
    def update_hash_progress(self, phase, current, total, filename):
        """Update progress for hash calculation phases"""
        if hasattr(self, 'start_time') and self.start_time:
            elapsed = int(time.time() - self.start_time)
            time_str = f" - {elapsed}s"
        else:
            time_str = ""
        
        if phase == "quick_hash":
            phase_name = t('progress_quick_compare')
        else:  # full_hash
            phase_name = t('progress_detailed_check')
        
        percentage = int((current / total * 100)) if total > 0 else 0
        self.progress_label.config(
            text=f"{phase_name}: {current:,}/{total:,} files ({percentage}%){time_str}..."
        )
    
    def run_scan(self, min_size, scan_id):
        """Run the scan in background thread"""
        try:
            self.duplicate_groups = self.duplicate_finder.find_duplicates(
                self.selected_directories,
                min_size=min_size,
                hash_progress_callback=lambda phase, cur, tot, file: 
                    self.after(0, lambda: self.update_hash_progress(phase, cur, tot, file))
            )
            # Only update UI if this is still the current scan
            if self.scanning and scan_id == self.current_scan_id:
                self.after(0, self.scan_complete)
        except Exception as e:
            # Only show error if this is still the current scan
            if self.scanning and scan_id == self.current_scan_id:
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
        
        if self.duplicate_groups:
            self.display_all_duplicates()
            total_files = sum(len(files) for files in self.duplicate_groups.values())
            total_size = sum(
                sum(f['size'] for f in files[1:])  # Size of duplicates (excluding one to keep)
                for files in self.duplicate_groups.values()
            )
            size_str = SizeFilter.format_size(total_size)
            self.progress_label.config(
                text=t('lbl_found_duplicates', groups=len(self.duplicate_groups), files=total_files, size=size_str)
            )
        else:
            self.progress_label.config(text=t('lbl_no_duplicates'))
            self.summary_label.config(text=t('lbl_no_duplicates'))
    
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
        messagebox.showerror(t('dlg_error'), error_msg)
    
    def cancel_scan(self):
        """Cancel ongoing scan"""
        self.duplicate_finder.cancel()
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
        
        # Check if it's a file row (has path in values)
        if values and len(values) > 4:
            filepath = values[4]  # Path is in 5th column (index 4)
            if filepath and os.path.exists(filepath):
                self.open_in_explorer(filepath)
    
    def open_in_explorer(self, filepath):
        """Open file location in Windows Explorer and select the file"""
        try:
            normalized_path = os.path.normpath(filepath)
            subprocess.run(['explorer', '/select,', normalized_path])
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở file explorer: {e}")
    
    def display_all_duplicates(self):
        """Display all duplicate files in a flat list"""
        if not self.duplicate_groups:
            return
        
        # Clear tree
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Display summary
        total_files = sum(len(files) for files in self.duplicate_groups.values())
        self.summary_label.config(
            text=t('lbl_found_groups', groups=len(self.duplicate_groups), files=total_files)
        )
        
        # Add all files to tree, group by group
        for group_idx, (hash_value, files) in enumerate(self.duplicate_groups.items(), 1):
            for file_info in files:
                name = os.path.basename(file_info['path'])
                size_str = SizeFilter.format_size(file_info['size'])
                modified_str = datetime.fromtimestamp(file_info['modified']).strftime('%Y-%m-%d %H:%M:%S')
                
                # Use alternating tags for visual grouping
                tag = f"group{group_idx % 2}"
                
                self.file_tree.insert('', tk.END, 
                                     text='☐',
                                     values=(f"#{group_idx}", name, size_str, modified_str, file_info['path']),
                                     tags=(tag, 'unchecked'))
        
        # Configure alternating colors for groups (will be updated by theme)
        # Default to dark theme colors since app starts with darkly theme
        self.file_tree.tag_configure('group0', background='#1a252f', foreground='#FFFFFF')
        self.file_tree.tag_configure('group1', background='#2b3e50', foreground='#FFFFFF')
        self.file_tree.tag_configure('checked', background='#375a7f', foreground='#FFFFFF')
        self.file_tree.tag_configure('unchecked', foreground='#FFFFFF')
    
    def on_tree_click(self, event):
        """Handle tree item click for checkbox"""
        region = self.file_tree.identify_region(event.x, event.y)
        # Allow clicking anywhere on the row (tree, cell) to toggle checkbox
        if region in ("tree", "cell"):
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
    
    def auto_select(self, strategy):
        """Auto-select files based on strategy (newest/oldest)"""
        if not self.duplicate_groups:
            messagebox.showinfo(t('dlg_info'), t('msg_no_groups'))
            return
        
        # First, deselect all
        for item in self.file_tree.get_children():
            self.file_tree.item(item, text='☐', tags=('unchecked',))
        
        # Build a mapping of path -> tree item for quick lookup
        path_to_item = {}
        for item in self.file_tree.get_children():
            values = self.file_tree.item(item, 'values')
            path = values[4]  # Path column
            path_to_item[path] = item
        
        # For each group in duplicate_groups, find the file to keep
        for hash_value, files in self.duplicate_groups.items():
            if len(files) <= 1:
                continue
            
            # Sort by modification timestamp
            if strategy == 'newest':
                sorted_files = sorted(files, key=lambda x: x['modified'], reverse=True)
            else:
                sorted_files = sorted(files, key=lambda x: x['modified'])
            
            # Keep the first one (newest or oldest), select all others
            keep_file = sorted_files[0]['path']
            
            for file_info in sorted_files[1:]:
                path = file_info['path']
                if path in path_to_item:
                    item = path_to_item[path]
                    # Get current tags
                    current_tags = list(self.file_tree.item(item, 'tags'))
                    # Update checkbox
                    self.file_tree.item(item, text='☑')
                    # Update tags - keep group tag, set to checked
                    new_tags = [t for t in current_tags if t.startswith('group')]
                    new_tags.append('checked')
                    self.file_tree.item(item, tags=tuple(new_tags))
    
    def delete_selected(self):
        """Delete selected files"""
        selected_files = []
        for item in self.file_tree.get_children():
            if self.file_tree.item(item, 'text') == '☑':
                values = self.file_tree.item(item, 'values')
                filepath = values[4]  # Path is now column 4 (Group, Name, Size, Modified, Path)
                selected_files.append(filepath)
        
        if not selected_files:
            messagebox.showinfo(t('dlg_no_selection_title'), t('dlg_no_selection'))
            return
        
        # Confirm deletion
        result = messagebox.askyesno(
            t('dlg_confirm_delete'),
            t('dlg_delete_count', count=len(selected_files))
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
            
            # Refresh display
            self.display_all_duplicates()
