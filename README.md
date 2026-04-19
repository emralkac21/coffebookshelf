<img width="1919" height="1079" alt="Screenshot_1" src="https://github.com/user-attachments/assets/64fb1016-a8a8-42c5-ace6-5454d6cb6148" />
# 🍵📖 CoffeBookShelf — Kişisel Okuma Takip Uygulaması

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python" />
  <img src="https://img.shields.io/badge/CustomTkinter-5.2%2B-green?style=flat-square" />
  <img src="https://img.shields.io/badge/SQLite3-built--in-orange?style=flat-square" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square" />
  <img src="https://img.shields.io/badge/Lisans-MIT-purple?style=flat-square" />
</p>

> Kitaplarını takip et, okuma alışkanlığı kazan, istatistiklerinle ilerleni izle.

BookShelf; okuma listeni yönetmeni, her kitap için seans bazlı zamanlayıcı tutmanı, alıntı ve notlar kaydetmeni, yıllık hedefler koymanı ve okuduklarını grafiklerle görselleştirmeni sağlayan masaüstü bir uygulamadır.

---

## 🖥️ Ekran Görüntüleri

| Ana Sayfa | Kütüphane (Grid) | Timer |
|-----------|-----------------|-------|
| <img width="1919" height="1079" alt="Screenshot_1" src="https://github.com/user-attachments/assets/e3780bce-9749-49d8-b453-a1a2ecc763a8" /> | Kapak, durum rozeti, ilerleme çubuğu | Büyük sayaç, pause/resume, otomatik seans kaydı |

| İstatistikler | Hedefler | Kitap Detayı |
|---------------|----------|--------------|
| Matplotlib bar/pie/heatmap | Yıllık ilerleme çubukları | 4 sekme: ilerleme, seanslar, notlar, alıntılar |

---

## ✨ Özellikler

### 🏠 Ana Sayfa / Dashboard
- Günlük okuma **streak** sayacı (art arda kaç gün okunduysa)
- Bu aya ait toplam **sayfa** ve **okuma süresi**
- Şu an okunan kitaplar — sayfa progress bar'ıyla birlikte
- Her kitap için **tek tıkla timer başlatma** düğmesi
- Bugünkü okuma seanslarının özet listesi

### 📚 Kitap Kütüphanesi
- **Grid** veya **Liste** görünüm seçeneği
- Renkli **durum rozetleri** (Okunacak / Okunuyor / Okundu / Yarıda Bırakıldı)
- **Filtre:** Durum, tür ve yayın yılına göre
- **Arama:** Başlık, yazar veya ISBN ile anlık arama

### ➕ Kitap Ekleme
- **Manuel giriş** — tüm alanlar elle doldurulabilir
- **ISBN ile otomatik doldurma** — Open Library API + Google Books API (yedek)
- **Başlık ile arama** — sonuç listesinden tıkla, formu otomatik doldur
- Kapak resmi **otomatik indirilir** ve `assets/covers/` klasörüne kaydedilir
- Kapak bulunamazsa **renk bazlı placeholder** üretilir

### 📄 Kitap Detay Sayfası
Kitaba tıklayınca açılan modal 4 sekme içerir:

| Sekme | İçerik |
|-------|--------|
| **İlerleme** | Sayfa güncelleme, progress bar, durum & tarih değiştirme |
| **Seanslar** | Tüm okuma seansları tablosu (tarih, süre, sayfa aralığı, not) |
| **Notlar** | Serbest metin notu, kaydetme |
| **Alıntılar** | Alıntı ekle (sayfa numarasıyla), listele, sil |

Ayrıca: **yarım yıldız destekli derecelendirme**, başlama/bitiş tarihi, kitabı silme.

### ⏱️ Okuma Timer & Seans Takibi *(En kritik özellik)*
- Kitap seç → **Başlat / Duraklat / Devam Et / Bitir**
- Timer bitince **seans kayıt penceresi** açılır: başlangıç-bitiş sayfası, not
- Sayfa güncellemesi otomatik yansır; kitabın son sayfasına ulaşılırsa durum **Okundu** olarak işaretlenir
- **Manuel seans ekleme:** geçmişe dönük kayıt (tarih, dakika, sayfa aralığı)
- Sağ panelde seçili kitabın **tüm seans geçmişi**, silme butonu ile birlikte

### 📊 İstatistikler & Raporlar
- Toplam okunan kitap, sayfa, saat, ortalama okuma hızı (sayfa/dakika), güncel seri
- **Aylık sayfa bar grafiği** — en yüksek ay vurgulanır
- **Tür dağılımı pie chart** — okunmuş kitapların türe göre dağılımı
- **Yıllık okuma heatmap** — her gün kaç sayfa okunduğu, takvim ızgarasında
- **Aylık tamamlanan kitap bar grafiği**
- Yıl seçici ile geçmiş yıllara bakma

### 🎯 Hedefler & Challenge
- Yıl bazlı **kitap / sayfa / saat** hedefi belirleme
- Her hedef için ayrı **progress bar** ve yüzde gösterimi
- Motivasyon mesajı (hedeflere göre değişir)

### ⚙️ Ayarlar & İçe/Dışa Aktarım
- **Koyu / Açık tema** geçişi (CustomTkinter appearance mode)
- **CSV dışa aktarım** — Goodreads uyumlu format
- **JSON dışa aktarım** — seanslar ve alıntılar dahil tam veri
- **Veritabanı yedeği** (`.db` dosyası kopyalama)
- **Yedeği geri yükleme**

---

## 🚀 Kurulum

### Gereksinimler

- Python **3.10** veya üzeri
- `pip`

### Adımlar

```bash
# 1. Projeyi indir veya klonla
git clone https://github.com/kullanici/bookshelf.git
cd bookshelf

# 2. (İsteğe bağlı) Sanal ortam oluştur
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. Uygulamayı çalıştır
python main.py
```

### `requirements.txt`

```
customtkinter>=5.2.0
Pillow>=10.0.0
matplotlib>=3.7.0
requests>=2.31.0
```

> **Not:** `matplotlib` grafik özelliği için gereklidir. Yüklü değilse uygulama çalışmaya devam eder, yalnızca İstatistikler sayfasındaki grafikler gösterilmez.

---

## 📁 Proje Yapısı

```
booktracker/
│
├── main.py                        ← Başlangıç noktası
├── app.py                         ← Ana pencere, view yönetimi, navigasyon
├── requirements.txt
├── README.md
│
├── assets/
│   └── covers/                    ← İndirilen ve üretilen kapak görselleri
│
├── database/
│   └── db_manager.py              ← SQLite3 singleton — tüm CRUD & sorgu metotları
│
├── services/
│   ├── book_search.py             ← Open Library + Google Books API araması
│   ├── cover_downloader.py        ← Kapak indirme (arka plan thread)
│   └── export_service.py          ← CSV / JSON dışa aktarım, DB yedek/geri yükleme
│
├── ui/
│   ├── components/
│   │   ├── sidebar.py             ← Sol navigasyon paneli
│   │   ├── book_card.py           ← Grid kartı + liste satırı bileşenleri
│   │   └── star_rating.py         ← Yarım yıldız destekli Canvas widget'ı
│   │
│   ├── views/                     ← Her sayfa ayrı bir view sınıfı
│   │   ├── dashboard.py           ← Ana sayfa
│   │   ├── library.py             ← Kütüphane (grid/liste, filtre, arama)
│   │   ├── timer_view.py          ← Okuma zamanlayıcısı ve seans geçmişi
│   │   ├── stats_view.py          ← Matplotlib grafik sayfası
│   │   ├── goals_view.py          ← Yıllık hedefler
│   │   └── settings_view.py       ← Tema, dışa aktarım, yedek
│   │
│   └── modals/
│       ├── add_book.py            ← Kitap ekleme (manuel + API arama)
│       └── book_detail.py         ← Kitap detay (4 sekme)
│
└── utils/
    ├── constants.py               ← Renkler, sabitler, navigasyon öğeleri
    └── helpers.py                 ← Format fonksiyonları, kapak yükleme/üretme
```

---

## 🗄️ Veritabanı Şeması

Uygulama ilk çalıştırmada `bookshelf.db` dosyasını otomatik oluşturur.

```
books               → Kitap bilgileri (başlık, yazar, ISBN, tür, sayfa, durum, puan…)
reading_sessions    → Okuma seansları (kitap_id, tarih, süre, sayfa aralığı, not)
quotes              → Alıntılar (kitap_id, metin, sayfa, eklenme tarihi)
goals               → Yıllık hedefler (yıl, kitap/sayfa/saat hedefi)
settings            → Uygulama ayarları (anahtar-değer)
```

---

## ⌨️ Hızlı Kullanım Kılavuzu

### İlk kitabı eklemek
1. Sol menüden **Kütüphane** → **＋ Kitap Ekle**
2. ISBN kutusuna ISBN-13 kodunu yazıp **Ara** — bilgiler otomatik dolar
3. Veya başlık/yazar adı yazıp ara, sonuç listesinden seç
4. **Kaydet**

### Okuma seansı başlatmak
1. Sol menüden **Timer**
2. Kitap açılır menüsünden kitabı seç
3. **▶ Başlat** — sayaç çalışmaya başlar
4. Okumayı bitirince **⏹ Bitir** → başlangıç/bitiş sayfasını gir → **Kaydet**

### Hızlı timer (Ana Sayfa'dan)
Ana Sayfa'da "Şu An Okuduklarım" listesindeki **▶** butonuna tıkla — doğrudan Timer sayfasına o kitap seçili olarak atlar.

---

## 🔌 Dış API Kullanımı

| Servis | Amaç | İnternet gerekli? |
|--------|------|:-----------------:|
| [Open Library API](https://openlibrary.org/developers/api) | ISBN ile kitap bilgisi | ✅ |
| [Google Books API](https://developers.google.com/books) | ISBN / başlık ile arama (yedek) | ✅ |

İnternet bağlantısı olmadan uygulama tamamen çalışır; yalnızca **otomatik doldurma ve kapak indirme** özellikleri devre dışı kalır.

---

## 🧩 Yeni Modül Eklemek

Mimari, yeni sayfa eklemeyi kolay kılacak şekilde tasarlandı:

### 1. Yeni bir view oluştur

```python
# ui/views/my_view.py
import customtkinter as ctk
from utils.constants import COLORS

class MyView(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg"])
        super().__init__(parent, **kwargs)
        self._app = app

    def refresh(self, **kwargs):
        # Sayfa her gösterildiğinde çağrılır
        pass
```

### 2. `app.py`'ye kaydet

```python
# app.py → _init_views() metoduna ekle
from ui.views.my_view import MyView

view_classes = {
    ...
    "my_view": MyView,   # ← ekle
}
```

### 3. `constants.py`'de navigasyona ekle

```python
NAV_ITEMS = [
    ...
    ("🔖", "Sayfam", "my_view"),   # ← ekle
]
```

Bu üç adım yeterli — sidebar, navigasyon ve view yönetimi otomatik çalışır.

---

## 🐛 Bilinen Sorunlar & Çözümler

| Sorun | Çözüm |
|-------|-------|
| `ModuleNotFoundError: tkinter` | `sudo apt install python3-tk` (Linux) |
| Grafikler görünmüyor | `pip install matplotlib` |
| Kapak indirme çalışmıyor | İnternet bağlantısını kontrol et |
| Windows'ta renk hatası (`invalid color name`) | v1.0.1+ ile düzeltildi |
| Yüksek DPI'da bulanık yazı | `main.py` başına `ctypes` DPI ayarı eklenebilir |

---

## 🤝 Katkıda Bulunmak

1. Fork'la
2. Feature branch aç: `git checkout -b feature/yeni-ozellik`
3. Commit'le: `git commit -m "feat: yeni özellik açıklaması"`
4. Push'la: `git push origin feature/yeni-ozellik`
5. Pull Request aç

---

## 📄 Lisans

MIT License — dilediğin gibi kullanabilir, değiştirebilir ve dağıtabilirsin.

---

<p align="center">
  Sevgiyle 🐍 Python ile yapıldı
</p>
