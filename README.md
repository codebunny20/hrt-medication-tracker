# HRTtrackerversion2

Desktop HRT tracker built with CustomTkinter.

- Logs HRT entries to `HRT_Tracker/data/hrt_entries.json`.
- Tracks symptoms in `HRT_Tracker/data/symptoms.json`.
- Manages resources in `HRT_Tracker/data/hrt_resources.json`.
- Persists app settings (theme, accent color, etc.) in `HRT_Tracker/data/app_settings.json`.

## Setup

1. Open a terminal in the project root folder:

   ```bash
   cd "c:\Users\Admin\HRTtrackerversion2"
   ```

2. (Optional but recommended) create and activate a virtualenv:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependencies (requirements are in the `HRT_Tracker` folder):

   ```bash
   pip install -r HRT_Tracker/requirements.txt
   ```

## Running the app

You can run the app from either directory; imports and data paths will work in both cases:

- From the project root:

  ```bash
  cd "c:\Users\Admin\HRTtrackerversion2"
  python HRT_Tracker/app.py
  ```

- Or from inside `HRT_Tracker`:

  ```bash
  cd "c:\Users\Admin\HRTtrackerversion2\HRT_Tracker"
  python app.py
  ```

The app windows use the JSON files under `HRT_Tracker/data/` and the theme under `HRT_Tracker/assets/themes/custom_theme.json`.

