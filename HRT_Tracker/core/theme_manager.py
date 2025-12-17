import json
import os

class ThemeManager:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        self.theme_file = os.path.join(base_dir, "assets", "themes", "custom_theme.json")
        self.theme = self.load_theme()

    def load_theme(self):
        # Load the theme from the custom_theme.json file
        if os.path.exists(self.theme_file):
            with open(self.theme_file, "r") as f:
                data = json.load(f)
            # expect {"theme": {...}}
            if isinstance(data, dict) and "theme" in data:
                return data["theme"]
            return data
        # sensible default if file missing
        return {
            "primary_color": "#3498db",
            "secondary_color": "#2ecc71",
            "background_color": "#ecf0f1",
            "text_color": "#2c3e50",
            "accent_color": "#e74c3c",
            "font": {"family": "Arial, sans-serif", "size": "14px"},
        }

    def save_theme(self, theme=None):
        # Save the current theme to the custom_theme.json file
        if theme is not None:
            self.theme = theme
        os.makedirs(os.path.dirname(self.theme_file), exist_ok=True)
        with open(self.theme_file, "w") as f:
            json.dump({"theme": self.theme}, f, indent=4)

    def set_accent_color(self, color):
        # Set the accent color for the application
        self.theme["accent_color"] = color
        self.save_theme()

    def set_background(self, background):
        # Set the background for the application
        self.theme["background_color"] = background
        self.save_theme()

    def get_theme(self):
        # Return the current theme settings
        return self.theme