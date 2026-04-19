"""
BookShelf - Kişisel Okuma Takip Uygulaması
Run: python main.py
"""
import os
import customtkinter as ctk # Eğer zaten varsa bunu tekrar ekleme
import sys

# Ensure working directory is the project root
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Make sure assets directory exists
os.makedirs("assets/covers", exist_ok=True)

from app import App

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
