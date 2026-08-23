import os
from dotenv import load_dotenv

# Cargar variables de entorno (opcional, si usas .env)
load_dotenv()

# Base de datos:
# - En local usa tu MySQL de siempre (127.0.0.1:3307)
# - En la nube define la variable DATABASE_URL, por ejemplo:
#   mysql+pymysql://usuario:contraseña@host:puerto/nombre_bd?charset=utf8mb4
SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:@127.0.0.1:3307/edufinanzas?charset=utf8mb4",
)

SQLALCHEMY_TRACK_MODIFICATIONS = False

# Configuración adicional
SECRET_KEY = os.getenv("SECRET_KEY", "edufinanzas-desarrollo-secret-key")

# Configuración de sesión
SESSION_TYPE = "filesystem"
SESSION_PERMANENT = False

# Configuración de Flask
DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

# Rutas de las plantillas y archivos estáticos
TEMPLATES_AUTO_RELOAD = DEBUG

# Configuración de CORS si es necesario
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5000").split(",")