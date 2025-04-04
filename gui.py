import sys
import os
import json
import pygame  # Wird hier für den Sound-Test genutzt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QMessageBox, QHBoxLayout, QSpinBox, QGroupBox, QCheckBox
)
from settings_module import save_settings

SETTINGS_FILE = "settings.json"
ICON_PATH = "legends_welcome.png"  # Stelle sicher, dass dies ein gültiger Icon-Pfad ist!
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_FILE = os.path.join(BASE_DIR, "Sounds", "error-126627.mp3")



def load_settings():
    """Lädt die Einstellungen und stellt sicher, dass alle Schlüssel vorhanden sind."""
    default_settings = {
        "whitelist_monster": [],
        "whitelist_player": [],
        "blacklist_player": [],  # Neue Einstellung für die Player Blacklist
        "gm_warning": False,
        "monster": {"click_delay": 500},
        "player": {"click_delay": 500}
    }

    try:
        with open(SETTINGS_FILE, "r") as file:
            settings = json.load(file)
            # Fehlende Schlüssel mit Standardwerten ergänzen
            for key in default_settings:
                if key not in settings:
                    settings[key] = default_settings[key]
            return settings
    except (FileNotFoundError, json.JSONDecodeError):
        return default_settings


class SettingsWindow(QWidget):
    """OCR-Settings-Fenster mit GM Warning, separater Whitelist und Player Blacklist."""

    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Settings for Mouseclick-OCR")
        self.setGeometry(300, 200, 800, 550)
        self.setWindowIcon(QIcon(ICON_PATH))

        main_layout = QVBoxLayout()

        # Layout für Whitelist und Blacklist (drei Spalten)
        lists_layout = QHBoxLayout()

        self.monster_whitelist_group = self.create_whitelist_group("Monster")
        lists_layout.addWidget(self.monster_whitelist_group)

        self.player_whitelist_group = self.create_whitelist_group("Player")
        lists_layout.addWidget(self.player_whitelist_group)

        self.player_blacklist_group = self.create_blacklist_group()
        lists_layout.addWidget(self.player_blacklist_group)

        main_layout.addLayout(lists_layout)

        # Layout für Einstellungen (Monster & Player)
        settings_layout = QHBoxLayout()
        self.monster_settings_group = self.create_settings_group("Monster")
        settings_layout.addWidget(self.monster_settings_group)

        self.player_settings_group = self.create_settings_group("Player")
        settings_layout.addWidget(self.player_settings_group)

        main_layout.addLayout(settings_layout)

        # GM Warning Checkbox
        self.gm_warning_checkbox = QCheckBox("activate GM Warning")
        self.gm_warning_checkbox.setChecked(self.settings["gm_warning"])
        self.gm_warning_checkbox.stateChanged.connect(self.toggle_gm_warning)
        main_layout.addWidget(self.gm_warning_checkbox)

        # Button zum Testen des Fehler-Sounds (wird nur ausgeführt, wenn GM Warning aktiviert ist)
        test_sound_button = QPushButton("Sound Test")
        test_sound_button.clicked.connect(self.test_sound)
        main_layout.addWidget(test_sound_button)

        # Speichern-Button
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self.save_changes)
        main_layout.addWidget(save_button)

        self.setLayout(main_layout)

    def create_whitelist_group(self, title):
        """Erstellt eine Gruppierung für Monster- oder Player-Whitelist."""
        group_box = QGroupBox(f"{title} Whitelist")
        layout = QVBoxLayout()

        whitelist_list = QListWidget()
        whitelist_list.addItems(self.settings[f"whitelist_{title.lower()}"])
        layout.addWidget(whitelist_list)

        name_layout = QHBoxLayout()
        name_input = QLineEdit()
        name_input.setPlaceholderText(f"New {title}-Name")
        name_layout.addWidget(name_input)

        add_button = QPushButton("Add")
        add_button.clicked.connect(lambda: self.add_name(title.lower(), name_input, whitelist_list))
        name_layout.addWidget(add_button)

        layout.addLayout(name_layout)

        remove_button = QPushButton("Delete")
        remove_button.clicked.connect(lambda: self.remove_name(title.lower(), whitelist_list))
        layout.addWidget(remove_button)

        group_box.setLayout(layout)

        setattr(self, f"{title.lower()}_whitelist_list", whitelist_list)
        setattr(self, f"{title.lower()}_name_input", name_input)

        return group_box

    def create_blacklist_group(self):
        """Erstellt eine Gruppierung für die Player Blacklist."""
        group_box = QGroupBox("Player Blacklist")
        layout = QVBoxLayout()

        blacklist_list = QListWidget()
        blacklist_list.addItems(self.settings["blacklist_player"])
        layout.addWidget(blacklist_list)

        name_layout = QHBoxLayout()
        name_input = QLineEdit()
        name_input.setPlaceholderText("New Player-Name")
        name_layout.addWidget(name_input)

        add_button = QPushButton("Add")
        add_button.clicked.connect(lambda: self.add_blacklist_name(name_input, blacklist_list))
        name_layout.addWidget(add_button)

        layout.addLayout(name_layout)

        remove_button = QPushButton("Delete")
        remove_button.clicked.connect(lambda: self.remove_blacklist_name(blacklist_list))
        layout.addWidget(remove_button)

        group_box.setLayout(layout)

        self.player_blacklist_list = blacklist_list
        self.player_blacklist_input = name_input

        return group_box

    def add_name(self, category, name_input, list_widget):
        """Fügt einen neuen Namen zur Whitelist hinzu."""
        new_name = name_input.text().strip()
        if not new_name:
            QMessageBox.warning(self, "Fail", "Field does not be empty!")
            return
        if new_name in self.settings[f"whitelist_{category}"]:
            QMessageBox.warning(self, "Fail", f"{new_name} still be in Whitelist!")
            return
        self.settings[f"whitelist_{category}"].append(new_name)
        list_widget.addItem(new_name)
        name_input.clear()
        save_settings(self.settings)

    def remove_name(self, category, list_widget):
        """Entfernt den ausgewählten Namen aus der Whitelist."""
        selected_item = list_widget.currentItem()
        if selected_item:
            name = selected_item.text()
            self.settings[f"whitelist_{category}"].remove(name)
            list_widget.takeItem(list_widget.row(selected_item))
            save_settings(self.settings)
        else:
            QMessageBox.warning(self, "Fail", "Please choose a Name!")

    def add_blacklist_name(self, name_input, list_widget):
        """Fügt einen neuen Namen zur Player Blacklist hinzu."""
        new_name = name_input.text().strip()
        if not new_name:
            QMessageBox.warning(self, "Fail", "Field does not be empty!")
            return
        if new_name in self.settings["blacklist_player"]:
            QMessageBox.warning(self, "Fail", f"{new_name} still be in Blacklist!")
            return
        self.settings["blacklist_player"].append(new_name)
        list_widget.addItem(new_name)
        name_input.clear()
        save_settings(self.settings)

    def remove_blacklist_name(self, list_widget):
        """Entfernt den ausgewählten Namen aus der Player Blacklist."""
        selected_item = list_widget.currentItem()
        if selected_item:
            name = selected_item.text()
            self.settings["blacklist_player"].remove(name)
            list_widget.takeItem(list_widget.row(selected_item))
            save_settings(self.settings)
        else:
            QMessageBox.warning(self, "Fail", "Please Choose a Name!")

    def create_settings_group(self, title):
        """Erstellt eine Gruppierung für Monster- oder Player-Einstellungen."""
        group_box = QGroupBox(f"{title} Settings")
        layout = QVBoxLayout()

        delay_label = QLabel("Click-Delay (ms):")
        layout.addWidget(delay_label)

        delay_input = QSpinBox()
        delay_input.setRange(100, 5000)
        delay_input.setSingleStep(100)
        delay_input.setValue(self.settings[title.lower()]["click_delay"])
        layout.addWidget(delay_input)

        save_button = QPushButton("Save")
        save_button.clicked.connect(lambda: self.save_individual_settings(title.lower()))
        layout.addWidget(save_button)

        group_box.setLayout(layout)
        setattr(self, f"{title.lower()}_delay_input", delay_input)
        return group_box

    def toggle_gm_warning(self):
        """Aktiviert oder deaktiviert die GM Warning-Funktion."""
        self.settings["gm_warning"] = self.gm_warning_checkbox.isChecked()
        save_settings(self.settings)

    def save_individual_settings(self, category):
        """Speichert die individuellen Einstellungen für Monster oder Player."""
        self.settings[category]["click_delay"] = getattr(self, f"{category}_delay_input").value()
        save_settings(self.settings)
        QMessageBox.information(self, "Saved", f"{category.capitalize()}-Settings are saved!")

    def save_changes(self):
        """Speichert alle Änderungen."""
        save_settings(self.settings)
        QMessageBox.information(self, "Saved", "Settings are updated!.")

    def test_sound(self):
        """Testet das Abspielen des Fehler-Sounds, falls GM Warning aktiviert ist."""
        if self.settings["gm_warning"]:
            try:
                # Prüfen, ob die Sound-Datei existiert:
                if not os.path.exists(SOUND_FILE):
                    QMessageBox.warning(self, "Fail!", f"Sound-File not found:\n{SOUND_FILE}")
                    return

                # Initialisiere den Mixer, falls nicht bereits initialisiert:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(SOUND_FILE)
                pygame.mixer.music.play()
            except Exception as e:
                QMessageBox.warning(self, "Fail", f"Fail to play the Sounds: {e}")
        else:
            QMessageBox.information(self, "Info", "GM Warning is not activated.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec())
