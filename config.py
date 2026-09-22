import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

# Cargar variables de entorno (opcional, si usas .env)
load_dotenv()


def _uri_de_base_datos() -> str:
    """Construye la URI de conexión a la base de datos.

    Orden de prioridad:
    1. DATABASE_URL completa (si ya viene lista para usar).
    2. Variables separadas DB_HOST/DB_USER/DB_PASSWORD/DB_NAME/DB_PORT:
       la contraseña se codifica automáticamente, así caracteres como @
       o espacios no rompen el formato de la URL.
    3. MySQL local por defecto (XAMPP en el puerto 3307).
    """
    url = os.getenv("DATABASE_URL", "").strip()
    # Limpiar comillas o espacios que se peguen por accidente en Vercel
    url = url.strip("\"'` ").strip()
    if url:
        try:
            from sqlalchemy.engine import make_url
            make_url(url)
            return url
        except Exception as exc:  # noqa: BLE001
            print(f"[AVISO] DATABASE_URL invalida ({exc}); se ignora y se usan DB_*")

    host = os.getenv("DB_HOST", "").strip()
    user = os.getenv("DB_USER", "").strip()
    nombre = os.getenv("DB_NAME", "").strip()
    if host and user and nombre:
        password = os.getenv("DB_PASSWORD", "")
        puerto = os.getenv("DB_PORT", "3306").strip() or "3306"
        return (
            f"mysql+pymysql://{user}:{quote_plus(password)}@{host}:{puerto}/{nombre}"
            "?charset=utf8mb4"
        )

    return "mysql+pymysql://root:@127.0.0.1:3307/edufinanzas?charset=utf8mb4"


SQLALCHEMY_DATABASE_URI = _uri_de_base_datos()

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

# Configuración de Google (Login con Google / Identity Services)
# Se obtiene en https://console.cloud.google.com/apis/credentials
# Tipo: "ID de cliente de OAuth 2.0" -> Aplicación web
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip().strip("\"'` ")

# Configuración de CORS si es necesario
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5000").split(",")