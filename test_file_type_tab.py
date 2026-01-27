# Test script to check if GUI loads correctly
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Force reload modules
if 'gui.file_type_filter_tab' in sys.modules:
    del sys.modules['gui.file_type_filter_tab']
if 'core.file_type_filter' in sys.modules:
    del sys.modules['core.file_type_filter']

import tkinter as tk
from tkinter import ttk
from gui.file_type_filter_tab import FileTypeFilterTab

# Create test window
root = tk.Tk()
root.title("Test File Type Tab")
root.geometry("1200x700")

# Create tab
tab = FileTypeFilterTab(root)
tab.pack(fill=tk.BOTH, expand=True)

print("FileTypeFilterTab created successfully")
print("Checking for action buttons...")

# Check if action buttons exist
def check_widgets(widget, level=0):
    """Recursively check widgets"""
    indent = "  " * level
    widget_type = widget.__class__.__name__
    
    if isinstance(widget, ttk.Button):
        text = widget.cget('text')
        print(f"{indent}Button: {text}")
    elif isinstance(widget, ttk.Label):
        text = widget.cget('text')
        if 'Tổng' in text or 'file' in text:
            print(f"{indent}Label: {text}")
    
    # Check children
    for child in widget.winfo_children():
        check_widgets(child, level + 1)

check_widgets(tab)

root.mainloop()
