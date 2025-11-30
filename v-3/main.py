import sys
import os
from detectar_dia import parse_date
from scraper import scrape_chabad_verses
from processor import save_to_json
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
    print("1) Chumash/Tanya")
    print("2) Rambam - 1 capítulo")
    print("3) Rambam - 3 capítulos (default)")
    print("4) Hayom Yom")
import sys
import os
from detectar_dia import parse_date
from scraper import scrape_chabad_verses
from processor import save_to_json
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
    print("1) Chumash/Tanya")
    print("2) Rambam - 1 capítulo")
    print("3) Rambam - 3 capítulos (default)")
    print("4) Hayom Yom")
    print("5) Todas")

    choice = input("Opción: ").strip()
    if choice == "":
        choice = "3"

    mapping = {
        "1": (["Chumash", "Tanya"], "Chumash_Tanya"),
        "2": (["Rambam_1_Chapter"], "Rambam_1"),
        "3": (["Rambam_3_Chapters"], "Rambam_3"),
        "4": (["HayomYom"], "HayomYom"),
        "5": (None, "All_Sections")
    }

    return mapping.get(choice, (["Rambam_3_Chapters"], "Rambam_3"))


def get_template_path():
    """
    Solicita la ruta del archivo template de Word con instrucciones detalladas
    """
    print("\n" + "=" * 70)
    print("CONFIGURACIÓN DEL TEMPLATE DE WORD")
    print("=" * 70)
    print("\n📋 INSTRUCCIONES:")
    print("   1) Proporcione la ruta completa de su archivo .docx template")
    print("   2) Si deja vacío, se usará la configuración por defecto")
    print("\n📝 CÓMO DEBE ESTAR EL TEMPLATE:")
    print("   • El archivo debe ser un documento Word (.docx)")
    print("   • Puede tener headers, footers, estilos, márgenes personalizados")
    print("   • Puede tener configuración de columnas, orientación, etc.")
    print("\n✅ QUÉ SE VA A INYECTAR:")
    print("   • El texto hebreo extraído del scraping")
    print("   • Se agregará al final del documento existente")
    print("\n❌ QUÉ NO SE VA A TOCAR:")
    print("   • Headers y footers existentes")
    print("   • Estilos y formatos del template")
    print("   • Configuración de página (márgenes, columnas, etc.)")
    print("   • Cualquier contenido que ya exista en el template")
    print("\n" + "=" * 70)
    
    template_path = input("\nRuta del template (Enter para omitir): ").strip()
    
    if template_path:
        # Remover comillas si el usuario las incluyó
        template_path = template_path.strip('"').strip("'")
        print(f"✓ Usando plantilla: {template_path}")
        return template_path
    else:
        print("⚠️ No se proporcionó plantilla. Se usará configuración por defecto.")
        return None


def get_output_directory():
    """
    Solicita el directorio donde guardar el archivo de salida
    """
    print("\n" + "=" * 70)
    print("DIRECTORIO DE SALIDA")
    print("=" * 70)
    print("\n📁 Especifique dónde guardar el archivo Word generado:")
    print("   • Proporcione la ruta completa del directorio")
    print("   • Si deja vacío, se guardará en la carpeta 'output'")
    print("\n" + "=" * 70)
    
    output_dir = input("\nDirectorio de salida (Enter para usar 'output'): ").strip()
    
    if output_dir:
        # Remover comillas si el usuario las incluyó
        output_dir = output_dir.strip('"').strip("'")
        # Crear el directorio si no existe
        os.makedirs(output_dir, exist_ok=True)
        print(f"✓ Guardando en: {output_dir}")
        return output_dir
    else:
        print("✓ Usando directorio por defecto: output")
        return "output"


def run_pipeline(date, sections=None, category_name="Study", template_path=None, output_dir="output"):
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
        print("✓ Archivo JSON generado")
    except Exception as e:
        print(f"✗ Error al guardar: {e}")
        return None

    print("\n📄 Paso 3/3: Generando Word...")
    try:
        word_file = json_to_word(json_file, date_obj=date, category_name=category_name, template_path=template_path, output_dir=output_dir)
        print("✓ Word generado correctamente")
    except Exception as e:
        print(f"✗ Error generando Word: {e}")
        return None

    print("\n📄 Archivos generados:")
    print(f"  • JSON:  {json_file}")
    print(f"  • Word:  {word_file}")

    return {
        "data": data,
        "files": {
            "json": json_file,
            "word": word_file,
        }
    }


if __name__ == "__main__":
    template_path = get_template_path()
    output_dir = get_output_directory()
    date = get_date()
    sections, category_name = get_category_selection()
    run_pipeline(date, sections=sections, category_name=category_name, template_path=template_path, output_dir=output_dir)