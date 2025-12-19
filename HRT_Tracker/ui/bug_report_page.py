import customtkinter as ctk
from tkinter import messagebox
import os
import json
import urllib.parse
from datetime import datetime

class BugReportPage(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        # precompute data dir / bug report path
        base_dir = os.path.dirname(os.path.dirname(__file__))
        self.data_dir = os.path.join(base_dir, "data")
        self.bug_reports_file = os.path.join(self.data_dir, "bug_reports.json")
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text="Bug Report", font=ctk.CTkFont(size=22, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=(20, 6), sticky="w")

        subtitle = ctk.CTkLabel(
            self,
            text="Fill in what happened as best you can. You can email, save, or copy this report.",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
            wraplength=800,
            justify="left",
        )
        subtitle.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        row = 2

        # Summary (required)
        summary_label = ctk.CTkLabel(self, text="Summary (one line):")
        summary_label.grid(row=row, column=0, padx=20, pady=(4, 2), sticky="w")

        self.summary_var = ctk.StringVar()
        self.summary_entry = ctk.CTkEntry(
            self,
            textvariable=self.summary_var,
            placeholder_text="Short title, e.g. 'Crash when saving HRT entry'",
        )
        self.summary_entry.grid(row=row + 1, column=0, padx=20, pady=(0, 6), sticky="ew")
        row += 2

        # Steps to reproduce
        steps_label = ctk.CTkLabel(self, text="Steps to reproduce:")
        steps_label.grid(row=row, column=0, padx=20, pady=(4, 2), sticky="w")
        self.steps_text = ctk.CTkTextbox(self, width=500, height=100)
        self.steps_text.insert(
            "1.0",
            "1. Open the app\n2. Go to ...\n3. Click ...\n4. Observe ...",
        )
        self.steps_text.grid(row=row + 1, column=0, padx=20, pady=(0, 6), sticky="nsew")
        self.rowconfigure(row + 1, weight=1)
        row += 2

        # Expected behavior
        expected_label = ctk.CTkLabel(self, text="Expected behavior:")
        expected_label.grid(row=row, column=0, padx=20, pady=(4, 2), sticky="w")
        self.expected_text = ctk.CTkTextbox(self, width=500, height=60)
        self.expected_text.grid(row=row + 1, column=0, padx=20, pady=(0, 6), sticky="ew")
        row += 2

        # Actual behavior
        actual_label = ctk.CTkLabel(self, text="Actual behavior:")
        actual_label.grid(row=row, column=0, padx=20, pady=(4, 2), sticky="w")
        self.actual_text = ctk.CTkTextbox(self, width=500, height=60)
        self.actual_text.grid(row=row + 1, column=0, padx=20, pady=(0, 6), sticky="ew")
        row += 2

        # Environment
        env_label = ctk.CTkLabel(self, text="Environment (OS, app version, anything relevant):")
        env_label.grid(row=row, column=0, padx=20, pady=(4, 2), sticky="w")
        self.environment_text = ctk.CTkTextbox(self, width=500, height=60)
        self.environment_text.insert("1.0", "e.g. Windows 11, Python 3.11, app downloaded from ...")
        self.environment_text.grid(row=row + 1, column=0, padx=20, pady=(0, 6), sticky="ew")
        row += 2

        # Optional logs / screenshots note
        logs_label = ctk.CTkLabel(self, text="Optional extra details / log snippet:")
        logs_label.grid(row=row, column=0, padx=20, pady=(4, 2), sticky="w")
        self.logs_text = ctk.CTkTextbox(self, width=500, height=80)
        self.logs_text.grid(row=row + 1, column=0, padx=20, pady=(0, 10), sticky="ew")
        row += 2

        # Buttons row
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=row, column=0, padx=20, pady=(0, 16), sticky="w")

        email_btn = ctk.CTkButton(
            btn_frame,
            text="Open Email",
            command=self._open_email_client,
            width=110,
        )
        email_btn.grid(row=0, column=0, padx=(0, 8), pady=4)

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save Locally",
            command=self._save_report_locally,
            width=110,
        )
        save_btn.grid(row=0, column=1, padx=(0, 8), pady=4)

        copy_btn = ctk.CTkButton(
            btn_frame,
            text="Copy to Clipboard",
            command=self._copy_report_to_clipboard,
            width=140,
        )
        copy_btn.grid(row=0, column=2, padx=(0, 8), pady=4)

        clear_btn = ctk.CTkButton(
            btn_frame,
            text="Clear Form",
            command=self._clear_form,
            width=100,
        )
        clear_btn.grid(row=0, column=3, padx=(0, 0), pady=4)

    # --- helpers: build report -------------------------------------------

    def _get_report_payload(self):
        """Collect form data into a dict and formatted text."""
        summary = (self.summary_var.get() or "").strip()
        if not summary:
            return None, None

        steps = self.steps_text.get("1.0", "end-1c").strip()
        expected = self.expected_text.get("1.0", "end-1c").strip()
        actual = self.actual_text.get("1.0", "end-1c").strip()
        environment = self.environment_text.get("1.0", "end-1c").strip()
        logs = self.logs_text.get("1.0", "end-1c").strip()
        created_at = datetime.now().isoformat(timespec="seconds")

        payload = {
            "summary": summary,
            "steps": steps,
            "expected": expected,
            "actual": actual,
            "environment": environment,
            "logs": logs,
            "created_at": created_at,
        }

        # Build a readable template
        lines = [
            f"Summary: {summary}",
            "",
            "Steps to reproduce:",
            steps or "(not provided)",
            "",
            "Expected behavior:",
            expected or "(not provided)",
            "",
            "Actual behavior:",
            actual or "(not provided)",
            "",
            "Environment:",
            environment or "(not provided)",
            "",
            "Extra details / logs:",
            logs or "(not provided)",
            "",
            f"Report created at: {created_at}",
        ]
        text = "\n".join(lines)
        return payload, text

    def _require_payload(self):
        payload, text = self._get_report_payload()
        if payload is None:
            messagebox.showwarning("Bug Report", "Please enter at least a one-line summary.")
        return payload, text

    # --- helpers: storage ------------------------------------------------

    def _load_existing_reports(self):
        if not os.path.exists(self.bug_reports_file):
            return []
        try:
            with open(self.bug_reports_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return []
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "reports" in data and isinstance(data["reports"], list):
            return data["reports"]
        return []

    def _save_reports_list(self, reports):
        os.makedirs(self.data_dir, exist_ok=True)
        # store as simple list for now
        with open(self.bug_reports_file, "w", encoding="utf-8") as f:
            json.dump(reports, f, indent=4, ensure_ascii=False)

    # --- helpers: actions ------------------------------------------------

    def _open_email_client(self):
        import webbrowser

        payload, text = self._require_payload()
        if payload is None:
            return

        to_addr = "bunnycontact.me@gmail.com"
        subject = f"HRT Tracker bug: {payload['summary']}"
        # URL‑encode subject/body
        params = {
            "subject": subject,
            "body": text,
        }
        query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        mailto_url = f"mailto:{to_addr}?{query}"
        try:
            webbrowser.open(mailto_url)
        except Exception as e:
            messagebox.showerror("Bug Report", f"Could not open email client:\n{e}")
            return

        messagebox.showinfo(
            "Bug Report",
            "Your email client should now be open with the bug report prefilled.\n"
            "You can review it and send when ready.",
        )

    def _save_report_locally(self):
        payload, _text = self._require_payload()
        if payload is None:
            return

        try:
            reports = self._load_existing_reports()
            reports.append(payload)
            self._save_reports_list(reports)
        except OSError as e:
            messagebox.showerror("Bug Report", f"Could not save report:\n{e}")
            return

        messagebox.showinfo("Bug Report", "Bug report saved to bug_reports.json in the data folder.")

    def _copy_report_to_clipboard(self):
        _payload, text = self._require_payload()
        if _payload is None:
            return

        try:
            # use the top-level Tk clipboard via this frame
            self.clipboard_clear()
            self.clipboard_append(text)
        except Exception as e:
            messagebox.showerror("Bug Report", f"Could not copy report to clipboard:\n{e}")
            return

        messagebox.showinfo("Bug Report", "Bug report copied to clipboard.")

    def _clear_form(self):
        self.summary_var.set("")
        self.steps_text.delete("1.0", "end")
        self.expected_text.delete("1.0", "end")
        self.actual_text.delete("1.0", "end")
        self.environment_text.delete("1.0", "end")
        self.logs_text.delete("1.0", "end")
        messagebox.showinfo("Bug Report", "Form cleared.")

    # optional hook for consistency with other pages
    def on_show(self):
        try:
            self.summary_entry.focus_set()
            self.summary_entry.icursor("end")
        except Exception:
            pass
