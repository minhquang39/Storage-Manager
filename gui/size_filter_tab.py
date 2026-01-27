"""
GUI tab for file size filter
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from datetime import datetime
from send2trash import send2trash
import os

from core.size_filter import SizeFilter


class SizeFilterTab(ttk.Frame):
    """Tab for finding and managing files by size"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.size_filter = SizeFilter(self.update_progress)
        self.selected_directories = []
        self.matched_files = []
        self.scanning = False
        
        self.create_widgets()
        
        # Auto-load all drives on startup
        self.auto_load_all_drives()
    
    def create_widgets(self):
        """Create all widgets for this tab"""
        
        # Top section - Directory selection
        top_frame = ttk.LabelFrame(self, text="Scan Scope (All Drives Loaded by Default)", padding=10)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Add Folder", 
                  command=self.add_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Scan All Drives", 
                  command=self.scan_all_drives).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear All", 
                  command=self.clear_directories).pack(side=tk.LEFT, padx=5)
        
        # Directory list
        self.dir_listbox = tk.Listbox(top_frame, height=3)
        self.dir_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Size filter options
        options_frame = ttk.LabelFrame(self, text="Size Filter", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Condition row
        condition_frame = ttk.Frame(options_frame)
        condition_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(condition_frame, text="Find files:").pack(side=tk.LEFT, padx=5)
        
        self.condition_var = tk.StringVar(value="larger_than")
        conditions = [
            ("Larger than", "larger_than"),
            ("Smaller than", "smaller_than"),
        ]
        for text, value in conditions:
            ttk.Radiobutton(condition_frame, text=text, 
                          variable=self.condition_var, 
                          value=value).pack(side=tk.LEFT, padx=5)
        
        # Size input row
        size_frame = ttk.Frame(options_frame)
        size_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(size_frame, text="Size:").pack(side=tk.LEFT, padx=5)
        self.size_value_var = tk.StringVar(value="100")
        ttk.Entry(size_frame, textvariable=self.size_value_var, 
                 width=15).pack(side=tk.LEFT, padx=5)
        
        self.size_unit_var = tk.StringVar(value="MB")
        units = ["B", "KB", "MB", "GB"]
        ttk.Combobox(size_frame, textvariable=self.size_unit_var, 
                    values=units, state='readonly', 
                    width=5).pack(side=tk.LEFT, padx=5)
        
        # Scan button
        self.scan_btn = ttk.Button(options_frame, text="Start Scan", 
                                   command=self.start_scan)
        self.scan_btn.pack(pady=5)
        
        self.cancel_btn = ttk.Button(options_frame, text="Cancel Scan", 
                                     command=self.cancel_scan, state=tk.DISABLED)
        self.cancel_btn.pack(pady=5)
        
        # Progress section
        progress_frame = ttk.LabelFrame(self, text="Progress", padding=10)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="Ready to scan")
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Results section
        results_frame = ttk.LabelFrame(self, text="Matching Files", padding=10)
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
        self.file_tree.heading('#0', text='Select')
        self.file_tree.heading('Name', text='Name')
        self.file_tree.heading('Size', text='Size')
        self.file_tree.heading('Modified', text='Modified')
        self.file_tree.heading('Path', text='Path')
        
        self.file_tree.column('#0', width=60)
        self.file_tree.column('Name', width=200)
        self.file_tree.column('Size', width=100)
        self.file_tree.column('Modified', width=150)
        self.file_tree.column('Path', width=300)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_tree.yview)
        
        # Action buttons
        action_frame = ttk.Frame(results_frame)
        action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(action_frame, text="Select All", 
                  command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Deselect All", 
                  command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        
        self.total_label = ttk.Label(action_frame, text="Total: 0 files, 0 B")
        self.total_label.pack(side=tk.LEFT, padx=20)
        
        ttk.Button(action_frame, text="Delete Selected", 
                  command=self.delete_selected,
                  style='Accent.TButton').pack(side=tk.RIGHT, padx=5)
        
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
    
    def clear_directories(self):
        """Clear all selected directories"""
        self.selected_directories.clear()
        self.dir_listbox.delete(0, tk.END)
    
    def update_progress(self, files_count, current_file):
        """Update progress display"""
        self.progress_label.config(
            text=f"Scanned {files_count} files... {os.path.basename(current_file)}"
        )
    
    def start_scan(self):
        """Start scanning for files matching size criteria"""
        if not self.selected_directories:
            messagebox.showwarning("No Folders", "Please select folders to scan")
            return
        
        try:
            size_value = float(self.size_value_var.get())
            if size_value <= 0:
                raise ValueError("Size must be positive")
        except ValueError as e:
            messagebox.showerror("Invalid Input", 
                               f"Please enter a valid positive number for size")
            return
        
        size_unit = self.size_unit_var.get()
        condition = self.condition_var.get()
        
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
                text=f"Found {len(self.matched_files)} matching files. Total size: {size_str}"
            )
        else:
            self.progress_label.config(text="No matching files found")
    
    def scan_error(self, error_msg):
        """Handle scan error"""
        self.scanning = False
        self.scan_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress_bar.stop()
        self.progress_label.config(text=f"Error: {error_msg}")
        messagebox.showerror("Scan Error", f"An error occurred: {error_msg}")
    
    def cancel_scan(self):
        """Cancel ongoing scan"""
        self.size_filter.cancel()
        self.scanning = False
        self.scan_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress_bar.stop()
        self.progress_label.config(text="Scan cancelled")
    
    def display_results(self):
        """Display scan results"""
        # Clear tree
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Sort by size (descending)
        sorted_files = sorted(self.matched_files, 
                            key=lambda x: x['size'], 
                            reverse=True)
        
        # Add files to tree
        for file_info in sorted_files:
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
            text=f"Total: {total_count} files ({total_str}) | "
                 f"Selected: {selected_count} files ({selected_str})"
        )
    
    def delete_selected(self):
        """Delete selected files"""
        selected_files = []
        for item in self.file_tree.get_children():
            if self.file_tree.item(item, 'text') == '☑':
                filepath = self.file_tree.item(item, 'values')[3]
                selected_files.append(filepath)
        
        if not selected_files:
            messagebox.showinfo("No Selection", "Please select files to delete")
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
            "Confirm Deletion",
            f"Move {len(selected_files)} file(s) ({size_str}) to Recycle Bin?"
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
                messages.append(f"✓ Successfully moved {success_count} file(s) to Recycle Bin")
            
            if skipped:
                messages.append(f"⚠ Skipped {len(skipped)} file(s) (already deleted or moved)")
            
            if failed:
                error_details = "\n".join([f"  • {os.path.basename(f)}: {e}" 
                                          for f, e in failed[:3]])
                if len(failed) > 3:
                    error_details += f"\n  • ... and {len(failed) - 3} more errors"
                messages.append(f"✗ Failed to delete {len(failed)} file(s):\n{error_details}")
            
            # Show appropriate message
            if failed and success_count == 0:
                messagebox.showerror("Deletion Failed", "\n\n".join(messages))
            elif failed or skipped:
                messagebox.showwarning("Partial Success", "\n\n".join(messages))
            else:
                messagebox.showinfo("Success", "\n\n".join(messages))
            
            # Remove deleted and skipped files from list and refresh display
            deleted_paths = set(selected_files) - {f for f, _ in failed}
            self.matched_files = [f for f in self.matched_files 
                                if f['path'] not in deleted_paths]
            self.display_results()
