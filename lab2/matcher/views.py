from django.shortcuts import render, redirect
from .forms import DocumentForm
from .models import Document
from transformer import *
import pandas as pd
import pickle

# Create your views here.

def index(request):
    return render(request, 'index.html')

def process_cv(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = DocumentForm()
    return render(request, 'process_cv.html', {
        'form': form
    })

def list_cv(request):
    try:
        df  = pd.DataFrame(list(Document.objects.all().values()))
        df = df[["id", "document", "uploaded_at"]]
        df["id"] = df["id"].astype(str)
        df["uploaded_at"] = df["uploaded_at"].dt.strftime('%Y-%m-%d')
    except:
        df = pd.DataFrame(columns = ["id", "document", "uploaded_at"])
    df.rename(columns = {"id": "ID", "document": "CV", "uploaded_at": "date"}, inplace = True)

    html_table = df.to_html(
        escape = False,
        index = False,
        border = 1,
        classes="table table-striped table-hover"
        )
    params = {"html_table": html_table}
    return render(request, 'list_cv.html', params)

def cv_specific(request, cv_id):
    ### Load CV based on ID
    filename = Document.objects.values_list(
        "document",
        flat = True
    ).get(id = cv_id)
    
    clean_text = get_text_from_document(filename)
    clean_text = prepare_text(clean_text)

    ### Load vectorizer

    vectorizer = pickle.load(
        open(
            "lab2/matcher/static/data/nuestro_vectorizer.pickle",
            "rb"
        )
    )

    ### Load predefined job matrix

    jobs = pickle.load(
        open(
            "lab2/matcher/static/data/puestos.pickle",
            "rb"
        )
    )
    jobs = prepare_matrix(jobs, "PUESTO")

    ### Vectorize

    text_vectorized = vectorize_text(vectorizer, [clean_text])

    jobs_vectorized = vectorize_text(vectorizer, jobs)

    ### Get similarity

    ranking = get_similarity(text_vectorized, jobs_vectorized, 10)

    ## Top

    ranking_match = ranking.to_html(
        formatters={
            "RANKING": "{:,.2%}".format
        },
        index = False,
        border = 1,
        classes = "table table-stripped table-hover",
    )
    params = {'html_match': ranking_match}
    return render(request, "match.html", params)