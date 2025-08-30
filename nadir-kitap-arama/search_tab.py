# -*- coding: utf-8 -*-
"""
Kitap arama sekmesi
"""

import json
import webbrowser
import locale
import logging
import traceback
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
    QScrollArea, QFrame, QProgressBar, QGroupBox, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from workers import BookSearchWorker
from widgets import ClickableLabel

# Loglama ayarları
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kitap_arama.log', encoding='utf-8'),
        logging.StreamHandler()  # Konsola da yazdır
    ]
)
logger = logging.getLogger(__name__)


class BookSearchTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.kategoriler = []
        self.sahaflar = []
        self.cities = []
        self.search_worker = None
        self.current_results = []
        
        self.init_data()
        self.init_ui()
        
    def init_data(self):
        """Veri dosyalarını yükle"""
        try:
            with open("kategoriler.json", "r", encoding="utf-8") as f:
                self.kategoriler = json.load(f)
            
            with open("sahaflar.json", "r", encoding="utf-8") as f:
                self.sahaflar = json.load(f)
                
            # Şehirleri çıkar ve Türkçe sıralama ile sırala
            unique_cities = list(set([sahaf.get('city', '') for sahaf in self.sahaflar if sahaf.get('city')]))
            # Türkçe karakterleri dikkate alarak sıralama
            try:
                locale.setlocale(locale.LC_COLLATE, 'Turkish_Turkey.1254')
                self.cities = sorted(unique_cities, key=locale.strxfrm)
            except:
                # Locale ayarlanamadıysa manuel Türkçe sıralama
                turkish_sort_key = lambda s: s.replace('ç','c1').replace('ğ','g1').replace('ı','i1').replace('ö','o1').replace('ş','s1').replace('ü','u1').replace('Ç','C1').replace('Ğ','G1').replace('İ','I1').replace('Ö','O1').replace('Ş','S1').replace('Ü','U1')
                self.cities = sorted(unique_cities, key=turkish_sort_key)
                
        except Exception as e:
            print(f"Veri yükleme hatası: {e}")
    
    def init_ui(self):
        """Arama sekmesi UI'sini oluştur"""
        layout = QHBoxLayout()
        
        # Sol panel - Arama kriterleri
        search_panel = self.create_search_panel()
        layout.addWidget(search_panel, 1)
        
        # Sağ panel - Sonuçlar
        results_panel = self.create_results_panel()
        layout.addWidget(results_panel, 2)
        
        self.setLayout(layout)
        
    def create_search_panel(self):
        """Arama panelini oluştur"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setMinimumWidth(350)
        panel.setMaximumWidth(400)
        
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("Kitap Arama")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Yazar girişi
        yazar_group = QGroupBox("Yazar")
        yazar_layout = QVBoxLayout()
        self.yazar_input = QLineEdit()
        self.yazar_input.setPlaceholderText("Yazar adını girin...")
        yazar_layout.addWidget(self.yazar_input)
        yazar_group.setLayout(yazar_layout)
        layout.addWidget(yazar_group)
        
        # Kitap adı girişi
        kitap_group = QGroupBox("Kitap Adı")
        kitap_layout = QVBoxLayout()
        self.kitap_input = QLineEdit()
        self.kitap_input.setPlaceholderText("Kitap adını girin...")
        kitap_layout.addWidget(self.kitap_input)
        kitap_group.setLayout(kitap_layout)
        layout.addWidget(kitap_group)
        
        # Ana kategori seçimi
        ana_kategori_group = QGroupBox("Ana Kategori")
        ana_kategori_layout = QVBoxLayout()
        self.ana_kategori_combo = QComboBox()
        self.ana_kategori_combo.addItem("Tümü", "0")
        for kategori in self.kategoriler:
            self.ana_kategori_combo.addItem(kategori['ana_kategori_adi'], kategori['ana_kategori_id'])
        self.ana_kategori_combo.currentTextChanged.connect(self.on_ana_kategori_changed)
        ana_kategori_layout.addWidget(self.ana_kategori_combo)
        ana_kategori_group.setLayout(ana_kategori_layout)
        layout.addWidget(ana_kategori_group)
        
        # Alt kategori seçimi
        alt_kategori_group = QGroupBox("Alt Kategori")
        alt_kategori_layout = QVBoxLayout()
        self.alt_kategori_combo = QComboBox()
        self.alt_kategori_combo.addItem("Tümü", "0")
        alt_kategori_layout.addWidget(self.alt_kategori_combo)
        alt_kategori_group.setLayout(alt_kategori_layout)
        layout.addWidget(alt_kategori_group)
        
        # Şehir seçimi
        sehir_group = QGroupBox("Şehir")
        sehir_layout = QVBoxLayout()
        
        # Şehir arama kutusu
        self.sehir_search = QLineEdit()
        self.sehir_search.setPlaceholderText("Şehir ara...")
        self.sehir_search.textChanged.connect(self.filter_cities)
        sehir_layout.addWidget(self.sehir_search)
        
        # Şehir combo kutusu
        self.sehir_combo = QComboBox()
        self.sehir_combo.setEditable(False)
        self.populate_cities()
        sehir_layout.addWidget(self.sehir_combo)
        
        sehir_group.setLayout(sehir_layout)
        layout.addWidget(sehir_group)
        
        # Arama yöntemi seçimi
        arama_yontemi_group = QGroupBox("Arama Yöntemi")
        arama_yontemi_layout = QVBoxLayout()
        self.arama_yontemi_combo = QComboBox()
        self.arama_yontemi_combo.addItem("🌐 Canlı Arama (Websitelerinden)", "canli")
        self.arama_yontemi_combo.addItem("💾 Yerel Arama (Veritabanından)", "yerel")
        self.arama_yontemi_combo.setToolTip("Canlı Arama: Websitelerinden güncel veri çeker (yavaş)\nYerel Arama: Mevcut veritabanından arar (hızlı)")
        self.arama_yontemi_combo.currentTextChanged.connect(self.on_arama_yontemi_changed)
        arama_yontemi_layout.addWidget(self.arama_yontemi_combo)
        arama_yontemi_group.setLayout(arama_yontemi_layout)
        layout.addWidget(arama_yontemi_group)
        
        # Sıralama seçimi
        siralama_group = QGroupBox("Sıralama")
        siralama_layout = QVBoxLayout()
        self.siralama_combo = QComboBox()
        self.siralama_combo.addItem("Fiyat Artan", "fiyatartan.")
        self.siralama_combo.addItem("Fiyat Azalan", "fiyatazalan.")
        self.siralama_combo.addItem("Tarih Yeni", "tarihyeni.")
        self.siralama_combo.addItem("Tarih Eski", "tariheski.")
        siralama_layout.addWidget(self.siralama_combo)
        siralama_group.setLayout(siralama_layout)
        layout.addWidget(siralama_group)
        
        # Arama butonları
        buttons_layout = QHBoxLayout()
        
        self.search_button = QPushButton("🔍 ARA")
        self.search_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.search_button.setMinimumHeight(50)
        self.search_button.clicked.connect(self.search_books)
        buttons_layout.addWidget(self.search_button)
        
        self.stop_button = QPushButton("⏹️ DURDUR")
        self.stop_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.stop_button.setMinimumHeight(50)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_search)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:disabled {
                background-color: #666;
                color: #999;
            }
        """)
        buttons_layout.addWidget(self.stop_button)
        
        layout.addLayout(buttons_layout)
        
        # Kaydetme butonu
        self.save_button = QPushButton("💾 SONUÇLARI KAYDET")
        self.save_button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.save_button.setMinimumHeight(40)
        self.save_button.clicked.connect(self.save_results)
        self.save_button.setEnabled(False)
        layout.addWidget(self.save_button)
        
        # Otomatik kaydetme seçeneği
        auto_save_group = QGroupBox("Kaydetme Seçenekleri")
        auto_save_layout = QVBoxLayout()
        
        self.auto_save_checkbox = QCheckBox("🔄 Otomatik Kaydet")
        self.auto_save_checkbox.setToolTip("Kitaplar bulundukça otomatik olarak veritabanına kaydedilir")
        auto_save_layout.addWidget(self.auto_save_checkbox)
        
        self.queue_status_label = QLabel("Kuyruk: 0 kayıt bekliyor")
        self.queue_status_label.setFont(QFont("Arial", 9))
        self.queue_status_label.setStyleSheet("color: #888;")
        auto_save_layout.addWidget(self.queue_status_label)
        
        auto_save_group.setLayout(auto_save_layout)
        layout.addWidget(auto_save_group)
        
        # Kuyruk durumunu güncelleme timer'ı
        self.queue_timer = QTimer()
        self.queue_timer.timeout.connect(self.update_queue_status)
        self.queue_timer.start(2000)  # Her 2 saniyede güncelle (RAM tasarrufu)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Aramaya hazır...")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        panel.setLayout(layout)
        
        return panel
    
    def populate_cities(self):
        """Şehirleri combo kutusuna ekle"""
        self.sehir_combo.clear()
        self.sehir_combo.addItem("Tüm Şehirler", "")
        for city in self.cities:
            self.sehir_combo.addItem(city, city)
    
    def filter_cities(self):
        """Şehirleri arama kriterine göre filtrele"""
        search_text = self.sehir_search.text().lower()
        self.sehir_combo.clear()
        self.sehir_combo.addItem("Tüm Şehirler", "")
        
        for city in self.cities:
            if search_text in city.lower():
                self.sehir_combo.addItem(city, city)
    
    def on_ana_kategori_changed(self):
        """Ana kategori değiştiğinde alt kategorileri güncelle"""
        self.alt_kategori_combo.clear()
        self.alt_kategori_combo.addItem("Tümü", "0")
        
        selected_data = self.ana_kategori_combo.currentData()
        if selected_data and selected_data != "0":
            # Seçilen ana kategorinin alt kategorilerini bul
            for kategori in self.kategoriler:
                if kategori['ana_kategori_id'] == selected_data:
                    for alt_kategori in kategori.get('alt_kategoriler', []):
                        if alt_kategori.get('kategori_adi') and alt_kategori.get('kategori_id'):
                            self.alt_kategori_combo.addItem(
                                alt_kategori['kategori_adi'], 
                                alt_kategori['kategori_id']
                            )
                    break
    
    def on_arama_yontemi_changed(self):
        """Arama yöntemi değiştiğinde UI'yi güncelle"""
        arama_yontemi = self.arama_yontemi_combo.currentData()
        
        # Kategori seçimleri her iki arama yönteminde de etkin olsun
        self.ana_kategori_combo.setEnabled(True)
        self.alt_kategori_combo.setEnabled(True)
        
        # Arama butonunun metnini güncelle
        if arama_yontemi == "yerel":
            self.search_button.setText("🔍 YEREL ARAMA")
            self.search_button.setToolTip("Mevcut veritabanından hızlı arama yapar")
        else:
            self.search_button.setText("🔍 CANLI ARAMA")
            self.search_button.setToolTip("Websitelerinden güncel veri çekerek arama yapar")
    
    def search_books(self):
        """Kitap arama işlemini başlat"""
        # Arama yöntemi kontrolü
        arama_yontemi = self.arama_yontemi_combo.currentData()
        
        if arama_yontemi == "yerel":
            self.search_local_database()
        else:
            self.search_online()
    
    def search_local_database(self):
        """Yerel veritabanından arama yap"""
        logger.info("Yerel veritabanı araması başlatılıyor...")
        
        # Arama parametrelerini topla
        yazar = self.yazar_input.text().strip()
        kitap_adi = self.kitap_input.text().strip()
        secili_sehir = self.sehir_combo.currentText() if self.sehir_combo.currentData() else ""
        ana_kategori_adi = self.ana_kategori_combo.currentText() if self.ana_kategori_combo.currentData() != "0" else ""
        alt_kategori_adi = self.alt_kategori_combo.currentText() if self.alt_kategori_combo.currentData() != "0" else ""
        
        logger.debug(f"Arama parametreleri - Yazar: {yazar}, Kitap: {kitap_adi}, Şehir: {secili_sehir}, Ana Kategori: {ana_kategori_adi}, Alt Kategori: {alt_kategori_adi}")
        
        # En az bir arama kriteri girilmiş olmalı
        if not yazar and not kitap_adi and not ana_kategori_adi and not alt_kategori_adi:
            logger.warning("Hiç arama kriteri girilmedi")
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir arama kriteri girin!")
            return
        
        # UI'yi güncelle
        self.search_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.clear_results()
        
        try:
            # Veritabanından arama yap
            self.update_status("Veritabanından aranıyor...")
            self.progress_bar.setValue(20)
            logger.info("Veritabanı sorgusu hazırlanıyor...")
            
            # Önce toplam sayıyı al (sayfalama için)
            count_query = "SELECT COUNT(*) FROM kitaplar WHERE 1=1"
            query = "SELECT * FROM kitaplar WHERE 1=1"
            params = []
            
            if yazar:
                filter_clause = " AND yazar LIKE ?"
                query += filter_clause
                count_query += filter_clause
                params.append(f"%{yazar}%")
                logger.debug(f"Yazar filtresi eklendi: {yazar}")
            
            if kitap_adi:
                filter_clause = " AND baslik LIKE ?"
                query += filter_clause
                count_query += filter_clause
                params.append(f"%{kitap_adi}%")
                logger.debug(f"Kitap adı filtresi eklendi: {kitap_adi}")
            
            # Kategori filtrelemesi
            if alt_kategori_adi:
                filter_clause = " AND alt_kategori LIKE ?"
                query += filter_clause
                count_query += filter_clause
                params.append(f"%{alt_kategori_adi}%")
                logger.debug(f"Alt kategori filtresi eklendi: {alt_kategori_adi}")
            elif ana_kategori_adi:
                filter_clause = " AND kategori LIKE ?"
                query += filter_clause
                count_query += filter_clause
                params.append(f"%{ana_kategori_adi}%")
                logger.debug(f"Ana kategori filtresi eklendi: {ana_kategori_adi}")
            
            if secili_sehir and secili_sehir != "Tüm Şehirler":
                filter_clause = " AND sehir = ?"
                query += filter_clause
                count_query += filter_clause
                params.append(secili_sehir)
                logger.debug(f"Şehir filtresi eklendi: {secili_sehir}")
            
            # Sıralama ekle
            siralama = self.siralama_combo.currentData()
            if siralama == "fiyatartan.":
                query += " ORDER BY CAST(fiyat AS REAL) ASC"
            elif siralama == "fiyatazalan.":
                query += " ORDER BY CAST(fiyat AS REAL) DESC"
            elif siralama == "tarihyeni.":
                query += " ORDER BY tarih DESC"
            elif siralama == "tariheski.":
                query += " ORDER BY tarih ASC"
            
            # Sayfalama ekle - maksimum 1000 sonuç
            query += " LIMIT 1000"
            
            logger.debug(f"Count sorgu: {count_query}")
            logger.debug(f"Final sorgu: {query}")
            logger.debug(f"Parametreler: {params}")
            
            self.progress_bar.setValue(40)
            
            # Önce toplam sayıyı al
            total_count = self.db_manager.execute_query(count_query, params)
            total_results = total_count[0][0] if total_count and len(total_count) > 0 else 0
            logger.info(f"Toplam {total_results} sonuç mevcut")
            
            self.progress_bar.setValue(60)
            
            # Ana sorguyu çalıştır
            logger.info("Veritabanı sorgusu çalıştırılıyor...")
            results = self.db_manager.execute_query(query, params)
            logger.info(f"Sorgu tamamlandı. {len(results)} sonuç alındı.")
            self.progress_bar.setValue(80)
            
            # Sonuçları formatla - DOĞRU MAPPING
            logger.info("Sonuçlar formatlanıyor...")
            formatted_results = []
            for i, row in enumerate(results):
                try:
                    # DOĞRU VERITABANI MAPPING:
                    # 0: id, 1: unique_id, 2: baslik, 3: yazar, 4: sahaf_name, 
                    # 5: sahaf_url, 6: fiyat, 7: fiyat_text, 8: kitap_url, 
                    # 9: aciklama, 10: kategori, 11: alt_kategori, 12: sehir, 13: tarih
                    formatted_results.append({
                        'yazar': row[3] if len(row) > 3 and row[3] else 'Bilinmeyen Yazar',
                        'kitap_adi': (row[2].strip() if len(row) > 2 and row[2] and str(row[2]).strip() else 'Bilinmeyen Başlık'),
                        'fiyat': row[7] if len(row) > 7 and row[7] else 'Fiyat Belirtilmemiş',  # Görüntüleme için metin formatı
                        'fiyat_numeric': row[6] if len(row) > 6 and row[6] else 0,  # Sıralama için sayısal değer
                        'site_url': row[8] if len(row) > 8 and row[8] else '',
                        'sahaf_adi': row[4] if len(row) > 4 and row[4] else 'Bilinmeyen Sahaf',
                        'sehir': row[12] if len(row) > 12 and row[12] else 'Bilinmeyen Şehir',
                        'tarih': row[13] if len(row) > 13 and row[13] else '',
                        'kategori': f"{row[10]} / {row[11]}" if len(row) > 11 and row[10] and row[11] else (row[10] if len(row) > 10 and row[10] else 'Kategori Belirtilmemiş'),
                        'aciklama': row[9] if len(row) > 9 and row[9] else ''
                    })
                except Exception as format_error:
                    logger.error(f"Satır {i} formatlanırken hata: {format_error}")
                    logger.debug(f"Problematik satır: {row}")
            
            logger.info(f"{len(formatted_results)} sonuç başarıyla formatlandı")
            self.progress_bar.setValue(100)
            self.current_results = formatted_results
            
            # Sonuçları göster
            self.display_results(formatted_results)
            
            # Sayfalama bilgisi ile status güncelle
            if total_results > 1000:
                status_msg = f"✅ {len(formatted_results)} sonuç gösteriliyor (Toplam: {total_results} - İlk 1000 sonuç)"
            else:
                status_msg = f"✅ {len(formatted_results)} sonuç bulundu (Yerel Arama)"
            
            self.update_status(status_msg)
            logger.info(f"Yerel arama tamamlandı. {len(formatted_results)} sonuç gösteriliyor.")
            
        except Exception as e:
            error_msg = f"Veritabanı arama hatası: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Hata detayı: {traceback.format_exc()}")
            QMessageBox.critical(self, "Hata", error_msg)
            self.update_status("❌ Arama hatası!")
            
        finally:
            # UI'yi sıfırla
            logger.debug("UI sıfırlanıyor...")
            self.search_button.setEnabled(True)
            self.progress_bar.setVisible(False)
            if self.current_results:
                self.save_button.setEnabled(True)
    
    def search_online(self):
        """Websitelerinden canlı arama yap"""
        if self.search_worker and self.search_worker.isRunning():
            return
        
        # Arama parametrelerini topla
        ana_kategori_id = self.ana_kategori_combo.currentData()
        alt_kategori_id = self.alt_kategori_combo.currentData()
        
        # Kategori adlarını al
        ana_kategori_adi = self.ana_kategori_combo.currentText() if ana_kategori_id != "0" else ""
        alt_kategori_adi = self.alt_kategori_combo.currentText() if alt_kategori_id != "0" else ""
        secili_sehir = self.sehir_combo.currentText() if self.sehir_combo.currentData() else ""
        
        search_params = {
            'yazar': self.yazar_input.text().strip(),
            'kitap_adi': self.kitap_input.text().strip(),
            'kategori2': ana_kategori_id if ana_kategori_id != "0" else "",
            'kategori': alt_kategori_id if alt_kategori_id != "0" else "",
            'kategori_adi': ana_kategori_adi,
            'alt_kategori_adi': alt_kategori_adi,
            'selected_city': self.sehir_combo.currentData(),
            'secili_sehir': secili_sehir,
            'siralama': self.siralama_combo.currentData()
        }
        
        # UI'yi güncelle
        self.search_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.save_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.clear_results()
        
        # Worker thread başlat (otomatik kaydetme seçeneği ile)
        auto_save = self.auto_save_checkbox.isChecked()
        self.search_worker = BookSearchWorker(
            search_params, 
            self.db_manager if auto_save else None, 
            auto_save
        )
        self.search_worker.progress_updated.connect(self.update_status)
        self.search_worker.results_ready.connect(self.display_results)
        self.search_worker.finished.connect(self.search_finished)
        self.search_worker.start()
    
    def stop_search(self):
        """Arama işlemini durdur"""
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.stop_search()
            self.update_status("Arama durduruluyor...")
            self.stop_button.setEnabled(False)
    
    def update_queue_status(self):
        """Kaydetme kuyruğu durumunu güncelle"""
        if hasattr(self.db_manager, 'get_queue_size'):
            queue_size = self.db_manager.get_queue_size()
            self.queue_status_label.setText(f"Kuyruk: {queue_size} kayıt bekliyor")
            
            if queue_size > 0:
                self.queue_status_label.setStyleSheet("color: #4CAF50;")
            else:
                self.queue_status_label.setStyleSheet("color: #888;")
    
    def save_results(self):
        """Mevcut sonuçları veritabanına kaydet"""
        if not self.current_results:
            QMessageBox.warning(self, "Uyarı", "Kaydedilecek sonuç bulunamadı!")
            return
        
        try:
            saved_count = self.db_manager.save_books(self.current_results)
            total_count = len(self.current_results)
            duplicate_count = total_count - saved_count
            
            message = f"Toplam {total_count} kitaptan {saved_count} tanesi kaydedildi."
            if duplicate_count > 0:
                message += f"\n{duplicate_count} kitap zaten kayıtlıydı."
            
            QMessageBox.information(self, "Başarılı", message)
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kaydetme sırasında hata oluştu:\n{str(e)}")
    
    def update_status(self, message):
        """Status labelını güncelle"""
        self.status_label.setText(message)
    
    def search_finished(self):
        """Arama tamamlandığında UI'yi güncelle"""
        self.search_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        if self.current_results:
            self.save_button.setEnabled(True)
        
        # Arama durumu kontrol et
        if hasattr(self.search_worker, '_stop_requested') and self.search_worker._stop_requested:
            result_count = len(self.current_results) if self.current_results else 0
            self.update_status(f"Arama durduruldu. {result_count} kitap bulundu.")
        else:
            result_count = len(self.current_results) if self.current_results else 0
            self.update_status(f"Arama tamamlandı. {result_count} kitap bulundu.")
    
    def create_results_panel(self):
        """Sonuçlar panelini oluştur"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        
        layout = QVBoxLayout()
        
        # Başlık ve sıralama
        header_layout = QHBoxLayout()
        
        self.results_title = QLabel("Arama Sonuçları")
        self.results_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(self.results_title)
        
        header_layout.addStretch()
        
        # Fiyat sıralama butonu
        self.sort_button = QPushButton("📊 Fiyat Sırala")
        self.sort_button.clicked.connect(self.toggle_price_sort)
        self.sort_ascending = True
        header_layout.addWidget(self.sort_button)
        
        layout.addLayout(header_layout)
        
        # Scroll area için widget
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        
        layout.addWidget(self.scroll_area)
        panel.setLayout(layout)
        
        return panel
    
    def toggle_price_sort(self):
        """Fiyat sıralamasını değiştir"""
        if not self.current_results:
            return
            
        self.sort_ascending = not self.sort_ascending
        self.sort_button.setText("📈 Fiyat Artan" if self.sort_ascending else "📉 Fiyat Azalan")
        
        def extract_numeric_price(book):
            """Fiyat text'inden sayısal değeri çıkar"""
            try:
                # Önce fiyat_text'i kontrol et (gerçek fiyat burada)
                fiyat_text = book.get('fiyat', '')
                
                if not fiyat_text or fiyat_text == 'Fiyat Belirtilmemiş':
                    return 0
                
                # Debug için fiyatı logla
                logger.debug(f"Fiyat text parsing: '{fiyat_text}'")
                
                # "11.784,23 TL" formatından sayısal değeri çıkar
                # Önce TL, Euro vs. para birimlerini kaldır
                clean_price = re.sub(r'\s*[A-Za-z₺€$£]+\s*', '', str(fiyat_text)).strip()
                
                # Sadece rakam, virgül ve nokta al
                numeric_str = re.sub(r'[^\d,.]', '', clean_price)
                
                if not numeric_str:
                    return 0
                
                # Türkçe format: "11.784,23" → "11784.23"
                if ',' in numeric_str and '.' in numeric_str:
                    # "11.784,23" formatı için
                    # Son virgülü ondalık ayırıcı olarak kabul et, noktaları binlik ayırıcı
                    parts = numeric_str.split(',')
                    if len(parts) >= 2:
                        integer_part = ''.join(parts[:-1]).replace('.', '')  # Noktaları kaldır
                        decimal_part = parts[-1]
                        numeric_str = f"{integer_part}.{decimal_part}"
                elif ',' in numeric_str and '.' not in numeric_str:
                    # "60,00" → "60.00"
                    numeric_str = numeric_str.replace(',', '.')
                elif '.' in numeric_str and ',' not in numeric_str:
                    # Zaten doğru format veya binlik ayırıcı
                    # Eğer 3'ten fazla haneli ve nokta varsa binlik ayırıcı olabilir
                    if len(numeric_str.replace('.', '')) > 3 and '.' in numeric_str:
                        # "1.500" gibi → "1500"
                        parts = numeric_str.split('.')
                        if len(parts) == 2 and len(parts[1]) == 3:
                            # Muhtemelen binlik ayırıcı
                            numeric_str = numeric_str.replace('.', '')
                
                # Sonuç
                if numeric_str:
                    result = float(numeric_str)
                    logger.debug(f"Parsed price text: '{fiyat_text}' → {result}")
                    return result
                return 0
                
            except Exception as e:
                logger.error(f"Fiyat text parsing hatası: '{book.get('fiyat', 'N/A')}' - {e}")
                return 0
        
        # Sonuçları sırala
        try:
            sorted_results = sorted(self.current_results, 
                                  key=extract_numeric_price, 
                                  reverse=not self.sort_ascending)
            
            # Sonuçları yeniden göster
            self.display_results(sorted_results)
            logger.info(f"Sonuçlar fiyata göre sıralandı ({'Artan' if self.sort_ascending else 'Azalan'})")
            
        except Exception as e:
            logger.error(f"Fiyat sıralama hatası: {e}")
            QMessageBox.warning(self, "Uyarı", "Fiyat sıralaması yapılırken hata oluştu!")
    
    def display_results(self, books):
        """Arama sonuçlarını chunked processing ile göster (UI donmasını engeller)"""
        self.current_results = books
        self.clear_results()
        
        if not books:
            no_results = QLabel("Sonuç bulunamadı.")
            no_results.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_results.setFont(QFont("Arial", 12))
            self.scroll_layout.addWidget(no_results)
            return
        
        self.results_title.setText(f"Arama Sonuçları ({len(books)} kitap)")
        
        # Büyük listeleri chunked processing ile göster
        if len(books) > 100:
            self.display_books_chunked(books)
        else:
            # Küçük listeleri direkt göster
            for book in books:
                book_widget = self.create_book_widget(book)
                self.scroll_layout.addWidget(book_widget)
            self.scroll_layout.addStretch()
    
    def display_books_chunked(self, books):
        """Kitapları parça parça göster (UI thread'ini bloklamaz)"""
        self.book_display_queue = books.copy()
        self.books_displayed = 0
        
        # İlk batch'i hemen göster
        self.process_next_book_chunk()
        
        # Timer ile kalan batch'leri işle
        self.display_timer = QTimer()
        self.display_timer.timeout.connect(self.process_next_book_chunk)
        self.display_timer.start(10)  # Her 10ms'de bir chunk işle
    
    def process_next_book_chunk(self):
        """Sonraki kitap chunk'ını işle"""
        if not hasattr(self, 'book_display_queue') or not self.book_display_queue:
            # Tüm kitaplar gösterildi
            if hasattr(self, 'display_timer'):
                self.display_timer.stop()
            self.scroll_layout.addStretch()
            self.update_status(f"Toplam {self.books_displayed} kitap gösteriliyor.")
            return
        
        # 20'şer kitap chunk'ları halinde işle
        chunk_size = 20
        current_chunk = self.book_display_queue[:chunk_size]
        self.book_display_queue = self.book_display_queue[chunk_size:]
        
        # Chunk'ı ekle
        for book in current_chunk:
            try:
                book_widget = self.create_book_widget(book)
                self.scroll_layout.addWidget(book_widget)
                self.books_displayed += 1
            except Exception as e:
                print(f"Kitap widget oluşturma hatası: {e}")
                continue
        
        # Progress göster
        if len(self.current_results) > 200:
            progress = int((self.books_displayed / len(self.current_results)) * 100)
            self.update_status(f"Sonuçlar yükleniyor... %{progress} ({self.books_displayed}/{len(self.current_results)})")
        
        # QApplication'a nefes al fırsatı ver
        QApplication.processEvents()
    
    def create_book_widget(self, book):
        """Tek kitap için widget oluştur"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.Box)
        widget.setStyleSheet("""
            QFrame {
                border: 1px solid #555;
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
                background-color: #3c3c3c;
            }
            QFrame:hover {
                background-color: #4a4a4a;
                border-color: #4CAF50;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Başlık (tıklanabilir)
        title_label = ClickableLabel(book.get('kitap_adi', 'Bilinmeyen Başlık'))
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.clicked.connect(lambda: webbrowser.open(book.get('site_url', '')))
        layout.addWidget(title_label)
        
        # Yazar
        if book.get('yazar'):
            author_label = QLabel(f"Yazar: {book['yazar']}")
            author_label.setFont(QFont("Arial", 10))
            layout.addWidget(author_label)
        
        # Sahaf adı (eğer varsa)
        if book.get('sahaf_adi'):
            sahaf_label = QLabel(f"Sahaf: {book['sahaf_adi']}")
            sahaf_label.setFont(QFont("Arial", 10))
            sahaf_label.setStyleSheet("color: #FFB74D;")
            layout.addWidget(sahaf_label)
        
        # Fiyat
        if book.get('fiyat'):
            price_label = QLabel(f"Fiyat: {book['fiyat']}")
            price_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            price_label.setStyleSheet("color: #4CAF50;")
            layout.addWidget(price_label)
        
        # Şehir
        if book.get('sehir'):
            city_label = QLabel(f"Şehir: {book['sehir']}")
            city_label.setFont(QFont("Arial", 9))
            city_label.setStyleSheet("color: #81C784;")
            layout.addWidget(city_label)
        
        # Kategori
        if book.get('kategori'):
            category_label = QLabel(f"Kategori: {book['kategori']}")
            category_label.setFont(QFont("Arial", 9))
            category_label.setStyleSheet("color: #64B5F6;")
            layout.addWidget(category_label)
        
        # Açıklama (kısaltılmış)
        if book.get('aciklama'):
            desc = book['aciklama']
            if len(desc) > 150:
                desc = desc[:150] + "..."
            desc_label = QLabel(desc)
            desc_label.setFont(QFont("Arial", 9))
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #cccccc;")
            layout.addWidget(desc_label)
        
        widget.setLayout(layout)
        return widget
    
    def clear_results(self):
        """Sonuçları temizle - büyük veri setleri için optimize edilmiş"""
        widget_count = self.scroll_layout.count()
        
        # Az widget varsa direkt temizle
        if widget_count <= 50:
            while self.scroll_layout.count():
                child = self.scroll_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            # Çok widget varsa parça parça temizle
            widgets_to_delete = []
            while self.scroll_layout.count():
                child = self.scroll_layout.takeAt(0)
                if child.widget():
                    widgets_to_delete.append(child.widget())
            
            # Parça parça sil
            for i in range(0, len(widgets_to_delete), 20):
                chunk = widgets_to_delete[i:i+20]
                for widget in chunk:
                    widget.deleteLater()
                QApplication.processEvents()  # UI thread'i bloke etme
