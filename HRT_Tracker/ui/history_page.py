import os
import customtkinter as ctk
from tkinter import Listbox, Scrollbar, END
from core.data_manager import DataManager

class HistoryPage(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        self.data_manager = DataManager(data_dir)
        self._build_ui()
        self._load_entries()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)

        label = ctk.CTkLabel(self, text="Historical HRT Entries", font=ctk.CTkFont(size=22, weight="bold"))
        label.grid(row=0, column=0, padx=20, pady=(20, 10))

        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.entry_list = Listbox(list_frame)
        self.entry_list.grid(row=0, column=0, sticky="nsew")

        scrollbar = Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.entry_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.entry_list.yview)

    def _load_entries(self):
        self.entry_list.delete(0, END)
        entries = self.data_manager.load_hrt_entries()
        # expect list of dicts with 'entry' and optional 'timestamp'
        for e in entries:
            if isinstance(e, dict):
                text = e.get("entry", "")
                ts = e.get("timestamp")
                display = f"{ts} - {text}" if ts else text
                self.entry_list.insert(END, display)
            else:
                self.entry_list.insert(END, str(e))