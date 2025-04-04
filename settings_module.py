import json

SETTINGS_FILE = "settings.json"

def load_settings():
    """Lädt die Einstellungen aus der JSON-Datei."""
    default_settings = {
        "whitelist_monster": [],
        "whitelist_player": [],
        "click_delay_monster": 0.5,
        "click_delay_player": 0.5
    }

    try:
        with open(SETTINGS_FILE, "r") as file:
            settings = json.load(file)

            # Falls Schlüssel fehlen, ergänze sie mit Standardwerten
            for key, value in default_settings.items():
                if key not in settings:
                    settings[key] = value

            return settings
    except (FileNotFoundError, json.JSONDecodeError):
        return default_settings

def save_settings(settings):
    """Speichert die Einstellungen in die JSON-Datei."""
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file, indent=4)
