from django.urls import re_path
from . import views


RE_ID_FIELD = "[a-zA-z_\-0-9:\s]+"

urlpatterns = [
    re_path(
        r'^(?P<version>(v1))/answers/?$',
        views.answers,
        name='questions'
    )
]


