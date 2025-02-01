from django.urls import path, include

from . import views 

urlpatterns = [
    path('', views.index, name = 'index'),
    path('process/', views.process_cv, name = 'process_cv'),
    path('cv/', views.list_cv, name = 'list_cv'),
]