OCR-Tool
Ein leistungsfähiges Werkzeug für Optical Character Recognition (OCR) mit spezieller Whitelist-Funktionalität für Spielernamen- und Monster-Erkennung.

OCR-Tool Preview

📋 Inhaltsverzeichnis
Funktionen
Systemanforderungen
Installation
Verwendung
Problembehandlung
Beiträge
Lizenz

🚀 Funktionen
Das OCR-Tool bietet folgende Hauptfunktionen:

Texterkennung in bestimmten Bildschirmbereichen
Whitelist-Filterung für Monster- und Spielernamen
Blacklist-Funktionalität für Spieler
Individuell einstellbare Klick-Verzögerungen
GM-Warnfunktion mit akustischer Alarmierung
Einfache Benutzeroberfläche für Einstellungsanpassungen

💻 Systemanforderungen

Betriebssystem: Windows 10 oder neuer
Python: Version 3.8 oder höher
Arbeitsspeicher: Mindestens 4 GB RAM
Festplattenspeicher: Mindestens 500 MB freier Speicherplatz (für Python-Pakete und OCR-Modelle)

📥 Installation

1. Repository klonen

git clone https://github.com/DEINUSERNAME/OCR-Tool.git
cd OCR-Tool


2. Virtuelle Umgebung einrichten

# Virtuelle Umgebung erstellen
python -m venv venv

# Virtuelle Umgebung aktivieren
# Für Windows:
venv\Scripts\activate
# Für Linux/Mac:
# source venv/bin/activate


3. Abhängigkeiten installieren

pip install -r requirements.txt

Hinweis: Die erste Installation von PaddleOCR kann einige Zeit dauern, da Modelle heruntergeladen werden.

4. Projektstruktur vorbereiten
Stelle sicher, dass folgende Ordner im Projektverzeichnis vorhanden sind:

logs
Sounds (enthält error-126627.mp3)
Version
Falls die Ordner fehlen, erstelle sie manuell:

mkdir logs Sounds Version

5. Icon und Sound-Dateien
Stelle sicher, dass die folgenden Dateien vorhanden sind:

legends_welcome.png (Icon für die Anwendung)
error-126627.mp3 (Alarm-Sound für die GM-Warnung)
Falls nicht, füge eigene Dateien mit diesen Namen hinzu oder passe die entsprechenden Konstanten in gui.py an.

🔧 Verwendung

Starten der Anwendung
1. Aktiviere die virtuelle Umgebung (falls noch nicht geschehen):
venv\Scripts\activate

2. Starte die Hauptanwendung:
python gui_module_v2.py oder
python gui_module.py #2 verschiedene Versionen

Einstellungen konfigurieren

1. Starte die Einstellungsanwendung:

python gui.py #Nicht Notwendig wenn die Hautpanwendung gestartet ist

2. Konfiguriere die folgenden Parameter:

OCR-Region (Bildschirmbereich für die Texterkennung)
Monster-Whitelist (Namen von Monstern, die erkannt werden sollen)
Player-Whitelist (Namen von Spielern, die erkannt werden sollen)
Player-Blacklist (Namen von Spielern, die ignoriert werden sollen)
GM-Warnung aktivieren/deaktivieren
Klick-Verzögerungen für Monster- und Spielernamen
3. Speichere die Einstellungen, bevor du die Anwendung schließt

Lizenzaktivierung
Beim ersten Start wirst du nach einem Lizenzschlüssel gefragt. Verwende einen der im Projekt enthaltenen Schlüssel oder generiere einen neuen mit:

❓ Problembehandlung

Python-Abhängigkeiten
Falls Probleme mit den Bibliotheken auftreten:

OCR-Genauigkeit
Wenn die Texterkennung nicht optimal funktioniert:

Stelle sicher, dass der gewählte Bildschirmbereich gut lesbare Texte enthält
Passe die Vertrauensschwelle in ocr_module.py an (Standardwert: 0.7)
Erwäge die Verwendung von Bildvorverarbeitung (Kontrastverstärkung, etc.)
Python-Versionskonflikt
Falls du Probleme mit der Python-Version hast:

👥 Beiträge

Beiträge zum Projekt sind willkommen! Bitte folge diesen Schritten:

Fork das Repository
Erstelle einen Feature-Branch (git checkout -b feature/amazing-feature)
Committe deine Änderungen (git commit -m 'Füge eine tolle Funktion hinzu')
Push zu deinem Branch (git push origin feature/amazing-feature)
Öffne einen Pull Request

📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Weitere Informationen findest du in der LICENSE Datei.

Erstellt mit ❤️ für die Gaming-Community. © 2025

Hinweis: Stelle sicher, dass du dieses Tool im Einklang mit den Nutzungsbedingungen der jeweiligen Spiele verwendest. Die Entwickler übernehmen keine Verantwortung für Konsequenzen, die durch den Einsatz dieser Software entstehen könnten.