import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QMenuBar, QMenu, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import QThread, Signal, QObject, Qt
from PySide6.QtGui import QIcon, QPixmap
from OCRControl import OCRControlWindow  # Importiere das OCR-Steuerungsfenster
from gui import SettingsWindow

ICON_PATH = "Legends_welcome.png"
WELCOME_IMAGE = "Legends_welcome.png"  # Dein hochgeladenes Bild

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OCR BOT")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setGeometry(300, 200, 400, 400)

        # Haupt-Widget und Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Menüführung
        self.create_menu_bar()

        # Welcome-Text-Bild mit Skalierung
        welcome_label = QLabel()
        welcome_pixmap = QPixmap(WELCOME_IMAGE)
        if not welcome_pixmap.isNull():
            welcome_pixmap = welcome_pixmap.scaled(400, 400)
            welcome_label.setPixmap(welcome_pixmap)
            welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            print("Fehler: Bilddatei nicht gefunden!")
        main_layout.addWidget(welcome_label)

        # Bereich für zusätzliche Buttons
        self.additional_buttons_layout = QVBoxLayout()
        main_layout.addLayout(self.additional_buttons_layout)

    def create_menu_bar(self):
        """Erstellt die Menüführung"""
        menu_bar = self.menuBar()

        # File-Menü
        file_menu = menu_bar.addMenu("File")
        save_action = file_menu.addAction("Save")
        save_action.triggered.connect(self.save_settings)
        license_action = file_menu.addAction("License Manager")
        license_action.triggered.connect(self.open_license_manager)
        file_menu.addSeparator()
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        # Settings-Menü
        settings_menu = menu_bar.addMenu("Settings")

        # Keypresser
        keypresser_action = settings_menu.addAction("KeyPresser")
        keypresser_action.triggered.connect(self.open_keypresser_settings)

        # OCR Program
        ocr_action = settings_menu.addAction("OCR Control")
        ocr_action.triggered.connect(self.open_ocr_control_window)

        # Settings
        ocr_action = settings_menu.addAction("Settings")
        ocr_action.triggered.connect(self.open_ocr_settings_window)

        # Help-Menü
        help_menu = menu_bar.addMenu("Help")
        manual_action = help_menu.addAction("Manual")
        manual_action.triggered.connect(self.open_manual_settings)
        changelog_action = help_menu.addAction("Changelog")
        changelog_action.triggered.connect(self.open_changelog_settings)

    def open_ocr_control_window(self):
        """Öffnet das OCR-Steuerungsfenster"""
        try:
            if not hasattr(self, "ocr_control_window") or self.ocr_control_window is None:
                self.ocr_control_window = OCRControlWindow()
            self.ocr_control_window.show()
            self.ocr_control_window.activateWindow()  # Fenster in den Vordergrund holen
        except Exception as e:
            print(f"Fehler beim Öffnen des OCR-Fensters: {e}")

    def open_ocr_settings_window(self):
        """Öffnet das OCR-Settings Fenster"""
        try:
            if not hasattr(self, "ocr_settings_window") or self.ocr_settings_window is None:
                self.ocr_settings_window = SettingsWindow()
            self.ocr_settings_window.show()
            self.ocr_settings_window.activateWindow()  # Fenster in den Vordergrund holen
        except Exception as e:
            print(f"Fehler beim Öffnen des Settings-Fensters: {e}")

    def save_settings(self):
        """Speichert die Einstellungen"""
        print("Settings gespeichert")
        # Hier Speicherlogik implementieren

    def open_license_manager(self):
        """Öffnet den Lizenzmanager in einem neuen Fenster"""
        try:
            from license_gui import LicenseGUI

            # Erstelle ein neues Fenster, falls nicht vorhanden
            if not hasattr(self, "license_window") or not self.license_window.isVisible():
                self.license_window = LicenseGUI()  # Kein Parent für eigenständiges Fenster
                self.license_window.setWindowTitle("Lizenzverwaltung")

            self.license_window.show()
            self.license_window.activateWindow()  # Bringt Fenster in den Vordergrund

        except ImportError as e:
            print(f"Fehlendes Modul: {e}")
            QMessageBox.critical(self, "Fehler", "Lizenzmodul nicht gefunden!")
        except Exception as e:
            print(f"Kritischer Fehler: {e}")
            QMessageBox.critical(self, "Fehler", f"Fehler: {str(e)}")

    def open_keypresser_settings(self):
        """Öffnet Keypresser-Einstellungen"""
        from keypresser import KeyPresser  # Importiere das Modul

        if not hasattr(self, "keypresser_window"):
            self.keypresser_window = KeyPresser()

        self.keypresser_window.show()
        self.keypresser_window.activateWindow()  # Bringt das Fenster in den Vordergrund

    def open_manual_settings(self):
        from manual import MANUAL_TEXT
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Manual", MANUAL_TEXT)

    def open_changelog_settings(self):
        from changelog import Changelog_TEXT
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Changelog", Changelog_TEXT)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
