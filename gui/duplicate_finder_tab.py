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

from core.duplicate_finder import DuplicateFinder
from core.size_filter import SizeFilter


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
        top_frame = ttk.LabelFrame(self, text="Phạm Vi Quét", padding=10)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Thêm Thư Mục", 
                  command=self.add_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Quét Tất Cả Ổ", 
                  command=self.scan_all_drives).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Xóa Thư Mục", 
                  command=self.remove_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Xóa Tất Cả", 
                  command=self.clear_directories).pack(side=tk.LEFT, padx=5)
        
        # Directory list
        self.dir_listbox = tk.Listbox(top_frame, height=3)
        self.dir_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scan options
        options_frame = ttk.Frame(top_frame)
        options_frame.pack(fill=tk.X)
        
        
        ttk.Label(options_frame, text="Kích Thước Tối Thiểu:").pack(side=tk.LEFT, padx=5)
        self.min_size_var = tk.StringVar(value="0")
        ttk.Entry(options_frame, textvariable=self.min_size_var, 
                 width=10).pack(side=tk.LEFT, padx=5)
        
        self.min_size_unit_var = tk.StringVar(value="KB")
        units = ["B", "KB", "MB", "GB"]
        ttk.Combobox(options_frame, textvariable=self.min_size_unit_var, 
                    values=units, state='readonly', 
                    width=5).pack(side=tk.LEFT, padx=5)
        
        # Scan button
        self.scan_btn = ttk.Button(top_frame, text="Bắt Đầu Quét", 
                                   command=self.start_scan)
        self.scan_btn.pack(pady=5)
        
        self.cancel_btn = ttk.Button(top_frame, text="Hủy Quét", 
                                     command=self.cancel_scan, state=tk.DISABLED)
        self.cancel_btn.pack(pady=5)
        
        # Progress section
        progress_frame = ttk.LabelFrame(self, text="Tiến Trình", padding=10)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="Sẵn sàng quét")
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
        results_frame = ttk.LabelFrame(self, text="File Trùng Lặp", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Summary label
        self.summary_label = ttk.Label(results_frame, text="Chưa tìm thấy file trùng lặp")
        self.summary_label.pack(fill=tk.X, pady=(0, 5))
        
        # File list with checkboxes
        list_frame = ttk.Frame(results_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_tree = ttk.Treeview(list_frame, columns=('Group', 'Name', 'Size', 'Modified', 'Path'),
                                     show='tree headings', yscrollcommand=scrollbar.set)
        self.file_tree.heading('#0', text='Chọn')
        self.file_tree.heading('Group', text='Nhóm')
        self.file_tree.heading('Name', text='Tên File')
        self.file_tree.heading('Size', text='Kích Thước')
        self.file_tree.heading('Modified', text='Ngày Sửa')
        self.file_tree.heading('Path', text='Đường Dẫn')
        
        self.file_tree.column('#0', width=60)
        self.file_tree.column('Group', width=80)
        self.file_tree.column('Name', width=180)
        self.file_tree.column('Size', width=100)
        self.file_tree.column('Modified', width=140)
        self.file_tree.column('Path', width=350)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_tree.yview)
        
        # Action buttons
        action_frame = ttk.Frame(results_frame)
        action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(action_frame, text="Chọn Tất Cả", 
                  command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Bỏ Chọn Tất Cả", 
                  command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Tự Động Chọn (Giữ Mới Nhất)", 
                  command=lambda: self.auto_select('newest')).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Xóa Đã Chọn", 
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
            "Đồng Ý quét tất cả ổ đĩa?",
            f"Chương trình sẽ quét tất cả ổ đĩa sau:\n{drive_list}\n\n"
            f"Các thư mục hệ thống (Windows, Program Files...) sẽ tự động bỏ qua.\n\n"
            f"Quá trình này có thể mất nhiều thời gian. Tiếp tục?",
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
            text=f"Đã quét {files_count} file{time_str}... {os.path.basename(current_file)}"
        )
    
    def start_scan(self):
        """Start scanning for duplicates"""
        if not self.selected_directories:
            messagebox.showwarning("Động Lượng Trống", "Vui lòng chọn thư mục để quét")
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
            messagebox.showerror("Đầu Vào Không Hợp Lệ", "Vui lòng nhập số hợp lệ cho kích thước tối thiểu")
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
    
    def run_scan(self, min_size, scan_id):
        """Run the scan in background thread"""
        try:
            self.duplicate_groups = self.duplicate_finder.find_duplicates(
                self.selected_directories,
                min_size=min_size
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
                text=f"Tìm thấy {len(self.duplicate_groups)} nhóm trùng lặp ({total_files} file). "
                     f"Dung lượng có thể giải phóng: {size_str}"
            )
        else:
            self.progress_label.config(text="Không tìm thấy file trùng lặp")
            self.summary_label.config(text="Không tìm thấy file trùng lặp")
    
    def scan_error(self, error_msg):
        """Handle scan error"""
        # Don't do anything if scan was cancelled
        if not self.scanning:
            return
        
        self.scanning = False
        self.scan_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress_bar.stop()
        self.progress_label.config(text=f"Lỗi: {error_msg}")
        messagebox.showerror("Lỗi Quét", f"Đã xảy ra lỗi: {error_msg}")
    
    def cancel_scan(self):
        """Cancel ongoing scan"""
        self.duplicate_finder.cancel()
        self.scanning = False
        self.scan_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress_bar.stop()
        self.progress_label.config(text="Đã hủy quét")
    
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
            text=f"Tìm thấy {len(self.duplicate_groups)} nhóm trùng lặp với {total_files} file tổng cộng"
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
        
        # Configure alternating colors for groups
        self.file_tree.tag_configure('group0', background='#f0f0f0')
        self.file_tree.tag_configure('group1', background='white')
    
    def on_tree_click(self, event):
        """Handle tree item click for checkbox"""
        region = self.file_tree.identify_region(event.x, event.y)
        if region == "tree":
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
            messagebox.showinfo("Không Có Nhóm", "Không có nhóm trùng lặp để chọn")
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
            messagebox.showinfo("Chưa Chọn File", "Vui lòng chọn file để xóa")
            return
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Xác Nhận Xóa",
            f"Chuyển {len(selected_files)} file vào Thùng Rác?"
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
                messages.append(f"✓ Đã chuyển {success_count} file vào Thùng Rác")
            
            if skipped:
                messages.append(f"⚠ Bỏ qua {len(skipped)} file (đã bị xóa hoặc di chuyển)")
            
            if failed:
                error_details = "\n".join([f"  • {os.path.basename(f)}: {e}" 
                                          for f, e in failed[:3]])
                if len(failed) > 3:
                    error_details += f"\n  • ... và {len(failed) - 3} lỗi khác"
                messages.append(f"✗ Không thể xóa {len(failed)} file:\n{error_details}")
            
            # Show appropriate message
            if failed and success_count == 0:
                messagebox.showerror("Xóa Thất Bại", "\n\n".join(messages))
            elif failed or skipped:
                messagebox.showwarning("Thành Công Một Phần", "\n\n".join(messages))
            else:
                messagebox.showinfo("Thành Công", "\n\n".join(messages))
            
            # Refresh display
            self.display_all_duplicates()
