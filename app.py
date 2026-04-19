import customtkinter as ctk
import os
from utils.constants import COLORS, SIDEBAR_WIDTH, WINDOW_SIZE, APP_NAME
from ui.components.sidebar import Sidebar


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        
        # --- GÜVENLİ İKON YÜKLEME (ASSETS) ---
        # Mevcut dosyanın bulunduğu klasörü al
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # İkonun assets/favicon.ico yolunda olduğunu varsayıyoruz
        icon_path = os.path.join(base_dir, "assets", "favicon.ico")

        if os.path.exists(icon_path):
            try:
                # after() kullanmak pencerenin tamamen yüklenmesini beklediği için daha garantidir
                self.after(200, lambda: self.wm_iconbitmap(icon_path))
            except Exception as e:
                print(f"İkon yükleme hatası: {e}")
        else:
            # Hata ayıklama için tam yolu yazdıralım
            print(f"Uyarı: İkon bulunamadı. Aranan yol: {icon_path}")
            
        self.geometry(WINDOW_SIZE)
        self.minsize(1000, 640)
        self.configure(fg_color=COLORS["bg_dark"])

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self._views = {}
        self._current_view = None
        self._build()

    def _build(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar
        sidebar = Sidebar(self, on_navigate=self.navigate, width=SIDEBAR_WIDTH)
        sidebar.grid(row=0, column=0, sticky="nsew")
        self._sidebar = sidebar

        # Content area
        self._content = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        self._content.grid(row=0, column=1, sticky="nsew")
        self._content.grid_rowconfigure(0, weight=1)
        self._content.grid_columnconfigure(0, weight=1)

        # Pre-load all views
        self._init_views()

        # Start on dashboard
        self.navigate("dashboard")

    def _init_views(self):
        from ui.views.dashboard     import DashboardView
        from ui.views.library       import LibraryView
        from ui.views.timer_view    import TimerView
        from ui.views.stats_view    import StatsView
        from ui.views.goals_view    import GoalsView
        from ui.views.settings_view import SettingsView

        view_classes = {
            "dashboard": DashboardView,
            "library":   LibraryView,
            "timer":     TimerView,
            "stats":     StatsView,
            "goals":     GoalsView,
            "settings":  SettingsView,
        }
        for key, cls in view_classes.items():
            view = cls(self._content, app=self)
            view.grid(row=0, column=0, sticky="nsew")
            view.grid_remove()
            self._views[key] = view

    def navigate(self, key: str, **kwargs):
        if self._current_view:
            self._views[self._current_view].grid_remove()

        view = self._views.get(key)
        if view:
            view.grid()
            if hasattr(view, "refresh"):
                view.refresh(**kwargs)
            self._current_view = key
            self._sidebar.set_active(key)

    def on_close(self):
        from database.db_manager import get_db
        get_db().close()
        self.destroy()
