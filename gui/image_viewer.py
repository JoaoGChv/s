import tkinter as tk
from tkinter import ttk
from typing import Iterable
from PIL import Image, ImageTk

class ImageViewer(ttk.Frame):
    """Mostra imagem + legenda."""
    def __init__(self, master):
        super().__init__(master, padding=10)

        # imagem + legenda lado a lado
        self.img_label = ttk.Label(self)
        self.img_label.pack(side=tk.LEFT, anchor="nw")

        self.legend_frame = ttk.Frame(self)
        self.legend_frame.pack(side=tk.LEFT, anchor="nw", padx=12)

    # ----------------------------------------------------------
    def show_image(self, pil_img, tipos: Iterable[str], color_map: dict[str, str]):
        foto = ImageTk.PhotoImage(pil_img)
        self.img_label.config(image=foto)
        self.img_label.image = foto
        self._build_legend(tipos, color_map)

    # ----------------------------------------------------------
    def _build_legend(self, types, color_map):
        for w in self.legend_frame.winfo_children():
            w.destroy()
        if not types:
            ttk.Label(self.legend_frame, text="(sem anotações)").pack(anchor="w")
            return
        for t in sorted(types):
            row = ttk.Frame(self.legend_frame)
            box = tk.Canvas(row, width=14, height=14, highlightthickness=0)
            box.create_rectangle(0, 0, 14, 14,
                                 fill=color_map.get(t, "white"), outline="")
            box.pack(side=tk.LEFT)
            ttk.Label(row, text=f" {t}").pack(side=tk.LEFT)
            row.pack(anchor="w", pady=2)
