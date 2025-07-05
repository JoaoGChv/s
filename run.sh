#!/usr/bin/env bash
# run.sh

set -e

echo "Iniciando o container pytorch-tkinter-app"

# Caminho para o dataset no host. Pode ser definido via variável de ambiente
# DATASET_PATH; caso contrário, usa o diretório 'dataset' da raiz do repo.
DATASET_PATH=${DATASET_PATH:-"$(pwd)/dataset"}

docker run \
  --rm \
  -e DISPLAY=${DISPLAY} \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v "$(pwd)/app.py":/app/app.py:ro \
  -v "${DATASET_PATH}":/app/dataset \
  -v "$(pwd)/gui":/app/gui:ro \
  -v "$(pwd)/utils":/app/utils:ro \
  -w /app \
  pytorch-tkinter-app

