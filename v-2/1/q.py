from playwright.sync_api import sync_playwright

URL = "https://www.chabad.fm/157/"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(URL, wait_until="domcontentloaded")

        # Evalúa los elementos de la misma forma que JS
        j = page.eval_on_selector_all(
            "main",
            """(elements) => elements.map(el => {
                const title = el.querySelector("p")?.innerText || null;
                const text = el.querySelector("div.PageView")?.innerText || null;
                return { title, text };
            })"""
        )

        browser.close()
        return j


if __name__ == "__main__":
    print("Iniciando scraping...")
    data = run()
    print("Datos extraídos:", data)
