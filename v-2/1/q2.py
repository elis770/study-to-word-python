from playwright.sync_api import sync_playwright

URL = 'https://www.chabad.org/dailystudy/rambam.asp?rambamChapters=3&tdate=11/26/2025#lt=he'

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(URL, wait_until="domcontentloaded")

        # Extraer solo span[lang="he"]
        verses = page.eval_on_selector_all(
            'div.co_body.article-body.cf div.verse-wrapper.linear',
            """(nodes) => {
                return nodes.map((node) => {
                    // seleccionar SOLO spans con lang="he"
                    const spans = [...node.querySelectorAll('span[lang="he"]')];
                    return spans.map(s => s.innerText.trim()).join(' ');
                });
            }"""
        )

        browser.close()
        return verses


if __name__ == "__main__":
    print("Iniciando scraping...")
    data = run()
    print("Versículos extraídos:\n", data)
