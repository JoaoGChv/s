# miss_annotation

Ferramenta simples para anotar imagens usando uma interface Tkinter.

## Uso

1. De permissão de execução aos arquivos

```bash
chmod +x build.sh run.sh
```

2. Construa a imagem Docker:

```bash
./build.sh
```

3. Passe a permissão ao Docker:

```bash
xhost +local:docker
```
4. Rode a interface:

```bash
./run.sh
```

5. Execute o contêiner apontando para o diretório do seu dataset:

```bash
DATASET_PATH=/home/joao/Downloads/train ./run.sh
```

Em sistemas Windows utilizando WSL, utilize `run_wsl.sh` no lugar de `run.sh`.

O diretório indicado em `DATASET_PATH` deve conter pelo menos as pastas
`images/` e o arquivo `annotations.yaml`. Caso exista a pasta opcional
`Segmentations/`, ela será ignorada pela aplicação.

Certifique-se de que o diretório usado em `DATASET_PATH` está em um
local onde você tenha permissão de escrita, pois o contêiner precisa
alterar arquivos do dataset durante a anotação.

O dataset será montado dentro do contêiner em `/app/dataset`, permitindo
que a aplicação escreva nele.

## Treinamento

Scripts de treinamento independentes estão disponíveis em `training/`.

### YOLOe
```bash
python3 training/train_yoloe.py /caminho/para/dataset \
    --epochs 100 --batch 16 --img-size 640 --lr 0.01
```

### GroundingDINO
```bash
python3 training/train_groundingdino.py /caminho/para/dataset \
    --config config.py --epochs 30 --lr 1e-4
```