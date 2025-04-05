from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QGroupBox, QSpinBox

class OCRSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("OCR Settings")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Beispiel: Eingabefeld für den Zielnamen
        self.name_input = QLineEdit()
        layout.addWidget(QLabel("Zielname:"))
        layout.addWidget(self.name_input)

        # Beispiel: Fensterkoordinaten
        self.region_input = QLineEdit()
        layout.addWidget(QLabel("Fensterkoordinaten (x1,y1,x2,y2):"))
        layout.addWidget(self.region_input)
        
        # Neuer Bereich: Bewegungsgrenzen
        movement_group = QGroupBox("Bewegungsgrenzen")
        movement_layout = QVBoxLayout()
        
        # X-Grenzen
        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel("X-Min:"))
        self.min_x_input = QSpinBox()
        self.min_x_input.setRange(0, 5000)
        self.min_x_input.setValue(0)
        x_layout.addWidget(self.min_x_input)
        
        x_layout.addWidget(QLabel("X-Max:"))
        self.max_x_input = QSpinBox()
        self.max_x_input.setRange(0, 5000)
        self.max_x_input.setValue(1920)  # Standardwert für FHD-Bildschirm
        x_layout.addWidget(self.max_x_input)
        
        movement_layout.addLayout(x_layout)
        
        # Y-Grenzen
        y_layout = QHBoxLayout()
        y_layout.addWidget(QLabel("Y-Min:"))
        self.min_y_input = QSpinBox()
        self.min_y_input.setRange(0, 5000)
        self.min_y_input.setValue(0)
        y_layout.addWidget(self.min_y_input)
        
        y_layout.addWidget(QLabel("Y-Max:"))
        self.max_y_input = QSpinBox()
        self.max_y_input.setRange(0, 5000)
        self.max_y_input.setValue(1080)  # Standardwert für FHD-Bildschirm
        y_layout.addWidget(self.max_y_input)
        
        movement_layout.addLayout(y_layout)
        
        movement_group.setLayout(movement_layout)
        layout.addWidget(movement_group)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Verbinde Signale
        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn.clicked.connect(self.close)

    def save_settings(self):
        """Speichert die Einstellungen (Beispiel)"""
        import json
        
        target_name = self.name_input.text()
        region = tuple(map(int, self.region_input.text().split(','))) if self.region_input.text() else (0, 0, 0, 0)
        
        # Bewegungsgrenzen speichern
        movement_bounds = {
            "min_x": self.min_x_input.value(),
            "max_x": self.max_x_input.value(),
            "min_y": self.min_y_input.value(),
            "max_y": self.max_y_input.value()
        }
        
        # Einstellungen in die settings.json Datei speichern
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            settings = {}
        
        settings["target_name"] = target_name
        settings["ocr_region"] = region
        settings["movement_bounds"] = movement_bounds
        
        with open("settings.json", "w") as f:
            json.dump(settings, f, indent=4)
        
        print(f"Einstellungen gespeichert: Name={target_name}, Region={region}, Bewegungsgrenzen={movement_bounds}")
        self.close()