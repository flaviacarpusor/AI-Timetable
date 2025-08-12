import json
from natural_language import parse_restrictii_din_fisier_text

def incarca_restrictii_nlp(fisier_text):
    """Optional, daca vrei sa le incarci tot din data.py."""
    return parse_restrictii_din_fisier_text(fisier_text)

def citeste_json(fisier):
    """Incarca un fisier JSON si returneaza datele sub forma de dictionar."""
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


def pregateste_problema_csp(fisier_json):
    data = citeste_json(fisier_json)
    if not data:
        return None

    tipuri = ["curs", "seminar"]
    materii_dict = data["materii"]
    grupe = data["grupe"]
    zile = data["zile"]
    ore = data["ore"]
    sali_curs = data["sali"]["curs"]
    sali_seminar = data["sali"]["seminar"]
    profesori = data["profesori"]

    # Generam variabile
    variabile = []

    def obtine_serie_din_grupa(g):
        """
        Returneaza litera seriei pe baza numelui grupei.
        De ex. 'A1' -> 'A', 'B3' -> 'B'.
        """
        return g[0]  # presupunem ca numele e A1, B2 etc. si prima litera e seria

    for materie, info_materie in materii_dict.items():
        grupe_materie = info_materie["grupe"]

        # Aflam toate seriile din grupele materiei
        # De exemplu, daca grupe_materie = ["A1", "A2"], serii = {"A"}.
        # Daca sunt ["B1","B3"], serii = {"B"}.
        serii = set(obtine_serie_din_grupa(g) for g in grupe_materie if g)

        # 1) Cream câte o variabila de curs pentru fiecare serie
        for serie in serii:
            variabile.append(("curs", materie, serie))

        # 2) Cream câte o variabila de seminar pentru fiecare grupa
        for grupa in grupe_materie:
            variabile.append(("seminar", materie, grupa))

    # Domenii...
    domenii = {}
    for var in variabile:
        tip, materie, grupa = var
        profesor = materii_dict[materie]["profesor"]
        sali_posibile = sali_curs if tip == "curs" else sali_seminar
        domenii[var] = {
            (sala, zi, ora, profesor)
            for sala in sali_posibile
            for zi in zile
            for ora in ore
        }

    return {
        "tipuri": tipuri,
        "materii": materii_dict,    # DICT, nu list
        "grupe": grupe,
        "zile": zile,
        "ore": ore,
        "sali_curs": sali_curs,
        "sali_seminar": sali_seminar,
        "profesori": profesori,
        "variabile": variabile,
        "domenii": domenii,
        "restrictii_profesori": profesori
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
