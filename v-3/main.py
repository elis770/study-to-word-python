# main.py
from detectar_dia import parse_date

"""
Script Principal - Orquestador del Pipeline de Scraping Rambam
Ejecuta el scraping, procesa los datos y convierte a Word
"""
import sys
from scraper import scrape_chabad_verses
from processor import save_to_json, save_to_html, save_raw_output
from scraping_to_word import json_to_word   # ⬅️ AGREGADO


def get_date():
    print("Bienvenido al script de procesamiento de estudios")
    print("Ingrese la fecha a consultar:")
    print("  - Fecha gregoriana (YYYY-MM-DD)")
    print("  - Fecha hebrea numérica (AAAA-MM-DD, año>5000)")
    print("  - Palabras clave: hoy, ayer, anteayer, mañana, pasado")
    print("Deje vacío para usar la fecha de hoy.")

    user_input = input("Fecha: ").strip()
    date_obj = parse_date(user_input)

    print(f"📅 Fecha seleccionada: {date_obj}")
    return date_obj


def get_category_selection():
    print("\n" + "=" * 50)
    print("Seleccione una categoría para descargar:")
    print("=" * 50)
    print("1) Tanya")
    print("2) Rambam - 1 capítulo")
    print("3) Rambam - 3 capítulos (default)")
    print("4) Hayom Yom")
    print("5) Todas")
    print()

    choice = input("Opción (1-5) [3]: ").strip()
    if choice == "":
        choice = "3"

    mapping = {
        "1": ["Tanya"],
        "2": ["Rambam_1_Chapter"],
        "3": ["Rambam_3_Chapters"],
        "4": ["HayomYom"],
        "5": None
    }

    return mapping.get(choice, ["Rambam_3_Chapters"])


def run_pipeline(date, sections=None):
    print("=" * 50)
    print("  Pipeline Completo")
    print("=" * 50)

    # ---------- SCRAPING ----------
    print("\n📥 Paso 1/3: Ejecutando scraping...")
    try:
        data = scrape_chabad_verses(date, sections=sections)
        print(f"✓ Scraping OK ({len(data)} secciones)")
    except Exception as e:
        print(f"✗ Error scraping: {e}")
        return None

    # ---------- GUARDAR JSON/HTML/RAW ----------
    print("\n📝 Paso 2/3: Guardando archivos...")
    try:
        raw_file = save_raw_output(data)
        json_file = save_to_json(data)       # ⬅️ ruta completa
        html_file = save_to_html(data)
        print("✓ Archivos JSON/HTML generados")
    except Exception as e:
        print(f"✗ Error al guardar: {e}")
        return None

    # ---------- WORD ----------
    print("\n📄 Paso 3/3: Generando Word...")
    try:
        word_file = json_to_word(json_file)   # ⬅️ NUEVO
        print("✓ Word generado correctamente")
    except Exception as e:
        print(f"✗ Error generando Word: {e}")
        return None

    print("\n" + "=" * 50)
    print("  ✓ Pipeline completado")
    print("=" * 50)

    print("\n📄 Archivos generados:")
    print(f"  • Raw:   {raw_file}")
    print(f"  • JSON:  {json_file}")
    print(f"  • HTML:  {html_file}")
    print(f"  • Word:  {word_file}")

    return {
        "data": data,
        "files": {
            "raw": raw_file,
            "json": json_file,
            "html": html_file,
            "word": word_file,
        }
    }


if __name__ == "__main__":
    date = get_date()
    sections = get_category_selection()
    run_pipeline(date, sections=sections)