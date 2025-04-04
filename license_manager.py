import sqlite3
import random

DB_FILE = "licenses.db"

def generate_license_key():
    """Erstellt einen zufälligen 20-stelligen Lizenzschlüssel im Format XXXX-XXXXX-XXXXX-XXXXX."""
    return "-".join(["".join([str(random.randint(0, 9)) for _ in range(5)]) for _ in range(4)])

def create_license_database():
    """Erstellt die Lizenz-Datenbank und füllt sie mit 1000 zufälligen Schlüsseln."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Tabelle für Lizenzen erstellen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_key TEXT UNIQUE,
            activated INTEGER DEFAULT 0
        )
    ''')

    # Prüfen, ob bereits Lizenzen vorhanden sind
    cursor.execute("SELECT COUNT(*) FROM licenses")
    count = cursor.fetchone()[0]

    if count == 0:  # Nur wenn noch keine Lizenzen existieren
        licenses = [(generate_license_key(), 0) for _ in range(1000)]
        cursor.executemany("INSERT INTO licenses (license_key, activated) VALUES (?, ?)", licenses)
        conn.commit()
        print("✅ 1.000 Lizenzschlüssel wurden erfolgreich generiert und gespeichert!")

    conn.close()

def check_license(license_key):
    """Überprüft, ob der Lizenzschlüssel existiert und noch nicht aktiviert wurde."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT activated FROM licenses WHERE license_key = ?", (license_key,))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        return False, "❌ Lizenzschlüssel nicht gefunden."
    elif result[0] == 1:
        return False, "⚠ Lizenzschlüssel wurde bereits verwendet."
    return True, "✅ Lizenzschlüssel gültig."

def activate_license(license_key):
    """Aktiviert eine Lizenz, falls sie gültig ist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT activated FROM licenses WHERE license_key = ?", (license_key,))
    result = cursor.fetchone()

    if result is None:
        conn.close()
        return False, "❌ Lizenzschlüssel nicht gefunden."
    elif result[0] == 1:
        conn.close()
        return False, "⚠ Lizenzschlüssel wurde bereits verwendet."

    cursor.execute("UPDATE licenses SET activated = 1 WHERE license_key = ?", (license_key,))
    conn.commit()
    conn.close()
    return True, "🎉 Lizenz wurde erfolgreich aktiviert!"

# Datenbank beim ersten Start initialisieren
create_license_database()
