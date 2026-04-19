import customtkinter as ctk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
from database.db_manager import get_db
from services.export_service import export_csv, export_json, backup_database, restore_database
from utils.constants import COLORS, APP_NAME, APP_VERSION


class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg"])
        super().__init__(parent, **kwargs)
        self._app = app
        self._db  = get_db()
        self._build()

    def refresh(self):
        pass

    def _build(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Ayarlar",
                     font=("Georgia", 22, "bold"),
                     text_color=COLORS["text"]
                     ).grid(row=0, column=0, sticky="w", padx=30, pady=(22, 10))

        scroll = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["bg"],
            scrollbar_button_color=COLORS["border"],
        )
        scroll.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))

        # ── Görünüm ───────────────────────────────────────────────────────
        self._section(scroll, "🎨  Görünüm")
        theme_frame = ctk.CTkFrame(scroll, fg_color=COLORS["card"], corner_radius=10)
        theme_frame.pack(fill="x", pady=(0, 16))

        inner = ctk.CTkFrame(theme_frame, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(inner, text="Tema",
                     font=("Helvetica", 12), text_color=COLORS["text_muted"]
                     ).pack(side="left")

        current_theme = self._db.get_setting("theme", "dark")
        theme_var = ctk.StringVar(value="Koyu" if current_theme == "dark" else "Açık")

        def on_theme(val):
            real = "dark" if val == "Koyu" else "light"
            self._db.set_setting("theme", real)
            ctk.set_appearance_mode(real)

        ctk.CTkOptionMenu(inner,
                          values=["Koyu", "Açık"],
                          variable=theme_var,
                          command=on_theme,
                          fg_color=COLORS["surface"],
                          button_color=COLORS["border"],
                          button_hover_color=COLORS["border_light"],
                          text_color=COLORS["text"],
                          width=130, height=32,
                          ).pack(side="right")

        # ── Dışa Aktarım ──────────────────────────────────────────────────
        self._section(scroll, "📤  Dışa Aktarım")
        export_card = ctk.CTkFrame(scroll, fg_color=COLORS["card"], corner_radius=10)
        export_card.pack(fill="x", pady=(0, 16))

        btn_row = ctk.CTkFrame(export_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=14)

        def do_csv():
            path = fd.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV", "*.csv")],
                initialfile="bookshelf_export.csv",
            )
            if path:
                ok = export_csv(path)
                mb.showinfo("Dışa Aktarım",
                            "CSV başarıyla kaydedildi." if ok
                            else "Hata oluştu.")

        def do_json():
            path = fd.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON", "*.json")],
                initialfile="bookshelf_export.json",
            )
            if path:
                ok = export_json(path)
                mb.showinfo("Dışa Aktarım",
                            "JSON başarıyla kaydedildi." if ok
                            else "Hata oluştu.")

        for lbl, cmd in [("CSV Olarak Kaydet", do_csv), ("JSON Olarak Kaydet", do_json)]:
            ctk.CTkButton(btn_row, text=lbl,
                          fg_color=COLORS["surface"],
                          hover_color=COLORS["card_hover"],
                          text_color=COLORS["text"],
                          border_color=COLORS["border"], border_width=1,
                          corner_radius=8, height=36, width=200,
                          command=cmd,
                          ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            export_card,
            text="CSV formatı Goodreads ile uyumludur.",
            font=("Helvetica", 10), text_color=COLORS["text_dim"],
        ).pack(anchor="w", padx=16, pady=(0, 10))

        # ── Veritabanı ────────────────────────────────────────────────────
        self._section(scroll, "💾  Veritabanı")
        db_card = ctk.CTkFrame(scroll, fg_color=COLORS["card"], corner_radius=10)
        db_card.pack(fill="x", pady=(0, 16))

        db_row = ctk.CTkFrame(db_card, fg_color="transparent")
        db_row.pack(fill="x", padx=16, pady=14)

        def do_backup():
            path = fd.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("SQLite", "*.db")],
                initialfile="bookshelf_backup.db",
            )
            if path:
                ok = backup_database(path)
                mb.showinfo("Yedek", "Yedek alındı." if ok else "Hata.")

        def do_restore():
            path = fd.askopenfilename(filetypes=[("SQLite", "*.db")])
            if path:
                if mb.askyesno("Geri Yükle",
                               "Mevcut veriler silinecek. Devam edilsin mi?"):
                    ok = restore_database(path)
                    mb.showinfo("Geri Yükle",
                                "Geri yüklendi. Uygulamayı yeniden başlatın."
                                if ok else "Hata.")

        for lbl, cmd in [("Yedek Al (.db)", do_backup), ("Yedeği Geri Yükle", do_restore)]:
            ctk.CTkButton(db_row, text=lbl,
                          fg_color=COLORS["surface"],
                          hover_color=COLORS["card_hover"],
                          text_color=COLORS["text"],
                          border_color=COLORS["border"], border_width=1,
                          corner_radius=8, height=36, width=200,
                          command=cmd,
                          ).pack(side="left", padx=(0, 10))

        # ── Hakkında ──────────────────────────────────────────────────────
        self._section(scroll, "ℹ️  Hakkında")
        about = ctk.CTkFrame(scroll, fg_color=COLORS["card"], corner_radius=10)
        about.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(about, text=f"{APP_NAME}  {APP_VERSION}",
                     font=("Georgia", 14, "bold"),
                     text_color=COLORS["accent"]).pack(anchor="w", padx=16, pady=(14, 2))
        ctk.CTkLabel(about, text="Kişisel Okuma Takip Uygulaması\nPython · CustomTkinter · SQLite3",
                     font=("Helvetica", 11), text_color=COLORS["text_muted"],
                     justify="left").pack(anchor="w", padx=16, pady=(0, 14))

        ctk.CTkFrame(scroll, height=30, fg_color="transparent").pack()

    def _section(self, parent, title):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", pady=(10, 6))
        ctk.CTkLabel(f, text=title,
                     font=("Georgia", 14, "bold"),
                     text_color=COLORS["text"]).pack(anchor="w")
        ctk.CTkFrame(f, height=1, fg_color=COLORS["border"]).pack(fill="x", pady=(4, 0))
