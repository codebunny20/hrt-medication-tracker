import os
import csv
from datetime import datetime
import customtkinter as ctk
from tkinter import Listbox, Scrollbar, END, filedialog, messagebox
from core.data_manager import DataManager

class HistoryPage(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        self.data_manager = DataManager(data_dir)
        self.entries = []          # full entry objects (all)
        self.filtered_entries = [] # current filtered view (subset of self.entries)
        self._build_ui()
        self._load_entries()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(2, weight=1)

        # title
        label = ctk.CTkLabel(
            self,
            text="Historical HRT Entries",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 5), sticky="w")

        # --- filter / search row -----------------------------------------
        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")
        for i in range(7):
            filter_frame.grid_columnconfigure(i, weight=0)
        filter_frame.grid_columnconfigure(6, weight=1)

        search_label = ctk.CTkLabel(filter_frame, text="Search:")
        search_label.grid(row=0, column=0, padx=(8, 4), pady=6, sticky="w")

        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(filter_frame, textvariable=self.search_var, width=180)
        search_entry.grid(row=0, column=1, padx=(0, 10), pady=6, sticky="w")

        start_label = ctk.CTkLabel(filter_frame, text="Start date (YYYY-MM-DD):")
        start_label.grid(row=0, column=2, padx=(0, 4), pady=6, sticky="w")

        self.start_date_var = ctk.StringVar()
        start_entry = ctk.CTkEntry(filter_frame, textvariable=self.start_date_var, width=110)
        start_entry.grid(row=0, column=3, padx=(0, 10), pady=6, sticky="w")

        end_label = ctk.CTkLabel(filter_frame, text="End date:")
        end_label.grid(row=0, column=4, padx=(0, 4), pady=6, sticky="w")

        self.end_date_var = ctk.StringVar()
        end_entry = ctk.CTkEntry(filter_frame, textvariable=self.end_date_var, width=110)
        end_entry.grid(row=0, column=5, padx=(0, 10), pady=6, sticky="w")

        filter_btn = ctk.CTkButton(filter_frame, text="Filter", width=70, command=self._apply_filters)
        filter_btn.grid(row=0, column=6, padx=(0, 4), pady=6, sticky="e")

        clear_btn = ctk.CTkButton(filter_frame, text="Clear", width=70, command=self._clear_filters)
        clear_btn.grid(row=0, column=7, padx=(0, 4), pady=6, sticky="e")

        refresh_btn = ctk.CTkButton(filter_frame, text="Refresh", width=80, command=self._load_entries)
        refresh_btn.grid(row=0, column=8, padx=(0, 4), pady=6, sticky="e")

        export_btn = ctk.CTkButton(filter_frame, text="Export", width=80, command=self._export_filtered)
        export_btn.grid(row=0, column=9, padx=(0, 8), pady=6, sticky="e")

        # --- main layout (list + details) --------------------------------
        # left: list of entries (scrollable)
        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=2, column=0, padx=(20, 10), pady=10, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.entry_list = Listbox(list_frame)
        self.entry_list.grid(row=0, column=0, sticky="nsew")

        scrollbar = Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.entry_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.entry_list.yview)

        # bind selection change to show details
        self.entry_list.bind("<<ListboxSelect>>", self._on_entry_selected)

        # right: detailed view
        detail_frame = ctk.CTkFrame(self)
        detail_frame.grid(row=2, column=1, padx=(10, 20), pady=10, sticky="nsew")
        detail_frame.grid_rowconfigure(1, weight=1)
        detail_frame.grid_columnconfigure(0, weight=1)

        detail_label = ctk.CTkLabel(
            detail_frame,
            text="Entry Details",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        detail_label.grid(row=0, column=0, padx=10, pady=(8, 4), sticky="w")

        self.detail_text = ctk.CTkTextbox(detail_frame, width=400, height=350)
        self.detail_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.detail_text.configure(state="disabled")

        # actions row under detail pane
        actions_frame = ctk.CTkFrame(detail_frame, fg_color="transparent")
        actions_frame.grid(row=2, column=0, padx=10, pady=(0, 8), sticky="e")

        delete_btn = ctk.CTkButton(actions_frame, text="Delete", width=80, command=self._delete_selected)
        delete_btn.grid(row=0, column=0, padx=(0, 8), pady=4)

        duplicate_btn = ctk.CTkButton(actions_frame, text="Duplicate", width=90, command=self._duplicate_selected)
        duplicate_btn.grid(row=0, column=1, padx=(0, 0), pady=4)

    # --- data loading / filtering ---------------------------------------

    def _load_entries(self):
        """Load entries from DataManager and refresh filtered view.

        Combines HRT entries and grouped symptom entries into a single timeline.
        """
        hrt_entries = self.data_manager.load_hrt_entries()
        symptom_entries = self.data_manager.load_symptom_entries()

        # tag entries if not already tagged
        for e in hrt_entries:
            if isinstance(e, dict) and "kind" not in e:
                e["kind"] = "hrt"
        for e in symptom_entries:
            if isinstance(e, dict) and "kind" not in e:
                e["kind"] = "symptom"

        # simple merge; we’ll sort by date/time/timestamp in the filter function
        self.entries = hrt_entries + symptom_entries
        self._apply_filters(apply_to_existing=True)

    def _apply_filters(self, apply_to_existing: bool = False):
        """Filter self.entries by search text and date range, then repopulate listbox."""
        if not apply_to_existing:
            # ensure we start from latest data on explicit "Filter" click
            self._load_entries()
            return

        search_text = (self.search_var.get() or "").strip().lower()

        start_str = (self.start_date_var.get() or "").strip()
        end_str = (self.end_date_var.get() or "").strip()
        start_dt = end_dt = None
        # parse dates if provided
        if start_str:
            try:
                start_dt = datetime.strptime(start_str, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showwarning("Filter", "Start date must be YYYY-MM-DD.")
                return
        if end_str:
            try:
                end_dt = datetime.strptime(end_str, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showwarning("Filter", "End date must be YYYY-MM-DD.")
                return

        def in_date_range(entry):
            if not isinstance(entry, dict):
                return True
            date_str = entry.get("date")
            if not date_str:
                return True if (start_dt is None and end_dt is None) else False
            try:
                d = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return True if (start_dt is None and end_dt is None) else False
            if start_dt and d < start_dt:
                return False
            if end_dt and d > end_dt:
                return False
            return True

        def matches_search(entry):
            if not search_text:
                return True
            if not isinstance(entry, dict):
                return search_text in str(entry).lower()
            fields = []

            for key in ("title", "mood", "symptoms", "notes", "entry"):
                val = entry.get(key)
                if val:
                    fields.append(str(val))

            for key in ("date", "time", "timestamp"):
                val = entry.get(key)
                if val:
                    fields.append(str(val))

            meds = entry.get("medications")
            if isinstance(meds, list):
                for m in meds:
                    if isinstance(m, dict):
                        for k in ("name", "dose", "unit", "route", "time"):
                            v = m.get(k)
                            if v:
                                fields.append(str(v))
                    else:
                        fields.append(str(m))

            # NEW: also search plain list of symptom strings if present
            sym_list = entry.get("symptom_list")
            if isinstance(sym_list, list):
                for s in sym_list:
                    fields.append(str(s))

            haystack = " ".join(fields).lower()
            return search_text in haystack

        # apply filters
        self.filtered_entries = [
            e for e in self.entries if in_date_range(e) and matches_search(e)
        ]

        # sort by date/time/timestamp descending
        def sort_key(e):
            if not isinstance(e, dict):
                return datetime.min
            date_str = e.get("date")
            time_str = e.get("time")
            ts = e.get("timestamp")
            try:
                if date_str and time_str:
                    return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                if date_str:
                    return datetime.strptime(date_str, "%Y-%m-%d")
                if ts:
                    return datetime.fromisoformat(ts)
            except Exception:
                return datetime.min
            return datetime.min

        self.filtered_entries.sort(key=sort_key, reverse=True)
        self._populate_listbox()
        self._set_detail_text("Select an entry on the left to view details.")

    def _clear_filters(self):
        self.search_var.set("")
        self.start_date_var.set("")
        self.end_date_var.set("")
        self.filtered_entries = list(self.entries)
        self._populate_listbox()
        self._set_detail_text("Select an entry on the left to view details.")

    def _populate_listbox(self):
        self.entry_list.delete(0, END)
        for idx, e in enumerate(self.filtered_entries):
            summary = self._format_entry_summary(e, idx)
            self.entry_list.insert(END, summary)

    # --- summary / details ----------------------------------------------

    def _format_entry_summary(self, entry, index):
        """Create a human-readable single-line summary for the entry."""
        if not isinstance(entry, dict):
            return f"{index + 1}: {str(entry)}"

        kind = entry.get("kind", "hrt")  # default to 'hrt' for old data
        title = entry.get("title") or ""
        date = entry.get("date") or ""
        time = entry.get("time") or ""
        ts = entry.get("timestamp") or ""
        meds = entry.get("medications") or []
        symptoms_text = entry.get("symptoms") or ""

        when = ""
        if date and time:
            when = f"{date} {time}"
        elif date:
            when = date
        elif ts:
            when = ts
        else:
            when = f"Entry {index + 1}"

        meds_part = ""
        if isinstance(meds, list) and meds:
            med_names = []
            for m in meds:
                if isinstance(m, dict):
                    name = (m.get("name") or "").strip()
                else:
                    name = str(m)
                if name:
                    med_names.append(name)
            if med_names:
                meds_part = " (" + ", ".join(med_names[:3]) + (", ..." if len(med_names) > 3 else "") + ")"

        if not title and "entry" in entry:
            title = str(entry.get("entry", ""))

        # NEW: distinguish symptom entries in the list
        if kind == "symptom":
            label = "Symptoms"
            if symptoms_text:
                label += f": {symptoms_text}"
            return f"{when} - {label}"

        if title:
            return f"{when} - {title}{meds_part}"
        return f"{when}{meds_part}"

    def _on_entry_selected(self, _event):
        """When the user selects an entry in the list, show full details."""
        if not self.filtered_entries:
            return
        selection = self.entry_list.curselection()
        if not selection:
            return
        index = selection[0]
        try:
            entry = self.filtered_entries[index]
        except IndexError:
            return
        detail = self._format_entry_detail(entry, index)
        self._set_detail_text(detail)

    def _format_entry_detail(self, entry, index):
        """Format a multi-line detailed view of the entry."""
        if not isinstance(entry, dict):
            return f"Entry {index + 1}\n\n{str(entry)}"

        lines = []
        kind = entry.get("kind", "hrt")
        if kind == "symptom":
            lines.append(f"Symptom entry #{index + 1}")
        else:
            lines.append(f"HRT entry #{index + 1}")

        eid = entry.get("id")
        if eid:
            lines.append(f"ID: {eid}")

        date = entry.get("date") or ""
        time = entry.get("time") or ""
        timestamp = entry.get("timestamp") or ""
        if date or time:
            lines.append(f"Date / Time: {date} {time}".strip())
        if timestamp:
            lines.append(f"Recorded at: {timestamp}")

        title = entry.get("title")
        if title:
            lines.append(f"Title: {title}")

        # Common mood field (both HRT and symptom entries)
        mood = entry.get("mood")
        if mood:
            lines.append(f"Mood: {mood}")

        # Extra symptom-page state (only present for symptom entries)
        if kind == "symptom":
            energy = entry.get("energy")
            if energy:
                lines.append(f"Energy: {energy}")

            sleep = entry.get("sleep")
            if sleep:
                lines.append(f"Sleep: {sleep}")

            dysphoria = entry.get("dysphoria")
            if dysphoria:
                lines.append(f"Dysphoria / distress: {dysphoria}")

            euphoria = entry.get("euphoria")
            if euphoria:
                lines.append(f"Euphoria & wins: {euphoria}")

            freeform = entry.get("freeform")
            if freeform:
                lines.append(f"Freeform: {freeform}")

            extra_context = entry.get("extra_context")
            if extra_context:
                lines.append("")
                lines.append("Extra context:")
                lines.append(extra_context)

        short_symptoms = entry.get("symptoms")
        if short_symptoms:
            # for HRT entries this is the short symptom text;
            # for symptom entries this is the combined list string
            lines.append(f"Symptoms: {short_symptoms}")

        simple_text = entry.get("entry")
        if simple_text and simple_text != title:
            lines.append(f"Text: {simple_text}")

        meds = entry.get("medications")
        if isinstance(meds, list) and meds:
            lines.append("")
            lines.append("Medications:")
            for i, m in enumerate(meds, start=1):
                if isinstance(m, dict):
                    name = m.get("name") or ""
                    dose = m.get("dose") or ""
                    unit = m.get("unit") or ""
                    m_time = m.get("time") or ""
                    route = m.get("route") or ""
                    parts = [p for p in [
                        name,
                        f"{dose}{(' ' + unit) if unit and dose else ''}".strip(),
                        f"at {m_time}" if m_time else "",
                        f"via {route}" if route else "",
                    ] if p]
                    line = f"  {i}. " + " ".join(parts) if parts else f"  {i}. (blank)"
                else:
                    line = f"  {i}. {str(m)}"
                lines.append(line)

        notes = entry.get("notes")
        if notes:
            lines.append("")
            lines.append("Notes:")
            lines.append(notes)

        return "\n".join(lines)

    def _set_detail_text(self, text):
        self.detail_text.configure(state="normal")
        self.detail_text.delete("1.0", END)
        self.detail_text.insert("1.0", text)
        self.detail_text.configure(state="disabled")

    # --- delete / duplicate / export ------------------------------------

    def _get_selected_entry(self):
        selection = self.entry_list.curselection()
        if not selection:
            return None, None
        idx = selection[0]
        if idx < 0 or idx >= len(self.filtered_entries):
            return None, None
        return idx, self.filtered_entries[idx]

    def _delete_selected(self):
        idx, entry = self._get_selected_entry()
        if entry is None:
            messagebox.showwarning("Delete", "Please select an entry to delete.")
            return
        if not isinstance(entry, dict) or "id" not in entry:
            messagebox.showwarning("Delete", "Selected entry has no stable id; cannot delete safely.")
            return

        answer = messagebox.askyesno(
            "Delete entry",
            "Are you sure you want to permanently delete this entry?",
            icon="warning",
        )
        if not answer:
            return

        if self.data_manager.delete_entry_by_id(entry["id"]):
            self._load_entries()
            messagebox.showinfo("Delete", "Entry deleted.")
        else:
            messagebox.showerror("Delete", "Could not delete entry (id not found).")

    def _duplicate_selected(self):
        idx, entry = self._get_selected_entry()
        if entry is None:
            messagebox.showwarning("Duplicate", "Please select an entry to duplicate.")
            return
        if not isinstance(entry, dict) or "id" not in entry:
            messagebox.showwarning("Duplicate", "Selected entry has no stable id; cannot duplicate safely.")
            return

        if self.data_manager.duplicate_entry_by_id(entry["id"]):
            self._load_entries()
            messagebox.showinfo("Duplicate", "Entry duplicated.")
        else:
            messagebox.showerror("Duplicate", "Could not duplicate entry (id not found).")

    def _export_filtered(self):
        if not self.filtered_entries:
            messagebox.showinfo("Export", "There are no entries to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export filtered entries to CSV",
        )
        if not file_path:
            return

        # collect field names
        base_fields = [
            "id",
            "date",
            "time",
            "timestamp",
            "title",
            "mood",
            "symptoms",
            "notes",
            "kind",  # NEW: indicate whether this is HRT or symptom
        ]
        # we'll store medications as a single text field per row
        fieldnames = base_fields + ["medications"]

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for e in self.filtered_entries:
                    if not isinstance(e, dict):
                        writer.writerow({"notes": str(e)})
                        continue
                    row = {k: e.get(k, "") for k in base_fields}
                    meds = e.get("medications") or []
                    meds_strs = []
                    if isinstance(meds, list):
                        for m in meds:
                            if isinstance(m, dict):
                                name = m.get("name") or ""
                                dose = m.get("dose") or ""
                                unit = m.get("unit") or ""
                                m_time = m.get("time") or ""
                                route = m.get("route") or ""
                                parts = [p for p in [
                                    name,
                                    f"{dose}{(' ' + unit) if unit and dose else ''}".strip(),
                                    f"at {m_time}" if m_time else "",
                                    f"via {route}" if route else "",
                                ] if p]
                                meds_strs.append(" ".join(parts) if parts else "(blank)")
                            else:
                                meds_strs.append(str(m))
                    row["medications"] = " | ".join(meds_strs)
                    writer.writerow(row)
            messagebox.showinfo("Export", f"Exported {len(self.filtered_entries)} entries to:\n{file_path}")
        except OSError as e:
            messagebox.showerror("Export", f"Failed to write file:\n{e}")