import customtkinter as ctk
import os
import tkinter.messagebox as mb
from services.book_search import search_by_isbn, search_by_title
from services.cover_downloader import download_cover
from database.db_manager import get_db
from utils.constants import COLORS, GENRES, STATUS_LABELS
from utils.helpers import load_or_generate_cover


class AddBookModal(ctk.CTkToplevel):
    def __init__(self, parent, on_saved=None, prefill: dict = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.title("Kitap Ekle")
        
        # --- GÜVENLİ İKON YÜKLEME (ALT KLASÖR İÇİN) ---
        # 1. Mevcut dosyanın yolunu al (ui/models/)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 2. İki kat yukarı çık (ui/models/ -> ui/ -> bookshelf_app/)
        # ve sonra assets/favicon.ico yoluna gir
        icon_path = os.path.join(current_dir, "..", "..", "assets", "favicon.ico")
        
        # Yolu normalize ederek temizle (karışık ../.. ifadelerini düzeltir)
        icon_path = os.path.normpath(icon_path)

        if os.path.exists(icon_path):
            try:
                # Pencere tamamen hazır olduğunda ikonu basmak en güvenli yoldur
                self.after(200, lambda: self.wm_iconbitmap(icon_path))
            except Exception as e:
                print(f"İkon yükleme hatası: {e}")
        else:
            # Hata ayıklama için terminale bak:
            print(f"UYARI: İkon dosyası bulunamadı!")
            print(f"Aranan Tam Yol: {icon_path}")
        # ----------------------------
        self.geometry("780x680")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["surface"])
        self._db       = get_db()
        self._on_saved = on_saved
        self._cover_url = ""
        self._prefill   = prefill or {}
        self._build()
        if prefill:
            self._fill_fields(prefill)

    def _build(self):
        # Title
        ctk.CTkLabel(self, text="Kitap Ekle",
                     font=("Georgia", 18, "bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=24, pady=(20, 4))
        ctk.CTkFrame(self, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=24)

        # ISBN search bar
        isbn_row = ctk.CTkFrame(self, fg_color="transparent")
        isbn_row.pack(fill="x", padx=24, pady=(14, 10))
        ctk.CTkLabel(isbn_row, text="ISBN veya Başlık ile Ara:",
                     font=("Helvetica", 11), text_color=COLORS["text_muted"]
                     ).pack(side="left")
        self._isbn_var = ctk.StringVar()
        ctk.CTkEntry(isbn_row, textvariable=self._isbn_var,
                     placeholder_text="ISBN-13 veya kitap adı...",
                     fg_color=COLORS["card"], border_color=COLORS["border"],
                     text_color=COLORS["text"], height=34, width=310,
                     ).pack(side="left", padx=10)
        self._search_btn = ctk.CTkButton(isbn_row, text="🔍  Ara",
                                          fg_color=COLORS["accent"],
                                          hover_color=COLORS["accent_hover"],
                                          text_color=COLORS["bg"],
                                          corner_radius=8, height=34, width=90,
                                          command=self._do_search)
        self._search_btn.pack(side="left")
        self._search_status = ctk.CTkLabel(isbn_row, text="",
                                            font=("Helvetica", 10),
                                            text_color=COLORS["text_muted"])
        self._search_status.pack(side="left", padx=10)

        # Search results listbox
        self._results_frame = ctk.CTkFrame(self, fg_color="transparent", height=0)
        self._results_frame.pack(fill="x", padx=24)

        # Main form (two columns: cover | fields)
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=24, pady=(10, 0))
        form.grid_columnconfigure(1, weight=1)

        # Cover preview
        self._cover_lbl = ctk.CTkLabel(form, text="", image=None)
        self._cover_lbl.grid(row=0, column=0, rowspan=10, padx=(0, 20), pady=0, sticky="n")
        self._refresh_cover_preview("", "", "")

        # Fields
        fields = ctk.CTkFrame(form, fg_color="transparent")
        fields.grid(row=0, column=1, sticky="nsew")
        fields.grid_columnconfigure(0, weight=1)
        fields.grid_columnconfigure(1, weight=1)

        def entry(parent, label, row, col=0, colspan=1, placeholder="", var=None):
            ctk.CTkLabel(parent, text=label, font=("Helvetica", 10),
                         text_color=COLORS["text_muted"]
                         ).grid(row=row*2, column=col, columnspan=colspan,
                                sticky="w", pady=(8, 2))
            v = var or ctk.StringVar()
            e = ctk.CTkEntry(parent, textvariable=v,
                             placeholder_text=placeholder,
                             fg_color=COLORS["card"], border_color=COLORS["border"],
                             text_color=COLORS["text"], height=34)
            e.grid(row=row*2+1, column=col, columnspan=colspan, sticky="ew",
                   padx=(0, 8 if col == 0 and colspan == 1 else 0))
            return v

        self._title_var   = entry(fields, "Başlık *", 0, 0, 2, "Kitap adı...")
        self._author_var  = entry(fields, "Yazar",    1, 0, 1, "Yazar adı")
        self._isbn_f_var  = entry(fields, "ISBN",     1, 1, 1, "978-…")
        self._pages_var   = entry(fields, "Toplam Sayfa", 2, 0, 1, "300")
        self._year_var    = entry(fields, "Yayın Yılı",   2, 1, 1, "2024")
        self._pub_var     = entry(fields, "Yayınevi",     3, 0, 1, "Yayınevi")

        # Genre
        ctk.CTkLabel(fields, text="Tür", font=("Helvetica", 10),
                     text_color=COLORS["text_muted"]
                     ).grid(row=7, column=1, sticky="w", pady=(8, 2))
        self._genre_var = ctk.StringVar(value="Diğer")
        ctk.CTkOptionMenu(fields, values=GENRES[1:],  # skip "Tümü"
                          variable=self._genre_var,
                          fg_color=COLORS["card"], button_color=COLORS["border"],
                          button_hover_color=COLORS["border_light"],
                          text_color=COLORS["text"], height=34,
                          ).grid(row=8, column=1, sticky="ew")

        # Status
        ctk.CTkLabel(fields, text="Durum", font=("Helvetica", 10),
                     text_color=COLORS["text_muted"]
                     ).grid(row=9, column=0, sticky="w", pady=(8, 2))
        self._status_var = ctk.StringVar(value="Okunacak")
        ctk.CTkOptionMenu(fields, values=list(STATUS_LABELS.values()),
                          variable=self._status_var,
                          fg_color=COLORS["card"], button_color=COLORS["border"],
                          button_hover_color=COLORS["border_light"],
                          text_color=COLORS["text"], height=34,
                          ).grid(row=10, column=0, sticky="ew", padx=(0, 8))

        # Notes
        ctk.CTkLabel(fields, text="Notlar", font=("Helvetica", 10),
                     text_color=COLORS["text_muted"]
                     ).grid(row=11, column=0, columnspan=2, sticky="w", pady=(8, 2))
        self._notes_entry = ctk.CTkEntry(fields,
                                          fg_color=COLORS["card"],
                                          border_color=COLORS["border"],
                                          text_color=COLORS["text"], height=34)
        self._notes_entry.grid(row=12, column=0, columnspan=2, sticky="ew")

        # Buttons
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=(14, 20))
        ctk.CTkButton(btn_row, text="💾  Kaydet",
                      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                      text_color=COLORS["bg"], corner_radius=8, height=38,
                      font=("Helvetica", 13, "bold"), command=self._save
                      ).pack(side="right", padx=(8, 0))
        ctk.CTkButton(btn_row, text="İptal",
                      fg_color="transparent", hover_color=COLORS["card"],
                      text_color=COLORS["text_muted"], border_color=COLORS["border"],
                      border_width=1, corner_radius=8, height=38,
                      command=self.destroy
                      ).pack(side="right")

    # ── Cover preview ────────────────────────────────────────────────────────

    def _refresh_cover_preview(self, cover_path, title, author):
        img = load_or_generate_cover(cover_path, title or "?", author or "", (110, 165))
        self._cover_lbl.configure(image=img)
        self._cover_lbl.image = img

    # ── Search ────────────────────────────────────────────────────────────────

    def _do_search(self):
        q = self._isbn_var.get().strip()
        if not q:
            return
        self._search_btn.configure(state="disabled", text="⏳ Aranıyor…")
        self._search_status.configure(text="")

        for w in self._results_frame.winfo_children():
            w.destroy()

        # Decide ISBN vs title
        digits = q.replace("-", "").replace(" ", "")
        if digits.isdigit() and len(digits) in (10, 13):
            search_by_isbn(q, self._on_isbn_result)
        else:
            search_by_title(q, self._on_title_results)

    def _on_isbn_result(self, result):
        self.after(0, lambda: self._handle_isbn(result))

    def _handle_isbn(self, result):
        self._search_btn.configure(state="normal", text="🔍  Ara")
        if result:
            self._fill_fields(result)
            self._search_status.configure(
                text="✓ Bulundu!", text_color=COLORS["green"])
        else:
            self._search_status.configure(
                text="Bulunamadı.", text_color=COLORS["red"])

    def _on_title_results(self, results):
        self.after(0, lambda: self._show_title_results(results))

    def _show_title_results(self, results):
        self._search_btn.configure(state="normal", text="🔍  Ara")
        for w in self._results_frame.winfo_children():
            w.destroy()
        if not results:
            self._search_status.configure(text="Sonuç yok.", text_color=COLORS["red"])
            return
        self._search_status.configure(
            text=f"{len(results)} sonuç", text_color=COLORS["text_muted"])

        lst = ctk.CTkScrollableFrame(self._results_frame,
                                      fg_color=COLORS["card"],
                                      height=120, corner_radius=8)
        lst.pack(fill="x", pady=(0, 8))
        for r in results[:8]:
            title  = r.get("title", "—")[:55]
            author = r.get("author", "")[:30]
            text   = f"{title}  –  {author}"
            ctk.CTkButton(lst, text=text, anchor="w",
                          fg_color="transparent",
                          hover_color=COLORS["card_hover"],
                          text_color=COLORS["text"],
                          font=("Helvetica", 11), height=28,
                          command=lambda rd=r: self._pick_result(rd),
                          ).pack(fill="x", padx=4, pady=1)

    def _pick_result(self, data):
        self._fill_fields(data)
        for w in self._results_frame.winfo_children():
            w.destroy()

    # ── Fill form ─────────────────────────────────────────────────────────────

    def _fill_fields(self, data: dict):
        def _set(var, key):
            v = data.get(key, "")
            var.set(str(v) if v else "")

        _set(self._title_var,  "title")
        _set(self._author_var, "author")
        _set(self._isbn_f_var, "isbn")
        _set(self._pages_var,  "total_pages")
        _set(self._year_var,   "year_published")
        _set(self._pub_var,    "publisher")

        genre = data.get("genre", "")
        if genre:
            self._genre_var.set(genre)

        self._cover_url = data.get("cover_url", "")
        self._refresh_cover_preview(
            "", data.get("title", ""), data.get("author", ""))

        # Download cover in background for preview
        if self._cover_url:
            download_cover(self._cover_url, callback=self._on_cover_downloaded)

    def _on_cover_downloaded(self, path):
        if path:
            self._temp_cover_path = path
            self.after(0, lambda: self._refresh_cover_preview(
                path,
                self._title_var.get(),
                self._author_var.get()
            ))

    # ── Save ──────────────────────────────────────────────────────────────────

    def _save(self):
        title = self._title_var.get().strip()
        if not title:
            mb.showwarning("Uyarı", "Başlık zorunludur.")
            return

        from utils.constants import STATUS_KEYS_FROM_LABEL
        status_label = self._status_var.get()
        status = STATUS_KEYS_FROM_LABEL.get(status_label, "to_read")

        try:
            pages = int(self._pages_var.get() or 0)
        except ValueError:
            pages = 0
        try:
            year = int(self._year_var.get() or 0)
        except ValueError:
            year = 0

        data = {
            "title":          title,
            "author":         self._author_var.get().strip(),
            "isbn":           self._isbn_f_var.get().strip(),
            "genre":          self._genre_var.get(),
            "total_pages":    pages,
            "year_published": year,
            "publisher":      self._pub_var.get().strip(),
            "status":         status,
            "notes":          self._notes_entry.get().strip(),
            "cover_path":     getattr(self, "_temp_cover_path", ""),
        }
        book_id = self._db.add_book(data)

        # Download & save cover with book_id filename
        if self._cover_url and not data["cover_path"]:
            cover_path = download_cover(self._cover_url, book_id=book_id)
            if cover_path:
                self._db.update_book(book_id, {"cover_path": cover_path})
        elif data["cover_path"]:
            # Rename temp cover to book id
            import os, shutil
            dest = f"assets/covers/cover_{book_id}.jpg"
            try:
                shutil.copy2(data["cover_path"], dest)
                self._db.update_book(book_id, {"cover_path": dest})
            except Exception:
                pass

        if self._on_saved:
            self._on_saved()
        self.destroy()
