import re


def parse_restrictie_limbaj_natural(propozitie: str):
    """
    Interpretează o propoziție care descrie o restricție de tipul:
      - "nu se fac ore luni dupa 12"
      - "fara cursuri joi dupa 14"
    Și o transformă într-un dicționar de tip constraint.
    """
    propozitie = propozitie.lower().strip()

    # Căutăm ziua
    zile_saptamana = ["luni", "marti", "miercuri", "joi", "vineri"]
    match_zi = re.search(r"\b(luni|marti|miercuri|joi|vineri)\b", propozitie)
    if match_zi:
        zi = match_zi.group(1)
        if zi == "marti":
            zi = "marți"  # Corectăm diacriticele
    else:
        return None  # Dacă nu există zi, ignorăm restricția

    # Căutăm "după <ora>"
    match_ora = re.search(r"după\s+(\d+)", propozitie)
    ora_start = int(match_ora.group(1)) if match_ora else None

    # Dacă avem zi și oră, construim restricția
    if any(cuv in propozitie for cuv in ["nu", "fără", "fara"]):
        return {
            "tip": "fără_valori",
            "descriere": propozitie,
            "detalii": {
                "zi": zi,
                "ora_start": ora_start
            }
        }

    return None


def parse_restrictii_din_fisier_text(nume_fisier: str):
    """
    Citește un fișier text linie cu linie,
    parsează fiecare linie cu parse_restrictie_limbaj_natural
    și returnează o listă de restricții (dicționare).
    """
    restrictii = []
    try:
        with open(nume_fisier, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                r = parse_restrictie_limbaj_natural(line)
                if r:
                    restrictii.append(r)
    except FileNotFoundError:
        print(f"Eroare: Fișierul {nume_fisier} nu a fost găsit.")
    except Exception as e:
        print(f"Eroare la citirea/parsingul fișierului {nume_fisier}: {e}")

    return restrictii
