from pathlib import Path

DATASET_DIR = Path("/app/dataset")
IMAGES_DIR  = DATASET_DIR / "images"
ANNOT_FILE  = DATASET_DIR / "annotations.yaml"

EXT_OK = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tif", ".tiff"}
