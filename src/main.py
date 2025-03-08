# src/main.py
import sys
import os



# Thêm đường dẫn để import từ thư mục gốc
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.gui.main_window import run_gui

if __name__ == "__main__":
    run_gui()