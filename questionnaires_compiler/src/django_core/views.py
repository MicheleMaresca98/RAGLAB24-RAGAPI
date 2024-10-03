import logging
import os

from django.http.response import JsonResponse

from .versioninfo import VERSION

COMMIT_HASH = os.getenv('COMMIT_HASH')

log = logging.getLogger(__name__)


def app_version(request, *args, **kwargs):
    version_payload = {
        'version': VERSION,
        'commit': COMMIT_HASH
    }
    log.info("VersionInfo: %r", version_payload)
    return JsonResponse(data=version_payload, status=200)
