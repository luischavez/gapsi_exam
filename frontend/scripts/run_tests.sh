#!/bin/bash

docker compose exec frontend npx ng test --watch=false "$@"
