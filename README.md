# miss_annotation

Ferramenta simples para anotar imagens usando uma interface Tkinter.

## Uso

1. Construa a imagem Docker:

```bash
./build.sh
```

2. Execute o contêiner apontando para o diretório do seu dataset:

```bash
DATASET_PATH=/home/joao/Downloads/train ./run.sh
```

Em sistemas Windows utilizando WSL, utilize `run_wsl.sh` no lugar de `run.sh`.

O diretório indicado em `DATASET_PATH` deve conter pelo menos as pastas
`images/` e o arquivo `annotations.yaml`. Caso exista a pasta opcional
`Segmentations/`, ela será ignorada pela aplicação.

O dataset será montado dentro do contêiner em `/app/dataset`.
