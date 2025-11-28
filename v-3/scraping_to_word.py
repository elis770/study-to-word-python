"""
Script para convertir scraping de Chabad.org a JSON y luego a Word
Combina la funcionalidad de scraping con generación de documentos Word
"""
import json
import os
from datetime import datetime
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# Importar funciones de los módulos existentes
from scraper import scrape_chabad_verses
from detectar_dia import parse_date

# Configuración
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def scraping_to_json(data, output_file="scraping_output.json"):
    """
    Convierte los datos del scraping a formato JSON
    
    Args:
        data (dict): Diccionario con secciones y sus versículos
        output_file (str): Nombre del archivo JSON de salida
        
    Returns:
        tuple: (ruta del archivo JSON, datos en formato dict)
    """
    # Crear estructura JSON organizada por secciones
    json_data = {}
    
    for section_name, verses in data.items():
        json_data[section_name] = {
            "he_vtitle": "Miqra according to the Masorah",
            "he_text": verses,
            "verse_count": len(verses)
        }
    
    output_path = os.path.join(OUTPUT_DIR, output_file)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)
    
    print(f"✓ JSON guardado en: {output_path}")
    return output_path, json_data


def set_rtl_paragraph(paragraph):
    """
    Configura un párrafo para texto RTL (Right-to-Left) en hebreo
    
    Args:
        paragraph: Objeto de párrafo de python-docx
    """
    pPr = paragraph._element.get_or_add_pPr()
    bidi = OxmlElement('w:bidi')
    bidi.set(qn('w:val'), '1')
    pPr.append(bidi)

def set_columns(section, cols=2):
    """
    Configura la sección para tener múltiples columnas con línea separadora
    """
    sectPr = section._sectPr
    cols_xml = OxmlElement('w:cols')
    cols_xml.set(qn('w:num'), str(cols))
    cols_xml.set(qn('w:sep'), '1')  # Línea separadora
    cols_xml.set(qn('w:space'), '425') # Espacio entre columnas
    sectPr.append(cols_xml)

def json_to_word(json_data, output_file="estudio_diario.docx"):
    """
    Convierte datos JSON a un documento Word con formato RTL y columnas
    """
    doc = Document()
    
    # Procesar cada sección
    for i, (section_name, section_data) in enumerate(json_data.items()):
        verses = section_data.get("he_text", [])
        if not verses:
            continue
            
        first_line = verses[0] if verses else ""
        body_verses = verses[1:] if len(verses) > 1 else []
        
        # Crear nueva sección de Word (excepto para la primera que ya existe)
        if i == 0:
            section = doc.sections[0]
        else:
            section = doc.add_section()
            
        # Configurar márgenes y columnas para esta sección
        section.page_height = Inches(11)
        section.page_width = Inches(8.5)
        section.left_margin = Inches(0.5)
        section.right_margin = Inches(0.5)
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        set_columns(section, 2)
        
        # --- Header Personalizado ---
        header = section.header
        # Borrar contenido anterior si lo hereda
        header.is_linked_to_previous = False
        
        # Limpiar párrafos existentes en el header
        for paragraph in header.paragraphs:
            p = paragraph._element
            p.getparent().remove(p)

        # Crear tabla de 1 fila x 3 columnas para el header
        table = header.add_table(rows=1, cols=3, width=Inches(7.5))
        table.autofit = False
        
        # Columna Izquierda (Cell 0): "לימוד היומי"
        cell_left = table.cell(0, 0)
        p_left = cell_left.paragraphs[0]
        p_left.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run_left = p_left.add_run("לימוד היומי")
        run_left.font.size = Pt(10)
        run_left.font.bold = True
        
        # Columna Centro (Cell 1): Nombre de la Sección
        cell_center = table.cell(0, 1)
        p_center = cell_center.paragraphs[0]
        p_center.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_center = p_center.add_run(section_name)
        run_center.font.size = Pt(12)
        run_center.font.bold = True
        run_center.font.color.rgb = RGBColor(41, 128, 185)
        
        # Columna Derecha (Cell 2): Primera línea del texto
        cell_right = table.cell(0, 2)
        p_right = cell_right.paragraphs[0]
        p_right.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        set_rtl_paragraph(p_right) # RTL para hebreo
        # Truncar si es muy largo para que no rompa el header
        header_text = (first_line[:50] + '...') if len(first_line) > 50 else first_line
        run_right = p_right.add_run(header_text)
        run_right.font.size = Pt(10)
        
        # --- Cuerpo del Texto ---
        for verse in body_verses:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            set_rtl_paragraph(p)
            
            run = p.add_run(verse)
            run.font.size = Pt(11)
            run.font.name = 'David' # Fuente hebrea común
            
            # Mínimo espaciado
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.1

    output_path = os.path.join(OUTPUT_DIR, output_file)
    doc.save(output_path)
    
    print(f"✓ Documento Word guardado en: {output_path}")
    return output_path


def get_date_from_user():
    """
    Solicita al usuario una fecha para el scraping
    
    Returns:
        datetime: Objeto de fecha parseado
    """
    print("=" * 60)
    print("  Script de Scraping a Word")
    print("=" * 60)
    print()
    print("Ingrese la fecha a consultar:")
    print("  - Fecha gregoriana (YYYY-MM-DD)")
    print("  - Fecha hebrea numérica (AAAA-MM-DD, año>5000)")
    print("  - Palabras clave: hoy, ayer, anteayer, mañana, pasado")
    print("Deje vacío para usar la fecha de hoy.")
    print()
    
    user_input = input("Fecha: ").strip()
    date_obj = parse_date(user_input)
    
    print(f"📅 Fecha seleccionada: {date_obj.strftime('%d/%m/%Y')}")
    print()
    return date_obj


def get_category_selection():
    """
    Solicita al usuario que seleccione una categoría para descargar
    
    Returns:
        list: Lista de secciones a scrapear
    """
    print("=" * 60)
    print("Seleccione una categoría para descargar:")
    print("=" * 60)
    print("1) Tanya (jumesh/tania)")
    print("2) Rambam - 1 capítulo")
    print("3) Rambam - 3 capítulos (default)")
    print("4) Hayom Yom")
    print("5) Todas las categorías")
    print()
    
    choice = input("Ingrese el número de opción (1-5) [3]: ").strip()
    if choice == "":
        choice = "3"
    
    # Mapeo de opciones a secciones
    if choice == "1":
        selected = ["Tanya"]
    elif choice == "2":
        selected = ["Rambam_1_Chapter"]
    elif choice == "3":
        selected = ["Rambam_3_Chapters"]
    elif choice == "4":
        selected = ["HayomYom"]
    elif choice == "5":
        selected = None  # None significa todas las secciones
    else:
        print(f"⚠️  Opción inválida '{choice}', usando default (Rambam 3 capítulos)")
        selected = ["Rambam_3_Chapters"]
    
    return selected


def main():
    """
    Función principal que ejecuta todo el pipeline:
    1. Scraping de Chabad.org
    2. Conversión a JSON
    3. Generación de documento Word
    """
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "SCRAPING A WORD - PIPELINE COMPLETO" + " " * 12 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    # Paso 1: Obtener fecha y categoría
    date = get_date_from_user()
    sections = get_category_selection()
    
    print()
    print("=" * 60)
    print("  Iniciando Pipeline")
    print("=" * 60)
    print()
    
    # Paso 2: Scraping
    print("📥 Paso 1/3: Ejecutando scraping con Playwright...")
    try:
        data = scrape_chabad_verses(date, sections=sections)
        total_verses = sum(len(v) for v in data.values())
        print(f"✓ Scraping completado: {total_verses} versículos en {len(data)} secciones")
    except Exception as e:
        print(f"✗ Error en el scraping: {e}")
        return
    
    print()
    
    # Paso 3: Convertir a JSON
    print("📝 Paso 2/3: Convirtiendo a JSON...")
    try:
        json_path, json_data = scraping_to_json(data)
        print(f"✓ JSON generado con {len(json_data)} secciones")
    except Exception as e:
        print(f"✗ Error al generar JSON: {e}")
        return
    
    print()
    
    # Paso 4: Generar Word
    print("📄 Paso 3/3: Generando documento Word...")
    try:
        word_path = json_to_word(json_data)
        print(f"✓ Documento Word generado exitosamente")
    except Exception as e:
        print(f"✗ Error al generar Word: {e}")
        return
    
    print()
    print("=" * 60)
    print("  ✓ Pipeline completado exitosamente")
    print("=" * 60)
    print()
    print("📄 Archivos generados:")
    print(f"  • {json_path}")
    print(f"  • {word_path}")
    print()
    print("💡 Abre el archivo Word para ver el resultado formateado")
    print()


if __name__ == "__main__":
    main()