import sys
import os
import datetime
import json
import traceback
import time
import pyautogui  # Für Mausbewegung & Tastendrücke
import pygetwindow as gw  # Für die Fensterliste und Auswahl
import pygame  # Für das Abspielen des Error-Sounds
from PyQt6.QtGui import QIcon, QTextCursor
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QHBoxLayout,
    QGroupBox
)
from PyQt6.QtCore import QThread, QTimer, pyqtSignal, pyqtSlot
from settings_module import load_settings
from ocr_module import ocr_loop
from logger import log_event  # Falls benötigt, ansonsten nicht zwingend

ICON_PATH = "legends_welcome"
LOG_FOLDER = "logs"

# Stelle sicher, dass das Log-Verzeichnis existiert
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)


def load_keypresser_settings():
    """Lädt die Keypresser-Einstellungen aus keypresser_settings.json oder legt Standardwerte an."""
    SETTINGS_KEYPRESSER = "keypresser_settings.json"
    try:
        with open(SETTINGS_KEYPRESSER, "r") as f:
            settings = json.load(f)
        return settings
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {str(i): {"enabled": False, "delay": 1000} for i in range(1, 10)}
        with open(SETTINGS_KEYPRESSER, "w") as f:
            json.dump(settings, f, indent=4)
        return settings


# ----------------------- OCR Thread -----------------------
class OcrThread(QThread):
    log_signal = pyqtSignal(str)  # Sende Logs an die GUI
    status_signal = pyqtSignal(str)  # Aktualisiert OCR-Status in der GUI
    mouse_action_signal = pyqtSignal(str, tuple, float)  # 🎯 Mausbewegung-Signal (Name, Position, Klickverzögerung)

    def __init__(self, shared_settings, recognized_positions):
        super().__init__()
        self.shared_settings = shared_settings
        self.recognized_positions = recognized_positions
        self.running = True

    def run(self):
        try:
            self.log_signal.emit("[OCR] 📌 OCR-Thread gestartet.")
            self.status_signal.emit("Running")

            while self.running:
                recognized_positions = ocr_loop(self.recognized_positions, self.shared_settings)

                if recognized_positions:
                    for name, pos in recognized_positions.items():
                        if not pos or pos == (0, 0):
                            self.log_signal.emit(f"[SYSTEM] ⚠️ Ungültige Position für {name}, kein Klick möglich.")
                            continue

                        click_delay = self.shared_settings.get("click_delay_monster", 500)

                        # 🎯 DEBUG: Prüfen, ob das Signal gesendet wird
                        print(f"[DEBUG] 🖱️ Sende Mausbewegung-Signal für {name} an {pos}")

                        # Signal senden
                        self.mouse_action_signal.emit(name, pos, click_delay)

                if not self.running:
                    break
                self.msleep(5000)

        except Exception as e:
            self.log_signal.emit(f"[SYSTEM] ❌ Fehler im OCR-Thread:\n{traceback.format_exc()}")
            self.status_signal.emit("Fehler")

    def stop(self):
        self.running = False
        self.quit()
        if not self.wait(2000):
            self.terminate()
            self.wait()


    def play_error_sound(self):
        """Spielt den Error-Sound ab, sofern möglich."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            sound_file = os.path.join(os.getcwd(), "OCRV2", "Sounds", "Error.mp3")
            error_sound = pygame.mixer.Sound(sound_file)
            error_sound.play()
        except Exception:
            self.log_signal.emit(f"[SYSTEM] ❌ Fehler beim Abspielen des Error-Sounds:\n{traceback.format_exc()}")

    def stop(self):
        self.running = False
        self.quit()
        if not self.wait(2000):
            self.terminate()
            self.wait()

# ----------------------- Mausaktions-Thread -----------------------
def move_and_click(x, y):
    """Bewegt die Maus zur erkannten Position und führt einen Klick aus."""
    print(f"[DEBUG] Bewege Maus zu ({x}, {y})...")
    pyautogui.moveTo(x, y, duration=0.5)  # Sanfte Bewegung

    time.sleep(0.2)  # Kleiner Delay, damit Windows die Bewegung registriert

    print("[DEBUG] Führe Linksklick aus...")
    pyautogui.click(x, y)
    print("[DEBUG] Klick abgeschlossen.")

class MouseActionThread(QThread):
    """
    Mausaktions-Thread:
    - Wartet auf Signale, um Mausbewegungen und Klicks auszuführen.
    """
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        self.exec()

    @pyqtSlot(str, tuple, float)
    def perform_mouse_action(self, name, pos, click_delay):
        """Bewegt die Maus zur erkannten Position und klickt"""
        try:
            x, y = pos
            print(f"[DEBUG] 🎯 Maus-Signal erhalten: {name} an {x}, {y} (Klick in {click_delay}s)")

            # **Direkt die Maus bewegen und klicken**
            print(f"[DEBUG] Bewege Maus zu ({x}, {y})...")
            pyautogui.moveTo(x, y, duration=0.5)
            pyautogui.click(x, y)

        except Exception as e:
            print(f"[SYSTEM] ❌ Fehler bei Mausaktion:\n{traceback.format_exc()}")


# ----------------------- Autoplay Thread (Keypresser-Funktionalität) -----------------------
class AutoplayThread(QThread):
    """
    Autoplay-Thread:
    - Führt die automatische Tasteneingabe (Keypresser) aus.
    - Nutzt Einstellungen (enabled, delay) für die Tasten 1-9, geladen aus keypresser_settings.json.
    """
    log_signal = pyqtSignal(str)

    def __init__(self, target_window, settings):
        super().__init__()
        self.target_window = target_window
        self.settings = settings
        self.running = True

    def run(self):
        self.log_signal.emit("[KeyPresser] Autoplay startet.")
        while self.running:
            if self.target_window is None:
                self.log_signal.emit("[KeyPresser] ⚠ No Destination Window!")
                self.running = False
                break
            if gw.getActiveWindow() != self.target_window:
                self.log_signal.emit("[KeyPresser] ⚠ Window not active!")
                time.sleep(1)
                continue
            for i in range(1, 10):
                if self.settings.get(str(i), {}).get("enabled", False):
                    pyautogui.press(str(i))
                    time.sleep(self.settings[str(i)]["delay"] / 1000)
            # Optional: kurze Pause, um CPU-Last zu reduzieren
        self.log_signal.emit("[KeyPresser] Autoplay stopped.")

    def stop(self):
        self.running = False


# ----------------------- Hauptfenster (OCRControlWindow) -----------------------
class OCRControlWindow(QWidget):
    """
    GUI zur Steuerung des OCR-Tools und Autoplay (Keypresser):
    - Der obere Steuerungsbereich wird in zwei Spalten angeordnet: links für OCR und rechts für Autoplay.
    - Der Fenster-Auswahlbereich sowie der Log-Bereich erhalten jeweils einen Rahmen mit Titel.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("OCR Steuerung & Live-Logs")
        self.setGeometry(350, 250, 700, 600)
        self.setWindowIcon(QIcon(ICON_PATH))

        today = datetime.datetime.now().strftime("%Y%m%d")
        self.log_file_ocr = os.path.join(LOG_FOLDER, f"OCR_{today}.txt")
        self.log_file_klick = os.path.join(LOG_FOLDER, f"KLICK_{today}.txt")
        self.log_file_system = os.path.join(LOG_FOLDER, f"SYSTEM_{today}.txt")

        self.shared_settings = load_settings()
        self.keypresser_settings = load_keypresser_settings()

        self.ocr_thread = None
        self.mouse_thread = None
        self.autoplay_thread = None
        self.recognized_positions = {}
        self.autoplay_running = False

        main_layout = QVBoxLayout()

        # --- Steuerungsbereich: Program Control ---
        program_control_box = QGroupBox("Program Control")
        control_layout = QHBoxLayout()

        # Linke Spalte: OCR-Steuerung
        ocr_layout = QVBoxLayout()
        self.ocr_status_label = QLabel("OCR Status: Stopped")
        ocr_layout.addWidget(self.ocr_status_label)
        self.start_button = QPushButton("Start OCR")
        self.start_button.clicked.connect(self.start_ocr)
        ocr_layout.addWidget(self.start_button)
        self.stop_button = QPushButton("Stop OCR")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_ocr)
        ocr_layout.addWidget(self.stop_button)
        ocr_layout.addStretch()  # Abstandshalter am unteren Rand
        control_layout.addLayout(ocr_layout)

        control_layout.addSpacing(40)  # Abstand zwischen den Spalten

        # Rechte Spalte: Autoplay-Steuerung
        autoplay_layout = QVBoxLayout()
        self.autoplay_status_label = QLabel("KeyPresser Status: Stopped")
        autoplay_layout.addWidget(self.autoplay_status_label)
        self.start_autoplay_button = QPushButton("Start KeyPresser")
        self.start_autoplay_button.clicked.connect(self.start_autoplay)
        autoplay_layout.addWidget(self.start_autoplay_button)
        self.stop_autoplay_button = QPushButton("Stop KeyPresser")
        self.stop_autoplay_button.setEnabled(False)
        self.stop_autoplay_button.clicked.connect(self.stop_autoplay)
        autoplay_layout.addWidget(self.stop_autoplay_button)
        autoplay_layout.addStretch()
        control_layout.addLayout(autoplay_layout)

        program_control_box.setLayout(control_layout)
        main_layout.addWidget(program_control_box)

        main_layout.addSpacing(20)

        # --- Fenster-Auswahl: Setting Windows ---
        window_box = QGroupBox("Setting Windows")
        window_layout = QHBoxLayout()
        self.window_list_combobox = QComboBox()
        window_layout.addWidget(self.window_list_combobox)
        self.update_window_list_button = QPushButton("Refresh")
        self.update_window_list_button.clicked.connect(self.update_window_list)
        window_layout.addWidget(self.update_window_list_button)
        self.select_window_button = QPushButton("Select Window")
        self.select_window_button.clicked.connect(self.select_window)
        window_layout.addWidget(self.select_window_button)
        window_box.setLayout(window_layout)
        main_layout.addWidget(window_box)

        main_layout.addSpacing(20)

        # --- Log-Bereich: Logging Area ---
        log_box = QGroupBox("Logging Area")
        log_area_layout = QVBoxLayout()
        log_control_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search in Logs...")
        self.search_input.textChanged.connect(self.update_logs)
        log_control_layout.addWidget(self.search_input)
        self.filter_dropdown = QComboBox()
        self.filter_dropdown.addItems(["All Logs", "OCR", "Clicks", "System"])
        self.filter_dropdown.currentIndexChanged.connect(self.update_logs)
        log_control_layout.addWidget(self.filter_dropdown)
        log_area_layout.addLayout(log_control_layout)
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        log_area_layout.addWidget(self.log_display)
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.update_logs)
        log_area_layout.addWidget(refresh_button)
        log_box.setLayout(log_area_layout)
        main_layout.addWidget(log_box)

        self.setLayout(main_layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_logs)
        self.timer.start(2000)

        self.update_logs()
        self.update_window_list()

    def write_log(self, message):
        timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        log_entry = f"{timestamp} {message}\n"
        lower_msg = message.lower()
        if lower_msg.startswith("[ocr]"):
            file_path = self.log_file_ocr
        elif lower_msg.startswith("[klick]"):
            file_path = self.log_file_klick
        elif lower_msg.startswith("[system]"):
            file_path = self.log_file_system
        else:
            file_path = self.log_file_system
        try:
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Fehler beim Schreiben in Log-Datei: {e}")

    def append_log(self, message):
        self.log_display.append(message.strip())
        self.log_display.moveCursor(QTextCursor.MoveOperation.End)
        self.write_log(message)

    def get_file_contents(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                return f.readlines()
        return []

    def update_logs(self):
        selected_filter = self.filter_dropdown.currentText().lower()
        search_text = self.search_input.text().lower()

        log_entries = []
        if selected_filter == "alle logs":
            log_entries.extend(self.get_file_contents(self.log_file_ocr))
            log_entries.extend(self.get_file_contents(self.log_file_klick))
            log_entries.extend(self.get_file_contents(self.log_file_system))
            log_entries.sort()  # Dank ISO-Timestamp lexikographisch sortiert
        elif selected_filter == "nur ocr":
            log_entries = self.get_file_contents(self.log_file_ocr)
        elif selected_filter == "nur klicks":
            log_entries = self.get_file_contents(self.log_file_klick)
        elif selected_filter == "system":
            log_entries = self.get_file_contents(self.log_file_system)
        else:
            log_entries = []

        if search_text:
            log_entries = [line for line in log_entries if search_text in line.lower()]

        self.log_display.setText("".join(log_entries))
        self.log_display.moveCursor(QTextCursor.MoveOperation.End)

    def update_window_list(self):
        try:
            windows = gw.getAllWindows()
            self.window_list_combobox.clear()
            for window in windows:
                if window.title:
                    # Nur den Fenstertitel anzeigen – ohne Koordinaten.
                    self.window_list_combobox.addItem(window.title, window.title)
            self.append_log("[SYSTEM] Window list updated.")
        except Exception:
            self.append_log(f"[SYSTEM] ❌ Fehler beim Aktualisieren der Fensterliste:\n{traceback.format_exc()}")

    def select_window(self):
        index = self.window_list_combobox.currentIndex()
        if index < 0:
            self.append_log("[SYSTEM] Kein Fenster ausgewählt.")
            return
        # Lese den gespeicherten Fenstertitel aus (ohne Koordinaten)
        title = self.window_list_combobox.itemData(index)
        if title:
            target_windows = gw.getWindowsWithTitle(title)
            if target_windows:
                target_window = target_windows[0]
                # Setze als Ziel-Fenster die Region des gefundenen Fensters
                self.shared_settings["ocr_region"] = (
                target_window.left, target_window.top, target_window.width, target_window.height)
                self.append_log(f"[SYSTEM] Selected Window: {title}")
            else:
                self.append_log(f"[SYSTEM] Found no Window '{title}'.")

    def start_ocr(self):
        """Startet das OCR-Skript"""
        try:
            if (not self.ocr_thread or not self.ocr_thread.isRunning()) and (
                    not self.mouse_thread or not self.mouse_thread.isRunning()):
                self.mouse_thread = MouseActionThread()
                self.mouse_thread.log_signal.connect(self.append_log)
                self.mouse_thread.start()

                self.ocr_thread = OcrThread(self.shared_settings, self.recognized_positions)
                self.ocr_thread.log_signal.connect(self.append_log)
                self.ocr_thread.status_signal.connect(lambda msg: self.ocr_status_label.setText(f"OCR Status: {msg}"))

                # 🛠 **DEBUG: Testen, ob perform_mouse_action direkt funktioniert**
                print("[DEBUG] Teste direkte Mausbewegung in start_ocr()...")
                self.mouse_thread.perform_mouse_action("Test-Name", (500, 500), 0.5)

                # **Manuelle Verbindung der Mausbewegung**
                print("[DEBUG] Versuche Verbindung: mouse_action_signal -> perform_mouse_action")
                self.ocr_thread.mouse_action_signal.connect(self.mouse_thread.perform_mouse_action)
                print("[DEBUG] Verbindung erfolgreich hergestellt!")

                self.ocr_thread.start()

                self.ocr_status_label.setText("OCR Status: Running")
                self.start_button.setEnabled(False)
                self.stop_button.setEnabled(True)

        except Exception as e:
            log_event(f"[SYSTEM] ❌ Fehler beim Starten des OCR-Threads:\n{traceback.format_exc()}")
            self.ocr_status_label.setText("OCR Status: Fehler")

    def stop_ocr(self):
        if self.ocr_thread and self.ocr_thread.isRunning():
            self.ocr_thread.stop()
            self.ocr_thread.quit()
            if not self.ocr_thread.wait(2000):
                self.ocr_thread.terminate()
                self.ocr_thread.wait()
            self.ocr_thread = None
        if self.mouse_thread and self.mouse_thread.isRunning():
            self.mouse_thread.quit()
            if not self.mouse_thread.wait(2000):
                self.mouse_thread.terminate()
                self.mouse_thread.wait()
            self.mouse_thread = None

        self.ocr_status_label.setText("OCR Status: Stopped")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def start_autoplay(self):
        if not self.autoplay_running:
            selected_window = self.window_list_combobox.currentText()
            if not selected_window:
                self.autoplay_status_label.setText("KeyPresser: ⚠ No Windows selected!")
                return
            target_window = gw.getWindowsWithTitle(selected_window)
            if not target_window:
                self.autoplay_status_label.setText("KeyPresser: ⚠ No Window found!")
                return
            target_window = target_window[0]
            self.target_window = target_window  # Gemeinsames Ziel-Fenster setzen
            self.autoplay_thread = AutoplayThread(target_window, self.keypresser_settings)
            self.autoplay_thread.log_signal.connect(
                lambda msg: (self.append_log(msg),
                             self.autoplay_status_label.setText(f"Autoplay: {msg.split(']')[-1].strip()}"))
            )
            self.autoplay_thread.start()
            self.autoplay_running = True
            self.autoplay_status_label.setText(f"KeyPresser: Running ({selected_window})")
            self.start_autoplay_button.setEnabled(False)
            self.stop_autoplay_button.setEnabled(True)

    def stop_autoplay(self):
        if self.autoplay_running and self.autoplay_thread:
            self.autoplay_thread.stop()
            self.autoplay_thread.wait(2000)
            self.autoplay_thread = None
            self.autoplay_running = False
            self.autoplay_status_label.setText("KeyPresser: Stopped")
            self.start_autoplay_button.setEnabled(True)
            self.stop_autoplay_button.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OCRControlWindow()
    window.show()
    sys.exit(app.exec())
