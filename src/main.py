# src/main.py
import sys
import os

# Thêm đường dẫn để import từ thư mục gốc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gui.main_window_v2 import run_gui

if __name__ == "__main__":
    run_gui()