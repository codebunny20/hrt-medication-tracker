import customtkinter as ctk
from tkinter import messagebox
import os
from datetime import datetime
from core.data_manager import DataManager

class SymptomsPage(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        self.data_manager = DataManager(data_dir)
        self.symptom_var = ctk.StringVar()
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text="Symptoms Tracker", font=ctk.CTkFont(size=22, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=(20, 10))

        label = ctk.CTkLabel(self, text="Enter Symptom:")
        label.grid(row=1, column=0, padx=20, pady=5, sticky="w")

        entry = ctk.CTkEntry(self, textvariable=self.symptom_var, width=350)
        entry.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        submit_btn = ctk.CTkButton(self, text="Submit", command=self.submit_symptom)
        submit_btn.grid(row=3, column=0, padx=20, pady=20)

    def submit_symptom(self):
        symptom = self.symptom_var.get().strip()
        if symptom:
            symptoms = self.data_manager.load_symptoms()
            symptoms.append(
                {
                    "symptom": symptom,
                    "timestamp": datetime.now().isoformat(timespec="seconds"),
                }
            )
            self.data_manager.save_symptoms(symptoms)
            messagebox.showinfo("Success", f"Symptom '{symptom}' recorded.")
            self.symptom_var.set("")
        else:
            messagebox.showwarning("Input Error", "Please enter a symptom.")