import os
import cv2
import numpy as np
import pyautogui
import time
from paddleocr import PaddleOCR
from logger import log_event

# PaddleOCR initialisieren
ocr = PaddleOCR(use_angle_cls=True, lang="en")

def normalize_text(text):
    """Normalisiert erkannte Texte für besseren Abgleich mit der Whitelist"""
    return text.strip().lower()

def screenshot_ocr_paddle(shared_settings):
    """OCR mit PaddleOCR & Whitelist-Abgleich."""
    if "ocr_region" not in shared_settings:
        log_event("[ERROR] OCR-Region nicht gesetzt!")
        return {}

    x1, y1, w1, h1 = shared_settings["ocr_region"]
    screenshot = pyautogui.screenshot(region=(x1, y1, w1, h1))
    image = np.array(screenshot)

    processed_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # OCR-Erkennung
    result = ocr.ocr(processed_image, cls=True)

    name_positions = {}
    whitelist = shared_settings.get("whitelist_monster", []) + shared_settings.get("whitelist_player", [])

    print("[DEBUG] Whitelist-Namen:")
    print(whitelist)

    for line in result:
        for word_info in line:
            text = word_info[1][0]  # Erkannten Text extrahieren
            confidence = word_info[1][1]  # Vertrauenswert
            x, y = int(word_info[0][0][0]), int(word_info[0][0][1])  # Position (x, y)

            normalized_text = normalize_text(text)

            print(f"[DEBUG] OCR: '{normalized_text}' (Confidence: {confidence}) bei ({x}, {y})")

            # Whitelist ebenfalls normalisieren
            whitelist_normalized = [normalize_text(name) for name in whitelist]

            # Falls der Name in der Whitelist ist, loggen & speichern
            if normalized_text in whitelist_normalized and confidence > 0.7:
                name_positions[normalized_text] = (x + 20, y + 40)
                log_event(f"OCR erkannte: {normalized_text} an Position ({x + 20}, {y + 40})")
                print(f"[LOG] Match gefunden: {normalized_text} bei ({x + 20}, {y + 40})")

          #   🖱️ **Direkt die Maus bewegen und klicken**
         #   print(f"[DEBUG] Bewege Maus direkt aus `ocr_module.py` zu ({x + 20}, {y + 40})...")
         #  pyautogui.moveTo(x + 20, y + 40, duration=0.5)
         #   pyautogui.click(x + 20, y + 40)

    return name_positions

def ocr_loop(shared_dict, shared_settings):
    """Führt die OCR-Erkennung aus und aktualisiert die gemeinsame Datenstruktur mit den erkannten Namen und Positionen"""
    recognized_positions = screenshot_ocr_paddle(shared_settings)

    print(f"[DEBUG] OCR-Loop: Erkannte Positionen: {recognized_positions}")

    shared_dict.clear()
    shared_dict.update(recognized_positions)

