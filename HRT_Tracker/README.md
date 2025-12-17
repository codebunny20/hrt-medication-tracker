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
  - **data_manager.py**: Handles data persistence for HRT entries and resources.
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
To set up the project, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd HRT_Tracker
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To run the application, execute the following command:
```
python app.py
```

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for details.