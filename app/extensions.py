"""
Extensiones compartidas de Flask.
Se separa la instancia de SQLAlchemy aquí para evitar imports circulares:
__init__ crea la app -> inicializa db -> luego importa los modelos.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
