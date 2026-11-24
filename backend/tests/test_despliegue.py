import os
import unittest
from unittest.mock import patch
from app.config import load_settings
from scripts.validar_despliegue import validar


class TestDespliegue(unittest.TestCase):
    def verificar(self, **changes):
        env = {
            'ECORAEE_STORAGE': 's3', 'ECORAEE_S3_BUCKET': 'evidencias', 'AWS_REGION': 'us-east-1',
            'ECORAEE_CORS_ORIGINS': 'https://frontend.cloudfront.net',
            'ECORAEE_JWT_SECRET': 'a' * 48,
            'ECORAEE_DB_URL': 'mssql+pyodbc://app:password@db.example/ecoraee?Encrypt=yes&TrustServerCertificate=no',
        }
        env.update(changes)
        with patch.dict(os.environ, env, clear=True):
            load_settings.cache_clear()
            try:
                validar()
            finally:
                load_settings.cache_clear()

    def test_configuracion_cloud(self):
        self.verificar()

    def test_rechaza_configuracion_insegura(self):
        for changes in [
            {'ECORAEE_STORAGE': 'local'},
            {'ECORAEE_CORS_ORIGINS': '*'},
            {'ECORAEE_JWT_SECRET': 'CAMBIAR' * 8},
            {'ECORAEE_DB_URL': 'mssql+pyodbc://app:password@db.example/db?Encrypt=yes&TrustServerCertificate=yes'},
        ]:
            with self.subTest(changes=list(changes)), self.assertRaises(RuntimeError):
                self.verificar(**changes)
