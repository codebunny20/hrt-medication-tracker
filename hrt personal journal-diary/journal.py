import customtkinter as ctk
import json
from datetime import datetime
import os
from tkinter import messagebox
import tkinter as tk

# Store journal data under: <this folder>\entrys\hrt_journal_data.json
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_ENTRYS_DIR = os.path.join(_BASE_DIR, "entrys")
os.makedirs(_ENTRYS_DIR, exist_ok=True)

DATA_FILE = os.path.join(_ENTRYS_DIR, "hrt_journal_data.json")


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Error saving data:", e)


class HRTJournalApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Trans Journal")
        self.geometry("900x600")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Load data
        self.data = load_data()
        self.data.setdefault("entries", [])
        self.data.setdefault("mood_snapshots", [])
        self.data.setdefault("identity", {
            "name": "",
            "pronouns": "",
            "labels": "",
            "affirmations": ""
        })
        self.data.setdefault("resources", "")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.build_ui()

        self._entries_window = None  # Track entries viewer window

    def build_ui(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.tab_today = self.tabview.add("Today")
        self.tab_mood = self.tabview.add("Mood & Body")
        self.tab_identity = self.tabview.add("Identity")
        self.tab_resources = self.tabview.add("Resources")
        self.tab_settings = self.tabview.add("Settings")

        self.build_today_tab()
        self.build_mood_tab()
        self.build_identity_tab()
        self.build_resources_tab()
        self.build_settings_tab()

    # ---------- TODAY TAB ----------
    def build_today_tab(self):
        self.tab_today.grid_rowconfigure(1, weight=1)
        self.tab_today.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(self.tab_today)
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        header_frame.grid_columnconfigure(1, weight=1)

        date_label = ctk.CTkLabel(
            header_frame,
            text=datetime.now().strftime("Today: %Y-%m-%d"),
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        date_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        tags_label = ctk.CTkLabel(header_frame, text="Tags (comma-separated):")
        tags_label.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="w")

        self.tags_entry = ctk.CTkEntry(header_frame, placeholder_text="e.g. euphoria, social, dysphoria")
        self.tags_entry.grid(row=1, column=1, padx=5, pady=(0, 5), sticky="ew")

        self.today_text = ctk.CTkTextbox(self.tab_today, wrap="word")
        self.today_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        button_frame = ctk.CTkFrame(self.tab_today)
        button_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        save_btn = ctk.CTkButton(button_frame, text="Save entry", command=self.save_today_entry)
        save_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        clear_btn = ctk.CTkButton(button_frame, text="Clear text", command=self.clear_today_text)
        clear_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        quick_hide_btn = ctk.CTkButton(button_frame, text="Quick hide", command=self.quick_hide)
        quick_hide_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Entries actions
        entries_frame = ctk.CTkFrame(self.tab_today)
        entries_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=(0, 5))
        entries_frame.grid_columnconfigure((0, 1), weight=1)

        view_btn = ctk.CTkButton(entries_frame, text="View saved entries", command=self.open_entries_viewer)
        view_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    def save_today_entry(self):
        text = self.today_text.get("1.0", "end").strip()
        tags_raw = self.tags_entry.get().strip()
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

        if not text and not tags:
            return

        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "tags": tags,
            "text": text
        }
        self.data["entries"].append(entry)
        save_data(self.data)

        self.title("Trans Journal  –  Saved")

    def clear_today_text(self):
        self.today_text.delete("1.0", "end")

    # ---------- ENTRIES VIEWER ----------
    def _entries_sorted(self):
        entries = list(self.data.get("entries", []) or [])
        return sorted(entries, key=lambda e: (e.get("timestamp") or e.get("date") or ""), reverse=True)

    def open_entries_viewer(self):
        entries = self._entries_sorted()
        if not entries:
            messagebox.showinfo("Entries", "No saved entries found.")
            return

        if self._entries_window is not None and self._entries_window.winfo_exists():
            self._entries_window.deiconify()
            self._entries_window.lift()
            self._entries_window.focus_force()
            self._refresh_entries_list()
            return

        win = ctk.CTkToplevel(self)
        self._entries_window = win
        win.title("Saved entries")
        win.geometry("900x600")
        win.transient(self)
        win.lift()
        win.focus_force()

        def _on_close():
            self._entries_window = None
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", _on_close)

        outer = ctk.CTkFrame(win)
        outer.pack(fill="both", expand=True, padx=10, pady=10)
        outer.grid_columnconfigure(0, weight=0)
        outer.grid_columnconfigure(1, weight=1)
        outer.grid_rowconfigure(0, weight=1)

        # Left: list
        left = ctk.CTkFrame(outer)
        left.grid(row=0, column=0, sticky="nsw", padx=(0, 10))
        ctk.CTkLabel(left, text="Entries").pack(anchor="w")

        self._entries_listbox = tk.Listbox(left, height=25, width=35, exportselection=False)
        self._entries_listbox.pack(fill="y", expand=False)

        # Right: preview
        right = ctk.CTkFrame(outer)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)

        self._entry_preview = ctk.CTkTextbox(right, wrap="word")
        self._entry_preview.grid(row=0, column=0, sticky="nsew")

        # Bottom buttons
        btn_row = ctk.CTkFrame(win, fg_color="transparent")
        btn_row.pack(fill="x", padx=10, pady=(0, 10))
        btn_row.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(btn_row, text="Refresh", command=self._refresh_entries_list).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(btn_row, text="Delete selected", command=self.delete_selected_entry).grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkButton(btn_row, text="Close", command=_on_close).grid(row=0, column=2, padx=5, sticky="ew")

        def _on_select(_evt=None):
            self._update_entry_preview_from_selection()

        self._entries_listbox.bind("<<ListboxSelect>>", _on_select)

        self._refresh_entries_list()

    def _refresh_entries_list(self):
        if not (self._entries_window is not None and self._entries_window.winfo_exists()):
            return
        if not hasattr(self, "_entries_listbox"):
            return

        entries = self._entries_sorted()
        self._viewer_entries = entries

        self._entries_listbox.delete(0, "end")
        for e in entries:
            ts = (e.get("timestamp") or "").strip()
            date = (e.get("date") or "").strip()
            tags = e.get("tags") or []
            tag_str = f" [{', '.join(tags)}]" if tags else ""
            label = (ts or date or "(no date)") + tag_str
            self._entries_listbox.insert("end", label)

        # auto-select first
        if entries:
            self._entries_listbox.selection_clear(0, "end")
            self._entries_listbox.selection_set(0)
            self._entries_listbox.activate(0)
            self._update_entry_preview_from_selection()

    def _get_selected_entry_index(self):
        if not hasattr(self, "_entries_listbox"):
            return None
        sel = self._entries_listbox.curselection()
        if not sel:
            return None
        return int(sel[0])

    def _update_entry_preview_from_selection(self):
        if not hasattr(self, "_entry_preview"):
            return
        idx = self._get_selected_entry_index()
        self._entry_preview.configure(state="normal")
        self._entry_preview.delete("1.0", "end")

        if idx is None or not hasattr(self, "_viewer_entries"):
            self._entry_preview.insert("1.0", "Select an entry to preview it.")
            self._entry_preview.configure(state="disabled")
            return

        try:
            e = self._viewer_entries[idx]
        except Exception:
            self._entry_preview.insert("1.0", "Select an entry to preview it.")
            self._entry_preview.configure(state="disabled")
            return

        ts = e.get("timestamp", "")
        date = e.get("date", "")
        tags = e.get("tags", [])
        text = e.get("text", "")

        lines = []
        if ts: lines.append(f"Timestamp: {ts}")
        if date: lines.append(f"Date: {date}")
        if tags: lines.append("Tags: " + ", ".join(tags))
        lines.append("")
        lines.append(text or "")

        self._entry_preview.insert("1.0", "\n".join(lines).strip())
        self._entry_preview.configure(state="disabled")

    def delete_selected_entry(self):
        if not (self._entries_window is not None and self._entries_window.winfo_exists()):
            messagebox.showinfo("Delete entry", "Open 'View saved entries' first.")
            return

        idx = self._get_selected_entry_index()
        if idx is None or not hasattr(self, "_viewer_entries"):
            messagebox.showinfo("Delete entry", "Select an entry to delete.")
            return

        entry = self._viewer_entries[idx]
        ts = (entry.get("timestamp") or entry.get("date") or "this entry").strip()

        if not messagebox.askyesno("Delete entry", f"Delete {ts}? This cannot be undone."):
            return

        try:
            self.data["entries"].remove(entry)
        except ValueError:
            t = entry.get("timestamp")
            self.data["entries"] = [e for e in (self.data.get("entries") or []) if e.get("timestamp") != t]

        save_data(self.data)
        self._refresh_entries_list()

    # ---------- MOOD TAB ----------
    def build_mood_tab(self):
        self.tab_mood.grid_rowconfigure(2, weight=1)
        self.tab_mood.grid_columnconfigure(0, weight=1)
        self.tab_mood.grid_columnconfigure(1, weight=1)

        mood_label = ctk.CTkLabel(self.tab_mood, text="Overall mood (0–10):")
        mood_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.mood_slider = ctk.CTkSlider(self.tab_mood, from_=0, to=10, number_of_steps=11)
        self.mood_slider.set(5)
        self.mood_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        dys_label = ctk.CTkLabel(self.tab_mood, text="Gender dysphoria intensity (0–10):")
        dys_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.dys_slider = ctk.CTkSlider(self.tab_mood, from_=0, to=10, number_of_steps=11)
        self.dys_slider.set(5)
        self.dys_slider.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        eup_label = ctk.CTkLabel(self.tab_mood, text="Gender euphoria intensity (0–10):")
        eup_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.eup_slider = ctk.CTkSlider(self.tab_mood, from_=0, to=10, number_of_steps=11)
        self.eup_slider.set(5)
        self.eup_slider.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        body_label = ctk.CTkLabel(self.tab_mood, text="Body feelings / notes:")
        body_label.grid(row=3, column=0, padx=5, pady=5, sticky="nw")

        self.body_text = ctk.CTkTextbox(self.tab_mood, wrap="word")
        self.body_text.grid(row=3, column=1, padx=5, pady=5, sticky="nsew")

        save_btn = ctk.CTkButton(self.tab_mood, text="Save mood snapshot", command=self.save_mood_snapshot)
        save_btn.grid(row=4, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

    def save_mood_snapshot(self):
        snapshot = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "mood": self.mood_slider.get(),
            "dysphoria": self.dys_slider.get(),
            "euphoria": self.eup_slider.get(),
            "body_notes": self.body_text.get("1.0", "end").strip()
        }
        self.data["mood_snapshots"].append(snapshot)
        save_data(self.data)
        self.title("Trans Journal  –  Mood Saved")

    # ---------- IDENTITY TAB ----------
    def build_identity_tab(self):
        self.tab_identity.grid_columnconfigure(1, weight=1)
        self.tab_identity.grid_rowconfigure(3, weight=1)

        name_label = ctk.CTkLabel(self.tab_identity, text="Name(s):")
        name_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = ctk.CTkEntry(self.tab_identity)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        pronoun_label = ctk.CTkLabel(self.tab_identity, text="Pronouns:")
        pronoun_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.pronoun_entry = ctk.CTkEntry(self.tab_identity)
        self.pronoun_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        labels_label = ctk.CTkLabel(self.tab_identity, text="Labels / words that feel good:")
        labels_label.grid(row=2, column=0, padx=5, pady=5, sticky="ne")
        self.labels_text = ctk.CTkTextbox(self.tab_identity, height=80, wrap="word")
        self.labels_text.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        affirm_label = ctk.CTkLabel(self.tab_identity, text="Affirmations you write for yourself:")
        affirm_label.grid(row=3, column=0, padx=5, pady=5, sticky="ne")
        self.affirm_text = ctk.CTkTextbox(self.tab_identity, wrap="word")
        self.affirm_text.grid(row=3, column=1, padx=5, pady=5, sticky="nsew")

        save_btn = ctk.CTkButton(self.tab_identity, text="Save identity info", command=self.save_identity)
        save_btn.grid(row=4, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

        ident = self.data.get("identity", {})
        self.name_entry.insert(0, ident.get("name", ""))
        self.pronoun_entry.insert(0, ident.get("pronouns", ""))
        self.labels_text.insert("1.0", ident.get("labels", ""))
        self.affirm_text.insert("1.0", ident.get("affirmations", ""))

    def save_identity(self):
        self.data["identity"] = {
            "name": self.name_entry.get().strip(),
            "pronouns": self.pronoun_entry.get().strip(),
            "labels": self.labels_text.get("1.0", "end").strip(),
            "affirmations": self.affirm_text.get("1.0", "end").strip()
        }
        save_data(self.data)
        self.title("Trans Journal  –  Identity Saved")

    # ---------- RESOURCES TAB ----------
    def build_resources_tab(self):
        self.tab_resources.grid_rowconfigure(1, weight=1)
        self.tab_resources.grid_columnconfigure(0, weight=1)

        info_label = ctk.CTkLabel(
            self.tab_resources,
            text="Personal resources: people, practices, media, coping tools, etc.",
            justify="left"
        )
        info_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.resources_text = ctk.CTkTextbox(self.tab_resources, wrap="word")
        self.resources_text.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.resources_text.insert("1.0", self.data.get("resources", ""))

        save_btn = ctk.CTkButton(self.tab_resources, text="Save resources", command=self.save_resources)
        save_btn.grid(row=2, column=0, padx=5, pady=10, sticky="ew")

    def save_resources(self):
        self.data["resources"] = self.resources_text.get("1.0", "end").strip()
        save_data(self.data)
        self.title("Trans Journal  –  Resources Saved")

    # ---------- SETTINGS TAB ----------
    def build_settings_tab(self):
        self.tab_settings.grid_columnconfigure(0, weight=1)

        hide_label = ctk.CTkLabel(
            self.tab_settings,
            text="Quick hide clears visible text and switches to this tab.\n"
                 "You can extend this with a lock screen or neutral cover.",
            justify="left"
        )
        hide_label.grid(row=0, column=0, padx=5, pady=10, sticky="w")

    def quick_hide(self):
        try:
            self.today_text.delete("1.0", "end")
        except Exception:
            pass
        self.tabview.set("Settings")
        self.title("Notes")

if __name__ == "__main__":
    app = HRTJournalApp()
    app.mainloop()