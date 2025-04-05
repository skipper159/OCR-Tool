import os
import cv2
import numpy as np
import pyautogui
import time
import re
from paddleocr import PaddleOCR
from logger import log_event

# PaddleOCR initialisieren
ocr = PaddleOCR(use_angle_cls=True, lang="en")

def normalize_text(text):
    """Normalisiert erkannte Texte für besseren Abgleich mit der Whitelist"""
    return text.strip().lower()

def extract_game_coordinates(text):
    """
    Extrahiert Spielkoordinaten aus dem erkannten Text
    Format könnte z.B. "Name (1234,5678)" sein oder ähnliche Formate
    """
    # Suchen nach Zahlen-Paaren in Klammern oder nach Zahlen mit Komma getrennt
    coord_pattern = r'\((\d+),\s*(\d+)\)'
    match = re.search(coord_pattern, text)
    
    if match:
        # Extrahiere x und y aus dem gefundenen Muster
        try:
            game_x = int(match.group(1))
            game_y = int(match.group(2))
            return game_x, game_y
        except (ValueError, IndexError):
            return None
    
    return None

def is_within_game_bounds(game_x, game_y, bounds):
    """
    Überprüft, ob Spielkoordinaten innerhalb der definierten Grenzen liegen
    Stellt sicher, dass die Werte zwischen den min_x/y und max_x/y Werten liegen
    """
    if not bounds:
        return True  # Wenn keine Grenzen definiert sind, immer True zurückgeben
    
    min_x = bounds.get("min_x", 1)
    max_x = bounds.get("max_x", 9999)
    min_y = bounds.get("min_y", 1)
    max_y = bounds.get("max_y", 9999)
    
    return min_x <= game_x <= max_x and min_y <= game_y <= max_y

def calculate_center_move_for_game_coordinates(game_coords, bounds):
    """
    Berechnet eine Bewegung innerhalb der erlaubten Spielkoordinaten
    Gibt einen Punkt zurück, der sicher innerhalb der Grenzen liegt
    """
    game_x, game_y = game_coords
    min_x = bounds.get("min_x", 1)
    max_x = bounds.get("max_x", 9999)
    min_y = bounds.get("min_y", 1)
    max_y = bounds.get("max_y", 9999)
    
    # Spielzentrum berechnen
    center_x = (min_x + max_x) // 2
    center_y = (min_y + max_y) // 2
    
    # Maximal 50% vom Zentrum entfernt
    max_distance_x = (max_x - min_x) // 4
    max_distance_y = (max_y - min_y) // 4
    
    # Neue Position berechnen
    target_x = game_x
    target_y = game_y
    
    if game_x < min_x:
        target_x = min_x + max_distance_x
    elif game_x > max_x:
        target_x = max_x - max_distance_x
        
    if game_y < min_y:
        target_y = min_y + max_distance_y
    elif game_y > max_y:
        target_y = max_y - max_distance_y
    
    # Sicherstellen, dass nicht zu weit vom Zentrum entfernt
    distance_from_center_x = abs(target_x - center_x)
    if distance_from_center_x > max_distance_x:
        if target_x > center_x:
            target_x = center_x + max_distance_x
        else:
            target_x = center_x - max_distance_x
            
    distance_from_center_y = abs(target_y - center_y)
    if distance_from_center_y > max_distance_y:
        if target_y > center_y:
            target_y = center_y + max_distance_y
        else:
            target_y = center_y - max_distance_y
    
    return target_x, target_y

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
    movement_bounds = shared_settings.get("movement_bounds", {})

    print("[DEBUG] Whitelist-Namen:")
    print(whitelist)
    
    # Spielkoordinaten-Grenzen anzeigen
    if movement_bounds:
        print("[DEBUG] Spielkoordinaten-Grenzen aktiv:")
        print(f"X: {movement_bounds.get('min_x', 1)} - {movement_bounds.get('max_x', 9999)}")
        print(f"Y: {movement_bounds.get('min_y', 1)} - {movement_bounds.get('max_y', 9999)}")

    for line in result:
        for word_info in line:
            full_text = word_info[1][0]  # Gesamten erkannten Text extrahieren
            confidence = word_info[1][1]  # Vertrauenswert
            x, y = int(word_info[0][0][0]), int(word_info[0][0][1])  # Bildschirm-Position (x, y)

            normalized_text = normalize_text(full_text)
            print(f"[DEBUG] OCR: '{normalized_text}' (Confidence: {confidence}) bei ({x}, {y})")

            # Extrahiere Spielkoordinaten, falls vorhanden
            game_coords = extract_game_coordinates(full_text)
            
            # Whitelist ebenfalls normalisieren
            whitelist_normalized = [normalize_text(name) for name in whitelist]

            # Falls der Name in der Whitelist ist, loggen & speichern
            if any(name in normalized_text for name in whitelist_normalized) and confidence > 0.7:
                # Globale Bildschirm-Position berechnen
                global_x = x1 + x + 20
                global_y = y1 + y + 40
                
                # Wenn Spielkoordinaten erkannt wurden, prüfe Grenzen
                if game_coords:
                    game_x, game_y = game_coords
                    log_event(f"[INFO] Spielkoordinaten erkannt: ({game_x}, {game_y})")
                    
                    # Prüfe, ob Spielkoordinaten innerhalb der Grenzen liegen
                    if movement_bounds and not is_within_game_bounds(game_x, game_y, movement_bounds):
                        # Berechne neue erlaubte Position
                        log_event(f"[WARNING] Position ({game_x}, {game_y}) außerhalb der Spielkoordinaten-Grenzen")
                        target_x, target_y = calculate_center_move_for_game_coordinates((game_x, game_y), movement_bounds)
                        log_event(f"[ACTION] Berechne neue Spielposition: ({target_x}, {target_y})")
                        
                        # Hier müsste man die berechneten Spielkoordinaten in Bildschirmkoordinaten übersetzen
                        # Da wir dafür keine direkte Formel haben, verwenden wir einfach die ursprüngliche Position
                        # und informieren den Nutzer
                        log_event("[INFO] Verwende ursprüngliche Bildschirmposition für Klick")
                        
                # Name und Position speichern (für Klicks immer Bildschirmposition verwenden)
                for whitelist_name in whitelist_normalized:
                    if whitelist_name in normalized_text:
                        name_positions[whitelist_name] = (global_x, global_y)
                        log_event(f"OCR erkannte: '{whitelist_name}' an Position ({global_x}, {global_y})")
                        print(f"[LOG] Match gefunden: '{whitelist_name}' bei ({global_x}, {global_y})")
                        if game_coords:
                            game_x, game_y = game_coords
                            print(f"[LOG] Spielkoordinaten: ({game_x}, {game_y})")
                        break

    return name_positions

def ocr_loop(shared_dict, shared_settings):
    """Führt die OCR-Erkennung aus und aktualisiert die gemeinsame Datenstruktur mit den erkannten Namen und Positionen"""
    recognized_positions = screenshot_ocr_paddle(shared_settings)

    print(f"[DEBUG] OCR-Loop: Erkannte Positionen: {recognized_positions}")

    shared_dict.clear()
    shared_dict.update(recognized_positions)
    
    return recognized_positions

