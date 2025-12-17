# HRT Tracker Application

## Overview
The HRT Tracker is an application designed to help users log and manage their Hormone Replacement Therapy (HRT) entries, track symptoms, and manage related resources. This application provides a user-friendly interface built with CustomTkinter.

## Project Structure
The project is organized into several directories and files:

- **app.py**: The main entry point of the application.
- **requirements.txt**: Lists the dependencies required for the project.
- **README.md**: Instructions and documentation for users.
- **.gitignore**: Specifies files and directories to be ignored by Git.
- **core/**: Contains the core logic of the application.
  - **settings_manager.py**: Manages application settings and themes.
  - **data_manager.py**: Handles data persistence for HRT entries, resources, and symptoms.
  - **theme_manager.py**: Manages the application's theme settings.
  - **utils.py**: Provides shared helper functions.
- **ui/**: Contains the user interface components.
  - **hrt_log_page.py**: Interface for logging HRT entries.
  - **history_page.py**: Interface for viewing historical entries.
  - **resources_page.py**: Interface for managing resources.
  - **symptoms_page.py**: Interface for tracking symptoms.
  - **settings_page.py**: Interface for adjusting theme and color settings.
  - **bug_report_page.py**: Interface for submitting bug reports.
- **assets/**: Contains icons, images, and themes.
  - **themes/**: Contains the custom theme configuration.
- **data/**: Stores user data in JSON format.
- **tests/**: Contains unit tests for core functionalities.

## Installation

From the project root:

```bash
cd "c:\Users\Admin\HRTtrackerversion2"
pip install -r HRT_Tracker/requirements.txt
```

Or from inside the `HRT_Tracker` directory:

```bash
cd "c:\Users\Admin\HRTtrackerversion2\HRT_Tracker"
pip install -r requirements.txt
```

## Usage

Run the application from either location:

- From project root:

  ```bash
  cd "c:\Users\Admin\HRTtrackerversion2"
  python HRT_Tracker/app.py
  ```

- From inside `HRT_Tracker`:

  ```bash
  cd "c:\Users\Admin\HRTtrackerversion2\HRT_Tracker"
  python app.py
  ```

The code in `app.py` adjusts `sys.path` so that `core` and `ui` imports, along with relative `data/` and `assets/` paths, work correctly in both cases.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file in the project root for details.