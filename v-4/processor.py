import json
import os

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_json_text(verses):
    """
    Procesa las líneas del JSON para:
    1. Unir líneas de 1-3 caracteres con la línea siguiente, con formato "letra. texto"
    2. Eliminar líneas que empiezan con "quiz"
    
    Args:
        verses (list): Lista de versículos/líneas de texto
        
    Returns:
        list: Lista procesada de versículos
    """
    if not verses:
        return verses
    
    cleaned = []
    i = 0
    
    while i < len(verses):
        line = verses[i].strip()
        
        # Saltar líneas que empiezan con "quiz" (case-insensitive)
        if line.lower().startswith("quiz"):
            i += 1
            continue
        
        # Verificar si la línea tiene 1-3 caracteres
        if 1 <= len(line) <= 3 and i + 1 < len(verses):
            # Unir con la siguiente línea
            next_line = verses[i + 1].strip()
            # Saltar si la siguiente línea también empieza con "quiz"
            if not next_line.lower().startswith("quiz"):
                merged_line = f"{line}. {next_line}"
                cleaned.append(merged_line)
                i += 2  # Saltar la siguiente línea ya que la unimos
                continue
            else:
                # Si la siguiente empieza con quiz, solo agregar la actual
                cleaned.append(line)
                i += 1
                continue
        
        # Agregar línea normal
        cleaned.append(line)
        i += 1
    
    return cleaned

def save_to_json(data, output_file="salida_formateada.json"):
    json_data = {}
    
    for section_name, verses in data.items():
        # Aplicar limpieza a cada sección
        cleaned_verses = clean_json_text(verses)
        json_data[section_name] = {
            "he_text": cleaned_verses
        }
    
    output_path = os.path.join(OUTPUT_DIR, output_file)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)
    
    return output_path