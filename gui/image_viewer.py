import tkinter as tk
from tkinter import ttk
from typing import Iterable, Callable, List, Tuple
from PIL import Image, ImageTk

Vector = List[Tuple[int, int]]

class ImageViewer(ttk.Frame):
    """Mostra imagem com legendas e permite desenhar anotações."""
    def __init__(self, master, on_new_annotation: Callable[[dict], None]):
        super().__init__(master, padding=10)

        # imagem + legenda lado a lado
        self.tool = "point"
        self._start = None
        self._current = None
        self._poly_points = []

        self.canvas.bind("Button-1>", self._on_click)
        self.canvas.bind("B1-Motion", self._on_drag)
        self.canvas.bind("ButtonRelease-1>", self._on_release)

        self.legend_frame = ttk.Frame(self)
        self.legend_frame.pack(side=tk.LEFT, anchor="nw", padx=12)

    # ----------------------------------------------------------
    def show_image(self, pil_img, tipos: Iterable[str], color_map: dict[str, str]):
        self.canvas.delete = ("all")
        foto = ImageTk.PhotoImage(pil_img)
        self.canvas.config(widht=foto.width(), height=foto.height())
        self.canvas.create_image(0, 0, image=foto, anchor="nw")
        self.canvas.image = foto 
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

    def _on_click(self, event):
        x, y =event.x, event.y
        if self.tool == "point":
            self._draw_point(x, y)
        elif self.tool == "bbox":
            self._start = (x, y)
            self._current = self._draw_bbox(x, y, x, y)
        elif self.tool == "polygon":
            self._poly_points[(x, y)]
            self._current = self.canvas.create_line(x, y, x, y, fill="red", width=2)
    
    def _on_grad(self, event):
        if self.tool == "bbox" and self._current:
            x0, y0 = self._start
            self._draw_bbox(x0, y0, event.x, event.y, item=self._current)
        elif self.tool == "polygon" and self._current:
            self._poly_points.append((event.x, event.y))
            coords = [c for pt in self._poly_points for c in pt]
            self.canvas.coords(self._current, *coords)
    
    def _on_release(self, event):
        if self.tool == "bbox" and self._current:
            x0, y0 = self._start
            self._draw_bbox(x0, y0, event.x, event.y, item=self._current)
            self._current = None
            self._start = None
        elif self.tool == "polygon" and self._current:
            self._poly_points.append((event.x, event.y))
            self.canvas.delete(self._current)
            self._draw_polygon(self._poly_points)
            self._poly_points = []
            self._current = None
    
    def _draw_point(self, x: int, y: int, color: str = "red"):
        r = 4
        return self.canvas.create_oval((x-r, y-r, x+r, y+r), outline=color, width=2)
    
    def _draw_bbox(self, x1: int, y1: int, x2: int, y2: int, color: str = "red", item: int | None = None):
        if item:
            self.canvas.coords(item, x1, y1, x2, y2)
            return item
        return self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=2)

    def _draw_polygon(self, points: list[tuple[int, int]], color: str = "red"):
        coords = [c for pt in points for c in pt]
        return self.canvas.create_polygon(*coords, outline=color, fill="", width=2)