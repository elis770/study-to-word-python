"""
Scraper modular de Chabad.org
Responsabilidad única: Obtener textos en hebreo de varias secciones
"""

from playwright.sync_api import sync_playwright
from datetime import datetime

# -------------------------------
# Configuración de URLs y tipos
# -------------------------------
BASE_URLS = {
    'Chumash': 'torahreading',
    'Tehilim': 'tehillim',
    'Tanya': 'tanya',
    'Rambam_1_Chapter': None,  # Se maneja como caso especial
    'Rambam_3_Chapters': None,  # Se maneja como caso especial
    'HayomYom': 'hayomyom'
}

SECTION_TYPE = {
    "Chumash": "tabla_hebrew",
    "Tehilim": "tabla_hebrew",
    "Tanya": "tanya",
    "Rambam_1_Chapter": "rambam",
    "Rambam_3_Chapters": "rambam",
    "HayomYom": "hayom_yom"
}

CLASES_PERMITIDAS = {'co_VerseNum', 'co_VerseText', 'co_RashiTitle', 'co_RashiText'}

# -------------------------------
# Funciones auxiliares
# -------------------------------
def build_url(section, date=None):
    """
    Genera la URL para una sección y fecha dadas.
    Maneja Rambam como caso especial según el número de capítulos.
    """
    if section in ["Rambam_1_Chapter", "Rambam_3_Chapters"]:
        chapters = "1" if section == "Rambam_1_Chapter" else "3"
        return f"https://www.chabad.org/dailystudy/rambam_cdo/rambamChapters/{chapters}#lt=he"

    base_path = BASE_URLS.get(section)
    if not base_path:
        raise ValueError(f"Sección desconocida: {section}")
    if date is None:
        date = datetime.today()
    formatted_date = date.strftime("%m/%d/%Y")
    return f"https://www.chabad.org/dailystudy/{base_path}.asp?tdate={formatted_date}#lt=he"

def scrape_single_url(url, section_name, section_type):
    """Scraping de una URL según tipo de sección"""
    print(f"  📄 Scraping {section_name} ({section_type})...")
    print(f"     🔗 {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--ignore-certificate-errors"])
        page = browser.new_page(ignore_https_errors=True)
        page.on("console", lambda msg: print(f"     🔍 [JS]: {msg.text}") if "Failed to load resource" not in msg.text else None)
        page.goto(url, wait_until="domcontentloaded")

        verses = page.evaluate(f"""() => {{
            const results = [];
            const seen = new Set();
            function addText(text) {{
                const cleanText = text.trim();
                if (cleanText && !seen.has(cleanText)) {{
                    results.push(cleanText);
                    seen.add(cleanText);
                }}
            }}
            const section_type = "{section_type}";
            const clasesPermitidas = new Set({list(CLASES_PERMITIDAS)});
            if (section_type === "tabla_hebrew") {{
                document.querySelectorAll('td.hebrew').forEach(td => {{
                    const spansValidos = Array.from(td.querySelectorAll('span')).filter(span =>
                        Array.from(span.classList).some(c => clasesPermitidas.has(c))
                    );
                    const spansText = spansValidos.map(span => span.innerText.trim()).filter(t => t).join(' ');
                    if (spansText) addText(spansText);
                }});
            }} else if (section_type === "hayom_yom") {{
                document.querySelectorAll('div.hayom-yom-info').forEach(el => addText(el.innerText));
            }} else if (section_type === "rambam") {{
                document.querySelectorAll('h2, span[lang="he"]').forEach(el => addText(el.innerText));
            }} else if (section_type === "tanya") {{
                document.querySelectorAll('h2, span[lang="he"]').forEach(el => addText(el.innerText));
            }}
            return results;
        }}""")
        browser.close()
        return verses

def scrape_chabad_verses(date=None, sections=None):
    """
    Extrae versículos de las secciones especificadas
    
    Args:
        date: Fecha para el scraping (None = hoy)
        sections: Lista de secciones a scrapear (None = todas)
    """
    if date is None:
        date = datetime.today()
    formatted_date = date.strftime("%m/%d/%Y")
    print(f"📅 Fecha: {formatted_date}")
    
    # Si no se especifican secciones, usar todas
    if sections is None:
        sections_to_scrape = list(BASE_URLS.keys())
    else:
        sections_to_scrape = sections
    
    results = {}
    for section_name in sections_to_scrape:
        section_type = SECTION_TYPE.get(section_name, "lang_he")
        url = build_url(section_name, date)
        try:
            verses = scrape_single_url(url, section_name, section_type)
            results[section_name] = verses
            print(f"     ✓ {len(verses)} versículos extraídos")
        except Exception as e:
            print(f"     ✗ Error: {e}")
            results[section_name] = []
        print()
    return results

# -------------------------------
# Ejecución directa
# -------------------------------
if __name__ == "__main__":
    print("Seleccione una categoría para descargar:")
    print("1) Tanya (jumesh/tania)")
    print("2) Rambam - 1 capítulo")
    print("3) Rambam - 3 capítulos (default)")
    print("4) Sefer Hamitzvot y Hayom Yom")
    print("5) Todas las categorías")
    choice = input("Ingrese el número de opción (1-5) [3]: ").strip()
    if choice == "":
        choice = "3"
    if choice == "1":
        selected = ["Tanya"]
    elif choice == "2":
        selected = ["Rambam_1_Chapter"]
    elif choice == "3":
        selected = ["Rambam_3_Chapters"]
    elif choice == "4":
        selected = ["HayomYom"]
    else:
        selected = None  # Todas las secciones
    
    data = scrape_chabad_verses(sections=selected)
    
    print("=" * 50)
    print("Resumen de resultados:")
    print("=" * 50)
    for section, verses in data.items():
        print(f"{section}: {len(verses)} versículos")
        if verses:
            print(f"  Primer versículo: {verses[0][:50]}...")
    print()