from django.urls import path
from . import views

urlpatterns = [
    path('csv_process/', views.process_csv, name='process_csv'),
    path('search_result/', views.search_result, name='search_result')
]