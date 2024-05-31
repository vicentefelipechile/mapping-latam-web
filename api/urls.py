from django.urls import path
from . import api

# Current Version
API_VERSION: int = 1

urlpatterns = [
    path("api/v" + str(API_VERSION) + "/index/", api.index, name="index"),
]