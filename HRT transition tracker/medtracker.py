import customtkinter as ctk
from tkinter import messagebox
import os
import json
from datetime import datetime

class DataManager:
	"""Simple file-backed JSON store for HRT entries (assets/log.json)."""
	def __init__(self, filepath):
		self.filepath = filepath
		folder = os.path.dirname(self.filepath)
		if not os.path.isdir(folder):
			os.makedirs(folder, exist_ok=True)
		if not os.path.exists(self.filepath):
			with open(self.filepath, "w", encoding="utf-8") as f:
				json.dump([], f)

	def load_hrt_entries(self):
		try:
			with open(self.filepath, "r", encoding="utf-8") as f:
				data = json.load(f)
				if isinstance(data, list):
					return data
		except Exception:
			pass
		with open(self.filepath, "w", encoding="utf-8") as f:
			json.dump([], f)
		return []

	def save_hrt_entries(self, entries):
		if entries is None:
			entries = []
		with open(self.filepath, "w", encoding="utf-8") as f:
			json.dump(entries, f, indent=2, ensure_ascii=False)

class HRTLogPage(ctk.CTkFrame):
	"""Concise hormone therapy medication logger."""

	def __init__(self, master=None):
		super().__init__(master)
		assets_file = os.path.join(os.path.dirname(__file__), "assets", "log.json")
		self.data_manager = DataManager(assets_file)

		# simple options
		self.unit_options = ["mg", "mcg", "mL", "patch", "pill"]
		self.route_options = ["oral", "sublingual", "IM", "SC", "transdermal", "gel"]

		# NEW: predefined medication dropdown options (edit as you like)
		self.medication_options = [
			"Estradiol (oral)",
			"Estradiol (sublingual)",
			"Estradiol valerate (IM)",
			"Estradiol cypionate (IM)",
			"Estradiol (gel)",
			"Estradiol (patch)",
			"Spironolactone",
			"Cyproterone acetate",
			"Bicalutamide",
			"Finasteride",
			"Dutasteride",
			"Progesterone",
			"Testosterone (gel)",
			"Testosterone cypionate (IM)",
			"Testosterone enanthate (IM)",
		]

		 # NEW: numeric dose options for dropdown (edit range/step as desired)
		self.dose_number_options = [f"{x/2:g}" for x in range(1, 21)]  # 0.5 .. 10

		# state variables
		self.date_var = ctk.StringVar()
		self.time_var = ctk.StringVar()
		self.notes_var = ctk.StringVar()
		self.med_rows = []
		self._log_window = None  # NEW: keep reference to View Log window

		# build UI
		self.columnconfigure(0, weight=1)
		self._build_ui()
		self._prefill_date_time()
		self._add_med_row()  # start with one row

	def _build_ui(self):
		row = 0
		# header
		title = ctk.CTkLabel(self, text="HRT Medication Logger", font=ctk.CTkFont(size=18, weight="bold"))
		title.grid(row=row, column=0, padx=12, pady=(12,6), sticky="w")
		row += 1

		# date/time row
		info_frame = ctk.CTkFrame(self)
		info_frame.grid(row=row, column=0, padx=12, pady=6, sticky="ew")
		info_frame.columnconfigure(3, weight=1)

		ctk.CTkLabel(info_frame, text="Date:").grid(row=0, column=0, padx=(4,2), sticky="w")
		self.date_entry = ctk.CTkEntry(info_frame, textvariable=self.date_var, width=120, placeholder_text="YYYY-MM-DD")
		self.date_entry.grid(row=0, column=1, padx=(0,8), sticky="w")

		ctk.CTkLabel(info_frame, text="Time:").grid(row=0, column=2, padx=(4,2), sticky="w")
		self.time_entry = ctk.CTkEntry(info_frame, textvariable=self.time_var, width=80, placeholder_text="HH:MM")
		self.time_entry.grid(row=0, column=3, padx=(0,4), sticky="w")
		row += 1

		# medications header + add button
		meds_header = ctk.CTkFrame(self, fg_color="transparent")
		meds_header.grid(row=row, column=0, padx=12, pady=(8,4), sticky="ew")
		meds_header.columnconfigure(0, weight=1)
		ctk.CTkLabel(meds_header, text="Medications", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w")
		ctk.CTkButton(meds_header, text="+ Add", width=80, command=self._add_med_row).grid(row=0, column=1, sticky="e")
		row += 1

		# meds container
		self.meds_container = ctk.CTkFrame(self)
		self.meds_container.grid(row=row, column=0, padx=12, pady=(0,8), sticky="ew")
		row += 1

		# notes
		ctk.CTkLabel(self, text="Notes (optional):").grid(row=row, column=0, padx=12, sticky="w")
		row += 1
		self.notes_entry = ctk.CTkTextbox(self, height=80)
		self.notes_entry.grid(row=row, column=0, padx=12, pady=(4,8), sticky="ew")
		row += 1

		# save button
		save_row = ctk.CTkFrame(self, fg_color="transparent")
		save_row.grid(row=row, column=0, padx=12, pady=(0,12), sticky="ew")
		save_row.columnconfigure(0, weight=1)

		ctk.CTkButton(save_row, text="View Log", width=120, command=self._view_log).grid(row=0, column=0, sticky="w")
		ctk.CTkButton(save_row, text="Save Entry", width=120, command=self._save_entry).grid(row=0, column=0, sticky="e")

	def _prefill_date_time(self):
		now = datetime.now()
		self.date_var.set(now.strftime("%Y-%m-%d"))
		self.time_var.set(now.strftime("%H:%M"))

	# minimal med row management
	def _add_med_row(self):
		index = len(self.med_rows)
		frame = ctk.CTkFrame(self.meds_container)
		frame.grid(row=index, column=0, pady=4, sticky="ew")
		frame.columnconfigure(7, weight=1)  # was 6

		name_var = ctk.StringVar()
		dose_var = ctk.StringVar()
		unit_var = ctk.StringVar(value=self.unit_options[0])
		time_var = ctk.StringVar()
		route_var = ctk.StringVar(value=self.route_options[0])

		# name dropdown
		name = ctk.CTkComboBox(frame, values=self.medication_options, variable=name_var, width=160)
		name.grid(row=0, column=0, padx=4, sticky="w")

		 # CHANGED: dose dropdown list of numbers
		dose = ctk.CTkComboBox(frame, values=self.dose_number_options, variable=dose_var, width=80)
		dose.grid(row=0, column=1, padx=4, sticky="w")

		unit = ctk.CTkComboBox(frame, values=self.unit_options, variable=unit_var, width=80)
		unit.grid(row=0, column=2, padx=4, sticky="w")

		route = ctk.CTkComboBox(frame, values=self.route_options, variable=route_var, width=100)
		route.grid(row=0, column=4, padx=4, sticky="w")

		rm = ctk.CTkButton(frame, text="Remove", width=80, command=lambda f=frame: self._remove_med_row(f))
		rm.grid(row=0, column=5, padx=4, sticky="e")

		self.med_rows.append({
			"frame": frame,
			"name_var": name_var,
			"dose_var": dose_var,
			"unit_var": unit_var,
			"time_var": time_var,
			"route_var": route_var,
		})

	def _remove_med_row(self, frame):
		# find and remove corresponding entry
		for r in list(self.med_rows):
			if r["frame"] == frame:
				r["frame"].destroy()
				self.med_rows.remove(r)
				break
		# re-grid remaining rows to keep order
		for i, r in enumerate(self.med_rows):
			r["frame"].grid_configure(row=i)

	def _collect_medications(self):
		meds = []
		for r in self.med_rows:
			name = r["name_var"].get().strip()
			dose = r["dose_var"].get().strip()
			unit = r["unit_var"].get().strip()
			time = r["time_var"].get().strip()
			route = r["route_var"].get().strip()
			if not any([name, dose, time]):
				continue
			meds.append({"name": name, "dose": dose, "unit": unit, "time": time, "route": route})
		return meds

	def _save_entry(self):
		date_str = self.date_var.get().strip()
		time_str = self.time_var.get().strip()
		notes = self.notes_entry.get("1.0", "end-1c").strip()

		# validate date/time formats
		if date_str:
			try:
				datetime.strptime(date_str, "%Y-%m-%d")
			except ValueError:
				messagebox.showwarning("Validation error", "Date must be YYYY-MM-DD.")
				return
		if time_str:
			try:
				datetime.strptime(time_str, "%H:%M")
			except ValueError:
				messagebox.showwarning("Validation error", "Time must be HH:MM.")
				return

		meds = self._collect_medications()
		if not meds:
			messagebox.showwarning("Validation error", "Enter at least one medication (name/dose/time).")
			return

		entries = self.data_manager.load_hrt_entries()
		now = datetime.now()
		entry = {
			"id": f"{now.strftime('%Y%m%d%H%M%S')}-{len(entries)}",
			"date": date_str,
			"time": time_str,
			"notes": notes,
			"medications": meds,
			"timestamp": now.isoformat(timespec="seconds"),
		}
		entries.append(entry)
		self.data_manager.save_hrt_entries(entries)

		messagebox.showinfo("Saved", "Entry saved.")
		self._reset_form()

	def _reset_form(self):
		self._prefill_date_time()
		self.notes_entry.delete("1.0", "end")
		for r in list(self.med_rows):
			r["frame"].destroy()
		self.med_rows.clear()
		self._add_med_row()

	def _format_entry_for_view(self, entry: dict) -> str:
		date_str = (entry.get("date") or "").strip()
		time_str = (entry.get("time") or "").strip()
		header = f"{date_str} {time_str}".strip() or (entry.get("timestamp") or "").strip() or "(no date/time)"

		lines = [header]
		for med in (entry.get("medications") or []):
			name = (med.get("name") or "").strip()
			dose = (med.get("dose") or "").strip()
			unit = (med.get("unit") or "").strip()
			route = (med.get("route") or "").strip()
			t = (med.get("time") or "").strip()

			parts = [p for p in [name, f"{dose} {unit}".strip(), route, t] if p]
			lines.append("  - " + (" | ".join(parts) if parts else "(empty medication)"))

		notes = (entry.get("notes") or "").strip()
		if notes:
			lines.append(f"  Notes: {notes}")

		return "\n".join(lines)

	def _view_log(self):
		entries = self.data_manager.load_hrt_entries()
		if not entries:
			messagebox.showinfo("View Log", "No saved entries found.")
			return

		# newest first
		text = "\n\n".join(self._format_entry_for_view(e) for e in reversed(entries))

		# NEW: if already open, just focus it
		if self._log_window is not None and self._log_window.winfo_exists():
			self._log_window.deiconify()
			self._log_window.lift()
			self._log_window.focus_force()
			return

		win = ctk.CTkToplevel(self)
		self._log_window = win  # keep reference
		win.title("Saved Logs")
		win.geometry("700x500")

		# NEW: keep on top + modal behavior until closed
		win.transient(self.winfo_toplevel())
		win.lift()
		win.focus_force()
		win.grab_set()

		def _on_close():
			try:
				win.grab_release()
			except Exception:
				pass
			self._log_window = None
			win.destroy()

		win.protocol("WM_DELETE_WINDOW", _on_close)

		# NEW: scrollable container for textbox
		body = ctk.CTkFrame(win)
		body.pack(fill="both", expand=True, padx=12, pady=12)
		body.columnconfigure(0, weight=1)
		body.rowconfigure(0, weight=1)

		tb = ctk.CTkTextbox(body)
		tb.grid(row=0, column=0, sticky="nsew")

		sb = ctk.CTkScrollbar(body, orientation="vertical", command=tb.yview)
		sb.grid(row=0, column=1, sticky="ns")

		tb.configure(yscrollcommand=sb.set)

		tb.insert("1.0", text)
		tb.configure(state="disabled")

if __name__ == "__main__":
    ctk.set_appearance_mode("System")      # optional
    ctk.set_default_color_theme("blue")    # optional

    app = ctk.CTk()
    app.title("HRT Medication Logger")
    app.geometry("700x500")

    page = HRTLogPage(app)
    page.pack(fill="both", expand=True)

    app.mainloop()
