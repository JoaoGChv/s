#!/usr/bin/env bash
# run.sh

set -e

echo "Iniciando o container pytorch-tkinter-app"
docker run \
  --rm \
  -e DISPLAY=${DISPLAY} \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v "$(pwd)/app.py":/app/app.py:ro \
  -v "$(pwd)/dataset":/app/dataset:ro \
  -w /app \
  pytorch-tkinter-app

