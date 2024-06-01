# ====================================================
# ================ Librerias y Clases ================
# ====================================================

from django.core.files.storage import Storage
from django.conf import settings

from CloudFlare import CloudFlare
from mappinglatam.settings import CUSTOM_CONFIG


# ====================================================
# ====================== Storage =====================
# ====================================================

CloudFlareSettings: dict[str | any] = CUSTOM_CONFIG["cloudflare"]

class MyStorage(Storage):
    __CloudFlareAPI: CloudFlare = None

    def __init__(self, option: dict = None):
        if not option:
            option = settings.CUSTOM_STORAGE_OPTIONS
        
        self.__CloudFlareAPI = CloudFlare(email=CloudFlareSettings["Email"], token=CloudFlareSettings["Token"])