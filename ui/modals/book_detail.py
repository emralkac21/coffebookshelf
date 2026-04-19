import customtkinter as ctk
import tkinter.messagebox as mb
from database.db_manager import get_db
from utils.constants import COLORS, GENRES, STATUS_LABELS
from utils.helpers import load_or_generate_cover, progress_percent, format_duration
from ui.components.star_rating import StarRating


class BookDetailModal(ctk.CTkToplevel):
    def __init__(self, parent, book_id: int, on_saved=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._db       = get_db()
        self._book_id  = book_id
        self._on_saved = on_saved
        self._book     = self._db.get_book(book_id)
        if not self._book:
            self.destroy()
            return

        self.title(f"Kitap Detayı: {self._book['title'][:40]}")
        self.geometry("940x700")
        self.resizable(True, True)
        self.configure(fg_color=COLORS["surface"])
        self._build()

    def _build(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ── Left: Cover + quick info ──────────────────────────────────────
        left = ctk.CTkScrollableFrame(
            self, width=260, fg_color=COLORS["bg"], corner_radius=0,
            scrollbar_button_color=COLORS["border"],
        )
        left.grid(row=0, column=0, sticky="nsew")

        b = self._book
        img = load_or_generate_cover(b["cover_path"], b["title"], b["author"], (200, 300))
        ctk.CTkLabel(left, image=img, text="").pack(padx=16, pady=(20, 10))

        ctk.CTkLabel(left, text=b["title"],
                     font=("Georgia", 14, "bold"),
                     text_color=COLORS["text"], wraplength=220,
                     justify="center").pack(padx=12)
        ctk.CTkLabel(left, text=b["author"] or "—",
                     font=("Helvetica", 11), text_color=COLORS["text_muted"],
                     wraplength=220, justify="center").pack(padx=12, pady=(2, 4))

        if b["genre"]:
            ctk.CTkLabel(left, text=b["genre"],
                         font=("Helvetica", 10),
                         fg_color=COLORS["card"],
                         text_color=COLORS["text_muted"],
                         corner_radius=6, padx=8, pady=3,
                         ).pack(pady=2)

        ctk.CTkFrame(left, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=16, pady=10)

        # Rating
        ctk.CTkLabel(left, text="Puanlama", font=("Helvetica", 10),
                     text_color=COLORS["text_muted"]).pack(anchor="w", padx=16)
        self._star = StarRating(left, initial=b["rating"],
                                on_change=self._on_rating,
                                bg=COLORS["bg"], star_size=22)
        self._star.pack(anchor="w", padx=16, pady=(2, 10))

        # Quick stats
        sessions = self._db.get_sessions_for_book(self._book_id)
        total_s  = sum(s["duration_seconds"] for s in sessions)
        total_pg = sum(s["pages_read"]       for s in sessions)

        for lbl, val in [
            ("Toplam Seans", str(len(sessions))),
            ("Toplam Süre",  format_duration(total_s)),
            ("Okunan Sayfa", str(total_pg)),
            ("Eklenme",      b["added_date"] or "—"),
            ("Başlangıç",    b["start_date"] or "—"),
            ("Bitiş",        b["end_date"]   or "—"),
        ]:
            row = ctk.CTkFrame(left, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=1)
            ctk.CTkLabel(row, text=lbl, font=("Helvetica", 10),
                         text_color=COLORS["text_dim"]).pack(side="left")
            ctk.CTkLabel(row, text=val, font=("Helvetica", 10),
                         text_color=COLORS["text_muted"]).pack(side="right")

        ctk.CTkFrame(left, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=16, pady=10)

        # Action buttons
        ctk.CTkButton(left, text="✏️  Düzenle",
                      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                      text_color=COLORS["bg"], corner_radius=8, height=34,
                      command=self._open_edit,
                      ).pack(fill="x", padx=16, pady=2)
        ctk.CTkButton(left, text="⏱  Timer Başlat",
                      fg_color=COLORS["green"], hover_color=COLORS["green_dark"],
                      text_color="white", corner_radius=8, height=34,
                      command=self._start_timer,
                      ).pack(fill="x", padx=16, pady=2)
        ctk.CTkButton(left, text="🗑  Sil",
                      fg_color="transparent", hover_color=COLORS["red_dark"],
                      text_color=COLORS["text_dim"], border_color=COLORS["border"],
                      border_width=1, corner_radius=8, height=32,
                      command=self._delete_book,
                      ).pack(fill="x", padx=16, pady=(2, 20))

        # ── Right: Tabbed content ──────────────────────────────────────────
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=0)
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        # Tab bar
        tab_bar = ctk.CTkFrame(right, fg_color=COLORS["bg"], corner_radius=0)
        tab_bar.grid(row=0, column=0, sticky="ew")

        self._tab_btns   = {}
        self._tab_frames = {}
        self._active_tab = ctk.StringVar(value="progress")

        for key, label in [("progress", "📊 İlerleme"),
                            ("sessions", "📋 Seanslar"),
                            ("notes",    "📝 Notlar"),
                            ("quotes",   "💬 Alıntılar")]:
            btn = ctk.CTkButton(
                tab_bar, text=label,
                font=("Helvetica", 12),
                fg_color="transparent",
                hover_color=COLORS["card"],
                text_color=COLORS["text_muted"],
                corner_radius=0, height=40,
                command=lambda k=key: self._show_tab(k),
            )
            btn.pack(side="left", padx=4, pady=6)
            self._tab_btns[key] = btn

        # Tab content area
        content = ctk.CTkFrame(right, fg_color=COLORS["bg"], corner_radius=0)
        content.grid(row=1, column=0, sticky="nsew")
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)
        self._content_area = content

        self._build_progress_tab()
        self._build_sessions_tab()
        self._build_notes_tab()
        self._build_quotes_tab()

        self._show_tab("progress")

    # ── Tabs ──────────────────────────────────────────────────────────────────

    def _show_tab(self, key: str):
        for k, f in self._tab_frames.items():
            f.grid_remove()
        for k, b in self._tab_btns.items():
            b.configure(fg_color="transparent", text_color=COLORS["text_muted"],
                        font=("Helvetica", 12))
        if key in self._tab_frames:
            self._tab_frames[key].grid(row=0, column=0, sticky="nsew")
        self._tab_btns[key].configure(
            fg_color=COLORS["card"],
            text_color=COLORS["accent"],
            font=("Helvetica", 12, "bold"),
        )
        self._active_tab.set(key)

    # ── Progress Tab ──────────────────────────────────────────────────────────

    def _build_progress_tab(self):
        f = ctk.CTkScrollableFrame(
            self._content_area, fg_color=COLORS["bg"],
            scrollbar_button_color=COLORS["border"],
        )
        self._tab_frames["progress"] = f
        b = self._book

        ctk.CTkLabel(f, text="Okuma İlerlemesi",
                     font=("Georgia", 15, "bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(16, 12))

        # Progress slider
        pct = progress_percent(b["current_page"], b["total_pages"])
        prog_frame = ctk.CTkFrame(f, fg_color=COLORS["card"], corner_radius=10)
        prog_frame.pack(fill="x", padx=20, pady=(0, 14))

        top_row = ctk.CTkFrame(prog_frame, fg_color="transparent")
        top_row.pack(fill="x", padx=14, pady=(12, 6))
        ctk.CTkLabel(top_row, text="Mevcut Sayfa",
                     font=("Helvetica", 11), text_color=COLORS["text_muted"]
                     ).pack(side="left")
        self._pct_lbl = ctk.CTkLabel(
            top_row,
            text=f"{b['current_page']} / {b['total_pages'] or '?'}  ({pct:.0f}%)",
            font=("Helvetica", 12, "bold"), text_color=COLORS["accent"])
        self._pct_lbl.pack(side="right")

        bar = ctk.CTkProgressBar(prog_frame, height=10, corner_radius=5,
                                  progress_color=COLORS["green"],
                                  fg_color=COLORS["border"])
        bar.pack(fill="x", padx=14, pady=(0, 8))
        bar.set(pct / 100)

        # Current page entry + update
        inp_row = ctk.CTkFrame(prog_frame, fg_color="transparent")
        inp_row.pack(fill="x", padx=14, pady=(0, 12))
        self._cur_page_var = ctk.StringVar(value=str(b["current_page"]))
        ctk.CTkEntry(inp_row, textvariable=self._cur_page_var,
                     fg_color=COLORS["surface"], border_color=COLORS["border"],
                     text_color=COLORS["text"], height=32, width=100,
                     ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(inp_row, text="Güncelle",
                      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                      text_color=COLORS["bg"], height=32, corner_radius=8,
                      command=self._update_progress,
                      ).pack(side="left")

        # Status & dates
        meta_card = ctk.CTkFrame(f, fg_color=COLORS["card"], corner_radius=10)
        meta_card.pack(fill="x", padx=20, pady=(0, 14))
        meta_card.grid_columnconfigure(1, weight=1)
        meta_card.grid_columnconfigure(3, weight=1)

        from utils.constants import STATUS_KEYS_FROM_LABEL
        ctk.CTkLabel(meta_card, text="Durum", font=("Helvetica", 10),
                     text_color=COLORS["text_muted"]
                     ).grid(row=0, column=0, padx=(14, 4), pady=(12, 2), sticky="w")
        self._status_var2 = ctk.StringVar(
            value=STATUS_LABELS.get(b["status"], b["status"]))
        ctk.CTkOptionMenu(meta_card, values=list(STATUS_LABELS.values()),
                          variable=self._status_var2,
                          fg_color=COLORS["surface"],
                          button_color=COLORS["border"],
                          button_hover_color=COLORS["border_light"],
                          text_color=COLORS["text"], height=30, width=160,
                          ).grid(row=1, column=0, padx=(14, 8), pady=(0, 12))

        for col, (lbl, key) in enumerate([("Başlangıç", "start_date"),
                                           ("Bitiş",     "end_date")], start=1):
            ctk.CTkLabel(meta_card, text=lbl, font=("Helvetica", 10),
                         text_color=COLORS["text_muted"]
                         ).grid(row=0, column=col, padx=(0, 4), pady=(12, 2), sticky="w")
            var = ctk.StringVar(value=b[key] or "")
            e = ctk.CTkEntry(meta_card, textvariable=var,
                             fg_color=COLORS["surface"], border_color=COLORS["border"],
                             text_color=COLORS["text"], height=30, width=120,
                             placeholder_text="YYYY-MM-DD")
            e.grid(row=1, column=col, padx=(0, 8), pady=(0, 12))
            setattr(self, f"_{key}_var", var)

        ctk.CTkButton(meta_card, text="💾 Bilgileri Kaydet",
                      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                      text_color=COLORS["bg"], height=30, corner_radius=8,
                      command=self._save_meta,
                      ).grid(row=1, column=3, padx=(0, 14), pady=(0, 12))

    # ── Sessions Tab ──────────────────────────────────────────────────────────

    def _build_sessions_tab(self):
        f = ctk.CTkScrollableFrame(
            self._content_area, fg_color=COLORS["bg"],
            scrollbar_button_color=COLORS["border"],
        )
        self._tab_frames["sessions"] = f

        ctk.CTkLabel(f, text="Okuma Seansları",
                     font=("Georgia", 15, "bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(16, 12))

        sessions = self._db.get_sessions_for_book(self._book_id)
        if not sessions:
            ctk.CTkLabel(f, text="Henüz seans kaydı yok.",
                         font=("Helvetica", 12), text_color=COLORS["text_dim"]
                         ).pack(anchor="w", padx=20)
            return

        # Header
        hdr = ctk.CTkFrame(f, fg_color=COLORS["surface"], corner_radius=8)
        hdr.pack(fill="x", padx=20, pady=(0, 4))
        for col, (lbl, w) in enumerate([("Tarih", 100), ("Süre", 90),
                                         ("Sayfa", 80), ("Not", 0)]):
            ctk.CTkLabel(hdr, text=lbl, font=("Helvetica", 10, "bold"),
                         text_color=COLORS["text_muted"], width=w, anchor="w"
                         ).grid(row=0, column=col, padx=8, pady=6, sticky="w")

        for s in sessions:
            row = ctk.CTkFrame(f, fg_color=COLORS["card"], corner_radius=8)
            row.pack(fill="x", padx=20, pady=(0, 4))
            row.grid_columnconfigure(3, weight=1)
            ctk.CTkLabel(row, text=s["date"], font=("Helvetica", 11),
                         text_color=COLORS["text"], width=100, anchor="w"
                         ).grid(row=0, column=0, padx=8, pady=6)
            ctk.CTkLabel(row, text=format_duration(s["duration_seconds"]),
                         font=("Helvetica", 11), text_color=COLORS["blue"],
                         width=90, anchor="w"
                         ).grid(row=0, column=1, padx=8)
            pages_txt = (f"{s['start_page']}→{s['end_page']}"
                         if s["start_page"] else str(s["pages_read"]))
            ctk.CTkLabel(row, text=pages_txt, font=("Helvetica", 11),
                         text_color=COLORS["green"], width=80, anchor="w"
                         ).grid(row=0, column=2, padx=8)
            if s["notes"]:
                ctk.CTkLabel(row, text=s["notes"][:60], font=("Helvetica", 10),
                             text_color=COLORS["text_muted"], anchor="w"
                             ).grid(row=0, column=3, padx=8, sticky="ew")
            sid = s["id"]
            ctk.CTkButton(row, text="✕", width=24, height=24,
                          fg_color="transparent", hover_color=COLORS["red_dark"],
                          text_color=COLORS["text_dim"], corner_radius=4,
                          command=lambda s=sid: self._del_session(s, f),
                          ).grid(row=0, column=4, padx=8)

    # ── Notes Tab ─────────────────────────────────────────────────────────────

    def _build_notes_tab(self):
        f = ctk.CTkScrollableFrame(
            self._content_area, fg_color=COLORS["bg"],
            scrollbar_button_color=COLORS["border"],
        )
        self._tab_frames["notes"] = f

        ctk.CTkLabel(f, text="Notlar",
                     font=("Georgia", 15, "bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(16, 8))

        self._notes_box = ctk.CTkTextbox(
            f, height=320,
            fg_color=COLORS["card"], border_color=COLORS["border"],
            text_color=COLORS["text"], font=("Helvetica", 12),
        )
        self._notes_box.pack(fill="x", padx=20, pady=(0, 10))
        if self._book["notes"]:
            self._notes_box.insert("1.0", self._book["notes"])

        ctk.CTkButton(f, text="💾  Notu Kaydet",
                      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                      text_color=COLORS["bg"], corner_radius=8, height=36,
                      command=self._save_notes,
                      ).pack(anchor="w", padx=20)

    # ── Quotes Tab ────────────────────────────────────────────────────────────

    def _build_quotes_tab(self):
        f = ctk.CTkFrame(self._content_area, fg_color=COLORS["bg"], corner_radius=0)
        f.grid_rowconfigure(1, weight=1)
        f.grid_columnconfigure(0, weight=1)
        self._tab_frames["quotes"] = f

        hdr = ctk.CTkFrame(f, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=20, pady=(14, 8))

        ctk.CTkLabel(hdr, text="Alıntılar",
                     font=("Georgia", 15, "bold"),
                     text_color=COLORS["text"]).pack(side="left")

        # Add quote mini-form
        add_f = ctk.CTkFrame(hdr, fg_color=COLORS["card"], corner_radius=8)
        add_f.pack(side="right")
        self._new_quote = ctk.CTkEntry(add_f,
                                        placeholder_text="Yeni alıntı…",
                                        fg_color=COLORS["surface"],
                                        border_color=COLORS["border"],
                                        text_color=COLORS["text"],
                                        height=30, width=260)
        self._new_quote.pack(side="left", padx=6, pady=6)
        self._new_quote_pg = ctk.CTkEntry(add_f,
                                           placeholder_text="Sf.",
                                           fg_color=COLORS["surface"],
                                           border_color=COLORS["border"],
                                           text_color=COLORS["text"],
                                           height=30, width=50)
        self._new_quote_pg.pack(side="left", padx=(0, 4), pady=6)
        ctk.CTkButton(add_f, text="＋", width=30, height=30,
                      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                      text_color=COLORS["bg"], corner_radius=6,
                      command=lambda: self._add_quote(f),
                      ).pack(side="left", padx=(0, 6), pady=6)

        # Quotes list
        self._quotes_scroll = ctk.CTkScrollableFrame(
            f, fg_color=COLORS["bg"],
            scrollbar_button_color=COLORS["border"],
        )
        self._quotes_scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        self._reload_quotes()

    # ── actions ───────────────────────────────────────────────────────────────

    def _on_rating(self, val):
        self._db.update_book(self._book_id, {"rating": val})

    def _update_progress(self):
        try:
            page = int(self._cur_page_var.get() or 0)
        except ValueError:
            return
        upd = {"current_page": page}
        if self._book["total_pages"] and page >= self._book["total_pages"]:
            upd["status"] = "read"
            from datetime import date
            upd["end_date"] = date.today().strftime("%Y-%m-%d")
        self._db.update_book(self._book_id, upd)
        self._book = self._db.get_book(self._book_id)
        pct = progress_percent(page, self._book["total_pages"])
        self._pct_lbl.configure(
            text=f"{page} / {self._book['total_pages'] or '?'}  ({pct:.0f}%)")
        if self._on_saved:
            self._on_saved()

    def _save_meta(self):
        from utils.constants import STATUS_KEYS_FROM_LABEL
        upd = {
            "status":     STATUS_KEYS_FROM_LABEL.get(self._status_var2.get(), "to_read"),
            "start_date": self._start_date_var.get().strip(),
            "end_date":   self._end_date_var.get().strip(),
        }
        self._db.update_book(self._book_id, upd)
        if self._on_saved:
            self._on_saved()

    def _save_notes(self):
        notes = self._notes_box.get("1.0", "end").strip()
        self._db.update_book(self._book_id, {"notes": notes})

    def _add_quote(self, parent):
        text = self._new_quote.get().strip()
        if not text:
            return
        try:
            pg = int(self._new_quote_pg.get() or 0)
        except ValueError:
            pg = 0
        self._db.add_quote(self._book_id, text, pg)
        self._new_quote.delete(0, "end")
        self._new_quote_pg.delete(0, "end")
        self._reload_quotes()

    def _reload_quotes(self):
        for w in self._quotes_scroll.winfo_children():
            w.destroy()
        quotes = self._db.get_quotes(self._book_id)
        if not quotes:
            ctk.CTkLabel(self._quotes_scroll,
                         text="Henüz alıntı eklenmedi.",
                         font=("Helvetica", 12), text_color=COLORS["text_dim"]
                         ).pack(pady=30)
            return
        for q in quotes:
            qf = ctk.CTkFrame(self._quotes_scroll,
                              fg_color=COLORS["card"], corner_radius=8)
            qf.pack(fill="x", pady=(0, 6))
            qf.grid_columnconfigure(0, weight=1)
            pg_txt = f"sf. {q['page']}" if q["page"] else ""
            ctk.CTkLabel(qf, text=f"❝  {q['quote']}",
                         font=("Georgia", 12, "italic"),
                         text_color=COLORS["text"], wraplength=460,
                         justify="left", anchor="w"
                         ).grid(row=0, column=0, padx=12, pady=(10, 2), sticky="ew")
            ctk.CTkLabel(qf, text=f"{pg_txt}  {q['added_date']}",
                         font=("Helvetica", 10), text_color=COLORS["text_dim"],
                         anchor="w"
                         ).grid(row=1, column=0, padx=14, pady=(0, 8), sticky="w")
            qid = q["id"]
            ctk.CTkButton(qf, text="✕", width=24, height=24,
                          fg_color="transparent", hover_color=COLORS["red_dark"],
                          text_color=COLORS["text_dim"], corner_radius=4,
                          command=lambda i=qid: self._del_quote(i),
                          ).grid(row=0, column=1, rowspan=2, padx=8)

    def _del_session(self, sid, parent_frame):
        self._db.delete_session(sid)
        self._tab_frames["sessions"] = None
        self._build_sessions_tab()
        self._show_tab("sessions")

    def _del_quote(self, qid):
        self._db.delete_quote(qid)
        self._reload_quotes()

    def _open_edit(self):
        from ui.modals.add_book import AddBookModal
        b = dict(self._book)
        b["cover_url"] = ""
        modal = AddBookModal(self, prefill=b, on_saved=self._on_edit_saved)
        modal.grab_set()

    def _on_edit_saved(self):
        self._book = self._db.get_book(self._book_id)
        if self._on_saved:
            self._on_saved()

    def _start_timer(self):
        self.destroy()
        self.master._app.navigate("timer", book_id=self._book_id)

    def _delete_book(self):
        if mb.askyesno("Sil", f"'{self._book['title']}' silinsin mi?\n"
                               "Tüm seanslar ve alıntılar da silinecek."):
            self._db.delete_book(self._book_id)
            if self._on_saved:
                self._on_saved()
            self.destroy()
