import customtkinter as ctk
from datetime import date
import calendar
from database.db_manager import get_db
from utils.constants import COLORS, MONTH_NAMES_TR
from utils.helpers import format_duration

try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


def _apply_style(fig, ax=None, axes=None):
    fig.patch.set_facecolor(COLORS["surface"])
    all_axes = [ax] if ax else (axes or [])
    for a in all_axes:
        a.set_facecolor(COLORS["card"])
        a.tick_params(colors=COLORS["text_muted"], labelsize=9)
        a.xaxis.label.set_color(COLORS["text_muted"])
        a.yaxis.label.set_color(COLORS["text_muted"])
        for spine in a.spines.values():
            spine.set_edgecolor(COLORS["border"])


class StatsView(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg"])
        super().__init__(parent, **kwargs)
        self._app  = app
        self._db   = get_db()
        self._year = date.today().year
        self._canvases = []
        self._build()

    def refresh(self):
        for c in self._canvases:
            try: c.get_tk_widget().destroy()
            except: pass
        self._canvases.clear()
        for w in self._content.winfo_children():
            w.destroy()
        self._fill_content()

    def _build(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=30, pady=(22, 10))

        ctk.CTkLabel(hdr, text="İstatistikler & Raporlar",
                     font=("Georgia", 22, "bold"),
                     text_color=COLORS["text"]).pack(side="left")

        # Year selector
        yr_frame = ctk.CTkFrame(hdr, fg_color="transparent")
        yr_frame.pack(side="right")
        ctk.CTkButton(yr_frame, text="◀", width=30, height=30,
                      fg_color=COLORS["card"], hover_color=COLORS["card_hover"],
                      text_color=COLORS["text"], corner_radius=6,
                      command=self._prev_year).pack(side="left", padx=2)
        self._year_lbl = ctk.CTkLabel(yr_frame, text=str(self._year),
                                       font=("Helvetica", 14, "bold"),
                                       text_color=COLORS["text"], width=60)
        self._year_lbl.pack(side="left", padx=4)
        ctk.CTkButton(yr_frame, text="▶", width=30, height=30,
                      fg_color=COLORS["card"], hover_color=COLORS["card_hover"],
                      text_color=COLORS["text"], corner_radius=6,
                      command=self._next_year).pack(side="left", padx=2)

        # Scrollable content
        self._content = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["bg"],
            scrollbar_button_color=COLORS["border"],
        )
        self._content.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))
        self._fill_content()

    def _prev_year(self):
        self._year -= 1
        self._year_lbl.configure(text=str(self._year))
        self.refresh()

    def _next_year(self):
        self._year += 1
        self._year_lbl.configure(text=str(self._year))
        self.refresh()

    def _fill_content(self):
        db = self._db
        stats = db.get_total_stats()

        # ── Summary cards ─────────────────────────────────────────────────
        card_row = ctk.CTkFrame(self._content, fg_color="transparent")
        card_row.pack(fill="x", pady=(0, 20))

        monthly = db.get_month_stats(self._year, date.today().month)
        avg_speed = self._calc_avg_speed()
        streak = db.get_streak()

        items = [
            ("📚", str(stats["books_read"]), "Toplam Okunan Kitap", COLORS["accent"]),
            ("📄", f"{stats['total_pages']:,}", "Toplam Okunan Sayfa", COLORS["blue"]),
            ("⏱",  f"{stats['total_hours']}s", "Toplam Okuma Süresi", COLORS["green"]),
            ("⚡", f"{avg_speed:.1f}", "Ort. Hız (sf/dk)", COLORS["yellow"]),
            ("🔥", str(streak), "Güncel Seri", COLORS["red"]),
        ]
        for icon, val, lbl, color in items:
            c = ctk.CTkFrame(card_row, fg_color=COLORS["card"], corner_radius=12,
                             width=160, height=90)
            c.pack(side="left", padx=(0, 12))
            c.pack_propagate(False)
            ctk.CTkLabel(c, text=icon, font=("Helvetica", 20)).pack(pady=(10, 0))
            ctk.CTkLabel(c, text=val, font=("Georgia", 18, "bold"),
                         text_color=color).pack()
            ctk.CTkLabel(c, text=lbl, font=("Helvetica", 9),
                         text_color=COLORS["text_muted"]).pack(pady=(0, 8))

        if not HAS_MPL:
            ctk.CTkLabel(
                self._content,
                text="Grafikleri görmek için: pip install matplotlib",
                font=("Helvetica", 12), text_color=COLORS["text_dim"],
            ).pack(pady=20)
            return

        # ── Monthly Pages Bar Chart ────────────────────────────────────────
        monthly_data = db.get_yearly_monthly(self._year)
        self._section("Aylık Sayfa Grafiği")
        self._bar_chart(monthly_data)

        # ── Genre Pie Chart ────────────────────────────────────────────────
        genre_data = db.get_genre_stats()
        if genre_data:
            self._section("Tür Dağılımı")
            self._pie_chart(genre_data)

        # ── Reading Calendar Heatmap ──────────────────────────────────────
        self._section(f"{self._year} Okuma Takvimi")
        self._heatmap()

        # ── Monthly finished books ────────────────────────────────────────
        finished = db.get_finished_per_month(self._year)
        if any(finished.values()):
            self._section("Aylık Tamamlanan Kitap")
            self._finished_chart(finished)

        ctk.CTkFrame(self._content, height=30, fg_color="transparent").pack()

    def _section(self, title: str):
        f = ctk.CTkFrame(self._content, fg_color="transparent")
        f.pack(fill="x", pady=(14, 6))
        ctk.CTkLabel(f, text=title,
                     font=("Georgia", 15, "bold"),
                     text_color=COLORS["text"]).pack(anchor="w")
        ctk.CTkFrame(f, height=1, fg_color=COLORS["border"]).pack(fill="x", pady=(4, 0))

    def _embed(self, fig):
        canvas = FigureCanvasTkAgg(fig, master=self._content)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.pack(fill="x", pady=(0, 10))
        self._canvases.append(canvas)

    def _bar_chart(self, data):
        months = [MONTH_NAMES_TR[d["month"]] for d in data]
        pages  = [d["pages"] for d in data]

        fig, ax = plt.subplots(figsize=(10, 3.2))
        _apply_style(fig, ax=ax)

        colors = [COLORS["accent"] if p == max(pages) else COLORS["blue"]
                  for p in pages]
        bars = ax.bar(months, pages, color=colors, width=0.6,
                      edgecolor=COLORS["border"], linewidth=0.5)
        for bar, val in zip(bars, pages):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(pages) * 0.02,
                        str(val), ha="center", va="bottom",
                        color=COLORS["text_muted"], fontsize=8)

        ax.set_ylabel("Sayfa", color=COLORS["text_muted"])
        ax.set_xlim(-0.5, 11.5)
        ax.margins(y=0.2)
        fig.tight_layout(pad=0.5)
        self._embed(fig)
        plt.close(fig)

    def _pie_chart(self, data):
        labels = [r["genre"] for r in data]
        values = [r["cnt"]   for r in data]

        palette = [COLORS["accent"], COLORS["blue"], COLORS["green"],
                   COLORS["yellow"], COLORS["purple"], COLORS["teal"],
                   COLORS["red"], "#c8a060", "#80a8d4"]

        fig, ax = plt.subplots(figsize=(6, 3.8))
        _apply_style(fig, ax=ax)

        wedges, texts, autotexts = ax.pie(
            values, labels=None, autopct="%1.0f%%",
            colors=palette[:len(values)],
            startangle=140,
            wedgeprops={"edgecolor": COLORS["border"], "linewidth": 1},
            pctdistance=0.82,
        )
        for t in autotexts:
            t.set_color(COLORS["bg"])
            t.set_fontsize(9)

        legend_patches = [mpatches.Patch(color=palette[i % len(palette)],
                                          label=f"{labels[i]} ({values[i]})")
                          for i in range(len(labels))]
        ax.legend(handles=legend_patches,
                  loc="center left", bbox_to_anchor=(1.0, 0.5),
                  fontsize=9, frameon=False,
                  labelcolor=COLORS["text_muted"])
        fig.tight_layout(pad=0.5)
        self._embed(fig)
        plt.close(fig)

    def _heatmap(self):
        daily = self._db.get_daily_pages(self._year)
        if not daily:
            ctk.CTkLabel(self._content, text="Bu yıl için veri yok.",
                         font=("Helvetica", 11), text_color=COLORS["text_dim"]
                         ).pack(anchor="w")
            return

        max_pages = max(daily.values()) if daily else 1

        fig, ax = plt.subplots(figsize=(10, 1.8))
        _apply_style(fig, ax=ax)

        # Build a 7×53 grid
        grid = [[0.0] * 53 for _ in range(7)]
        start_wd = date(self._year, 1, 1).weekday()  # Mon=0
        for d_str, pages in daily.items():
            try:
                d = date.fromisoformat(d_str)
            except ValueError:
                continue
            doy    = d.timetuple().tm_yday - 1
            col    = (doy + start_wd) // 7
            row    = (doy + start_wd) % 7
            if col < 53:
                grid[row][col] = pages / max_pages

        import numpy as np
        arr = np.array(grid)
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
            "reading", [COLORS["card"], COLORS["accent"]])
        ax.imshow(arr, aspect="auto", cmap=cmap, vmin=0, vmax=1,
                  interpolation="nearest")
        ax.set_yticks(range(7))
        ax.set_yticklabels(["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"],
                            fontsize=8, color=COLORS["text_muted"])
        ax.set_xticks([])
        fig.tight_layout(pad=0.3)
        self._embed(fig)
        plt.close(fig)

    def _finished_chart(self, finished: dict):
        months = [MONTH_NAMES_TR[m] for m in range(1, 13)]
        counts = [finished.get(f"{self._year}-{m:02d}", 0) for m in range(1, 13)]

        fig, ax = plt.subplots(figsize=(10, 2.6))
        _apply_style(fig, ax=ax)
        ax.bar(months, counts, color=COLORS["green"], edgecolor=COLORS["border"],
               linewidth=0.5, width=0.6)
        ax.set_ylabel("Kitap", color=COLORS["text_muted"])
        ax.set_xlim(-0.5, 11.5)
        ax.margins(y=0.25)
        for i, v in enumerate(counts):
            if v > 0:
                ax.text(i, v + 0.05, str(v), ha="center", va="bottom",
                        color=COLORS["text_muted"], fontsize=9)
        fig.tight_layout(pad=0.5)
        self._embed(fig)
        plt.close(fig)

    def _calc_avg_speed(self) -> float:
        db  = self._db
        rows = db._conn_get().execute(
            """SELECT SUM(pages_read) p, SUM(duration_seconds) s
               FROM reading_sessions WHERE duration_seconds > 0"""
        ).fetchone()
        if rows and rows["s"] and rows["p"]:
            return rows["p"] / (rows["s"] / 60)
        return 0.0
