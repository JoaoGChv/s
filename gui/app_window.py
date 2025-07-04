import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from PIL import Image
import threading
import subprocess
import queue

from utils import DATASET_DIR, IMAGES_DIR, EXT_OK, AnnotationStore, draw_annotations

from utils import IMAGES_DIR, EXT_OK, AnnotationStore, draw_annotations
from .sidebar import Sidebar
from .image_viewer import ImageViewer
from .toolbar import ToolBar


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
        classes = sorted(self.annos.color_map.keys())
        self.toolbar = ToolBar(self, classes,
                               self._change_mode,
                               self._change_class,
                               self._save_annotations,
                               self._add_class)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self.sidebar = Sidebar(self, self.images, self._on_select)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.viewer = ImageViewer(self, self._new_annotation)
        self.viewer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_training_ui()

        self.current_file = None
        self._change_class(classes[0] if classes else None)

        # primeiro item
        self.sidebar.select_first()
        self._on_select(self.images[0])

        self.training_thread = None
        self.training_proc = None
        self.log_queue = queue.Queue()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _change_mode(self, mode: str):
        self.viewer.set_mode(mode)

    def _change_class(self, cls: str | None):
        if cls:
            self.viewer.set_class(cls)
        self.current_class = cls
    
    def _add_class(self, cls: str):
        self.annos.add_class(cls)
        self.toolbar.add_class(cls)
        self._change_class(cls)

    def _new_annotation(self, anno: dict):
        if not self.current_file:
            return
        self.annos.add_annotation(self.current_file, anno)
        self.annos.save()
        self.toolbar.enable_save(True)
        # atualiza visualização para incluir nova anotação
        self._on_select(self.current_file)

    def _save_annotations(self):
        self.annos.save()
        self.toolbar.enable_save(False)
    
    def _on_select(self, fname: str):
        self.current_file = fname
        img_path = IMAGES_DIR / fname
        try:
            img = Image.open(img_path)
        except Exception as exc:
            messagebox.showerror("Erro", f"Falha ao abrir {img_path}: {exc}")
            return
        tipos = draw_annotations(img, self.annos.annos_for(fname), self.annos.color_map)
        self.viewer.show_image(img, tipos, self.annos.color_map)

    # --------------------------------------------------------------
    def _build_training_ui(self):
        frame = ttk.LabelFrame(self, text="Treinamento", padding=8)
        frame.pack(side=tk.BOTTOM, fill=tk.X)

        controls = ttk.Frame(frame)
        controls.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(controls, text="Modelo:").pack(side=tk.LEFT)
        self.model_var = tk.StringVar(value="YOLOe")
        self.model_combo = ttk.Combobox(
            controls, state="readonly",
            values=["YOLOe", "GroundingDINO"],
            textvariable=self.model_var, width=15
        )
        self.model_combo.pack(side=tk.LEFT, padx=4)

        ttk.Label(controls, text="Epochs:").pack(side=tk.LEFT)
        self.epochs_var = tk.IntVar(value=10)
        ttk.Entry(controls, textvariable=self.epochs_var, width=6).pack(side=tk.LEFT, padx=4)

        ttk.Label(controls, text="Batch:").pack(side=tk.LEFT)
        self.batch_var = tk.IntVar(value=16)
        ttk.Entry(controls, textvariable=self.batch_var, width=6).pack(side=tk.LEFT, padx=4)

        self.train_btn = ttk.Button(controls, text="Iniciar Treinamento", command=self._start_training)
        self.train_btn.pack(side=tk.LEFT, padx=8)

        self.log_text = tk.Text(frame, height=8)
        self.log_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=6)
        self.log_text.config(state=tk.DISABLED)

    # --------------------------------------------------------------
    def _build_training_command(self) -> list[str]:
        root = Path(__file__).resolve().parent.parent
        model = self.model_var.get()
        if model == "YOLOe":
            script = root / "training" / "train_yoloe.py"
            return ["python", "-u", str(script), str(DATASET_DIR),
                    "--epochs", str(self.epochs_var.get()),
                    "--batch", str(self.batch_var.get())]
        else:
            script = root / "training" / "train_groundingdino.py"
            return ["python", "-u", str(script), str(DATASET_DIR),
                    "--epochs", str(self.epochs_var.get())]

    # --------------------------------------------------------------
    def _start_training(self):
        if self.training_thread and self.training_thread.is_alive():
            messagebox.showwarning("Treinamento", "Treinamento já em andamento.")
            return
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

        cmd = self._build_training_command()
        self.training_thread = threading.Thread(target=self._run_training, args=(cmd,), daemon=True)
        self.training_thread.start()
        self.after(100, self._poll_log_queue)

    # --------------------------------------------------------------
    def _run_training(self, cmd: list[str]):
        self.training_proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1
        )
        assert self.training_proc.stdout is not None
        for line in self.training_proc.stdout:
            self.log_queue.put(line)
        self.training_proc.wait()
        self.log_queue.put("Treinamento concluído.\n")

    # --------------------------------------------------------------
    def _poll_log_queue(self):
        while True:
            try:
                line = self.log_queue.get_nowait()
            except queue.Empty:
                break
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, line)
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)

        if self.training_thread and self.training_thread.is_alive():
            self.after(100, self._poll_log_queue)
        else:
            if self.training_thread:
                self.training_thread.join()
                self.training_thread = None

    # --------------------------------------------------------------
    def _on_close(self):
        if self.training_thread and self.training_thread.is_alive():
            self.training_thread.join()
        self.destroy()
