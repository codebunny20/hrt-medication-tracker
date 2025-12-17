import customtkinter as ctk
from tkinter import messagebox

class BugReportPage(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text="Bug Report", font=ctk.CTkFont(size=22, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=(20, 10))

        desc_label = ctk.CTkLabel(self, text="Description of the bug:")
        desc_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")

        self.description_text = ctk.CTkTextbox(self, width=500, height=200)
        self.description_text.grid(row=2, column=0, padx=20, pady=5, sticky="nsew")

        submit_btn = ctk.CTkButton(self, text="Submit", command=self.submit_bug_report)
        submit_btn.grid(row=3, column=0, padx=20, pady=20, sticky="w")

    def submit_bug_report(self):
        description = self.description_text.get("1.0", "end-1c")
        if description.strip():
            # ...send/save bug report here...
            messagebox.showinfo("Success", "Bug report submitted successfully!")
            self.description_text.delete("1.0", "end")
        else:
            messagebox.showwarning("Warning", "Please enter a description of the bug.")