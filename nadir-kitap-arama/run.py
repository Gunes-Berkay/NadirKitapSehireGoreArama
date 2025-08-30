#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nadir Kitap Arama & Analiz Uygulaması
Modül içi çalıştırma dosyası
"""

import sys
import os

# Mevcut dizini sys.path'e ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from PyQt6.QtWidgets import QApplication
from main_window import MainApplication


def main():
    """Uygulamayı başlat"""
    app = QApplication(sys.argv)
    
    # Uygulama ikonunu ayarla (varsa)
    app.setApplicationName("Nadir Kitap Arama")
    app.setApplicationVersion("2.0")
    
    window = MainApplication()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
