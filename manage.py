#!/usr/bin/env python3
import os
import sys

if __name__ == "__main__":
    sys.dont_write_bytecode = True

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spartan.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
