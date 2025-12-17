import os
import customtkinter as ctk
from tkinter import messagebox
from tkinter import Listbox, Scrollbar  # keep native for listbox for now
from core.data_manager import DataManager


class ResourcesPage(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        self.data_manager = DataManager(data_dir)
        # now returns the inner list from {"resources": [...]}
        self.resources = self.data_manager.load_hrt_resources()
        self._build_ui()
        self._load_resources()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text="Resources", font=ctk.CTkFont(size=22, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=(20, 10))

        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.resources_listbox = Listbox(list_frame, width=50, height=15)
        self.resources_listbox.grid(row=0, column=0, sticky="nsew")

        scrollbar = Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.resources_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.resources_listbox.yview)

        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        add_btn = ctk.CTkButton(btn_frame, text="Add Resource", command=self._add_resource)
        add_btn.grid(row=0, column=0, padx=(0, 10))

        remove_btn = ctk.CTkButton(btn_frame, text="Remove Resource", command=self._remove_resource)
        remove_btn.grid(row=0, column=1)

    def _load_resources(self):
        self.resources_listbox.delete(0, "end")
        # expect list of dicts with "name" key, but also handle plain strings
        for r in self.resources:
            if isinstance(r, dict):
                self.resources_listbox.insert("end", r.get("name", str(r)))
            else:
                self.resources_listbox.insert("end", str(r))

    def _add_resource(self):
        # quick text prompt; could be replaced by a dialog later
        name = ctk.CTkInputDialog(text="Enter resource name:", title="Add Resource").get_input()
        if not name:
            return
        # store simple list of names or dicts; keep existing shape if possible
        if self.resources and isinstance(self.resources[0], dict):
            self.resources.append({"name": name})
        else:
            self.resources.append(name)
        self.data_manager.save_hrt_resources(self.resources)
        self._load_resources()

    def _remove_resource(self):
        selection = self.resources_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Error", "Please select a resource to remove.")
            return
        index = selection[0]
        del self.resources[index]
        self.data_manager.save_hrt_resources(self.resources)
        self._load_resources()