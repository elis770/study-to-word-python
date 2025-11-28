"""
Módulo para convertir un JSON generado por el pipeline principal a un documento Word (RTL)
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


def set_rtl_paragraph(paragraph):
    """Configura un párrafo como RTL."""
    pPr = paragraph._element.get_or_add_pPr()
    bidi = OxmlElement("w:bidi")
    bidi.set(qn("w:val"), "1")
    pPr.append(bidi)


def set_columns(section, cols=2):
    """Configura columnas de una sección Word."""
    sectPr = section._sectPr
    cols_xml = OxmlElement("w:cols")
    cols_xml.set(qn("w:num"), str(cols))
    cols_xml.set(qn("w:sep"), "1")
    cols_xml.set(qn("w:space"), "425")
    sectPr.append(cols_xml)


def json_to_word(json_file_path: str, output_file="estudio_diario.docx"):
    """
    Convierte un archivo JSON (ruta completa) a documento Word.
    
    Args:
        json_file_path (str): ruta del archivo JSON generado por el pipeline
        output_file (str): nombre del archivo Word final
    """
    # Leer JSON
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    doc = Document()

    for i, (section_name, section_data) in enumerate(data.items()):
        verses = section_data.get("he_text", [])
        if not verses:
            continue

        first_line = verses[0] if verses else ""
        body = verses[1:] if len(verses) > 1 else []

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

        # Crear tabla (3 columnas) con WIDTH (CORREGIDO)
        table = header.add_table(rows=1, cols=3, width=Inches(6.5))
        table.autofit = True

        # Izquierda
        cell_left = table.cell(0, 0).paragraphs[0]
        run_left = cell_left.add_run("לימוד היומי")
        run_left.font.size = Pt(10)
        run_left.font.bold = True

        # Centro
        cell_center = table.cell(0, 1).paragraphs[0]
        run_center = cell_center.add_run(section_name)
        run_center.font.size = Pt(12)
        run_center.font.bold = True
        run_center.font.color.rgb = RGBColor(41, 128, 185)

        # Derecha
        p_right = table.cell(0, 2).paragraphs[0]
        set_rtl_paragraph(p_right)
        header_text = first_line[:50] + "..." if len(first_line) > 50 else first_line
        run_right = p_right.add_run(header_text)
        run_right.font.size = Pt(10)

        # ===========================
        # CUERPO
        # ===========================
        for verse in body:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            set_rtl_paragraph(p)

            run = p.add_run(verse)
            run.font.size = Pt(11)
            run.font.name = "David"

    out_path = os.path.join(OUTPUT_DIR, output_file)
    doc.save(out_path)

    print(f"✓ Word generado: {out_path}")
    return out_path