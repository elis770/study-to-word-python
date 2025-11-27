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

def run_pipeline(date):
    """
    Ejecuta el pipeline completo de scraping y procesamiento
    
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
        data = scrape_chabad_verses(date)
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


def start_interactive_shell(results):
    """
    Inicia un shell interactivo de Python con los resultados cargados
    
    Args:
        results (dict): Resultados del pipeline
    """
    print("=" * 50)
    print("  🐍 Iniciando Shell Interactivo de Python")
    print("=" * 50)
    print()
    print("Variables disponibles:")
    print("  • results - Diccionario con todos los resultados")
    print("  • data - Diccionario con versículos por sección")
    print("  • files - Diccionario con rutas de archivos generados")
    print()
    print("Funciones disponibles:")
    print("  • scrape_chabad_verses(date) - Ejecutar scraping nuevamente")
    print("  • save_to_json(data) - Guardar en JSON")
    print("  • save_to_html(data) - Guardar en HTML")
    print()
    print("Escribe 'exit()' o presiona Ctrl+Z + Enter para salir")
    print("=" * 50)
    print()
    
    # Preparar variables para el shell
    data = results["data"] if results else {}
    files = results["files"] if results else {}
    
    # Crear un namespace con las variables y funciones útiles
    local_vars = {
        "results": results,
        "data": data,
        "files": files,
        "scrape_chabad_verses": scrape_chabad_verses,
        "save_to_json": save_to_json,
        "save_to_html": save_to_html,
        "save_raw_output": save_raw_output,
    }
    
    # Iniciar el shell interactivo
    code.interact(local=local_vars, banner="")


if __name__ == "__main__":
    date = get_date()
    # Ejecutar el pipeline
    results = run_pipeline(date)
    
    # Iniciar shell interactivo
    if results:
        start_interactive_shell(results)
    else:
        print("⚠️  El pipeline falló. No se puede iniciar el shell interactivo.")
        sys.exit(1)