from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import yaml
import colorsys

class AnnotationStore:
    _BASE_COLORS = [
        "red", "blue", "orange", "green", "magenta",
        "cyan", "yellow", "purple", "brown", "pink",
    ]

    def __init__(self, path: Path):
        self.path = path
        self.data: Dict[str, Any] = {}
        self.color_map: Dict[str, str] = {}
        self._load()

    # --------------------------------------------------
    def _load(self):
        if not self.path.exists():
            self.path.write_text("# Gerado automaticamente\nimages: {}\n",
                                 encoding="utf-8")
        with open(self.path, "r", encoding="utf-8") as f:
            self.data = yaml.safe_load(f) or {}

        self._build_color_map()

    # --------------------------------------------------
    def _build_color_map(self):
        """Gera o mapa de cores a partir do YAML (ou paleta automática)."""
        # 1. coleta todos os tipos + possíveis cores declaradas
        explicit = {}     # {tipo: cor do YAML}
        tipos = set()

        for rec in self.data.get("images", {}).values():
            for ann in rec.get("annotations", []):
                t = ann.get("type")
                if not t:
                    continue
                tipos.add(t)
                if "color" in ann:
                    explicit[t] = ann["color"]

        # 2. distribui cores:
        self.color_map = {}
        #   a) primeiro os definidos pelo YAML
        self.color_map.update(explicit)

        #   b) faltantes → usa paleta base, depois gera HSV → hex
        palette = list(self._BASE_COLORS)
        i = 0
        for t in sorted(tipos):
            if t in self.color_map:
                continue
            if i < len(palette):
                self.color_map[t] = palette[i]
            else:
                # gera cor em degraus de matiz
                h = (i * 0.12) % 1.0
                r, g, b = (int(c * 255) for c in colorsys.hsv_to_rgb(h, 0.85, 0.95))
                self.color_map[t] = f"#{r:02x}{g:02x}{b:02x}"
            i += 1

    # --------------------------------------------------
    def annos_for(self, fname: str) -> list[dict]:
        """Anotações da imagem (lista vazia se não houver)."""
        return self.data.get("images", {}).get(fname, {}).get("annotations", [])
    
    def add_annotation(self, filename: str, annotation_dict: Dict[str, Any]):
        """Adiciona uma anotação a uma imagem."""
        imgs = self.data.setdefault(filename, {})
        record = imgs.setdefault("annotations", [])
        annos = record.setdefault("annotations", [])
        annos.append(annotation_dict)

        ann_type = annotation_dict.get("type")
        if ann_type and (ann_type not in self.color_map or "color" in annotation_dict):
            self._build_color_map

    def save(self):
        """Grava o YAML atualizado em ``self.path``."""
        with open(self.path, "w", encoding="utf-8") as f:
            yaml.dump(self.data, f, allow_unicode=True)
