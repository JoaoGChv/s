import tkinter as tk
from tkinter import ttk
from typing import Iterable, Callable, List, Tuple
from PIL import Image, ImageTk

Vector = List[Tuple[int, int]]

class ImageViewer(ttk.Frame):
    """Mostra imagem com legendas e permite desenhar anotações."""
    def __init__(self, master, on_new_annotation: Callable[[dict], None]):
        super().__init__(master, padding=10)
        self._on_new = on_new_annotation

        self.canvas = tk.Canvas(self, highlightthickness=0, cursor="cross")
        self.canvas.pack(side=tk.LEFT, anchor="nw")

        self.legend_frame = ttk.Frame(self)
        self.legend_frame.pack(side=tk.LEFT, anchor="nw", padx=12)

        self.tool = "point"
        self.current_class: str | None = None
        self.color_map: dict[str, str] = {}
        self._start: Tuple[int, int] | None = None
        self._current = None
        self._poly_points: Vector = []

        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

    # ----------------------------------------------------------
    def set_mode(self, mode: str):
        self.tool = mode

    def set_class(self, cls: str | None):
        self.current_class = cls

    # ----------------------------------------------------------
    def show_image(self, pil_img: Image.Image,
                   tipos: Iterable[str],
                   color_map: dict[str, str]):
        self.canvas.delete("all")
        foto = ImageTk.PhotoImage(pil_img)
        self.canvas.config(width=foto.width(), height=foto.height())
        self.canvas.create_image(0, 0, image=foto, anchor="nw")
        self.canvas.image = foto
        self.color_map = color_map
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

    # ----------------------------------------------------------
    def _current_color(self) -> str:
        if self.current_class:
            return self.color_map.get(self.current_class, "red")
        return "red"

    def _on_click(self, event):
        x, y = event.x, event.y
        if self.tool == "point":
            self._draw_point(x, y, self._current_color())
            if self.current_class:
                self._on_new({"type": self.current_class, "vector": [(x, y)], "in_image": True})
        elif self.tool == "bbox":
            self._start = (x, y)
            self._current = self._draw_bbox(x, y, x, y, self._current_color())
        elif self.tool == "polygon":
            self._poly_points = [(x, y)]
            self._current = self.canvas.create_line(x, y, x, y,
                                                    fill=self._current_color(), width=2)

    def _on_drag(self, event):
        if self.tool == "bbox" and self._current:
            x0, y0 = self._start
            self._draw_bbox(x0, y0, event.x, event.y, self._current_color(), item=self._current)
        elif self.tool == "polygon" and self._current:
            self._poly_points.append((event.x, event.y))
            coords = [c for pt in self._poly_points for c in pt]
            self.canvas.coords(self._current, *coords)

    def _on_release(self, event):
        if self.tool == "bbox" and self._current:
            x0, y0 = self._start
            self._draw_bbox(x0, y0, event.x, event.y, self._current_color(), item=self._current)
            if self.current_class:
                anno = {"type": self.current_class,
                        "vector": [(x0, y0), (event.x, event.y)],
                        "in_image": True}
                self._on_new(anno)
            self._current = None
            self._start = None
        elif self.tool == "polygon" and self._current:
            self._poly_points.append((event.x, event.y))
            self.canvas.delete(self._current)
            self._draw_polygon(self._poly_points, self._current_color())
            if self.current_class:
                self._on_new({"type": self.current_class,
                              "vector": self._poly_points.copy(),
                              "in_image": True})
            self._poly_points = []
            self._current = None

    # ----------------------------------------------------------
    def _draw_point(self, x: int, y: int, color: str = "red"):
        r = 4
        return self.canvas.create_oval((x - r, y - r, x + r, y + r), outline=color, width=2)

    def _draw_bbox(self, x1: int, y1: int, x2: int, y2: int, color: str = "red", item: int | None = None):
        if item:
            self.canvas.coords(item, x1, y1, x2, y2)
            self.canvas.itemconfigure(item, outline=color)
            return item
        return self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=2)

    def _draw_polygon(self, points: Vector, color: str = "red"):
        coords = [c for pt in points for c in pt]
        return self.canvas.create_polygon(*coords, outline=color, fill="", width=2)