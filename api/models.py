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

from mappinglatam.settings import CUSTOM_CONFIG as EnvSettings

# ====================================================
# ================== Almacenamiento ==================
# ====================================================

from .storage import Storage as CloudFlareStorage

class Storage(Model):
    storage_id:     AutoField = AutoField(primary_key=True)
    storage_url:    TextField = TextField(unique=True)

    def ObtenerURLUsandoTipoArchivo(self, TipoArchivo: str | list = None) -> str:
        if not TipoArchivo:
            raise ValueError("Tipo de archivo no puede ser nulo")
        
        if not isinstance(TipoArchivo, list):
            TipoArchivo = [TipoArchivo]

        resultados = self.objects.get(storage_url__in=TipoArchivo)
        return resultados.storage_url
    
    def SubirArchivoObjeto(self, FileObject, Key: str = None, Prefix: str = "") -> None:
        try:
            CloudFlareStorage.UploadFileObject(FileObject, f"{Prefix}/{Key}")
        except Exception as e:
            print(e)
        else:
            self.objects.create(
                storage_url = f"""{EnvSettings["cloudflare"]["PublicURL"]}/{Prefix}/{Key}"""
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
# ====================== Usuario =====================
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



# ====================================================
# ======================= Post =======================
# ====================================================

NSFW_PORN: int = 1
NSFW_VIOLENCE: int = 2
NSFW_HATE: int = 3

TIPO_NSFW: tuple = (
    (NSFW_PORN, "Porn"),
    (NSFW_VIOLENCE, "Violence"),
    (NSFW_HATE, "Hate")
)

class Post(Model):
    post_id:            AutoField = AutoField(primary_key=True)
    post_usuario_id:    ForeignKey = ForeignKey(Usuario, on_delete=models.CASCADE)

    post_contenido:     TextField = TextField()
    post_fecha:         TimeField = TimeField(default=timezone.now)
    post_nsfw:          IntegerField = IntegerField(choices=TIPO_NSFW, default=0)
    post_media1:        TextField = TextField()
    post_media2:        TextField = TextField()
    post_media3:        TextField = TextField()
    post_media4:        TextField = TextField()

    def CrearPost(self, Usuario: Usuario = None, Contenido: str = None, Media: list = None, NSFW: int = 0):
        if not Usuario:
            raise ValueError("Usuario no puede ser nulo")
        
        if not Contenido:
            raise ValueError("Contenido no puede ser nulo")
        
        if not Media:
            Media = ["", "", "", ""]

        Media[0] = Media[0] if len(Media[0]) > 0 else ""
        Media[1] = Media[1] if len(Media[1]) > 0 else ""
        Media[2] = Media[2] if len(Media[2]) > 0 else ""
        Media[3] = Media[3] if len(Media[3]) > 0 else ""
        
        if NSFW not in TIPO_NSFW:
            raise ValueError("NSFW no valido")

        self.objects.create(
            post_usuario_id = Usuario,
            post_contenido = Contenido,
            post_media1 = Media[0],
            post_media2 = Media[1],
            post_media3 = Media[2],
            post_media4 = Media[3],
            post_nsfw = NSFW
        )

    def EsNSFW(self) -> bool:
        return self.post_nsfw > 0



class Like(Model):
    like_id:            AutoField = AutoField(primary_key=True)
    like_post_id:       ForeignKey = ForeignKey("Post", on_delete=models.CASCADE)
    like_usuario_id:    ForeignKey = ForeignKey("Usuario", on_delete=models.CASCADE)

    def LikePost(self, Post: Post = None, Usuario: Usuario = None) -> None:
        if not Post:
            raise ValueError("Post no puede ser nulo")
        
        if not Usuario:
            raise ValueError("Usuario no puede ser nulo")

        self.objects.create(
            like_post_id = Post,
            like_usuario_id = Post.post_usuario_id
        )

        Registro: Registro = Registro()
        Registro.Log(
            Descripcion = f"El usuario {Usuario.usuario_nombre} le dio like al post {Post.post_id}",
            Usuario = Usuario
        )


class Comentario(Model):
    comentario_id:      AutoField = AutoField(primary_key=True)
    comentario_post_id: ForeignKey = ForeignKey("Post", on_delete=models.CASCADE)
    comentario_usuario_id: ForeignKey = ForeignKey("Usuario", on_delete=models.CASCADE)

    comentario_texto:   TextField = TextField()
    comentario_fecha:   TimeField = TimeField(default=timezone.now)

class Tag(Model):
    tag_id:             AutoField = AutoField(primary_key=True)
    tag_post_id:        ForeignKey = ForeignKey("Post", on_delete=models.CASCADE)
    tag_usuario_id:     ForeignKey = ForeignKey("Usuario", on_delete=models.CASCADE)

    tag_texto:          TextField = TextField()
    tag_fecha:          TimeField = TimeField(default=timezone.now)



# ====================================================
# ===================== Registro =====================
# ====================================================

class Registro(Model):
    registro_id:            AutoField = AutoField(primary_key=True)
    registro_fecha:         TimeField = TimeField(default=timezone.now)
    registro_descripcion:   TextField = TextField()
    registro_usuario:       ForeignKey = ForeignKey(Usuario, on_delete=models.CASCADE)

    def Log(self, Descripcion: str = None, Usuario: Usuario = None) -> None:
        if not Descripcion:
            raise ValueError("Descripcion no puede ser nula")

        if not Usuario:
            raise ValueError("Usuario no puede ser nulo")

        self.objects.create(
            registro_descripcion = Descripcion,
            registro_usuario = Usuario
        )