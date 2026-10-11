# Terraform

Infraestructura en GCP.

## Recursos

- APIs de Cloud Run, Firebase, Firebase Hosting, Firestore, Artifact Registry y Secret Manager
- Firestore en modo nativo con los índices compuestos
- Artifact Registry para la imagen del backend
- Service account del backend, solo con acceso a Firestore y a su secreto
- El backend en Cloud Run, público y escalando a 0
- Firebase en el proyecto y un sitio de Hosting para el frontend. `firebase deploy`

## Variables

| Variable | Default | |
|---|---|---|
| `project_id` | — | Obligatoria |
| `region` | `us-central1` | |
| `backend_image_tag` | `null` | tag de la imagen |
| `hosting_site_id` | `<project_id>-app` | Sitio de Firebase Hosting, tiene que ser único en todo Firebase |
| `max_instances` | `1` | Instancias máximas del backend |
| `jwt_secret_version` | `1` | Subirla genera una clave nueva |
| `repository_id`, `backend_service_name` | | Nombres, normalmente no hace falta cambiarlos |

## Outputs

- `backend_url`: va en `apiUrl` de `frontend/src/environments/environment.ts`. Se conoce antes de crear el backend porque Cloud Run usa una URL predecible por proyecto y región.
- `registry`: prefijo para etiquetar la imagen del backend.
- `hosting_site_id`: se usa en `firebase target:apply` al publicar el frontend.
- `frontend_url`: la URL pública de la app (`https://<sitio>.web.app`).
