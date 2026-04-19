import customtkinter as ctk
from database.db_manager import get_db
from utils.constants import COLORS, GENRES, STATUS_LABELS
from ui.components.book_card import BookCard, BookListRow


ALL_STATUSES = ["Tümü"] + list(STATUS_LABELS.values())


class LibraryView(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg"])
        super().__init__(parent, **kwargs)
        self._app         = app
        self._db          = get_db()
        self._view_mode   = "grid"   # "grid" or "list"
        self._status_filter = "Tümü"
        self._genre_filter  = "Tümü"
        self._search_var  = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._reload_cards())
        self._build()

    def refresh(self):
        self._reload_cards()

    def _build(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._toolbar().grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))

        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg"],
            scrollbar_button_color=COLORS["border"],
        )
        self._scroll.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 20))

        self._reload_cards()

    def _toolbar(self) -> ctk.CTkFrame:
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid_columnconfigure(1, weight=1)

        # Title
        ctk.CTkLabel(bar, text="Kütüphanem",
                     font=("Georgia", 22, "bold"),
                     text_color=COLORS["text"]).grid(row=0, column=0, sticky="w")

        # Search
        search = ctk.CTkEntry(
            bar, placeholder_text="🔍  Başlık, yazar veya ISBN ara…",
            textvariable=self._search_var,
            fg_color=COLORS["surface"], border_color=COLORS["border"],
            text_color=COLORS["text"], height=36, width=260,
        )
        search.grid(row=0, column=1, padx=(16, 8), sticky="w")

        # Status filter
        self._status_var = ctk.StringVar(value="Tümü")
        ctk.CTkOptionMenu(
            bar, values=ALL_STATUSES,
            variable=self._status_var,
            command=self._on_status_filter,
            fg_color=COLORS["surface"], button_color=COLORS["border"],
            button_hover_color=COLORS["border_light"],
            text_color=COLORS["text"], width=140, height=36,
        ).grid(row=0, column=2, padx=(0, 8))

        # Genre filter
        self._genre_var = ctk.StringVar(value="Tümü")
        ctk.CTkOptionMenu(
            bar, values=GENRES,
            variable=self._genre_var,
            command=self._on_genre_filter,
            fg_color=COLORS["surface"], button_color=COLORS["border"],
            button_hover_color=COLORS["border_light"],
            text_color=COLORS["text"], width=120, height=36,
        ).grid(row=0, column=3, padx=(0, 8))

        # View toggle
        toggle = ctk.CTkFrame(bar, fg_color=COLORS["surface"], corner_radius=8)
        toggle.grid(row=0, column=4, padx=(0, 12))
        for sym, mode in [("⊞", "grid"), ("☰", "list")]:
            ctk.CTkButton(
                toggle, text=sym, width=34, height=34,
                corner_radius=6,
                fg_color="transparent",
                hover_color=COLORS["card"],
                text_color=COLORS["text_muted"],
                command=lambda m=mode: self._set_view(m),
            ).pack(side="left", padx=2, pady=2)

        # Add book
        ctk.CTkButton(
            bar, text="＋  Kitap Ekle",
            font=("Helvetica", 13, "bold"),
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color=COLORS["bg"], corner_radius=8, height=36,
            command=self._open_add,
        ).grid(row=0, column=5)

        return bar

    # ── filter handlers ─────────────────────────────────────────────────────

    def _on_status_filter(self, val): self._status_filter = val; self._reload_cards()
    def _on_genre_filter(self,  val): self._genre_filter  = val; self._reload_cards()
    def _set_view(self, mode):        self._view_mode = mode;    self._reload_cards()

    def _reload_cards(self):
        for w in self._scroll.winfo_children():
            w.destroy()

        books = self._db.get_all_books(
            status=self._status_filter,
            genre=self._genre_filter,
            search=self._search_var.get().strip() or None,
        )

        if not books:
            ctk.CTkLabel(
                self._scroll, text="Kitap bulunamadı.",
                font=("Helvetica", 14), text_color=COLORS["text_dim"],
            ).pack(pady=60)
            return

        if self._view_mode == "grid":
            self._build_grid(books)
        else:
            self._build_list(books)

    def _build_grid(self, books):
        container = ctk.CTkFrame(self._scroll, fg_color="transparent")
        container.pack(fill="both", expand=True)

        COLS = 6
        for i, book in enumerate(books):
            card = BookCard(container, book, on_click=self._open_detail)
            card.grid(row=i // COLS, column=i % COLS, padx=8, pady=8, sticky="n")

    def _build_list(self, books):
        for book in books:
            row = BookListRow(self._scroll, book, on_click=self._open_detail)
            row.pack(fill="x", pady=(0, 6))

    # ── navigation ─────────────────────────────────────────────────────────

    def _open_add(self):
        from ui.modals.add_book import AddBookModal
        modal = AddBookModal(self, on_saved=self._reload_cards)
        modal.grab_set()

    def _open_detail(self, book_id: int):
        from ui.modals.book_detail import BookDetailModal
        modal = BookDetailModal(self, book_id=book_id, on_saved=self._reload_cards)
        modal.grab_set()
