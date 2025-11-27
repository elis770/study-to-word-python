# normalize_ref.py
import urllib.parse

def normalize_for_sefaria(daily_dict: dict) -> dict:
    """
    Recorre un diccionario de estudios diarios y normaliza las referencias
    para que puedan ser usadas en la API de Sefaria.

    Args:
        daily_dict (dict): Diccionario con referencias 'en' y 'he'.

    Returns:
        dict: Diccionario con referencias normalizadas en la clave 'en_normalized'.
    """
    normalized_dict = {}

    for key, refs in daily_dict.items():
        # Solo procesamos si refs es un diccionario
        if not isinstance(refs, dict) or 'en' not in refs:
            continue

        ref = refs['en']

        # Si es Rambam1 o Rambam3, agregamos 'Mishneh Torah, ' al inicio
        if key in ('Rambam1', 'Rambam3'):
            ref = f"Mishneh Torah, {ref}"

        # Reemplazar espacios por guiones bajos
        ref = ref.replace(" ", "_")

        # Codificar caracteres especiales (ej: :, ;)
        ref = urllib.parse.quote(ref, safe='_')  # dejamos _ sin codificar

        # Guardamos la referencia normalizada
        normalized_dict[key] = {
            **refs,
            'en_normalized': ref
        }

    return normalized_dict