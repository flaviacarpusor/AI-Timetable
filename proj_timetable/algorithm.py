from constraints import constrangeri_binare

noduri_explorate = 0
backtrack_count = 0

def ac3(domenii, constrangeri_binare, params):
    """Aplica Algoritmul AC3 pentru a reduce domeniile variabilelor."""
    print("\n Aplicare AC3...")

    for var, domeniu in domenii.items():
        domenii[var] = {valoare for valoare in domeniu if params['este_valida'](var, valoare, {}, params)}

    print("\n Domenii dupa eliminarea constrangerilor unare:")
    for var, dom in domenii.items():
        print(f"{var}: {len(dom)} valori")

    queue = [(xi, xj) for xi in domenii for xj in domenii if xi != xj]
    while queue:
        xi, xj = queue.pop(0)
        if revise(domenii, xi, xj, constrangeri_binare, params):
            if not domenii[xi]:
                print(f" Domeniul lui {xi} a devenit vid.")
                return False
            for xk in (set(domenii.keys()) - {xi, xj}):
                queue.append((xk, xi))
    return True

def revise(domenii, xi, xj, constrangeri_binare, params):
    """Reduce domeniul unei variabile daca este inconsistent cu o alta variabila."""
    revised = False
    for x in set(domenii[xi]):
        if not any(constrangeri_binare(xi, x, xj, y, params) for y in domenii[xj]):
            print(f" AC3 elimina {x} din domeniul lui {xi} (nu e compatibil cu {xj})")
            domenii[xi].remove(x)
            revised = True
    return revised

def backtracking(asignari, domenii, params, utilizeaza_ac3=False):
    """Algoritmul Backtracking pentru cautarea unei solutii CSP."""
    global noduri_explorate, backtrack_count

    if all(asignari[var] is not None for var in asignari):
        return asignari

    # Alegem variabila neasignata cu domeniul cel mai mic (MRV - Minimum Remaining Values)
    variabila_neasignata = min(
        (var for var in asignari if asignari[var] is None),
        key=lambda var: len(domenii[var])
    )

    #  Daca nu mai avem valori posibile, revenim (evitam recursivitatea infinita)
    if len(domenii[variabila_neasignata]) == 0:
        return None

    print(f"\n Se incearca asignarea pentru {variabila_neasignata} ({len(domenii[variabila_neasignata])} valori disponibile)")

    # Ordonam valorile folosind Least Constraining Value (LCV)
    valori_ordonate = sortare_lcv(variabila_neasignata, domenii[variabila_neasignata], asignari, domenii, params)

    for valoare in valori_ordonate:
        if not params['este_valida'](variabila_neasignata, valoare, asignari, params):
            continue

        # Verificam consistenta binara
        consistent = True
        if not utilizeaza_ac3:
            for alta_variabila, alta_valoare in asignari.items():
                if alta_valoare is not None:
                    if not constrangeri_binare(variabila_neasignata, valoare, alta_variabila, alta_valoare, params):
                        consistent = False
                        break
        if not consistent:
            continue

        # Asignam valoarea
        asignari[variabila_neasignata] = valoare
        domenii_copie = {var: set(dom) for var, dom in domenii.items()}
        domenii[variabila_neasignata] = {valoare}

        noduri_explorate += 1

        # Aplicam AC3 daca este activat
        if utilizeaza_ac3:
            if not ac3(domenii, constrangeri_binare, params):
                domenii = domenii_copie
                asignari[variabila_neasignata] = None
                backtrack_count += 1
                continue

        # Apelam recursiv backtracking
        rezultat = backtracking(asignari, domenii, params, utilizeaza_ac3)

        if rezultat is not None:
            return rezultat

        # Restauram domeniile si incercam alta valoare
        domenii = domenii_copie
        asignari[variabila_neasignata] = None
        backtrack_count += 1

    return None

def sortare_lcv(variabila, valori, asignari, domenii, params):
    """Sorteaza valorile in functie de cat de mult reduc domeniul celorlalte variabile."""

    def constrangeri_impuse(valoare):
        count = 0
        for alta_variabila in domenii:
            if asignari[alta_variabila] is None and alta_variabila != variabila:
                for alta_valoare in domenii[alta_variabila]:
                    if not params.get('constrangeri_binare', lambda *args: True)(variabila, valoare, alta_variabila, alta_valoare, params):
                        count += 1
        return count

    return sorted(valori, key=constrangeri_impuse)
