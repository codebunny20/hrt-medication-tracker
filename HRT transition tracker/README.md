💊 HRT Transition Tracker — Medication Logger
A compact, privacy-first GUI tool for logging hormone replacement therapy (HRT) medication events.
Built with accessibility, emotional safety, and beginner-friendly Python in mind.

🧡 Why I Built This
I've been on HRT for around 3 years and filled at least two notebooks tracking every dose, route, and time. As a left-handed person, writing has always been difficult — so I built this app to make tracking easier, safer, and more accessible.
This tool helps you log:
• 	Date and time
• 	One or more medications (name, dose, unit, route)
• 	Optional notes, mood, and symptoms
All data is stored locally in simple JSON files. No accounts, no cloud, no ads — just your data, on your device.

🖥️ Platform & License
• 	✅ Works on Windows 10 or newer
• 	🚧 Linux, Android, macOS, and iOS support in progress
• 	🆓 MIT licensed — free to use, modify, and improve
• 	🔐 All data stays local on your machine

🚀 How to Use
1. 	Launch the app to open the HRT Medication Logger window
2. 	Date and time fields are prefilled (editable)
3. 	Use + Add to insert medication rows:
• 	Name (dropdown or custom)
• 	Dose (numeric dropdown)
• 	Unit (mg, mcg, mL, patch, pill)
• 	Route (oral, sublingual, IM, SC, transdermal, gel)
• 	Optional time per row
4. 	Use Remove to delete a row
5. 	Add optional notes, mood, and symptoms
6. 	Click Save Entry to validate and save
7. 	Click View Log to browse saved entries (newest first)
✅ Validation Rules
• 	Date format: 
• 	Time format: 
• 	At least one medication name and dose/time required to save

📂 Data Storage
All entries are stored locally in 
• 	Format: list of JSON objects
• 	Location: internal folder beside the script
• 	Includes unique entry IDs and ISO timestamps
• 	Safe write strategy with optional  backups

✨ Features
• 	Predefined medication list and dose values
• 	Custom medication names supported
• 	Multiple medication rows per entry
• 	Simple validation for date/time formats
• 	Read/write JSON backend
• 	Read-only log viewer with scroll and modal behavior
• 	Lightweight GUI using CustomTkinter
• 	Keyboard shortcuts and context-aware quick-save
• 	Built-in Help and Bug Report pages
• 	Contribution page for GitHub and local planning
• 	Local-only data storage with safe write strategy
• 	Appearance settings (Light/Dark/System), inclusive language, font size, and window geometry

🛠️ Planned Features
• 	CSV export/import
• 	Per-medication reminders and scheduling
• 	Search and filter in the log viewer
• 	Linux and mobile support
• 	Optional safe mode and dysphoria-aware UI

🐣 Beginner-Friendly
I'm still learning Python and building this as I go.
If you want to contribute, fork the repo, open issues, or submit pull requests — all are welcome.

🤝 Contributing
• 	All contributions are welcome
• 	MIT license
• 	No data leaves your machine
• 	Feel free to fork, improve, or adapt for your own needs

📬 Contact & Support
• 	Bug reports: use the built-in Bug Report page
• 	Contributions: use the app’s Contribute tab or visit the GitHub repo
• 	Questions? Open an issue or reach out via GitHub