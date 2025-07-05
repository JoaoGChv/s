import tkinter as tk
from tkinter import ttk
from typing import Sequence, Callable

class ToolBar(ttk.Frame):
    """Barra de ferramentas com modos de desenho e seleção de classe."""
    def __init__(self,
                 master,
                 classes: Sequence[str],
                 change_mode: Callable[[str], None],
                 change_class: Callable[[str], None],
                 save_cb: Callable[[str], None],
                 add_class: Callable[[str], None]):
        super().__init__(master, padding=4)
        self._change_mode = change_mode
        self._change_class = change_class
        self._save_cb = save_cb
        self._add_class_cb = add_class

        # botoes de modo
        self.point_btn = ttk.Button(self, text="Point",
                                    command=lambda: change_mode("point"))
        self.bbox_btn = ttk.Button(self, text="Bounding Box",
                                   command=lambda: change_mode("bbox"))
        self.poly_btn = ttk.Button(self, text="Polígono",
                                   command=lambda: change_mode("polygon"))
        for b in (self.point_btn, self.bbox_btn, self.poly_btn):
            b.pack(side=tk.LEFT, padx=2)

        # seleção de classe
        self.class_combo = ttk.Combobox(self, state="readonly",
                                        values=list(classes))
        if classes:
            self.class_combo.current(0)
        self.class_combo.bind(
            "<<ComboboxSelected>>",
            lambda _e: self._change_class(self.class_combo.get()))
        self.class_combo.pack(side=tk.LEFT, padx=8)

        # campo nova classe
        self.new_class_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.new_class_var, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(self, text="Nova Classe", command=self._on_new_class).pack(side=tk.LEFT, padx=2)

        # botão salvar
        self.save_btn = ttk.Button(self, text="Salvar Anotações",
                                   command=self._save_cb, state=tk.DISABLED)
        self.save_btn.pack(side=tk.RIGHT, padx=4)

    # --------------------------------------------------------------
    def enable_save(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.save_btn.config(state=state)

    # --------------------------------------------------------------
    def _on_new_class(self):
        cls = self.new_class_var.get().strip()
        if not cls:
            return
        self._add_class_cb(cls)
        self.new_class_var.set("")

    # --------------------------------------------------------------
    def add_class(self, cls: str):
        values = list(self.class_combo['values'])
        if cls not in values:
            values.append(cls)
            self.class_combo['values'] = values
        self.class_combo.set(cls)