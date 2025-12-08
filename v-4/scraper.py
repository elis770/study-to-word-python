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
def build_url(section, date=None, lang="he"):
    """
    Genera la URL para una sección y fecha dadas.
    Maneja Rambam como caso especial según el número de capítulos.
    
    Args:
        section: Nombre de la sección
        date: Fecha para el scraping (None = hoy)
        lang: 'he' para hebreo, 'en' para inglés, 'both' para ambos
    """
    if date is None:
        date = datetime.today()
    formatted_date = date.strftime("%m/%d/%Y")
    
    # Determinar el fragmento de idioma
    if lang == "en":
        lang_fragment = "primary"
    elif lang == "both":
        lang_fragment = "both"
    else:
        lang_fragment = "he"
    
    # Manejar RAMBAM primero (antes de validar base_path)
    if section in ["Rambam_1_Chapter", "Rambam_3_Chapters"]:
        chapters = "1" if section == "Rambam_1_Chapter" else "3"
        return f"https://www.chabad.org/dailystudy/rambam.asp?rambamChapters={chapters}&tdate={formatted_date}#lt={lang_fragment}"
    
    # Para otras secciones, validar y usar base_path
    base_path = BASE_URLS.get(section)
    if not base_path:
        raise ValueError(f"Sección desconocida: {section}")
    
    return f"https://www.chabad.org/dailystudy/{base_path}.asp?tdate={formatted_date}#lt={lang_fragment}"


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

                // --- Normalización de casos especiales ---
                if (cleanText.includes("\\n")) {{
                    const [first, ...rest] = cleanText.split("\\n").map(s => s.trim()).filter(Boolean);

                    // Primera parte = título corto (1–3 letras hebreas)
                    if (first && first.length >= 1 && first.length <= 3 && rest.length > 0) {{
                        const rejoined = rest.join(" ");
                        const finalLine = `${{first}}. ${{rejoined}}`.trim();

                        results.push(finalLine);
                        seen.add(finalLine);

                        return; 
                    }}
                }}

                // Valor normal
                results.push(cleanText);
                seen.add(cleanText);
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
                document.querySelectorAll('div.hayom-yom-container').forEach(el => addText(el.innerText));
            }} else if (section_type === "rambam") {{
                document.querySelectorAll('h2, span[lang="he"]').forEach(el => addText(el.innerText));
            }} else if (section_type === "tanya") {{
                document.querySelectorAll('h2, span[lang="he"]').forEach(el => addText(el.innerText));
            }}

            return results;
        }}""")

        browser.close()
        return verses


def scrape_chabad_verses(date=None, sections=None, lang="he"):
    """
    Extrae versículos de las secciones especificadas
    
    Args:
        date: Fecha para el scraping (None = hoy)
        sections: Lista de secciones a scrapear (None = todas)
        lang: 'he' para hebreo, 'en' para inglés, 'both' para ambos
    """
    if date is None:
        date = datetime.today()
    formatted_date = date.strftime("%m/%d/%Y")
    
    if lang == "both":
        lang_display = "Ambos (Hebreo e Inglés)"
    elif lang == "en":
        lang_display = "Inglés"
    else:
        lang_display = "Hebreo"
    
    print(f"📅 Fecha: {formatted_date} | Idioma del contenido: {lang_display}")
    
    # Si no se especifican secciones, usar todas
    if sections is None:
        sections_to_scrape = list(BASE_URLS.keys())
    else:
        sections_to_scrape = sections
    
    results = {}

    for section_name in sections_to_scrape:
        section_type = SECTION_TYPE.get(section_name, "lang_he")
        url = build_url(section_name, date, lang)

        try:
            verses = scrape_single_url(url, section_name, section_type)
            results[section_name] = verses
            print(f"     ✓ {len(verses)} versículos extraídos")
        except Exception as e:
            print(f"     ✗ Error: {e}")
            results[section_name] = []

        print()

    return results