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

import sys
import os
from detectar_dia import parse_date
from scraper import scrape_chabad_verses
from processor import save_to_json
from scraping_to_word import json_to_word

# ============================================================
# LOCALIZATION CONFIGURATION
# ============================================================

TRANSLATIONS = {
    "es": {
        "welcome": "Bienvenido al script de procesamiento de estudios",
        "enter_date": "Ingrese la fecha a consultar:",
        "date_format_1": "  - Fecha gregoriana (YYYY-MM-DD)",
        "date_format_2": "  - Fecha hebrea numérica (AAAA-MM-DD, año>5000)",
        "date_keywords": "  - Palabras clave: hoy, ayer, anteayer, mañana, pasado",
        "date_empty": "Deje vacío para usar la fecha de hoy.",
        "date_prompt": "Fecha: ",
        "date_selected": "📅 Fecha seleccionada: {}",
        "category_title": "Seleccione una categoría para descargar:",
        "cat_1": "1) Chumash/Tanya",
        "cat_2": "2) Rambam - 1 capítulo",
        "cat_3": "3) Rambam - 3 capítulos (default)",
        "cat_4": "4) Hayom Yom",
        "cat_5": "5) Todas",
        "option_prompt": "Opción: ",
        "template_config_title": "CONFIGURACIÓN DEL TEMPLATE DE WORD",
        "template_instructions": "\n📋 INSTRUCCIONES:\n   1) Proporcione la ruta completa de su archivo .docx template\n   2) Si deja vacío, se usará la configuración por defecto",
        "template_requirements": "\n📝 CÓMO DEBE ESTAR EL TEMPLATE:\n   • El archivo debe ser un documento Word (.docx)\n   • Puede tener headers, footers, estilos, márgenes personalizados\n   • Puede tener configuración de columnas, orientación, etc.",
        "template_injection": "\n✅ QUÉ SE VA A INYECTAR:\n   • El texto hebreo extraído del scraping\n   • Se agregará al final del documento existente",
        "template_untouched": "\n❌ QUÉ NO SE VA A TOCAR:\n   • Headers y footers existentes\n   • Estilos y formatos del template\n   • Configuración de página (márgenes, columnas, etc.)\n   • Cualquier contenido que ya exista en el template",
        "template_path_prompt": "\nRuta del template (Enter para omitir): ",
        "template_path_prompt_simple": "Ruta del template (.docx) [Enter para omitir]: ",
        "using_template": "✓ Usando plantilla: {}",
        "no_template": "⚠️ No se proporcionó plantilla. Se usará configuración por defecto.",
        "output_dir_title": "DIRECTORIO DE SALIDA",
        "output_dir_instructions": "\n📁 Especifique dónde guardar el archivo Word generado:\n   • Proporcione la ruta completa del directorio\n   • Si deja vacío, se guardará en la carpeta 'output'",
        "output_dir_prompt": "\nDirectorio de salida (Enter para usar 'output'): ",
        "output_dir_prompt_simple": "Directorio de salida [Enter para usar 'output']: ",
        "saving_in": "✓ Guardando en: {}",
        "using_default_output": "✓ Usando directorio por defecto: output",
        "step_1": "\n📥 Paso 1/3: Ejecutando scraping...",
        "scraping_ok": "✓ Scraping OK ({} secciones)",
        "scraping_error": "✗ Error scraping: {}",
        "step_2": "\n📝 Paso 2/3: Guardando archivos...",
        "json_generated": "✓ Archivo JSON generado",
        "save_error": "✗ Error al guardar: {}",
        "step_3": "\n📄 Paso 3/3: Generando Word...",
        "word_generated": "✓ Word generado correctamente",
        "word_error": "✗ Error generando Word: {}",
        "files_generated": "\n📄 Archivos generados:",
        "menu_title": "MENÚ PRINCIPAL",
        "menu_opt_1": "1. Ejecutar programa",
        "menu_opt_2": "2. Cambiar idioma / Change Language",
        "menu_opt_3": "3. Salir / Exit",
        "menu_opt_4": "4. Modo Simple: {}",
        "simple_on": "ACTIVADO",
        "simple_off": "DESACTIVADO",
        "bye": "¡Hasta luego!",
        "invalid_option": "Opción no válida."
    },
    "en": {
        "welcome": "Welcome to the study processing script",
        "enter_date": "Enter the date to query:",
        "date_format_1": "  - Gregorian date (YYYY-MM-DD)",
        "date_format_2": "  - Hebrew numeric date (YYYY-MM-DD, year>5000)",
        "date_keywords": "  - Keywords: today, yesterday, tomorrow",
        "date_empty": "Leave empty to use today's date.",
        "date_prompt": "Date: ",
        "date_selected": "📅 Selected date: {}",
        "category_title": "Select a category to download:",
        "cat_1": "1) Chumash/Tanya",
        "cat_2": "2) Rambam - 1 Chapter",
        "cat_3": "3) Rambam - 3 Chapters (default)",
        "cat_4": "4) Hayom Yom",
        "cat_5": "5) All",
        "option_prompt": "Option: ",
        "template_config_title": "WORD TEMPLATE CONFIGURATION",
        "template_instructions": "\n📋 INSTRUCTIONS:\n   1) Provide the full path to your .docx template file\n   2) If left empty, default configuration will be used",
        "template_requirements": "\n📝 TEMPLATE REQUIREMENTS:\n   • The file must be a Word document (.docx)\n   • It can have custom headers, footers, styles, margins\n   • It can have column settings, orientation, etc.",
        "template_injection": "\n✅ WHAT WILL BE INJECTED:\n   • The Hebrew text extracted from scraping\n   • It will be appended to the end of the existing document",
        "template_untouched": "\n❌ WHAT WILL NOT BE TOUCHED:\n   • Existing headers and footers\n   • Template styles and formatting\n   • Page setup (margins, columns, etc.)\n   • Any content already existing in the template",
        "template_path_prompt": "\nTemplate path (Enter to skip): ",
        "template_path_prompt_simple": "Template path (.docx) [Enter to skip]: ",
        "using_template": "✓ Using template: {}",
        "no_template": "⚠️ No template provided. Using default configuration.",
        "output_dir_title": "OUTPUT DIRECTORY",
        "output_dir_instructions": "\n📁 Specify where to save the generated Word file:\n   • Provide the full directory path\n   • If left empty, it will be saved in the 'output' folder",
        "output_dir_prompt": "\nOutput directory (Enter to use 'output'): ",
        "output_dir_prompt_simple": "Output directory [Enter to use 'output']: ",
        "saving_in": "✓ Saving in: {}",
        "using_default_output": "✓ Using default directory: output",
        "step_1": "\n📥 Step 1/3: Running scraping...",
        "scraping_ok": "✓ Scraping OK ({} sections)",
        "scraping_error": "✗ Scraping error: {}",
        "step_2": "\n📝 Step 2/3: Saving files...",
        "json_generated": "✓ JSON file generated",
        "save_error": "✗ Error saving: {}",
        "step_3": "\n📄 Step 3/3: Generating Word...",
        "word_generated": "✓ Word generated successfully",
        "word_error": "✗ Error generating Word: {}",
        "files_generated": "\n📄 Generated files:",
        "menu_title": "MAIN MENU",
        "menu_opt_1": "1. Execute Program",
        "menu_opt_2": "2. Change Language / Cambiar idioma",
        "menu_opt_3": "3. Exit / Salir",
        "menu_opt_4": "4. Simple Mode: {}",
        "simple_on": "ON",
        "simple_off": "OFF",
        "bye": "Goodbye!",
        "invalid_option": "Invalid option."
    }
}

def get_text(key, lang="es", *args):
    """Retrieves text from the dictionary based on language."""
    text = TRANSLATIONS.get(lang, TRANSLATIONS["es"]).get(key, key)
    if args:
        return text.format(*args)
    return text

# ============================================================
# MAIN FUNCTIONS
# ============================================================

def get_date(lang="es"):
    print(get_text("welcome", lang))
    print(get_text("enter_date", lang))
    print(get_text("date_format_1", lang))
    print(get_text("date_format_2", lang))
    print(get_text("date_keywords", lang))
    print(get_text("date_empty", lang))

    user_input = input(get_text("date_prompt", lang)).strip()
    date_obj = parse_date(user_input)

    print(get_text("date_selected", lang, date_obj))
    return date_obj


def get_category_selection(lang="es"):
    print("\n" + "=" * 50)
    print(get_text("category_title", lang))
    print("=" * 50)
    print(get_text("cat_1", lang))
    print(get_text("cat_2", lang))
    print(get_text("cat_3", lang))
    print(get_text("cat_4", lang))
    print(get_text("cat_5", lang))

    choice = input(get_text("option_prompt", lang)).strip()
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


def get_template_path(lang="es", simple_mode=False):
    """
    Solicita la ruta del archivo template de Word
    """
    if not simple_mode:
        print("\n" + "=" * 70)
        print(get_text("template_config_title", lang))
        print("=" * 70)
        print(get_text("template_instructions", lang))
        print(get_text("template_requirements", lang))
        print(get_text("template_injection", lang))
        print(get_text("template_untouched", lang))
        print("\n" + "=" * 70)
        prompt = get_text("template_path_prompt", lang)
    else:
        prompt = get_text("template_path_prompt_simple", lang)
    
    template_path = input(prompt).strip()
    
    if template_path:
        # Remover comillas si el usuario las incluyó
        template_path = template_path.strip('"').strip("'")
        print(get_text("using_template", lang, template_path))
        return template_path
    else:
        print(get_text("no_template", lang))
        return None


def get_output_directory(lang="es", simple_mode=False):
    """
    Solicita el directorio donde guardar el archivo de salida
    """
    if not simple_mode:
        print("\n" + "=" * 70)
        print(get_text("output_dir_title", lang))
        print("=" * 70)
        print(get_text("output_dir_instructions", lang))
        print("\n" + "=" * 70)
        prompt = get_text("output_dir_prompt", lang)
    else:
        prompt = get_text("output_dir_prompt_simple", lang)
    
    output_dir = input(prompt).strip()
    
    if output_dir:
        # Remover comillas si el usuario las incluyó
        output_dir = output_dir.strip('"').strip("'")
        # Crear el directorio si no existe
        os.makedirs(output_dir, exist_ok=True)
        print(get_text("saving_in", lang, output_dir))
        return output_dir
    else:
        print(get_text("using_default_output", lang))
        return "output"


def run_pipeline(date, sections=None, category_name="Study", template_path=None, output_dir="output", lang="es"):
    print(get_text("step_1", lang))
    try:
        data = scrape_chabad_verses(date, sections=sections)
        print(get_text("scraping_ok", lang, len(data)))
    except Exception as e:
        print(get_text("scraping_error", lang, e))
        return None

    print(get_text("step_2", lang))
    try:
        json_file = save_to_json(data)
        print(get_text("json_generated", lang))
    except Exception as e:
        print(get_text("save_error", lang, e))
        return None

    print(get_text("step_3", lang))
    try:
        word_file = json_to_word(json_file, date_obj=date, category_name=category_name, template_path=template_path, output_dir=output_dir)
        print(get_text("word_generated", lang))
    except Exception as e:
        print(get_text("word_error", lang, e))
        return None

    print(get_text("files_generated", lang))
    print(f"  • JSON:  {json_file}")
    print(f"  • Word:  {word_file}")

    return {
        "data": data,
        "files": {
            "json": json_file,
            "word": word_file,
        }
    }

def select_language():
    print("\nSelect Language / Seleccione Idioma:")
    print("1. Español (default)")
    print("2. English")
    choice = input("Option/Opción: ").strip()
    if choice == "2":
        return "en"
    return "es"

def main_menu():
    current_lang = "es"
    simple_mode = False
    
    while True:
        status_text = get_text("simple_on", current_lang) if simple_mode else get_text("simple_off", current_lang)
        
        print("\n" + "=" * 40)
        print(get_text("menu_title", current_lang))
        print("=" * 40)
        print(get_text("menu_opt_1", current_lang))
        print(get_text("menu_opt_2", current_lang))
        print(get_text("menu_opt_4", current_lang, status_text))
        print(get_text("menu_opt_3", current_lang))
        
        choice = input(get_text("option_prompt", current_lang)).strip()
        
        if choice == "1":
            # Ejecutar programa
            template_path = get_template_path(current_lang, simple_mode)
            output_dir = get_output_directory(current_lang, simple_mode)
            date = get_date(current_lang)
            sections, category_name = get_category_selection(current_lang)
            run_pipeline(date, sections=sections, category_name=category_name, template_path=template_path, output_dir=output_dir, lang=current_lang)
            
            input("\nPress Enter to continue..." if current_lang == "en" else "\nPresione Enter para continuar...")
            
        elif choice == "2":
            current_lang = select_language()
            print(f"Language set to: {current_lang}")
            
        elif choice == "3":
            print(get_text("bye", current_lang))
            break
            
        elif choice == "4":
            simple_mode = not simple_mode
            
        else:
            print(get_text("invalid_option", current_lang))

if __name__ == "__main__":
    main_menu()