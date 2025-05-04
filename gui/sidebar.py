import tkinter as tk
from tkinter import ttk
from typing import Callable, Sequence

class Sidebar(ttk.Frame):
    """Listbox de arquivos; emite callback quando o usuário seleciona."""
    def __init__(self, master, filenames: Sequence[str],
                 on_select: Callable[[str], None]):
        super().__init__(master, padding=8)
        self._on_select = on_select

        scroll = ttk.Scrollbar(self, orient="vertical")
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(
            self, width=28, height=30,
            listvariable=tk.StringVar(value=filenames),
            exportselection=False,
            yscrollcommand=scroll.set
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.config(command=self.listbox.yview)

        self.listbox.bind("<<ListboxSelect>>", self._clicked)

    # ----------------------------------------------------------
    def _clicked(self, _event):
        sel = self.listbox.curselection()
        if sel:
            self._on_select(self.listbox.get(sel[0]))

    # ----------------------------------------------------------
    def select_first(self):
        self.listbox.selection_set(0)
