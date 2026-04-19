"""
Half-star rating widget built on tkinter Canvas.
"""
import tkinter as tk
import customtkinter as ctk
from utils.constants import COLORS


class StarRating(tk.Canvas):
    """
    Interactive 0–5 star rating with 0.5 precision.
    Usage:
        sr = StarRating(parent, initial=3.5, on_change=callback)
        sr.pack()
    """
    STAR_COUNT = 5
    SIZE = 20          # star bounding box per star
    PAD  = 3

    def __init__(self, parent, initial: float = 0, on_change=None,
                 interactive=True, star_size=20, **kwargs):
        self.star_size  = star_size
        self.PAD        = 3
        w = (star_size + self.PAD) * self.STAR_COUNT
        h = star_size + 2
        kwargs.setdefault("bg", COLORS["surface"])
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(parent, width=w, height=h, **kwargs)
        self._rating    = initial
        self._hover     = -1
        self._on_change = on_change
        self._interactive = interactive
        self._draw()
        if interactive:
            self.bind("<Motion>",    self._on_motion)
            self.bind("<Leave>",     self._on_leave)
            self.bind("<Button-1>",  self._on_click)

    # ── public ──────────────────────────────────────────────────────────

    @property
    def rating(self) -> float:
        return self._rating

    @rating.setter
    def rating(self, val: float):
        self._rating = round(min(5, max(0, val)) * 2) / 2
        self._draw()

    # ── private ─────────────────────────────────────────────────────────

    def _pos_to_rating(self, x: int) -> float:
        step = self.star_size + self.PAD
        raw  = x / step          # 0‥STAR_COUNT
        half = round(raw * 2) / 2
        return max(0.5, min(5.0, half))

    def _on_motion(self, e):
        self._hover = self._pos_to_rating(e.x)
        self._draw(hover=self._hover)

    def _on_leave(self, e):
        self._hover = -1
        self._draw()

    def _on_click(self, e):
        new = self._pos_to_rating(e.x)
        if new == self._rating:
            new = 0
        self._rating = new
        self._draw()
        if self._on_change:
            self._on_change(self._rating)

    def _draw(self, hover=-1):
        self.delete("all")
        display = hover if hover > 0 else self._rating
        step = self.star_size + self.PAD
        for i in range(self.STAR_COUNT):
            x  = i * step + 1
            y  = 1
            s  = self.star_size
            filled = min(1.0, max(0.0, display - i))
            self._draw_star(x, y, s, filled)

    def _draw_star(self, x, y, size, fill: float):
        """Draw a star at (x,y) with given fill fraction (0, 0.5, 1)."""
        import math
        cx, cy = x + size / 2, y + size / 2
        outer  = size / 2
        inner  = outer * 0.4
        points_outer, points_inner = [], []
        for k in range(5):
            a_o = math.radians(k * 72 - 90)
            a_i = math.radians(k * 72 + 36 - 90)
            points_outer.append((cx + outer * math.cos(a_o), cy + outer * math.sin(a_o)))
            points_inner.append((cx + inner * math.cos(a_i), cy + inner * math.sin(a_i)))
        star_pts = []
        for o, i in zip(points_outer, points_inner):
            star_pts.extend(o)
            star_pts.extend(i)

        # Empty star outline
        self.create_polygon(star_pts, fill=COLORS["surface"],
                            outline=COLORS["border_light"], width=1)

        if fill <= 0:
            return

        if fill >= 1:
            self.create_polygon(star_pts, fill=COLORS["accent"], outline="", width=0)
        else:
            # Half star: clip right side
            mid_x = cx
            clip_pts = [
                mid_x - 0.5, y - 1,
                mid_x - 0.5, y + size + 1,
            ]
            # Draw full and then mask right half
            self.create_polygon(star_pts, fill=COLORS["accent"], outline="", width=0,
                                tags="full_star")
            # Mask right half with surface color
            self.create_rectangle(
                mid_x, y - 1, x + size + 2, y + size + 2,
                fill=COLORS["surface"], outline=""
            )
            # Re-draw outline on top
            self.create_polygon(star_pts, fill="", outline=COLORS["border_light"], width=1)
