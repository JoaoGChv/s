#!/usr/bin/env bash
set -e

echo "Iniciando o container pytorch-tkinter-app com suporte a GUI"

# Caminho para o dataset no host. Defina a variável DATASET_PATH para usar um
# diretório diferente. Se não definido, assume 'dataset' dentro do repo.
DATASET_PATH=${DATASET_PATH:-"$(pwd)/dataset"}

# Detecta IP do servidor X no host Windows
HOST_IP=$(grep nameserver /etc/resolv.conf | awk '{print $2}')
export DISPLAY=${HOST_IP}:0

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
