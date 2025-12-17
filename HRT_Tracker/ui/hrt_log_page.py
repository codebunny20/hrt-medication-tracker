import customtkinter as ctk
from tkinter import messagebox

class HRTLogPage(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
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
        entry_text = self.entry.get()
        if entry_text:
            # ...save the entry to JSON via DataManager in future...
            messagebox.showinfo("Success", "Entry logged successfully!")
            self.entry.delete(0, "end")
        else:
            messagebox.showwarning("Warning", "Please enter a value.")