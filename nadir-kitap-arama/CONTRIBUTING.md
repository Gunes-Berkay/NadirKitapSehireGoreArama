# 🤝 Katkıda Bulunma Rehberi

Nadir Kitap Arama & Analiz Uygulaması'na katkıda bulunmak istediğiniz için teşekkür ederiz! Bu rehber, katkıda bulunma sürecini kolaylaştırmak için hazırlanmıştır.

## 📋 İçindekiler

- [Geliştirme Ortamını Kurma](#geliştirme-ortamını-kurma)
- [Katkı Türleri](#katkı-türleri)
- [Pull Request Süreci](#pull-request-süreci)
- [Kod Standartları](#kod-standartları)
- [Bug Raporlama](#bug-raporlama)
- [Özellik İsteği](#özellik-i̇steği)

## 🛠️ Geliştirme Ortamını Kurma

### 1. Repository'yi Fork Edin
```bash
# GitHub'da fork butonuna tıklayın, sonra:
git clone https://github.com/KULLANICI_ADINIZ/nadir-kitap-arama.git
cd nadir-kitap-arama
```

### 2. Geliştirme Ortamını Hazırlayın
```bash
# Sanal ortam oluşturun
python -m venv venv

# Sanal ortamı aktifleştirin
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Gereksinimlerimizi kurun
pip install -r requirements.txt

# Development dependencies (opsiyonel)
pip install pytest pytest-qt black flake8
```

### 3. Upstream Remote Ekleyin
```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/nadir-kitap-arama.git
```

## 🎯 Katkı Türleri

### 🐛 Bug Fixes
- Mevcut hataları düzeltme
- Performance iyileştirmeleri
- Memory leak'leri giderme

### ✨ Yeni Özellikler
- UI/UX iyileştirmeleri
- Yeni analiz türleri
- Export/import fonksiyonları

### 📚 Dokümantasyon
- README güncellemeleri
- Kod yorumları
- API dokümantasyonu

### 🧪 Test
- Unit testleri
- Integration testleri
- Performance testleri

## 🔄 Pull Request Süreci

### 1. Branch Oluşturun
```bash
# Main branch'ten başlayın
git checkout main
git pull upstream main

# Yeni feature branch oluşturun
git checkout -b feature/yeni-ozellik-adi
# veya
git checkout -b bugfix/hata-aciklamasi
```

### 2. Geliştirme Yapın
- Küçük, anlamlı commit'ler yapın
- Commit mesajlarını Türkçe yazın
- Her commit'in tek bir amacı olsun

### 3. Test Edin
```bash
# Uygulamayı test edin
python run.py

# Test suite çalıştırın (eğer varsa)
pytest

# Code quality check
flake8 gui_dosyalari/
black gui_dosyalari/ --check
```

### 4. Push ve PR Oluşturun
```bash
git push origin feature/yeni-ozellik-adi
```

GitHub'da Pull Request oluşturun ve şu bilgileri ekleyin:
- **Başlık**: Kısa ve açıklayıcı
- **Açıklama**: Ne yaptığınızı detaylıca açıklayın
- **Test**: Nasıl test edildiğini belirtin
- **Screenshots**: UI değişiklikleri varsa ekran görüntüleri

## 📝 Kod Standartları

### 🐍 Python Kodlama Standartları

```python
# PEP 8 uyumlu kod yazın
# Türkçe yorum ve docstring'ler kullanın

def kitap_ara(yazar_adi: str, kitap_adi: str = "") -> List[Dict]:
    """
    Verilen kriterlere göre kitap arar.
    
    Args:
        yazar_adi: Aranacak yazar adı
        kitap_adi: Aranacak kitap adı (opsiyonel)
    
    Returns:
        Bulunan kitapların listesi
    """
    # Implementation...
    pass
```

### 🎨 UI/UX Standartları
- Dark theme uyumlu renkler kullanın
- Türkçe etiketler ve butonlar
- Responsive tasarım prensipleri
- Accessibility kuralları

### 🗄️ Veritabanı Standartları
- Thread-safe işlemler
- Transaction kullanımı
- Proper error handling
- Data validation

## 🐛 Bug Raporlama

### Issue Template
```markdown
## 🐛 Bug Raporu

### Açıklama
Hatanın kısa açıklaması...

### Reproduce Adımları
1. Uygulamayı başlat
2. X menüsüne git
3. Y butonuna tıkla
4. Hata oluşur

### Beklenen Davranış
Ne olması gerekiyordu...

### Gerçek Davranış
Ne oldu...

### Sistem Bilgileri
- OS: Windows 11
- Python: 3.10.5
- PyQt6: 6.5.1

### Ekran Görüntüleri
(Varsa ekleyin)

### Hata Mesajları
```
Traceback...
```

### Ek Bilgiler
Başka önemli detaylar...
```

## ✨ Özellik İsteği

### Feature Request Template
```markdown
## 🚀 Özellik İsteği

### Özellik Açıklaması
Yeni özelliğin detaylı açıklaması...

### Motivasyon
Bu özellik neden gerekli...

### Kullanım Senaryosu
Nasıl kullanılacağının örneği...

### Alternatifler
Mevcut çözümler ve neden yeterli değil...

### Teknik Detaylar
Implementation fikirleri...

### Mockup/Wireframe
(Varsa UI tasarımları)
```

## 🔍 Code Review Süreci

### Review Kriterleri
- [ ] Kod PEP 8 uyumlu
- [ ] Docstring'ler mevcut
- [ ] Error handling uygun
- [ ] Performance etkileri değerlendirilmiş
- [ ] UI responsive
- [ ] Thread safety sağlanmış

### Review Yorumları
- Yapıcı ve kibar olun
- Örneklerle açıklayın
- Öğretici yaklaşım benimseyin

## 🏷️ Versiyonlama

### Semantic Versioning
- **MAJOR**: Breaking changes
- **MINOR**: Yeni özellikler (backward compatible)
- **PATCH**: Bug fixes

### Tag Oluşturma
```bash
git tag -a v2.1.0 -m "Release v2.1.0: Excel export özelliği eklendi"
git push upstream v2.1.0
```

## 📞 İletişim

### Geliştirici Topluluğu
- **Discord**: [Proje Discord Sunucusu]
- **Telegram**: [Proje Telegram Grubu]
- **GitHub Discussions**: Genel tartışmalar için

### Mentorship
Yeni geliştiriciler için mentor desteği:
- Slack DM
- Zoom pair programming
- Code review sessions

## 🎉 Katkıda Bulunanları Tanıma

### Contributors List
Katkıda bulunanlar otomatik olarak README.md dosyasına eklenir.

### Recognition
- GitHub profile'da highlight
- Monthly contributor spotlight
- Özel badge'ler

## 📚 Kaynaklar

### Öğrenme Materyalleri
- [PyQt6 Documentation](https://doc.qt.io/qtforpython/)
- [Python Threading Guide](https://docs.python.org/3/library/threading.html)
- [SQLite Best Practices](https://sqlite.org/draft/bestpractices.html)

### Useful Tools
- **IDE**: PyCharm, VSCode
- **GUI Designer**: Qt Designer
- **Database**: DB Browser for SQLite
- **Testing**: pytest, pytest-qt

---

🙏 **Katkılarınız için şimdiden teşekkür ederiz!**

Bu rehberde eksik gördüğünüz bir konu varsa, lütfen issue açın veya pull request gönderin.
