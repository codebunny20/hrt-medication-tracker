import customtkinter as ctk
from tkinter import messagebox
from core.settings_manager import SettingsManager
from core.theme_manager import ThemeManager

class SettingsPage(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.manager = SettingsManager()
        self.theme_manager = ThemeManager()
        self.theme_var = ctk.StringVar()
        self._build_ui()
        self._load_settings()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(size=22, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=(20, 10))

        theme_label = ctk.CTkLabel(self, text="Select Theme:")
        theme_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")

        self.theme_combo = ctk.CTkComboBox(
            self,
            variable=self.theme_var,
            values=["Light", "Dark", "System"],
            width=200,
        )
        self.theme_combo.grid(row=2, column=0, padx=20, pady=5, sticky="w")

        save_btn = ctk.CTkButton(self, text="Save Settings", command=self._save_settings)
        save_btn.grid(row=5, column=0, padx=20, pady=20, sticky="w")

    def _load_settings(self):
        theme = self.manager.get_setting("theme", "System")
        _accent = self.manager.get_setting("accent_color", "#3498db")
        self.theme_var.set(theme)

    def _save_settings(self):
        theme = self.theme_var.get() or "System"

        self.manager.set_setting("theme", theme)

        # reflect immediately in CustomTkinter
        mode = "system"
        if theme.lower() == "light":
            mode = "light"
        elif theme.lower() == "dark":
            mode = "dark"
        ctk.set_appearance_mode(mode)

        theme_data = self.theme_manager.get_theme()
        self.theme_manager.save_theme(theme_data)

        messagebox.showinfo("Settings", "Settings saved.")