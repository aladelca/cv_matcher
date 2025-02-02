from django.shortcuts import render, redirect
from .forms import DocumentForm
from .models import Document
from .transformer import (
    get_text_from_document,
    get_pdf,
    prepare_text,
    prepare_matrix,
    vectorize_text,
    get_similarity
)
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
    except Exception:
        df = pd.DataFrame(columns = ["id", "document", "uploaded_at"])
    df.rename(columns = {"id": "ID", "document": "CV", "uploaded_at": "date"}, inplace = True)

    def add_url(data):
        output = "<a href='"
        output = output + data
        output = output + "'>"
        output = output + data
        output = output + "</a"
        return output
    
    df["ID"] = df["ID"].apply(add_url)

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
    
    if ".docx" in  filename:
        clean_text = get_text_from_document(filename)
    elif ".pdf" in filename:
        clean_text = get_pdf(filename)
        
    clean_text = prepare_text(clean_text)

    ### Load vectorizer

    vectorizer = pickle.load(
        open(
            "matcher/static/data/nuestro_vectorizer.pickle",
            "rb"
        )
    )

    ### Load predefined job matrix

    jobs = pickle.load(
        open(
            "matcher/static/data/puestos.pickle",
            "rb"
        )
    )
    jobs = prepare_matrix(jobs, "PUESTO")

    ### Vectorize

    text_vectorized = vectorize_text(vectorizer, [clean_text])

    jobs_vectorized = vectorize_text(vectorizer, jobs["PUESTO"])

    ### Get similarity

    ranking = get_similarity(text_vectorized, jobs_vectorized, jobs, 10)

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