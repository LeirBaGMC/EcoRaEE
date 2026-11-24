# Preparación del MVP AWS

Destino: React/Vite en S3 privado con CloudFront; FastAPI en EC2 Ubuntu detrás de Nginx y ALB; SQL Server en RDS privado; evidencias en otro bucket S3. No se necesitan contenedores ni dominio propio.

Estos archivos preparan el software: no crean recursos ni constituyen evidencia de un despliegue probado en AWS.

## Frontend

El workflow `Verificar y empaquetar` genera un artefacto con el contenido de `frontend/dist`. Publicar su contenido en la raíz del bucket del frontend. Antes de publicar, completar `config.js` con `window.ECORAEE_CONFIG = { API_URL: 'https://DISTRIBUCION_API.cloudfront.net' };`.

Este archivo es público: solo contiene la URL, nunca secretos. Permite cambiar la API sin recompilar. La configuración de ejecución tiene prioridad sobre `VITE_API_URL`. En producción no se permite el fallback silencioso a localhost o HTTP.

CloudFront: origen S3 normal privado con OAC y documento raíz `index.html`. Configurar `index.html` y `config.js` sin caché prolongada; invalidar ambos tras publicar. Los assets con hash pueden tener caché larga. Si se incorporan rutas del lado del cliente, configurar su resolución a `index.html` sin ocultar errores de la API.

## Backend

El artefacto conserva las carpetas `backend/` y `deploy/`. Ubicar `backend` en `/opt/ecoraee/backend`. Preparar una cuenta de servicio `ecoraee`, Python 3.11 o superior, ODBC Driver 18, unixODBC y un entorno virtual `/opt/ecoraee/venv` con `requirements.txt`. La instalación de estas dependencias sigue siendo necesaria: subir el código no las instala.

Completar la plantilla `backend/.env.aws.example` en `/etc/ecoraee/backend.env`, fuera del repositorio. Proteger el directorio y archivo para root; systemd lee el EnvironmentFile antes de ejecutar como usuario de servicio. Puede provisionarse posteriormente desde Parameter Store; este cambio NO implementa todavía esa recuperación automática.

Instalar `ec2/ecoraee.service` en systemd y `ec2/nginx.conf` como sitio Nginx, desactivando el sitio por defecto. Activar el servicio y Nginx después de validar su configuración. Uvicorn solo escucha en loopback; Nginx escucha en 80 y el SG de EC2 debe permitirlo solo desde el SG del ALB. No abrir 8000 al exterior. Los logs de Uvicorn quedan en journald; falta configurar su envío a CloudWatch.

El arranque ejecuta `python -m scripts.validar_despliegue`: comprueba S3, CORS, JWT y TLS de SQL sin conectar a AWS. No verifica existencia de recursos, privilegios ni disponibilidad. Usar `/health/live` para vida del proceso y `/health/ready` para disponibilidad de SQL. Acordar el health check del ALB según la política de reemplazo; una caída compartida de RDS no debe disparar reemplazos masivos de EC2.

Crear el esquema y migrar los datos de forma separada. La aplicación debe usar un usuario SQL con permisos de aplicación, no el usuario maestro de RDS. Instalar la cadena CA de RDS si el almacén del sistema no la reconoce. No resolver errores TLS habilitando TrustServerCertificate. El pool se multiplica por workers e instancias; inicialmente se configura un worker.

## Sin dominio propio

Usar dos distribuciones CloudFront: frontend y API. Para la API: origen ALB, HTTPS del navegador, todos los métodos necesarios para CRUD, caché desactivada y reenvío de Authorization, query strings y encabezados requeridos (incluido CORS). No añadir un prefijo `/api` porque las rutas actuales no lo tienen.

El tramo CloudFront a ALB será HTTP en este diseño sin certificado de origen. No es TLS extremo a extremo. Restringir el origen al tráfico de CloudFront y validar un encabezado de origen secreto mediante una regla del ALB; devolver 403 en la regla por defecto. EC2 solo acepta tráfico del ALB. Nginx marca el esquema externo como HTTPS para esta topología: si cambia, revisar esa configuración.

## Automatización y límites de verificación

`.github/workflows/ci.yml` ejecuta pruebas unitarias y build y publica artefactos para descarga. No ejecuta pruebas de integración contra una base productiva, no incluye archivos `.env` y no despliega en AWS. Su ejecución remota debe verificarse después de subir los cambios a GitHub. El despliegue automático mediante OIDC y las plantillas CloudFormation quedan pendientes de los identificadores y de la definición final de infraestructura.

Antes de grabar: comprobar login y roles, CRUD persistido en RDS, subida/lectura/borrado de evidencias S3, CORS, TLS SQL, acceso HTTPS y recuperación tras reiniciar EC2. El adaptador S3 está implementado pero requiere prueba real con el rol de EC2. Guardar snapshot y evidencias antes de retirar recursos.
