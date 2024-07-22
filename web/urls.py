from django.urls import path
from . import views

urlpatterns = [
    path("", views.MainPage, name="web-MainPage"),
    path("createnewpost", views.CreateNewPost, name="web-CreateNewPost"),
    path("login", views.LoginPage, name="web-LoginPage")
]