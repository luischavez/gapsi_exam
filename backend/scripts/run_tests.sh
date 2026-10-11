#!/bin/bash

docker compose exec backend pytest "$@"
