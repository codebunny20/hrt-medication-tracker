# HRT Transition Tracker — Medication Logger

## Intro
A compact GUI tool to log hormone replacement therapy (HRT) medication events. Record date, time, one or more medications with dose, unit, route and optional notes. Entries are saved to a simple JSON file for later review. Iv'e put this together to help keep track of when, how, medication was taken, what was taken and the dose/amount taken. ive been on my hrt for around 3 years and ive filled at least two note books with this information and im left handed so writing has always been difficult so I wanted to make tracking medications easier.

## Note
    this will only work on windows 10 or newer-im working on expanding this tool to linux, android, Mac, Ios.

    Im still a begginer with python and im still learning this project is MIT licensed and all info stays on your local machine so feel free to altre, improve, and make changes.

## Help
- Launch the application to open the HRT Medication Logger window.
- Date and Time fields are prefilled; edit them if needed (Date: YYYY-MM-DD, Time: HH:MM).
- Use "+ Add" to add medication rows. For each medication select:
  - Medication name (from the dropdown or type to add custom)
  - Dose (numeric dropdown)
  - Unit (mg, mcg, mL, patch, pill)
  - Route (oral, sublingual, IM, SC, transdermal, gel)
  - Optional time for the medication row
- Use "Remove" to delete a medication row.
- Enter optional notes in the Notes box.
- Click "Save Entry" to validate and persist the entry to assets/log.json.
- Click "View Log" to open a read-only window with saved entries (newest first).

Validation:
- Date must be YYYY-MM-DD.
- Time must be HH:MM.
- At least one medication must include a name and dose/time to save.

Data storage:
- Saved entries are stored as a list of JSON objects in `assets/log.json` located in the _internal file beside the script.

## Features
- Predefined medication list and dose values with ability to type custom names.
- Multiple medication rows per entry.
- Simple validation of date and time formats.
- Read/write JSON backend with unique entry IDs and ISO timestamps.
- Read-only log viewer with scroll and modal behavior.
- Small, dependency-light GUI using customtkinter for a modern appearance.

## Notes & Future Features
- Add CSV export / import.
- Add per-medication reminders / scheduling.
- Add search and filter in the log viewer.
