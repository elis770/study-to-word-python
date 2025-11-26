# main.py
from detectar_dia import parse_date
from sefaria_api import get_sefaria_for_date

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

    print(f"\nEstudios de Sefaria para {result['dateUsed']}:")
    for k, v in result.items():
        if k not in ["loading", "dateUsed"]:
            print(f"- {k}: {v}")