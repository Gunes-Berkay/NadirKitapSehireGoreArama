# Nadir Kitap Arama & Analiz Uygulaması

## 📁 Proje Yapısı

```
Nadir Kitap/
├── run.py                    # Ana çalıştırma dosyası
├── kitap_arama_gui.py       # Orijinal monolitik dosya (yedek)
├── kategoriler.json         # Kategori verileri
├── sahaflar.json           # Sahaf verileri
├── kitaplar.db             # SQLite veritabanı
└── gui_dosyalari/          # Modülerleştirilmiş GUI bileşenleri
    ├── __init__.py         # Paket dosyası
    ├── utils.py            # Yardımcı fonksiyonlar
    ├── database.py         # Veritabanı yönetimi
    ├── widgets.py          # Custom widget'lar
    ├── workers.py          # Thread worker'lar
    ├── search_tab.py       # Kitap arama sekmesi
    ├── analysis_tab.py     # Kitap analiz sekmesi
    └── main_window.py      # Ana uygulama penceresi
```

## 🚀 Uygulamayı Çalıştırma

```bash
python run.py
```

## 📋 Modül Açıklamaları

### 🔧 `utils.py` - Yardımcı Fonksiyonlar
- `turkish_to_english_chars()`: Türkçe karakter dönüştürme

### 🗄️ `database.py` - Veritabanı Yönetimi
- `DatabaseManager`: Thread-safe SQLite işlemleri
- Asenkron kaydetme sistemi
- Batch işleme ve bellek optimizasyonu

### 🎨 `widgets.py` - Custom Widget'lar
- `ClickableLabel`: Tıklanabilir etiket widget'ı

### ⚡ `workers.py` - Thread Worker'lar
- `BookSearchWorker`: Çoklu thread kitap arama
- Web scraping ve veri işleme
- Progress tracking ve iptal mekanizması

### 🔍 `search_tab.py` - Arama Sekmesi
- Gelişmiş arama formu
- Chunked display processing (UI donması engelleme)
- Otomatik kaydetme seçenekleri
- Real-time progress tracking

### 📊 `analysis_tab.py` - Analiz Sekmesi
- Filtreli analiz sistemi
- Yazar, sahaf, kategori, şehir analizleri
- Fiyat analizleri ve genel istatistikler
- Zengin raporlama sistemi

### 🖥️ `main_window.py` - Ana Pencere
- Tab-based arayüz
- Dark theme tasarım
- Merkezi uygulama yönetimi

### ▶️ `run.py` - Çalıştırma Dosyası
- Uygulama başlatma noktası
- QApplication kurulumu

## ✨ Özellikler

### 🎯 Arama Özellikleri
- **Çoklu Filtre**: Yazar, kitap adı, kategori, alt kategori, şehir
- **Akıllı Karakter Dönüştürme**: Türkçe → İngilizce
- **Threaded Arama**: Maksimum performans
- **Progress Tracking**: Real-time ilerleme takibi
- **Durdurma Özelliği**: İstediğiniz zaman aramaları durdurun
- **Chunked Display**: Büyük sonuçlarda UI donması engelleme

### 💾 Veritabanı Özellikleri
- **Thread-Safe**: Eşzamanlı işlemler desteklenir
- **Batch Processing**: 50'li gruplar halinde kaydetme
- **Bounded Queue**: Bellek sınırları (1000 item)
- **Unique ID**: Duplicate kayıt engelleme
- **Auto-Save**: Otomatik kaydetme seçeneği

### 📈 Analiz Özellikleri
- **Filtreli Analiz**: Kategori, şehir, fiyat filtrelemeleri
- **Yazar Analizi**: En çok kitabı olan yazarlar, fiyat analizleri
- **Sahaf Analizi**: Sahaf performans metrikleri
- **Kategori Analizi**: Kategori bazında istatistikler
- **Şehir Analizi**: Coğrafi dağılım analizi
- **Fiyat Analizi**: Detaylı fiyat istatistikleri
- **Genel İstatistikler**: Kapsamlı özet raporlar

### 🎨 UI/UX Özellikleri
- **Dark Theme**: Modern koyu tema
- **Responsive Design**: Büyük veri setlerinde responsive
- **Clickable Links**: Kitap URL'lerine direkt erişim
- **Real-time Updates**: Canlı durum güncellemeleri
- **Memory Efficient**: RAM dostu tasarım

## 🔧 Teknik Detaylar

### 🧵 Threading Architecture
- **ThreadPoolExecutor**: Maksimum 8 concurrent thread
- **Stop Mechanism**: Güvenli thread sonlandırma
- **Memory Cleanup**: Her 5 operasyonda bellek temizliği

### 🎭 UI Responsiveness
- **Chunked Processing**: 20'li gruplar halinde display
- **QTimer Based**: 10ms interval ile progressive loading
- **processEvents()**: UI thread protection

### 💾 Memory Management
- **Bounded Queues**: 1000 item limit
- **Batch Operations**: 50 item batches
- **Garbage Collection**: Otomatik bellek temizliği

## 🏗️ Modülerleştirme Faydaları

1. **Kod Okunabilirliği**: Her modül tek sorumluluk prensibi
2. **Geliştirme Kolaylığı**: Bağımsız modül geliştirme
3. **Test Edilebilirlik**: Her modül ayrı test edilebilir
4. **Yeniden Kullanılabilirlik**: Modüller başka projelerde kullanılabilir
5. **Bakım Kolaylığı**: Bug fix ve feature'lar lokalize edilebilir
6. **Performans**: İhtiyaç duyulan modüller lazy load edilebilir

## 🔄 Güncellemeler

### v2.0 - Modüler Mimari
- ✅ Monolitik yapıdan modüler yapıya geçiş
- ✅ 8 ayrı modüle bölünmüş kod yapısı
- ✅ Import optimizasyonu
- ✅ Thread-safe veritabanı işlemleri
- ✅ UI responsiveness iyileştirmeleri
- ✅ Memory management optimizasyonları

## 👨‍💻 Geliştirici Notları

Bu modüler yapı sayesinde:
- Yeni özellikler kolayca eklenebilir
- Mevcut modüller bağımsız olarak güncellenebilir
- Test senaryoları her modül için ayrı yazılabilir
- Kod review süreci daha verimli hale gelir
- Yeni geliştiriciler projeye daha kolay adapte olabilir
