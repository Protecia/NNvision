import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))



os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet.settings")

import django
django.setup()

from app1.models import Camera, Result

