import customtkinter as ctk
from datetime import date
from database.db_manager import get_db
from utils.constants import COLORS
from utils.helpers import format_duration, progress_percent, load_or_generate_cover


class DashboardView(ctk.CTkScrollableFrame):
    def __init__(self, parent, app, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg"])
        kwargs.setdefault("scrollbar_button_color", COLORS["border"])
        super().__init__(parent, **kwargs)
        self._app = app
        self._db  = get_db()

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def _build(self):
        db   = self._db
        now  = date.today()

        # ── Header ────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(28, 6))

        days_tr = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
        months_tr = ["","Ocak","Şubat","Mart","Nisan","Mayıs","Haziran",
                     "Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
        day_name = days_tr[now.weekday()]
        date_str = f"{day_name}, {now.day} {months_tr[now.month]} {now.year}"

        ctk.CTkLabel(
            header, text=date_str,
            font=("Helvetica", 12),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            header, text="Hoş geldin! 👋",
            font=("Georgia", 26, "bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w")

        # ── Quick Timer Button ────────────────────────────────────────────
        ctk.CTkButton(
            header, text="⏱  Okumaya Başla",
            font=("Helvetica", 13, "bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["bg"],
            corner_radius=8,
            height=38,
            width=180,
            command=lambda: self._app.navigate("timer"),
        ).pack(anchor="w", pady=(10, 0))

        # ── Stats Row ─────────────────────────────────────────────────────
        stats    = db.get_total_stats()
        streak   = db.get_streak()
        m_stats  = db.get_month_stats(now.year, now.month)
        today_st = db.get_today_stats()

        stat_items = [
            ("🔥", str(streak), "Gün Serisi"),
            ("📄", f"{m_stats['pages']:,}", "Bu Ay (sayfa)"),
            ("⏰", f"{m_stats['seconds']//3600}s {(m_stats['seconds']%3600)//60}dk",
             "Bu Ay (süre)"),
            ("📚", str(stats["books_read"]), "Toplam Okunan"),
        ]

        row_frame = ctk.CTkFrame(self, fg_color="transparent")
        row_frame.pack(fill="x", padx=30, pady=(18, 0))
        for icon, val, lbl in stat_items:
            card = self._stat_card(row_frame, icon, val, lbl)
            card.pack(side="left", padx=(0, 12), ipadx=10)

        # ── Divider ───────────────────────────────────────────────────────
        ctk.CTkFrame(self, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=30, pady=22
        )

        # ── Currently Reading ─────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="Şu An Okuduklarım",
            font=("Georgia", 17, "bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=30, pady=(0, 12))

        reading = db.get_currently_reading()
        if not reading:
            ctk.CTkLabel(
                self, text="Şu an aktif bir kitap yok. Kütüphaneden bir kitap seç!",
                font=("Helvetica", 12),
                text_color=COLORS["text_dim"],
            ).pack(anchor="w", padx=30)
        else:
            for book in reading[:5]:
                self._reading_card(book).pack(fill="x", padx=30, pady=(0, 10))

        # ── Today's Sessions ──────────────────────────────────────────────
        ctk.CTkFrame(self, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=30, pady=22
        )
        ctk.CTkLabel(
            self, text="Bugün",
            font=("Georgia", 17, "bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=30, pady=(0, 10))

        today_sessions = db.get_sessions_range(
            now.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")
        )
        if not today_sessions:
            ctk.CTkLabel(
                self, text="Bugün henüz okuma seansı kaydedilmedi.",
                font=("Helvetica", 12),
                text_color=COLORS["text_dim"],
            ).pack(anchor="w", padx=30)
        else:
            for s in today_sessions[:8]:
                self._session_row(s).pack(fill="x", padx=30, pady=(0, 6))

        ctk.CTkFrame(self, height=30, fg_color="transparent").pack()

    # ── helpers ──────────────────────────────────────────────────────────

    def _stat_card(self, parent, icon, val, lbl):
        card = ctk.CTkFrame(parent, fg_color=COLORS["card"], corner_radius=10,
                            width=155, height=90)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=icon, font=("Helvetica", 22)).pack(pady=(12, 0))
        ctk.CTkLabel(card, text=val,
                     font=("Georgia", 20, "bold"),
                     text_color=COLORS["accent"]).pack()
        ctk.CTkLabel(card, text=lbl,
                     font=("Helvetica", 10),
                     text_color=COLORS["text_muted"]).pack(pady=(0, 10))
        return card

    def _reading_card(self, book):
        frame = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=10)
        frame.grid_columnconfigure(1, weight=1)

        # Mini cover
        img = load_or_generate_cover(book["cover_path"], book["title"], book["author"], (48, 70))
        ctk.CTkLabel(frame, image=img, text="").grid(row=0, column=0, rowspan=3,
                                                      padx=(12, 10), pady=10)
        # Title & author
        title = book["title"][:55] + ("…" if len(book["title"]) > 55 else "")
        ctk.CTkLabel(frame, text=title, font=("Georgia", 13, "bold"),
                     text_color=COLORS["text"], anchor="w").grid(
            row=0, column=1, sticky="ew", padx=0, pady=(10, 0))
        ctk.CTkLabel(frame, text=book["author"],
                     font=("Helvetica", 11), text_color=COLORS["text_muted"],
                     anchor="w").grid(row=1, column=1, sticky="ew")

        # Progress bar
        pct = progress_percent(book["current_page"], book["total_pages"])
        prog_row = ctk.CTkFrame(frame, fg_color="transparent")
        prog_row.grid(row=2, column=1, sticky="ew", pady=(4, 10), padx=(0, 12))

        bar = ctk.CTkProgressBar(prog_row, height=6, corner_radius=3,
                                  progress_color=COLORS["green"],
                                  fg_color=COLORS["border"])
        bar.pack(side="left", fill="x", expand=True)
        bar.set(pct / 100)

        ctk.CTkLabel(prog_row,
                     text=f" {book['current_page']}/{book['total_pages']} sf  {pct:.0f}%",
                     font=("Helvetica", 10), text_color=COLORS["green"]).pack(side="left")

        # Timer button
        bid = book["id"]
        ctk.CTkButton(frame, text="▶", width=34, height=34,
                      fg_color=COLORS["accent_dim"],
                      hover_color=COLORS["accent"],
                      text_color=COLORS["accent"],
                      corner_radius=17,
                      command=lambda: self._app.navigate("timer", book_id=bid)
                      ).grid(row=0, column=2, rowspan=3, padx=12)
        return frame

    def _session_row(self, session):
        frame = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=6)
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="📖", font=("Helvetica", 16)).grid(
            row=0, column=0, padx=(12, 8), pady=8)
        ctk.CTkLabel(frame,
                     text=session["title"][:45] + ("…" if len(session["title"]) > 45 else ""),
                     font=("Helvetica", 12, "bold"),
                     text_color=COLORS["text"], anchor="w"
                     ).grid(row=0, column=1, sticky="ew")
        dur = format_duration(session["duration_seconds"])
        info = f"{dur}  ·  {session['pages_read']} sayfa"
        ctk.CTkLabel(frame, text=info,
                     font=("Helvetica", 10), text_color=COLORS["text_muted"],
                     anchor="e").grid(row=0, column=2, padx=12)
        return frame
