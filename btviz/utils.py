# utils.py
from PyQt5.QtWidgets import QApplication


def calculate_window(scale_width=0.5, scale_height=0.5):
    screen = QApplication.primaryScreen().geometry()
    screen_width, screen_height = screen.width(), screen.height()
    window_width, window_height = int(screen_width * scale_width), int(screen_height * scale_height)
    x_pos, y_pos = (screen_width - window_width) // 2, (screen_height - window_height) // 2
    return window_width, window_height, x_pos, y_pos
