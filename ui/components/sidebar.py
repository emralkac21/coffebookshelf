import customtkinter as ctk
from utils.constants import COLORS, NAV_ITEMS, APP_NAME, APP_VERSION


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, on_navigate, **kwargs):
        kwargs.setdefault("fg_color",    COLORS["sidebar_bg"])
        kwargs.setdefault("corner_radius", 0)
        super().__init__(parent, **kwargs)
        self._on_navigate = on_navigate
        self._active      = "dashboard"
        self._buttons     = {}
        self._build()

    def _build(self):
        self.grid_rowconfigure(20, weight=1)

        # ── Logo ──────────────────────────────────────────────────────────
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.pack(fill="x", padx=16, pady=(22, 6))

        ctk.CTkLabel(
            logo_frame, text="📖", font=("Helvetica", 28),
            text_color=COLORS["accent"]
        ).pack(anchor="w")
        ctk.CTkLabel(
            logo_frame, text=APP_NAME,
            font=("Georgia", 20, "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w")
        ctk.CTkLabel(
            logo_frame, text="Kişisel Okuma Takibi",
            font=("Helvetica", 10),
            text_color=COLORS["text_dim"]
        ).pack(anchor="w")

        # ── Divider ───────────────────────────────────────────────────────
        ctk.CTkFrame(self, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=16, pady=(14, 14)
        )

        # ── Nav Items ────────────────────────────────────────────────────
        for icon, label, key in NAV_ITEMS:
            btn = self._make_nav_btn(icon, label, key)
            btn.pack(fill="x", padx=10, pady=2)
            self._buttons[key] = btn

        # ── Bottom spacer + version ───────────────────────────────────────
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self, text=f"v{APP_VERSION}",
            font=("Helvetica", 10),
            text_color=COLORS["text_dim"]
        ).pack(pady=(0, 12))

        self.set_active("dashboard")

    def _make_nav_btn(self, icon: str, label: str, key: str) -> ctk.CTkButton:
        def cmd():
            self.set_active(key)
            self._on_navigate(key)

        btn = ctk.CTkButton(
            self,
            text=f"  {icon}  {label}",
            anchor="w",
            font=("Helvetica", 13),
            height=42,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS["card_hover"],
            text_color=COLORS["sidebar_text"],
            command=cmd,
        )
        return btn

    def set_active(self, key: str):
        if self._active and self._active in self._buttons:
            self._buttons[self._active].configure(
                fg_color="transparent",
                text_color=COLORS["sidebar_text"],
                font=("Helvetica", 13),
            )
        self._active = key
        if key in self._buttons:
            self._buttons[key].configure(
                fg_color=COLORS["sidebar_active"],
                text_color=COLORS["accent"],
                font=("Helvetica", 13, "bold"),
            )
