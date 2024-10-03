import logging
from typing import Optional

from rest_framework.exceptions import APIException, ValidationError
from rest_framework.views import exception_handler
from pydantic import ValidationError as PydanticValidationError

from questionnaires_compiler.api.serializers.api_schemas import ErrorData


class QuestionnairesCompilerError(APIException):
    title = 'Generic error'
    default_detail = 'A generic error has occurred'
    status_code = 500
    default_code = 1000
    trace_id = None

    def __init__(self, message: Optional[str] = None) -> None:
        # self.trace_id = correlation_id.get()
        if message is None:
            message = self.default_detail
        super(QuestionnairesCompilerError, self).__init__(message)

    def __str__(self) -> str:
        return f'{self.title}: {self.default_detail}'

    @classmethod
    def make_description(cls) -> str:
        return f'{cls.default_code} - {cls.default_detail}'


class SchemasValidationError(QuestionnairesCompilerError):
    title = 'Generic validation error'
    default_detail = 'A generic validation error has occurred'
    status_code = 400
    default_code = 1050

    def __init__(self, errors):
        super().__init__()
        self.default_detail = errors


class DbError(QuestionnairesCompilerError):
    title = 'Generic error in db operations'
    default_detail = 'A generic error has occurred in db operations'
    status_code = 500
    default_code = 1010


class IdentityConflict(DbError):
    title = 'Identity conflict'
    default_detail = "Identity with this id is already in database"
    status_code = 409
    default_code = 1011


class BackofficeUserConfilct(DbError):
    title = 'Backoffice user conflict'
    default_detail = "User with this username is already in database"
    status_code = 409
    default_code = 1015


class OrganizationConfilct(DbError):
    title = 'Organization conflict'
    default_detail = "Organization with this id is already in database"
    status_code = 409
    default_code = 1016


class OrganizationTokenConfilct(DbError):
    title = 'OrganizationToken conflict'
    default_detail = "OrganizationToken with this value is already in database"
    status_code = 409
    default_code = 1016


class IdentityNotExist(DbError):
    title = 'Identity does not exist'
    default_detail = 'Identity does not exist'
    status_code = 404
    default_code = 1020


class IdentityVerificationNotExist(DbError):
    title = 'IdentityVerification does not exist'
    default_detail = 'IdentityVerification does not exist'
    status_code = 404
    default_code = 1021


class OrganizationNotExist(DbError):
    title = 'Organization does not exist'
    default_detail = 'Organization does not exist'
    status_code = 404
    default_code = 1022


class OrganizationTokenNotExist(DbError):
    title = 'OrganizationToken does not exist'
    default_detail = 'OrganizationToken does not exist'
    status_code = 404
    default_code = 1023


class BackofficeUserNotExist(DbError):
    title = 'Backoffice user does not exist'
    default_detail = 'Backoffice user  does not exist'
    status_code = 404
    default_code = 1024


class IdentityVerificationScoreNotExist(DbError):
    title = 'IdentityVerification Score does not exist'
    default_detail = 'IdentityVerification Score does not exist'
    status_code = 404
    default_code = 1025


def custom_serializer_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        if isinstance(exc, PydanticValidationError):
            exc = SchemasValidationError(exc.errors())
        else:
            logging.exception(msg="Unknown exception")
            exc = QuestionnairesCompilerError()
        response = exception_handler(exc, context)

    if isinstance(exc, APIException):
        _type = exc.__class__.__name__

        if isinstance(exc, ValidationError):
            _title = "Validation error"
            _detail = response.data
            _code = 1030
        else:
            _title = getattr(exc, "title", "generic error")
            _detail = exc.default_detail
            _code = exc.get_codes()

        _data = ErrorData(
            code=_code, status=exc.status_code,
            detail=str(_detail), title=_title, type=_type)
        response.data = _data.model_dump()

    return response
