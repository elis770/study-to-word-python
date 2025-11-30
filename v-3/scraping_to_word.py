"""
Módulo optimizado para insertar texto hebreo en un Word basado en una plantilla
sin modificar ninguna configuración del documento.

La plantilla controla:
- columnas
- márgenes
- fuentes y tamaños
- RTL
- estilos
- encabezados / tablas de encabezado
"""

import json
import os
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# Helper functions for RTL and column configuration
# ============================================================

def set_rtl_paragraph(paragraph):
    """Configura un párrafo como RTL."""
    pPr = paragraph._element.get_or_add_pPr()
    bidi = OxmlElement("w:bidi")
    bidi.set(qn("w:val"), "1")
    pPr.append(bidi)


def set_columns(section, cols=2):
    """Configura columnas de una sección Word."""
    sectPr = section._sectPr
    
    # Configuración RTL para la sección (importante para el orden de columnas)
    if not sectPr.find(qn("w:bidi")):
        bidi = OxmlElement("w:bidi")
        sectPr.append(bidi)

    cols_xml = OxmlElement("w:cols")
    cols_xml.set(qn("w:num"), str(cols))
    cols_xml.set(qn("w:sep"), "1")  # Línea entre columnas
    cols_xml.set(qn("w:space"), "425")  # 0.75 cm
    cols_xml.set(qn("w:equalWidth"), "1")
    sectPr.append(cols_xml)


# ============================================================
# 1. Proceso el JSON: obtengo el header y cuerpo de cada sección
# ============================================================

def process_json_data(json_file_path: str):
    """
    Convierte el JSON en una lista lista de secciones.
    Cada sección contiene:
    - name: nombre del estudio (Chumash, Rambam, etc.)
    - header_text: primer versículo
    - body: todos los demás versículos
    """
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    processed_sections = []

    for section_name, section_data in data.items():
        verses = section_data.get("he_text", [])
        if not verses:
            continue

        first_line = verses[0] if verses else ""
        body = verses[1:] if len(verses) > 1 else []

        processed_sections.append({
            "name": section_name,
            "header_text": first_line,
            "body": body
        })

    return processed_sections


# ============================================================
# 2a. Crear Word desde plantilla: REEMPLAZAR contenido
# ============================================================

def create_word_from_template(sections_data,
                              template_path: str,
                              output_file: str = "estudio_diario.docx",
                              output_dir: str = "output"):
    """
    Usa un archivo .docx de plantilla que ya contiene:
    - Estilos configurados
    - Columnas (si las hay)
    - RTL
    - Encabezados
    - Cualquier diseño deseado

    El script ELIMINA el contenido existente e inserta el nuevo texto
    respetando los estilos configurados en la plantilla.
    """

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"La plantilla no existe: {template_path}")

    # Cargar plantilla
    doc = Document(template_path)

    # 🔥 PASO 0: Capturar la fuente del primer párrafo ANTES de borrar
    # Esto asegura que usemos la tipografía exacta que el usuario configuró
    template_font_name = None
    template_font_size = None
    
    if doc.paragraphs:
        first_para = doc.paragraphs[0]
        if first_para.runs:
            first_run = first_para.runs[0]
            template_font_name = first_run.font.name
            template_font_size = first_run.font.size

    # 🔥 PASO 1: Eliminar TODO el contenido existente (párrafos)
    # Mantener solo la estructura (secciones, headers, footers, estilos)
    for paragraph in doc.paragraphs[:]:  # [:] crea una copia para iterar seguro
        p_element = paragraph._element
        p_element.getparent().remove(p_element)

    # 🔥 PASO 2: Insertar nuevo texto usando el estilo por defecto de la plantilla
    for section in sections_data:
        # Insertar versículos
        for verse in section["body"]:
            # Agregar párrafo usando el estilo "Normal" de la plantilla
            p = doc.add_paragraph(verse, style='Normal')
            
            # 🔥 Aplicar la fuente capturada de la plantilla original
            if p.runs and template_font_name:
                for run in p.runs:
                    run.font.name = template_font_name
                    if template_font_size:
                        run.font.size = template_font_size

    # Guardar documento resultante
    out_path = os.path.join(output_dir, output_file)
    doc.save(out_path)

    print(f"✓ Documento generado: {out_path}")

    return out_path


# ============================================================
# 2b. Crear Word desde cero (fallback sin plantilla)
# ============================================================

def create_word_from_scratch(sections_data, output_file="estudio_diario.docx", output_dir="output"):
    """
    Genera el documento Word programáticamente cuando no hay plantilla.
    Aplica configuración RTL, columnas, headers, etc.
    """
    doc = Document()

    for i, section_info in enumerate(sections_data):
        # CREAR SECCIÓN
        section = doc.sections[0] if i == 0 else doc.add_section()

        # Configuración de página
        section.page_height = Inches(11)
        section.page_width = Inches(8.5)
        section.left_margin = Inches(0.5)
        section.right_margin = Inches(0.5)
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)

        # Columnas
        set_columns(section, 2)

        # ===========================
        # HEADER
        # ===========================
        header = section.header
        header.is_linked_to_previous = False

        # Limpiar contenido existente
        for p in header.paragraphs:
            p._element.getparent().remove(p._element)

        # Crear tabla (3 columnas) con WIDTH
        table = header.add_table(rows=1, cols=3, width=Inches(6.5))
        table.autofit = True

        # Izquierda
        cell_left = table.cell(0, 0).paragraphs[0]
        run_left = cell_left.add_run("לימוד היומי")
        run_left.font.size = Pt(10)
        run_left.font.bold = True

        # Centro
        cell_center = table.cell(0, 1).paragraphs[0]
        run_center = cell_center.add_run(section_info["name"])
        run_center.font.size = Pt(12)
        run_center.font.bold = True
        run_center.font.color.rgb = RGBColor(41, 128, 185)

        # Derecha
        p_right = table.cell(0, 2).paragraphs[0]
        set_rtl_paragraph(p_right)
        
        raw_header = section_info["header_text"]
        header_text = raw_header[:50] + "..." if len(raw_header) > 50 else raw_header
        
        run_right = p_right.add_run(header_text)
        run_right.font.size = Pt(10)

        # ===========================
        # CUERPO
        # ===========================
        for verse in section_info["body"]:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            set_rtl_paragraph(p)

            run = p.add_run(verse)
            run.font.size = Pt(11)
            run.font.name = "David"

    out_path = os.path.join(output_dir, output_file)
    doc.save(out_path)
    print(f"✓ Word generado: {out_path}")
    
    # Abrir automáticamente archivo y carpeta
    try:
        os.startfile(out_path)
        os.startfile(os.path.dirname(out_path))
    except Exception as e:
        print(f"Nota: No se pudo abrir automáticamente el archivo/carpeta: {e}")
        
    return out_path

    cols_xml.set(qn("w:sep"), "1")  # Línea entre columnas
    cols_xml.set(qn("w:space"), "425")  # 0.75 cm
    cols_xml.set(qn("w:equalWidth"), "1")
    sectPr.append(cols_xml)


# ============================================================
# 1. Proceso el JSON: obtengo el header y cuerpo de cada sección
# ============================================================

def process_json_data(json_file_path: str):
    """
    Convierte el JSON en una lista lista de secciones.
    Cada sección contiene:
    - name: nombre del estudio (Chumash, Rambam, etc.)
    - header_text: primer versículo
    - body: todos los demás versículos
    """
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    processed_sections = []

    for section_name, section_data in data.items():
        verses = section_data.get("he_text", [])
        if not verses:
            continue

        first_line = verses[0] if verses else ""
        body = verses[1:] if len(verses) > 1 else []

        processed_sections.append({
            "name": section_name,
            "header_text": first_line,
            "body": body
        })

    return processed_sections


# ============================================================
# 2a. Crear Word desde plantilla: REEMPLAZAR contenido
# ============================================================

def create_word_from_template(sections_data,
                              template_path: str,
                              output_file: str = "estudio_diario.docx",
                              output_dir: str = "output"):
    """
    Usa un archivo .docx de plantilla que ya contiene:
    - Estilos configurados
    - Columnas (si las hay)
    - RTL
    - Encabezados
    - Cualquier diseño deseado

    El script ELIMINA el contenido existente e inserta el nuevo texto
    respetando los estilos configurados en la plantilla.
    """

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"La plantilla no existe: {template_path}")

    # Cargar plantilla
    doc = Document(template_path)

    # 🔥 PASO 0: Capturar la fuente del primer párrafo ANTES de borrar
    # Esto asegura que usemos la tipografía exacta que el usuario configuró
    template_font_name = None
    template_font_size = None
    
    if doc.paragraphs:
        first_para = doc.paragraphs[0]
        if first_para.runs:
            first_run = first_para.runs[0]
            template_font_name = first_run.font.name
            template_font_size = first_run.font.size

    # 🔥 PASO 1: Eliminar TODO el contenido existente (párrafos)
    # Mantener solo la estructura (secciones, headers, footers, estilos)
    for paragraph in doc.paragraphs[:]:  # [:] crea una copia para iterar seguro
        p_element = paragraph._element
        p_element.getparent().remove(p_element)

    # 🔥 PASO 2: Insertar nuevo texto usando el estilo por defecto de la plantilla
    for section in sections_data:
        # Insertar versículos
        for verse in section["body"]:
            # Agregar párrafo usando el estilo "Normal" de la plantilla
            p = doc.add_paragraph(verse, style='Normal')
            
            # 🔥 Aplicar la fuente capturada de la plantilla original
            if p.runs and template_font_name:
                for run in p.runs:
                    run.font.name = template_font_name
                    if template_font_size:
                        run.font.size = template_font_size

    # Guardar documento resultante
    out_path = os.path.join(output_dir, output_file)
    doc.save(out_path)

    print(f"✓ Documento generado: {out_path}")

    return out_path


# ============================================================
# 2b. Crear Word desde cero (fallback sin plantilla)
# ============================================================

def create_word_from_scratch(sections_data, output_file="estudio_diario.docx", output_dir="output"):
    """
    Genera el documento Word programáticamente cuando no hay plantilla.
    Aplica configuración RTL, columnas, headers, etc.
    """
    doc = Document()

    for i, section_info in enumerate(sections_data):
        # CREAR SECCIÓN
        section = doc.sections[0] if i == 0 else doc.add_section()

        # Configuración de página
        section.page_height = Inches(11)
        section.page_width = Inches(8.5)
        section.left_margin = Inches(0.5)
        section.right_margin = Inches(0.5)
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)

        # Columnas
        set_columns(section, 2)

        # ===========================
        # HEADER
        # ===========================
        header = section.header
        header.is_linked_to_previous = False

        # Limpiar contenido existente
        for p in header.paragraphs:
            p._element.getparent().remove(p._element)

        # Crear tabla (3 columnas) con WIDTH
        table = header.add_table(rows=1, cols=3, width=Inches(6.5))
        table.autofit = True

        # Izquierda
        cell_left = table.cell(0, 0).paragraphs[0]
        run_left = cell_left.add_run("לימוד היומי")
        run_left.font.size = Pt(10)
        run_left.font.bold = True

        # Centro
        cell_center = table.cell(0, 1).paragraphs[0]
        run_center = cell_center.add_run(section_info["name"])
        run_center.font.size = Pt(12)
        run_center.font.bold = True
        run_center.font.color.rgb = RGBColor(41, 128, 185)

        # Derecha
        p_right = table.cell(0, 2).paragraphs[0]
        set_rtl_paragraph(p_right)
        
        raw_header = section_info["header_text"]
        header_text = raw_header[:50] + "..." if len(raw_header) > 50 else raw_header
        
        run_right = p_right.add_run(header_text)
        run_right.font.size = Pt(10)

        # ===========================
        # CUERPO
        # ===========================
        for verse in section_info["body"]:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            set_rtl_paragraph(p)

            run = p.add_run(verse)
            run.font.size = Pt(11)
            run.font.name = "David"

    out_path = os.path.join(output_dir, output_file)
    doc.save(out_path)
    print(f"✓ Word generado: {out_path}")
    
    # Abrir automáticamente archivo y carpeta
    try:
        os.startfile(out_path)
        os.startfile(os.path.dirname(out_path))
    except Exception as e:
        print(f"Nota: No se pudo abrir automáticamente el archivo/carpeta: {e}")
        
    return out_path


# ============================================================
# 3. Función orquestadora
# ============================================================

def json_to_word(json_file_path: str,
                 date_obj=None,
                 category_name="Study",
                 template_path: str = None,
                 output_file="estudio_diario.docx",
                 output_dir="output"):
    """
    Convierte un JSON a Word.
    - Si template_path existe: usa la plantilla
    - Si no: genera el documento desde cero con configuración RTL
    """
    # Crear el directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Ajustar nombre según fecha y categoría
    if date_obj:
        # Convertir datetime a string con formato YYYY-MM-DD (sin caracteres inválidos)
        date_str = str(date_obj).split()[0] if ' ' in str(date_obj) else str(date_obj)
        # Construir nombre del archivo: Categoria_Fecha.docx
        safe_category = category_name.replace(" ", "_").replace("/", "-")
        output_file = f"{safe_category}_{date_str}.docx"

    # Procesar JSON
    sections_data = process_json_data(json_file_path)

    # Decidir método de generación
    if template_path and os.path.exists(template_path):
        print(f"📄 Usando plantilla: {template_path}")
        return create_word_from_template(
            sections_data,
            template_path=template_path,
            output_file=output_file,
            output_dir=output_dir
        )
    else:
        if template_path:
            print(f"⚠️ Plantilla no encontrada: {template_path}")
        print("📝 Generando documento desde cero...")
        return create_word_from_scratch(
            sections_data,
            output_file=output_file,
            output_dir=output_dir
        )