import docx
import pandas as pd
import re
import unicodedata
import nltk
from nltk.stem import WordNetLemmatizer
import PyPDF2
from sklearn.metrics.pairwise import cosine_similarity

def get_pdf(path):
    with open(path, 'rb') as file:
        
        lector = PyPDF2.PdfReader(file)
        final_text = []
        for page_num in range(len(lector.pages)):
            page = lector.pages[page_num]
            text = page.extract_text()
            final_text.append(text)
        return " ".join(final_text)
    
def get_text_from_document(path):
    doc = docx.Document(path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)

    return " ".join(full_text)

def clean_text(text):
    normalized_text = unicodedata.normalize('NFKD', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', normalized_text)
    return text.lower()

def prepare_text(text):

    stopwords = nltk.corpus.stopwords.words('spanish')
    wordnet_lemmatizer = WordNetLemmatizer()
    text = clean_text(text)
    tokens = nltk.word_tokenize(text)
    tokens_sin_stopwords = [word for word in tokens if word not in stopwords]
    tokens_lematizados = [wordnet_lemmatizer.lemmatize(word, pos = "v") for word in tokens_sin_stopwords]
    return " ".join(tokens_lematizados)

def vectorize_text(vect, text):
    return vect.transform(text)

def prepare_matrix(jobs, colname):
    jobs[colname] = jobs[colname].apply(prepare_text)
    return jobs


def get_similarity(
        text_vectorized, 
        jobs_vectorized, 
        df_jobs, 
        n = 5
        ):
    similarities = cosine_similarity(text_vectorized, jobs_vectorized)
    top_similarities = pd.Series(similarities[0]).sort_values(ascending = False).head(n)
    indexes = top_similarities.index
    df = pd.DataFrame(df_jobs.iloc[indexes, 0])
    df["RANKING"] = top_similarities
    df = df.rename(columns = {"PUESTO":"JOBS"})
    df["JOBS"] = df["JOBS"].str.title()
    return df.reset_index(drop = True)
