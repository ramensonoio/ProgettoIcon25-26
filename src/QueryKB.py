from swipl_bootstrap import configure_swipl

configure_swipl()

from pyswip import Prolog


def main():
    prolog = Prolog()
    print("Avvio del motore Prolog e caricamento della Knowledge Base...")
    prolog.consult('KB.pl')

    film_ids = []

    while True:
        try:
            menu = """
=== CINELOGIC: KNOWLEDGE BASE ===
1) Trova film in base alle tue preferenze
2) Trova la migliore piattaforma di streaming per i film trovati
3) Esci
Inserisci un valore (1-3): """
            choice = int(input(menu))

            if choice == 1:
                film_ids = query_filmstreaming(prolog)
            elif choice == 2:
                if film_ids:
                    find_best_streaming_platform(prolog, film_ids)
                else:
                    print("\nAttenzione: Esegui prima una ricerca di film (opzione 1).")
            elif choice == 3:
                print("\nUscita dal programma. A presto!")
                break
            else:
                print("\nErrore: Input non valido. Scegli 1, 2 o 3.")
        except ValueError:
            print("\nErrore: Devi inserire un numero intero.")


def query_filmstreaming(prolog):
    uscita = None
    genere = None
    durata = None
    film_ids = []

    # 1. Periodo
    while uscita is None:
        try:
            uscita_input = int(
                input("\nPeriodo di uscita:\n1) Recente (>2010)\n2) Tra 2000 e 2010\n3) Pre 2000\nScegli: "))
            mappa_uscita = {1: "recente", 2: "tra_2000_2010", 3: "pre_2000"}
            uscita = mappa_uscita.get(uscita_input)
            if not uscita: print("Input non valido.")
        except ValueError:
            print("Inserisci un numero.")

    # 2. Genere
    genres = ["western", "scifi", "romance", "drama", "horror", "thriller", "comedy", "crime",
              "documentation", "family", "action", "fantasy", "animation", "music", "history",
              "war", "european", "sport", "reality"]
    while genere is None:
        try:
            print("\nGeneri disponibili:")
            for i, g in enumerate(genres, 1):
                print(f"{i}) {g.capitalize()}")
            genere_input = int(input("Scegli il numero del genere: "))

            if 1 <= genere_input <= len(genres):
                genere = genres[genere_input - 1]
            else:
                print(f"Input non valido. Scegli tra 1 e {len(genres)}.")
        except ValueError:
            print("Inserisci un numero.")

    # 3. Durata
    while durata is None:
        try:
            durata_input = int(
                input("\nDurata:\n1) Breve (<60 min)\n2) Media (60-90 min)\n3) Lunga (>90 min)\nScegli: "))
            mappa_durata = {1: "breve", 2: "media", 3: "lunga"}
            durata = mappa_durata.get(durata_input)
            if not durata: print("Input non valido.")
        except ValueError:
            print("Inserisci un numero.")

    query = f"{uscita}_{genere}_{durata}(ID), title(ID, Titolo)"

    print("\nRicerca nella Knowledge Base in corso...")
    try:
        results = list(prolog.query(query))

        if not results:
            print("Nessun film trovato con questi filtri.")
        else:
            ids_set = set()
            print("\n=== FILM TROVATI ===")
            for soln in results:
                if soln["ID"] not in ids_set:
                    print(f"- {soln['Titolo'].title()} (ID: {soln['ID']})")
                    film_ids.append(soln["ID"])
                    ids_set.add(soln["ID"])
    except Exception as e:
        print(f"Errore Prolog: {e}")

    return film_ids


def find_best_streaming_platform(prolog, film_ids):
    price_filters = []

    # Selezione del prezzo
    while not price_filters:
        try:
            price_input = int(input("\nSeleziona il tuo budget per lo streaming:\n"
                                    "1) Economica (< 9.99)\n2) Media (fino a 9.99)\n3) Costosa (qualsiasi prezzo)\nScegli: "))
            if price_input == 1:
                price_filters = ["prezzo_economy"]
            elif price_input == 2:
                price_filters = ["prezzo_economy", "prezzo_medio"]
            elif price_input == 3:
                price_filters = ["prezzo_economy", "prezzo_medio", "prezzo_costoso"]
            else:
                print("Input non valido.")
        except ValueError:
            print("Inserisci un numero.")

    platform_count = {}

    print("\nAnalisi delle piattaforme in corso...")
    for film_id in film_ids:
        # Per ogni film, cerco su che piattaforma si trova
        query_piattaforma = f"streaming_service({film_id}, Piattaforma)"

        try:
            results = list(prolog.query(query_piattaforma))
            for result in results:
                piattaforma = result["Piattaforma"]

                # Controllo se il film rispetta almeno uno dei filtri di prezzo
                price_match = False
                for price_filter in price_filters:
                    check_query = f"{price_filter}({film_id})"
                    # Se la lista tornata non è vuota, il fatto è vero
                    if list(prolog.query(check_query)):
                        price_match = True
                        break

                if price_match:
                    platform_count[piattaforma] = platform_count.get(piattaforma, 0) + 1

        except Exception as e:
            print(f"Errore query per ID {film_id}: {e}")

    # Risultato finale
    if platform_count:
        best_platform = max(platform_count, key=platform_count.get)
        print("\n=== RISULTATO ===")
        print(f"La piattaforma più consigliata per te è: **{best_platform.upper()}**")
        print(
            f"Contiene {platform_count[best_platform]} dei film che hai cercato ad un prezzo compatibile col tuo budget.")
    else:
        print("\nNessuna piattaforma offre questi film al prezzo selezionato.")


if __name__ == "__main__":
    main()