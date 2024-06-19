# ====================================================
# ================ Librerias y Clases ================
# ====================================================

from django.http import JsonResponse
from django.core.handlers.wsgi import WSGIRequest
from mappinglatam.settings import DEBUG


# ====================================================
# ===================== Variables ====================
# ====================================================

STATUS_NOT_ALLOWED: int = 405
STATUS_OK: int = 200

METHOD_NOT_ALLOWED: dict[str] = {
    "message": "Method not allowed."
}


# ====================================================
# ======================= APIs =======================
# ====================================================

def SimpleAPI(request: WSGIRequest) -> JsonResponse:
    if not DEBUG and request.method == "GET": return JsonResponse(METHOD_NOT_ALLOWED, status=STATUS_NOT_ALLOWED)

    data: dict[str] = {
        "message": "Hello, World!",
    }

    return JsonResponse(data, status=STATUS_OK)

def Files(request: WSGIRequest) -> JsonResponse:
    if not DEBUG and request.method == "GET": return JsonResponse(METHOD_NOT_ALLOWED, status=STATUS_NOT_ALLOWED)

    print(request)

    data: dict[str] = {
        "message": "Hello, World!",
    }

    return JsonResponse(data, status=STATUS_OK)