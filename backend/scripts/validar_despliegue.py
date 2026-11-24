"""Validación local de configuración. No conecta a AWS ni revela secretos."""
import os
from urllib.parse import urlsplit
from sqlalchemy.engine import make_url
from app.config import load_settings


def validar():
    s = load_settings()
    if s.storage_mode != 's3' or not s.s3_bucket or not s.s3_region:
        raise RuntimeError('Producción requiere S3, bucket y AWS_REGION.')
    if not s.cors_origins:
        raise RuntimeError('Configura el origen HTTPS del frontend en CORS.')
    for origin in s.cors_origins:
        u = urlsplit(origin)
        if u.scheme != 'https' or not u.hostname or u.path or u.query or u.fragment or u.username:
            raise RuntimeError('CORS requiere orígenes HTTPS exactos, sin ruta ni credenciales.')
    secret = os.environ.get('ECORAEE_JWT_SECRET', '')
    if len(secret) < 32 or 'CAMBIAR' in secret.upper():
        raise RuntimeError('Configura un secreto JWT propio de al menos 32 caracteres.')
    try:
        db = make_url(s.db_url)
    except Exception:
        raise RuntimeError('ECORAEE_DB_URL no es una URL SQLAlchemy válida.') from None
    query = {k.lower(): str(v).lower() for k, v in db.query.items()}
    if db.drivername != 'mssql+pyodbc' or not db.host or not db.username or not db.password or not db.database:
        raise RuntimeError('Configura SQL Server con host, base y usuario SQL de aplicación.')
    if db.host.lower() in {'localhost', '127.0.0.1', '::1'}:
        raise RuntimeError('La base de producción no puede ser localhost.')
    if query.get('encrypt') not in {'yes', 'true'} or query.get('trustservercertificate') not in {'no', 'false'}:
        raise RuntimeError('SQL requiere Encrypt=yes y TrustServerCertificate=no.')
    if query.get('trusted_connection') in {'yes', 'true'}:
        raise RuntimeError('No usar autenticación integrada de Windows en EC2 Linux.')


if __name__ == '__main__':
    validar()
    print('Configuración de despliegue válida. Conectividad todavía no comprobada.')
