FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y python3-tk && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app.py /app/app.py

ENTRYPOINT ["python3", "/app/app.py"]
