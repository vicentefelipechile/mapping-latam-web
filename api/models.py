# ====================================================
# ================ Librerias y Clases ================
# ====================================================

from typing import Any
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import Permission

from django.utils import timezone
from django.db import models
from django.db.models import Model

from django.forms import ChoiceField
from django.db.models import TextField, IntegerField, CharField, AutoField, TimeField
from django.db.models import BooleanField
from django.db.models import ForeignKey, ManyToManyField

from hashlib import sha256
from random import randint



# ====================================================
# ===================== Registro =====================
# ====================================================

class Registro(Model):
    registro_id:            AutoField = AutoField(primary_key=True)
    registro_fecha:         TimeField = TimeField(default=timezone.now)
    registro_descripcion:   TextField = TextField()
    registro_usuario:       ForeignKey = ForeignKey("Usuario", on_delete=models.CASCADE)

    def Log(self, Descripcion: str = None, Usuario: object = None) -> None:
        if not Descripcion:
            raise ValueError("Descripcion no puede ser nula")

        if not Usuario:
            raise ValueError("Usuario no puede ser nulo")

        self.objects.create(
            registro_descripcion = Descripcion,
            registro_usuario = Usuario
        )


# ====================================================
# ===================== Permisos =====================
# ====================================================

# ALL: int = 0 - Desactivado por temas de seguridad
PERM_CREATE: int = 1
PERM_EDIT:   int = 2 ^ 1 # 2
PERM_DELETE: int = 2 ^ 2 # 4
PERM_VIEW:   int = 2 ^ 3 # 8
PERM_UPLOAD: int = 2 ^ 4 # 16
PERM_NSFW:   int = 2 ^ 5 # 32

TIPO_PERMISO: tuple = (
    (PERM_CREATE, "Create"),
    (PERM_EDIT,   "Edit"),
    (PERM_DELETE, "Delete"),
    (PERM_VIEW,   "View"),
    (PERM_UPLOAD, "Upload"),
    (PERM_NSFW,   "NSFW")
)

class Permisos(Model):
    permiso_id:     AutoField = AutoField(primary_key=True)
    permiso_nombre: TextField = TextField(unique=True)

    def CrearPermiso(self, Nombre: str = None) -> object | None:
        if not Nombre:
            raise ValueError("Nombre de permiso no puede ser nulo")

        # Sumar todos los permisos anteriores y sumar 1
        AllPerms: list = self.objects.all()
        LastPerm: int = 1

        for Perm in AllPerms:
            LastPerm += Perm.permiso_id

        NewPermiso: Permisos = self.objects.create(
            permiso_nombre = Nombre
        )

        return NewPermiso
    

    def ExistePermiso(self, Nombre: str = None) -> bool:
        if not Nombre:
            raise ValueError("Nombre de permiso no puede ser nulo")
        
        try:
            Permiso: Permisos = self.objects.get(permiso_nombre=Nombre)
            return not not Permiso
        except:
            return False
        

    def TienePermiso(self, Nombre: str = None, Permiso: int = None) -> bool:
        if not Nombre:
            raise ValueError("Nombre de permiso no puede ser nulo")
        
        if not Permiso:
            raise ValueError("Permiso no puede ser nulo")
        
        try:
            Permiso: Permisos = self.objects.get(permiso_nombre=Nombre)
            return Permiso.permiso_id & Permiso
        except:
            return False


    def GenerarPermisos(self) -> None:
        ExistAtLeastOne: bool = self.objects.all().count() > 0

        if not ExistAtLeastOne:
            for Permiso in TIPO_PERMISO:
                self.objects.create(
                    permiso_nombre = Permiso[1]
                )



# ====================================================
# ====================== Modelos =====================
# ====================================================

ROOT:   int = 0
ADMIN:  int = 1
USER:   int = 2

TIPO_USUARIO: tuple = (
    (ROOT,  "Root"),
    (ADMIN, "Admin"),
    (USER,  "User")
)

TIPO_USUARIO_ENUM: list = [ROOT, ADMIN, USER]


class Usuario(Model):
    usuario_id:       AutoField = AutoField(primary_key=True)
    usuario_tipo:     IntegerField = IntegerField(choices=TIPO_USUARIO, default=USER)

    usuario_nombre:   CharField = CharField(max_length=50, unique=True)
    usuario_password: CharField = CharField(max_length=256)
    usuario_desactivado: BooleanField = BooleanField(default=False)


    # ==============
    # === Metodos ==
    # ==============

    def CrearUsuario(self, Nombre: str = None, Password: str = None, Tipo: int = USER, Responsable: str = None) -> object | None:
        if not Nombre:
            raise ValueError("Nombre de usuario no puede ser nulo")

        if not Password:
            raise ValueError("Password de usuario no puede ser nulo")
        
        if not Responsable:
            raise ValueError("Responsable no puede ser nulo")
        
        if Tipo not in TIPO_USUARIO_ENUM:
            raise ValueError("Tipo de usuario no valido")
        
        NewUser: Usuario = self.objects.create(
            usuario_nombre = Nombre,
            usuario_password = make_password(Password),
            usuario_tipo = Tipo
        )

        return NewUser


    def BorrarUsuario(self, Nombre: str = None, Responsable: str = None) -> bool:
        if not Nombre:
            raise ValueError("Nombre de usuario no puede ser nulo")

        if not Responsable:
            raise ValueError("Responsable no puede ser nulo")
        
        # Obtener el tipo de usuario del responsable
        UserResponsable: Usuario = self.objects.get(usuario_nombre=Responsable)
        HasPermission: bool = UserResponsable.usuario_tipo in [ROOT, ADMIN]

        if HasPermission:
            UserTarget: Usuario = self.objects.get(usuario_nombre=Nombre)
            UserTarget.delete()

            return True
        else:
            return False


    def RestaurarUsuario(self, Nombre: str = None, Responsable: str = None) -> bool:
        if not Nombre:
            raise ValueError("Nombre de usuario no puede ser nulo")

        if not Responsable:
            raise ValueError("Responsable no puede ser nulo")
        
        # Obtener el tipo de usuario del responsable
        UserResponsable: Usuario = self.objects.get(usuario_nombre=Responsable)
        HasPermission: bool = UserResponsable.usuario_tipo in [ROOT, ADMIN]

        if HasPermission:
            UserTarget: Usuario = self.objects.get(usuario_nombre=Nombre)
            UserTarget.usuario_desactivado = False

            return True
    

    def ModificarPassword(self, Nombre: str = None, Password: str = None, Responsable: str = None) -> bool:
        if not Nombre:
            raise ValueError("Nombre de usuario no puede ser nulo")

        if not Password:
            raise ValueError("Password de usuario no puede ser nulo")
        
        if not Responsable:
            raise ValueError("Responsable no puede ser nulo")
        
        UserResponsable: Usuario = self.objects.get(usuario_nombre=Responsable)
        HasPermission: bool = (Nombre == Responsable) or ( UserResponsable.usuario_tipo in [ROOT] )

        return True
    

    def ModificarTipo(self, Nombre: str = None, Tipo: int = USER, Responsable: str = None) -> bool:
        # Obtener el tipo de usuario del responsable
        if not Nombre:
            raise ValueError("Nombre de usuario no puede ser nulo")
        
        if Tipo not in TIPO_USUARIO_ENUM:
            raise ValueError("Tipo de usuario no valido")
        
        if not Responsable:
            raise ValueError("Responsable no puede ser nulo")
        
        UserResponsable: Usuario = self.objects.get(usuario_nombre=Responsable)
        HasPermission: bool = UserResponsable.usuario_tipo in [ROOT]

        if HasPermission:
            UserTarget: Usuario = self.objects.get(usuario_nombre=Nombre)
            UserTarget.usuario_tipo = Tipo

            return True
        else:
            return False
    

    def VerificarPassword(self, Nombre: str = None, Password: str = None) -> bool:
        if not Nombre:
            raise ValueError("Nombre de usuario no puede ser nulo")

        if not Password:
            raise ValueError("Password de usuario no puede ser nulo")
        
        UserTarget: Usuario = self.objects.get(usuario_nombre=Nombre)
        return check_password(Password, UserTarget.usuario_password)