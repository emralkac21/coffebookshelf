import customtkinter as ctk
from datetime import date
from database.db_manager import get_db
from utils.constants import COLORS


class GoalsView(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg"])
        super().__init__(parent, **kwargs)
        self._app  = app
        self._db   = get_db()
        self._year = date.today().year
        self._build()

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def _build(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=30, pady=(22, 10))
        ctk.CTkLabel(hdr, text="Hedefler & Challenge",
                     font=("Georgia", 22, "bold"),
                     text_color=COLORS["text"]).pack(side="left")

        yr_f = ctk.CTkFrame(hdr, fg_color="transparent")
        yr_f.pack(side="right")
        ctk.CTkButton(yr_f, text="◀", width=30, height=30,
                      fg_color=COLORS["card"], corner_radius=6,
                      text_color=COLORS["text"],
                      command=self._prev_y).pack(side="left", padx=2)
        self._yr_lbl = ctk.CTkLabel(yr_f, text=str(self._year),
                                     font=("Helvetica", 14, "bold"),
                                     text_color=COLORS["text"], width=55)
        self._yr_lbl.pack(side="left")
        ctk.CTkButton(yr_f, text="▶", width=30, height=30,
                      fg_color=COLORS["card"], corner_radius=6,
                      text_color=COLORS["text"],
                      command=self._next_y).pack(side="left", padx=2)

        scroll = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["bg"],
            scrollbar_button_color=COLORS["border"],
        )
        scroll.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))
        self._scroll = scroll
        self._fill()

    def _prev_y(self):
        self._year -= 1
        self._yr_lbl.configure(text=str(self._year))
        for w in self._scroll.winfo_children():
            w.destroy()
        self._fill()

    def _next_y(self):
        self._year += 1
        self._yr_lbl.configure(text=str(self._year))
        for w in self._scroll.winfo_children():
            w.destroy()
        self._fill()

    def _fill(self):
        db    = self._db
        goal  = db.get_goal(self._year)
        stats = db.get_total_stats()

        # Books finished THIS year
        rows = db._conn_get().execute(
            "SELECT COUNT(*) cnt FROM books WHERE status='read' AND end_date LIKE ?",
            (f"{self._year}-%",)
        ).fetchone()
        books_this_year = rows["cnt"] if rows else 0

        # Pages & seconds this year
        import calendar as cal_mod
        first_day = f"{self._year}-01-01"
        last_day  = f"{self._year}-12-31"
        r2 = db._conn_get().execute(
            """SELECT COALESCE(SUM(pages_read),0) p, COALESCE(SUM(duration_seconds),0) s
               FROM reading_sessions WHERE date BETWEEN ? AND ?""",
            (first_day, last_day)
        ).fetchone()
        pages_this_year = r2["p"] if r2 else 0
        hours_this_year = (r2["s"] if r2 else 0) / 3600

        # Set Goal Card
        goal_card = ctk.CTkFrame(self._scroll, fg_color=COLORS["surface"],
                                  corner_radius=14)
        goal_card.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(goal_card, text=f"🎯  {self._year} Hedefleri",
                     font=("Georgia", 17, "bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(16, 12))

        flds = ctk.CTkFrame(goal_card, fg_color="transparent")
        flds.pack(fill="x", padx=20, pady=(0, 12))

        def lbl_entry(parent, text, default):
            ctk.CTkLabel(parent, text=text, font=("Helvetica", 11),
                         text_color=COLORS["text_muted"]).pack(anchor="w")
            e = ctk.CTkEntry(parent, placeholder_text=str(default),
                             fg_color=COLORS["card"], border_color=COLORS["border"],
                             text_color=COLORS["text"], height=34, width=120)
            e.insert(0, str(default))
            e.pack(anchor="w", pady=(2, 10))
            return e

        books_e = lbl_entry(flds, "Kitap hedefi", goal["books_target"] if goal else 12)
        pages_e = lbl_entry(flds, "Sayfa hedefi", goal["pages_target"] if goal else 5000)
        hours_e = lbl_entry(flds, "Saat hedefi",  goal["hours_target"] if goal else 100)

        def save_goal():
            try:
                db.set_goal(
                    self._year,
                    int(books_e.get() or 0),
                    int(pages_e.get() or 0),
                    int(hours_e.get() or 0),
                )
            except ValueError:
                pass
            for w in self._scroll.winfo_children():
                w.destroy()
            self._fill()

        ctk.CTkButton(goal_card, text="💾  Hedefi Kaydet",
                      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                      text_color=COLORS["bg"], height=36, corner_radius=8,
                      font=("Helvetica", 12, "bold"), command=save_goal
                      ).pack(anchor="w", padx=20, pady=(0, 16))

        if not goal:
            return

        # Progress cards
        prog_title = ctk.CTkLabel(
            self._scroll, text="İlerleme",
            font=("Georgia", 16, "bold"), text_color=COLORS["text"])
        prog_title.pack(anchor="w", pady=(0, 10))

        items = [
            ("📚", "Kitap", books_this_year, goal["books_target"],
             COLORS["accent"], "kitap"),
            ("📄", "Sayfa", pages_this_year, goal["pages_target"],
             COLORS["blue"], "sayfa"),
            ("⏰", "Saat",  round(hours_this_year), goal["hours_target"],
             COLORS["green"], "saat"),
        ]

        for icon, name, current, target, color, unit in items:
            if not target:
                continue
            pct = min(100.0, current / target * 100) if target else 0
            card = ctk.CTkFrame(self._scroll, fg_color=COLORS["card"],
                                corner_radius=12)
            card.pack(fill="x", pady=(0, 10))

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=16, pady=(14, 4))
            ctk.CTkLabel(top, text=f"{icon}  {name}",
                         font=("Helvetica", 13, "bold"),
                         text_color=COLORS["text"]).pack(side="left")
            ctk.CTkLabel(top,
                         text=f"{current:,} / {target:,} {unit}  ({pct:.0f}%)",
                         font=("Helvetica", 12), text_color=color
                         ).pack(side="right")

            bar = ctk.CTkProgressBar(card, height=10, corner_radius=5,
                                      progress_color=color,
                                      fg_color=COLORS["border"])
            bar.pack(fill="x", padx=16, pady=(0, 14))
            bar.set(pct / 100)

        # Motivational message
        if items:
            avg_pct = sum(
                min(100.0, (c / t * 100)) for _, _, c, t, _, _ in items if t
            ) / sum(1 for _, _, c, t, _, _ in items if t)
            emoji = "🎉" if avg_pct >= 100 else "💪" if avg_pct >= 50 else "📖"
            msg = (
                "Tüm hedeflere ulaştın!" if avg_pct >= 100
                else f"Hedeflerin %{avg_pct:.0f}'ine ulaştın. Devam et!"
            )
            ctk.CTkLabel(
                self._scroll, text=f"{emoji}  {msg}",
                font=("Helvetica", 13), text_color=COLORS["text_muted"],
            ).pack(anchor="w", pady=12)
