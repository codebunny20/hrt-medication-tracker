import os
import sys
import customtkinter as ctk

# --- make imports work no matter where you run from ---
# When PyInstaller bundles to onefile, data files are extracted to sys._MEIPASS.
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ensure the directory that contains the "core" and "ui" packages is on sys.path
# e.g. ...\HRT_Tracker
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# if user runs "python HRT_Tracker\app.py" from repo root,
# also ensure repo root is on sys.path (useful for some tools/tests)
REPO_ROOT = os.path.dirname(BASE_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ui.settings_page import SettingsPage
from ui.hrt_log_page import HRTLogPage
from ui.history_page import HistoryPage
from ui.resources_page import ResourcesPage
from ui.symptoms_page import SymptomsPage
from ui.bug_report_page import BugReportPage
from ui.help_page import HelpPage  # NEW
from core.settings_manager import SettingsManager


class HRTTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # simpler window config
        self.title("HRT Tracker")
        self.minsize(1040, 790)

        # snap window to top-left of the current screen, keeping size
        width, height = 1040, 790
        try:
            screen_x = self.winfo_screenx()
            screen_y = self.winfo_screeny()
        except Exception:
            screen_x = 0
            screen_y = 0
        self.geometry(f"{width}x{height}+{screen_x}+{screen_y}")

        # layout: top nav (row 0) + content (row 1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # top navigation bar
        self.navbar = ctk.CTkFrame(self, height=48, corner_radius=0)
        self.navbar.grid(row=0, column=0, sticky="ew")
        self.navbar.grid_columnconfigure(7, weight=1)  # was 6, shift right for Help

        self.logo_label = ctk.CTkLabel(
            self.navbar, text="HRT Tracker", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=(16, 24), pady=8)

        # navigation buttons (ordered by typical usage)
        self.btn_hrt_log = ctk.CTkButton(
            self.navbar, text="Log HRT", width=90, command=self.show_hrt_log_page
        )
        self.btn_hrt_log.grid(row=0, column=1, padx=4, pady=8)

        self.btn_history = ctk.CTkButton(
            self.navbar, text="History", width=90, command=self.show_history_page
        )
        self.btn_history.grid(row=0, column=2, padx=4, pady=8)

        self.btn_symptoms = ctk.CTkButton(
            self.navbar, text="Symptoms", width=90, command=self.show_symptoms_page
        )
        self.btn_symptoms.grid(row=0, column=3, padx=4, pady=8)

        self.btn_resources = ctk.CTkButton(
            self.navbar, text="Resources", width=90, command=self.show_resources_page
        )
        self.btn_resources.grid(row=0, column=4, padx=4, pady=8)

        self.btn_bug_report = ctk.CTkButton(
            self.navbar, text="Bug Report", width=100, command=self.show_bug_report_page
        )
        self.btn_bug_report.grid(row=0, column=5, padx=4, pady=8)

        # NEW: Help button
        self.btn_help = ctk.CTkButton(
            self.navbar, text="Help", width=80, command=self.show_help_page
        )
        self.btn_help.grid(row=0, column=6, padx=4, pady=8)

        self.btn_settings = ctk.CTkButton(
            self.navbar, text="Settings", width=90, command=self.show_settings_page
        )
        self.btn_settings.grid(row=0, column=7, padx=(4, 16), pady=8, sticky="e")

        # main content area
        self.content = ctk.CTkFrame(self)
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        # instantiate pages (as CTkFrames)
        self.pages = {}
        self.pages["settings"] = SettingsPage(self.content)
        self.pages["hrt_log"] = HRTLogPage(self.content)
        self.pages["history"] = HistoryPage(self.content)
        self.pages["resources"] = ResourcesPage(self.content)
        self.pages["symptoms"] = SymptomsPage(self.content)
        self.pages["bug_report"] = BugReportPage(self.content)
        self.pages["help"] = HelpPage(self.content)  # NEW

        # show default page: logging HRT is the primary action
        self.current_page = None
        self.show_hrt_log_page()

    def _show_page(self, key: str):
        if self.current_page is not None:
            self.current_page.grid_forget()
        page = self.pages[key]
        page.grid(row=0, column=0, sticky="nsew")
        self.current_page = page
        # notify page that it is now visible (useful for quick focus behavior)
        on_show = getattr(page, "on_show", None)
        if callable(on_show):
            on_show()

    def show_settings_page(self):
        self._show_page("settings")

    def show_hrt_log_page(self):
        self._show_page("hrt_log")

    def show_history_page(self):
        self._show_page("history")

    def show_resources_page(self):
        self._show_page("resources")

    def show_symptoms_page(self):
        self._show_page("symptoms")

    def show_bug_report_page(self):
        self._show_page("bug_report")

    def show_help_page(self):  # NEW
        self._show_page("help")


def main():
    # global CustomTkinter appearance, driven by saved settings when available
    settings = SettingsManager()
    theme = settings.get_setting("theme", "System")
    mode = "system"
    if str(theme).lower() == "light":
        mode = "light"
    elif str(theme).lower() == "dark":
        mode = "dark"
    ctk.set_appearance_mode(mode)
    ctk.set_default_color_theme("blue")

    app = HRTTrackerApp()
    app.mainloop()


if __name__ == "__main__":
    main()