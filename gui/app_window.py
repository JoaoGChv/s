import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from PIL import Image

from utils import IMAGES_DIR, EXT_OK, AnnotationStore, draw_annotations
from .sidebar import Sidebar
from .image_viewer import ImageViewer

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Visualizador de Imagens c/ Anotações")
        self.geometry("1000x700")

        # ---- dados -----------------------------------------------------
        self.images = sorted(p.name for p in IMAGES_DIR.iterdir()
                             if p.suffix.lower() in EXT_OK)
        if not self.images:
            messagebox.showerror("Erro", f"Nenhuma imagem em {IMAGES_DIR}")
            self.destroy(); return

        self.annos = AnnotationStore(Path(IMAGES_DIR.parent, "annotations.yaml"))

        # ---- UI --------------------------------------------------------
        self.sidebar = Sidebar(self, self.images, self._on_select)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.viewer = ImageViewer(self)
        self.viewer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # primeiro item
        self.sidebar.select_first()
        self._on_select(self.images[0])

    # ------------------------------------------------------------------
    def _on_select(self, filename: str):
        img_path = IMAGES_DIR / filename
        pil_img = Image.open(img_path).convert("RGB")
        tipos_presentes = draw_annotations(
            pil_img,
            self.annos.annos_for(filename),
            self.annos.color_map,
        )
        self.viewer.show_image(pil_img, tipos_presentes, self.annos.color_map)
