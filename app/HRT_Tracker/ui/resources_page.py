import os
import webbrowser
import customtkinter as ctk
from tkinter import messagebox
from tkinter import Listbox, Scrollbar  # keep native for listbox for now
from core.data_manager import DataManager


class ResourcesPage(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        self.data_manager = DataManager(data_dir)
        # now always returns list of dicts with name/link/description/tags
        self.resources = self.data_manager.load_hrt_resources()
        self.filtered_indices = list(range(len(self.resources)))
        self.search_var = ctk.StringVar()
        self._build_ui()
        self._load_resources()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text="Resources", font=ctk.CTkFont(size=22, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        # search row
        search_frame = ctk.CTkFrame(self)
        search_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        search_frame.grid_columnconfigure(2, weight=1)

        search_label = ctk.CTkLabel(search_frame, text="Search:")
        search_label.grid(row=0, column=0, padx=(8, 4), pady=6, sticky="w")

        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, width=200)
        search_entry.grid(row=0, column=1, padx=(0, 8), pady=6, sticky="w")

        search_btn = ctk.CTkButton(search_frame, text="Go", width=60, command=self._apply_search)
        search_btn.grid(row=0, column=2, padx=(0, 4), pady=6, sticky="w")

        clear_btn = ctk.CTkButton(search_frame, text="Clear", width=60, command=self._clear_search)
        clear_btn.grid(row=0, column=3, padx=(0, 4), pady=6, sticky="w")

        # list of resources
        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.resources_listbox = Listbox(list_frame, width=50, height=15)
        self.resources_listbox.grid(row=0, column=0, sticky="nsew")

        scrollbar = Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.resources_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.resources_listbox.yview)

        # buttons row
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="w")

        add_btn = ctk.CTkButton(btn_frame, text="Add", command=self._add_resource)
        add_btn.grid(row=0, column=0, padx=(0, 10))

        edit_btn = ctk.CTkButton(btn_frame, text="Edit", command=self._edit_resource)
        edit_btn.grid(row=0, column=1, padx=(0, 10))

        open_btn = ctk.CTkButton(btn_frame, text="Open", command=self._open_resource)
        open_btn.grid(row=0, column=2, padx=(0, 10))

        remove_btn = ctk.CTkButton(btn_frame, text="Remove", command=self._remove_resource)
        remove_btn.grid(row=0, column=3)

    # --- filtering / loading --------------------------------------------

    def _apply_search(self):
        term = (self.search_var.get() or "").strip().lower()
        if not term:
            self.filtered_indices = list(range(len(self.resources)))
        else:
            indices = []
            for idx, r in enumerate(self.resources):
                if not isinstance(r, dict):
                    text = str(r).lower()
                else:
                    parts = [
                        r.get("name") or "",
                        r.get("description") or "",
                        r.get("link") or "",
                        ", ".join(r.get("tags") or []),
                    ]
                    text = " ".join(parts).lower()
                if term in text:
                    indices.append(idx)
            self.filtered_indices = indices
        self._load_resources()

    def _clear_search(self):
        self.search_var.set("")
        self.filtered_indices = list(range(len(self.resources)))
        self._load_resources()

    def _load_resources(self):
        self.resources_listbox.delete(0, "end")
        for idx in self.filtered_indices:
            r = self.resources[idx]
            if isinstance(r, dict):
                name = r.get("name") or "(unnamed)"
                tags = r.get("tags") or []
                tag_str = f" [{', '.join(tags)}]" if tags else ""
                self.resources_listbox.insert("end", f"{name}{tag_str}")
            else:
                self.resources_listbox.insert("end", str(r))

    def _get_selected_index(self):
        selection = self.resources_listbox.curselection()
        if not selection:
            return None
        visible_index = selection[0]
        if visible_index < 0 or visible_index >= len(self.filtered_indices):
            return None
        return self.filtered_indices[visible_index]

    # --- dialogs ---------------------------------------------------------

    def _edit_dialog(self, title, initial=None):
        """Simple modal dialog for editing a resource; returns dict or None."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.grab_set()
        dialog.transient(self)

        dialog.grid_columnconfigure(1, weight=1)

        name_var = ctk.StringVar(value=(initial or {}).get("name", ""))
        link_var = ctk.StringVar(value=(initial or {}).get("link", ""))
        desc_text_val = (initial or {}).get("description", "")
        tags_initial = (initial or {}).get("tags", [])
        if isinstance(tags_initial, list):
            tags_str = ", ".join(tags_initial)
        else:
            tags_str = str(tags_initial)
        tags_var = ctk.StringVar(value=tags_str)

        row = 0
        ctk.CTkLabel(dialog, text="Name:").grid(row=row, column=0, padx=10, pady=(10, 4), sticky="w")
        name_entry = ctk.CTkEntry(dialog, textvariable=name_var, width=320)
        name_entry.grid(row=row, column=1, padx=10, pady=(10, 4), sticky="ew")

        row += 1
        ctk.CTkLabel(dialog, text="Link (URL):").grid(row=row, column=0, padx=10, pady=4, sticky="w")
        link_entry = ctk.CTkEntry(dialog, textvariable=link_var, width=320)
        link_entry.grid(row=row, column=1, padx=10, pady=4, sticky="ew")

        row += 1
        ctk.CTkLabel(dialog, text="Description:").grid(row=row, column=0, padx=10, pady=4, sticky="nw")
        desc_box = ctk.CTkTextbox(dialog, width=320, height=100)
        desc_box.grid(row=row, column=1, padx=10, pady=4, sticky="nsew")
        dialog.grid_rowconfigure(row, weight=1)
        if desc_text_val:
            desc_box.insert("1.0", desc_text_val)

        row += 1
        ctk.CTkLabel(dialog, text="Tags (comma separated):").grid(row=row, column=0, padx=10, pady=4, sticky="w")
        tags_entry = ctk.CTkEntry(dialog, textvariable=tags_var, width=320)
        tags_entry.grid(row=row, column=1, padx=10, pady=4, sticky="ew")

        result = {"value": None}

        def on_ok():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Validation", "Name cannot be empty.")
                return
            link = link_var.get().strip()
            desc = desc_box.get("1.0", "end-1c").strip()
            tags_raw = tags_var.get().strip()
            tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []
            result["value"] = {
                "name": name,
                "link": link,
                "description": desc,
                "tags": tags,
            }
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        row += 1
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=(8, 10), sticky="e")

        ok_btn = ctk.CTkButton(btn_frame, text="OK", width=80, command=on_ok)
        ok_btn.grid(row=0, column=0, padx=(0, 8))

        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", width=80, command=on_cancel)
        cancel_btn.grid(row=0, column=1)

        name_entry.focus_set()
        dialog.wait_window()
        return result["value"]

    # --- CRUD actions ----------------------------------------------------

    def _add_resource(self):
        data = self._edit_dialog("Add Resource")
        if not data:
            return
        self.resources.append(data)
        self.data_manager.save_hrt_resources(self.resources)
        self._apply_search()  # re-run with current search term

    def _edit_resource(self):
        idx = self._get_selected_index()
        if idx is None:
            messagebox.showwarning("Edit Resource", "Please select a resource to edit.")
            return
        current = self.resources[idx] if isinstance(self.resources[idx], dict) else {}
        data = self._edit_dialog("Edit Resource", initial=current)
        if not data:
            return
        self.resources[idx] = data
        self.data_manager.save_hrt_resources(self.resources)
        self._apply_search()

    def _open_resource(self):
        idx = self._get_selected_index()
        if idx is None:
            messagebox.showwarning("Open Resource", "Please select a resource to open.")
            return
        r = self.resources[idx]
        if not isinstance(r, dict):
            messagebox.showwarning("Open Resource", "Selected item has no link.")
            return
        link = (r.get("link") or "").strip()
        if not link:
            messagebox.showwarning("Open Resource", "This resource does not have a link set.")
            return
        if not (link.startswith("http://") or link.startswith("https://")):
            link = "http://" + link
        try:
            webbrowser.open(link)
        except Exception as e:
            messagebox.showerror("Open Resource", f"Could not open link:\n{e}")

    def _remove_resource(self):
        idx = self._get_selected_index()
        if idx is None:
            messagebox.showwarning("Remove Resource", "Please select a resource to remove.")
            return
        if not messagebox.askyesno("Confirm Remove", "Remove the selected resource?"):
            return
        del self.resources[idx]
        self.data_manager.save_hrt_resources(self.resources)
        # rebuild filtered indices safely for current search term
        self._apply_search()