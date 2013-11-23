#!/usr/bin/env python
import os
import sys
from os.path import dirname, abspath, join

if __name__ == "__main__":
    sys.path.insert(0, dirname(abspath(__file__)))
    sys.path.insert(1, join(dirname(abspath(__file__)), 'apps'))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "turtlecrossing.settings.local")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

