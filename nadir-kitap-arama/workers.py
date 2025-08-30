# -*- coding: utf-8 -*-
"""
Thread worker'lar
"""

import json
import re
import urllib.parse
import time
import concurrent.futures
import cloudscraper
from bs4 import BeautifulSoup
from PyQt6.QtCore import QThread, pyqtSignal

from utils import turkish_to_english_chars


class BookSearchWorker(QThread):
    progress_updated = pyqtSignal(str)
    results_ready = pyqtSignal(list)
    book_found = pyqtSignal(dict)  # Her kitap bulunduğunda emit edilir
    
    def __init__(self, search_params, db_manager=None, auto_save=False):
        super().__init__()
        self.search_params = search_params
        self.db_manager = db_manager
        self.auto_save = auto_save
        self._stop_requested = False
        
        # Sahaflar listesini yükle
        self.sahaflar = []
        try:
            with open('sahaflar.json', 'r', encoding='utf-8') as f:
                self.sahaflar = json.load(f)
        except Exception as e:
            print(f"Sahaflar dosyası yüklenemedi: {e}")
            self.sahaflar = []
        
    def stop_search(self):
        """Arama işlemini durdur"""
        self._stop_requested = True
        self.progress_updated.emit("Arama durduruluyor...")
    
    def get_sahaf_info(self, sahaf_name):
        """Sahaf adından sahaf bilgilerini al"""
        for sahaf in self.sahaflar:
            if sahaf.get('name') == sahaf_name:
                return sahaf
        return None
        
    def run(self):
        try:
            self.progress_updated.emit("Arama başlatılıyor...")
            
            if self._stop_requested:
                self.progress_updated.emit("Arama durduruldu.")
                self.results_ready.emit([])
                return
            
            # Şehir seçilmişse o şehirdeki sahaflar için arama yap
            selected_city = self.search_params.get('selected_city')
            if selected_city and selected_city != "Tüm Şehirler":
                all_books = self.search_by_city_threaded()
            else:
                all_books = self.search_general()
            
            if self._stop_requested:
                self.progress_updated.emit("Arama durduruldu.")
                self.results_ready.emit([])
                return
            
            # Sonuçları yayınla
            self.results_ready.emit(all_books)
            
            # Otomatik kaydetme aktifse ve şehir bazlı arama değilse (çünkü zaten kaydedildi)
            if self.auto_save and self.db_manager and all_books and not selected_city:
                self.progress_updated.emit(f"Veritabanına {len(all_books)} kitap kaydediliyor...")
                
                # RAM dostu parçalı kaydetme
                batch_size = 50
                for i in range(0, len(all_books), batch_size):
                    batch = all_books[i:i + batch_size]
                    self.db_manager.save_books_async(batch)
                    
                    # Progress güncelle
                    progress = min(100, int((i + batch_size) / len(all_books) * 100))
                    self.progress_updated.emit(f"Veritabanına kaydediliyor... %{progress}")
                    
                    # RAM'i rahatlatmak için kısa bekle
                    time.sleep(0.05)
                
                self.progress_updated.emit(f"Kaydetme tamamlandı. {len(all_books)} kitap veritabanına eklendi.")
            
        except Exception as e:
            self.progress_updated.emit(f"Hata: {str(e)}")
            self.results_ready.emit([])
        finally:
            self.finished.emit()
    
    def search_by_city_threaded(self):
        """Şehirdeki sahafları threaded olarak ara"""
        selected_city = self.search_params['selected_city']
        self.progress_updated.emit(f"{selected_city} şehrindeki sahaflar aranıyor...")
        
        # Sahaflar dosyasını yükle
        try:
            with open('sahaflar.json', 'r', encoding='utf-8') as f:
                sahaflar = json.load(f)
        except FileNotFoundError:
            self.progress_updated.emit("Sahaflar dosyası bulunamadı!")
            return []
        
        # Seçilen şehirdeki sahafları bul
        city_sahaflar = [sahaf for sahaf in sahaflar if sahaf['city'] == selected_city]
        
        if not city_sahaflar:
            self.progress_updated.emit(f"{selected_city} şehrinde sahaf bulunamadı!")
            return []
        
        self.progress_updated.emit(f"{selected_city} şehrinde {len(city_sahaflar)} sahaf bulundu.")
        
        # Maksimum thread sayısı (CPU sayısına göre)
        max_workers = min(8, len(city_sahaflar))  # Maksimum 8 thread
        all_books = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Her sahaf için arama task'ları oluştur
            future_to_sahaf = {}
            
            for i, sahaf in enumerate(city_sahaflar):
                # Sahaf ID'sini URL'den çıkar
                sahaf_url = sahaf['seller_url']
                match = re.search(r'sahaf(\d+)\.html', sahaf_url)
                if not match:
                    continue
                    
                sahaf_id = match.group(1)
                
                # Thread'e sahaf arama görevini ver
                future = executor.submit(self.search_for_sahaf, sahaf_id, sahaf['name'])
                future_to_sahaf[future] = (i+1, sahaf['name'])
            
            # Sonuçları topla
            completed = 0
            for future in concurrent.futures.as_completed(future_to_sahaf):
                if self._stop_requested:
                    self.progress_updated.emit("Arama durduruldu.")
                    # Bekleyen task'ları iptal et
                    for f in future_to_sahaf:
                        f.cancel()
                    return all_books
                
                completed += 1
                sahaf_index, sahaf_name = future_to_sahaf[future]
                
                try:
                    sahaf_books = future.result()
                    all_books.extend(sahaf_books)
                    
                    self.progress_updated.emit(
                        f"Sahaf {completed}/{len(city_sahaflar)}: {sahaf_name} - "
                        f"{len(sahaf_books)} kitap bulundu (Toplam: {len(all_books)})"
                    )
                    
                    # Otomatik kaydetme aktifse kitapları toplu kaydet
                    if self.auto_save and self.db_manager and sahaf_books:
                        # RAM'i korumak için küçük batch'lerde kaydet
                        if len(sahaf_books) > 100:
                            # Büyük grupları parçala
                            for i in range(0, len(sahaf_books), 50):
                                batch = sahaf_books[i:i + 50]
                                self.db_manager.save_books_async(batch)
                                time.sleep(0.01)  # CPU'ya biraz nefes ver
                        else:
                            self.db_manager.save_books_async(sahaf_books)
                        
                        # Her 5 sahafta bir bellek temizliği
                        if completed % 5 == 0:
                            self.db_manager.cleanup_memory()
                            
                except Exception as e:
                    self.progress_updated.emit(f"Sahaf {sahaf_name} hatası: {str(e)}")
        
        self.progress_updated.emit(f"Tüm sahaflar tarandı. Toplam {len(all_books)} kitap bulundu.")
        return all_books
    
    def search_for_sahaf(self, sahaf_id, sahaf_name):
        """Belirli bir sahaf için arama yap"""
        # Arama parametrelerini al ve Türkçe karakterleri dönüştür
        kitap_adi_raw = self.search_params['kitap_adi']
        yazar_raw = self.search_params['yazar']
        
        # Türkçe karakterleri İngilizce'ye çevir
        kitap_adi_converted = turkish_to_english_chars(kitap_adi_raw)
        yazar_converted = turkish_to_english_chars(yazar_raw)
        
        # URL encode et
        kitap_adi = urllib.parse.quote(kitap_adi_converted) if kitap_adi_converted else ''
        yazar = urllib.parse.quote(yazar_converted) if yazar_converted else ''
        kategori2 = self.search_params.get('kategori2', '')
        kategori = self.search_params.get('kategori', '')
        siralama = self.search_params.get('siralama', 'fiyatartan.')
        
        scraper = cloudscraper.create_scraper()
        sahaf_books = []
        page = 1
        max_pages = 100  # Sahaf bazında daha düşük limit
        
        while page <= max_pages:
            if self._stop_requested:
                break
                
            url = f"https://www.nadirkitap.com/kitapara.php?ara=aramayap&ref=&kategori2={kategori2}&kitap_Adi={kitap_adi}&yazar={yazar}&ceviren=&hazirlayan=&siralama={siralama}&satici={sahaf_id}&ortakkargo=0&yayin_Evi=&yayin_Yeri=&isbn=&fiyat1=&fiyat2=&tarih1=0&tarih2=0&guzelciltli=0&birincibaski=0&imzali=0&eskiyeni=0&cilt=0&listele=&tip=&dil=0&kategori={kategori}&page={page}"
            
            try:
                response = scraper.get(url, timeout=10)
                if response.status_code != 200:
                    break
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Kitap konteynerini bul
                books_container = soup.find("div", class_="list-cell")
                if not books_container:
                    break
                
                product_list = books_container.find("ul", class_="product-list")
                if not product_list:
                    break
                    
                li_elements = product_list.find_all("li")
                if not li_elements:
                    break
                
                page_books = []
                for li in li_elements:
                    book_data = self.extract_book_data(li)
                    if book_data:
                        # Sahaf adını güncelle (parametre olarak gelen ismi kullan)
                        book_data['sahaf_name'] = sahaf_name
                        # Sahaf URL'i extract_book_data'dan geliyorsa kullan, yoksa sahaflar.json'dan al
                        if not book_data.get('sahaf_url'):
                            sahaf_info = self.get_sahaf_info(sahaf_name)
                            book_data['sahaf_url'] = sahaf_info.get('seller_url', '') if sahaf_info else ''
                        
                        # Kategori bilgilerini ekle
                        book_data['kategori'] = self.search_params.get('kategori_adi', '')
                        book_data['alt_kategori'] = self.search_params.get('alt_kategori_adi', '')
                        book_data['sehir'] = self.search_params.get('secili_sehir', '')
                        
                        page_books.append(book_data)
                
                if not page_books:
                    break
                    
                sahaf_books.extend(page_books)
                page += 1
                
            except Exception as e:
                self.progress_updated.emit(f"Sahaf {sahaf_name} için hata: {str(e)}")
                break
        
        return sahaf_books
    
    def search_general(self):
        """Genel arama yap (şehir seçilmemişse)"""
        # Arama parametrelerini al ve Türkçe karakterleri dönüştür
        kitap_adi_raw = self.search_params['kitap_adi']
        yazar_raw = self.search_params['yazar']
        
        # Türkçe karakterleri İngilizce'ye çevir
        kitap_adi_converted = turkish_to_english_chars(kitap_adi_raw)
        yazar_converted = turkish_to_english_chars(yazar_raw)
        
        # URL encode et
        kitap_adi = urllib.parse.quote(kitap_adi_converted) if kitap_adi_converted else ''
        yazar = urllib.parse.quote(yazar_converted) if yazar_converted else ''
        kategori2 = self.search_params.get('kategori2', '')
        kategori = self.search_params.get('kategori', '')
        siralama = self.search_params.get('siralama', 'fiyatartan.')
        
        # Debug bilgisi göster
        if kitap_adi_raw != kitap_adi_converted:
            self.progress_updated.emit(f"Kitap adı dönüştürüldü: '{kitap_adi_raw}' → '{kitap_adi_converted}'")
        if yazar_raw != yazar_converted:
            self.progress_updated.emit(f"Yazar adı dönüştürüldü: '{yazar_raw}' → '{yazar_converted}'")
        
        scraper = cloudscraper.create_scraper()
        all_books = []
        page = 1
        max_pages = 1000  # Maksimum sayfa limiti
        
        while page <= max_pages:
            if self._stop_requested:
                self.progress_updated.emit("Arama durduruldu.")
                break
                
            url = f"https://www.nadirkitap.com/kitapara.php?ara=aramayap&ref=&kategori2={kategori2}&kitap_Adi={kitap_adi}&yazar={yazar}&ceviren=&hazirlayan=&siralama={siralama}&satici=0&ortakkargo=0&yayin_Evi=&yayin_Yeri=&isbn=&fiyat1=&fiyat2=&tarih1=0&tarih2=0&guzelciltli=0&birincibaski=0&imzali=0&eskiyeni=0&cilt=0&listele=&tip=&dil=0&kategori={kategori}&page={page}"
            
            self.progress_updated.emit(f"Sayfa {page} çekiliyor...")
            
            try:
                response = scraper.get(url, timeout=10)
                if response.status_code != 200:
                    break
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Kitap konteynerini bul
                books_container = soup.find("div", class_="list-cell")
                if not books_container:
                    break
                
                product_list = books_container.find("ul", class_="product-list")
                if not product_list:
                    break
                    
                li_elements = product_list.find_all("li")
                if not li_elements:
                    break
                
                page_books = []
                for li in li_elements:
                    book_data = self.extract_book_data(li)
                    if book_data:
                        # Kategori bilgilerini ekle
                        book_data['kategori'] = self.search_params.get('kategori_adi', '')
                        book_data['alt_kategori'] = self.search_params.get('alt_kategori_adi', '')
                        book_data['sehir'] = ''  # Genel aramada şehir bilgisi yok
                        
                        page_books.append(book_data)
                
                if not page_books:
                    break
                    
                all_books.extend(page_books)
                self.progress_updated.emit(f"Sayfa {page} tamamlandı - {len(page_books)} kitap bulundu (Toplam: {len(all_books)})")
                
                # Eğer bu sayfada 25'den az kitap varsa sonraki sayfa yok demektir
                if len(page_books) < 25:
                    break
                
                page += 1
                
                # Rate limiting
                self.msleep(200)
                
            except Exception as e:
                self.progress_updated.emit(f"Sayfa {page} için hata: {str(e)}")
                break
        
        return all_books
    
    def extract_book_data(self, li):
        """Bir li elementinden kitap verilerini çıkarır"""
        try:
            # Kitap başlığı
            title_tag = li.find("h4", class_="break-work")
            if not title_tag:
                return None
                
            title_link = title_tag.find("a")
            if not title_link:
                return None
                
            title = title_link.find("span").text.strip() if title_link.find("span") else title_link.text.strip()
            book_url = title_link.get("href", "")
            
            # Yazar - h4'ten sonra gelen p tag'ından al
            author = ""
            # H4'ün parent div'ini bul
            title_parent = title_tag.parent
            if title_parent:
                # H4'ten sonra gelen p tag'ını bul
                p_tag = title_parent.find("p")
                if p_tag:
                    author = p_tag.text.strip()
            
            # Fiyat - product-list-price sınıfındaki div'den al
            price_text = ""
            price_numeric = 0
            price_div = li.find("div", class_="product-list-price")
            if price_div:
                price_text = price_div.text.strip()
                try:
                    # Fiyattan sadece sayıları çıkar (96,00 TL -> 96.00)
                    price_clean = re.sub(r'[^\d,.]', '', price_text.replace(',', '.'))
                    if price_clean:
                        price_numeric = float(price_clean)
                except ValueError:
                    price_numeric = 0
            
            # Açıklama - Yayınevi bilgisini al
            description = ""
            yayin_li = None
            ul_elements = li.find_all("ul", class_="product-list-bottom")
            for ul in ul_elements:
                li_elements = ul.find_all("li")
                for li_item in li_elements:
                    if "Yayınevi" in li_item.text:
                        yayin_li = li_item
                        break
                if yayin_li:
                    break
            
            if yayin_li:
                yayin_span = yayin_li.find("span", class_="col-md-9")
                if yayin_span:
                    description = yayin_span.text.strip().lstrip(": ").strip()
            
            # Sahaf bilgilerini çıkar - seller-link sınıfındaki a tag'ından al
            sahaf_name = ""
            sahaf_url = ""
            seller_link = li.find("a", class_="seller-link")
            if seller_link:
                sahaf_name = seller_link.text.strip()
                sahaf_url = seller_link.get("href", "")
                if sahaf_url and not sahaf_url.startswith("http"):
                    sahaf_url = f"https://www.nadirkitap.com{sahaf_url}"
            
            return {
                "kitap_adi": title,
                "yazar": author,
                "fiyat": price_text,
                "fiyat_numeric": price_numeric,
                "site_url": book_url,
                "aciklama": description,
                "sahaf_adi": sahaf_name,
                "sahaf_url": sahaf_url
            }
            
        except Exception as e:
            return None
