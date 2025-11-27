import requests
import json

def get_text(daily_dict: dict) -> dict:
    all_texts = {}
    for study_type, refs in daily_dict.items():
        if not isinstance(refs, dict):
            continue

        en_ref = refs.get("en")
        if not en_ref:
            print(f"No se encontró referencia en inglés para '{study_type}'. Saltando.")
            continue

        print(f"Procesando: {study_type} ({en_ref})")
        all_texts[study_type] = {}

        url = f"https://www.sefaria.org/api/v3/texts/{en_ref}?context=0&multiple=1"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Buscamos versión hebrea primero
            he_version = next((v for v in data.get('versions', []) if v.get('language') == 'he'), None)
            
            if he_version:
                all_texts[study_type]['he_vtitle'] = he_version.get('versionTitle')
                all_texts[study_type]['he_text'] = he_version.get('text')
            else:
                # Si no hay hebreo, intentamos directamente el campo 'text' general
                text = data.get('text')
                if text:
                    all_texts[study_type]['text'] = text
                else:
                    print(f"No se encontró versión hebrea ni campo 'text' para {en_ref}.")

        except requests.exceptions.RequestException as e:
            print(f"Error al obtener el texto para {en_ref}: {e}")
            continue
        except json.JSONDecodeError:
            print(f"Error al decodificar el JSON para {en_ref}.")
            continue

    return all_texts