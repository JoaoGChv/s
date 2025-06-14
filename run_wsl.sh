#!/usr/bin/env bash
set -e

echo "Iniciando o container pytorch-tkinter-app com suporte a GUI"

# Detecta IP do servidor X no host Windows
HOST_IP=$(grep nameserver /etc/resolv.conf | awk '{print $2}')
export DISPLAY=${HOST_IP}:0

docker run \
  --rm \
  -e DISPLAY=${DISPLAY} \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v "$(pwd)/app.py":/app/app.py:ro \
  -v "$(pwd)/dataset":/app/dataset:ro \
  -v "$(pwd)/gui":/app/gui:ro \
  -v "$(pwd)/utils":/app/utils:ro \
  -w /app \
  pytorch-tkinter-app
