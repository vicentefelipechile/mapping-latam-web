from django.urls import path
from . import views

urlpatterns = [
    path("", views.MainPage, name="web-MainPage")
]