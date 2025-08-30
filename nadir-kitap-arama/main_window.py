# -*- coding: utf-8 -*-
"""
Ana uygulama penceresi
"""

from PyQt6.QtWidgets import QMainWindow, QTabWidget
from PyQt6.QtCore import Qt

from database import DatabaseManager
from search_tab import BookSearchTab
from analysis_tab import BookAnalysisTab


class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.init_ui()
        self.apply_dark_theme()
        
    def init_ui(self):
        """Ana UI'yi başlat"""
        self.setWindowTitle("Nadir Kitap Arama & Analiz Uygulaması")
        self.setGeometry(100, 100, 1400, 900)
        
        # Tab widget oluştur
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Tab'ları oluştur
        self.search_tab = BookSearchTab(self.db_manager)
        self.analysis_tab = BookAnalysisTab(self.db_manager)
        
        # Tab'ları ekle
        self.tab_widget.addTab(self.search_tab, "🔍 Kitap Arama")
        self.tab_widget.addTab(self.analysis_tab, "📊 Kitap Analizi")
        
    def apply_dark_theme(self):
        """Koyu tema uygula"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            
            QTabWidget::pane {
                border: 1px solid #555;
                background-color: #2b2b2b;
            }
            
            QTabBar::tab {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
            
            QTabBar::tab:hover {
                background-color: #555;
            }
        """)
