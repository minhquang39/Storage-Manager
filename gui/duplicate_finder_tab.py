"""
GUI tab for duplicate file finder
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from datetime import datetime
from send2trash import send2trash
import os

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
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all widgets for this tab"""
        
        # Top section - Directory selection
        top_frame = ttk.LabelFrame(self, text="Select Folders to Scan", padding=10)
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
        
        # Scan options
        options_frame = ttk.Frame(top_frame)
        options_frame.pack(fill=tk.X)
        
        ttk.Label(options_frame, text="Min File Size:").pack(side=tk.LEFT, padx=5)
        self.min_size_var = tk.StringVar(value="0")
        ttk.Entry(options_frame, textvariable=self.min_size_var, 
                 width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(options_frame, text="KB").pack(side=tk.LEFT)
        
        # Scan button
        self.scan_btn = ttk.Button(top_frame, text="Start Scan", 
                                   command=self.start_scan)
        self.scan_btn.pack(pady=5)
        
        self.cancel_btn = ttk.Button(top_frame, text="Cancel Scan", 
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
        results_frame = ttk.LabelFrame(self, text="Duplicate Files", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Navigation
        nav_frame = ttk.Frame(results_frame)
        nav_frame.pack(fill=tk.X)
        
        self.prev_btn = ttk.Button(nav_frame, text="← Previous Group", 
                                   command=self.prev_group, state=tk.DISABLED)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.group_label = ttk.Label(nav_frame, text="No duplicates found")
        self.group_label.pack(side=tk.LEFT, padx=10)
        
        self.next_btn = ttk.Button(nav_frame, text="Next Group →", 
                                   command=self.next_group, state=tk.DISABLED)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        # File list with checkboxes
        list_frame = ttk.Frame(results_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_tree = ttk.Treeview(list_frame, columns=('Size', 'Modified', 'Path'),
                                     show='tree headings', yscrollcommand=scrollbar.set)
        self.file_tree.heading('#0', text='Select')
        self.file_tree.heading('Size', text='Size')
        self.file_tree.heading('Modified', text='Modified')
        self.file_tree.heading('Path', text='Path')
        
        self.file_tree.column('#0', width=60)
        self.file_tree.column('Size', width=100)
        self.file_tree.column('Modified', width=150)
        self.file_tree.column('Path', width=400)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_tree.yview)
        
        # Action buttons
        action_frame = ttk.Frame(results_frame)
        action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(action_frame, text="Select All", 
                  command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Deselect All", 
                  command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Auto-Select (Keep Newest)", 
                  command=lambda: self.auto_select('newest')).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Delete Selected", 
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
            "Scan All Drives",
            f"This will scan all available drives:\n{drive_list}\n\n"
            f"System folders (Windows, Program Files, etc.) will be automatically excluded.\n\n"
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
        """Start scanning for duplicates"""
        if not self.selected_directories:
            messagebox.showwarning("No Folders", "Please select folders to scan")
            return
        
        try:
            min_size_kb = float(self.min_size_var.get())
            min_size_bytes = int(min_size_kb * 1024)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for minimum size")
            return
        
        self.scanning = True
        self.scan_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.progress_bar.start()
        self.duplicate_groups.clear()
        
        # Run scan in separate thread
        thread = threading.Thread(
            target=self.run_scan,
            args=(min_size_bytes,),
            daemon=True
        )
        thread.start()
    
    def run_scan(self, min_size):
        """Run the scan in background thread"""
        try:
            self.duplicate_groups = self.duplicate_finder.find_duplicates(
                self.selected_directories,
                min_size=min_size
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
        
        if self.duplicate_groups:
            self.current_group_index = 0
            self.display_current_group()
            total_size = sum(
                sum(f['size'] for f in files[1:])  # Size of duplicates (excluding one to keep)
                for files in self.duplicate_groups.values()
            )
            size_str = SizeFilter.format_size(total_size)
            self.progress_label.config(
                text=f"Found {len(self.duplicate_groups)} duplicate groups. "
                     f"Potential space to free: {size_str}"
            )
        else:
            self.progress_label.config(text="No duplicates found")
            self.group_label.config(text="No duplicates found")
    
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
        self.duplicate_finder.cancel()
        self.scanning = False
        self.scan_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress_bar.stop()
        self.progress_label.config(text="Scan cancelled")
    
    def display_current_group(self):
        """Display current duplicate group"""
        if not self.duplicate_groups:
            return
        
        # Clear tree
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Get current group
        group_hashes = list(self.duplicate_groups.keys())
        if self.current_group_index >= len(group_hashes):
            self.current_group_index = 0
        
        current_hash = group_hashes[self.current_group_index]
        files = self.duplicate_groups[current_hash]
        
        # Update navigation
        self.group_label.config(
            text=f"Group {self.current_group_index + 1} of {len(self.duplicate_groups)} "
                 f"({len(files)} duplicates)"
        )
        
        self.prev_btn.config(state=tk.NORMAL if self.current_group_index > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.current_group_index < len(group_hashes) - 1 else tk.DISABLED)
        
        # Add files to tree
        for file_info in files:
            size_str = SizeFilter.format_size(file_info['size'])
            modified_str = datetime.fromtimestamp(file_info['modified']).strftime('%Y-%m-%d %H:%M:%S')
            
            self.file_tree.insert('', tk.END, 
                                 text='☐',
                                 values=(size_str, modified_str, file_info['path']),
                                 tags=('unchecked',))
    
    def prev_group(self):
        """Show previous duplicate group"""
        if self.current_group_index > 0:
            self.current_group_index -= 1
            self.display_current_group()
    
    def next_group(self):
        """Show next duplicate group"""
        if self.current_group_index < len(self.duplicate_groups) - 1:
            self.current_group_index += 1
            self.display_current_group()
    
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
        """Auto-select files based on strategy"""
        if not self.duplicate_groups:
            return
        
        # Get current group
        group_hashes = list(self.duplicate_groups.keys())
        current_hash = group_hashes[self.current_group_index]
        files = self.duplicate_groups[current_hash]
        
        # Determine which to keep
        if strategy == 'newest':
            files_sorted = sorted(files, key=lambda x: x.get('modified', 0), reverse=True)
        elif strategy == 'oldest':
            files_sorted = sorted(files, key=lambda x: x.get('modified', 0))
        else:
            files_sorted = files
        
        keep_file = files_sorted[0]['path']
        
        # Update checkboxes
        for item in self.file_tree.get_children():
            filepath = self.file_tree.item(item, 'values')[2]
            if filepath != keep_file:
                self.file_tree.item(item, text='☑', tags=('checked',))
            else:
                self.file_tree.item(item, text='☐', tags=('unchecked',))
    
    def delete_selected(self):
        """Delete selected files"""
        selected_files = []
        for item in self.file_tree.get_children():
            if self.file_tree.item(item, 'text') == '☑':
                filepath = self.file_tree.item(item, 'values')[2]
                selected_files.append(filepath)
        
        if not selected_files:
            messagebox.showinfo("No Selection", "Please select files to delete")
            return
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Deletion",
            f"Move {len(selected_files)} file(s) to Recycle Bin?"
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
            
            # Refresh display
            self.display_current_group()
