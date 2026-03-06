from rest_framework.authentication import BaseAuthentication
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import AuthenticationFailed
from .models import Pot

class DeviceTokenAuthentication(BaseAuthentication): #esp icin ozel dogrulama
    header_name = "HTTP_X_DEVICE_TOKEN"

    def authenticate(self, request):
        token = request.META.get(self.header_name)

        if not token:
            return None
        
        try:
            pot = Pot.objects.get(device_token=token)
        except Pot.DoesNotExist:
            raise AuthenticationFailed("")
        
        return(AnonymousUser(),pot)
