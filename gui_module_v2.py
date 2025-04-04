import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout,
    QWidget, QMenuBar, QMenu, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap

ICON_PATH = "Legends_welcome.png"
WELCOME_IMAGE = "Legends_welcome.png"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Legends BOT")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setGeometry(300, 200, 400, 400)

        # Haupt-Widget und Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Welcome-Bild
        welcome_label = QLabel()
        welcome_pixmap = QPixmap(WELCOME_IMAGE)
        if not welcome_pixmap.isNull():
            welcome_pixmap = welcome_pixmap.scaled(400, 400)
            welcome_label.setPixmap(welcome_pixmap)
            welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            print("Fehler: Bilddatei nicht gefunden!")
        main_layout.addWidget(welcome_label)


        # Menüführung
        self.create_menu_bar()

    def create_menu_bar(self):
        """Erstellt die Menüführung"""
        menu_bar = self.menuBar()

        # File-Menü
        file_menu = menu_bar.addMenu("File")

        # License Manager
        license_action = file_menu.addAction("License Manager")
        license_action.triggered.connect(self.open_license_manager)

        # Separator
        file_menu.addSeparator()

        # Exit Action
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        # Tools-Menü
        tools_menu = menu_bar.addMenu("Tools")
        keypresser_action = tools_menu.addAction("KeyPresser")
        keypresser_action.triggered.connect(self.open_keypresser_settings)
        ocr_action = tools_menu.addAction("OCR")
        ocr_action.triggered.connect(self.open_ocr_settings)

        # Help-Menü
        help_menu = menu_bar.addMenu("Help")
        manual_action = help_menu.addAction("Manual")
        manual_action.triggered.connect(self.open_manual_settings)
        changelog_action = help_menu.addAction("Changelog")
        changelog_action.triggered.connect(self.open_changelog_settings)


    def open_keypresser_settings(self):
        """Öffnet den KeyPresser"""
        from keypresser import KeyPresser
        self.keypresser_window = KeyPresser()
        self.keypresser_window.show()

    def open_ocr_settings(self):
        """Öffnet OCR-Einstellungen aus einem externen Modul"""
        try:
            # Importiere das OCR-Einstellungsmodul
            from ocr_settings_module import OCRSettingsDialog

            # Erstelle und zeige den Dialog
            self.ocr_settings_dialog = OCRSettingsDialog(self)
            self.ocr_settings_dialog.exec()
        except ImportError:
            print("Fail: OCR-Module not found!")
        except Exception as e:
            print(f"Fail: Can´t opening OCR-Settings: {str(e)}")

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

    def open_manual_settings(self):
        """Zeigt das Handbuch an"""
        from manual import MANUAL_TEXT
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Manual", MANUAL_TEXT)

    def open_changelog_settings(self):
        """Zeigt den Changelog an"""
        from changelog import Changelog_TEXT
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Changelog", Changelog_TEXT)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())