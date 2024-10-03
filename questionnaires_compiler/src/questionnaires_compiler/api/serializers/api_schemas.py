import json
from typing import Optional, Union, Any

from pydantic import BaseModel, Field, field_validator


# IETF devised RFC 7807
class ErrorData(BaseModel):
    type: str = Field(
        ...,
        description='a URI identifier that categorizes the error'
    )

    title: str = Field(
        ...,
        description='a brief, human-readable message about the error'
    )

    status: int = Field(
        ...,
        description='the HTTP response code'
    )

    code: Union[str, Any] = Field(
        None,
        description='specific error code'
    )

    detail: Union[str, Any] = Field(
        ...,
        description='a human-readable explanation of the error'
    )

    # instance: str
    trace_id: Optional[str] = Field(
        None,
        description='a random string that identifies the specific occurrence '
                    'of the error'
    )

    @field_validator('detail', 'code', mode='before')
    def join_dict(cls, v):
        if v and not isinstance(v, str):
            return json.dumps(v)
        return str(v)

