# ====================================================
# ================ Librerias y Clases ================
# ====================================================

from django.shortcuts import render
from django.template import loader, Template

from django.http import HttpResponse
from django.core.handlers.wsgi import WSGIRequest

# Import settings "CUSTOM_CONFIG" from settings.py
from mappinglatam.settings import CUSTOM_CONFIG

# ====================================================
# ====================== Paginas =====================
# ====================================================

WebPageContext: dict = CUSTOM_CONFIG["web"]

def MainPage(request: WSGIRequest) -> HttpResponse:
    return render(request, "index.html", WebPageContext)

def CreateNewPost(request: WSGIRequest) -> HttpResponse:
    print(request.COOKIES)

    return render(request, "newpost.html", WebPageContext)