import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox
from license_manager import check_license, activate_license


class LicenseGUI(QWidget):
    """GUI zur Lizenzaktivierung und -prüfung."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Lizenzverwaltung")
        self.setGeometry(400, 300, 400, 200)

        layout = QVBoxLayout()

        self.status_label = QLabel("Geben Sie Ihren Lizenzschlüssel ein:")
        layout.addWidget(self.status_label)

        self.license_input = QLineEdit()
        self.license_input.setPlaceholderText("XXXX-XXXXX-XXXXX-XXXXX")
        layout.addWidget(self.license_input)

        self.check_button = QPushButton("Lizenz prüfen")
        self.check_button.clicked.connect(self.check_license)
        layout.addWidget(self.check_button)

        self.activate_button = QPushButton("Lizenz aktivieren")
        self.activate_button.clicked.connect(self.activate_license)
        layout.addWidget(self.activate_button)

        self.setLayout(layout)

    def check_license(self):
        """Überprüft, ob der Lizenzschlüssel gültig ist."""
        license_key = self.license_input.text().strip()
        if not license_key:
            QMessageBox.warning(self, "Fehler", "Bitte einen Lizenzschlüssel eingeben!")
            return

        valid, message = check_license(license_key)
        QMessageBox.information(self, "Lizenzprüfung", message)

    def activate_license(self):
        """Aktiviert den Lizenzschlüssel."""
        license_key = self.license_input.text().strip()
        if not license_key:
            QMessageBox.warning(self, "Fehler", "Bitte einen Lizenzschlüssel eingeben!")
            return

        success, message = activate_license(license_key)
        if success:
            self.status_label.setText("Lizenzstatus: ✅ Aktiviert")
        QMessageBox.information(self, "Lizenzaktivierung", message)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LicenseGUI()
    window.show()
    sys.exit(app.exec())
