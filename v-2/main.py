# main.py
from detectar_dia import parse_date
from sefaria_api import get_sefaria_for_date
from s import normalize_for_sefaria
from texto import get_text
import json

if __name__ == "__main__":
    print("Bienvenido al consultor de estudios de Sefaria.")
    print("Ingrese la fecha a consultar:")
    print("  - Fecha gregoriana (YYYY-MM-DD)")
    print("  - Fecha hebrea numérica (AAAA-MM-DD, año>5000)")
    print("  - Palabras clave: hoy, ayer, anteayer, mañana, pasado")
    print("Deje vacío para usar la fecha de hoy.")

    user_input = input("Fecha: ").strip()
    date_obj = parse_date(user_input)
    result = get_sefaria_for_date(date_obj)

    print(result)
    # print(type(result))
    # print(f"\nEstudios de Sefaria para {result['dateUsed']}:")
    # for k, v in result.items():
    #     if k not in ["loading", "dateUsed"]:
    #         print(f"- {k}: {v}")

    # print("procesando archivo word")

    x = normalize_for_sefaria(result)
       # Guardar el resultado en el archivo salida.txt
    with open("salida1.txt", "w", encoding="utf-8") as f:
        json.dump(x, f, ensure_ascii=False, indent=4)

    s = get_text(x)
    
    # Guardar el resultado en el archivo salida.txt
    with open("salida2.txt", "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=4)