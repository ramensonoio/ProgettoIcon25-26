import QueryKB
import mainOntology
import classification_validation


def main():
    print("==== Benvenuti in CineLogic ====")

    # Uso una stringa multilinea per il menu: è molto più facile da leggere e modificare!
    menu_text = """
Seleziona un'operazione:
1) Recommender System
2) Interagisci con la KB
3) Interagisci con l'ontologia
4) Esci
"""

    while True:
        print(menu_text)
        choice = input(
            "Inserisci un valore (1-4): ").strip()  # rimuove eventuali spazi vuoti digitati per sbaglio

        if choice == '1':
            print("\n--- Avvio Recommender System ---")
            classification_validation.main_recommender()

        elif choice == '2':
            print('\n--- Caricamento della KB... Attendi... ---')
            QueryKB.main()

        elif choice == '3':
            print('\n--- Avvio Ontologia ---')
            mainOntology.main_ontology()

        elif choice == '4':
            print('\nUscita in corso... Arrivederci!')
            break  # Esce dal ciclo while

        else:
            print('\nErrore: Valore non valido! Digita 1, 2, 3 o 4.')


# Punto di ingresso standard di Python
if __name__ == "__main__":
    main()