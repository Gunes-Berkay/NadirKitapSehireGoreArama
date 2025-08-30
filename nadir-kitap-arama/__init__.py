# -*- coding: utf-8 -*-
"""
Nadir Kitap Arama & Analiz Uygulaması - GUI Modülleri
"""

__version__ = "2.0"
__author__ = "Nadir Kitap Arama Uygulaması"
__description__ = "PyQt6 tabanlı modüler kitap arama ve analiz uygulaması"

# Ana modüllerden temel sınıfları import et
from main_window import MainApplication
from database import DatabaseManager
from search_tab import BookSearchTab
from analysis_tab import BookAnalysisTab
from workers import BookSearchWorker
from widgets import ClickableLabel
from utils import turkish_to_english_chars

__all__ = [
    'MainApplication',
    'DatabaseManager', 
    'BookSearchTab',
    'BookAnalysisTab',
    'BookSearchWorker',
    'ClickableLabel',
    'turkish_to_english_chars'
]

# Kolayca çalıştırabilmek için main fonksiyonu
def run_app():
    """Uygulamayı çalıştır"""
    from run import main
    main()
