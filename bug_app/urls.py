from django.urls import path
from . import views

urlpatterns = [
    path('', views.data_display, name='data_display'),
]