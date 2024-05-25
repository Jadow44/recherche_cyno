import pandas as pd
import spacy
from Conf.config import API_KEY, QUERIES, NUM_RESULTS
from Conf.utils import update_proxies_if_needed
from Conf.data_collection import collect_data
from Conf.data_processing import clean_data, preprocess_data, label_data
from Conf.data_classification import classify_texts

def main():
    update_proxies_if_needed()
    all_articles = collect_data(QUERIES, NUM_RESULTS, API_KEY)
    df = pd.DataFrame(all_articles)
    df.to_csv('bibliothèque_cyno/data/raw/all_articles.csv', index=False)
    
    df = clean_data(df)
    df.to_csv('bibliothèque_cyno/data/cleaned/cleaned_articles.csv', index=False)

    nlp = spacy.load('en_core_web_sm')
    df = preprocess_data(df, nlp)
    df.to_csv('bibliothèque_cyno/data/processed/processed_articles.csv', index=False)

    df = label_data(df)
    df.to_csv('bibliothèque_cyno/data/labeled/labeled_articles.csv', index=False)

    classify_texts(df)

if __name__ == '__main__':
    main()
