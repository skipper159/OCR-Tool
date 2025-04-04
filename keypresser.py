import sys
import json
import threading
import time
import random
import pyautogui
import pygetwindow as gw
import traceback
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QCheckBox, QSpinBox, QHBoxLayout, QComboBox
)
from PyQt6.QtCore import QTimer

SETTINGS_FILE = "keypresser_settings.json"

class KeyPresser(QWidget):
    """GUI zum automatischen Drücken der Tasten 1-9 in einem bestimmten Fenster."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("KeyPresser - Automatic key input")
        self.setGeometry(400, 200, 450, 500)
        self.setWindowIcon(QIcon("Legends_welcome.png"))  # Favicon hinzufügen

        self.running = False  # Steuerung des Keypress-Threads
        self.thread = None
        self.target_window = None  # Referenz auf das Ziel-Fenster
        self.target_window_title = ""  # Speichert nur den Fenstertitel
        self.load_settings()

        layout = QVBoxLayout()

        # Status Label
        self.status_label = QLabel("Status: stopped")
        layout.addWidget(self.status_label)

        # Fenster-Auswahl
        self.window_selector = QComboBox()
        self.window_selector.currentIndexChanged.connect(self.set_target_window)
        self.update_window_list()
        layout.addWidget(self.window_selector)

        # Aktualisieren-Button für Fensterliste
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.update_window_list)
        layout.addWidget(refresh_button)

        # Erstelle Kontrollkästchen + Geschwindigkeits-Einstellung für jede Taste
        self.checkboxes = {}
        self.spinboxes = {}

        for i in range(1, 10):  # Tasten 1-9
            row_layout = QHBoxLayout()

            checkbox = QCheckBox(f"Key {i}")
            checkbox.setChecked(self.settings[str(i)]["enabled"])
            self.checkboxes[i] = checkbox
            row_layout.addWidget(checkbox)

            arrow_label = QLabel("\u2193")  # Pfeil nach unten hinzufügen
            row_layout.addWidget(arrow_label)

            spinbox = QSpinBox()
            spinbox.setRange(100, 5000)  # 100ms bis 5000ms
            spinbox.setSingleStep(50)
            spinbox.setValue(self.settings[str(i)]["delay"])
            spinbox.setSuffix(" ms")  # Einheit hinzufügen
            self.spinboxes[i] = spinbox
            row_layout.addWidget(spinbox)

            layout.addLayout(row_layout)

        # Start-Button
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_pressing)
        layout.addWidget(self.start_button)

        # Stopp-Button
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_pressing)
        layout.addWidget(self.stop_button)

        # Einstellungen speichern
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def load_settings(self):
        """Lädt die gespeicherten Einstellungen aus der JSON-Datei."""
        try:
            with open(SETTINGS_FILE, "r") as file:
                self.settings = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = {str(i): {"enabled": False, "delay": 1000} for i in range(1, 10)}
            self.save_settings()

    def save_settings(self):
        """Speichert die aktuellen Einstellungen in die JSON-Datei."""
        for i in range(1, 10):
            self.settings[str(i)] = {
                "enabled": self.checkboxes[i].isChecked(),
                "delay": self.spinboxes[i].value()
            }

        with open(SETTINGS_FILE, "w") as file:
            json.dump(self.settings, file, indent=4)

    def update_window_list(self):
        """Aktualisiert die Liste der offenen Fenster."""
        try:
            windows = gw.getAllWindows()
            self.window_selector.clear()
            for window in windows:
                if window.title:
                    # Nur den Fenstertitel anzeigen – ohne Koordinaten.
                    self.window_selector.addItem(window.title, window.title)
        except Exception:
            print(f"[SYSTEM] ❌ Fehler beim Aktualisieren der Fensterliste:\n{traceback.format_exc()}")

    def set_target_window(self):
        """Setzt das ausgewählte Fenster als Ziel-Fenster."""
        self.target_window_title = self.window_selector.currentText()
        self.status_label.setText(f"✅ Windows selected: {self.target_window_title}")

    def start_pressing(self):
        """Startet den automatischen Tastendruck."""
        if not self.running:
            if not self.target_window_title:
                self.status_label.setText("⚠ No Window selected!")
                return

            self.running = True
            self.thread = threading.Thread(target=self.press_keys, daemon=True)
            self.thread.start()

            self.status_label.setText("Status: Running")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)

    def stop_pressing(self):
        """Stoppt den automatischen Tastendruck."""
        if self.running:
            self.running = False
            self.status_label.setText("Status: stopped")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def press_keys(self):
        """Drückt aktivierte Tasten mit zufälliger Verzögerung innerhalb von ±50ms vom eingestellten Wert.
        Wenn das Ziel-Fenster nicht aktiv ist, wird der Vorgang pausiert, bis das Fenster wieder im Vordergrund ist."""
        while self.running:
            active_window = gw.getActiveWindow()
            # Überprüfe, ob das aktive Fenster den Zieltitel (case-insensitive) enthält
            if not active_window or self.target_window_title.lower() not in active_window.title.lower():
                self.status_label.setText("⚠ Fenster nicht aktiv! Pausiere...")
                # Warte in einer Schleife, bis das gewünschte Fenster wieder aktiv ist
                while self.running:
                    active_window = gw.getActiveWindow()
                    if active_window and self.target_window_title.lower() in active_window.title.lower():
                        self.status_label.setText("✅ Fenster aktiv, fahre fort")
                        break
                    time.sleep(1)
                # Falls running währenddessen false geworden ist, breche die äußere Schleife ab
                if not self.running:
                    break

            # Sobald das Ziel-Fenster aktiv ist, drücke die Tasten 1-9 gemäß den Einstellungen
            for i in range(1, 10):
                if self.settings[str(i)]["enabled"]:
                    adjusted_delay = self.settings[str(i)]["delay"] + random.randint(-50, 50)
                    adjusted_delay = max(100, adjusted_delay)  # Sicherstellen, dass es nicht unter 100ms geht
                    pyautogui.press(str(i))
                    time.sleep(adjusted_delay / 1000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KeyPresser()
    window.show()
    sys.exit(app.exec())
