import sys
from detectar_dia import parse_date
from scraper import scrape_chabad_verses
from processor import save_to_json, save_to_html, save_raw_output
from scraping_to_word import json_to_word

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

    choice = input("Opción: ").strip()
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


def run_pipeline(date, sections=None, template_path=None):
    print("\n📥 Paso 1/3: Ejecutando scraping...")
    try:
        data = scrape_chabad_verses(date, sections=sections)
        print(f"✓ Scraping OK ({len(data)} secciones)")
    except Exception as e:
        print(f"✗ Error scraping: {e}")
        return None

    print("\n📝 Paso 2/3: Guardando archivos...")
    try:
        json_file = save_to_json(data)
        # raw_file = save_raw_output(data)
        # html_file = save_to_html(data)
        print("✓ Archivo JSON generado")
    except Exception as e:
        print(f"✗ Error al guardar: {e}")
        return None

    print("\n📄 Paso 3/3: Generando Word...")
    try:
        word_file = json_to_word(json_file, date_obj=date, template_path=template_path)
        print("✓ Word generado correctamente")
    except Exception as e:
        print(f"✗ Error generando Word: {e}")
        return None

    print("\n📄 Archivos generados:")
    print(f"  • JSON:  {json_file}")
    # print(f"  • Raw:   {raw_file}")
    # print(f"  • HTML:  {html_file}")
    print(f"  • Word:  {word_file}")

    return {
        "data": data,
        "files": {
            "json": json_file,
            # "raw": raw_file,
            # "html": html_file,
            "word": word_file,
        }
    }


if __name__ == "__main__":
    template_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    if template_path:
        print(f"📄 Usando plantilla: {template_path}")
    else:
        print("⚠️ No se proporcionó plantilla. Se usará configuración por defecto.")

    date = get_date()
    sections = get_category_selection()
    run_pipeline(date, sections=sections, template_path=template_path)