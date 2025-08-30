# -*- coding: utf-8 -*-
"""
Veritabanı yönetimi
"""

import sqlite3
import hashlib
import threading
import time
import gc
from queue import Queue


class DatabaseManager:
    def __init__(self, db_path="kitaplar.db"):
        self.db_path = db_path
        self.lock = threading.Lock()  # Thread safety için
        self.save_queue = Queue(maxsize=1000)  # Queue boyutunu sınırla
        self.batch_size = 50  # Batch boyutunu küçült
        self.init_database()
        self.start_save_worker()
    
    def init_database(self):
        """Veritabanını oluştur ve tabloları hazırla"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kitaplar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unique_id TEXT UNIQUE,
                baslik TEXT,
                yazar TEXT,
                sahaf_name TEXT,
                sahaf_url TEXT,
                fiyat REAL,
                fiyat_text TEXT,
                kitap_url TEXT,
                aciklama TEXT,
                kategori TEXT,
                alt_kategori TEXT,
                sehir TEXT,
                tarih DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_save_worker(self):
        """Veritabanı kaydetme thread'ini başlat"""
        def worker():
            while True:
                try:
                    item = self.save_queue.get(timeout=1)
                    if item is None:  # Poison pill
                        break
                    
                    if isinstance(item, tuple) and item[0] == 'batch':
                        # Toplu kaydetme
                        _, books_list = item
                        self.save_books(books_list)
                    else:
                        # Tekil kaydetme
                        self._save_book_direct(item)
                    
                    self.save_queue.task_done()
                except:
                    continue
        
        self.save_thread = threading.Thread(target=worker, daemon=True)
        self.save_thread.start()
    
    def generate_unique_id(self, book_data):
        """Kitap için unique ID oluştur"""
        # Başlık, yazar ve sahaf adının birleşiminden hash oluştur
        content = f"{book_data.get('title', '')}{book_data.get('author', '')}{book_data.get('sahaf_name', '')}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def save_book_async(self, book_data):
        """Kitabı asenkron olarak kaydetme kuyruğuna ekle"""
        self.save_queue.put(book_data)
    
    def _save_book_direct(self, book_data):
        """Kitabı doğrudan veritabanına kaydet (thread-safe)"""
        with self.lock:
            unique_id = self.generate_unique_id(book_data)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO kitaplar 
                    (unique_id, baslik, yazar, sahaf_name, sahaf_url, fiyat, fiyat_text, kitap_url, aciklama, kategori, alt_kategori, sehir)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    unique_id,
                    book_data.get('title', ''),
                    book_data.get('author', ''),
                    book_data.get('sahaf_name', ''),
                    book_data.get('sahaf_url', ''),
                    book_data.get('price_numeric', 0),
                    book_data.get('price', ''),
                    book_data.get('url', ''),
                    book_data.get('description', ''),
                    book_data.get('kategori', ''),
                    book_data.get('alt_kategori', ''),
                    book_data.get('sehir', '')
                ))
                
                conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                print(f"Veritabanı kayıt hatası: {e}")
                return False
            finally:
                conn.close()
    
    def save_book(self, book_data):
        """Tek kitabı senkron olarak kaydet (eski metod)"""
        return self._save_book_direct(book_data)
    
    def save_books(self, books_list):
        """Kitap listesini toplu olarak veritabanına kaydet (optimize edilmiş)"""
        if not books_list:
            return 0
            
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                # Toplu insert için verileri hazırla
                insert_data = []
                for book in books_list:
                    unique_id = self.generate_unique_id(book)
                    insert_data.append((
                        unique_id,
                        book.get('title', ''),
                        book.get('author', ''),
                        book.get('sahaf_name', ''),
                        book.get('sahaf_url', ''),
                        book.get('price_numeric', 0),
                        book.get('price', ''),
                        book.get('url', ''),
                        book.get('description', ''),
                        book.get('kategori', ''),
                        book.get('alt_kategori', ''),
                        book.get('sehir', '')
                    ))
                
                # Toplu insert yap
                cursor.executemany('''
                    INSERT OR IGNORE INTO kitaplar 
                    (unique_id, baslik, yazar, sahaf_name, sahaf_url, fiyat, fiyat_text, kitap_url, aciklama, kategori, alt_kategori, sehir)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', insert_data)
                
                conn.commit()
                return cursor.rowcount
            except Exception as e:
                print(f"Toplu veritabanı kayıt hatası: {e}")
                return 0
            finally:
                conn.close()
    
    def save_books_async(self, books_list):
        """Kitap listesini asenkron olarak parçalı kaydet (RAM optimized)"""
        if not books_list:
            return
            
        # Büyük listeleri küçük parçalara böl
        for i in range(0, len(books_list), self.batch_size):
            batch = books_list[i:i + self.batch_size]
            
            # Queue doluysa bekle
            while self.save_queue.qsize() >= self.save_queue.maxsize - 10:
                time.sleep(0.1)
            
            try:
                self.save_queue.put(('batch', batch), timeout=5)
            except:
                # Queue dolu, direkt kaydet
                self.save_books(batch)
                print(f"Queue dolu, {len(batch)} kitap direkt kaydedildi")
    
    def get_queue_size(self):
        """Kaydetme kuyruğundaki bekleyen kayıt sayısı"""
        return self.save_queue.qsize()
    
    def wait_for_save_completion(self):
        """Tüm kaydetme işlemlerinin tamamlanmasını bekle"""
        self.save_queue.join()
    
    def cleanup_memory(self):
        """Bellek temizliği yap"""
        gc.collect()  # Garbage collection çalıştır
        
        # Queue çok dolmuşsa bekle
        while self.save_queue.qsize() > self.save_queue.maxsize * 0.8:
            time.sleep(0.5)
    
    def execute_query(self, query, params=None):
        """SQL sorgusu çalıştır ve sonuçları döndür"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # SELECT sorgusu ise sonuçları al
                if query.strip().upper().startswith('SELECT'):
                    results = cursor.fetchall()
                    conn.close()
                    return results
                else:
                    # INSERT, UPDATE, DELETE sorguları için
                    conn.commit()
                    affected_rows = cursor.rowcount
                    conn.close()
                    return affected_rows
                    
        except Exception as e:
            print(f"Veritabanı sorgu hatası: {e}")
            print(f"Sorgu: {query}")
            if params:
                print(f"Parametreler: {params}")
            return []
