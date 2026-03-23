from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

class EmailOrUsernameBackend(BaseBackend):
    """
    Custom authentication backend that allows users to login with either username or email.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to find user by username first
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                # If not found, try to find user by email
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None
        
        # Check if the password is correct
        if user.check_password(password) and user.is_active:
            return user
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
