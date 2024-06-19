from django.urls import path
from . import api

# Current Version
API_VERSION: int = 1

urlpatterns = [
    path("", api.SimpleAPI, name="SimpleAPI"),
    path("files", api.Files, name="Files")
]