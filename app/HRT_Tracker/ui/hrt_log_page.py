import customtkinter as ctk
from tkinter import messagebox
import os
from datetime import datetime
from core.data_manager import DataManager

class HRTLogPage(ctk.CTkFrame):
    """Advanced HRT log page with date/time, medications, mood, symptoms, and notes."""

    def __init__(self, master=None):
        super().__init__(master)
        # set up DataManager pointing at ../data
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        self.data_manager = DataManager(data_dir)

        # simple in‑memory config; could later be made user‑editable
        self.medication_suggestions = [
            "Estradiol", "Spironolactone", "Progesterone", "Finasteride",
            "Testosterone gel", "Testosterone cypionate",
        ]
        self.unit_options = ["mg", "mcg", "mL", "patch", "pill"]
        self.route_options = ["oral", "sublingual", "IM", "SC", "transdermal", "patch", "gel"]
        self.mood_options = ["", "Very bad", "Bad", "Neutral", "Good", "Very good"]

        # state
        self.clock_var = ctk.StringVar(value="")
        self.show_seconds = True  # could later be driven from settings
        self.date_var = ctk.StringVar()
        self.time_var = ctk.StringVar()
        self.title_var = ctk.StringVar()
        self.mood_var = ctk.StringVar()
        self.symptoms_var = ctk.StringVar()
        self.notes_font_size = ctk.IntVar(value=12)

        # NEW: add placeholder hints for some fields (CustomTkinter >=5.2)
        self.date_placeholder = "YYYY-MM-DD"
        self.time_placeholder = "HH:MM (24h)"
        self.title_placeholder = "Optional short label for this entry"
        self.symptoms_placeholder = "e.g. headache, fatigue, mood swings"

        self.medication_rows = []  # list of dicts per row

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

        # build UI INSIDE scrollable_frame
        self._build_ui(parent=self.scrollable_frame)
        self._start_clock()
        self._prefill_date_time()

    # --- scrolling helpers -----------------------------------------------

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        # stretch inner frame to canvas width
        self.canvas.itemconfigure(self.scrollable_window, width=event.width)

    def _on_mousewheel(self, event):
        # note: different platforms use different deltas
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
        widget.bind_all("<MouseWheel>", self._on_mousewheel)   # Windows/macOS
        widget.bind_all("<Button-4>", self._on_mousewheel)     # Linux
        widget.bind_all("<Button-5>", self._on_mousewheel)

    def _disable_mousewheel(self, widget):
        widget.unbind_all("<MouseWheel>")
        widget.unbind_all("<Button-4>")
        widget.unbind_all("<Button-5>")

    # --- lifecycle hooks -------------------------------------------------

    def on_show(self):
        """Called by app when page becomes visible; gives quick focus to date field."""
        try:
            self.date_entry.focus_set()
            self.date_entry.icursor("end")
        except Exception:
            pass

    # --- UI building -----------------------------------------------------

    def _build_ui(self, parent):
        # NOTE: was previously `self`; now everything is attached to `parent`
        parent.columnconfigure(0, weight=1)

        # --- PAGE TITLE ROW ------------------------------------------------
        title_row = ctk.CTkFrame(parent, fg_color="transparent")
        title_row.grid(row=0, column=0, padx=20, pady=(20, 6), sticky="ew")
        title_row.grid_columnconfigure(0, weight=1)
        title_row.grid_columnconfigure(1, weight=0)

        title = ctk.CTkLabel(
            title_row,
            text="Log HRT Entry",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        title.grid(row=0, column=0, sticky="w")

        clock_label = ctk.CTkLabel(
            title_row,
            textvariable=self.clock_var,
            font=ctk.CTkFont(size=14),
        )
        clock_label.grid(row=0, column=1, sticky="e", padx=(10, 0))

        # gentle description under title
        subtitle = ctk.CTkLabel(
            parent,
            text="Record today’s dose, timing, and how you’re feeling.",
            font=ctk.CTkFont(size=12, slant="italic"),
            anchor="w",
        )
        subtitle.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        # --- TOP INFO: DATE / TIME / TITLE / MOOD / SYMPTOMS --------------
        info_frame = ctk.CTkFrame(parent)
        info_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        info_frame.grid_columnconfigure(6, weight=1)

        # section header
        info_header = ctk.CTkLabel(
            info_frame,
            text="When & how are you feeling?",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        info_header.grid(row=0, column=0, columnspan=7, padx=10, pady=(8, 2), sticky="w")

        # subtle helper text
        info_hint = ctk.CTkLabel(
            info_frame,
            text="Use your local date/time; both fields accept manual edits.",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
        )
        info_hint.grid(row=1, column=0, columnspan=7, padx=10, pady=(0, 6), sticky="w")

        # Date
        date_label = ctk.CTkLabel(info_frame, text="Date:")
        date_label.grid(row=2, column=0, padx=(10, 5), pady=5, sticky="w")

        self.date_entry = ctk.CTkEntry(
            info_frame,
            textvariable=self.date_var,
            width=120,
            placeholder_text=self.date_placeholder,
        )
        self.date_entry.grid(row=2, column=1, padx=(0, 5), pady=5, sticky="w")

        calendar_btn = ctk.CTkButton(
            info_frame, text="Today", width=70, command=self._set_today_as_date
        )
        calendar_btn.grid(row=2, column=2, padx=(0, 10), pady=5, sticky="w")

        # Time
        time_label = ctk.CTkLabel(info_frame, text="Time:")
        time_label.grid(row=2, column=3, padx=(10, 5), pady=5, sticky="w")

        self.time_entry = ctk.CTkEntry(
            info_frame,
            textvariable=self.time_var,
            width=80,
            placeholder_text=self.time_placeholder,
        )
        self.time_entry.grid(row=2, column=4, padx=(0, 5), pady=5, sticky="w")

        now_btn = ctk.CTkButton(info_frame, text="Now", width=60, command=self._fill_time_now)
        now_btn.grid(row=2, column=5, padx=(0, 10), pady=5, sticky="w")

        # Optional short title
        title_label = ctk.CTkLabel(info_frame, text="Entry title:")
        title_label.grid(row=3, column=0, padx=(10, 5), pady=(8, 5), sticky="w")

        title_entry = ctk.CTkEntry(
            info_frame,
            textvariable=self.title_var,
            width=260,
            placeholder_text=self.title_placeholder,
        )
        title_entry.grid(row=3, column=1, columnspan=3, padx=(0, 10), pady=(8, 5), sticky="ew")

        # Mood dropdown
        mood_label = ctk.CTkLabel(info_frame, text="Mood:")
        mood_label.grid(row=3, column=4, padx=(10, 5), pady=(8, 5), sticky="e")

        mood_combo = ctk.CTkComboBox(
            info_frame, values=self.mood_options, variable=self.mood_var, width=120
        )
        mood_combo.grid(row=3, column=5, padx=(0, 10), pady=(8, 5), sticky="w")

        # Symptoms single‑line
        symptoms_label = ctk.CTkLabel(info_frame, text="Symptoms (short):")
        symptoms_label.grid(row=4, column=0, padx=(10, 5), pady=(8, 10), sticky="w")

        symptoms_entry = ctk.CTkEntry(
            info_frame,
            textvariable=self.symptoms_var,
            placeholder_text=self.symptoms_placeholder,
        )
        symptoms_entry.grid(
            row=4,
            column=1,
            columnspan=5,
            padx=(0, 10),
            pady=(8, 10),
            sticky="ew",
        )

        # --- MEDICATIONS SECTION ------------------------------------------
        meds_frame = ctk.CTkFrame(parent)
        meds_frame.grid(row=3, column=0, padx=20, pady=(4, 6), sticky="nsew")
        meds_frame.grid_columnconfigure(0, weight=1)
        meds_frame.grid_columnconfigure(1, weight=0)
        meds_frame.grid_columnconfigure(2, weight=0)
        meds_frame.grid_columnconfigure(3, weight=0)
        meds_frame.grid_columnconfigure(4, weight=0)
        meds_frame.grid_columnconfigure(5, weight=0)
        meds_frame.grid_columnconfigure(6, weight=0)
        meds_frame.grid_columnconfigure(7, weight=0)

        meds_header_row = ctk.CTkFrame(meds_frame, fg_color="transparent")
        meds_header_row.grid(row=0, column=0, columnspan=8, padx=8, pady=(8, 2), sticky="ew")
        meds_header_row.grid_columnconfigure(0, weight=1)
        meds_header_row.grid_columnconfigure(1, weight=0)

        meds_label = ctk.CTkLabel(
            meds_header_row,
            text="Medications taken",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        meds_label.grid(row=0, column=0, sticky="w")

        add_med_btn = ctk.CTkButton(
            meds_header_row,
            text="+ Add medication",
            command=self._add_med_row,
            width=140,
        )
        add_med_btn.grid(row=0, column=1, sticky="e")

        meds_hint = ctk.CTkLabel(
            meds_frame,
            text="Include each HRT-related medication as its own row with dose, time, and route.",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
        )
        meds_hint.grid(row=1, column=0, columnspan=8, padx=8, pady=(0, 6), sticky="w")

        # header row
        headers = ["Name", "Dose", "Unit", "Time", "Route", "", ""]
        for col, text in enumerate(headers):
            h = ctk.CTkLabel(
                meds_frame,
                text=text,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("gray20", "gray70"),
            )
            h.grid(row=2, column=col, padx=4, pady=(0, 4), sticky="w")

        self.meds_container = meds_frame

        # --- NOTES SECTION ------------------------------------------------
        notes_outer = ctk.CTkFrame(parent)
        notes_outer.grid(row=4, column=0, padx=20, pady=10, sticky="nsew")
        notes_outer.grid_rowconfigure(1, weight=1)
        notes_outer.grid_columnconfigure(0, weight=1)

        notes_label_frame = ctk.CTkFrame(notes_outer, fg_color="transparent")
        notes_label_frame.grid(row=0, column=0, padx=0, pady=(0, 4), sticky="ew")
        notes_label_frame.grid_columnconfigure(0, weight=1)

        notes_label = ctk.CTkLabel(
            notes_label_frame,
            text="Notes (optional)",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        notes_label.grid(row=0, column=0, padx=2, pady=2, sticky="w")

        font_slider_label = ctk.CTkLabel(notes_label_frame, text="Font size:")
        font_slider_label.grid(row=0, column=1, padx=(10, 2), pady=2, sticky="e")

        font_slider = ctk.CTkSlider(
            notes_label_frame,
            from_=10,
            to=20,
            number_of_steps=10,
            variable=self.notes_font_size,
            command=self._on_font_size_change,
        )
        font_slider.grid(row=0, column=2, padx=(0, 4), pady=2, sticky="e")

        notes_hint = ctk.CTkLabel(
            notes_outer,
            text="Use this space for anything that doesn’t fit above (side effects, context, reminders).",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
            anchor="w",
            justify="left",
        )
        notes_hint.grid(row=1, column=0, padx=2, pady=(0, 4), sticky="ew")

        self.notes_text = ctk.CTkTextbox(notes_outer, width=500, height=140)
        self.notes_text.grid(row=2, column=0, padx=0, pady=(0, 4), sticky="nsew")
        self._apply_notes_font_size()

        # --- SAVE BUTTON ROW ----------------------------------------------
        save_row = ctk.CTkFrame(parent, fg_color="transparent")
        save_row.grid(row=5, column=0, padx=20, pady=(5, 20), sticky="ew")
        save_row.grid_columnconfigure(0, weight=1)

        save_btn = ctk.CTkButton(
            save_row,
            text="Save Entry",
            command=self._save_entry,
            width=140,
        )
        save_btn.grid(row=0, column=0, sticky="e")

        # start with one medication row
        self._add_med_row()

    # --- Clock / date / time helpers ------------------------------------

    def _start_clock(self):
        """Update clock label every second."""
        self._update_clock()
        self.after(1000, self._start_clock)

    def _update_clock(self):
        now = datetime.now()
        if self.show_seconds:
            self.clock_var.set(now.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            self.clock_var.set(now.strftime("%Y-%m-%d %H:%M"))

    def _prefill_date_time(self):
        now = datetime.now()
        self.date_var.set(now.strftime("%Y-%m-%d"))
        self.time_var.set(now.strftime("%H:%M"))

    def _set_today_as_date(self):
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))

    def _fill_time_now(self):
        self.time_var.set(datetime.now().strftime("%H:%M"))

    # --- Notes font size -------------------------------------------------

    def _apply_notes_font_size(self):
        size = int(self.notes_font_size.get())
        current_font = ctk.CTkFont(size=size)
        self.notes_text.configure(font=current_font)

    def _on_font_size_change(self, _value):
        self._apply_notes_font_size()

    # --- Medication rows -------------------------------------------------

    def _add_med_row(self):
        """Add a new medication row with suggestion dropdown, unit/route, 'Now' and 'Remove'."""
        row_index = len(self.medication_rows) + 3  # after headers (row 2)
        name_var = ctk.StringVar()
        dose_var = ctk.StringVar()
        unit_var = ctk.StringVar(value=self.unit_options[0])
        time_var = ctk.StringVar()
        route_var = ctk.StringVar(value=self.route_options[0])

        name_combo = ctk.CTkComboBox(
            self.meds_container,
            values=self.medication_suggestions,
            variable=name_var,
            width=170,
        )
        name_combo.grid(row=row_index, column=0, padx=4, pady=2, sticky="ew")

        dose_entry = ctk.CTkEntry(
            self.meds_container,
            textvariable=dose_var,
            width=70,
            placeholder_text="e.g. 4",
        )
        dose_entry.grid(row=row_index, column=1, padx=4, pady=2, sticky="ew")

        unit_combo = ctk.CTkComboBox(
            self.meds_container, values=self.unit_options, variable=unit_var, width=70
        )
        unit_combo.grid(row=row_index, column=2, padx=4, pady=2, sticky="ew")

        time_entry = ctk.CTkEntry(
            self.meds_container,
            textvariable=time_var,
            width=70,
            placeholder_text="HH:MM",
        )
        time_entry.grid(row=row_index, column=3, padx=4, pady=2, sticky="ew")

        route_combo = ctk.CTkComboBox(
            self.meds_container, values=self.route_options, variable=route_var, width=90
        )
        route_combo.grid(row=row_index, column=4, padx=4, pady=2, sticky="ew")

        now_btn = ctk.CTkButton(
            self.meds_container,
            text="Now",
            width=50,
            command=lambda v=time_var: v.set(datetime.now().strftime("%H:%M")),
        )
        now_btn.grid(row=row_index, column=5, padx=4, pady=2, sticky="ew")

        remove_btn = ctk.CTkButton(
            self.meds_container,
            text="Remove",
            width=70,
            command=lambda: self._remove_med_row(row_dict),
        )
        remove_btn.grid(row=row_index, column=6, padx=4, pady=2, sticky="ew")

        row_dict = {
            "frame_row": row_index,
            "name_var": name_var,
            "dose_var": dose_var,
            "unit_var": unit_var,
            "time_var": time_var,
            "route_var": route_var,
            "widgets": [
                name_combo,
                dose_entry,
                unit_combo,
                time_entry,
                route_combo,
                now_btn,
                remove_btn,
            ],
        }
        self.medication_rows.append(row_dict)

    def _remove_med_row(self, row_dict):
        """Remove a medication row and re-pack remaining rows."""
        # destroy widgets
        for w in row_dict["widgets"]:
            w.destroy()
        # remove from list
        self.medication_rows.remove(row_dict)
        # re-flow remaining rows to keep layout tidy
        for i, row in enumerate(self.medication_rows, start=0):
            new_grid_row = i + 3  # after headers
            for col, w in enumerate(row["widgets"]):
                w.grid_configure(row=new_grid_row, column=col)
            row["frame_row"] = new_grid_row

    # --- Save logic ------------------------------------------------------

    def _collect_medications(self):
        meds = []
        for row in self.medication_rows:
            name = row["name_var"].get().strip()
            dose = row["dose_var"].get().strip()
            unit = row["unit_var"].get().strip()
            time = row["time_var"].get().strip()
            route = row["route_var"].get().strip()

            if not any([name, dose, time]):
                # fully empty row, skip
                continue
            meds.append(
                {
                    "name": name,
                    "dose": dose,
                    "unit": unit,
                    "time": time,
                    "route": route,
                }
            )
        return meds

    def _save_entry(self):
        date_str = self.date_var.get().strip()
        time_str = self.time_var.get().strip()
        title = self.title_var.get().strip()
        mood = self.mood_var.get().strip()
        symptoms = self.symptoms_var.get().strip()
        notes = self.notes_text.get("1.0", "end-1c").strip()

        # Simple validation for date/time format (optional but helpful)
        if date_str:
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Validation error", "Date must be in YYYY-MM-DD format.")
                return
        if time_str:
            try:
                datetime.strptime(time_str, "%H:%M")
            except ValueError:
                messagebox.showwarning("Validation error", "Time must be in HH:MM (24h) format.")
                return

        meds = self._collect_medications()
        if not meds:
            messagebox.showwarning(
                "Validation error",
                "Please enter at least one medication (name/dose/time).",
            )
            return

        entries = self.data_manager.load_hrt_entries()
        now = datetime.now()
        entry = {
            # simple unique id based on timestamp and current length
            "id": f"{now.strftime('%Y%m%d%H%M%S')}-{len(entries)}",
            "title": title,
            "date": date_str,
            "time": time_str,
            "mood": mood,
            "symptoms": symptoms,
            "notes": notes,
            "medications": meds,
            "timestamp": now.isoformat(timespec="seconds"),
        }
        entries.append(entry)
        self.data_manager.save_hrt_entries(entries)

        messagebox.showinfo("Success", "Entry saved.")
        self._reset_form()

    def _reset_form(self):
        self._prefill_date_time()
        self.title_var.set("")
        self.mood_var.set("")
        self.symptoms_var.set("")
        self.notes_text.delete("1.0", "end")
        # remove all medication rows then add a fresh empty one
        for row in list(self.medication_rows):
            self._remove_med_row(row)
        self._add_med_row()