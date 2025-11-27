"""
Módulo de Procesamiento de Datos
Responsabilidad única: Procesar datos y guardarlos en archivos (JSON, HTML)
"""
import json
import os

# Crear carpeta de salida si no existe
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_to_json(data, output_file="salida_formateada.json"):
    """
    Guarda los versículos en formato JSON compatible con Sefaria API
    
    Args:
        data (dict): Diccionario con secciones y sus versículos
                     Ejemplo: {'Tanya': [...], 'Rambam_1_Chapter': [...]}
        output_file (str): Nombre del archivo de salida
        
    Returns:
        str: Ruta del archivo generado
    """
    # Crear estructura JSON organizada por secciones
    json_data = {}
    
    for section_name, verses in data.items():
        json_data[section_name] = {
            "he_vtitle": "Miqra according to the Masorah",
            "he_text": verses
        }
    
    output_path = os.path.join(OUTPUT_DIR, output_file)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)
    
    return output_path



def save_to_html(data, output_file="salida_rtl.html"):
    """
    Genera un archivo HTML con visualización RTL de los versículos organizado por secciones
    
    Args:
        data (dict): Diccionario con secciones y sus versículos
        output_file (str): Nombre del archivo HTML de salida
        
    Returns:
        str: Ruta del archivo generado
    """
    html_content = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>לימוד יומי - Versículos en Hebreo</title>
    <style>
        body {{
            font-family: 'David Libre', 'Times New Roman', serif;
            direction: rtl;
            text-align: right;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            line-height: 1.8;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            text-align: center;
        }}
        h2 {{
            color: #2980b9;
            margin-top: 30px;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 5px;
        }}
        .metadata {{
            background-color: #e8f4f8;
            padding: 10px;
            margin: 20px 0;
            border-radius: 4px;
            font-size: 14px;
            color: #555;
        }}
        .verse {{
            background-color: white;
            padding: 15px;
            margin: 10px 0;
            border-right: 4px solid #3498db;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-radius: 4px;
        }}
        .verse-number {{
            color: #3498db;
            font-weight: bold;
            margin-left: 10px;
            font-size: 16px;
        }}
        .verse-text {{
            font-size: 18px;
            color: #333;
            line-height: 2;
        }}
    </style>
</head>
<body>
    <h1>לימוד יומי</h1>
    <div class="metadata">
        <strong>מקור:</strong> Miqra according to the Masorah
    </div>
    <div id="verses-container">
"""
    
    # Agregar cada sección
    for section_name, verses in data.items():
        html_content += f"""        <div class="section">
            <h2>{section_name}</h2>
"""
        if not verses:
             html_content += """            <p>No se encontraron versículos para esta sección.</p>
"""
        else:
            for i, verse in enumerate(verses, 1):
                html_content += f"""            <div class="verse">
                <span class="verse-number">{i}</span>
                <span class="verse-text">{verse}</span>
            </div>
"""
        html_content += """        </div>
"""
    
    html_content += """    </div>
</body>
</html>
"""
    
    output_path = os.path.join(OUTPUT_DIR, output_file)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return output_path


def save_raw_output(data, output_file="salida4.txt"):
    """
    Guarda la salida raw del scraping
    
    Args:
        data (dict): Diccionario con secciones y sus versículos
        output_file (str): Nombre del archivo de salida
        
    Returns:
        str: Ruta del archivo generado
    """
    output_path = os.path.join(OUTPUT_DIR, output_file)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("Iniciando scraping...\n")
        f.write("==========================================\n")
        
        for section, verses in data.items():
            f.write(f"SECCIÓN: {section}\n")
            f.write(f"Cantidad: {len(verses)}\n")
            f.write("-" * 20 + "\n")
            f.write(str(verses))
            f.write("\n\n")
            f.write("==========================================\n")
    
    return output_path


if __name__ == "__main__":
    # Ejemplo de uso independiente
    print("📝 Ejecutando procesador independientemente...")
    sample_verses = ["פסוק לדוגמה 1", "פסוק לדוגמה 2", "פסוק לדוגמה 3"]
    
    json_file = save_to_json(sample_verses)
    html_file = save_to_html(sample_verses)
    raw_file = save_raw_output(sample_verses)
    
    print(f"✓ Archivos generados:")
    print(f"  • {json_file}")
    print(f"  • {html_file}")
    print(f"  • {raw_file}")