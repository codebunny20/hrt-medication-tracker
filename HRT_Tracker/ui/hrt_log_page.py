import customtkinter as ctk
from tkinter import messagebox
import os
from datetime import datetime
from core.data_manager import DataManager

class HRTLogPage(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        # set up DataManager pointing at ../data
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        self.data_manager = DataManager(data_dir)
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text="Log HRT Entry", font=ctk.CTkFont(size=22, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=(20, 10))

        entry_label = ctk.CTkLabel(self, text="Entry:")
        entry_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")

        self.entry = ctk.CTkEntry(self, width=350)
        self.entry.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        submit_button = ctk.CTkButton(self, text="Submit", command=self.submit_entry)
        submit_button.grid(row=3, column=0, padx=20, pady=20)

    def submit_entry(self):
        entry_text = self.entry.get().strip()
        if not entry_text:
            messagebox.showwarning("Warning", "Please enter a value.")
            return

        # load existing, append, and save
        entries = self.data_manager.load_hrt_entries()
        new_entry = {
            "entry": entry_text,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
        entries.append(new_entry)
        self.data_manager.save_hrt_entries(entries)

        messagebox.showinfo("Success", "Entry logged successfully!")
        self.entry.delete(0, "end")