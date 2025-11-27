"""
Módulo de Scraping Web
Responsabilidad única: Obtener datos de la página web usando Playwright
"""
from playwright.sync_api import sync_playwright
from datetime import datetime

# Diccionario de URLs con sus nombres de sección
# URLS = {
#     'Chumash': 'https://www.chabad.org/dailystudy/torahreading.asp?tdate={date}#lt=he',
# }
URLS = {
    'Chumash': 'https://www.chabad.org/dailystudy/torahreading.asp?tdate={date}#lt=he',
    # 'Tehilim': 'https://www.chabad.org/dailystudy/tehillim.asp?tdate={date}#lt=he',
    'Tanya': 'https://www.chabad.org/dailystudy/tanya.asp?tdate={date}&commentary=false#lt=he',
    'Rambam_1_Chapter': 'https://www.chabad.org/dailystudy/rambam.asp?rambamChapters=1&tdate={date}#lt=he',
    'Rambam_3_Chapters': 'https://www.chabad.org/dailystudy/rambam.asp?rambamChapters=3&tdate={date}#lt=he',
    'sefer_hamitzvot': 'https://www.chabad.org/dailystudy/seferHamitzvos.asp?tdate={date}&lang=heb',
    'hayom_yom': 'https://www.chabad.org/dailystudy/hayomyom.asp?tdate={date}',
}

def scrape_single_url(url, section_name):
    """
    Hace scraping de una sola URL
    
    Args:
        url (str): URL a scrapear
        section_name (str): Nombre de la sección
        
    Returns:
        list: Lista de versículos extraídos
    """
    print(f"  📄 Scraping {section_name}...")
    print(f"     🔗 {url}")
    
    with sync_playwright() as p:
        # Ignorar errores de HTTPS para evitar problemas de certificados
        browser = p.chromium.launch(headless=False, args=["--ignore-certificate-errors"])
        page = browser.new_page(ignore_https_errors=True)

        # Capturar logs del navegador (filtrando errores de red ruidosos)
        page.on("console", lambda msg: print(f"     🔍 [JS]: {msg.text}") if "Failed to load resource" not in msg.text else None)

        page.goto(url, wait_until="domcontentloaded")

        # Estrategia de selectores múltiples
        # 1. Tablas específicas (Chumash/Tehilim)
        # 2. div.hayom-yom-info
        # 3. span[lang="he"]
        # 4. Elementos con dir="rtl"
        
        verses = page.evaluate("""() => {
            const results = [];
            const seen = new Set();

            function addText(text) {
    const cleanText = text.trim();
    if (cleanText && !seen.has(cleanText)) {
        results.push(cleanText);
        seen.add(cleanText);
    }
}

// Definimos las clases permitidas
const clasesPermitidas = new Set(['co_VerseNum', 'co_VerseText', 'co_RashiTitle', 'co_RashiText']);

// 1. Buscar en tablas específicas (Chumash)
 if (results.length === 0){
    const tdsHebrew = document.querySelectorAll('td.hebrew');
    tdsHebrew.forEach((td) => {
        // Seleccionamos SOLO los <span> con una de las clases permitidas
        const spansValidos = Array.from(td.querySelectorAll('span')).filter(span => {
            const spanClasses = new Set(span.classList);
            return [...clasesPermitidas].some(clase => spanClasses.has(clase));
        });

        // Extraemos y unimos el texto de los spans válidos
        const spansText = spansValidos
            .map(span => span.innerText.trim())
            .filter(texto => texto !== '') // Opcional: eliminar spans con texto vacío
            .join(' ');

        if (spansText) {
            addText(spansText);
        } else {
            console.log("      ⚠️ Texto vacío / no válido");
        }
    });

    console.log("📦 Total acumulado en results tras Caso B:", results.length);
}


            // 2. Buscar en hayom-yom-info
             if (results.length === 0) {
            document.querySelectorAll('div.hayom-yom-info').forEach(el => addText(el.innerText));
            }
            // 3. Buscar spans con lang="he", rambam y tanya
            if (results.length === 0) {
            document.querySelectorAll('h2, span[lang="he"]').forEach(el => addText(el.innerText));
            }

            return results;
        }""")

        browser.close()
        return verses


def scrape_rambam_verses(date=None):
    """
    Extrae versículos en hebreo de múltiples páginas de Chabad.org
    
    Args:
        date (datetime): Objeto datetime con la fecha a consultar.
                        Si es None, usa la fecha de hoy.
        
    Returns:
        dict: Diccionario con los resultados organizados por sección
              Ejemplo: {
                  'Tanya': [...],
                  'Rambam_1_Chapter': [...],
                  'Rambam_3_Chapters': [...]
              }
    """
    # Si no se proporciona fecha, usar hoy
    if date is None:
        date = datetime.today()
    
    # Formatear fecha en formato MM/DD/YYYY para la URL
    formatted_date = date.strftime("%m/%d/%Y")
    
    print(f"📅 Fecha: {formatted_date}")
    print(f"🔍 Iniciando scraping de {len(URLS)} secciones...")
    print()
    
    results = {}
    
    # Iterar sobre cada URL
    for section_name, url_template in URLS.items():
        url = url_template.format(date=formatted_date)
        
        try:
            verses = scrape_single_url(url, section_name)
            results[section_name] = verses
            print(f"     ✓ {len(verses)} versículos extraídos")
        except Exception as e:
            print(f"     ✗ Error: {e}")
            results[section_name] = []
        
        print()
    
    return results


if __name__ == "__main__":
    print("🔍 Ejecutando scraper independientemente...")
    print("Usando la fecha de hoy...")
    print()
    
    data = scrape_rambam_verses()
    
    print("=" * 50)
    print("Resumen de resultados:")
    print("=" * 50)
    for section, verses in data.items():
        print(f"{section}: {len(verses)} versículos")
        if verses:
            print(f"  Primer versículo: {verses[0][:50]}...")
    print()