# Issue Tracker

Aplicación para registrar y dar seguimiento a incidencias: inicio de sesión, alta de incidencias, cambio de estado y prioridad, filtros y un resumen por estado.

- **Backend:** FastAPI, Firestore, JWT, contraseñas con Argon2
- **Frontend:** Angular (standalone components, reactive forms, lazy loading)
- **Infraestructura:** Docker Compose en local; en GCP el backend en Cloud Run, frontend en Firebase Hosting y los datos en Firestore, deploy con Terraform

En línea:

- App: https://gapsi-511219.web.app (usuarios de prueba más abajo)
- API: https://backend-435928575208.us-central1.run.app/docs

[backend](backend/README.md)
[frontend](frontend/README.md)
[terraform](terraform/README.md).

## Correr en local

```bash
docker compose up --build
```

| Servicio | URL |
|---|---|
| Frontend | http://localhost:9901 |
| API | http://localhost:9900 |
| Documentación de la API | http://localhost:9900/docs |
| Emulador de Firestore | http://localhost:9902 |

Al levantar, el servicio `seed` carga usuarios e incidencias de prueba.

### Usuarios de prueba

| Usuario | Contraseña |
|---|---|
| user1 | demo_user1pass |
| user2 | demo_user2pass |

## Tests

```bash
./backend/scripts/run_tests.sh
./frontend/scripts/run_tests.sh
```

Los test corren usando el emulador de firestore.

## API

Todos los endpoints, salvo el login, requieren `Authorization: Bearer <token>`.

| Método | Ruta | |
|---|---|---|
| POST | `/auth/login` | Devuelve el JWT |
| GET | `/auth/user` | Usuario de la sesión |
| GET | `/issues` | Lista paginada. Filtros opcionales: `status`, `priority`. Paginación: `limit` (1-100, 20 por defecto) y `cursor` |
| POST | `/issues` | Crea una incidencia, siempre empieza como `open` |
| PATCH | `/issues/{id}` | Cambia `status` y/o `priority` |
| GET | `/issues/summary` | Total y cantidad por estado |

Prioridades: `high`, `medium`, `low`. Estados: `open`, `in_progress`, `done`.

La lista se pagina por cursor: cada respuesta trae `next_cursor`, que se manda en la siguiente petición para obtener la página que sigue.

### Postman

La colección está en `backend/postman_collection.json`. Al importarla, corre primero `Auth > Login`: guarda el token y las demás peticiones lo usan. Apunta a `http://localhost:9900`; para otro ambiente cambiar la variable `baseUrl`.

## Estructura

```
backend/
  app/
    routers/      endpoints
    services/     consultas a Firestore
    schemas/      modelos de Pydantic
    internal/     hash de contraseñas y JWT
  scripts/        seed y tests
  postman_collection.json
  tests/
frontend/src/app/
  core/auth/      servicio de sesión, interceptor y guards
  layout/shell/   encabezado y contenedor de las páginas con sesión
  features/
    login/
    issues/       lista, resumen y formulario de alta
terraform/        despliegue en GCP
```

## Despliegue en GCP

Terraform crea Firestore (con los índices que usa la lista), Artifact Registry, el secreto del JWT en Secret Manager, el backend en Cloud Run y el sitio de Firebase Hosting.

1. Infraestructura base:

   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars   # poner project_id
   terraform init
   terraform apply
   ```

2. Poner la salida de `terraform output -raw backend_url` como `apiUrl` en `frontend/src/environments/environment.ts`.

3. Construir y subir la imagen del backend:

   ```bash
   REGISTRY=$(terraform output -raw registry)
   gcloud auth configure-docker "${REGISTRY%%/*}"
   docker build --platform linux/amd64 --target prod -t "$REGISTRY/backend:v1" ../backend
   docker push "$REGISTRY/backend:v1"
   ```

4. Agregar `backend_image_tag = "v1"` a `terraform.tfvars` y correr `terraform apply` otra vez.

5. Publicar el frontend en Firebase Hosting:

   ```bash
   SITE=$(terraform output -raw hosting_site_id)
   cd ../frontend
   npm ci && npm run build
   npx firebase-tools login
   npx firebase-tools target:apply hosting app "$SITE" --project <proyecto>
   npx firebase-tools deploy --only hosting:app --project <proyecto>
   ```

   `target:apply` solo hace falta la primera vez; guarda el sitio en `.firebaserc`. La app queda en `terraform output frontend_url`.

6. Cargar los usuarios en el Firestore real:

   ```bash
   cd ../backend
   GOOGLE_CLOUD_PROJECT=<proyecto> uv run python -m scripts.seed
   ```

Para actualizar el backend se sube una imagen con un tag nuevo, se cambia en `terraform.tfvars` y se aplica. Para el frontend basta con `npm run build` y `firebase deploy`.
