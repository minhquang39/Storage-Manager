"""
GUI tab for file type filter
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from datetime import datetime
from send2trash import send2trash
import os

from core.file_type_filter import FileTypeFilter
from core.size_filter import SizeFilter


class FileTypeFilterTab(ttk.Frame):
    """Tab for finding and managing files by type/extension"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.file_type_filter = FileTypeFilter(self.update_progress)
        self.selected_directories = []
        self.matched_files = []
        self.scanning = False
        self.group_vars = {}  # Store checkbox variables for each group
        
        self.create_widgets()
        
        # Auto-load all drives on startup
        self.auto_load_all_drives()
    
    def create_widgets(self):
        """Create all widgets for this tab"""
        
        # Top section - Directory selection
        top_frame = ttk.LabelFrame(self, text="Phạm Vi Quét (Tất cả ổ đĩa đã được tải)", padding=10)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Thêm Thư Mục", 
                  command=self.add_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Quét Tất Cả Ổ", 
                  command=self.scan_all_drives).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Xóa Tất Cả", 
                  command=self.clear_directories).pack(side=tk.LEFT, padx=5)
        
        # Directory list
        self.dir_listbox = tk.Listbox(top_frame, height=3)
        self.dir_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # File type filter options
        options_frame = ttk.LabelFrame(self, text="Chọn Loại File", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create checkboxes for each file type group
        groups_container = ttk.Frame(options_frame)
        groups_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Split into two columns for better layout
        left_col = ttk.Frame(groups_container)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        right_col = ttk.Frame(groups_container)
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Get group info and create checkboxes
        groups = FileTypeFilter.FILE_TYPE_GROUPS
        group_items = list(groups.items())
        mid_point = (len(group_items) + 1) // 2
        
        for idx, (group_key, group_data) in enumerate(group_items):
            container = left_col if idx < mid_point else right_col
            
            var = tk.BooleanVar(value=False)
            self.group_vars[group_key] = var
            
            # Create frame for each group
            group_frame = ttk.Frame(container)
            group_frame.pack(fill=tk.X, pady=2)
            
            # Checkbox
            cb = ttk.Checkbutton(group_frame, 
                                text=group_data['name'],
                                variable=var)
            cb.pack(side=tk.LEFT)
            
            # Extension count label
            ext_count = len(group_data['extensions'])
            ext_preview = ', '.join(list(group_data['extensions'])[:3])
            if ext_count > 3:
                ext_preview += f', ... (+{ext_count - 3})'
            
            tooltip = ttk.Label(group_frame, 
                              text=f"({ext_count} loại: {ext_preview})",
                              foreground='gray')
            tooltip.pack(side=tk.LEFT, padx=5)
        
        # Scan button
        self.scan_btn = ttk.Button(options_frame, text="Bắt Đầu Quét", 
                                   command=self.start_scan)
        self.scan_btn.pack(pady=5)
        
        self.cancel_btn = ttk.Button(options_frame, text="Hủy Quét", 
                                     command=self.cancel_scan, state=tk.DISABLED)
        self.cancel_btn.pack(pady=5)
        
        # Progress section
        progress_frame = ttk.LabelFrame(self, text="Tiến Trình", padding=10)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="Sẵn sàng quét")
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Results section
        results_frame = ttk.LabelFrame(self, text="File Tìm Thấy", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # File list with checkboxes
        list_frame = ttk.Frame(results_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_tree = ttk.Treeview(list_frame, 
                                     columns=('Group', 'Name', 'Size', 'Modified', 'Path'),
                                     show='tree headings', 
                                     yscrollcommand=scrollbar.set)
        self.file_tree.heading('#0', text='Chọn')
        self.file_tree.heading('Group', text='Loại')
        self.file_tree.heading('Name', text='Tên File')
        self.file_tree.heading('Size', text='Kích Thước')
        self.file_tree.heading('Modified', text='Ngày Sửa')
        self.file_tree.heading('Path', text='Đường Dẫn')
        
        self.file_tree.column('#0', width=50)
        self.file_tree.column('Group', width=120)
        self.file_tree.column('Name', width=180)
        self.file_tree.column('Size', width=100)
        self.file_tree.column('Modified', width=130)
        self.file_tree.column('Path', width=280)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_tree.yview)
        
        # Action buttons (always visible at bottom)
        action_frame = ttk.Frame(results_frame)
        action_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        
        ttk.Button(action_frame, text="Chọn Tất Cả", 
                  command=self.select_all_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Bỏ Chọn Tất Cả", 
                  command=self.deselect_all_files).pack(side=tk.LEFT, padx=5)
        
        self.total_label = ttk.Label(action_frame, text="Tổng: 0 file, 0 B")
        self.total_label.pack(side=tk.LEFT, padx=20)
        
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
        
        # Clear existing and add all drives
        self.selected_directories.clear()
        self.dir_listbox.delete(0, tk.END)
        
        for drive in drives:
            self.selected_directories.append(drive)
            self.dir_listbox.insert(tk.END, drive)
    
    def clear_directories(self):
        """Clear all selected directories"""
        self.selected_directories.clear()
        self.dir_listbox.delete(0, tk.END)
    
    def select_all_groups(self):
        """Select all file type groups"""
        for var in self.group_vars.values():
            var.set(True)
    
    def deselect_all_groups(self):
        """Deselect all file type groups"""
        for var in self.group_vars.values():
            var.set(False)
    
    def update_progress(self, files_count, current_file):
        """Update progress display"""
        self.progress_label.config(
            text=f"Đã quét {files_count} file... {os.path.basename(current_file)}"
        )
    
    def start_scan(self):
        """Start scanning for files matching type criteria"""
        if not self.selected_directories:
            messagebox.showwarning("Chưa Chọn Thư Mục", "Vui lòng chọn thư mục để quét")
            return
        
        # Get selected groups
        selected_groups = {
            group_key for group_key, var in self.group_vars.items() 
            if var.get()
        }
        
        if not selected_groups:
            messagebox.showwarning("Chưa Chọn Loại File", 
                                 "Vui lòng chọn ít nhất một loại file để quét")
            return
        
        self.scanning = True
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
            args=(selected_groups,),
            daemon=True
        )
        thread.start()
    
    def run_scan(self, selected_groups):
        """Run the scan in background thread"""
        try:
            self.matched_files = self.file_type_filter.find_files_by_types(
                self.selected_directories,
                selected_groups
            )
            self.after(0, self.scan_complete)
        except Exception as e:
            self.after(0, lambda: self.scan_error(str(e)))
    
    def scan_complete(self):
        """Handle scan completion"""
        self.scanning = False
        self.scan_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress_bar.stop()
        
        if self.matched_files:
            self.display_results()
            total_size = sum(f['size'] for f in self.matched_files)
            size_str = SizeFilter.format_size(total_size)
            self.progress_label.config(
                text=f"Tìm thấy {len(self.matched_files)} file. Tổng dung lượng: {size_str}"
            )
        else:
            self.progress_label.config(text="Không tìm thấy file nào")
    
    def scan_error(self, error_msg):
        """Handle scan error"""
        self.scanning = False
        self.scan_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress_bar.stop()
        self.progress_label.config(text=f"Lỗi: {error_msg}")
        messagebox.showerror("Lỗi Quét", f"Đã xảy ra lỗi: {error_msg}")
    
    def cancel_scan(self):
        """Cancel ongoing scan"""
        self.file_type_filter.cancel()
        self.scanning = False
        self.scan_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress_bar.stop()
        self.progress_label.config(text="Đã hủy quét")
    
    def display_results(self):
        """Display scan results"""
        # Clear tree
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Sort by group then by size
        sorted_files = sorted(self.matched_files, 
                            key=lambda x: (x.get('group', ''), -x['size']))
        
        # Add files to tree
        for file_info in sorted_files:
            group = file_info.get('group', '❓ Khác')
            name = file_info['name']
            size_str = SizeFilter.format_size(file_info['size'])
            modified_str = datetime.fromtimestamp(
                file_info['modified']
            ).strftime('%Y-%m-%d %H:%M:%S')
            path = file_info['path']
            
            self.file_tree.insert('', tk.END,
                                 text='☐',
                                 values=(group, name, size_str, modified_str, path),
                                 tags=('unchecked',))
        
        # Update totals
        self.update_total_display()
    
    def on_tree_click(self, event):
        """Handle tree item click for checkbox"""
        region = self.file_tree.identify_region(event.x, event.y)
        if region == "tree":
            item = self.file_tree.identify_row(event.y)
            if item:
                self.toggle_checkbox(item)
                self.update_total_display()
    
    def toggle_checkbox(self, item):
        """Toggle checkbox state"""
        current_text = self.file_tree.item(item, 'text')
        if current_text == '☐':
            self.file_tree.item(item, text='☑', tags=('checked',))
        else:
            self.file_tree.item(item, text='☐', tags=('unchecked',))
    
    def select_all_files(self):
        """Select all files"""
        for item in self.file_tree.get_children():
            self.file_tree.item(item, text='☑', tags=('checked',))
        self.update_total_display()
    
    def deselect_all_files(self):
        """Deselect all files"""
        for item in self.file_tree.get_children():
            self.file_tree.item(item, text='☐', tags=('unchecked',))
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
                path = self.file_tree.item(item, 'values')[4]
                for f in self.matched_files:
                    if f['path'] == path:
                        selected_size += f['size']
                        break
        
        total_str = SizeFilter.format_size(total_size)
        selected_str = SizeFilter.format_size(selected_size)
        
        self.total_label.config(
            text=f"Tổng: {total_count} file ({total_str}) | "
                 f"Đã chọn: {selected_count} file ({selected_str})"
        )
    
    def delete_selected(self):
        """Delete selected files"""
        selected_files = []
        for item in self.file_tree.get_children():
            if self.file_tree.item(item, 'text') == '☑':
                filepath = self.file_tree.item(item, 'values')[4]
                selected_files.append(filepath)
        
        if not selected_files:
            messagebox.showinfo("Chưa Chọn File", "Vui lòng chọn file để xóa")
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
            "Xác Nhận Xóa",
            f"Chuyển {len(selected_files)} file ({size_str}) vào Thùng Rác?"
        )
        
        if result:
            failed = []
            skipped = []
            success_count = 0
            
            for filepath in selected_files:
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
            
            # Remove deleted and skipped files from list and refresh display
            deleted_paths = set(selected_files) - {f for f, _ in failed}
            self.matched_files = [f for f in self.matched_files 
                                if f['path'] not in deleted_paths]
            self.display_results()
