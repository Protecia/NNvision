import os
import sys

sys.path.append(os.path.abspath(".."))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet.settings")

import django
django.setup()

from app1.models import Camera, Result
