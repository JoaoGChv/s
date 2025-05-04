"""
Atalhos para utilidades principais.
"""
from .config import DATASET_DIR, IMAGES_DIR, ANNOT_FILE, EXT_OK
from .annotations import AnnotationStore
from .image_ops import draw_annotations

__all__ = [
    "DATASET_DIR",
    "IMAGES_DIR",
    "ANNOT_FILE",
    "EXT_OK",
    "AnnotationStore",
    "draw_annotations",
]
