#!/usr/bin/env bash
# build.sh

set -e

echo "Construindo a imagem Docker"
docker build -f docker/Dockerfile -t pytorch-tkinter-app .

