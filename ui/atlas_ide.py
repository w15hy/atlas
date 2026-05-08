"""Atlas IDE — Interfaz grafica para el ecosistema SPL + VM Atlas.

Cinco paneles muestran cada fase del pipeline (.atl, .pre, .asm, .binReloc, .bin),
una zona en vivo refleja registros, flags y buses, y una shell muestra la
salida de las instrucciones OUT y el inspector mem>.

Ejecutar:
    python -m ui.atlas_ide
o:
    python ui/atlas_ide.py
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import queue
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

# ── Paths ────────────────────────────────────────────────────────────────
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_THIS_DIR, ".."))
_SPL_DIR = os.path.join(_ROOT, "SPL")
_PROGRAMS_DIR = os.path.join(_SPL_DIR, "programs")

for _p in (_ROOT, _SPL_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def _load_pipeline():
    """Carga SPL/pipeline.py como modulo independiente (no hay SPL/__init__.py)."""
    path = os.path.join(_SPL_DIR, "pipeline.py")
    spec = importlib.util.spec_from_file_location("atlas_pipeline", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pipeline = _load_pipeline()

from CPU.cpu import CPU  # noqa: E402
from CPU.ram import RAM  # noqa: E402
from CPU import instructions as _cpu_instr  # noqa: E402


# ── Constantes UI ────────────────────────────────────────────────────────
COLOR_BG = "#1e1e2e"
COLOR_PANEL = "#2a2a3e"
COLOR_TEXT = "#dcdcdc"
COLOR_ACCENT = "#7aa2f7"
COLOR_ACCENT2 = "#bb9af7"
COLOR_OK = "#9ece6a"
COLOR_ERR = "#f7768e"
COLOR_DIM = "#565f89"
FONT_MONO = ("Consolas", 9)
FONT_MONO_SMALL = ("Consolas", 8)
FONT_BOLD = ("Segoe UI", 9, "bold")
FONT_NORMAL = ("Segoe UI", 9)


# ── Stream que envia salida a una cola (thread-safe) ─────────────────────
class _QueueWriter:
    def __init__(self, q: "queue.Queue[str]"):
        self.q = q

    def write(self, s):
        if s:
            self.q.put(s)
        return len(s) if s else 0

    def flush(self):
        pass


# ─────────────────────────────────────────────────────────────────────────
class CodePanel(ttk.Frame):
    """Panel con titulo, area de texto monoespaciada y barra de scroll."""

    def __init__(self, master, title: str, *, editable: bool = False):
        super().__init__(master, style="Panel.TFrame")
        self.title_var = tk.StringVar(value=title)
        header = ttk.Label(self, textvariable=self.title_var, style="PanelHeader.TLabel")
        header.pack(fill="x", padx=4, pady=(2, 2))

        self.text = scrolledtext.ScrolledText(
            self,
            wrap="none",
            font=FONT_MONO,
            bg=COLOR_PANEL,
            fg=COLOR_TEXT,
            insertbackground=COLOR_TEXT,
            relief="flat",
            borderwidth=0,
            undo=True,
        )
        self.text.pack(fill="both", expand=True, padx=2, pady=(0, 2))
        self.editable = editable
        if not editable:
            self.text.config(state="disabled")

    def set_content(self, text: str, *, info: str | None = None):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", text)
        if not self.editable:
            self.text.config(state="disabled")
        if info is not None:
            base = self.title_var.get().split("  —")[0]
            self.title_var.set(f"{base}  —  {info}")

    def get_content(self) -> str:
        return self.text.get("1.0", "end-1c")

    def clear(self):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        if not self.editable:
            self.text.config(state="disabled")


# ─────────────────────────────────────────────────────────────────────────
class RegistersPanel(ttk.Frame):
    """Vista en vivo de registros generales, especiales, flags y buses."""

    def __init__(self, master):
        super().__init__(master, style="Panel.TFrame")
        ttk.Label(self, text="Estado de la maquina", style="PanelHeader.TLabel").pack(
            fill="x", padx=4, pady=(2, 2)
        )

        body = ttk.Frame(self, style="Panel.TFrame")
        body.pack(fill="both", expand=True, padx=4, pady=(0, 4))

        # Cabecera con paso e instruccion
        self.step_var = tk.StringVar(value="Paso #0")
        self.instr_var = tk.StringVar(value="—")
        ttk.Label(body, textvariable=self.step_var, font=FONT_BOLD,
                  background=COLOR_PANEL, foreground=COLOR_ACCENT).pack(anchor="w")
        ttk.Label(body, textvariable=self.instr_var, font=FONT_MONO_SMALL,
                  background=COLOR_PANEL, foreground=COLOR_ACCENT2,
                  wraplength=240, justify="left").pack(anchor="w", pady=(0, 6))

        # Registros R0..R15
        regs_box = tk.LabelFrame(body, text=" Registros generales ", bg=COLOR_PANEL,
                                 fg=COLOR_DIM, font=FONT_NORMAL, bd=1, relief="solid")
        regs_box.pack(fill="x", pady=2)
        self.reg_vars: list[tk.StringVar] = []
        grid = tk.Frame(regs_box, bg=COLOR_PANEL)
        grid.pack(fill="x", padx=4, pady=2)
        for i in range(16):
            var = tk.StringVar(value=f"R{i:<2}: 0x{0:016X}")
            self.reg_vars.append(var)
            row = i % 8
            col = i // 8
            tk.Label(grid, textvariable=var, font=FONT_MONO_SMALL,
                     bg=COLOR_PANEL, fg=COLOR_TEXT, anchor="w",
                     width=24).grid(row=row, column=col, sticky="w", padx=2)

        # Especiales
        sp_box = tk.LabelFrame(body, text=" Registros especiales ", bg=COLOR_PANEL,
                               fg=COLOR_DIM, font=FONT_NORMAL, bd=1, relief="solid")
        sp_box.pack(fill="x", pady=2)
        self.pc_var = tk.StringVar(value="PC: 0x00000000")
        self.sp_var = tk.StringVar(value="SP: 0x00000000")
        self.ir_var = tk.StringVar(value="IR: " + "0" * 64)
        for var in (self.pc_var, self.sp_var, self.ir_var):
            tk.Label(sp_box, textvariable=var, font=FONT_MONO_SMALL,
                     bg=COLOR_PANEL, fg=COLOR_TEXT, anchor="w").pack(fill="x", padx=4)

        # Flags
        fl_box = tk.LabelFrame(body, text=" Flags ", bg=COLOR_PANEL, fg=COLOR_DIM,
                               font=FONT_NORMAL, bd=1, relief="solid")
        fl_box.pack(fill="x", pady=2)
        self.flag_vars = {k: tk.StringVar(value=f"{k}=0") for k in ("Z", "C", "N", "V")}
        fl_grid = tk.Frame(fl_box, bg=COLOR_PANEL)
        fl_grid.pack(fill="x", padx=4, pady=2)
        for i, k in enumerate(("Z", "C", "N", "V")):
            tk.Label(fl_grid, textvariable=self.flag_vars[k], font=FONT_MONO_SMALL,
                     bg=COLOR_PANEL, fg=COLOR_TEXT, width=6,
                     anchor="w").grid(row=0, column=i, sticky="w", padx=2)

        # Buses
        bus_box = tk.LabelFrame(body, text=" Buses ", bg=COLOR_PANEL, fg=COLOR_DIM,
                                font=FONT_NORMAL, bd=1, relief="solid")
        bus_box.pack(fill="x", pady=2)
        self.bus_addr_var = tk.StringVar(value="Address: 0x00000000")
        self.bus_data_var = tk.StringVar(value="Data:    0x" + "0" * 16)
        self.bus_ctrl_var = tk.StringVar(value="Control: —")
        for var in (self.bus_addr_var, self.bus_data_var, self.bus_ctrl_var):
            tk.Label(bus_box, textvariable=var, font=FONT_MONO_SMALL,
                     bg=COLOR_PANEL, fg=COLOR_TEXT, anchor="w").pack(fill="x", padx=4)

    def update_from_cpu(self, cpu: CPU):
        reg = cpu.reg
        self.step_var.set(f"Paso #{cpu.step_count}")
        try:
            instr = cpu._instr_name()
        except Exception:
            instr = "—"
        self.instr_var.set(f"Instr: {instr}")
        for i in range(16):
            v = reg.get_reg(i)
            self.reg_vars[i].set(f"R{i:<2}: 0x{v:016X}  ({v:>12d})")
        self.pc_var.set(f"PC: 0x{reg.PC:08X}  ({reg.PC})")
        self.sp_var.set(f"SP: 0x{reg.SP:08X}  ({reg.SP})")
        ir = reg.IR
        self.ir_var.set(f"IR: {ir}")
        flags = reg.get_flags()
        for k, v in flags.items():
            self.flag_vars[k].set(f"{k}={1 if v else 0}")
        b = cpu.buses
        self.bus_addr_var.set(f"Address: 0x{b.address_bus.get_address():08X}")
        self.bus_data_var.set(f"Data:    0x{b.data_bus.read_data():016X}")
        sigs = b.control_bus.get_signals()
        self.bus_ctrl_var.set(
            "Control: " + " ".join(f"{k}={1 if v else 0}" for k, v in sigs.items())
        )


# ─────────────────────────────────────────────────────────────────────────
class ShellPanel(ttk.Frame):
    """Shell con la salida de OUT y respuestas del inspector mem>."""

    def __init__(self, master):
        super().__init__(master, style="Panel.TFrame")
        ttk.Label(self, text="Shell — OUT del programa / mem>",
                  style="PanelHeader.TLabel").pack(fill="x", padx=4, pady=(2, 2))
        self.text = scrolledtext.ScrolledText(
            self,
            wrap="word",
            font=FONT_MONO,
            bg="#11111b",
            fg=COLOR_TEXT,
            insertbackground=COLOR_TEXT,
            relief="flat",
            borderwidth=0,
        )
        self.text.pack(fill="both", expand=True, padx=2, pady=(0, 2))
        self.text.tag_config("out", foreground=COLOR_OK)
        self.text.tag_config("err", foreground=COLOR_ERR)
        self.text.tag_config("info", foreground=COLOR_ACCENT)
        self.text.tag_config("dim", foreground=COLOR_DIM)
        self.text.config(state="disabled")

    def append(self, text: str, tag: str | None = None):
        self.text.config(state="normal")
        if tag:
            self.text.insert("end", text, tag)
        else:
            # Auto-tag para [OUT]
            if "[OUT]" in text:
                self.text.insert("end", text, "out")
            elif "[ERROR]" in text or "[!]" in text:
                self.text.insert("end", text, "err")
            else:
                self.text.insert("end", text)
        self.text.see("end")
        self.text.config(state="disabled")

    def clear(self):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.config(state="disabled")


# ─────────────────────────────────────────────────────────────────────────
class AtlasIDE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Atlas IDE — SPL + VM")
        self.geometry("1600x980")
        self.configure(bg=COLOR_BG)
        self.minsize(1100, 720)

        self._setup_styles()

        # Estado
        self.atl_path: str | None = None
        self.bin_path: str | None = None
        self.binreloc_path: str | None = None
        self.asm_path: str | None = None
        self.pre_path: str | None = None
        self.cpu: CPU | None = None
        self.ram: RAM | None = None
        self.exec_thread: threading.Thread | None = None
        self.exec_stop_flag = threading.Event()
        self.io_queue: "queue.Queue[str]" = queue.Queue()
        self.bin_base_addr = 0
        self.bin_bytes: list[str] = []

        self._build_top_bar()
        self._build_main_area()

        self.after(60, self._poll_io_queue)

    # ── Estilos ────────────────────────────────────────────────────────
    def _setup_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TFrame", background=COLOR_BG)
        style.configure("Panel.TFrame", background=COLOR_PANEL,
                        borderwidth=1, relief="solid")
        style.configure("Top.TFrame", background=COLOR_BG)
        style.configure("PanelHeader.TLabel", background=COLOR_PANEL,
                        foreground=COLOR_ACCENT, font=FONT_BOLD,
                        anchor="w")
        style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT,
                        font=FONT_NORMAL)
        style.configure("Top.TLabel", background=COLOR_BG,
                        foreground=COLOR_TEXT, font=FONT_NORMAL)
        style.configure("Tag.TLabel", background=COLOR_BG,
                        foreground=COLOR_DIM, font=FONT_NORMAL)
        style.configure("TButton", font=FONT_NORMAL, padding=(10, 4))
        style.map("TButton",
                  background=[("active", COLOR_ACCENT)],
                  foreground=[("active", COLOR_BG)])
        style.configure("Accent.TButton", font=FONT_BOLD,
                        background=COLOR_ACCENT, foreground=COLOR_BG)
        style.configure("Run.TButton", font=FONT_BOLD,
                        background=COLOR_OK, foreground=COLOR_BG)
        style.configure("TEntry", fieldbackground=COLOR_PANEL,
                        foreground=COLOR_TEXT, insertcolor=COLOR_TEXT)
        style.configure("TCombobox", fieldbackground=COLOR_PANEL,
                        foreground=COLOR_TEXT)

    # ── Toolbar ────────────────────────────────────────────────────────
    def _build_top_bar(self):
        bar = ttk.Frame(self, style="Top.TFrame")
        bar.pack(side="top", fill="x", padx=8, pady=6)

        ttk.Label(bar, text="Atlas IDE", style="Top.TLabel",
                  font=("Segoe UI", 12, "bold"), foreground=COLOR_ACCENT
                  ).pack(side="left", padx=(0, 14))

        ttk.Label(bar, text=".org:", style="Top.TLabel").pack(side="left")
        self.org_var = tk.StringVar(value="0x0000")
        self.org_entry = ttk.Entry(bar, textvariable=self.org_var, width=10,
                                   font=FONT_MONO)
        self.org_entry.pack(side="left", padx=(4, 14))
        # Al confirmar (Enter) o salir del campo, recompilamos con el nuevo .org.
        self.org_entry.bind("<Return>", lambda _e: self._on_org_changed())
        self.org_entry.bind("<FocusOut>", lambda _e: self._on_org_changed())
        self._last_org_compiled: int | None = None

        ttk.Button(bar, text="Cargar archivo", command=self.on_load_file
                   ).pack(side="left", padx=2)
        ttk.Button(bar, text="Compilar", command=self.on_compile,
                   style="Accent.TButton").pack(side="left", padx=2)

        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y",
                                                    padx=10, pady=4)

        ttk.Label(bar, text="Modo:", style="Top.TLabel").pack(side="left")
        self.mode_var = tk.StringVar(value="Completo")
        mode_cb = ttk.Combobox(
            bar, textvariable=self.mode_var,
            values=("Completo", "Paso a paso", "PaP temporizado"),
            state="readonly", width=18, font=FONT_NORMAL,
        )
        mode_cb.pack(side="left", padx=(4, 6))

        ttk.Label(bar, text="Delay (s):", style="Top.TLabel").pack(side="left")
        self.delay_var = tk.StringVar(value="0.5")
        ttk.Entry(bar, textvariable=self.delay_var, width=6,
                  font=FONT_MONO).pack(side="left", padx=(4, 14))

        self.run_btn = ttk.Button(bar, text="Ejecutar", command=self.on_execute,
                                  style="Run.TButton")
        self.run_btn.pack(side="left", padx=2)
        self.step_btn = ttk.Button(bar, text="Step", command=self.on_step)
        self.step_btn.pack(side="left", padx=2)
        ttk.Button(bar, text="Detener", command=self.on_stop
                   ).pack(side="left", padx=2)
        ttk.Button(bar, text="Reset VM", command=self.on_reset_vm
                   ).pack(side="left", padx=2)

        self.status_var = tk.StringVar(value="Listo. Carga un archivo .atl para comenzar.")
        ttk.Label(bar, textvariable=self.status_var, style="Tag.TLabel",
                  foreground=COLOR_DIM).pack(side="right", padx=4)

    # ── Area principal ─────────────────────────────────────────────────
    def _build_main_area(self):
        # Layout en grid: 4 columnas x 2 filas para los paneles + sidebar a la derecha + shell + mem>
        container = ttk.Frame(self, style="TFrame")
        container.pack(side="top", fill="both", expand=True, padx=8, pady=(0, 4))

        for c in range(4):
            container.grid_columnconfigure(c, weight=1, uniform="cols")
        container.grid_columnconfigure(3, weight=1, uniform="cols",
                                       minsize=290)
        container.grid_rowconfigure(0, weight=3, uniform="rows")
        container.grid_rowconfigure(1, weight=3, uniform="rows")
        container.grid_rowconfigure(2, weight=2, uniform="rows")

        # Fila 0
        self.atl_panel = CodePanel(container, "1. Codigo fuente (.atl)",
                                   editable=True)
        self.atl_panel.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.pre_panel = CodePanel(container, "2. Preprocesado (.pre)")
        self.pre_panel.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        self.asm_panel = CodePanel(container, "3. Ensamblado (.asm)")
        self.asm_panel.grid(row=0, column=2, sticky="nsew", padx=2, pady=2)

        # Sidebar de registros (rowspan 2)
        self.regs_panel = RegistersPanel(container)
        self.regs_panel.grid(row=0, column=3, rowspan=2, sticky="nsew",
                             padx=2, pady=2)

        # Fila 1
        self.binreloc_panel = CodePanel(container, "4. Reubicable (.binReloc)")
        self.binreloc_panel.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        self.bin_panel = CodePanel(container, "5. Binario final (.bin)")
        self.bin_panel.grid(row=1, column=1, sticky="nsew", padx=2, pady=2)

        # Build log (donde pipeline.run() escribe sus mensajes)
        self.build_log = CodePanel(container, "Log de compilacion / sistema")
        self.build_log.grid(row=1, column=2, sticky="nsew", padx=2, pady=2)

        # Fila 2: shell ocupando casi todo, sidebar sigue cubierto por regs
        shell_wrap = ttk.Frame(container, style="TFrame")
        shell_wrap.grid(row=2, column=0, columnspan=3, sticky="nsew",
                        padx=2, pady=2)
        shell_wrap.grid_rowconfigure(0, weight=1)
        shell_wrap.grid_columnconfigure(0, weight=1)
        self.shell = ShellPanel(shell_wrap)
        self.shell.grid(row=0, column=0, sticky="nsew")

        # Cuadro mem> debajo del shell
        mem_bar = ttk.Frame(shell_wrap, style="TFrame")
        mem_bar.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        ttk.Label(mem_bar, text="mem>", style="Top.TLabel",
                  foreground=COLOR_ACCENT2,
                  font=("Consolas", 10, "bold")).pack(side="left", padx=(2, 4))
        self.mem_var = tk.StringVar()
        self.mem_entry = ttk.Entry(mem_bar, textvariable=self.mem_var,
                                   font=FONT_MONO)
        self.mem_entry.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.mem_entry.bind("<Return>", lambda _e: self.on_mem_inspect())
        ttk.Button(mem_bar, text="Inspeccionar", command=self.on_mem_inspect
                   ).pack(side="left", padx=2)
        ttk.Button(mem_bar, text="Limpiar shell", command=self.shell.clear
                   ).pack(side="left", padx=2)
        ttk.Label(mem_bar, text="(formatos: 0x400, 1024, 0b1000... · agrega +N)",
                  style="Tag.TLabel").pack(side="left", padx=(8, 0))

        # En la columna 3 (sidebar) en la fila 2, mostramos un panel de
        # informacion sobre el binario cargado.
        info_box = tk.LabelFrame(container, text=" Carga de binario ",
                                 bg=COLOR_PANEL, fg=COLOR_DIM,
                                 font=FONT_NORMAL, bd=1, relief="solid")
        info_box.grid(row=2, column=3, sticky="nsew", padx=2, pady=2)
        self.bin_info_var = tk.StringVar(
            value="Sin binario cargado.\nCompila un .atl para producirlo."
        )
        tk.Label(info_box, textvariable=self.bin_info_var, font=FONT_MONO_SMALL,
                 bg=COLOR_PANEL, fg=COLOR_TEXT, anchor="nw", justify="left",
                 wraplength=270).pack(fill="both", expand=True, padx=6, pady=6)

    # ── Cola de IO (recoge stdout redirigido) ──────────────────────────
    def _poll_io_queue(self):
        try:
            while True:
                chunk = self.io_queue.get_nowait()
                self.shell.append(chunk)
        except queue.Empty:
            pass
        # Si el thread de ejecucion terminó, refrescamos registros una vez mas
        if self.exec_thread and not self.exec_thread.is_alive():
            self.exec_thread = None
            if self.cpu is not None:
                self.regs_panel.update_from_cpu(self.cpu)
            self._set_status("Ejecucion finalizada.")
        self.after(60, self._poll_io_queue)

    def _set_status(self, msg: str):
        self.status_var.set(msg)

    # ── Carga de archivo .atl ──────────────────────────────────────────
    def on_load_file(self):
        initial = _PROGRAMS_DIR if os.path.isdir(_PROGRAMS_DIR) else _ROOT
        path = filedialog.askopenfilename(
            title="Selecciona un archivo .atl",
            initialdir=initial,
            filetypes=[("Atlas SPL", "*.atl"), ("Todos", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                source = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")
            return
        self.atl_path = path
        self.atl_panel.set_content(source, info=os.path.basename(path))
        self.pre_panel.clear()
        self.asm_panel.clear()
        self.binreloc_panel.clear()
        self.bin_panel.clear()
        self.build_log.clear()
        self._set_status(f"Archivo cargado: {os.path.basename(path)}")

    # ── Compilacion ────────────────────────────────────────────────────
    def on_compile(self):
        if not self.atl_path:
            messagebox.showwarning("Atlas IDE",
                                   "Carga primero un archivo .atl.")
            return
        # Si el usuario edito el panel 1, lo guardamos antes de compilar
        try:
            edited = self.atl_panel.get_content()
            with open(self.atl_path, "r", encoding="utf-8") as f:
                disk = f.read()
            if edited != disk:
                with open(self.atl_path, "w", encoding="utf-8") as f:
                    f.write(edited)
        except Exception as e:
            messagebox.showerror("Error",
                                 f"No se pudo guardar el .atl editado:\n{e}")
            return

        # Parsear .org antes de compilar; si es invalido, abortamos
        try:
            org = self._parse_org()
        except ValueError as e:
            messagebox.showerror("Atlas IDE", str(e))
            return

        self.build_log.clear()
        self.pre_panel.clear()
        self.asm_panel.clear()
        self.binreloc_panel.clear()
        self.bin_panel.clear()
        self._set_status(f"Compilando con .org = 0x{org:04X}...")
        self.update_idletasks()

        # Capturamos prints del pipeline
        log_buf = io.StringIO()
        ok = False
        bin_path = None
        try:
            with contextlib.redirect_stdout(log_buf), contextlib.redirect_stderr(log_buf):
                bin_path = pipeline.run(self.atl_path, org=org)
            ok = bin_path is not None
        except Exception as e:
            log_buf.write(f"\n[EXCEPCION] {e}\n")
            ok = False

        self.build_log.set_content(log_buf.getvalue())

        if not ok:
            self._set_status("Compilacion fallida.")
            self.shell.append("\n[ERROR] Falla en compilacion. Ver log.\n", "err")
            return

        self.bin_path = bin_path
        basename = os.path.splitext(os.path.basename(bin_path))[0]
        build_dir = os.path.dirname(bin_path)
        self.pre_path = os.path.join(build_dir, f"{basename}.pre")
        self.asm_path = os.path.join(build_dir, f"{basename}.asm")
        self.binreloc_path = os.path.join(build_dir, f"{basename}.binReloc")

        # Cargar contenidos a los paneles
        for panel, path in (
            (self.pre_panel, self.pre_path),
            (self.asm_panel, self.asm_path),
            (self.binreloc_panel, self.binreloc_path),
            (self.bin_panel, self.bin_path),
        ):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                panel.set_content(content, info=os.path.basename(path))
            except Exception as e:
                panel.set_content(f"[!] No se pudo leer {path}\n{e}")

        # Cargar el .bin para tener self.bin_bytes / bin_base_addr listos.
        # Solo reescribimos org_var si difiere del valor del usuario,
        # para preservar el formato (hex/dec) que tecleo.
        try:
            base = self._read_bin(self.bin_path)
            try:
                user_val = int(self.org_var.get().strip() or "0", 0)
            except ValueError:
                user_val = None
            if user_val != base:
                self.org_var.set(f"0x{base:04X}")
            self._last_org_compiled = base
        except Exception:
            pass

        self._set_status(
            f"Compilado OK -> {os.path.basename(bin_path)}  (.org=0x{org:04X})"
        )

    def _on_org_changed(self):
        """Disparado por <Return> o <FocusOut> sobre el campo .org.

        Si el valor cambio respecto al ultimo compilado y hay un .atl
        cargado, dispara una recompilacion con el nuevo .org. Asi el
        binario se genera ya con la directriz correcta en lugar de
        intentar reubicarlo a posteriori.
        """
        if not self.atl_path:
            return
        if self.exec_thread and self.exec_thread.is_alive():
            return  # no recompilar mientras se ejecuta
        try:
            org = self._parse_org()
        except ValueError as e:
            self._set_status(str(e))
            return
        if self._last_org_compiled is not None and org == self._last_org_compiled:
            return  # nada cambio
        self.shell.append(
            f"\n[*] .org cambio a 0x{org:04X} -> recompilando...\n", "info"
        )
        self.on_compile()

    def _read_bin(self, path: str) -> int:
        """Carga self.bin_bytes desde el .bin y devuelve la base sugerida."""
        instrucciones: list[str] = []
        base_addr = 0
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                linea = raw.strip()
                if not linea or linea.startswith("#"):
                    continue
                if linea.startswith("@"):
                    base_addr = int(linea[1:])
                    continue
                instrucciones.append(linea)
        self.bin_bytes = instrucciones
        self.bin_base_addr = base_addr
        return base_addr

    # ── Reset / cargar VM ──────────────────────────────────────────────
    def _parse_org(self) -> int:
        s = self.org_var.get().strip()
        if not s:
            return self.bin_base_addr
        try:
            return int(s, 0)
        except ValueError:
            raise ValueError(f"Direccion .org invalida: {s!r}")

    def _prepare_vm(self) -> bool:
        if not self.bin_path or not os.path.exists(self.bin_path):
            messagebox.showwarning("Atlas IDE",
                                   "No hay binario. Compila primero.")
            return False
        try:
            self._read_bin(self.bin_path)
            base = self._parse_org()
        except ValueError as e:
            messagebox.showerror("Atlas IDE", str(e))
            return False

        self.ram = RAM(65536)
        self.cpu = CPU(self.ram)
        # Cargar bytes
        for i, b in enumerate(self.bin_bytes):
            try:
                self.ram.write(base + i, b)
            except Exception as e:
                messagebox.showerror("Atlas IDE",
                                     f"Error escribiendo en RAM @ {base + i}: {e}")
                return False
        self.cpu.reg.PC = base
        info = (
            f"Archivo: {os.path.basename(self.bin_path)}\n"
            f"Bytes:   {len(self.bin_bytes)}\n"
            f"Base:    0x{base:08X}  ({base})\n"
            f"PC inic: 0x{base:08X}\n"
            f"RAM:     {self.ram.size} bytes"
        )
        self.bin_info_var.set(info)
        self.regs_panel.update_from_cpu(self.cpu)
        self.shell.append(
            f"\n[+] {len(self.bin_bytes)} bytes cargados desde "
            f"{os.path.basename(self.bin_path)} en 0x{base:04X}\n", "info"
        )
        return True

    def on_reset_vm(self):
        if not self._prepare_vm():
            return
        self._set_status("VM reiniciada y binario recargado.")

    def on_stop(self):
        if self.exec_thread and self.exec_thread.is_alive():
            self.exec_stop_flag.set()
            if self.cpu:
                self.cpu.running = False
            self._set_status("Deteniendo ejecucion...")
        else:
            self._set_status("No hay ejecucion en curso.")

    # ── Modos de ejecucion ─────────────────────────────────────────────
    def on_execute(self):
        if self.exec_thread and self.exec_thread.is_alive():
            messagebox.showinfo("Atlas IDE", "Ya hay una ejecucion en curso.")
            return
        if self.cpu is None:
            if not self._prepare_vm():
                return
        mode = self.mode_var.get()
        if mode == "Completo":
            self._run_completo()
        elif mode == "Paso a paso":
            self._set_status("Modo Paso a paso. Usa 'Step' para avanzar.")
        elif mode == "PaP temporizado":
            self._run_temporizado()

    def on_step(self):
        if self.cpu is None:
            if not self._prepare_vm():
                return
        if self.exec_thread and self.exec_thread.is_alive():
            messagebox.showinfo("Atlas IDE",
                                "Hay una ejecucion automatica activa.")
            return
        if not self.cpu.running:
            self.shell.append("[*] La maquina esta detenida (halt).\n", "dim")
            return
        # Ejecutar un paso, capturando prints de OUT
        writer = _QueueWriter(self.io_queue)
        try:
            with contextlib.redirect_stdout(writer):
                self.cpu.step()
        except Exception as e:
            self.shell.append(f"[ERROR] {e}\n", "err")
            return
        self.regs_panel.update_from_cpu(self.cpu)

    def _run_completo(self):
        self.exec_stop_flag.clear()

        def worker():
            writer = _QueueWriter(self.io_queue)
            with contextlib.redirect_stdout(writer):
                try:
                    while self.cpu.running and not self.exec_stop_flag.is_set():
                        self.cpu.step()
                except Exception as e:
                    print(f"[ERROR ejecucion] {e}")
            # refresco final lo hace _poll_io_queue al detectar thread muerto

        self._set_status("Ejecutando (modo completo)...")
        self.shell.append("\n[*] Modo EJECUCION COMPLETA\n", "info")
        self.exec_thread = threading.Thread(target=worker, daemon=True)
        self.exec_thread.start()

    def _run_temporizado(self):
        try:
            delay = max(0.0, float(self.delay_var.get()))
        except ValueError:
            delay = 0.5
        self.exec_stop_flag.clear()

        def worker():
            writer = _QueueWriter(self.io_queue)
            with contextlib.redirect_stdout(writer):
                try:
                    while self.cpu.running and not self.exec_stop_flag.is_set():
                        self.cpu.step()
                        # refresco UI desde el hilo principal
                        self.after(0, self.regs_panel.update_from_cpu, self.cpu)
                        if delay > 0:
                            # sleep en pequenos tramos para responder a stop
                            slept = 0.0
                            while slept < delay and not self.exec_stop_flag.is_set():
                                time.sleep(min(0.05, delay - slept))
                                slept += 0.05
                except Exception as e:
                    print(f"[ERROR ejecucion] {e}")

        self._set_status(f"Ejecutando paso a paso (delay={delay}s)...")
        self.shell.append(f"\n[*] Modo PaP TEMPORIZADO (delay={delay}s)\n", "info")
        self.exec_thread = threading.Thread(target=worker, daemon=True)
        self.exec_thread.start()

    # ── Inspector mem> ─────────────────────────────────────────────────
    def on_mem_inspect(self):
        if self.ram is None:
            self.shell.append("mem> [!] No hay RAM. Reinicia la VM.\n", "err")
            return
        entrada = self.mem_var.get().strip()
        if not entrada:
            return
        self.shell.append(f"mem> {entrada}\n", "dim")
        try:
            n_bytes = 1
            if "+" in entrada:
                a, b = entrada.split("+", 1)
                addr = int(a.strip(), 0)
                n_bytes = max(1, min(64, int(b.strip(), 0)))
            else:
                addr = int(entrada, 0)
            if n_bytes == 1:
                byte = self.ram.read(addr)
                v = int(byte, 2)
                self.shell.append(
                    f"  [{addr} / 0x{addr:04X}]  bin={byte}  "
                    f"dec={v}  hex=0x{v:02X}\n"
                )
            else:
                self.shell.append(
                    f"  [{addr} / 0x{addr:04X}] .. "
                    f"[{addr + n_bytes - 1} / 0x{addr + n_bytes - 1:04X}]"
                    f"  ({n_bytes} bytes)\n"
                )
                for off in range(0, n_bytes, 8):
                    chunk = min(8, n_bytes - off)
                    bins = " ".join(self.ram.read(addr + off + b) for b in range(chunk))
                    decs = " ".join(
                        f"{int(self.ram.read(addr + off + b), 2):3d}"
                        for b in range(chunk)
                    )
                    self.shell.append(f"    0x{addr + off:04X} | {bins}\n")
                    self.shell.append(f"           dec: {decs}\n", "dim")
                if n_bytes <= 8:
                    bloque = self.ram.read_block(addr, n_bytes)
                    val = int(bloque, 2)
                    self.shell.append(
                        f"    -> valor entero ({n_bytes * 8} bits): "
                        f"{val}  (0x{val:X})\n", "info"
                    )
        except Exception as e:
            self.shell.append(f"  [!] Error: {e}\n", "err")
        finally:
            self.mem_var.set("")


def main():
    app = AtlasIDE()
    app.mainloop()


if __name__ == "__main__":
    main()
