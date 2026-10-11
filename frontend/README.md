# Frontend

Cliente del Issue Tracker en Angular 22

## Como correrlo

Se levanta desde la raíz del repo con `docker compose up`. url: http://localhost:9901

## URL de la API

Está en `src/environments/`:

- `environment.development.ts`: dev local
- `environment.ts`: produccion

## Estructura

```
src/app/
  core/auth/        AuthService, interceptor que agrega el JWT y guards
  layout/shell/     encabezado y contenedor de las páginas con sesión
  features/
    login/
    issues/
      issue-list/     lista, filtros, cambio de estado/prioridad y paginación
      issue-summary/  totales por estado
      issue-form/     alta de incidencias
      issues.service.ts
      issue.models.ts
```

Todas las páginas se cargan con lazy loading. Las rutas de incidencias están en `features/issues/issues.routes.ts`

Si el backend responde 401 (token vencido o inválido), el interceptor cierra la sesión y regresa al login.

## Tests

```bash
./scripts/run_tests.sh
```

## Producción

Deploy a Firebase Hosting.

```bash
npm run build
npx firebase-tools deploy --only hosting:app --project <proyecto>
```

La primera vez hay que asociar el target `app` al sitio; los pasos completos están en el [README principal](../README.md#despliegue-en-gcp).
