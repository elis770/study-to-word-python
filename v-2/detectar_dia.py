# detectar_dia.py
from datetime import datetime, timedelta
from convertdate import hebrew

KEYWORDS = {"hoy": 0, "ayer": -1, "anteayer": -2, "mañana": 1, "pasado": 2}

def parse_date(input_str: str = "") -> datetime:
    """
    Convierte un string en datetime gregoriano.
    Acepta:
      - "" o None -> hoy
      - Palabras clave: 'hoy', 'ayer', 'anteayer', 'mañana', 'pasado'
      - Fecha gregoriana YYYY-MM-DD
      - Fecha hebrea numérica AAAA-MM-DD (año>5000)
    """
    today = datetime.today()
    if not input_str:
        return today

    input_str = input_str.strip().lower()

    # Palabras clave
    if input_str in KEYWORDS:
        return today + timedelta(days=KEYWORDS[input_str])

    # Intentar YYYY-MM-DD
    try:
        parts = input_str.split("-")
        if len(parts) == 3:
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])

            if year > 5000:
                # Fecha hebrea -> convertir a gregoriano
                g_year, g_month, g_day = hebrew.to_gregorian(year, month, day)
                return datetime(g_year, g_month, g_day)
            else:
                # Fecha gregoriana
                return datetime(year, month, day)
    except Exception:
        pass

    # Si falla, usar hoy
    return today