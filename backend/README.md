# Backend

API del Issue Tracker.

## Como correrlo

Se levanta desde la raíz del repo con `docker compose up`, junto con el emulador de Firestore. La API queda en http://localhost:9900

## Configuración

Todo se lee de variables de entorno (`app/config.py`).

| Variable | Default | |
|---|---|---|
| `JWT_SECRET_KEY` | — | Obligatoria. Clave para firmar los tokens |
| `JWT_ALGORITHM` | `HS256` | |
| `JWT_EXPIRE_MINUTES` | `30` | |
| `CORS_ORIGINS` | `["http://localhost:9901"]` | Lista en JSON con los orígenes del frontend |
| `GOOGLE_CLOUD_PROJECT` | — | Proyecto de Firestore |
| `FIRESTORE_EMULATOR_HOST` | — | Si existe, usa el emulador en lugar de Firestore real |

## Estructura

```
app/
  main.py         app, CORS y routers
  routers/        endpoints (auth, issues)
  services/       consultas a Firestore
  schemas/        modelos de entrada y salida
  internal/       hash de contraseñas (Argon2) y JWT
  dependencies.py cliente de Firestore y usuario de la sesión
scripts/
  seed.py         usuarios e incidencias de prueba
  run_seeds.sh
  run_tests.sh
tests/
```

Los endpoints solo validan y responden; las consultas a Firestore viven en `services/`.

## Datos de prueba

`scripts/seed.py` crea los usuarios `user1` / `demo_user1pass` y `user2` / `demo_user2pass`, y 50 incidencias con prioridad, estado y autor al azar. Corre solo al levantar el compose; para repetirlo:

```bash
./scripts/run_seeds.sh
```

## Tests

```bash
./scripts/run_tests.sh
```

Usan el emulador de firestore con un proyecto aparte (`gapsi-exam-test`) y vacían la base antes de cada prueba.

## Postman

La colección es `postman_collection.json`. Correr primero `Auth > Login`, que guarda el token para las demás peticiones.
