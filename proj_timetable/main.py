import time
import json
from data import pregateste_problema_csp
from constraints import este_valida, constrangeri_binare
from algorithm import ac3, backtracking
from data import pregateste_problema_csp
from natural_language import parse_restrictii_din_fisier_text

def salveaza_orar_in_fisier(solutie, params, nume_fisier="orar_final.txt"):
    """Salveaza orarul intr-un fisier text, sub forma tabelara."""
    if solutie is None:
        with open(nume_fisier, "w", encoding="utf-8") as f:
            f.write(" Nu s-a gasit nicio solutie valida pentru orar.\n")
        print(f" Nu s-a putut genera un orar valid! Verifica constrangerile.")
        return

    header = ["Ziua", "Ora", "Materie", "Tip", "Grupa", "Profesor", "Sala"]
    date = []

    # Ordonam pentru a afisa frumos
    orar_ordonat = sorted(
        solutie.items(),
        key=lambda x: (params['zile'].index(x[1][1]), int(x[1][2]))
    )

    for var, val in orar_ordonat:
        tip, materie, grupa = var
        sala, zi, ora, profesor = val
        date.append([zi, ora, materie, tip, grupa, profesor, sala])

    col_widths = [max(len(str(x)) for x in col) for col in zip(header, *date)]
    title_row = " | ".join(h.center(w) for h, w in zip(header, col_widths))
    separator = "-+-".join("-" * w for w in col_widths)

    with open(nume_fisier, "w", encoding="utf-8") as f:
        f.write(title_row + "\n")
        f.write(separator + "\n")
        for row in date:
            f.write(" | ".join(str(item).ljust(w) for item, w in zip(row, col_widths)) + "\n")

    print(f" Orarul a fost salvat corect in `{nume_fisier}`.")

def citeste_json(fisier):
    """Incarca un fisier JSON si returneazs datele sub forma de dictionar."""
    try:
        with open(fisier, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Eroare: Fisierul {fisier} nu a fost gasit.")
        return {}
    except json.JSONDecodeError:
        print(f"Eroare: Fisierul {fisier} nu este un JSON valid.")
        return {}
    except Exception as e:
        print(f"Eroare necunoscuta la citirea JSON-ului {fisier}: {e}")
        return {}

def citeste_din_prompt():
    """Citeste date de la utilizator pentru profesori, materii si ore."""
    profesori = {}
    materii = {}

    # Citire profesori
    nr_profesori = int(input("Cate cadre didactice doriti sa adaugati? "))
    for _ in range(nr_profesori):
        nume_profesor = input("Introduceti numele profesorului: ")
        zile_indisponibile = input("Introduceti zilele (ex: luni,marti) in care este indisponibil: ").split(',')
        ore_indisponibile = input("Introduceti orele (ex: 08,10) in care este indisponibil: ").split(',')
        max_ore_pe_zi = int(input(f"Introduceti numarul maxim de ore pe zi pentru {nume_profesor}: "))

        profesori[nume_profesor] = {
            "indisponibilitati": {
                "zile": [zi.strip() for zi in zile_indisponibile],
                "ore": [ora.strip() for ora in ore_indisponibile]
            },
            "max_ore_pe_zi": max_ore_pe_zi
        }

    # Citire materii
    nr_materii = int(input("Cate materii doriti sa adaugati? "))
    for _ in range(nr_materii):
        materie = input("Introduceti numele materiei: ")
        profesor = input(f"Introduceti profesorul pentru {materie}: ")
        grupe = input(f"Introduceti grupele pentru {materie} (separate prin virgula): ").split(',')
        materii[materie] = {"profesor": profesor, "grupe": [gr.strip() for gr in grupe]}

    # Citire ore si grupe globale
    grupe_globale = input("Introduceti grupele globale (ex: B1,B2) (separate prin virgula): ").split(',')
    ore_disponibile = input("Introduceti orele globale (ex: 08,10,12) (separate prin virgula): ").split(',')

    # Zilele saptamanii
    # Poti lasa default (luni,marti,miercuri,joi,vineri) sau ceri la user
    zile = ["luni", "marti", "miercuri", "joi", "vineri"]

    # Salile
    sali_curs = input("Introduceti salile de curs (ex: C101,C102) (separate prin virgula): ").split(',')
    sali_seminar = input("Introduceti salile de seminar (ex: S301,S302) (separate prin virgula): ").split(',')

    return {
        "profesori": profesori,
        "materii": materii,
        "grupe": [g.strip() for g in grupe_globale],
        "ore": [o.strip() for o in ore_disponibile],
        "zile": zile,
        "sali": {
            "curs": [s.strip() for s in sali_curs],
            "seminar": [s.strip() for s in sali_seminar]
        }
    }

def salveaza_instanta_combina(instanta_noua, nume_fisier="instanta1.json"):
    """Salveaza instanta combinata (veche si noua) intr-un fisier JSON."""
    try:
        # Incarca fisierul existent
        with open(nume_fisier, 'r', encoding='utf-8') as f:
            instanta_veche = json.load(f)

        # Combina datele existente cu cele noi
        instanta_combinate = instanta_veche

        # Adaugam datele din instanta_noua
        # Profesori
        for profesor, date in instanta_noua["profesori"].items():
            if profesor not in instanta_combinate["profesori"]:
                instanta_combinate["profesori"][profesor] = date
            else:
                # Actualizam profesori daca exista deja
                instanta_combinate["profesori"][profesor]["indisponibilitati"]["zile"].extend(
                    date["indisponibilitati"]["zile"])
                instanta_combinate["profesori"][profesor]["indisponibilitati"]["ore"].extend(
                    date["indisponibilitati"]["ore"])
                instanta_combinate["profesori"][profesor]["max_ore_pe_zi"] = max(
                    instanta_combinate["profesori"][profesor]["max_ore_pe_zi"], date["max_ore_pe_zi"])

        # Materii
        for materie, date in instanta_noua["materii"].items():
            if materie not in instanta_combinate["materii"]:
                instanta_combinate["materii"][materie] = date
            else:
                # Daca materia exista deja, adaugam grupele noi
                instanta_combinate["materii"][materie]["grupe"].extend(date["grupe"])

        # Grupe si ore
        instanta_combinate["grupe"].extend(instanta_noua["grupe"])
        instanta_combinate["ore"].extend(instanta_noua["ore"])

        # Salile si zilele
        instanta_combinate["sali"]["curs"].extend(instanta_noua["sali"]["curs"])
        instanta_combinate["sali"]["seminar"].extend(instanta_noua["sali"]["seminar"])
        instanta_combinate["zile"].extend(instanta_noua["zile"])

        # Salveaza instanta combinata in fisier
        with open(nume_fisier, 'w', encoding='utf-8') as f:
            json.dump(instanta_combinate, f, indent=4, ensure_ascii=False)

        print(f" Instanta combinata a fost salvata in fisierul `{nume_fisier}`.")

    except Exception as e:
        print(f"Eroare la salvarea instantei combinate: {e}")

def rezolva_orar():
    data = pregateste_problema_csp("instanta1.json")
    if not data:
        print(" Eroare: Nu s-a putut incarca instanta.")
        return

    asignari = {var: None for var in data["variabile"]}
    domenii = {var: set(dom) for var, dom in data["domenii"].items()}

    params = {
        'sali_curs': data["sali_curs"],
        'sali_seminar': data["sali_seminar"],
        'materii': data["materii"],
        'grupe': data["grupe"],
        'restrictii_profesori': data["restrictii_profesori"],
        'zile': data["zile"],
        'ore': data["ore"],
        'max_ore_pe_zi': 8,
        'este_valida': este_valida,
        'constrangeri_binare': constrangeri_binare
    }



    print("\n Testare Backtracking **cu** AC3")
    if ac3(domenii, constrangeri_binare, params):
        solutie_cu_ac3 = backtracking(asignari, domenii, params, utilizeaza_ac3=True)
        if solutie_cu_ac3:
            salveaza_orar_in_fisier(solutie_cu_ac3, params, "orar_cu_ac3.txt")
        else:
            print(" Nu s-a gasit nicio solutie **cu AC3**.")
    else:
        print(" AC3 a redus domeniile la valori imposibile. Nu exista solutie.")

def main():
    # ---------- 1) Citeste date noi de la tastatura ----------
    raspuns = input("Doriti sa adaugati date noi la fisierul instanta1.json? (da/nu): ")
    if raspuns.lower().startswith("d"):
        instanta_noua = citeste_din_prompt()
        # Combinam datele de la tastatura cu fisierul existent (instanta1.json)
        salveaza_instanta_combina(instanta_noua, "instanta1.json")

    # ---------- 2) Incarca instanta (acum modificata) ----------
    data = pregateste_problema_csp("instanta1.json")
    if not data:
        print(" Eroare: Nu s-a putut incarca instanta.")
        return

    # ---------- 3) Citeste restrictii limbaj natural ----------
    # (Ex. restrictii_natural.txt contine "Fara ore luni dupa 12" etc.)
    lista_restrictii_nlp = parse_restrictii_din_fisier_text("restrictii_natural.txt")
    print("\n Restrictii NLP incarcate:", lista_restrictii_nlp)

    # ---------- 4) Construim parametrii pentru backtracking ----------
    asignari = {var: None for var in data["variabile"]}
    domenii = {var: set(dom) for var, dom in data["domenii"].items()}
    params = {
        'sali_curs': data["sali_curs"],
        'sali_seminar': data["sali_seminar"],
        'materii': data["materii"],
        'grupe': data["grupe"],
        'restrictii_profesori': data["restrictii_profesori"],
        'zile': data["zile"],
        'ore': data["ore"],
        'max_ore_pe_zi': 8,
        'este_valida': este_valida,
        'constrangeri_binare': constrangeri_binare,
        # CHEIA: punem lista de restrictii NLP
        'lista_restrictii_nlp': lista_restrictii_nlp
    }


    # ---------- 6) Testare Backtracking (cu AC3) ----------
    print("\n Testare Backtracking **cu** AC3")
    from algorithm import ac3
    # Reinitializam domeniile
    asignari = {var: None for var in data["variabile"]}
    domenii = {var: set(dom) for var, dom in data["domenii"].items()}

    if ac3(domenii, constrangeri_binare, params):
        solutie_cu_ac3 = backtracking(asignari, domenii, params, utilizeaza_ac3=True)
        if solutie_cu_ac3:
            salveaza_orar_in_fisier(solutie_cu_ac3, params, "orar_cu_ac3.txt")
        else:
            print(" Nu s-a gasit nicio solutie **cu AC3**.")
    else:
        print(" AC3 a redus domeniile la valori imposibile. Nu exista solutie.")


if __name__ == "__main__":
    main()

