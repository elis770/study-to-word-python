# sefaria_api.py
import requests
from datetime import datetime

ORDERS_MAP = {
    1: "parasha",
    2: "haftara",
    3: "daf_yomi",
    4: "Tanakh",
    5: "Mishnah",
    6: "Rambam1",
    7: "Rambam3",
    8: "Talmud-week",
    9: "Shuljan Arukh",
    10: "Arukh HaShulchan Yomi",
    11: "Tanakh Yomi",
    12: "Chok LeYisrae",
    13: "?",
    14: "?",
    15: "Tanya",
    16: "Yerushalmi Yomi",
}

def get_sefaria_for_date(date: datetime) -> dict:
    """
    Llama a la API de Sefaria y devuelve los estudios para la fecha dada.
    """
    studies = {}
    loading = True

    try:
        day = date.day
        month = date.month
        year = date.year

        url = f"https://www.sefaria.org/api/calendars?day={day}&month={month}&year={year}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        for item in data.get("calendar_items", []):
            key = ORDERS_MAP.get(item.get("order"))
            if key:
                if item.get("order") == 15:  # ejemplo: Tanya
                    studies[key] = {"en": item.get("ref")}
                else:
                    studies[key] = item.get("displayValue")

    except Exception as e:
        print("Error al obtener datos de Sefaria:", e)
    finally:
        loading = False

    date_used = f"{year}-{month:02}-{day:02}"
    return {
        **studies,
        "loading": loading,
        "dateUsed": date_used
    }