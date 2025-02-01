from django.shortcuts import render, redirect
from .forms import DocumentForm
from .models import Document
import pandas as pd
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