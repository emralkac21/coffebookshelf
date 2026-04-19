import customtkinter as ctk
from datetime import datetime, date
from database.db_manager import get_db
from utils.constants import COLORS, STATUS_LABELS
from utils.helpers import format_duration_short, format_duration


class TimerView(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg"])
        super().__init__(parent, **kwargs)
        self._app  = app
        self._db   = get_db()

        # Timer state
        self._running         = False
        self._paused          = False
        self._accumulated     = 0   # seconds before last pause
        self._start_time      = None
        self._selected_book   = None   # full sqlite Row
        self._session_note    = ""
        self._after_id        = None

        self._build()

    def refresh(self, book_id=None):
        self._load_books()
        if book_id:
            # Pre-select the book
            for i, b in enumerate(self._books):
                if b["id"] == book_id:
                    self._book_var.set(self._book_labels[i])
                    self._on_book_select(self._book_labels[i])
                    break

    def _build(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ── Left panel: Timer ─────────────────────────────────────────────
        left = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=16)
        left.grid(row=0, column=0, sticky="nsew", padx=(28, 12), pady=28)
        left.grid_rowconfigure(10, weight=1)

        ctk.CTkLabel(left, text="Okuma Timer",
                     font=("Georgia", 20, "bold"),
                     text_color=COLORS["text"]).pack(pady=(24, 4))
        ctk.CTkLabel(left, text="Kitap seç ve zamanlayıcıyı başlat",
                     font=("Helvetica", 11), text_color=COLORS["text_muted"]).pack()

        # Book selector
        ctk.CTkLabel(left, text="Kitap", font=("Helvetica", 11, "bold"),
                     text_color=COLORS["text_muted"]).pack(anchor="w", padx=24, pady=(20, 4))

        self._books = []
        self._book_labels = []
        self._book_var = ctk.StringVar(value="— Kitap seç —")

        self._book_menu = ctk.CTkOptionMenu(
            left,
            values=["— Kitap seç —"],
            variable=self._book_var,
            command=self._on_book_select,
            fg_color=COLORS["card"], button_color=COLORS["border"],
            button_hover_color=COLORS["border_light"],
            text_color=COLORS["text"], width=300, height=38,
        )
        self._book_menu.pack(padx=24)
        self._load_books()

        # Book info label
        self._book_info_lbl = ctk.CTkLabel(
            left, text="", font=("Helvetica", 11),
            text_color=COLORS["text_muted"], wraplength=280
        )
        self._book_info_lbl.pack(padx=24, pady=(6, 0))

        # ── Big Timer Display ──────────────────────────────────────────────
        timer_frame = ctk.CTkFrame(left, fg_color=COLORS["card"], corner_radius=20)
        timer_frame.pack(padx=24, pady=24, fill="x")

        self._timer_lbl = ctk.CTkLabel(
            timer_frame, text="00:00",
            font=("Courier", 58, "bold"),
            text_color=COLORS["accent"],
        )
        self._timer_lbl.pack(pady=(20, 4))
        self._timer_sub = ctk.CTkLabel(
            timer_frame, text="Hazır",
            font=("Helvetica", 12), text_color=COLORS["text_muted"],
        )
        self._timer_sub.pack(pady=(0, 20))

        # ── Control Buttons ────────────────────────────────────────────────
        btn_row = ctk.CTkFrame(left, fg_color="transparent")
        btn_row.pack(padx=24, pady=(0, 16))

        self._start_btn = ctk.CTkButton(
            btn_row, text="▶  Başlat",
            font=("Helvetica", 14, "bold"),
            fg_color=COLORS["green"], hover_color=COLORS["green_dark"],
            text_color="white", corner_radius=10, width=120, height=44,
            command=self._toggle_start,
        )
        self._start_btn.pack(side="left", padx=6)

        self._pause_btn = ctk.CTkButton(
            btn_row, text="⏸  Duraklat",
            font=("Helvetica", 14, "bold"),
            fg_color=COLORS["card"], hover_color=COLORS["card_hover"],
            text_color=COLORS["text_muted"], corner_radius=10, width=130, height=44,
            state="disabled",
            command=self._toggle_pause,
        )
        self._pause_btn.pack(side="left", padx=6)

        self._stop_btn = ctk.CTkButton(
            btn_row, text="⏹  Bitir",
            font=("Helvetica", 14, "bold"),
            fg_color=COLORS["card"], hover_color=COLORS["red_dark"],
            text_color=COLORS["text_muted"], corner_radius=10, width=110, height=44,
            state="disabled",
            command=self._stop_timer,
        )
        self._stop_btn.pack(side="left", padx=6)

        # ── Session note ────────────────────────────────────────────────────
        ctk.CTkLabel(left, text="Seans Notu (isteğe bağlı)",
                     font=("Helvetica", 11), text_color=COLORS["text_muted"]
                     ).pack(anchor="w", padx=24)
        self._note_entry = ctk.CTkEntry(
            left, placeholder_text="Bu seansa dair not...",
            fg_color=COLORS["card"], border_color=COLORS["border"],
            text_color=COLORS["text"], height=36,
        )
        self._note_entry.pack(fill="x", padx=24, pady=(4, 16))

        # Manual session add
        ctk.CTkButton(
            left, text="＋  Manuel Seans Ekle",
            font=("Helvetica", 11),
            fg_color="transparent", border_color=COLORS["border"],
            hover_color=COLORS["card"], text_color=COLORS["text_muted"],
            border_width=1, corner_radius=8, height=32,
            command=self._manual_session,
        ).pack(padx=24, pady=(0, 20))

        # ── Right panel: Session History ──────────────────────────────────
        right = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=16)
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 28), pady=28)
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(right, text="Seans Geçmişi",
                     font=("Georgia", 18, "bold"),
                     text_color=COLORS["text"]).grid(
            row=0, column=0, sticky="w", padx=20, pady=(20, 10)
        )

        self._history_scroll = ctk.CTkScrollableFrame(
            right, fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
        )
        self._history_scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

        self._refresh_history()

    # ── Book loading ──────────────────────────────────────────────────────

    def _load_books(self):
        books = self._db.get_all_books()
        self._books = books
        self._book_labels = []
        for b in books:
            status = STATUS_LABELS.get(b["status"], b["status"])
            self._book_labels.append(f"{b['title'][:40]}  [{status}]")
        vals = self._book_labels if self._book_labels else ["— Kitap yok —"]
        self._book_menu.configure(values=["— Kitap seç —"] + vals)

    def _on_book_select(self, label):
        if label == "— Kitap seç —":
            self._selected_book = None
            self._book_info_lbl.configure(text="")
            return
        try:
            idx = self._book_labels.index(label)
            self._selected_book = self._books[idx]
            b = self._selected_book
            info = f"{b['author']}  ·  Sayfa: {b['current_page']}/{b['total_pages'] or '?'}"
            self._book_info_lbl.configure(text=info)
        except ValueError:
            pass
        self._refresh_history()

    # ── Timer logic ────────────────────────────────────────────────────────

    def _elapsed(self) -> int:
        if self._running and not self._paused and self._start_time:
            delta = (datetime.now() - self._start_time).total_seconds()
            return int(self._accumulated + delta)
        return self._accumulated

    def _toggle_start(self):
        if not self._selected_book:
            self._flash_error("Önce bir kitap seçin.")
            return
        if not self._running:
            # Start
            self._running     = True
            self._paused      = False
            self._start_time  = datetime.now()
            self._start_btn.configure(text="▶  Devam", fg_color=COLORS["green"])
            self._pause_btn.configure(state="normal", text_color=COLORS["text"])
            self._stop_btn.configure(state="normal", text_color=COLORS["text"])
            self._timer_sub.configure(text="Okunuyor…", text_color=COLORS["green"])
            self._tick()
        else:
            # Already running – button acts as resume-from-paused
            pass

    def _toggle_pause(self):
        if not self._running:
            return
        if not self._paused:
            # Pause
            self._accumulated += int((datetime.now() - self._start_time).total_seconds())
            self._paused      = True
            self._pause_btn.configure(text="▶  Devam")
            self._timer_sub.configure(text="Duraklatıldı", text_color=COLORS["yellow"])
        else:
            # Resume
            self._start_time = datetime.now()
            self._paused     = False
            self._pause_btn.configure(text="⏸  Duraklat")
            self._timer_sub.configure(text="Okunuyor…", text_color=COLORS["green"])
            self._tick()

    def _stop_timer(self):
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
        total = self._elapsed()
        self._running     = False
        self._paused      = False
        self._accumulated = 0
        self._start_time  = None

        self._start_btn.configure(text="▶  Başlat", fg_color=COLORS["green"])
        self._pause_btn.configure(state="disabled",
                                   text="⏸  Duraklat", text_color=COLORS["text_muted"])
        self._stop_btn.configure( state="disabled",  text_color=COLORS["text_muted"])
        self._timer_lbl.configure(text="00:00")
        self._timer_sub.configure(text="Hazır", text_color=COLORS["text_muted"])

        if total >= 10:
            self._save_session_dialog(total)

    def _tick(self):
        if not self._running or self._paused:
            return
        elapsed = self._elapsed()
        self._timer_lbl.configure(text=format_duration_short(elapsed))
        self._after_id = self.after(1000, self._tick)

    # ── Session save dialog ────────────────────────────────────────────────

    def _save_session_dialog(self, total_seconds: int):
        book = self._selected_book
        note = self._note_entry.get().strip()
        self._note_entry.delete(0, "end")

        win = ctk.CTkToplevel(self)
        win.title("Seans Kaydet")
        win.geometry("400x360")
        win.resizable(False, False)
        win.configure(fg_color=COLORS["surface"])
        win.grab_set()

        ctk.CTkLabel(win, text="Seans Tamamlandı! 🎉",
                     font=("Georgia", 16, "bold"),
                     text_color=COLORS["text"]).pack(pady=(20, 4))
        ctk.CTkLabel(win, text=f"Süre: {format_duration(total_seconds)}",
                     font=("Helvetica", 12), text_color=COLORS["accent"]).pack()

        # Pages
        page_frame = ctk.CTkFrame(win, fg_color="transparent")
        page_frame.pack(pady=16)
        ctk.CTkLabel(page_frame, text="Başlangıç sayfası:",
                     font=("Helvetica", 11), text_color=COLORS["text_muted"]
                     ).grid(row=0, column=0, padx=8, sticky="e")
        start_var = ctk.StringVar(value=str(book["current_page"]))
        ctk.CTkEntry(page_frame, textvariable=start_var, width=80,
                     fg_color=COLORS["card"], border_color=COLORS["border"],
                     text_color=COLORS["text"]
                     ).grid(row=0, column=1, padx=4)
        ctk.CTkLabel(page_frame, text="Bitiş sayfası:",
                     font=("Helvetica", 11), text_color=COLORS["text_muted"]
                     ).grid(row=1, column=0, padx=8, pady=(8, 0), sticky="e")
        end_var = ctk.StringVar(value=str(book["current_page"]))
        ctk.CTkEntry(page_frame, textvariable=end_var, width=80,
                     fg_color=COLORS["card"], border_color=COLORS["border"],
                     text_color=COLORS["text"]
                     ).grid(row=1, column=1, padx=4, pady=(8, 0))

        ctk.CTkLabel(win, text="Not:",
                     font=("Helvetica", 11), text_color=COLORS["text_muted"]
                     ).pack(anchor="w", padx=24)
        note_ent = ctk.CTkEntry(win, placeholder_text="Seans notu…",
                                fg_color=COLORS["card"], border_color=COLORS["border"],
                                text_color=COLORS["text"])
        if note:
            note_ent.insert(0, note)
        note_ent.pack(fill="x", padx=24, pady=(4, 12))

        def save():
            try:
                sp = int(start_var.get() or 0)
                ep = int(end_var.get()   or 0)
                pages_read = max(0, ep - sp)
            except ValueError:
                sp, ep, pages_read = 0, 0, 0
            self._db.add_session({
                "book_id":          book["id"],
                "date":             date.today().strftime("%Y-%m-%d"),
                "duration_seconds": total_seconds,
                "pages_read":       pages_read,
                "start_page":       sp,
                "end_page":         ep,
                "notes":            note_ent.get().strip(),
            })
            # Update book current_page
            if ep > book["current_page"]:
                update = {"current_page": ep}
                if ep >= book["total_pages"] and book["total_pages"]:
                    update["status"] = "read"
                    from datetime import date as dt
                    update["end_date"] = dt.today().strftime("%Y-%m-%d")
                self._db.update_book(book["id"], update)
            win.destroy()
            self._refresh_history()
            self._load_books()

        ctk.CTkButton(win, text="💾  Kaydet",
                      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                      text_color=COLORS["bg"], corner_radius=8, height=38,
                      font=("Helvetica", 13, "bold"), command=save
                      ).pack(padx=24, pady=(0, 8), fill="x")
        ctk.CTkButton(win, text="İptal",
                      fg_color="transparent", hover_color=COLORS["card"],
                      text_color=COLORS["text_muted"], corner_radius=8, height=32,
                      command=win.destroy
                      ).pack(padx=24, fill="x")

    # ── Manual session ─────────────────────────────────────────────────────

    def _manual_session(self):
        if not self._selected_book:
            self._flash_error("Önce bir kitap seçin.")
            return
        book = self._selected_book

        win = ctk.CTkToplevel(self)
        win.title("Manuel Seans")
        win.geometry("380x400")
        win.configure(fg_color=COLORS["surface"])
        win.grab_set()

        ctk.CTkLabel(win, text="Manuel Okuma Seansı",
                     font=("Georgia", 15, "bold"),
                     text_color=COLORS["text"]).pack(pady=(20, 16))

        fields = ctk.CTkFrame(win, fg_color="transparent")
        fields.pack(fill="x", padx=24)

        def row(lbl, placeholder, val=""):
            ctk.CTkLabel(fields, text=lbl, font=("Helvetica", 11),
                         text_color=COLORS["text_muted"]).pack(anchor="w")
            e = ctk.CTkEntry(fields, placeholder_text=placeholder,
                             fg_color=COLORS["card"], border_color=COLORS["border"],
                             text_color=COLORS["text"], height=34)
            if val:
                e.insert(0, val)
            e.pack(fill="x", pady=(2, 10))
            return e

        date_e = row("Tarih (YYYY-MM-DD)", "2024-01-15", date.today().strftime("%Y-%m-%d"))
        dur_e  = row("Süre (dakika)", "30")
        sp_e   = row("Başlangıç sayfası", str(book["current_page"]))
        ep_e   = row("Bitiş sayfası",     str(book["current_page"]))
        note_e = row("Not", "Seans notu…")

        def save():
            try:
                minutes = int(dur_e.get() or 0)
                sp = int(sp_e.get() or 0)
                ep = int(ep_e.get() or 0)
            except ValueError:
                minutes = sp = ep = 0
            self._db.add_session({
                "book_id":          book["id"],
                "date":             date_e.get().strip() or date.today().strftime("%Y-%m-%d"),
                "duration_seconds": minutes * 60,
                "pages_read":       max(0, ep - sp),
                "start_page":       sp,
                "end_page":         ep,
                "notes":            note_e.get().strip(),
            })
            if ep > book["current_page"]:
                self._db.update_book(book["id"], {"current_page": ep})
            win.destroy()
            self._refresh_history()

        ctk.CTkButton(win, text="💾  Kaydet",
                      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                      text_color=COLORS["bg"], corner_radius=8, height=38,
                      font=("Helvetica", 13, "bold"), command=save
                      ).pack(padx=24, pady=8, fill="x")

    # ── History ────────────────────────────────────────────────────────────

    def _refresh_history(self):
        for w in self._history_scroll.winfo_children():
            w.destroy()

        if not self._selected_book:
            ctk.CTkLabel(
                self._history_scroll,
                text="Bir kitap seçerek\nseans geçmişini görün.",
                font=("Helvetica", 12), text_color=COLORS["text_dim"],
            ).pack(pady=40)
            return

        sessions = self._db.get_sessions_for_book(self._selected_book["id"])
        if not sessions:
            ctk.CTkLabel(self._history_scroll,
                         text="Henüz seans kaydı yok.",
                         font=("Helvetica", 12), text_color=COLORS["text_dim"]
                         ).pack(pady=40)
            return

        for s in sessions:
            self._session_row(s).pack(fill="x", pady=(0, 6))

    def _session_row(self, session) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self._history_scroll,
                             fg_color=COLORS["card"], corner_radius=8)
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text=session["date"],
                     font=("Helvetica", 11, "bold"),
                     text_color=COLORS["accent"]).grid(
            row=0, column=0, padx=10, pady=(8, 0), sticky="w")

        dur = format_duration(session["duration_seconds"])
        ctk.CTkLabel(frame,
                     text=f"{dur}  ·  {session['pages_read']} sayfa",
                     font=("Helvetica", 11), text_color=COLORS["text"]
                     ).grid(row=1, column=0, padx=10, pady=(0, 8), sticky="w")

        if session["notes"]:
            ctk.CTkLabel(frame, text=session["notes"][:50],
                         font=("Helvetica", 10), text_color=COLORS["text_muted"]
                         ).grid(row=0, column=1, rowspan=2, padx=8, sticky="w")

        sid = session["id"]
        ctk.CTkButton(
            frame, text="✕", width=26, height=26,
            fg_color="transparent", hover_color=COLORS["red_dark"],
            text_color=COLORS["text_dim"], corner_radius=4,
            command=lambda s=sid: self._del_session(s),
        ).grid(row=0, column=2, rowspan=2, padx=8)
        return frame

    def _del_session(self, sid):
        self._db.delete_session(sid)
        self._refresh_history()

    def _flash_error(self, msg: str):
        self._timer_sub.configure(text=msg, text_color=COLORS["red"])
        self.after(2500, lambda: self._timer_sub.configure(
            text="Hazır", text_color=COLORS["text_muted"]
        ))
