import os
import customtkinter as ctk
from tkinter import Listbox, Scrollbar, END
from core.data_manager import DataManager

class HistoryPage(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        self.data_manager = DataManager(data_dir)
        self.entries = []          # full entry objects
        self._build_ui()
        self._load_entries()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(1, weight=1)

        label = ctk.CTkLabel(
            self,
            text="Historical HRT Entries",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")

        # left: list of entries
        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="nsew")
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
        detail_frame.grid(row=1, column=1, padx=(10, 20), pady=10, sticky="nsew")
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

        # refresh button
        refresh_btn = ctk.CTkButton(
            self, text="Refresh", command=self._load_entries, width=80
        )
        refresh_btn.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="e")

    def _load_entries(self):
        """Load entries from DataManager and populate the listbox."""
        self.entry_list.delete(0, END)
        self.entries = self.data_manager.load_hrt_entries()

        for idx, e in enumerate(self.entries):
            summary = self._format_entry_summary(e, idx)
            self.entry_list.insert(END, summary)

        # clear detail view when reloading
        self._set_detail_text("Select an entry on the left to view details.")

    def _format_entry_summary(self, entry, index):
        """Create a human-readable single-line summary for the entry."""
        if not isinstance(entry, dict):
            return f"{index + 1}: {str(entry)}"

        # newer rich schema
        title = entry.get("title") or ""
        date = entry.get("date") or ""
        time = entry.get("time") or ""
        ts = entry.get("timestamp") or ""
        meds = entry.get("medications") or []

        # prefer display: "YYYY-MM-DD HH:MM - Title (Estradiol, Spironolactone)"
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

        if title:
            return f"{when} - {title}{meds_part}"
        return f"{when}{meds_part}"

    def _on_entry_selected(self, _event):
        """When the user selects an entry in the list, show full details."""
        if not self.entries:
            return
        selection = self.entry_list.curselection()
        if not selection:
            return
        index = selection[0]
        try:
            entry = self.entries[index]
        except IndexError:
            return
        detail = self._format_entry_detail(entry, index)
        self._set_detail_text(detail)

    def _format_entry_detail(self, entry, index):
        """Format a multi-line detailed view of the entry."""
        if not isinstance(entry, dict):
            return f"Entry {index + 1}\n\n{str(entry)}"

        lines = []
        lines.append(f"Entry #{index + 1}")
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

        mood = entry.get("mood")
        if mood:
            lines.append(f"Mood: {mood}")

        short_symptoms = entry.get("symptoms")
        if short_symptoms:
            lines.append(f"Symptoms (short): {short_symptoms}")

        # legacy simple entry text
        simple_text = entry.get("entry")
        if simple_text and simple_text != title:
            lines.append(f"Text: {simple_text}")

        # medications
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

        # notes
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