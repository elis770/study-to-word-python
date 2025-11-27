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
    'SeferHamitzvot': 'seferHamitzvos',
    'HayomYom': 'hayomyom'
}

SECTION_TYPE = {
    "Chumash": "tabla_hebrew",
    "Tehilim": "tabla_hebrew",
    "Tanya": "lang_he",
    "Rambam_1_Chapter": "lang_he",
    "Rambam_3_Chapters": "lang_he",
    "SeferHamitzvot": "lang_he",
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
    return f"https://www.chabad.org/dailystudy/{base_path}.asp?tdate={formatted_date}"

def scrape_single_url(url, section_name, section_type):
    """
    Scraping de una URL según tipo de sección
    """
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
            }} else if (section_type === "dir_rtl") {{
                document.querySelectorAll('div[dir="rtl"]').forEach(el => addText(el.innerText));
            }} else if (section_type === "lang_he") {{
                document.querySelectorAll('h2, span[lang="he"]').forEach(el => addText(el.innerText));
            }}

            return results;
        }}""")
        
        browser.close()
        return verses

# -------------------------------
# Función principal
# -------------------------------
def scrape_chabad_verses(date=None):
    """
    Extrae versículos de todas las secciones definidas
    """
    if date is None:
        date = datetime.today()
    formatted_date = date.strftime("%m/%d/%Y")
    
    print(f"📅 Fecha: {formatted_date}")
    results = {}
    
    for section_name in BASE_URLS.keys():
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
    data = scrape_chabad_verses()
    
    print("=" * 50)
    print("Resumen de resultados:")
    print("=" * 50)
    for section, verses in data.items():
        print(f"{section}: {len(verses)} versículos")
        if verses:
            print(f"  Primer versículo: {verses[0][:50]}...")
    print()