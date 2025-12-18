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
        self.preset_symptoms = [
            "Fatigue",
            "Headaches",
            "Nausea",
            "Hot flashes / warmth",
            "Cramps / pressure",
            "Skin changes",
        ]
        self.preset_vars = {}
        self.mood_var = ctk.StringVar(value="")
        self.energy_var = ctk.StringVar(value="")
        self.sleep_var = ctk.StringVar(value="")
        self.dysphoria_var = ctk.StringVar()
        self.euphoria_var = ctk.StringVar()
        self.freeform_var = ctk.StringVar()
        self.catchall_text = None
        # keep reference to first checkbox for focus on_show
        self._first_preset_checkbox = None

        # --- scrollable container setup ----------------------------------
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas = ctk.CTkCanvas(self, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ctk.CTkScrollbar(
            self, orientation="vertical", command=self.canvas.yview
        )
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # inner frame that holds actual UI content
        self.scrollable_frame = ctk.CTkFrame(self.canvas)
        self.scrollable_window = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )

        # update scrollregion when inner frame size changes
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        # keep inner frame width in sync with canvas width
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # mouse wheel support
        self._bind_mousewheel(self.canvas)

        # build UI inside scrollable_frame
        self._build_ui(parent=self.scrollable_frame)
        self._load_recent_symptoms()

    # --- scrolling helpers -----------------------------------------------

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.scrollable_window, width=event.width)

    def _on_mousewheel(self, event):
        if event.num == 4:       # Linux scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:     # Linux scroll down
            self.canvas.yview_scroll(1, "units")
        else:                    # Windows / macOS
            direction = -1 if event.delta > 0 else 1
            self.canvas.yview_scroll(direction, "units")

    def _bind_mousewheel(self, widget):
        widget.bind("<Enter>", lambda _e: self._enable_mousewheel(widget))
        widget.bind("<Leave>", lambda _e: self._disable_mousewheel(widget))

    def _enable_mousewheel(self, widget):
        widget.bind_all("<MouseWheel>", self._on_mousewheel)
        widget.bind_all("<Button-4>", self._on_mousewheel)
        widget.bind_all("<Button-5>", self._on_mousewheel)

    def _disable_mousewheel(self, widget):
        widget.unbind_all("<MouseWheel>")
        widget.unbind_all("<Button-4>")
        widget.unbind_all("<Button-5>")

    # --- lifecycle hook --------------------------------------------------

    def on_show(self):
        """Called by app when page becomes visible; scroll to top and focus first control."""
        try:
            self.canvas.yview_moveto(0.0)
            if self._first_preset_checkbox is not None:
                self._first_preset_checkbox.focus_set()
        except Exception:
            pass

    # --- UI building -----------------------------------------------------

    def _build_ui(self, parent):
        parent.columnconfigure(0, weight=1)

        # top header
        title = ctk.CTkLabel(
            parent,
            text="Symptoms Tracker",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        title.grid(row=0, column=0, padx=20, pady=(20, 6), sticky="w")

        subtitle = ctk.CTkLabel(
            parent,
            text="Work from top to bottom: pick symptoms, add mood / context, then press “Record symptoms”.",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
            wraplength=700,
            justify="left",
        )
        subtitle.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        # section: common symptoms
        presets_frame = ctk.CTkFrame(parent)
        presets_frame.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
        presets_frame.grid_columnconfigure(0, weight=1)
        presets_frame.grid_columnconfigure(1, weight=1)

        presets_label = ctk.CTkLabel(
            presets_frame,
            text="1. Common symptoms",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        presets_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(8, 2), sticky="w")

        presets_hint = ctk.CTkLabel(
            presets_frame,
            text="Tick anything that applies right now. You can scroll if the list is long.",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
        )
        presets_hint.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 4), sticky="w")

        for idx, name in enumerate(self.preset_symptoms):
            var = ctk.BooleanVar()
            self.preset_vars[name] = var
            col = idx % 2
            row = 2 + idx // 2
            chk = ctk.CTkCheckBox(presets_frame, text=name, variable=var)
            chk.grid(row=row, column=col, padx=10, pady=2, sticky="w")
            if idx == 0:
                self._first_preset_checkbox = chk

        # section: mood & state
        mood_frame = ctk.CTkFrame(parent)
        mood_frame.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")
        for i in range(6):
            mood_frame.grid_columnconfigure(i, weight=0)
        mood_frame.grid_columnconfigure(5, weight=1)

        mood_label = ctk.CTkLabel(
            mood_frame,
            text="2. Mood & daily state (optional)",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        mood_label.grid(row=0, column=0, columnspan=6, padx=10, pady=(8, 2), sticky="w")

        mood_hint = ctk.CTkLabel(
            mood_frame,
            text="These fields help you see patterns over time but can be left blank.",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
        )
        mood_hint.grid(row=1, column=0, columnspan=6, padx=10, pady=(0, 4), sticky="w")

        mood_dd_label = ctk.CTkLabel(mood_frame, text="Mood:")
        mood_dd_label.grid(row=2, column=0, padx=(10, 4), pady=4, sticky="w")

        mood_options = ["", "Very low", "Low", "Neutral", "Okay", "Good", "Very good", "Overwhelmed"]
        mood_combo = ctk.CTkComboBox(
            mood_frame,
            values=mood_options,
            variable=self.mood_var,
            width=140,
        )
        mood_combo.grid(row=2, column=1, padx=(0, 10), pady=4, sticky="w")

        energy_label = ctk.CTkLabel(mood_frame, text="Energy:")
        energy_label.grid(row=2, column=2, padx=(0, 4), pady=4, sticky="w")

        energy_options = ["", "Very low", "Low", "Okay", "Good", "Wired"]
        energy_combo = ctk.CTkComboBox(
            mood_frame,
            values=energy_options,
            variable=self.energy_var,
            width=120,
        )
        energy_combo.grid(row=2, column=3, padx=(0, 10), pady=4, sticky="w")

        sleep_label = ctk.CTkLabel(mood_frame, text="Sleep quality:")
        sleep_label.grid(row=2, column=4, padx=(0, 4), pady=4, sticky="w")

        sleep_options = ["", "Poor", "Okay", "Good", "Great"]
        sleep_combo = ctk.CTkComboBox(
            mood_frame,
            values=sleep_options,
            variable=self.sleep_var,
            width=120,
        )
        sleep_combo.grid(row=2, column=5, padx=(0, 10), pady=4, sticky="w")

        # section: short notes
        other_frame = ctk.CTkFrame(parent)
        other_frame.grid(row=4, column=0, padx=20, pady=(5, 10), sticky="ew")
        other_frame.grid_columnconfigure(0, weight=1)
        other_frame.grid_columnconfigure(1, weight=1)

        dys_label = ctk.CTkLabel(
            other_frame,
            text="3. Short notes (optional)",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        dys_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(8, 2), sticky="w")

        dys_hint = ctk.CTkLabel(
            other_frame,
            text="You can keep these very brief; they’ll appear together in History.",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
        )
        dys_hint.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 4), sticky="w")

        dys_field_label = ctk.CTkLabel(
            other_frame,
            text="Dysphoria / distress:",
        )
        dys_field_label.grid(row=2, column=0, padx=10, pady=(4, 2), sticky="w")

        dys_entry = ctk.CTkEntry(
            other_frame,
            textvariable=self.dysphoria_var,
            placeholder_text="Short note, if you want to name it.",
        )
        dys_entry.grid(row=3, column=0, padx=10, pady=(0, 6), sticky="ew")

        eup_label = ctk.CTkLabel(
            other_frame,
            text="Euphoria & wins:",
        )
        eup_label.grid(row=2, column=1, padx=10, pady=(4, 2), sticky="w")

        eup_entry = ctk.CTkEntry(
            other_frame,
            textvariable=self.euphoria_var,
            placeholder_text="Any small wins, gender euphoria, affirming moments.",
        )
        eup_entry.grid(row=3, column=1, padx=10, pady=(0, 6), sticky="ew")

        freeform_label = ctk.CTkLabel(
            other_frame,
            text="Freeform (single line):",
        )
        freeform_label.grid(row=4, column=0, padx=10, pady=(4, 2), sticky="w")

        freeform_entry = ctk.CTkEntry(
            other_frame,
            textvariable=self.freeform_var,
            placeholder_text="Anything else you'd like to jot down in a single line.",
        )
        freeform_entry.grid(row=5, column=0, columnspan=2, padx=10, pady=(0, 6), sticky="ew")

        # section: detailed context
        catchall_frame = ctk.CTkFrame(parent)
        catchall_frame.grid(row=5, column=0, padx=20, pady=(0, 10), sticky="nsew")
        parent.rowconfigure(5, weight=1)
        catchall_frame.grid_rowconfigure(2, weight=1)
        catchall_frame.grid_columnconfigure(0, weight=1)

        catchall_label = ctk.CTkLabel(
            catchall_frame,
            text="4. Anything else (optional)",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        catchall_label.grid(row=0, column=0, padx=10, pady=(8, 2), sticky="w")

        hint = (
            "Use this space for body sensations, emotional context, social stressors, "
            "cycle timing, injection site notes, or anything that feels relevant."
        )
        catchall_hint = ctk.CTkLabel(
            catchall_frame,
            text=hint,
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
            wraplength=600,
            justify="left",
        )
        catchall_hint.grid(row=1, column=0, padx=10, pady=(0, 4), sticky="w")

        self.catchall_text = ctk.CTkTextbox(catchall_frame, width=500, height=120)
        self.catchall_text.grid(row=2, column=0, padx=10, pady=(0, 8), sticky="nsew")

        # section: actions
        buttons_frame = ctk.CTkFrame(parent)
        buttons_frame.grid(row=6, column=0, padx=20, pady=(5, 10), sticky="ew")
        buttons_frame.grid_columnconfigure(0, weight=0)
        buttons_frame.grid_columnconfigure(1, weight=0)
        buttons_frame.grid_columnconfigure(2, weight=0)
        buttons_frame.grid_columnconfigure(3, weight=1)

        record_btn = ctk.CTkButton(
            buttons_frame,
            text="Record symptoms",
            command=self.submit_symptom,
            width=150,
        )
        record_btn.grid(row=0, column=0, padx=10, pady=(4, 8), sticky="w")

        clear_btn = ctk.CTkButton(
            buttons_frame,
            text="Clear selections",
            command=self._clear_current_selection,
            width=140,
        )
        clear_btn.grid(row=0, column=1, padx=10, pady=(4, 8), sticky="w")

        clear_entries_btn = ctk.CTkButton(
            buttons_frame,
            text="Clear recorded entries",
            command=self._clear_recorded_symptoms,
            width=160,
        )
        clear_entries_btn.grid(row=0, column=2, padx=10, pady=(4, 8), sticky="w")

        # section: recent entries
        recent_frame = ctk.CTkFrame(parent)
        recent_frame.grid(row=7, column=0, padx=20, pady=(5, 20), sticky="nsew")
        parent.rowconfigure(7, weight=1)
        recent_frame.grid_rowconfigure(1, weight=1)
        recent_frame.grid_columnconfigure(0, weight=1)

        recent_label = ctk.CTkLabel(
            recent_frame,
            text="5. Recently recorded symptoms",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        recent_label.grid(row=0, column=0, padx=10, pady=(8, 4), sticky="w")

        self.recent_text = ctk.CTkTextbox(recent_frame, width=500, height=160)
        self.recent_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.recent_text.configure(state="disabled")

    # --- existing logic below (unchanged) -------------------------------

    def _load_recent_symptoms(self, limit: int = 20):
        symptoms = self.data_manager.load_symptoms()
        def _key(item):
            ts = item.get("timestamp") if isinstance(item, dict) else None
            try:
                return datetime.fromisoformat(ts)
            except Exception:
                return datetime.min

        items = [
            s for s in symptoms
            if isinstance(s, dict) and s.get("symptom")
        ]
        items.sort(key=_key, reverse=True)
        items = items[:limit]

        self.recent_text.configure(state="normal")
        self.recent_text.delete("1.0", "end")
        if not items:
            self.recent_text.insert("1.0", "No symptoms recorded yet.")
        else:
            lines = []
            for s in items:
                ts = s.get("timestamp", "")
                sym = s.get("symptom", "")
                lines.append(f"{ts}: {sym}" if ts else sym)
            self.recent_text.insert("1.0", "\n".join(lines))
        self.recent_text.configure(state="disabled")

    def _clear_recorded_symptoms(self):
        """Clear all recorded symptom entries for this page only (flat log).

        This no longer affects grouped symptom_entries used by the History page.
        """
        if not messagebox.askyesno(
            "Confirm clear",
            "This will remove all recorded symptoms shown on this page (recent list).\n\n"
            "It will NOT remove items from the History page.\n\nContinue?",
        ):
            return

        # Clear flat symptom log only
        self.data_manager.save_symptoms([])

        # Do NOT touch grouped symptom entries here anymore
        self._load_recent_symptoms()
        messagebox.showinfo("Cleared", "All recorded symptoms on this page have been cleared.")

    def _clear_current_selection(self):
        """Clear all current symptom selections in the UI only."""
        for var in self.preset_vars.values():
            var.set(False)
        self.symptom_var.set("")
        self.mood_var.set("")
        self.energy_var.set("")
        self.sleep_var.set("")
        self.dysphoria_var.set("")
        self.euphoria_var.set("")
        self.freeform_var.set("")
        if self.catchall_text is not None:
            self.catchall_text.delete("1.0", "end")

    def submit_symptom(self):
        chosen = [name for name, var in self.preset_vars.items() if var.get()]
        other = self.symptom_var.get().strip()
        if other:
            chosen.append(other)

        if not chosen:
            messagebox.showwarning("Input Error", "Please select or enter at least one symptom.")
            return

        # 1) keep existing flat symptom log (per-symptom items)
        symptoms = self.data_manager.load_symptoms()
        now = datetime.now().isoformat(timespec="seconds")
        for sym in chosen:
            symptoms.append(
                {
                    "symptom": sym,
                    "timestamp": now,
                }
            )
        self.data_manager.save_symptoms(symptoms)

        # 2) save a grouped symptom entry for History page, enriched with new fields
        symptom_entries = self.data_manager.load_symptom_entries()
        dt = datetime.fromisoformat(now)
        date_str = dt.strftime("%Y-%m-%d")
        time_str = dt.strftime("%H:%M")

        mood = (self.mood_var.get() or "").strip()
        energy = (self.energy_var.get() or "").strip()
        sleep = (self.sleep_var.get() or "").strip()
        dysphoria = (self.dysphoria_var.get() or "").strip()
        euphoria = (self.euphoria_var.get() or "").strip()
        freeform = (self.freeform_var.get() or "").strip()
        catchall = ""
        if self.catchall_text is not None:
            catchall = self.catchall_text.get("1.0", "end-1c").strip()

        note_parts = []
        if dysphoria:
            note_parts.append(f"Dysphoria / distress: {dysphoria}")
        if euphoria:
            note_parts.append(f"Euphoria & wins: {euphoria}")
        if freeform:
            note_parts.append(f"Freeform: {freeform}")
        if catchall:
            note_parts.append(f"Context: {catchall}")
        combined_notes = "\n".join(note_parts)

        entry = {
            "id": f"sym-{dt.strftime('%Y%m%d%H%M%S')}-{len(symptom_entries)}",
            "kind": "symptom",
            "title": "Symptoms",
            "date": date_str,
            "time": time_str,
            "mood": mood,
            "symptoms": ", ".join(chosen),
            "energy": energy,
            "sleep": sleep,
            "dysphoria": dysphoria,
            "euphoria": euphoria,
            "freeform": freeform,
            "extra_context": catchall,
            "notes": combined_notes,
            "medications": [],
            "timestamp": now,
        }
        symptom_entries.append(entry)
        self.data_manager.save_symptom_entries(symptom_entries)

        messagebox.showinfo("Success", "Symptoms recorded.")
        self._clear_current_selection()
        self._load_recent_symptoms()