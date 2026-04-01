from owlready2 import *


def main_ontology():
    print("\n=== BENVENUTO NELL'ONTOLOGIA DI CINELOGIC ===")

    print("Caricamento ontologia in corso... Attendi...")
    ontology_path = 'Ontologia.owx'
    ontology = get_ontology(ontology_path).load()
    print("Ontologia caricata con successo!")

    # Menu principale
    while True:
        menu_text = """
Seleziona un'operazione:
1) Visualizzazione Classi
2) Visualizzazione Proprietà d'Oggetto
3) Visualizzazione Proprietà dei Dati
4) Esegui query specifiche
5) Esci dall'Ontologia
"""
        print(menu_text)
        menu_answer = input("Inserisci un valore (1-5): ").strip()

        if menu_answer == '1':
            print("\n--- CLASSI PRESENTI NELL'ONTOLOGIA ---")
            for item in ontology.classes():
                print(f"- {item}")

            # Sottomenu esplorazione classi
            while True:
                class_menu = """
Vorresti esplorare le istanze di una delle seguenti classi?
1) Film
2) Release_year
3) Streaming_service
4) Genre
5) Customer
6) Film_production_studios
7) Torna al menu principale
"""
                print(class_menu)
                class_answer = input("Inserisci un valore (1-7): ").strip()

                if class_answer == '1':
                    print("\nLISTA FILM PRESENTI:")
                    for item in ontology.search(is_a=ontology.Film): print(f"- {item}")
                elif class_answer == '2':
                    print("\nLISTA ANNI DI RILASCIO PRESENTI:")
                    for item in ontology.search(is_a=ontology.Release_year): print(f"- {item}")
                elif class_answer == '3':
                    print("\nLISTA DEI SERVIZI DI STREAMING PRESENTI:")
                    for item in ontology.search(is_a=ontology.Streaming_Service): print(f"- {item}")
                elif class_answer == '4':
                    print("\nLISTA DEI GENERI PRESENTI:")
                    for item in ontology.search(is_a=ontology.Genre): print(f"- {item}")
                elif class_answer == '5':
                    print("\nLISTA DEI CLIENTI PRESENTI:")
                    for item in ontology.search(is_a=ontology.Customer): print(f"- {item}")
                elif class_answer == '6':
                    print("\nLISTA DEGLI STUDI DI PRODUZIONE PRESENTI:")
                    for item in ontology.search(is_a=ontology.Film_production_studios): print(f"- {item}")
                elif class_answer == '7':
                    print("Ritorno al menu principale...")
                    break  # Esce solo dal sottomenu delle classi
                else:
                    print("Valore non valido! Inseriscine uno tra quelli presenti.")

        elif menu_answer == '2':
            print("\n--- PROPRIETÁ D'OGGETTO PRESENTI ---")
            for item in ontology.object_properties():
                print(f"- {item}")

        elif menu_answer == '3':
            print("\n--- PROPRIETÁ DEI DATI PRESENTI ---")
            for item in ontology.data_properties():
                print(f"- {item}")

        elif menu_answer == '4':
            while True:
                query_menu = """
Scegli una query da eseguire:
1) Lista film presenti su 'Amazon'
2) Lista film di genere 'Sci-Fi'
3) Studi di produzione del film 'Deep Water'
4) Torna al menu principale
"""
                print(query_menu)
                query_choice = input("Inserisci un valore (1-4): ").strip()

                if query_choice == '1':
                    print("\nFILM PRESENTI SU AMAZON:")
                    amazon_films = ontology.search(is_a=ontology.Film,
                                                   is_distribuited_by=ontology.search(is_a=ontology.Amazon))
                    for item in amazon_films: print(f"- {item}")

                elif query_choice == '2':
                    print("\nFILM DI GENERE SCI-FI:")
                    scifi_films = ontology.search(is_a=ontology.Film, has_genre=ontology.search(is_a=ontology.scifi))
                    for item in scifi_films: print(f"- {item}")

                elif query_choice == '3':
                    deep_water = ontology.search_one(is_a=ontology.Film, is_distribuited_by=ontology.Hulu)
                    if deep_water:
                        production_studios = ontology.search(realize=deep_water)
                        if production_studios:
                            print(f"\nSTUDI DI PRODUZIONE DEL FILM '{deep_water}':")
                            for studio in production_studios:
                                print(f"- {studio}")
                        else:
                            print(f"Nessuno studio trovato nell'ontologia per il film '{deep_water}'.")
                    else:
                        print("Errore: Impossibile trovare il film associato a Hulu nell'ontologia.")

                elif query_choice == '4':
                    break  # Ritorna al menu principale
                else:
                    print("Scelta non valida.")

        elif menu_answer == '5':
            print("\nUscita dall'Ontologia in corso...")
            break  # Esce dal programma (o torna al main principale)

        else:
            print("\nValore non valido! Digita un numero da 1 a 5.")


if __name__ == "__main__":
    main_ontology()