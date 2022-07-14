# Import necessary packages
from django.urls import path
from . import views

# View's URL mapping
urlpatterns = [
    path('', views.index, name='index'),
    path('search_file/', views.search_file, name='search_file'),
]
