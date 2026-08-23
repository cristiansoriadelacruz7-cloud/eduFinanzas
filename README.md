# EduFinanzas

Aplicación web de educación financiera para estudiantes peruanos.
Flask + MySQL en el backend, frontend estático (HTML/CSS/JS) servido por el mismo servidor.

## Estructura

```
eduFinanzas/
├── app/
│   ├── __init__.py       # Factory de Flask + rutas del frontend
│   ├── extensions.py     # SQLAlchemy
│   ├── models/db.py      # Modelos ORM (Usuario, Ingreso, Gasto, MetaAhorro, etc.)
│   ├── routes/           # Blueprints de la API (/api/...)
│   ├── controllers/      # Lógica de negocio
│   └── models/           # Modelos de datos auxiliares
├── frontend/
│   ├── index.html        # Landing
│   ├── pages/            # login, registro, dashboard, movimiento, reportes
│   ├── css/ y js/        # Estilos y lógica de cliente (objeto global EF)
│   ├── robots.txt        # SEO
│   └── sitemap.xml       # SEO
├── database/edufinanzas.sql   # Esquema inicial de la BD
├── config.py             # Lee DATABASE_URL y SECRET_KEY del entorno
├── Procfile              # Comando de arranque en producción (gunicorn)
└── requirements.txt
```

## Ejecutar en local

1. Crear el entorno virtual e instalar dependencias:

   ```
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Tener MySQL corriendo y crear la base de datos `edufinanzas`
   (o importar `database/edufinanzas.sql`).

3. (Opcional) Copiar `.env.example` a `.env` y ajustar valores.

4. Arrancar:

   ```
   python app/__init__.py
   ```

   Abre http://127.0.0.1:5000

---

## 1) Subir a GitHub

```bash
git init
git add .
git commit -m "Primer commit: EduFinanzas"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/edufinanzas.git
git push -u origin main
```

> Crea primero el repositorio vacío en https://github.com/new (sin README,
> sin .gitignore, sin licencia, para no chocar con este historial).
> El archivo `.env` NO se sube: está protegido por `.gitignore`.

## 2) Base de datos en la nube (MySQL gratis)

Opción recomendada: **Aiven for MySQL** (plan free):

1. Crea cuenta en https://aiven.io y crea un servicio **MySQL** (plan Free).
2. Espera a que el servicio esté "RUNNING".
3. En la vista del servicio copia el **Service URI**.
4. Conviértelo a formato SQLAlchemy:

   ```
   mysql+pymysql://USUARIO:CONTRASENA@HOST:PUERTO/defaultdb?charset=utf8mb4&ssl=true
   ```

   (Aiven exige conexión SSL; PyMySQL la activa con `ssl=true` en la URL).
5. Las tablas se crean solas al primer arranque (`db.create_all()`).

Alternativas: TiDB Cloud Serverless (compatible MySQL), Clever Cloud, Railway (de pago).

## 3) Desplegar la app gratis en Render

1. Crea cuenta en https://render.com con tu GitHub.
2. **New + → Web Service** → conecta el repo `edufinanzas`.
3. Configuración:
   - **Runtime**: Python 3
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `gunicorn app:app --workers 2 --threads 4 --timeout 90 --bind 0.0.0.0:$PORT`
     (o simplemente deja que lea el `Procfile`)
4. **Environment variables**:
   - `DATABASE_URL` = la URL SQLAlchemy de Aiven del paso anterior
   - `SECRET_KEY` = una cadena larga y aleatoria
   - `FLASK_DEBUG` = `false`
5. **Create Web Service**. En unos minutos tendrás una URL tipo
   `https://edufinanzas.onrender.com`.

> El plan gratuito "duerme" tras 15 minutos sin tráfico; la primera visita tarda ~50 s en despertar.

## 4) Aparecer en Google

1. Cuando Render te dé la URL definitiva:
   - Actualiza el dominio dentro de `frontend/sitemap.xml` y `frontend/robots.txt`,
     haz commit y push.
2. Ve a https://search.google.com/search-console con tu cuenta de Google.
3. Agrega la propiedad (tu URL de Render) y verifica (método HTML o DNS).
4. En **Sitemaps** envía: `https://TU-DOMINIO/sitemap.xml`
5. Usa **Inspección de URL → Solicitar indexación** para la página principal.
6. En días/semanas aparecerás en las búsquedas (mejor antes si compartes el enlace).

---

## API principal

| Método | Ruta | Descripción |
|---|---|---|
| POST | /api/login | Inicia sesión |
| POST | /api/logout | Cierra sesión |
| GET | /api/sesion | Usuario actual |
| POST | /api/registro | Registro con validación DNI (RENIEC simulada) |
| GET | /api/dashboard | Resumen financiero del mes |
| GET/PUT | /api/presupuesto | Presupuesto diario personalizado |
| GET/POST | /api/gastos · /api/ingresos | CRUD movimientos |
| DELETE | /api/gastos/<id> · /api/ingresos/<id> | Eliminar movimiento |
| GET/POST | /api/metas | Metas de ahorro |
| PUT | /api/metas/<id>/aportar | Aportar a una meta |
| DELETE | /api/metas/<id> | Eliminar meta |
| GET | /api/reportes | Reportes mensuales y por categoría |
