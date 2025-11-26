# download_mishneh_torah_books.py
import requests, urllib.parse, json, os, time, re

INDEX_URL = "https://www.sefaria.org/api/v2/index/Mishneh_Torah"
TEXTS_BASE = "https://www.sefaria.org/api/v3/texts/"
OUT_DIR = "mishneh_books"
os.makedirs(OUT_DIR, exist_ok=True)

def fetch_json(url):
    r = requests.get(url, headers={"Accept":"application/json"})
    r.raise_for_status()
    return r.json()

index = fetch_json(INDEX_URL)
# index['schema'] contains the tree (SchemaNodes and JaggedArrayNodes)
schema = index.get("schema", {})

def collect_book_titles(node):
    """
    Recursively find leaf jagged nodes that represent books (titles).
    We return the English primary title when available.
    """
    titles = []
    # Some nodes have 'nodes' (SchemaNode) while leaf nodes have no 'nodes'
    if 'nodes' in node and node['nodes']:
        for child in node['nodes']:
            titles.extend(collect_book_titles(child))
    else:
        # This is a leaf; read its titles array
        t = node.get("titles") or node.get("heTitles") or []
        if isinstance(t, list) and len(t) > 0:
            # try to grab English text if present
            # titles items often look like: {"lang":"en","text":"Repentance","primary":True}
            found = None
            for item in t:
                if isinstance(item, dict) and item.get('lang') in ('en','eng','en'):
                    found = item.get('text')
                    break
            if not found:
                # fallback to first title's text
                first = t[0]
                if isinstance(first, dict):
                    found = first.get('text')
                else:
                    found = str(first)
            if found:
                titles.append(found)
    return titles

book_titles = collect_book_titles(schema)
book_titles = list(dict.fromkeys(book_titles))  # unique, preserve order
print("Found books:", len(book_titles), book_titles)

def safe_filename(s):
    return re.sub(r'[^\w\-_\. ]', '_', s).strip()

for i, book in enumerate(book_titles, 1):
    tref = f"Mishneh Torah, {book}"
    url = TEXTS_BASE  +  urllib.parse.quote(tref, safe='')
    print(f"[{i}/{len(book_titles)}] Fetching {tref} ...")
    try:
        data = fetch_json(url)
        fname = f"{i:02d}_{safe_filename(book)}.json"
        with open(os.path.join(OUT_DIR, fname), "w", encoding="utf-8") as out:
            json.dump(data, out, ensure_ascii=False, indent=2)
        print(" saved ->", fname)
    except Exception as e:
        print(" ERROR:", e)
    time.sleep(1.0)  # be polite and avoid hammering the API
