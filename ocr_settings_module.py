from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout

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
        target_name = self.name_input.text()
        region = tuple(map(int, self.region_input.text().split(',')))
        print(f"Einstellungen gespeichert: Name={target_name}, Region={region}")
        self.close()