import os
import customtkinter as ctk

class HelpPage(ctk.CTkFrame):
    """Read‑only help explaining how the app works, data locations, and tips."""

    def __init__(self, master=None):
        super().__init__(master)
        self._build_ui()

    def _build_ui(self):
        # scrollable container (similar pattern as other pages)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        canvas = ctk.CTkCanvas(self, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)

        inner = ctk.CTkFrame(canvas)
        window = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_frame_configure(_event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event):
            canvas.itemconfigure(window, width=event.width)

        inner.bind("<Configure>", _on_frame_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        # optional mouse wheel support
        self._bind_mousewheel(canvas)

        # actual help content
        inner.columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            inner,
            text="Help & Guide",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        title.grid(row=0, column=0, padx=20, pady=(20, 6), sticky="w")

        subtitle = ctk.CTkLabel(
            inner,
            text=(
                "This page explains what each part of the HRT Tracker does, "
                "where your data is stored, and some common troubleshooting tips."
            ),
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
            wraplength=800,
            justify="left",
        )
        subtitle.grid(row=1, column=0, padx=20, pady=(0, 12), sticky="w")

        row = 2

        # 1. Overview
        row = self._section_header(inner, row, "1. What the app does")
        overview_text = (
            "- Log HRT: record doses, timing, mood, symptoms, and detailed notes.\n"
            "- Symptoms: quickly track how your body and mood feel, with context fields.\n"
            "- History: view a combined timeline of HRT and symptom entries, search, filter, export.\n"
            "- Resources: keep useful links and notes for HRT‑related information.\n"
            "- Settings: appearance (light/dark/system) and basic app settings.\n"
            "- Bug Report: send yourself a description of issues you run into."
        )
        row = self._section_body(inner, row, overview_text)

        # 2. Page explanations
        row = self._section_header(inner, row, "2. Page‑by‑page explanation")

        # Log HRT
        row = self._subsection_header(inner, row, "2.1 Log HRT")
        log_text = (
            "Use this page whenever you take HRT:\n"
            "• Date / Time: pre‑filled with now; you can type over them.\n"
            "• Entry title: optional short label (e.g. “Morning dose”).\n"
            "• Mood / Symptoms: quick, single‑line context fields.\n"
            "• Medications table:\n"
            "  - Each row is one medication (e.g. Estradiol, Spironolactone).\n"
            "  - Fill name, dose + unit, time, and route.\n"
            "  - “+ Add medication” to add more rows; “Remove” to delete a row.\n"
            "  - The “Now” button fills the row’s time with the current time.\n"
            "• Notes: free‑form text area for anything that doesn’t fit elsewhere; "
            "  use the slider to change the font size.\n"
            "When you click “Save Entry”, the app validates that there is at least "
            "one medication row with some content and then stores everything in the "
            "HRT entries file."
        )
        row = self._section_body(inner, row, log_text)

        # Symptoms
        row = self._subsection_header(inner, row, "2.2 Symptoms")
        symptoms_text = (
            "Use this page when you want to capture how you feel, without "
            "necessarily tying it to a dose:\n"
            "• Common symptoms: tick anything that applies.\n"
            "• Mood & daily state: dropdowns for mood, energy, and sleep quality.\n"
            "• Short notes: quick one‑line fields for dysphoria, euphoria, or other notes.\n"
            "• Anything else: a larger textbox for body sensations, emotional context, "
            "  cycle timing, etc.\n"
            "Click “Record symptoms” to save:\n"
            "• A flat symptom list used for the sidebar “recent symptoms” view.\n"
            "• A grouped symptom entry that appears in the History timeline.\n"
            "“Clear selections” resets the current form; “Clear recorded entries” only "
            "clears the flat symptom list, not the History log."
        )
        row = self._section_body(inner, row, symptoms_text)

        # History
        row = self._subsection_header(inner, row, "2.3 History")
        history_text = ( 
            "note: if you dont see the entrie you saved press the refresh button.\n"
            "The History page shows a combined list of HRT entries and grouped "
            "symptom entries.\n"
            "• Search: finds text across titles, mood, symptoms, notes, medications, and dates.\n"
            "• Start / End date: filters entries in a given date range (YYYY‑MM‑DD).\n"
            "• Filter / Clear / Refresh:\n"
            "  - Filter: apply current search + dates.\n"
            "  - Clear: remove filters and show everything.\n"
            "  - Refresh: reload from disk in case files were edited externally.\n"
            "• Export: save the current filtered list as a CSV file for spreadsheets.\n"
            "• Left pane: a scrollable summary list; select an item to see details.\n"
            "• Right pane: full details, including medications and notes.\n"
            "• Delete: permanently remove an entry (HRT or symptoms) from disk.\n"
            "• Duplicate: create a copy of the selected entry with a new ID and timestamp."
        )
        row = self._section_body(inner, row, history_text)

        # Resources
        row = self._subsection_header(inner, row, "2.4 Resources")
        resources_text = (
            "A lightweight bookmark list for links, hotlines, or documents you find helpful.\n"
            "• Search: filters by name, description, link, or tags.\n"
            "• Add / Edit: open a small dialog where you can set:\n"
            "  - Name (required).\n"
            "  - Link (URL – optional; “Open” uses this).\n"
            "  - Description and tags (comma‑separated labels).\n"
            "• Open: opens the selected resource’s link in your default browser.\n"
            "• Remove: delete the selected resource from the list."
        )
        row = self._section_body(inner, row, resources_text)

        # Settings
        row = self._subsection_header(inner, row, "2.5 Settings")
        settings_text = (
            "Control basic appearance and defaults:\n"
            "• Theme: choose Light, Dark, or System; the change is applied immediately.\n"
            "The app also stores an accent color internally; future versions may expose more "
            "appearance and behavior options here.\n"
            "Settings are saved to the app_settings.json file in the data folder."
        )
        row = self._section_body(inner, row, settings_text)

        # Bug Report
        row = self._subsection_header(inner, row, "2.6 Bug Report")
        bug_text = (
            "A simple page for jotting down issues you notice.\n"
            "• Type a description in the textbox.\n"
            "• Press “Submit” to clear the text and show a confirmation.\n"
            "In your own setup you can wire this to email, a file, or an issue tracker."
        )
        row = self._section_body(inner, row, bug_text)

        # 3. Where your data lives
        row = self._section_header(inner, row, "3. Where your data is stored")

        base_dir = os.path.dirname(os.path.dirname(__file__))
        data_dir = os.path.join(base_dir, "data")
        hrt_entries_path = os.path.join(data_dir, "hrt_entries.json")
        symptom_entries_path = os.path.join(data_dir, "symptom_entries.json")
        flat_symptoms_path = os.path.join(data_dir, "symptoms.json")
        resources_path = os.path.join(data_dir, "hrt_resources.json")
        settings_path = os.path.join(data_dir, "app_settings.json")

        data_text = (
            "All data stays on your machine in JSON files. The default locations are:\n"
            f"• HRT entries: {hrt_entries_path}\n"
            f"• Grouped symptom entries (History): {symptom_entries_path}\n"
            f"• Flat symptom list (Symptoms page sidebar): {flat_symptoms_path}\n"
            f"• Resources: {resources_path}\n"
            f"• Settings (theme and more): {settings_path}\n\n"
            "You can back up the app by copying the entire project folder or just the "
            "HRT_Tracker/data/ directory. Deleting one of these files will reset that "
            "part of the app the next time it runs (a new file is created automatically)."
        )
        row = self._section_body(inner, row, data_text)

        # 4. Troubleshooting
        row = self._section_header(inner, row, "4. Troubleshooting tips")
        troubleshoot_text = (
            "• The app won’t start:\n"
            "  - Make sure you installed dependencies with:\n"
            "    pip install -r HRT_Tracker/requirements.txt\n"
            "  - Run the app from the project root or from inside HRT_Tracker as shown in README.\n\n"
            "• A page looks blank or errors appear when saving:\n"
            "  - Check that the JSON files under HRT_Tracker/data/ are valid. If one looks "
            "    corrupted, you can rename it (to keep a backup) and restart the app to let "
            "    it create a fresh file.\n\n"
            "• I can’t find my older entries:\n"
            "  - Try clearing filters in History.\n"
            "  - Make sure the HRT_Tracker/data directory hasn’t been moved or deleted.\n\n"
            "• I want to move the app to another machine:\n"
            "  - Copy the entire project folder (especially the HRT_Tracker/data directory) "
            "    to the new machine and install Python + requirements there."
        )
        row = self._section_body(inner, row, troubleshoot_text)

        # 5. Keyboard / navigation hints (basic)
        row = self._section_header(inner, row, "5. Navigation tips")
        nav_text = (
            "• Use the buttons at the top to switch between pages.\n"
            "• On long pages (Log HRT, Symptoms, Help), use the mouse wheel or trackpad to scroll.\n"
            "• Some fields (like date/time) get focus automatically when you open a page, so "
            "you can start typing right away."
        )
        row = self._section_body(inner, row, nav_text)

    # ---- small helpers for styling sections -----------------------------

    def _section_header(self, parent, row, text):
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        label.grid(row=row, column=0, padx=20, pady=(12, 4), sticky="w")
        return row + 1

    def _subsection_header(self, parent, row, text):
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        label.grid(row=row, column=0, padx=26, pady=(8, 2), sticky="w")
        return row + 1

    def _section_body(self, parent, row, text):
        body = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=11),
            justify="left",
            wraplength=800,
            anchor="w",
        )
        body.grid(row=row, column=0, padx=32, pady=(0, 2), sticky="w")
        return row + 1

    # --- simple mouse‑wheel support --------------------------------------

    def _on_mousewheel(self, event, canvas):
        if event.num == 4:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            canvas.yview_scroll(1, "units")
        else:
            direction = -1 if event.delta > 0 else 1
            canvas.yview_scroll(direction, "units")

    def _bind_mousewheel(self, widget):
        widget.bind("<Enter>", lambda _e: self._enable_mousewheel(widget))
        widget.bind("<Leave>", lambda _e: self._disable_mousewheel(widget))

    def _enable_mousewheel(self, widget):
        widget.bind_all("<MouseWheel>", lambda e: self._on_mousewheel(e, widget))
        widget.bind_all("<Button-4>", lambda e: self._on_mousewheel(e, widget))
        widget.bind_all("<Button-5>", lambda e: self._on_mousewheel(e, widget))

    def _disable_mousewheel(self, widget):
        widget.unbind_all("<MouseWheel>")
        widget.unbind_all("<Button-4>")
        widget.unbind_all("<Button-5>")

    # optional hook so app can call on_show like other pages
    def on_show(self):
        pass
