def verifica_restrictii_nlp(zi, ora, lista_restrictii):
    """
    Verifica daca (zi, ora) respecta restrictiile de tip "fara_valori".
    Returneaza False daca exista conflict, True altfel.
    """
    for r in lista_restrictii:
        if r["tip"] == "fara_valori":
            if r["detalii"]["zi"] == zi:
                ora_start = r["detalii"]["ora_start"]
                if ora_start is not None and int(ora) > ora_start:
                    return False  # Conflict: ora este dupa ora restrictionata
    return True


def este_valida(variabila, valoare, asignari, params):
    tip, materie, grupa = variabila
    sala, zi, ora, profesor = valoare

    print(f"🔍 Testam {variabila} -> {valoare}")

    #  Verificam daca sala este potrivita pentru tipul evenimentului
    if tip == 'curs' and sala not in params['sali_curs']:
        print(f" Eliminat {valoare}: Sala {sala} nu este pentru cursuri")
        return False
    if tip == 'seminar' and sala not in params['sali_seminar']:
        print(f" Eliminat {valoare}: Sala {sala} nu este pentru seminarii")
        return False

    #  Profesorul nu poate preda in zile si ore indisponibile
    indisponibilitati = params['restrictii_profesori'].get(profesor, {}).get('indisponibilitati', {})
    if zi in indisponibilitati.get('zile', []) and ora in indisponibilitati.get('ore', []):
        print(f" Eliminat {valoare}: Profesorul {profesor} indisponibil {zi} la ora {ora}")
        return False

    #  Profesorul nu poate depasi numarul maxim de ore pe zi
    ore_profesor = [val[2] for var, val in asignari.items() if val and val[3] == profesor and val[1] == zi]
    if len(ore_profesor) >= params['max_ore_pe_zi']:
        print(f" Eliminat {valoare}: Profesorul {profesor} depaseste {params['max_ore_pe_zi']} ore pe zi")
        return False

    #  Un singur curs per materie, comun pentru toate grupele care incep cu "B"
    if tip == "curs":
        prefix_grupa = "".join([c for c in grupa if not c.isdigit()])
        cursuri_existente = {var for var, val in asignari.items()
                             if val and var[1] == materie and var[0] == "curs" and
                             "".join([c for c in var[2] if not c.isdigit()]) == prefix_grupa}
        if len(cursuri_existente) > 0:
            print(f" Eliminat {valoare}: Exista deja un curs pentru {materie} seria {prefix_grupa}")
            return False

    # Restrictii NLP (Natural Language Processing)
    if "lista_restrictii_nlp" in params:
        if not verifica_restrictii_nlp(zi, ora, params["lista_restrictii_nlp"]):
            print(f" Eliminat {valoare}: Restrictie NLP pentru ziua {zi} si ora {ora}")
            return False

    print(f" Acceptat {valoare}")
    return True



def expand_group(g):
    """
    Daca 'g' este o serie, intoarcem lista completa de subgrupe (A1, A2 etc.).
    Altfel, intoarcem direct grupa.
    """
    if g == "B":
        return ["B1","B2","B3"]
    elif g == "A":
        # Pune aici exact subgrupele pe care le folosesti in date
        # Daca e "A1", "A2", "A4", pune toate subgrupele reale
        return ["A1","A2","A4"]

    else:
        # Daca nu e serie, e deja o grupa concreta (ex. 'B2' sau 'A2')
        return [g]


def constrangeri_binare(xi, valoare_xi, xj, valoare_xj, params):
    if xi == xj:
        return True

    tip_xi, materie_xi, grupa_xi = xi
    tip_xj, materie_xj, grupa_xj = xj
    sala_xi, zi_xi, ora_xi, profesor_xi = valoare_xi
    sala_xj, zi_xj, ora_xj, profesor_xj = valoare_xj

    # Extindem grupele
    grup_xi = expand_group(grupa_xi)  # lista
    grup_xj = expand_group(grupa_xj)  # lista

    # 1) Grupa (extinsa) nu poate avea doua evenimente in acelasi timp
    # Adica daca exista vreo subgrupa comuna, e conflict
    if set(grup_xi).intersection(grup_xj) and zi_xi == zi_xj and ora_xi == ora_xj:
        return False

    # 2) Profesorul nu poate preda doua evenimente in acelasi timp
    if profesor_xi == profesor_xj and zi_xi == zi_xj and ora_xi == ora_xj:
        return False

    # 3) Sala nu poate gazdui doua evenimente in acelasi timp
    if sala_xi == sala_xj and zi_xi == zi_xj and ora_xi == ora_xj:
        return False

    return True
