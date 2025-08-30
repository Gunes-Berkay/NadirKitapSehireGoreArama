# -*- coding: utf-8 -*-
"""
Kitap analiz sekmesi
"""

import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
    QTextEdit, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class BookAnalysisTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        """Analiz sekmesi UI'sini oluştur"""
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("📊 Kitap Koleksiyonu Analizi")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Filtre paneli
        filter_panel = self.create_filter_panel()
        layout.addWidget(filter_panel)
        
        # Analiz butonları
        buttons_layout = QGridLayout()
        
        # Yazar analizi
        author_btn = QPushButton("👤 Yazar Analizi")
        author_btn.clicked.connect(self.show_author_analysis)
        buttons_layout.addWidget(author_btn, 0, 0)
        
        # Sahaf analizi
        sahaf_btn = QPushButton("🏪 Sahaf Analizi")
        sahaf_btn.clicked.connect(self.show_sahaf_analysis)
        buttons_layout.addWidget(sahaf_btn, 0, 1)
        
        # Fiyat analizi
        price_btn = QPushButton("💰 Fiyat Analizi")
        price_btn.clicked.connect(self.show_price_analysis)
        buttons_layout.addWidget(price_btn, 1, 0)
        
        # İstatistik özeti
        stats_btn = QPushButton("📈 Genel İstatistikler")
        stats_btn.clicked.connect(self.show_general_stats)
        buttons_layout.addWidget(stats_btn, 1, 1)
        
        # Kategori analizi (yeni)
        category_btn = QPushButton("📚 Kategori Analizi")
        category_btn.clicked.connect(self.show_category_analysis)
        buttons_layout.addWidget(category_btn, 2, 0)
        
        # Şehir analizi (yeni)
        city_btn = QPushButton("🌍 Şehir Analizi")
        city_btn.clicked.connect(self.show_city_analysis)
        buttons_layout.addWidget(city_btn, 2, 1)
        
        layout.addLayout(buttons_layout)
        
        # Sonuçlar alanı
        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        self.results_area.setFont(QFont("Consolas", 10))
        layout.addWidget(self.results_area)
        
        self.setLayout(layout)
    
    def create_filter_panel(self):
        """Analiz için filtre paneli oluştur"""
        panel = QGroupBox("🔍 Analiz Filtreleri")
        layout = QHBoxLayout()
        
        # Kategori filtresi
        category_layout = QVBoxLayout()
        category_layout.addWidget(QLabel("Kategori:"))
        self.category_filter = QComboBox()
        self.category_filter.addItem("Tüm Kategoriler", "")
        self.populate_categories()
        category_layout.addWidget(self.category_filter)
        
        # Alt kategori filtresi
        alt_category_layout = QVBoxLayout()
        alt_category_layout.addWidget(QLabel("Alt Kategori:"))
        self.alt_category_filter = QComboBox()
        self.alt_category_filter.addItem("Tüm Alt Kategoriler", "")
        self.populate_alt_categories()
        category_layout.addWidget(self.alt_category_filter)
        
        # Şehir filtresi
        city_layout = QVBoxLayout()
        city_layout.addWidget(QLabel("Şehir:"))
        self.city_filter = QComboBox()
        self.city_filter.addItem("Tüm Şehirler", "")
        self.populate_cities()
        city_layout.addWidget(self.city_filter)
        
        # Fiyat aralığı filtresi
        price_layout = QVBoxLayout()
        price_layout.addWidget(QLabel("Fiyat Aralığı:"))
        price_range_layout = QHBoxLayout()
        self.min_price_input = QLineEdit()
        self.min_price_input.setPlaceholderText("Min fiyat")
        self.min_price_input.setMaximumWidth(80)
        self.max_price_input = QLineEdit()
        self.max_price_input.setPlaceholderText("Max fiyat")
        self.max_price_input.setMaximumWidth(80)
        price_range_layout.addWidget(self.min_price_input)
        price_range_layout.addWidget(QLabel("-"))
        price_range_layout.addWidget(self.max_price_input)
        price_range_layout.addWidget(QLabel("₺"))
        price_layout.addLayout(price_range_layout)
        
        # Filtre temizleme butonu
        clear_btn = QPushButton("🔄 Filtreleri Temizle")
        clear_btn.clicked.connect(self.clear_filters)
        clear_btn.setMaximumWidth(150)
        
        # Layout'a ekle
        layout.addLayout(category_layout)
        layout.addLayout(alt_category_layout)
        layout.addLayout(city_layout)
        layout.addLayout(price_layout)
        layout.addWidget(clear_btn)
        
        panel.setLayout(layout)
        return panel
    
    def populate_categories(self):
        """Kategori dropdown'ını doldur"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT kategori FROM kitaplar WHERE kategori != "" AND kategori IS NOT NULL ORDER BY kategori')
            categories = cursor.fetchall()
            
            for category in categories:
                self.category_filter.addItem(category[0], category[0])
            
            conn.close()
        except Exception as e:
            print(f"Kategori yükleme hatası: {e}")
    
    def populate_alt_categories(self):
        """Alt kategori dropdown'ını doldur"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT alt_kategori FROM kitaplar WHERE alt_kategori != "" AND alt_kategori IS NOT NULL ORDER BY alt_kategori')
            alt_categories = cursor.fetchall()
            
            for alt_category in alt_categories:
                self.alt_category_filter.addItem(alt_category[0], alt_category[0])
            
            conn.close()
        except Exception as e:
            print(f"Alt kategori yükleme hatası: {e}")
    
    def populate_cities(self):
        """Şehir dropdown'ını doldur"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT sehir FROM kitaplar WHERE sehir != "" AND sehir IS NOT NULL ORDER BY sehir')
            cities = cursor.fetchall()
            
            for city in cities:
                self.city_filter.addItem(city[0], city[0])
            
            conn.close()
        except Exception as e:
            print(f"Şehir yükleme hatası: {e}")
    
    def clear_filters(self):
        """Tüm filtreleri temizle"""
        self.category_filter.setCurrentIndex(0)
        self.alt_category_filter.setCurrentIndex(0)
        self.city_filter.setCurrentIndex(0)
        self.min_price_input.clear()
        self.max_price_input.clear()
    
    def get_filter_conditions(self):
        """Aktif filtrelere göre SQL WHERE koşullarını oluştur"""
        conditions = []
        params = []
        
        # Kategori filtresi
        if self.category_filter.currentData():
            conditions.append("kategori = ?")
            params.append(self.category_filter.currentData())
        
        # Alt kategori filtresi
        if self.alt_category_filter.currentData():
            conditions.append("alt_kategori = ?")
            params.append(self.alt_category_filter.currentData())
        
        # Şehir filtresi
        if self.city_filter.currentData():
            conditions.append("sehir = ?")
            params.append(self.city_filter.currentData())
        
        # Fiyat aralığı filtresi
        try:
            if self.min_price_input.text().strip():
                min_price = float(self.min_price_input.text().strip())
                conditions.append("fiyat >= ?")
                params.append(min_price)
        except ValueError:
            pass
        
        try:
            if self.max_price_input.text().strip():
                max_price = float(self.max_price_input.text().strip())
                conditions.append("fiyat <= ?")
                params.append(max_price)
        except ValueError:
            pass
        
        return conditions, params
    
    def get_filter_info(self):
        """Aktif filtrelerin bilgisini döndür"""
        filter_parts = []
        
        if self.category_filter.currentData():
            filter_parts.append(f"Kategori: {self.category_filter.currentText()}")
        
        if self.alt_category_filter.currentData():
            filter_parts.append(f"Alt Kategori: {self.alt_category_filter.currentText()}")
        
        if self.city_filter.currentData():
            filter_parts.append(f"Şehir: {self.city_filter.currentText()}")
        
        price_range = []
        if self.min_price_input.text().strip():
            price_range.append(f"Min: {self.min_price_input.text()}₺")
        if self.max_price_input.text().strip():
            price_range.append(f"Max: {self.max_price_input.text()}₺")
        if price_range:
            filter_parts.append(f"Fiyat: {', '.join(price_range)}")
        
        return " | ".join(filter_parts) if filter_parts else None
    
    def show_author_analysis(self):
        """Yazar analizi göster (filtreli)"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            # Filtre koşullarını al
            conditions, params = self.get_filter_conditions()
            base_where = "yazar != '' AND yazar IS NOT NULL AND fiyat > 0"
            if conditions:
                where_clause = f"WHERE {base_where} AND " + " AND ".join(conditions)
            else:
                where_clause = f"WHERE {base_where}"
            
            # Filtre bilgisini göster
            filter_info = self.get_filter_info()
            
            # Toplam yazar sayısı
            cursor.execute(f'SELECT COUNT(DISTINCT yazar) FROM kitaplar {where_clause}', params)
            toplam_yazar = cursor.fetchone()[0]
            
            # En çok kitabı olan yazarlar
            cursor.execute(f'''
                SELECT yazar, COUNT(*) as kitap_sayisi, 
                       AVG(fiyat) as ortalama_fiyat,
                       MIN(fiyat) as min_fiyat,
                       MAX(fiyat) as max_fiyat,
                       COUNT(DISTINCT sahaf_name) as sahaf_sayisi
                FROM kitaplar 
                {where_clause}
                GROUP BY yazar 
                ORDER BY kitap_sayisi DESC 
                LIMIT 15
            ''', params)
            
            top_authors = cursor.fetchall()
            
            # En pahalı kitabı olan yazarlar
            cursor.execute(f'''
                SELECT yazar, baslik, fiyat, sahaf_name
                FROM kitaplar 
                {where_clause}
                ORDER BY fiyat DESC 
                LIMIT 10
            ''', params)
            
            expensive_books = cursor.fetchall()
            
            # Yazar başına ortalama fiyat analizi
            cursor.execute(f'''
                SELECT yazar, AVG(fiyat) as ort_fiyat, COUNT(*) as kitap_sayisi
                FROM kitaplar 
                {where_clause}
                GROUP BY yazar 
                HAVING COUNT(*) >= 3
                ORDER BY ort_fiyat DESC 
                LIMIT 10
            ''', params)
            
            avg_price_authors = cursor.fetchall()
            
            text = "👤 YAZAR ANALİZİ RAPORU\n"
            text += "=" * 90 + "\n\n"
            
            if filter_info:
                text += f"🔍 AKTİF FİLTRELER: {filter_info}\n\n"
            
            text += f"📊 Toplam Yazar Sayısı: {toplam_yazar}\n\n"
            
            text += "📚 EN ÇOK KİTABI OLAN YAZARLAR (Top 15)\n"
            text += "-" * 90 + "\n"
            text += f"{'Yazar':<25} {'Kitap':<6} {'Sahaf':<6} {'Ort.Fiyat':<10} {'Min':<8} {'Max':<8}\n"
            text += "-" * 90 + "\n"
            
            for row in top_authors:
                yazar, kitap_sayisi, ort_fiyat, min_fiyat, max_fiyat, sahaf_sayisi = row
                text += f"{yazar[:24]:<25} {kitap_sayisi:<6} {sahaf_sayisi:<6} "
                text += f"{ort_fiyat:.1f}₺{'':<4} {min_fiyat:.1f}₺{'':<3} {max_fiyat:.1f}₺\n"
            
            text += "\n💰 EN PAHALI KİTAPLAR (Top 10)\n"
            text += "-" * 90 + "\n"
            text += f"{'Yazar':<20} {'Kitap':<30} {'Fiyat':<10} {'Sahaf':<20}\n"
            text += "-" * 90 + "\n"
            
            for row in expensive_books:
                yazar, baslik, fiyat, sahaf = row
                text += f"{yazar[:19]:<20} {baslik[:29]:<30} {fiyat:.1f}₺{'':<5} {sahaf[:19]:<20}\n"
            
            text += "\n📈 EN YÜKSEK ORTALAMA FİYATLI YAZARLAR (3+ kitap)\n"
            text += "-" * 60 + "\n"
            text += f"{'Yazar':<30} {'Ortalama Fiyat':<15} {'Kitap Sayısı':<12}\n"
            text += "-" * 60 + "\n"
            
            for row in avg_price_authors:
                yazar, ort_fiyat, kitap_sayisi = row
                text += f"{yazar[:29]:<30} {ort_fiyat:.2f}₺{'':<9} {kitap_sayisi:<12}\n"
            
            conn.close()
            self.results_area.setText(text)
            
        except Exception as e:
            self.results_area.setText(f"Yazar analizi hatası: {str(e)}")
    
    def show_category_analysis(self):
        """Kategori analizi göster"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            # Filtre koşullarını al
            conditions, params = self.get_filter_conditions()
            base_where = "kategori != '' AND kategori IS NOT NULL"
            if conditions:
                where_clause = f"WHERE {base_where} AND " + " AND ".join(conditions)
            else:
                where_clause = f"WHERE {base_where}"
            
            filter_info = self.get_filter_info()
            
            # Kategori başına istatistikler
            cursor.execute(f'''
                SELECT kategori, COUNT(*) as kitap_sayisi,
                       COUNT(DISTINCT yazar) as yazar_sayisi,
                       COUNT(DISTINCT sahaf_name) as sahaf_sayisi,
                       AVG(fiyat) as ort_fiyat,
                       MIN(fiyat) as min_fiyat,
                       MAX(fiyat) as max_fiyat
                FROM kitaplar 
                {where_clause}
                GROUP BY kategori 
                ORDER BY kitap_sayisi DESC
                LIMIT 20
            ''', params)
            
            category_stats = cursor.fetchall()
            
            text = "📚 KATEGORİ ANALİZİ RAPORU\n"
            text += "=" * 95 + "\n\n"
            
            if filter_info:
                text += f"🔍 AKTİF FİLTRELER: {filter_info}\n\n"
            
            text += "📊 KATEGORİ İSTATİSTİKLERİ\n"
            text += "-" * 95 + "\n"
            text += f"{'Kategori':<25} {'Kitap':<6} {'Yazar':<6} {'Sahaf':<6} {'Ort.Fiyat':<10} {'Min-Max':<15}\n"
            text += "-" * 95 + "\n"
            
            for row in category_stats:
                kategori, kitap_sayisi, yazar_sayisi, sahaf_sayisi, ort_fiyat, min_fiyat, max_fiyat = row
                ort_fiyat_str = f"{ort_fiyat:.1f}₺" if ort_fiyat else "N/A"
                min_max_str = f"{min_fiyat:.0f}-{max_fiyat:.0f}₺" if min_fiyat and max_fiyat else "N/A"
                text += f"{kategori[:24]:<25} {kitap_sayisi:<6} {yazar_sayisi:<6} {sahaf_sayisi:<6} "
                text += f"{ort_fiyat_str:<10} {min_max_str:<15}\n"
            
            conn.close()
            self.results_area.setText(text)
            
        except Exception as e:
            self.results_area.setText(f"Kategori analizi hatası: {str(e)}")
    
    def show_city_analysis(self):
        """Şehir analizi göster"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            # Filtre koşullarını al
            conditions, params = self.get_filter_conditions()
            base_where = "sehir != '' AND sehir IS NOT NULL"
            if conditions:
                where_clause = f"WHERE {base_where} AND " + " AND ".join(conditions)
            else:
                where_clause = f"WHERE {base_where}"
            
            filter_info = self.get_filter_info()
            
            # Şehir başına istatistikler
            cursor.execute(f'''
                SELECT sehir, COUNT(*) as kitap_sayisi,
                       COUNT(DISTINCT sahaf_name) as sahaf_sayisi,
                       COUNT(DISTINCT yazar) as yazar_sayisi,
                       AVG(fiyat) as ort_fiyat,
                       COUNT(DISTINCT kategori) as kategori_sayisi
                FROM kitaplar 
                {where_clause}
                GROUP BY sehir 
                ORDER BY kitap_sayisi DESC
                LIMIT 15
            ''', params)
            
            city_stats = cursor.fetchall()
            
            text = "🌍 ŞEHİR ANALİZİ RAPORU\n"
            text += "=" * 90 + "\n\n"
            
            if filter_info:
                text += f"🔍 AKTİF FİLTRELER: {filter_info}\n\n"
            
            text += "📊 ŞEHİR İSTATİSTİKLERİ (Top 15)\n"
            text += "-" * 90 + "\n"
            text += f"{'Şehir':<20} {'Kitap':<6} {'Sahaf':<6} {'Yazar':<6} {'Kategori':<9} {'Ort.Fiyat':<10}\n"
            text += "-" * 90 + "\n"
            
            for row in city_stats:
                sehir, kitap_sayisi, sahaf_sayisi, yazar_sayisi, ort_fiyat, kategori_sayisi = row
                ort_fiyat_str = f"{ort_fiyat:.1f}₺" if ort_fiyat else "N/A"
                text += f"{sehir[:19]:<20} {kitap_sayisi:<6} {sahaf_sayisi:<6} {yazar_sayisi:<6} "
                text += f"{kategori_sayisi:<9} {ort_fiyat_str:<10}\n"
            
            conn.close()
            self.results_area.setText(text)
            
        except Exception as e:
            self.results_area.setText(f"Şehir analizi hatası: {str(e)}")
    
    def show_sahaf_analysis(self):
        """Sahaf analizi göster"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            # Toplam sahaf sayısı
            cursor.execute('SELECT COUNT(DISTINCT sahaf_name) FROM kitaplar WHERE sahaf_name != "" AND sahaf_name IS NOT NULL')
            toplam_sahaf = cursor.fetchone()[0]
            
            # En çok kitabı olan sahaflar
            cursor.execute('''
                SELECT sahaf_name, COUNT(*) as kitap_sayisi,
                       AVG(fiyat) as ortalama_fiyat,
                       COUNT(DISTINCT yazar) as yazar_sayisi,
                       MIN(fiyat) as min_fiyat,
                       MAX(fiyat) as max_fiyat,
                       sehir
                FROM kitaplar 
                WHERE sahaf_name != '' AND sahaf_name IS NOT NULL AND fiyat > 0
                GROUP BY sahaf_name 
                ORDER BY kitap_sayisi DESC 
                LIMIT 15
            ''')
            
            top_sahafs = cursor.fetchall()
            
            # En pahalı ortalamaya sahip sahaflar (5+ kitap)
            cursor.execute('''
                SELECT sahaf_name, AVG(fiyat) as ort_fiyat, COUNT(*) as kitap_sayisi, sehir
                FROM kitaplar 
                WHERE sahaf_name != '' AND sahaf_name IS NOT NULL AND fiyat > 0
                GROUP BY sahaf_name 
                HAVING COUNT(*) >= 5
                ORDER BY ort_fiyat DESC 
                LIMIT 10
            ''')
            
            expensive_sahafs = cursor.fetchall()
            
            # Şehir bazında sahaf dağılımı
            cursor.execute('''
                SELECT sehir, COUNT(DISTINCT sahaf_name) as sahaf_sayisi, 
                       COUNT(*) as toplam_kitap,
                       AVG(fiyat) as ort_fiyat
                FROM kitaplar 
                WHERE sehir != '' AND sehir IS NOT NULL AND sahaf_name != '' AND fiyat > 0
                GROUP BY sehir 
                ORDER BY sahaf_sayisi DESC 
                LIMIT 10
            ''')
            
            city_stats = cursor.fetchall()
            
            text = "🏪 SAHAF ANALİZİ RAPORU\n"
            text += "=" * 95 + "\n\n"
            text += f"📊 Toplam Sahaf Sayısı: {toplam_sahaf}\n\n"
            
            text += "📚 EN ÇOK KİTABI OLAN SAHAFLAR (Top 15)\n"
            text += "-" * 95 + "\n"
            text += f"{'Sahaf':<25} {'Kitap':<6} {'Yazar':<6} {'Şehir':<12} {'Ort.Fiyat':<10} {'Min-Max':<15}\n"
            text += "-" * 95 + "\n"
            
            for row in top_sahafs:
                sahaf, kitap_sayisi, ort_fiyat, yazar_sayisi, min_fiyat, max_fiyat, sehir = row
                sehir_str = sehir[:11] if sehir else "Bilinmiyor"
                text += f"{sahaf[:24]:<25} {kitap_sayisi:<6} {yazar_sayisi:<6} {sehir_str:<12} "
                text += f"{ort_fiyat:.1f}₺{'':<5} {min_fiyat:.0f}-{max_fiyat:.0f}₺\n"
            
            text += "\n💰 EN PAHALI ORTALAMALI SAHAFLAR (5+ kitap)\n"
            text += "-" * 70 + "\n"
            text += f"{'Sahaf':<30} {'Ortalama Fiyat':<15} {'Kitap':<6} {'Şehir':<12}\n"
            text += "-" * 70 + "\n"
            
            for row in expensive_sahafs:
                sahaf, ort_fiyat, kitap_sayisi, sehir = row
                sehir_str = sehir[:11] if sehir else "Bilinmiyor"
                text += f"{sahaf[:29]:<30} {ort_fiyat:.2f}₺{'':<9} {kitap_sayisi:<6} {sehir_str:<12}\n"
            
            text += "\n🌍 ŞEHİR BAZINDA SAHAF DAĞILIMI (Top 10)\n"
            text += "-" * 70 + "\n"
            text += f"{'Şehir':<15} {'Sahaf Sayısı':<12} {'Toplam Kitap':<12} {'Ort.Fiyat':<12}\n"
            text += "-" * 70 + "\n"
            
            for row in city_stats:
                sehir, sahaf_sayisi, toplam_kitap, ort_fiyat = row
                text += f"{sehir:<15} {sahaf_sayisi:<12} {toplam_kitap:<12} {ort_fiyat:.2f}₺\n"
            
            conn.close()
            self.results_area.setText(text)
            
        except Exception as e:
            self.results_area.setText(f"Hata: {str(e)}")
    
    def show_price_analysis(self):
        """Fiyat analizi göster"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            # Fiyat istatistikleri
            cursor.execute('''
                SELECT COUNT(*) as toplam_kitap,
                       AVG(fiyat) as ortalama_fiyat,
                       MIN(fiyat) as min_fiyat,
                       MAX(fiyat) as max_fiyat,
                       SUM(fiyat) as toplam_deger
                FROM kitaplar 
                WHERE fiyat > 0
            ''')
            
            stats = cursor.fetchone()
            
            # Fiyat aralıklarına göre dağılım
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN fiyat < 50 THEN '0-50₺'
                        WHEN fiyat < 100 THEN '50-100₺'
                        WHEN fiyat < 200 THEN '100-200₺'
                        WHEN fiyat < 500 THEN '200-500₺'
                        ELSE '500₺+'
                    END as fiyat_araligi,
                    COUNT(*) as kitap_sayisi,
                    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM kitaplar WHERE fiyat > 0), 1) as yuzde
                FROM kitaplar 
                WHERE fiyat > 0
                GROUP BY fiyat_araligi
                ORDER BY 
                    CASE fiyat_araligi
                        WHEN '0-50₺' THEN 1
                        WHEN '50-100₺' THEN 2
                        WHEN '100-200₺' THEN 3
                        WHEN '200-500₺' THEN 4
                        ELSE 5
                    END
            ''')
            
            distribution = cursor.fetchall()
            
            # En pahalı kitaplar
            cursor.execute('''
                SELECT baslik, yazar, sahaf_name, fiyat
                FROM kitaplar 
                WHERE fiyat > 0
                ORDER BY fiyat DESC 
                LIMIT 10
            ''')
            
            expensive_books = cursor.fetchall()
            
            # En ucuz kitaplar
            cursor.execute('''
                SELECT baslik, yazar, sahaf_name, fiyat
                FROM kitaplar 
                WHERE fiyat > 0
                ORDER BY fiyat ASC 
                LIMIT 10
            ''')
            
            cheap_books = cursor.fetchall()
            
            # Medyan hesapla
            cursor.execute('SELECT fiyat FROM kitaplar WHERE fiyat > 0 ORDER BY fiyat')
            all_prices = [row[0] for row in cursor.fetchall()]
            median_price = all_prices[len(all_prices)//2] if all_prices else 0
            
            text = "💰 FİYAT ANALİZİ RAPORU\n"
            text += "=" * 90 + "\n\n"
            
            if stats:
                toplam, ortalama, minimum, maksimum, toplam_deger = stats
                text += f"📊 GENEL İSTATİSTİKLER:\n"
                text += f"• Toplam Kitap: {toplam:,} adet\n"
                text += f"• Ortalama Fiyat: {ortalama:.2f}₺\n"
                text += f"• Medyan Fiyat: {median_price:.2f}₺\n"
                text += f"• En Düşük Fiyat: {minimum:.2f}₺\n"
                text += f"• En Yüksek Fiyat: {maksimum:,.2f}₺\n"
                text += f"• Toplam Koleksiyon Değeri: {toplam_deger:,.2f}₺\n\n"
            
            text += "📈 FİYAT DAĞILIMI:\n"
            text += "-" * 40 + "\n"
            text += f"{'Fiyat Aralığı':<15} {'Kitap Sayısı':<12} {'Yüzde':<8}\n"
            text += "-" * 40 + "\n"
            for aralık, sayı, yuzde in distribution:
                bar = "█" * int(yuzde // 3)  # Visual bar
                text += f"{aralık:<15} {sayı:>6} adet{'':<4} %{yuzde:<6} {bar}\n"
            
            text += "\n💎 EN PAHALI KİTAPLAR (Top 10):\n"
            text += "-" * 90 + "\n"
            text += f"{'Başlık':<35} {'Yazar':<20} {'Sahaf':<20} {'Fiyat':<10}\n"
            text += "-" * 90 + "\n"
            
            for book in expensive_books:
                baslik, yazar, sahaf, fiyat = book
                text += f"{baslik[:34]:<35} {(yazar or 'Bilinmiyor')[:19]:<20} "
                text += f"{(sahaf or 'Bilinmiyor')[:19]:<20} {fiyat:,.2f}₺\n"
            
            text += "\n💝 EN UCUZ KİTAPLAR (Top 10):\n"
            text += "-" * 90 + "\n"
            text += f"{'Başlık':<35} {'Yazar':<20} {'Sahaf':<20} {'Fiyat':<10}\n"
            text += "-" * 90 + "\n"
            
            for book in cheap_books:
                baslik, yazar, sahaf, fiyat = book
                text += f"{baslik[:34]:<35} {(yazar or 'Bilinmiyor')[:19]:<20} "
                text += f"{(sahaf or 'Bilinmiyor')[:19]:<20} {fiyat:.2f}₺\n"
            
            conn.close()
            self.results_area.setText(text)
            
        except Exception as e:
            self.results_area.setText(f"Fiyat analizi hatası: {str(e)}")
    
    def show_general_stats(self):
        """Genel istatistikleri göster"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            # Toplam istatistikler
            cursor.execute('SELECT COUNT(*) FROM kitaplar')
            total_books = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT yazar) FROM kitaplar WHERE yazar != "" AND yazar IS NOT NULL')
            total_authors = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT sahaf_name) FROM kitaplar WHERE sahaf_name != "" AND sahaf_name IS NOT NULL')
            total_sahafs = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT sehir) FROM kitaplar WHERE sehir != "" AND sehir IS NOT NULL')
            total_cities = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT kategori) FROM kitaplar WHERE kategori != "" AND kategori IS NOT NULL')
            total_categories = cursor.fetchone()[0]
            
            # Fiyat istatistikleri
            cursor.execute('SELECT AVG(fiyat), SUM(fiyat) FROM kitaplar WHERE fiyat > 0')
            avg_price, total_value = cursor.fetchone()
            
            # En çok kitabı olan yazar
            cursor.execute('''
                SELECT yazar, COUNT(*) as kitap_sayisi 
                FROM kitaplar 
                WHERE yazar != "" AND yazar IS NOT NULL
                GROUP BY yazar 
                ORDER BY kitap_sayisi DESC 
                LIMIT 1
            ''')
            top_author = cursor.fetchone()
            
            # En çok kitabı olan sahaf
            cursor.execute('''
                SELECT sahaf_name, COUNT(*) as kitap_sayisi 
                FROM kitaplar 
                WHERE sahaf_name != "" AND sahaf_name IS NOT NULL
                GROUP BY sahaf_name 
                ORDER BY kitap_sayisi DESC 
                LIMIT 1
            ''')
            top_sahaf = cursor.fetchone()
            
            # Son eklenen kitaplar
            cursor.execute('''
                SELECT baslik, yazar, sahaf_name, fiyat, tarih 
                FROM kitaplar 
                ORDER BY tarih DESC 
                LIMIT 10
            ''')
            recent_books = cursor.fetchall()
            
            # Kategori dağılımı
            cursor.execute('''
                SELECT kategori, COUNT(*) as kitap_sayisi
                FROM kitaplar 
                WHERE kategori != "" AND kategori IS NOT NULL
                GROUP BY kategori 
                ORDER BY kitap_sayisi DESC 
                LIMIT 10
            ''')
            category_stats = cursor.fetchall()
            
            # Şehir dağılımı
            cursor.execute('''
                SELECT sehir, COUNT(*) as kitap_sayisi, COUNT(DISTINCT sahaf_name) as sahaf_sayisi
                FROM kitaplar 
                WHERE sehir != "" AND sehir IS NOT NULL
                GROUP BY sehir 
                ORDER BY kitap_sayisi DESC 
                LIMIT 8
            ''')
            city_stats = cursor.fetchall()
            
            text = "📈 GENEL İSTATİSTİKLER RAPORU\n"
            text += "=" * 85 + "\n\n"
            
            text += "📊 TOPLAM SAYILAR:\n"
            text += f"• Kitap Sayısı: {total_books:,} adet\n"
            text += f"• Yazar Sayısı: {total_authors:,} kişi\n"
            text += f"• Sahaf Sayısı: {total_sahafs:,} işletme\n"
            text += f"• Şehir Sayısı: {total_cities:,} lokasyon\n"
            text += f"• Kategori Sayısı: {total_categories:,} tür\n\n"
            
            text += "💰 FİNANSAL ÖZET:\n"
            if avg_price and total_value:
                text += f"• Ortalama Kitap Fiyatı: {avg_price:.2f}₺\n"
                text += f"• Toplam Koleksiyon Değeri: {total_value:,.2f}₺\n\n"
            
            text += "🏆 REKORLAR:\n"
            if top_author:
                text += f"• En Çok Kitabı Olan Yazar: {top_author[0]} ({top_author[1]} kitap)\n"
            if top_sahaf:
                text += f"• En Çok Kitabı Olan Sahaf: {top_sahaf[0]} ({top_sahaf[1]} kitap)\n\n"
            
            text += "📚 KATEGORİ DAĞILIMI (Top 10):\n"
            text += "-" * 50 + "\n"
            text += f"{'Kategori':<30} {'Kitap Sayısı':<15}\n"
            text += "-" * 50 + "\n"
            for kategori, sayı in category_stats:
                text += f"{kategori[:29]:<30} {sayı:<15}\n"
            
            text += "\n🌍 ŞEHİR DAĞILIMI (Top 8):\n"
            text += "-" * 55 + "\n"
            text += f"{'Şehir':<20} {'Kitap':<10} {'Sahaf':<10}\n"
            text += "-" * 55 + "\n"
            for sehir, kitap_sayisi, sahaf_sayisi in city_stats:
                text += f"{sehir:<20} {kitap_sayisi:<10} {sahaf_sayisi:<10}\n"
            
            text += "\n🕒 SON EKLENEN KİTAPLAR (Top 10):\n"
            text += "-" * 85 + "\n"
            text += f"{'Başlık':<30} {'Yazar':<20} {'Sahaf':<15} {'Fiyat':<10}\n"
            text += "-" * 85 + "\n"
            
            for book in recent_books:
                baslik, yazar, sahaf, fiyat, tarih = book
                yazar_str = yazar[:19] if yazar else "Bilinmiyor"
                sahaf_str = sahaf[:14] if sahaf else "Bilinmiyor"
                fiyat_str = f"{fiyat:.0f}₺" if fiyat else "Belirtilmemiş"
                text += f"{baslik[:29]:<30} {yazar_str:<20} {sahaf_str:<15} {fiyat_str:<10}\n"
            
            conn.close()
            self.results_area.setText(text)
            
        except Exception as e:
            self.results_area.setText(f"Genel istatistik hatası: {str(e)}")
