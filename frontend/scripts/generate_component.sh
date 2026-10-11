#!/bin/bash

docker compose exec frontend npx ng generate component "$1"
