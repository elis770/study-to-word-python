# main.py
from detectar_dia import parse_date

"""
Script Principal - Orquestador del Pipeline de Scraping Rambam
Ejecuta el scraping, procesa los datos y abre un shell interactivo
"""
import sys
import code
from scraper import scrape_chabad_verses
from processor import save_to_json, save_to_html, save_raw_output

def get_date():
    print("Bienvenido al script de procesamiento de estudios")
    print("Ingrese la fecha a consultar:")
    print("  - Fecha gregoriana (YYYY-MM-DD)")
    print("  - Fecha hebrea numérica (AAAA-MM-DD, año>5000)")
    print("  - Palabras clave: hoy, ayer, anteayer, mañana, pasado")
    print("Deje vacío para usar la fecha de hoy.")

    user_input = input("Fecha: ").strip()
    date_obj = parse_date(user_input)
    result = date_obj

    print(result)
    return result

def get_category_selection():
    """
    Solicita al usuario que seleccione una categoría para descargar
    
    Returns:
        list: Lista de secciones a scrapear
    """
    print()
    print("=" * 50)
    print("Seleccione una categoría para descargar:")
    print("=" * 50)
    print("1) Tanya (jumesh/tania)")
    print("2) Rambam - 1 capítulo")
    print("3) Rambam - 3 capítulos (default)")
    print("4) Hayom Yom")
    print("5) Todas las categorías")
    print()
    
    choice = input("Ingrese el número de opción (1-5) [por default es 3]: ").strip()
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

def run_pipeline(date, sections=None):
    """
    Ejecuta el pipeline completo de scraping y procesamiento
    
    Args:
        date: Fecha para el scraping
        sections: Lista de secciones a scrapear (None = todas)
    
    Returns:
        dict: Diccionario con los resultados y rutas de archivos generados
    """
    print("=" * 50)
    print("  Pipeline Completo de Scraping Rambam")
    print("=" * 50)
    print()
    
    # Paso 1: Scraping
    print("📥 Paso 1/2: Ejecutando scraping con Playwright...")
    try:
        data = scrape_chabad_verses(date, sections=sections)
        total_verses = sum(len(v) for v in data.values())
        print(f"✓ Scraping completado: {total_verses} versículos extraídos en {len(data)} secciones")
    except Exception as e:
        print(f"✗ Error en el scraping: {e}")
        return None
    
    print()
    
    # Paso 2: Procesamiento
    print("🔄 Paso 2/2: Procesando datos y generando archivos...")
    try:
        raw_file = save_raw_output(data)
        json_file = save_to_json(data)
        html_file = save_to_html(data)
        
        print("✓ Procesamiento completado")
    except Exception as e:
        print(f"✗ Error en el procesamiento: {e}")
        return None
    
    print()
    print("=" * 50)
    print("  ✓ Pipeline completado exitosamente")
    print("=" * 50)
    print()
    print("📄 Archivos generados:")
    print(f"  • {raw_file} - Salida raw del scraping")
    print(f"  • {json_file} - JSON formato Sefaria API")
    print(f"  • {html_file} - Visualizador HTML RTL")
    print()
    print("🌐 Abre salida_rtl.html en tu navegador para ver el resultado")
    print()
    
    return {
        "data": data,
        "files": {
            "raw": raw_file,
            "json": json_file,
            "html": html_file
        }
    }

if __name__ == "__main__":
    date = get_date()
    sections = get_category_selection()
    
    # Ejecutar el pipeline
    results = run_pipeline(date, sections=sections)