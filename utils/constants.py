APP_NAME = "CoffeShelf"
APP_VERSION = "1.0.0 Emrullah ALKAÇ"
DB_PATH = "bookshelf.db"
COVERS_DIR = "assets/covers"
DEFAULT_COVER = "assets/default_cover.png"

WINDOW_SIZE = "1340x840"
SIDEBAR_WIDTH = 230

STATUS_TO_READ  = "to_read"
STATUS_READING  = "reading"
STATUS_READ     = "read"
STATUS_DNF      = "dnf"

STATUS_LABELS = {
    "to_read": "Okunacak",
    "reading": "Okunuyor",
    "read":    "Okundu",
    "dnf":     "Yarıda Bırakıldı",
}

STATUS_KEYS_FROM_LABEL = {v: k for k, v in STATUS_LABELS.items()}

GENRES = [
    "Tümü", "Roman", "Bilim Kurgu", "Fantezi", "Polisiye", "Tarih",
    "Biyografi", "Kişisel Gelişim", "Bilim", "Felsefe", "Psikoloji",
    "Ekonomi", "Sanat", "Şiir", "Çocuk", "Gençlik", "Diğer",
]

MONTH_NAMES_TR = [
    "", "Oca", "Şub", "Mar", "Nis", "May", "Haz",
    "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara",
]

COLORS = {
    # Arka plan ve Yüzeyler (Derin Espresso ve Mocha tonları)
    "bg_dark":      "#17110F",  # En alt katman (Çok koyu espresso)
    "bg":           "#1E1614",  # Ana uygulama arka planı (Koyu kavrulmuş kahve)
    "surface":      "#2C211D",  # Yüzeyler (Mocha)
    "card":         "#352822",  # Kartlar (Biraz daha açık mocha)
    "card_hover":   "#42322B",  # Kart üzerine gelince (Sütlü kahveye doğru)
    "border":       "#4D3A32",  # Kenarlıklar
    "border_light": "#5E483E",

    # Vurgu Renkleri (Karamel ve Altın kahve tonları)
    "accent":       "#D59B6A",  # Ana vurgu rengi (Sıcak karamel)
    "accent_dark":  "#B07D53",  # Tıklama/Aktif durumlar
    "accent_hover": "#E8B285",  # Hover durumu
    "accent_dim":   "#4A3525",  # Vurgu renginin arka planda kullanılacak koyu hali

    # Durum ve Anlamsal Renkler (Kahve temasına uyan pastel/toprak tonları)
    "green":        "#7DAF74",  # Adaçayı yeşili (Çiğ durmaması için)
    "green_dark":   "#5E8756",
    "red":          "#CC6666",  # Kiremit kırmızısı
    "red_dark":     "#A34C4C",
    "blue":         "#6C9DBE",  # Çelik/Puslu mavi
    "yellow":       "#D9B466",  # Bal sarısı
    "purple":       "#9C78AB",  # Mürdüm/Erik
    "teal":         "#60A39C",  # Soluk turkuaz

    # Durumlar (Okuma takip veya kelime kartları durumları için)
    "status_to_read": "#6C9DBE",  # Puslu mavi
    "status_reading": "#D9B466",  # Bal sarısı (Daha aktif hissettirir)
    "status_read":    "#D59B6A",  # Karamel (Tamamlanan)
    "status_dnf":     "#CC6666",  # Kiremit kırmızısı

    # Rozet (Badge) Arka Planları (Kart rengi olan #352822 ile harmanlanmış koyu tonlar)
    "badge_to_read_bg": "#2A3236",  
    "badge_reading_bg": "#3D3826",  
    "badge_read_bg":    "#423024",  
    "badge_dnf_bg":     "#402828",  

    # Metin Renkleri (Latte köpüğü tonlarında, saf beyaz olmayan sıcak açık renkler)
    "text":          "#F4F3F2",  # Ana metin (Sıcak kırık beyaz)
    "text_muted":    "#B3A8A0",  # İkincil metinler
    "text_dim":      "#827770",  # Pasif detaylar
    "text_disabled": "#5C524C",  # Devre dışı metinler

    # Yan Menü (Sidebar) (Ana alandan ayrışan daha karanlık ve tok bir kahve)
    "sidebar_bg":     "#120D0C",  # En karanlık ton
    "sidebar_active": "#2C211D",  # Seçili menü arka planı
    "sidebar_text":   "#C4B9B3",  
    "sidebar_accent": "#D59B6A",  # Karamel menü vurgusu
}

NAV_ITEMS = [
    ("🏠", "Ana Sayfa",    "dashboard"),
    ("📚", "Kütüphane",   "library"),
    ("⏱",  "Timer",       "timer"),
    ("📊", "İstatistikler","stats"),
    ("🎯", "Hedefler",    "goals"),
    ("⚙",  "Ayarlar",     "settings"),
]
