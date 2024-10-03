import datetime
import logging

import jwt
from django.contrib.auth.models import AnonymousUser
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import authentication, exceptions

from django_core.settings import application_settings, admin_settings

_JWT_SECRET = application_settings.JWT_SECRET

_log = logging.getLogger(__name__)


class BearerAuthentication(authentication.TokenAuthentication):
    keyword = "Bearer"


class AdminAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):

        admin_token = request.META.get('HTTP_X_API_KEY')
        if admin_token is None:
            raise exceptions.NotAuthenticated()

        elif admin_token == admin_settings.ADMIN_TOKEN:
            return Admin(), None
        else:
            _log.exception("Failed admin authentication %r" % request)
            raise exceptions.AuthenticationFailed()


class CallbackAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):

        jwt_token = request.query_params.get('token')
        if jwt_token is None:
            raise exceptions.NotAuthenticated()

        try:
            jwt.decode(jwt_token, key=_JWT_SECRET, algorithms=["HS256"])
            return TrustFullService(), None

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed()

        except Exception:
            _log.exception("Cannot validate jwt token")
            raise exceptions.AuthenticationFailed()


def build_jwt_ticket() -> str:
    valid_before = datetime.datetime.now() + \
                   datetime.timedelta(minutes=10)

    return jwt.encode(
        payload={'exp': valid_before}, key=_JWT_SECRET, algorithm='HS256'
    )


class TrustFullService(AnonymousUser):

    def __init__(self):
        super().__init__()

    @property
    def is_authenticated(self):
        return True


class Admin(AnonymousUser):

    token_id = "created_by_questionnaires_compiler_administrator"

    # TODO: mappare informnazioni provenienti dalla sessione e salvarle nello
    #   storico operazioni effettuate su organizzazione, utente

    def __init__(self):
        super().__init__()

    @property
    def is_authenticated(self):
        return True
