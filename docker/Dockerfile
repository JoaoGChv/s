FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

# Evita prompts interativos e instala tkinter
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y python3-tk && \
    rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho e copia o app
WORKDIR /app
COPY app.py /app/app.py

# Ao iniciar o container, executa o app.py
ENTRYPOINT ["python3", "/app/app.py"]
