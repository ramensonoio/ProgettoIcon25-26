import pandas as pd
import numpy as np

from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, RandomizedSearchCV, RepeatedKFold

from recommenderSystem import get_recommendation
def tune_knn_model(hyperparameters, X_train, y_train, n_iterazioni=20):
    # Inizializzo il modello base
    knn = KNeighborsClassifier()

    # Imposto la validazione incrociata
    cv_fold = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)

    # Imposto la ricerca
    random_search = RandomizedSearchCV(
        estimator=knn,
        cv=cv_fold,
        param_distributions=hyperparameters,
        n_iter=n_iterazioni,  # Numero di combinazioni casuali da provare
        random_state=1  # Per riproducibilità
    )

    # Addestro la ricerca
    random_search.fit(X_train, y_train)

    # Estraggo il miglior modello trovato e lo restituisco
    best_knn = random_search.best_estimator_

    return best_knn

def evaluate_model(y_test, y_pred, pred_prob):
    # Stampo il report di classificazione
    print("Classification Report:\n")
    print(classification_report(y_test, y_pred, zero_division=0.0))

    # Calcolo il ROC AUC score
    roc_score = roc_auc_score(y_test, pred_prob, multi_class='ovr')

    # Stampo il risultato
    print(f"ROC Score: {roc_score:.4f}")  # Il .4f arrotonda a 4 cifre decimali

    return roc_score


def search_hyperparameters(X_train, y_train):
    # Definisco lo spazio degli iperparametri
    hyperparameters = {
        'n_neighbors': list(range(1, 30)),
        'weights': ['uniform', 'distance'],
        'metric': ['euclidean', 'manhattan', 'hamming']
    }

    # Inizializzo il modello base e la validazione incrociata
    knn = KNeighborsClassifier()
    cv_fold = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)

    # Imposto la Randomized Search
    random_search = RandomizedSearchCV(
        estimator=knn,
        cv=cv_fold,
        param_distributions=hyperparameters,
        n_iter=15,  # Proviamo 15 combinazioni diverse
        random_state=1  # Per riproducibilità
    )

    # Addestro la ricerca sui soli dati di training
    random_search.fit(X_train, y_train)

    # Estraggo e restituisco direttamente il modello vincitore
    return random_search.best_estimator_


def compare_and_select_best_model(X_train, X_test, y_train, y_test):

    print("\n--- COMPOSIZIONE MODELLO BASE ---")
    # Uso i parametri di default espliciti per chiarezza
    knn_base = KNeighborsClassifier(n_neighbors=5, weights='uniform')
    knn_base.fit(X_train, y_train)

    # Controllo visivo sui primi 5 elementi
    print(f"Predizioni primi 5 elementi: {knn_base.predict(X_test)[0:5]}")
    print(f"Valori effettivi:            {list(y_test[0:5])}")

    print("\nValutazione del modello Base:")
    y_pred_base = knn_base.predict(X_test)
    pred_prob_base = knn_base.predict_proba(X_test)
    evaluate_model(y_test, y_pred_base, pred_prob_base)

    print("\n--- RICERCA IPERPARAMETRI (RANDOMIZED SEARCH) ---")

    best_knn = search_hyperparameters(X_train, y_train)

    # Stampo i parametri vincenti estraendoli dal modello
    best_params = best_knn.get_params()
    print(f"Best Weights: {best_params['weights']}")
    print(f"Best Metric: {best_params['metric']}")
    print(f"Best n_neighbors: {best_params['n_neighbors']}")

    print("\nValutazione del modello Ottimizzato:")
    y_pred_best = best_knn.predict(X_test)
    pred_prob_best = best_knn.predict_proba(X_test)
    evaluate_model(y_test, y_pred_best, pred_prob_best)

    print("\nModello ottimizzato pronto. Ora possiamo procedere alla fase di recommendation...")

    return best_knn


def main_recommender():
    # Caricamento Dati
    movie_data = pd.read_csv('../dataset/pre-processato/pre_processed_dataset.csv')
    # creazione categoria star (media_voti)
    movie_data['media_voti'] = (movie_data['imdb_score'] + movie_data['tmdb_score']) / 2

    # pd.cut divide i dati in fasce. I bin sono i limiti: [0, 5, 7.5, 10]
    # labels sono i valori da assegnare a quelle fasce: [1, 2, 3]
    movie_data['star'] = pd.cut(
        movie_data['media_voti'],
        bins=[0, 5.0, 7.5, 10.0],
        labels=[1, 2, 3],
        include_lowest=True
    )

    # Preparazione Variabili
    features = ['runtime']

    x = movie_data[features].copy()
    y = movie_data['star'].astype(int).to_numpy()

    movie_index = get_recommendation()

    recommend_data = movie_data[['title', 'release_year', 'genre', 'streaming_service', 'star']].iloc[
        movie_index].copy()
    predict_data = movie_data[features].iloc[movie_index].copy()

    # Dividiamo il dataset in due parti, 80% destinato al training e 20% destinato al testing
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=1, stratify=y)

    # trasformiamo i dati per renderli adeguati
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    predict_data_scaled = scaler.transform(predict_data)

    # Addestramento
    knn_model = compare_and_select_best_model(X_train, X_test, y_train, y_test)

    # Previsione sui nuovi dati raccomandati
    star_prediction = knn_model.predict(predict_data_scaled)

    # Output
    pd.set_option('display.max_columns', None)

    recommend_data['star_prediction'] = star_prediction

    print("\nEcco una lista di 5 film più simili a quello indicato, con una predizione sulla categoria star:\n")
    print(recommend_data)
    print("\n")
