from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

class EmailBackend(ModelBackend):
    """
    Autenticación personalizada usando correo electrónico en lugar de nombre de usuario.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Si se proporciona email directamente en kwargs, utilizarlo
        email = kwargs.get('email') or username
        if not email or not password:
            return None
            
        UserModel = get_user_model()
        
        try:
            # Buscar usuario por email (puede venir como username o como email)
            user = UserModel.objects.get(email=email)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            # Si no existe usuario con ese email, retornar None
            return None
            
    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None