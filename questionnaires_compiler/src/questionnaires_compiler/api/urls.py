from django.urls import re_path
from . import views


RE_ID_FIELD = "[a-zA-z_\-0-9:\s]+"

urlpatterns = [
    re_path(
        r'^(?P<version>(v1))/answers/?$',
        views.answers,
        name='questions'
    ),
    re_path(
        r'^(?P<version>(v1))/extract_questions/?$',
        views.extract_questions,
        name='extract_questions'
    ),
    re_path(
        r'^(?P<version>(v1))/update_answer/?$',
        views.update_answer,
        name='update_answer'
    ),
    re_path(
        r'^(?P<version>(v1))/finish_document/?$',
        views.finish_document,
        name='finish_document'
    ),
]


