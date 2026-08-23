"""
Punto de entrada para Vercel (funciones serverless).

Vercel ejecuta los archivos dentro de la carpeta api/ y busca en ellos
una variable `app` de tipo WSGI. Nuestro factory está en app/__init__.py.
"""

import os
import sys

# Poner la raíz del proyecto en el path (para importar `app` y `config`)
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from app import app  # noqa: E402,F401  (variable WSGI que espera Vercel)
