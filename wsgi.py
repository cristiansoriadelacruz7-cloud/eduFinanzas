"""
Punto de entrada WSGI para hosting en producción (AlwaysData, etc.).

AlwaysData espera un archivo que exponga la variable `application`.
Nuestro factory está en app/__init__.py, donde `app = create_app()`.
"""

import os
import sys

# Asegurar que la raíz del proyecto esté en el path (para encontrar config.py)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app as application  # noqa: E402,F401
