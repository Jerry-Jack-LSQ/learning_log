
from django.urls import path
from . import views

app_name = 'mogu'

urlpatterns = [
    path('', views.index, name='index')
]   