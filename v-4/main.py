import sys
import os
import json
from detectar_dia import parse_date
from scraper import scrape_chabad_verses
from processor import save_to_json
from scraping_to_word import json_to_word

# ============================================================
# LOCALIZATION CONFIGURATION
# ============================================================

def load_translations():
    """Carga las traducciones desde el archivo JSON"""
    translations_path = os.path.join(os.path.dirname(__file__), "translations.json")
    try:
        with open(translations_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Warning: translations.json not found at {translations_path}")
        return {"es": {}, "en": {}}
    except json.JSONDecodeError as e:
        print(f"⚠️ Warning: Error loading translations.json: {e}")
        return {"es": {}, "en": {}}

TRANSLATIONS = load_translations()

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


def run_pipeline(date, sections=None, category_name="Study", template_path=None, output_dir="output", lang="es", content_lang="he"):
    print(get_text("step_1", lang))
    try:
        data = scrape_chabad_verses(date, sections=sections, lang=content_lang)
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
    content_lang = "he"
    
    while True:
        status_text = get_text("simple_on", current_lang) if simple_mode else get_text("simple_off", current_lang)
        
        # Determinar el texto del idioma del contenido
        if content_lang == "he":
            content_lang_text = get_text("content_lang_he", current_lang)
        elif content_lang == "en":
            content_lang_text = get_text("content_lang_en", current_lang)
        else:  # both
            content_lang_text = get_text("content_lang_both", current_lang)
        
        print("\n" + "=" * 40)
        print(get_text("menu_title", current_lang))
        print("=" * 40)
        print("\n" + "x" * 40)
        print("Sobre la opcion 4, no estuvo funcionando el cambio de idioma, por favor, selecciona la opcion 2 para cambiar el idioma., eso se vera en la proxima actualizacion")
        print("\n" + "Regarding option 4, the language change wasn’t working. Please select option 2 to change the language. This will be fixed in the next update")
        print("x" * 40)
        print(get_text("menu_opt_1", current_lang))
        print(get_text("menu_opt_2", current_lang))
        print(get_text("menu_opt_3", current_lang, status_text))
        print(get_text("menu_opt_4", current_lang, content_lang_text))
        print(get_text("menu_opt_5", current_lang))
        
        choice = input(get_text("option_prompt", current_lang)).strip()
        
        if choice == "1":
            # Ejecutar programa
            template_path = get_template_path(current_lang, simple_mode)
            output_dir = get_output_directory(current_lang, simple_mode)
            date = get_date(current_lang)
            sections, category_name = get_category_selection(current_lang)
            run_pipeline(date, sections=sections, category_name=category_name, template_path=template_path, output_dir=output_dir, lang=current_lang, content_lang=content_lang)
            
            input("\nPress Enter to continue..." if current_lang == "en" else "\nPresione Enter para continuar...")
            
        elif choice == "2":
            current_lang = select_language()
            print(f"Language set to: {current_lang}")
            
            
        elif choice == "3":
            simple_mode = not simple_mode
            
        elif choice == "4":
            # Ciclar entre he → en → both
            if content_lang == "he":
                content_lang = "en"
                print(get_text("content_lang_warning", current_lang))
            elif content_lang == "en":
                content_lang = "both"
            else:  # both
                content_lang = "he"
            
        elif choice == "5":
            print(get_text("bye", current_lang))
            break
        else:
            print(get_text("invalid_option", current_lang))

if __name__ == "__main__":
    main_menu()