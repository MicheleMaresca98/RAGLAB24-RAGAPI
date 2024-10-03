#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import logging
import os
import sys


log = logging.getLogger(__name__)


def initialize_debugger():
    import debugpy

    # RUN_MAIN envvar is set by the reloader to indicate that this is the
    # actual thread running Django. This code is in the parent process and
    # initializes the debugger
    log.info("RUN_MAIN: ", os.getenv("RUN_MAIN"))
    if not os.getenv("RUN_MAIN"):
        debugpy.listen(("0.0.0.0", 5678))


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    if 'runserver' in sys.argv:
        initialize_debugger()
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
