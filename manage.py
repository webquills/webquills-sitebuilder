#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys
from pathlib import Path


def get_django_package() -> str:
    """A simple heuristic to find the main package for this Django project."""
    project_dir = Path(__file__).parent
    for item in project_dir.iterdir():
        if not item.is_dir():
            continue
        if item.joinpath("settings.py").exists():
            # Found it
            return item.name

    # If we fall through the loop, there is no settings.py, or this file is in the
    # wrong place.
    raise Exception(
        "Unable to locate a Django settings file (searched */settings.py). "
        "This script cannot continue without a settings file."
    )


def main():
    """Run administrative tasks."""
    package = get_django_package()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{package}.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
