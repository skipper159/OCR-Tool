import os
import datetime

LOG_DIR = "logs"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Callback-Funktion für die GUI
log_callback = None

def get_log_file():
    """Erstellt den Dateipfad für das Log des aktuellen Tages."""
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"log_{date_str}.txt")

def log_event(event):
    """Speichert ein Ereignis mit Zeitstempel in der Log-Datei und aktualisiert die GUI."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {event}\n"

    with open(get_log_file(), "a", encoding="utf-8") as log_file:  # UTF-8 verwenden
        log_file.write(log_entry)

    print(log_entry.strip())  # Für Debugging in der Konsole

    # Falls eine GUI verbunden ist, das Log live aktualisieren
    if log_callback:
        log_callback(log_entry)
