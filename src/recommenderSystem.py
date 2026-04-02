import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.stats import pearsonr


def get_info():
    print("--- Ricerca Film ---")
    print("Inserisci i dati del film che ti interessa:\n")

    # .strip() rimuove spazi vuoti accidentali
    # .title() mette in automatico l'iniziale maiuscola a ogni parola
    title = input("Inserisci il titolo: ").strip().title()
    genre = input("Inserisci il genere (es. Action, Scifi): ").strip().title()

    # Per l'anno usiamo un blocco try-except per assicurarci che si inserisca un numero
    while True:
        try:
            year_input = input("Inserisci l'anno di uscita: ").strip()
            year = int(year_input)  # Converto in intero!
            break
        except ValueError:
            print("Errore: L'anno deve essere un numero intero (es. 2015). Riprova.")

    # Creiamo il dataframe temporaneo
    user_data = pd.DataFrame({
        'title': title,
        'genre': genre,
        'year': year
    }, index=[0])

    return user_data


from sklearn.metrics.pairwise import cosine_similarity


def construct_recommendation(filename, user_data):
    # Caricamento Dati
    movie_data = pd.read_csv(filename)
    colonne_utili = ['title', 'description', 'release_year', 'runtime', 'production_countries', 'imdb_score',
                     'tmdb_score', 'genre', 'streaming_service', 'actors']
    movie_data = movie_data[colonne_utili].copy()

    # Controllo se il film esiste
    user_title = user_data['title'].iloc[0]

    if user_title in movie_data['title'].values:
        # Trovo l'indice del film esistente
        target_index = movie_data.index[movie_data['title'] == user_title].tolist()[0]
    else:
        # Aggiungo il nuovo film IN CIMA (indice 0)
        movie_data = pd.concat([user_data, movie_data], ignore_index=True)
        target_index = 0

    # Creazione del contenuto testuale
    # Riempiamo i valori mancanti con una stringa vuota per non inquinare il testo
    colonne_testo = ['title', 'release_year', 'runtime', 'production_countries', 'genre']
    movie_data[colonne_testo] = movie_data[colonne_testo].fillna('')

    # Metodo per concatenare colonne
    movie_data['all_content'] = movie_data[colonne_testo].astype(str).agg(';'.join, axis=1)

    # Vettorizzazione
    tfidf_matrix = vectorize_data(movie_data)

    print("\nInizio calcolo delle similarità...")

    # Calcolo delle Similarità
    # Estraiamo il vettore del film target
    target_vector = tfidf_matrix[target_index]

    # cosine_similarity calcola istantaneamente la distanza tra il target e TUTTI gli altri
    # Restituisce un array di punteggi (da 0 a 1)
    similarities = cosine_similarity(target_vector, tfidf_matrix).flatten()

    # Estrazione dei Top 5
    # enumerate abbina l'indice di riga al punteggio: [(0, score), (1, score), ...]
    corr_list = list(enumerate(similarities))

    # Ordiniamo per punteggio (x[1]) decrescente.
    # Prendiamo [1:6] per saltare il primo risultato (il film stesso, score=1.0)
    sorted_corr = sorted(corr_list, key=lambda x: x[1], reverse=True)[1:6]

    # Estraiamo solo gli indici
    movie_index = [item[0] for item in sorted_corr]

    print(f"Movie_Index trovati: {movie_index}")
    print("\n[5 film più simili trovati con successo!]")
    print("Passaggio all'analisi del modello...")

    return movie_index


from sklearn.feature_extraction.text import TfidfVectorizer


def vectorize_data(movie_data):
    # Inizializzo
    vectorizer = TfidfVectorizer(
        analyzer='word',
        stop_words='english',  # Ignora "the", "a", "is", ecc.
        # Legge sia parole singole ("Action") che coppie ("Science Fiction")
        ngram_range=(1, 2)
    )

    # Addestro e trasformo il testo in matrice matematica
    tfidf_matrix = vectorizer.fit_transform(movie_data['all_content'])

    # Restituisco la matrice sparsa
    return tfidf_matrix


def get_recommendation():
    print("\n=== BENVENUTO NEL RECOMMENDER SYSTEM ===\n")
    print("Digita le caratteristiche del film \n su cui vuoi che si avvii la raccomandazione.")

    # Salvo il percorso in una variabile
    dataset_path = '../dataset/pre-processato/pre_processed_dataset.csv'

    while True:
        # 1. Chiedo i dati
        user_data = get_info()

        # 2. Li mostro all'utente
        print("\nQuesti sono i dati del film che hai inserito:")
        print(user_data)

        # 3. Chiedo conferma
        answer = input("\nÈ corretto? (y/n): ").strip().lower()

        # 4. Controllo la risposta
        if answer == 'y':
            print("\nPerfetto! Dati confermati.")
            break

        elif answer == 'n':
            print("\nNessun problema, reinseriamo i dati da capo.")

        else:
            print("\nRisposta non riconosciuta. Per favore, digita 'y' per confermare o 'n' per annullare.")

    print("\nRicerca delle raccomandazioni in corso... Attendi...")

    movie_index = construct_recommendation(dataset_path, user_data)

    print("\nEcco i Movie_Index trovati:\n", movie_index)

    return movie_index
