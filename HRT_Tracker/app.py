import customtkinter as ctk
import tkinter as tk

from ui.settings_page import SettingsPage
from ui.hrt_log_page import HRTLogPage
from ui.history_page import HistoryPage
from ui.resources_page import ResourcesPage
from ui.symptoms_page import SymptomsPage
from ui.bug_report_page import BugReportPage


class HRTTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # basic window config
        self.title("HRT Tracker")
        self.geometry("1000x650")

        # grid layout: sidebar (col 0) + content (col 1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar, text="HRT Tracker", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_settings = ctk.CTkButton(
            self.sidebar, text="Settings", command=self.show_settings_page
        )
        self.btn_settings.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        self.btn_hrt_log = ctk.CTkButton(
            self.sidebar, text="Log HRT", command=self.show_hrt_log_page
        )
        self.btn_hrt_log.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.btn_history = ctk.CTkButton(
            self.sidebar, text="History", command=self.show_history_page
        )
        self.btn_history.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        self.btn_resources = ctk.CTkButton(
            self.sidebar, text="Resources", command=self.show_resources_page
        )
        self.btn_resources.grid(row=4, column=0, padx=20, pady=5, sticky="ew")

        self.btn_symptoms = ctk.CTkButton(
            self.sidebar, text="Symptoms", command=self.show_symptoms_page
        )
        self.btn_symptoms.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        self.btn_bug_report = ctk.CTkButton(
            self.sidebar, text="Bug Report", command=self.show_bug_report_page
        )
        self.btn_bug_report.grid(row=6, column=0, padx=20, pady=5, sticky="ew")

        # content container
        self.content = ctk.CTkFrame(self)
        self.content.grid(row=0, column=1, sticky="nsew")
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

        # show default page
        self.current_page = None
        self.show_settings_page()

    def _show_page(self, key: str):
        if self.current_page is not None:
            self.current_page.grid_forget()
        page = self.pages[key]
        page.grid(row=0, column=0, sticky="nsew")
        self.current_page = page

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


def main():
    # global CustomTkinter appearance
    ctk.set_appearance_mode("system")  # or "dark", "light"
    ctk.set_default_color_theme("blue")  # can later wire this to ThemeManager

    app = HRTTrackerApp()
    app.mainloop()


if __name__ == "__main__":
    main()