import customtkinter as ctk
from utils.constants import COLORS, STATUS_LABELS
from utils.helpers import load_or_generate_cover, progress_percent


class BookCard(ctk.CTkFrame):
    """Grid-style book card (120×180 cover + metadata)."""

    def __init__(self, parent, book, on_click=None, **kwargs):
        kwargs.setdefault("fg_color",    COLORS["card"])
        kwargs.setdefault("corner_radius", 10)
        super().__init__(parent, **kwargs)
        self._book     = book
        self._on_click = on_click
        self._build()
        self._bind_click(self)

    def _bind_click(self, widget):
        widget.bind("<Button-1>", self._click)
        widget.bind("<Enter>",    self._enter)
        widget.bind("<Leave>",    self._leave)
        for child in widget.winfo_children():
            self._bind_click(child)

    def _click(self, _=None):
        if self._on_click:
            self._on_click(self._book["id"])

    def _enter(self, _=None):
        self.configure(fg_color=COLORS["card_hover"])

    def _leave(self, _=None):
        self.configure(fg_color=COLORS["card"])

    def _build(self):
        b = self._book

        # Cover
        cover_img = load_or_generate_cover(b["cover_path"], b["title"], b["author"], (120, 178))
        cover_lbl = ctk.CTkLabel(self, image=cover_img, text="")
        cover_lbl.pack(padx=10, pady=(10, 6))

        # Status badge
        status     = b["status"]
        status_lbl = STATUS_LABELS.get(status, status)
        scolor     = COLORS.get(f"status_{status}", COLORS["accent"])
        sbg        = COLORS.get(f"badge_{status}_bg", COLORS["card_hover"])
        badge = ctk.CTkLabel(
            self, text=status_lbl,
            font=("Helvetica", 9, "bold"),
            fg_color=sbg,
            text_color=scolor,
            corner_radius=4,
            padx=6, pady=2,
        )
        badge.pack(padx=10, anchor="w")

        # Title
        title = b["title"][:28] + ("…" if len(b["title"]) > 28 else "")
        ctk.CTkLabel(
            self, text=title,
            font=("Georgia", 12, "bold"),
            text_color=COLORS["text"],
            wraplength=140, justify="left",
        ).pack(padx=10, pady=(4, 0), anchor="w")

        # Author
        author = b["author"][:26] + ("…" if len(b["author"]) > 26 else "")
        ctk.CTkLabel(
            self, text=author or "—",
            font=("Helvetica", 10),
            text_color=COLORS["text_muted"],
        ).pack(padx=10, anchor="w")

        # Progress bar (only for reading)
        if status == "reading" and b["total_pages"]:
            pct = progress_percent(b["current_page"], b["total_pages"])
            prog_frame = ctk.CTkFrame(self, fg_color="transparent")
            prog_frame.pack(fill="x", padx=10, pady=(4, 2))

            ctk.CTkProgressBar(
                prog_frame,
                progress_color=COLORS["green"],
                fg_color=COLORS["border"],
                height=5,
                corner_radius=3,
            ).pack(fill="x", side="left", expand=True)
            # set value after packing
            bars = [w for w in prog_frame.winfo_children()
                    if isinstance(w, ctk.CTkProgressBar)]
            if bars:
                bars[0].set(pct / 100)

            ctk.CTkLabel(
                prog_frame, text=f"{pct:.0f}%",
                font=("Helvetica", 9),
                text_color=COLORS["text_muted"],
            ).pack(side="left", padx=(4, 0))

        # Rating stars (read-only display)
        if b["rating"] > 0:
            stars = "★" * int(b["rating"]) + ("½" if b["rating"] % 1 else "")
            ctk.CTkLabel(
                self, text=stars,
                font=("Helvetica", 10),
                text_color=COLORS["yellow"],
            ).pack(padx=10, pady=(2, 8), anchor="w")
        else:
            ctk.CTkFrame(self, height=8, fg_color="transparent").pack()


class BookListRow(ctk.CTkFrame):
    """Compact list-view row for the library."""

    def __init__(self, parent, book, on_click=None, **kwargs):
        kwargs.setdefault("fg_color",    COLORS["card"])
        kwargs.setdefault("corner_radius", 6)
        super().__init__(parent, **kwargs)
        self._book     = book
        self._on_click = on_click
        self._build()
        self._bind_click(self)

    def _bind_click(self, w):
        w.bind("<Button-1>", self._click)
        w.bind("<Enter>",    self._enter)
        w.bind("<Leave>",    self._leave)
        for c in w.winfo_children():
            self._bind_click(c)

    def _click(self, _=None):
        if self._on_click:
            self._on_click(self._book["id"])

    def _enter(self, _=None): self.configure(fg_color=COLORS["card_hover"])
    def _leave(self, _=None): self.configure(fg_color=COLORS["card"])

    def _build(self):
        b = self._book
        self.grid_columnconfigure(1, weight=1)

        # Mini cover
        cover_img = load_or_generate_cover(b["cover_path"], b["title"], b["author"], (38, 56))
        ctk.CTkLabel(self, image=cover_img, text="").grid(
            row=0, column=0, rowspan=2, padx=(10, 8), pady=6
        )

        # Title
        title = b["title"][:60] + ("…" if len(b["title"]) > 60 else "")
        ctk.CTkLabel(
            self, text=title,
            font=("Georgia", 12, "bold"),
            text_color=COLORS["text"], anchor="w"
        ).grid(row=0, column=1, sticky="ew", padx=0, pady=(8, 0))

        # Author + genre
        sub = b["author"]
        if b["genre"]:
            sub += f"  ·  {b['genre']}"
        ctk.CTkLabel(
            self, text=sub,
            font=("Helvetica", 10),
            text_color=COLORS["text_muted"], anchor="w"
        ).grid(row=1, column=1, sticky="ew", pady=(0, 8))

        # Status badge
        status = b["status"]
        scolor = COLORS.get(f"status_{status}", COLORS["accent"])
        sbg    = COLORS.get(f"badge_{status}_bg", COLORS["card_hover"])
        lbl    = STATUS_LABELS.get(status, status)
        ctk.CTkLabel(
            self, text=lbl,
            font=("Helvetica", 9, "bold"),
            fg_color=sbg,
            text_color=scolor,
            corner_radius=4, padx=6, pady=2,
        ).grid(row=0, column=2, padx=8, pady=(8, 0))

        # Progress
        if status == "reading" and b["total_pages"]:
            pct = progress_percent(b["current_page"], b["total_pages"])
            ctk.CTkLabel(
                self, text=f"{b['current_page']}/{b['total_pages']} sf  ({pct:.0f}%)",
                font=("Helvetica", 10),
                text_color=COLORS["green"],
            ).grid(row=1, column=2, padx=8, pady=(0, 8))
        elif b["rating"] > 0:
            stars = "★" * int(b["rating"])
            ctk.CTkLabel(
                self, text=stars,
                font=("Helvetica", 11),
                text_color=COLORS["yellow"],
            ).grid(row=1, column=2, padx=8, pady=(0, 8))
