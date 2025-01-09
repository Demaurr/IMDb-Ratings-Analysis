from django.urls import path
from . import views

urlpatterns = [
    path('process_file/', views.process_csv, name='process_csv'),
    path('search_result/', views.search_result, name='search_result')
]