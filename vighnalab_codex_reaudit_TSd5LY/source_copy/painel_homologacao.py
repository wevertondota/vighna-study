# -*- coding: utf-8 -*-
"""Interface Windows para o homologador QA V1.1, sem dependências gráficas adicionais.

Tkinter é parte da instalação padrão de Python; PySide6 é usado somente
pelo processo de homologação, escolhido pelo usuário.
"""
from __future__ import annotations

import os
import json
from datetime import datetime
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

import painel_core as core
import painel_planejamento as plane
from painel_historico_ui import HistoryView
from painel_historico import HistoryStore
import painel_gates as gates
import painel_g7 as g7
import painel_checkpoints as checkpoints
import painel_atualizador as painel_updater
import painel_central_qa as central_qa
import painel_g5_ui as ambiente_qt
import zipfile

ROOT = Path(__file__).resolve().parent
RUNNER = ROOT / "homologador_windows.py"
HASHES_PREPARACAO = {'base': 'e2c0ac43221dcd358cff8a7bb576f1143f81f079a5d4aee5e0d5ee6d9971c51d', 'rc2': 'a3613317c65e3a76ce97c0feb10c1853992f347b054854af4eb09908862f4985', 'ajuste': '83747a90f8c8c873c52d5cfa6611062cc3a7735c20dd17399d485ec461fbbd7c'}


class Painel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VighnaLab | Desenvolvimento e Homologação")
        self.geometry("860x680")
        self.minsize(710, 560)
        self.configure(bg="#f4f7fa")
        self.events: queue.Queue = queue.Queue()
        self.running = False
        self.lines: list[str] = []
        self.new_zip: Path | None = None
        self.run_started = 0.0
        self.python_path = tk.StringVar(value=core.load_config().get("python_qt") or core.suggested_python_path())
        self.status = tk.StringVar(value="Pronto para executar os testes")
        self.result_text = tk.StringVar(value="Nenhum resultado desta execução")
        try:
            self.plano = checkpoints.load_effective()
            self.plano_error = None
        except (OSError, ValueError) as exc:
            self.plano = None
            self.plano_error = str(exc)
        self._build_ui()
        self.result_text.trace_add("write", self._refresh_result_buttons)
        self.after(100, self._poll_queue)

    def _build_ui(self):
        self.title("VighnaLab | Desenvolvimento e Homologação")
        self.geometry("1150x745")
        self.minsize(960, 640)
        self.configure(bg="#eef2f7")
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TFrame", background="#f5f7fb")
        style.configure("TLabel", background="#f5f7fb", foreground="#263447", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 19, "bold"), foreground="#163b5b")
        style.configure("Sub.TLabel", foreground="#5e7186", font=("Segoe UI", 9))
        style.configure("Section.TLabel", foreground="#253a54", font=("Segoe UI", 11, "bold"))
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 10))
        style.configure("Secondary.TButton", font=("Segoe UI", 9), padding=(10, 8))
        style.configure("Roadmap.Treeview", rowheight=32, font=("Segoe UI", 10), background="white",
                        fieldbackground="white", foreground="#28394d", borderwidth=0)
        style.configure("Roadmap.Treeview.Heading", font=("Segoe UI", 9, "bold"), padding=(9, 10))
        style.map("Roadmap.Treeview", background=[("selected", "#dbeaff")], foreground=[("selected", "#123451")])
        self.nav_buttons = {}
        self.pages = {}
        self.container = tk.Frame(self, bg="#eef2f7")
        self.container.pack(fill="both", expand=True)
        self._build_sidebar()
        body = tk.Frame(self.container, bg="#f5f7fb")
        body.pack(side="left", fill="both", expand=True)
        self._body_header = tk.Frame(body, bg="white", height=65, highlightbackground="#e3eaf1", highlightthickness=1)
        self._body_header.pack(fill="x")
        self._body_header.pack_propagate(False)
        # Posicionamento independente: impedir sobreposição em escala Tk alta e janela estreita.
        self._header_title_label = tk.Label(
            self._body_header, text="CENTRAL DE DESENVOLVIMENTO", bg="white", fg="#29455f",
            font=("Segoe UI", 11, "bold"), anchor="w"
        )
        self._header_title_label.place(x=24, rely=0.5, anchor="w")
        self._header_status_label = tk.Label(
            self._body_header, text="Checkpoint importado localmente · sem conexão automática",
            bg="white", fg="#63788f", font=("Segoe UI", 9), justify="right", anchor="e"
        )
        self._header_status_label.place(relx=1.0, x=-22, rely=0.5, anchor="e")

        # Preservar a mensagem integral sempre que couber. Em espaço reduzido,
        # repartir em duas linhas, sem perder o estado de importação e de conexão.
        from tkinter import font as tkfont
        font_status = tkfont.Font(root=self, font=self._header_status_label.cget("font"))
        status_variants = (
            "Checkpoint importado localmente · sem conexão automática",
            "Checkpoint importado localmente\nSem conexão automática",
            "Checkpoint importado\nSem conexão automática",
            "Checkpoint local\nSem conexão automática",
            "Checkpoint local",
        )

        def reajustar_cabecalho(event=None):
            largura = self._body_header.winfo_width()
            if largura < 2:
                return
            titulo_largura = self._header_title_label.winfo_reqwidth()
            espaco_status = max(1, largura - 24 - titulo_largura - 22 - 18)
            escolhido = status_variants[-1]
            for texto in status_variants:
                if max(font_status.measure(linha) for linha in texto.split("\n")) + 4 <= espaco_status:
                    escolhido = texto
                    break
            if self._header_status_label.cget("text") != escolhido:
                self._header_status_label.configure(text=escolhido)

        self._body_header.bind("<Configure>", reajustar_cabecalho, add="+")
        self.page_host = tk.Frame(body, bg="#f5f7fb")
        self.page_host.pack(fill="both", expand=True, padx=20, pady=18)
        for page in ("geral", "planejamento", "preparacao", "gates", "testes", "historico", "sincronizar", "atualizacoes", "configuracoes"):
            self.pages[page] = tk.Frame(self.page_host, bg="#f5f7fb")
        self._build_overview()
        self._build_preparation()
        self._build_roadmap()
        self._build_gates()
        self._build_tests()
        self._build_history()
        self._build_sync()
        self._build_settings()
        self._build_updates()
        self._show_page("geral")


    def _build_sidebar(self):
        fundo = "#172b42"
        ativo = "#294e70"
        texto = "#dce9f5"
        secundario = "#9fb8ce"

        side = tk.Frame(self.container, width=232, bg=fundo)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        marca = tk.Frame(side, bg=fundo)
        marca.pack(fill="x", padx=17, pady=(15, 10))

        tk.Label(
            marca, text="VighnaLab",
            bg=fundo, fg="#ecf6ff",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w")

        tk.Label(
            marca, text="LABORATÓRIO DO\nVIGHNASTUDY",
            bg=fundo, fg=secundario,
            font=("Segoe UI", 8), justify="left", anchor="w", wraplength=180
        ).pack(anchor="w", pady=(2, 0))

        tk.Frame(
            side, bg="#496078", height=1
        ).pack(fill="x", padx=17)

        rodape = tk.Frame(side, bg=fundo)
        rodape.pack(side="bottom", fill="x")
        self._sidebar_footer = rodape

        tk.Frame(
            rodape, bg="#496078", height=1
        ).pack(fill="x", padx=17, pady=(7, 9))

        tk.Label(
            rodape,
            text="VighnaLab · v" + painel_updater.panel_version(ROOT),
            bg=fundo, fg="#dce9f5",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=17)

        tk.Label(
            rodape,
            text="G5/G6 aprovados · G7 pendente\n"
                 "M2 RC2: não instalar\n"
                 "M3 R35: experimental",
            bg=fundo, fg=secundario,
            justify="left", anchor="w", wraplength=192,
            font=("Segoe UI", 8)
        ).pack(anchor="w", padx=17, pady=(4, 11))

        corpo = tk.Frame(side, bg=fundo)
        corpo.pack(fill="both", expand=True)

        canvas = tk.Canvas(
            corpo, bg=fundo,
            highlightthickness=0,
            borderwidth=0,
            takefocus=0
        )
        barra = tk.Scrollbar(
            corpo, orient="vertical",
            command=canvas.yview, width=10
        )
        canvas.configure(yscrollcommand=barra.set)

        barra.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        conteudo = tk.Frame(canvas, bg=fundo)
        janela = canvas.create_window(
            (0, 0), window=conteudo, anchor="nw"
        )

        conteudo.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(
                janela, width=e.width
            )
        )

        self._sidebar_canvas = canvas

        def rolar(event):
            if getattr(event, "num", None) in (4, 5):
                passos = -1 if event.num == 4 else 1
            else:
                delta = getattr(event, "delta", 0)
                if not delta:
                    return
                passos = -1 if delta > 0 else 1
            canvas.yview_scroll(passos, "units")
            return "break"

        secoes = (
            ("INÍCIO", (
                ("geral", "Painel inicial"),
            )),
            ("PLANEJAMENTO", (
                ("planejamento", "Planejamento M1–M9"),
            )),
            ("OPERAÇÕES", (
                ("preparacao", "Preparação de versões"),
                ("testes", "Testes e validações"),
                ("gates", "Gates de liberação"),
            )),
            ("EVIDÊNCIAS", (
                ("historico", "Evidências e histórico"),
            )),
            ("SISTEMA", (
                ("sincronizar", "Sincronização"),
                ("atualizacoes", "Atualizações do painel"),
                ("configuracoes", "Configurações"),
            )),
        )

        for grupo, paginas in secoes:
            titulo = tk.Label(
                conteudo, text=grupo,
                bg=fundo, fg="#91acc3",
                font=("Segoe UI", 8, "bold")
            )
            titulo.pack(
                anchor="w", padx=17, pady=(10, 3)
            )
            titulo.bind("<MouseWheel>", rolar)
            titulo.bind("<Button-4>", rolar)
            titulo.bind("<Button-5>", rolar)

            for chave, rotulo in paginas:
                botao = tk.Button(
                    conteudo, text=rotulo,
                    anchor="w",
                    relief="flat", bd=0,
                    cursor="hand2",
                    fg=texto, bg=fundo,
                    activebackground=ativo,
                    activeforeground="white",
                    font=("Segoe UI", 9),
                    padx=12, pady=5,
                    highlightthickness=0,
                    command=lambda pagina=chave:
                        self._show_page(pagina)
                )
                botao.pack(
                    fill="x", padx=8, pady=1
                )
                botao.bind("<MouseWheel>", rolar)
                botao.bind("<Button-4>", rolar)
                botao.bind("<Button-5>", rolar)
                self.nav_buttons[chave] = botao

        canvas.bind("<MouseWheel>", rolar)
        canvas.bind("<Button-4>", rolar)
        canvas.bind("<Button-5>", rolar)

    def _show_page(self, name):
        if name not in self.pages:
            return
        for frame in self.pages.values():
            frame.pack_forget()
        self.pages[name].pack(fill="both", expand=True)
        for key, button in self.nav_buttons.items():
            active = key == name
            button.configure(bg="#294e70" if active else "#172b42",
                             fg="white" if active else "#dce9f5")
        if name == "historico":
            self._refresh_history()
        if name == "gates":
            self._refresh_gates()
        if name == "atualizacoes":
            self._refresh_update_info()

    def _heading(self, parent, title, subtitle):
        tk.Label(parent, text=title, fg="#193b59", bg="#f5f7fb",
                 font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(0, 2))
        tk.Label(parent, text=subtitle, fg="#607488", bg="#f5f7fb",
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 16))

    def _card(self, parent, label, value, note, *, accent="#33678d"):
        panel = tk.Frame(parent, bg="white", highlightthickness=1,
                         highlightbackground="#e0e8f0", padx=16, pady=13)
        tk.Label(panel, text=label.upper(), bg="white", fg="#6d7f91",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(panel, text=value, bg="white", fg=accent,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(5, 4))
        tk.Label(panel, text=note, bg="white", fg="#63788c", justify="left",
                 wraplength=215, font=("Segoe UI", 9)).pack(anchor="w")
        return panel

    def _section(self, parent, title):
        panel = tk.Frame(parent, bg="white", highlightthickness=1, highlightbackground="#e1e8f0")
        tk.Label(panel, text=title, bg="white", fg="#26435f",
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=16, pady=(14, 7))
        return panel



    def _system_scroller(self, page):
        """Rolagem local para as páginas de sistema; sem bind_all global."""
        viewport = tk.Frame(page, bg="#f5f7fb")
        viewport.pack(fill="both", expand=True)
        canvas = tk.Canvas(viewport, bg="#f5f7fb", borderwidth=0,
                           highlightthickness=0, takefocus=0)
        scrollbar = ttk.Scrollbar(viewport, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        content = tk.Frame(canvas, bg="#f5f7fb")
        window = canvas.create_window((0, 0), window=content, anchor="nw")
        content.bind("<Configure>", lambda _e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window, width=e.width))
        return content, canvas

    def _system_scroll_bind(self, content, canvas):
        """Roda do mouse somente sobre a página, sem capturar outras telas."""
        def wheel(event):
            if getattr(event, "num", 0) in (4, 5):
                step = -1 if event.num == 4 else 1
            else:
                delta = getattr(event, "delta", 0)
                if not delta:
                    return
                step = -1 if delta > 0 else 1
            canvas.yview_scroll(step, "units")
            return "break"

        def bind_tree(widget):
            if isinstance(widget, (tk.Entry, ttk.Entry, ttk.Combobox, tk.Text)):
                return
            for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                widget.bind(sequence, wheel, add="+")
            for child in widget.winfo_children():
                bind_tree(child)
        bind_tree(content)

    def _system_notice(self, parent, caption, message, *, caution=False):
        background = "#fff5e8" if caution else "#e9f0f7"
        foreground = "#805523" if caution else "#294b67"
        strip = tk.Frame(parent, bg=background, padx=14, pady=10)
        strip.pack(fill="x", pady=(0, 12))
        tk.Label(strip, text=caption, bg=background, fg=foreground,
                 font=("Segoe UI", 9, "bold"), anchor="w").pack(fill="x")
        tk.Label(strip, text=message, bg=background, fg="#536e86" if not caution else "#765e40",
                 font=("Segoe UI", 9), justify="left", anchor="w",
                 wraplength=620).pack(fill="x", pady=(3, 0))
        return strip

    def _build_preparation(self):
        page = self.pages["preparacao"]
        fundo = "#f5f7fb"

        self._heading(
            page, "Preparação de versões",
            "Selecione, confira e reconcilie as fontes oficiais em laboratório."
        )

        self.prep_files = {}
        self.prep_labels = {}
        self.prep_status = tk.StringVar(
            value="Aguardando seleção das três fontes."
        )

        rodape = self._section(page, "Verificação e resultado")
        rodape.pack(side="bottom", fill="x", pady=(10, 0))

        estado = tk.Label(
            rodape, textvariable=self.prep_status,
            bg="white", fg="#415e78",
            justify="left", anchor="w",
            wraplength=690, font=("Segoe UI", 9)
        )
        estado.pack(fill="x", padx=16, pady=(2, 10))
        rodape.bind(
            "<Configure>",
            lambda e: estado.configure(
                wraplength=max(180, e.width - 36)
            )
        )

        acoes = ttk.Frame(rodape)
        acoes.pack(fill="x", padx=16, pady=(0, 13))

        ttk.Button(
            acoes, text="Verificar as três fontes",
            command=self._verify_preparation,
            style="Secondary.TButton"
        ).pack(side="left")

        self.prep_action_btn = ttk.Button(
            acoes,
            text="Gerar candidato de laboratório",
            command=self._start_reconciliation,
            style="Primary.TButton"
        )
        self.prep_action_btn.pack(side="left", padx=(9, 0))

        descricao = tk.Frame(
            page, bg="#e9f0f7", padx=13, pady=9
        )
        descricao.pack(fill="x", pady=(0, 9))

        tk.Label(
            descricao,
            text="1. Fontes  →  2. Integridade  →  3. Reconciliação",
            bg="#e9f0f7", fg="#294b67",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        tk.Label(
            descricao,
            text="O resultado é um pacote parcial para auditoria. "
                 "Nenhuma instalação do VighnaStudy é autorizada.",
            bg="#e9f0f7", fg="#536e86",
            font=("Segoe UI", 9),
            justify="left", wraplength=730
        ).pack(anchor="w", pady=(5, 0))

        regiao = ttk.Frame(page)
        regiao.pack(fill="both", expand=True)

        canvas = tk.Canvas(
            regiao, bg=fundo,
            highlightthickness=0, borderwidth=0
        )
        barra = ttk.Scrollbar(
            regiao, orient="vertical",
            command=canvas.yview
        )
        canvas.configure(yscrollcommand=barra.set)

        barra.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        conteudo = tk.Frame(canvas, bg=fundo)
        identificador = canvas.create_window(
            (0, 0), window=conteudo, anchor="nw"
        )
        conteudo.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(
                identificador, width=e.width
            )
        )
        self.prep_canvas = canvas

        fontes = (
            ("base", "Base R1D",
             "Referência anterior ao ajuste de inicialização."),
            ("rc2", "M2 RC2",
             "Código dos componentes de Configurações."),
            ("ajuste", "Ajuste de inicialização",
             "Janela maximizada e barra lateral recolhida."),
        )

        for numero, (chave, titulo, explicacao) in enumerate(
            fontes, 1
        ):
            quadro = self._section(
                conteudo,
                str(numero) + ". " + titulo
            )
            quadro.pack(fill="x", pady=(0, 9))

            tk.Label(
                quadro, text=explicacao,
                bg="white", fg="#64788b",
                font=("Segoe UI", 9),
                justify="left", anchor="w"
            ).pack(fill="x", padx=16, pady=(0, 9))

            linha = ttk.Frame(quadro)
            linha.pack(fill="x", padx=16, pady=(0, 13))

            status = tk.StringVar(
                value="Nenhum arquivo selecionado"
            )
            self.prep_labels[chave] = status

            ttk.Label(
                linha, textvariable=status,
                style="Sub.TLabel", wraplength=440
            ).pack(
                side="left", fill="x", expand=True
            )

            ttk.Button(
                linha, text="Selecionar ZIP",
                command=lambda k=chave:
                    self._select_preparation_zip(k),
                style="Secondary.TButton"
            ).pack(side="right", padx=(8, 0))

        def rolar(event):
            if getattr(event, "num", None) in (4, 5):
                passos = -1 if event.num == 4 else 1
            else:
                delta = getattr(event, "delta", 0)
                if not delta:
                    return
                passos = -1 if delta > 0 else 1
            canvas.yview_scroll(passos, "units")
            return "break"

        def vincular(widget):
            for evento in (
                "<MouseWheel>", "<Button-4>", "<Button-5>"
            ):
                widget.bind(evento, rolar, add="+")
            for filho in widget.winfo_children():
                vincular(filho)

        vincular(conteudo)
        vincular(canvas)

    def _select_preparation_zip(self, chave):
        arquivo = filedialog.askopenfilename(
            parent=self, title="Selecionar fonte de laboratório",
            filetypes=[("Arquivo ZIP", "*.zip")]
        )
        if not arquivo:
            return
        try:
            path = Path(arquivo)
            if path.stat().st_size > 100_000_000:
                raise ValueError("ZIP acima do limite de 100 MB.")
            with zipfile.ZipFile(path) as z:
                if len(z.infolist()) > 10000 or z.testzip() is not None:
                    raise ValueError("ZIP inválido ou excessivamente complexo.")
            import hashlib
            h = hashlib.sha256()
            with path.open("rb") as f:
                for bloco in iter(lambda: f.read(1024 * 1024), b""):
                    h.update(bloco)
            if h.hexdigest() != HASHES_PREPARACAO[chave]:
                raise ValueError(
                    "SHA-256 diferente da fonte de referência. Seleção recusada."
                )
        except (OSError, ValueError, zipfile.BadZipFile) as exc:
            messagebox.showerror("Fonte não aceita", str(exc), parent=self)
            return
        self.prep_files[chave] = path
        self.prep_labels[chave].set(path.name)
        self.prep_status.set(
            "Fonte conferida. Continue a seleção ou revalide as três fontes."
        )

    def _verify_preparation(self):
        import hashlib
        pendentes = [
            chave for chave in HASHES_PREPARACAO
            if chave not in self.prep_files
        ]
        if pendentes:
            self.prep_status.set(
                "Fontes ainda não selecionadas: " + ", ".join(pendentes)
            )
            return
        try:
            for chave, path in self.prep_files.items():
                h = hashlib.sha256()
                with path.open("rb") as f:
                    for bloco in iter(lambda: f.read(1024 * 1024), b""):
                        h.update(bloco)
                if h.hexdigest() != HASHES_PREPARACAO[chave]:
                    raise ValueError(
                        "A fonte " + chave + " foi alterada após a seleção."
                    )
        except (OSError, ValueError) as exc:
            self.prep_status.set("BLOQUEADO: " + str(exc))
            return
        self.prep_status.set(
            "Três fontes íntegras. Preparação documental concluída; "
            "reconciliação e instalação NÃO autorizadas."
        )


    def _start_reconciliation(self):
        if self.running or getattr(self, "_recon_busy", False):
            messagebox.showwarning(
                "Operação em andamento",
                "Aguarde a execução atual.",
                parent=self
            )
            return

        if set(self.prep_files) != set(HASHES_PREPARACAO):
            self.prep_status.set(
                "Selecione as três fontes antes de reconciliar."
            )
            return

        import painel_reconciliacao as recon
        self._recon_busy = True
        self.prep_status.set(
            "Reconciliação em laboratório. Aguarde..."
        )
        self.prep_action_btn.configure(state="disabled")

        self._recon_result = queue.Queue()
        arquivos = dict(self.prep_files)

        def worker():
            try:
                resultado = recon.produzir(arquivos)
                self._recon_result.put(("ok", str(resultado)))
            except Exception as exc:
                self._recon_result.put(("erro", str(exc)))

        threading.Thread(
            target=worker, daemon=True
        ).start()
        self.after(150, self._poll_reconciliation)

    def _poll_reconciliation(self):
        try:
            tipo, mensagem = self._recon_result.get_nowait()
        except queue.Empty:
            self.after(150, self._poll_reconciliation)
            return

        self._recon_busy = False
        self.prep_action_btn.configure(state="normal")

        if tipo == "ok":
            self.prep_status.set(
                "Candidato de laboratório gerado: " + mensagem
            )
            messagebox.showinfo(
                "Reconciliação concluída",
                "ZIP de laboratório criado:\n\n"
                + mensagem
                + "\n\nNão instalar no VighnaStudy.",
                parent=self
            )
        else:
            self.prep_status.set(
                "Reconciliação bloqueada: " + mensagem
            )
            messagebox.showwarning(
                "Conflito ou validação recusada",
                mensagem, parent=self
            )


    def _build_overview(self):
        page = self.pages["geral"]
        bg = "#f5f7fb"

        self._heading(
            page, "Painel inicial",
            "Resumo do último checkpoint importado. Não representa atividade em tempo real."
        )

        if self.plano is None:
            tk.Label(
                page, text="Planejamento indisponível: " + str(self.plano_error),
                bg=bg, fg="#a14031", wraplength=620
            ).pack(anchor="w")
            return

        dados = self.plano

        faixa = tk.Frame(page, bg="#e9f0f7", padx=13, pady=10)
        faixa.pack(fill="x", pady=(0, 12))

        tk.Label(
            faixa, text="ESTADO DOCUMENTADO",
            bg="#e9f0f7", fg="#49667e",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")

        # A largura do resumo acompanha o espaço disponível no cartão.
        # Um wrap fixo de 720px cortava a referência em 960x640 com escala Tk elevada.
        resumo_checkpoint = tk.Label(
            faixa,
            text=str(dados["checkpoint"]) +
                 "  |  Referência: " + str(dados["data_referencia"]),
            bg="#e9f0f7", fg="#254561",
            font=("Segoe UI", 10),
            anchor="w", justify="left",
            wraplength=400
        )
        resumo_checkpoint.pack(anchor="w", pady=(4, 0))

        def ajustar_resumo_checkpoint(event):
            # 13 px de margem interna em cada lado do Frame.
            largura_disponivel = max(80, event.width - 26)
            if int(resumo_checkpoint.cget("wraplength")) != largura_disponivel:
                resumo_checkpoint.configure(wraplength=largura_disponivel)

        faixa.bind("<Configure>", ajustar_resumo_checkpoint, add="+")

        regiao = tk.Frame(page, bg=bg)
        regiao.pack(fill="both", expand=True)

        canvas = tk.Canvas(
            regiao, bg=bg, highlightthickness=0, borderwidth=0
        )
        barra = ttk.Scrollbar(
            regiao, orient="vertical", command=canvas.yview
        )
        canvas.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        conteudo = tk.Frame(canvas, bg=bg)
        identificador = canvas.create_window(
            (0, 0), window=conteudo, anchor="nw"
        )
        conteudo.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(
                identificador, width=e.width
            )
        )

        tk.Label(
            conteudo, text="FRENTES DO PROJETO",
            bg=bg, fg="#49667e",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(0, 7))

        indicadores = tk.Frame(conteudo, bg=bg)
        indicadores.pack(fill="x")

        cores = {
            "M1": "#315e78",
            "M2": "#a16824",
            "M3": "#5759a0"
        }
        cartoes = []

        for chave in ("M1", "M2", "M3"):
            item = next(
                (x for x in dados["macrolotes"] if x["id"] == chave),
                None
            )
            if item:
                estado = plane.STATUS.get(
                    item["situacao"], str(item["situacao"])
                )
                titulo = chave + " — " + str(item["nome"])
                descricao = str(item["resumo"])[:105]
            else:
                estado = "Sem informação"
                titulo = chave
                descricao = "Não consta no checkpoint importado"

            card = self._card(
                indicadores, titulo, estado,
                descricao, accent=cores[chave]
            )
            # As colunas precisam medir o texto já com quebra de linha.
            # Sem isso, títulos compridos alargam o grid e cortam o 3º cartão.
            rotulos = [w for w in card.winfo_children()
                       if isinstance(w, tk.Label)]
            for rotulo in rotulos:
                rotulo.configure(wraplength=215, justify="left")

            def ajustar_textos_cartao(event, labels=tuple(rotulos)):
                largura = max(140, event.width - 36)
                for rotulo in labels:
                    if int(rotulo.cget("wraplength")) != largura:
                        rotulo.configure(wraplength=largura)

            card.bind("<Configure>", ajustar_textos_cartao, add="+")
            cartoes.append(card)

        organizacao = {"colunas": None}

        def distribuir(event=None):
            largura = indicadores.winfo_width()
            colunas = 1 if largura < 740 else 3
            if organizacao["colunas"] == colunas:
                return
            organizacao["colunas"] = colunas

            for card in cartoes:
                card.grid_forget()

            for coluna in range(3):
                indicadores.grid_columnconfigure(
                    coluna, weight=1 if coluna < colunas else 0
                )

            for i, card in enumerate(cartoes):
                card.grid(
                    row=i // colunas,
                    column=i % colunas,
                    sticky="nsew",
                    padx=(0, 8) if (i % colunas) < colunas - 1 else 0,
                    pady=(0, 8)
                )

        indicadores.bind("<Configure>", distribuir)

        registrado = self._section(
            conteudo, "Trabalho registrado no checkpoint"
        )
        registrado.pack(fill="x", pady=(7, 11))

        trabalho = dados["trabalho_registrado"]

        titulo = tk.Label(
            registrado, text=trabalho["titulo"],
            bg="white", fg="#213e5b",
            font=("Segoe UI", 12, "bold"),
            justify="left", anchor="w"
        )
        titulo.pack(fill="x", padx=16, pady=(1, 5))

        detalhe = tk.Label(
            registrado, text=trabalho["detalhe"],
            bg="white", fg="#607386",
            font=("Segoe UI", 10),
            justify="left", anchor="w"
        )
        detalhe.pack(fill="x", padx=16, pady=(0, 7))

        tk.Label(
            registrado,
            text="Situação documentada: " + trabalho["situacao"],
            bg="white", fg="#995c26",
            font=("Segoe UI", 9, "bold"),
            anchor="w"
        ).pack(fill="x", padx=16, pady=(0, 11))

        registrado.bind(
            "<Configure>",
            lambda e: (
                titulo.configure(wraplength=max(180, e.width - 36)),
                detalhe.configure(wraplength=max(180, e.width - 36))
            )
        )

        proximas = self._section(
            conteudo, "Próximas atividades do checkpoint"
        )
        proximas.pack(fill="x", pady=(0, 10))

        descricoes = []
        for indice, atividade in enumerate(
            dados["proximas_atividades"][:4], 1
        ):
            item = tk.Label(
                proximas,
                text=str(indice) + ". " + str(atividade["nome"]),
                bg="white", fg="#40576e",
                font=("Segoe UI", 10),
                justify="left", anchor="w"
            )
            item.pack(fill="x", padx=16, pady=5)
            descricoes.append(item)

        proximas.bind(
            "<Configure>",
            lambda e: [
                widget.configure(wraplength=max(180, e.width - 36))
                for widget in descricoes
            ]
        )

        acoes = ttk.Frame(proximas)
        acoes.pack(fill="x", padx=16, pady=(10, 15))

        ttk.Button(
            acoes, text="Abrir planejamento",
            command=lambda: self._show_page("planejamento"),
            style="Primary.TButton"
        ).pack(side="left")

        ttk.Button(
            acoes, text="Testes e validações",
            command=lambda: self._show_page("testes"),
            style="Secondary.TButton"
        ).pack(side="left", padx=(9, 0))

        def rolar(event):
            delta = getattr(event, "delta", 0)
            if getattr(event, "num", None) in (4, 5):
                passos = -1 if event.num == 4 else 1
            elif delta:
                passos = -1 if delta > 0 else 1
            else:
                return
            canvas.yview_scroll(passos, "units")
            return "break"

        def ligar_rolagem(widget):
            for evento in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                widget.bind(evento, rolar, add="+")
            for filho in widget.winfo_children():
                ligar_rolagem(filho)

        ligar_rolagem(conteudo)
        ligar_rolagem(canvas)


    def _build_roadmap(self):
        page = self.pages["planejamento"]
        bg = "#f5f7fb"

        self._heading(
            page, "Planejamento M1–M9",
            "Consulte os macrolotes, seus requisitos e a próxima ação documentada."
        )

        if self.plano is None:
            tk.Label(
                page, text="Planejamento indisponível: " + str(self.plano_error),
                bg=bg, fg="#9b392f"
            ).pack(anchor="w")
            return

        macrolotes = self.plano["macrolotes"]

        informacao = tk.Frame(
            page, bg="#e9f0f7", padx=13, pady=9
        )
        informacao.pack(fill="x", pady=(0, 11))

        tk.Label(
            informacao,
            text=str(len(macrolotes)) + " macrolotes documentados"
                 "  |  Referência: " +
                 str(self.plano["data_referencia"]),
            bg="#e9f0f7", fg="#294b67",
            font=("Segoe UI", 10, "bold"),
            anchor="w"
        ).pack(fill="x")

        tk.Label(
            informacao,
            text="Esta página não autoriza instalação ou aprovação de Gates.",
            bg="#e9f0f7", fg="#5d738a",
            font=("Segoe UI", 9),
            anchor="w"
        ).pack(fill="x", pady=(3, 0))

        detalhe = self._section(page, "Macrolote selecionado")
        detalhe.pack(side="bottom", fill="x", pady=(10, 0))

        self.roadmap_title = tk.StringVar(
            value="Selecione um macrolote"
        )
        self.roadmap_description = tk.StringVar(value="")
        self.roadmap_next = tk.StringVar(value="")

        campos = []
        for variavel, fonte, tamanho in (
            (self.roadmap_title, "#213f5c", 11),
            (self.roadmap_description, "#516982", 9),
            (self.roadmap_next, "#7f5227", 9)
        ):
            label = tk.Label(
                detalhe, textvariable=variavel,
                bg="white", fg=fonte,
                font=("Segoe UI", tamanho),
                justify="left", anchor="w"
            )
            label.pack(
                fill="x", padx=16,
                pady=(1, 6) if tamanho == 11 else (1, 4)
            )
            campos.append(label)

        detalhe.bind(
            "<Configure>",
            lambda e: [
                label.configure(
                    wraplength=max(180, e.width - 40)
                ) for label in campos
            ]
        )

        painel = tk.Frame(
            page, bg="white",
            highlightthickness=1,
            highlightbackground="#e1e8f0"
        )
        painel.pack(
            side="top", fill="both", expand=True
        )

        colunas = ("macrolote", "escopo", "situacao")
        tree = ttk.Treeview(
            painel, columns=colunas,
            show="headings", selectmode="browse",
            style="Roadmap.Treeview",
            height=7
        )

        for coluna, titulo, largura in (
            ("macrolote", "Lote", 65),
            ("escopo", "Frente de trabalho", 430),
            ("situacao", "Situação", 165)
        ):
            tree.heading(coluna, text=titulo)
            tree.column(
                coluna, width=largura,
                minwidth=55 if coluna == "macrolote" else 120,
                stretch=(coluna == "escopo"),
                anchor="center" if coluna == "macrolote" else "w"
            )

        barra = ttk.Scrollbar(
            painel, orient="vertical", command=tree.yview
        )
        tree.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y", padx=(0, 7), pady=8)
        tree.pack(
            side="left", fill="both", expand=True,
            padx=(8, 0), pady=8
        )

        for chave, cor in (
            ("referencia", "#335b75"),
            ("homologacao", "#945e22"),
            ("laboratorio", "#5c5794"),
            ("planejado", "#687a89")
        ):
            tree.tag_configure(chave, foreground=cor)

        for item in macrolotes:
            tree.insert(
                "", "end", iid=item["id"],
                values=(
                    item["id"],
                    item["nome"],
                    plane.STATUS[item["situacao"]]
                ),
                tags=(item["situacao"],)
            )

        self.roadmap_tree = tree
        tree.bind(
            "<<TreeviewSelect>>", self._on_lote_selected
        )

        if tree.exists("M2"):
            tree.selection_set("M2")
        elif tree.get_children():
            tree.selection_set(tree.get_children()[0])

        self._on_lote_selected()

    def _on_lote_selected(self, _event=None):
        if self.plano is None or not hasattr(self, "roadmap_tree"):
            return
        selected = self.roadmap_tree.selection()
        if not selected:
            return
        index = selected[0]
        item = next((x for x in self.plano["macrolotes"] if x["id"] == index), None)
        if item:
            self.roadmap_title.set(item["id"] + " — " + item["nome"] + " · " + plane.STATUS[item["situacao"]])
            self.roadmap_description.set("Escopo: " + item["resumo"])
            self.roadmap_next.set("Próxima ação: " + item["proxima_acao"])


    def _build_gates(self):
        page = self.pages["gates"]

        self._heading(
            page, "Gates de liberação",
            "Requisitos, evidências e pendências do M2 RC2."
        )

        aviso = tk.Frame(
            page, bg="#e9f0f7",
            padx=13, pady=9
        )
        aviso.pack(fill="x", pady=(0, 10))

        tk.Label(
            aviso,
            text="A aprovação dos testes não autoriza "
                 "a instalação do VighnaStudy.",
            bg="#e9f0f7", fg="#294b67",
            font=("Segoe UI", 10, "bold"),
            anchor="w"
        ).pack(fill="x")

        tk.Label(
            aviso,
            text="Os estados são calculados a partir "
                 "das evidências registradas no histórico local.",
            bg="#e9f0f7", fg="#536e86",
            font=("Segoe UI", 9),
            anchor="w", justify="left",
            wraplength=740
        ).pack(fill="x", pady=(4, 0))

        # As ações permanecem agrupadas no rodapé.
        comandos = self._section(
            page, "Ações e evidências"
        )
        comandos.pack(side="bottom", fill="x", pady=(10, 0))

        primarios = ttk.Frame(comandos)
        primarios.pack(fill="x", padx=16, pady=(0, 8))

        ttk.Button(
            primarios,
            text="Reavaliar evidências",
            command=self._refresh_gates,
            style="Primary.TButton"
        ).pack(side="left")

        ttk.Button(
            primarios,
            text="Abrir histórico",
            command=lambda: self._show_page("historico"),
            style="Secondary.TButton"
        ).pack(side="left", padx=(8, 0))

        secundarias = ttk.Frame(comandos)
        secundarias.pack(fill="x", padx=16, pady=(0, 13))

        ttk.Button(
            secundarias,
            text="Registrar ZIP G5-C",
            command=self._register_g5c,
            style="Secondary.TButton"
        ).pack(side="left")

        ttk.Button(
            secundarias,
            text="Gerar dossiê G7",
            command=self._generate_g7_dossier,
            style="Secondary.TButton"
        ).pack(side="left", padx=(8, 0))

        # Situação sempre derivada do motor original.
        resumo = tk.Frame(
            page, bg="#ffffff",
            highlightthickness=1,
            highlightbackground="#e1e8f0"
        )
        resumo.pack(side="top", fill="x", pady=(0, 10))

        tk.Label(
            resumo, text="SITUAÇÃO DAS EVIDÊNCIAS",
            bg="white", fg="#536c83",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=16, pady=(11, 4))

        self.gates_summary = tk.StringVar(
            value="Verificando evidências locais..."
        )
        resumo_label = tk.Label(
            resumo,
            textvariable=self.gates_summary,
            bg="white", fg="#294b67",
            font=("Segoe UI", 10, "bold"),
            justify="left", anchor="w"
        )
        resumo_label.pack(
            fill="x", padx=16, pady=(0, 12)
        )
        resumo.bind(
            "<Configure>",
            lambda e: resumo_label.configure(
                wraplength=max(180, e.width - 36)
            )
        )

        tabela = self._section(
            page, "Requisitos de homologação"
        )
        tabela.pack(
            side="top", fill="both", expand=True
        )

        area = ttk.Frame(tabela)
        area.pack(
            fill="both", expand=True,
            padx=12, pady=(0, 12)
        )

        colunas = (
            "id", "etapa", "estado", "evidencia"
        )
        tree = ttk.Treeview(
            area, columns=colunas,
            show="headings", height=7,
            selectmode="browse"
        )

        for chave, titulo, largura in (
            ("id", "Gate", 58),
            ("etapa", "Requisito", 245),
            ("estado", "Situação", 120),
            ("evidencia", "Evidência registrada", 320)
        ):
            tree.heading(chave, text=titulo)
            tree.column(
                chave, width=largura,
                minwidth=54,
                stretch=(chave == "evidencia"),
                anchor="center" if chave == "id" else "w"
            )

        tree.tag_configure(
            "EVIDENCIADO", foreground="#23634e"
        )
        tree.tag_configure(
            "BLOQUEADO", foreground="#9b671e"
        )
        tree.tag_configure(
            "FALHOU", foreground="#a33331"
        )
        tree.tag_configure(
            "PENDENTE", foreground="#667789"
        )

        vertical = ttk.Scrollbar(
            area, orient="vertical",
            command=tree.yview
        )
        tree.configure(
            yscrollcommand=vertical.set
        )
        vertical.pack(
            side="right", fill="y"
        )
        tree.pack(
            side="left", fill="both", expand=True
        )

        self.gates_tree = tree
        self._refresh_gates()

    def _generate_g7_dossier(self):
        """Solicita somente uma pasta de ZIPS QA; relatório salvo no próprio painel."""
        folder=filedialog.askdirectory(parent=self,
            title='Pasta com os três ZIPs G6 já aprovados (não selecione dados pessoais)')
        if not folder:return
        try:
            self._refresh_gates()
            report=g7.evaluate(Path(folder),self.gates_report)
            destination=core.dossier_folder()
            name='G7_DOSSIE_PRELIMINAR_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.zip'
            output=g7.export(report,destination/name)
        except (OSError,ValueError,zipfile.BadZipFile,KeyError,AttributeError) as exc:
            messagebox.showerror('Auditoria G7 não concluída',str(exc),parent=self);return
        ok=sum(x['status']=='EVIDENCIA_CONFERIDA' for x in report['evidencias_g6'].values())
        messagebox.showinfo('G7 — Dossiê preliminar gerado',
            f'Evidências G6 conferidas: {ok}/3\nPendências: {len(report["pendencias"])}\n\n'
            f'Arquivo: {output}\n\nG7 PENDENTE; instalação NÃO AUTORIZADA.',parent=self)

    def _register_g5c(self):
        file=filedialog.askopenfilename(parent=self,title='Selecionar diagnóstico G5-C aprovado',
            filetypes=[('Evidência G5-C','*.zip')])
        if not file:return
        try:
            result=ambiente_qt.g5c_register_evidence(Path(file))
        except (OSError,ValueError,zipfile.BadZipFile) as exc:
            messagebox.showerror('Evidência não registrada',str(exc),parent=self);return
        messagebox.showinfo('G5-C registrado',
            'Integridade e requisitos documentais conferidos.\nA autoria não é autenticada e o G7 continua obrigatório.\n'
            'A instalação do M2 NÃO está autorizada.',parent=self)
        self._refresh_gates()

    def _refresh_gates(self):
        if not hasattr(self,'gates_tree'):return
        try:
            report=gates.evaluate(self.history_view.store if hasattr(self,'history_view') else HistoryStore())
            self.gates_report=report
            g5local=ambiente_qt.g5c_load_registry()
            if g5local:
                row=next((x for x in report['gates'] if x['id']=='G5'),None)
                if row:
                    row['situacao']='EVIDENCIADO'
                    row['origem']='G5-C documental: '+g5local['arquivo_nome']
                    row['observacao']='Verificação automática de hash/contrato; imagens exigem auditoria humana G7.'
                    report['evidenciados']+=1;report['pendentes']-=1
        except (OSError,ValueError) as exc:
            self.gates_summary.set('Histórico indisponível: '+str(exc))
            return
        for item in self.gates_tree.get_children():self.gates_tree.delete(item)
        for row in report['gates']:
            self.gates_tree.insert('', 'end',values=(row['id'],row['nome'],
                row['situacao'],row['origem']),tags=(row['situacao'],))
        self.gates_summary.set(
            f"{report['evidenciados']} evidenciados · {report['pendentes']} pendentes · "
            f"{report['bloqueados']} bloqueados · {report['falhas']} falharam · INSTALAÇÃO NÃO AUTORIZADA")

    def _build_sync(self):
        content, canvas = self._system_scroller(self.pages["sincronizar"])
        self._heading(content, "Sincronização manual",
                      "Checkpoints de planejamento importados e exportados de forma local.")
        self._system_notice(
            content, "SINCRONIZAÇÃO CONTROLADA",
            "Não há conexão em tempo real com o ChatGPT, nem transferência automática de dados.")

        card = self._section(content, "Checkpoint disponível neste computador")
        card.pack(fill="x", pady=(0, 12))
        current = self.plano
        self.sync_state = tk.StringVar(value=(current["checkpoint"] if current else "Indisponível"))
        self.sync_reference = tk.StringVar(value=(current["data_referencia"] if current else "—"))
        tk.Label(card, textvariable=self.sync_state, bg="white", fg="#234b69",
                 font=("Segoe UI", 12, "bold"), anchor="w", justify="left",
                 wraplength=620).pack(fill="x", padx=16, pady=(1, 4))
        tk.Label(card, textvariable=self.sync_reference, bg="white", fg="#647c91",
                 font=("Segoe UI", 9), anchor="w").pack(fill="x", padx=16, pady=(0, 14))

        actions = self._section(content, "Ações de sincronização")
        actions.pack(fill="x", pady=(0, 12))
        buttons = ttk.Frame(actions)
        buttons.pack(fill="x", padx=16, pady=(1, 10))
        ttk.Button(buttons, text="Importar checkpoint (.zip)",
                   command=self._import_checkpoint,
                   style="Primary.TButton").pack(side="left")
        ttk.Button(buttons, text="Exportar status (.zip)",
                   command=self._export_status,
                   style="Secondary.TButton").pack(side="left", padx=(10, 0))
        tk.Label(actions, text="Confira a origem e os dados exibidos antes de confirmar uma importação.",
                 bg="white", fg="#64788a", anchor="w", justify="left",
                 font=("Segoe UI", 9), wraplength=640).pack(
                     fill="x", padx=16, pady=(0, 12))

        rules = self._section(content, "Limites e proteção")
        rules.pack(fill="x", pady=(0, 6))
        for item in (
            "Importa dois arquivos JSON com validação de tamanho, estrutura e SHA-256.",
            "Preserva o planejamento anterior para recuperação local.",
            "A importação não executa código e não altera gates nem o VighnaStudy.",
            "O status exportado deve ser anexado manualmente à conversa.",
            "Nenhum checkpoint concede autorização de instalação do M2 ou M3.",
        ):
            tk.Label(rules, text="• " + item, bg="white", fg="#455e74",
                     font=("Segoe UI", 9), anchor="w", justify="left",
                     wraplength=630).pack(fill="x", padx=16, pady=(1, 5))
        tk.Frame(rules, bg="white", height=7).pack(fill="x")
        self._system_scroll_bind(content, canvas)

    def _import_checkpoint(self):
        filename=filedialog.askopenfilename(parent=self,title='Importar checkpoint do planejamento',
            filetypes=[('Checkpoint de planejamento','*.zip')])
        if not filename:return
        try:
            state=checkpoints.read_checkpoint(Path(filename))
        except (OSError,ValueError) as exc:
            messagebox.showerror('Checkpoint rejeitado',str(exc),parent=self);return
        preview=(f"CHECKPOINT: {state['checkpoint']}\nDATA: {state['data_referencia']}\n"
                 f"TRABALHO: {state['trabalho_registrado']['titulo']}\n\n"
                 "O arquivo tem integridade verificada, mas não possui assinatura de autoria.\n"
                 "Importar substituirá apenas o PLANEJAMENTO LOCAL e nunca autorizará instalação.\n\nContinuar?")
        if not messagebox.askyesno('Conferir checkpoint',preview,parent=self):return
        try:state=checkpoints.apply_checkpoint(Path(filename))
        except (OSError,ValueError) as exc:
            messagebox.showerror('Importação não concluída',str(exc),parent=self);return
        self.plano=state
        self.plano_error=None
        self.sync_state.set(state['checkpoint'])
        self.sync_reference.set(state['data_referencia'])
        # Atualiza a visão geral e o planejamento sem modificar o motor dos testes.
        for page,constructor in [('geral',self._build_overview),('planejamento',self._build_roadmap)]:
            for widget in self.pages[page].winfo_children():widget.destroy()
            constructor()
        messagebox.showinfo('Checkpoint importado','Planejamento atualizado. Gates continuam independentes.',parent=self)

    def _export_status(self):
        if self.plano is None:
            messagebox.showwarning('Planejamento','Nenhum checkpoint válido para exportação.',parent=self);return
        target=filedialog.asksaveasfilename(parent=self,title='Exportar status local para ChatGPT',
            initialfile='VighnaStudy_STATUS_LOCAL_V3.zip',defaultextension='.zip',
            filetypes=[('ZIP de status','*.zip')])
        if not target:return
        try:
            report=gates.evaluate(self.history_view.store)
            result=checkpoints.export_status(self.plano,report,Path(target))
        except (OSError,ValueError) as exc:
            messagebox.showerror('Falha ao exportar',str(exc),parent=self);return
        messagebox.showinfo('Status exportado',
            'Arquivo criado:\n'+str(result)+'\n\nAnexe manualmente ao ChatGPT.',parent=self)

    def _refresh_result_buttons(self, *_):
        """Atualiza rodapé sem modificar o motor/hashes históricos de execução."""
        found = bool(self.new_zip and self.new_zip.is_file() and not self.running)
        state = "normal" if found else "disabled"
        self.folder_btn.configure(state=state)
        self.copy_btn.configure(state=state)

    def _scroll_tests_event(self, event):
        """Rola a página Testes; preserva a rolagem nativa dentro do log."""
        if not self.pages["testes"].winfo_ismapped():
            return
        child = event.widget
        while child is not None:
            if child is self.log:
                return
            child = getattr(child, "master", None)
        if getattr(event, "num", None) in (4, 5):
            steps = -1 if event.num == 4 else 1
        else:
            delta = getattr(event, "delta", 0)
            if not delta:
                return
            steps = -1 if delta > 0 else 1
            steps *= max(1, min(4, abs(delta) // 120))
        self.tests_canvas.yview_scroll(steps, "units")
        return "break"


    def _start_central_qa(self):
        if self.central_running or self.running:
            messagebox.showwarning("Central de homologação", "Há um teste em andamento.")
            return
        escolhidos = [key for key, var in self.central_options.items() if var.get()]
        if not escolhidos:
            messagebox.showinfo("Central de homologação", "Selecione ao menos uma verificação.")
            return
        self.central_running = True
        for item in self.central_status_vars.values():
            item.set("NÃO EXECUTADO")
        self.central_evidence = None
        self.central_btn.configure(state="disabled")
        self.central_copy_btn.configure(state="disabled")
        self.central_feedback.set("Preparando cópia temporária isolada...")
        self.central_queue = queue.Queue()

        def worker():
            try:
                result = central_qa.execute(
                    ROOT, selected=escolhidos,
                    on_progress=lambda nome, estado: self.central_queue.put(("progresso", nome, estado))
                )
                self.central_queue.put(("concluido", result))
            except Exception as exc:
                self.central_queue.put(("erro", f"{type(exc).__name__}: {exc}"))

        threading.Thread(target=worker, name="vighnalab-central-qa", daemon=True).start()
        self.after(120, self._poll_central_qa)

    def _poll_central_qa(self):
        try:
            while True:
                event = self.central_queue.get_nowait()
                if event[0] == "progresso":
                    if event[1] in self.central_status_vars:
                        self.central_status_vars[event[1]].set(event[2].replace("PASSOU_COM_RESSALVAS", "RESSALVAS"))
                    self.central_feedback.set(event[1] + " — " + event[2])
                elif event[0] == "concluido":
                    self.central_running = False
                    self.central_btn.configure(state="normal")
                    self.central_evidence = Path(event[1]["arquivo"])
                    self.central_copy_btn.configure(state="normal")
                    self.central_feedback.set(
                        event[1]["resultado"] + " · ZIP: " + self.central_evidence.name
                    )
                elif event[0] == "erro":
                    self.central_running = False
                    self.central_btn.configure(state="normal")
                    self.central_feedback.set("Falha da central: " + event[1])
        except queue.Empty:
            pass
        if self.central_running:
            self.after(120, self._poll_central_qa)

    def _copy_central_evidence(self):
        if self.central_evidence and self.central_evidence.is_file():
            self.clipboard_clear()
            self.clipboard_append(str(self.central_evidence))
            self.update_idletasks()
            messagebox.showinfo("Central de homologação", "Caminho copiado. O arquivo permanece no TEMP.")

    def _build_tests(self):
        page = self.pages["testes"]

        self._heading(
            page, "Testes e validações",
            "Execução em cópias isoladas, com evidências para auditoria."
        )

        fixo = ttk.Frame(page)
        fixo.pack(side="bottom", fill="x", pady=(8, 0))
        ttk.Separator(
            fixo, orient="horizontal"
        ).pack(fill="x", pady=(0, 7))

        ttk.Label(
            fixo, text="Último resultado",
            style="Section.TLabel"
        ).pack(anchor="w")

        self.result_label = ttk.Label(
            fixo, textvariable=self.result_text,
            style="Sub.TLabel", wraplength=530
        )
        self.result_label.pack(
            fill="x", pady=(3, 6)
        )

        self.folder_btn = ttk.Button(
            fixo, text="Abrir pasta do resultado",
            command=self._open_result_folder,
            style="Secondary.TButton"
        )
        self.copy_btn = ttk.Button(
            fixo, text="Copiar caminho do ZIP",
            command=self._copy_result,
            style="Secondary.TButton"
        )

        self.folder_btn.pack(side="left", pady=(0, 3))
        self.copy_btn.pack(
            side="left", padx=8, pady=(0, 3)
        )
        self.folder_btn.configure(state="disabled")
        self.copy_btn.configure(state="disabled")

        area = ttk.Frame(page)
        area.pack(fill="both", expand=True)

        self.tests_canvas = tk.Canvas(
            area, bg="#f5f7fb",
            highlightthickness=0,
            borderwidth=0, takefocus=0
        )
        self.tests_scrollbar = ttk.Scrollbar(
            area, orient="vertical",
            command=self.tests_canvas.yview
        )
        self.tests_canvas.configure(
            yscrollcommand=self.tests_scrollbar.set
        )

        self.tests_scrollbar.pack(
            side="right", fill="y"
        )
        self.tests_canvas.pack(
            side="left", fill="both", expand=True
        )

        conteudo = ttk.Frame(self.tests_canvas)
        self.tests_content = conteudo
        janela = self.tests_canvas.create_window(
            (0, 0), window=conteudo, anchor="nw"
        )

        conteudo.bind(
            "<Configure>",
            lambda e: self.tests_canvas.configure(
                scrollregion=self.tests_canvas.bbox("all")
            )
        )
        self.tests_canvas.bind(
            "<Configure>",
            lambda e: (
                self.tests_canvas.itemconfigure(
                    janela, width=e.width
                ),
                self.result_label.configure(
                    wraplength=max(180, e.width - 40)
                )
            )
        )

        informacao = ttk.Frame(conteudo)
        informacao.pack(fill="x", pady=(0, 9))

        ttk.Label(
            informacao,
            text="Ambiente de execução: Python + PySide6",
            style="Sub.TLabel"
        ).pack(side="left")

        ttk.Button(
            informacao,
            text="Configurar ambiente",
            command=lambda:
                self._show_page("configuracoes"),
            style="Secondary.TButton"
        ).pack(side="right")

        # Central automatizada: coordena apenas testes de fontes do painel
        # em clone descartável. Os botões G5/G6 e o homologador original
        # continuam independentes e inalterados.
        central = self._section(conteudo, "Central de Homologação Automatizada")
        central.pack(fill="x", pady=(0, 10))
        ttk.Label(
            central,
            text="Execute verificações em sequência e receba um único ZIP de evidências. "
                 "Sem instalação e sem usar bancos ou backups pessoais.",
            style="Sub.TLabel", wraplength=640
        ).pack(anchor="w", padx=16, pady=(0, 6))
        self.central_options = {}
        self.central_status_vars = {}
        descricoes = (
            ("integridade", "Integridade e versão das fontes"),
            ("regressoes", "Regressões automatizadas (ignorados explícitos)"),
            ("sqlite", "Backup e restauração SQLite sintéticos"),
            ("g7", "Regressões documentais G7 (não aprova G7)"),
            ("g7_seguranca", "G7: ataques sintéticos e bloqueios documentais"),
            ("g7_prontidao", "G7 real: preparar evidências (sem acessar backups)"),
            ("ntfs", "NTFS: junction isolada e arquivos sentinela"),
            ("dpi", "DPI nativo: medir escala atual (outras pendentes)"),
            ("pyinstaller", "PyInstaller: smoke opcional, sem instalar dependências"),
            ("diagnosticos_exe", "EXE: 4 diagnósticos internos de leitura (sem dados reais)"),
        )
        for perfil, descricao in descricoes:
            selecionado = tk.BooleanVar(value=True)
            self.central_options[perfil] = selecionado
            item = ttk.Frame(central)
            item.pack(fill="x", padx=16, pady=1)
            ttk.Checkbutton(item, text=descricao, variable=selecionado).pack(side="left", fill="x", expand=True)
            estado = tk.StringVar(value="NÃO EXECUTADO")
            self.central_status_vars[perfil] = estado
            ttk.Label(item, textvariable=estado, style="Sub.TLabel", width=17, anchor="e").pack(side="right")
        self.central_feedback = tk.StringVar(value="Nenhuma execução iniciada")
        ttk.Label(
            central, textvariable=self.central_feedback,
            style="Sub.TLabel", wraplength=650
        ).pack(anchor="w", padx=16, pady=(8, 7))
        linha_central = ttk.Frame(central)
        linha_central.pack(fill="x", padx=16, pady=(0, 13))
        self.central_btn = ttk.Button(
            linha_central, text="Executar bateria selecionada",
            command=self._start_central_qa, style="Primary.TButton"
        )
        self.central_btn.pack(side="left", padx=(0, 8))
        self.central_copy_btn = ttk.Button(
            linha_central, text="Copiar caminho das evidências",
            command=self._copy_central_evidence, style="Secondary.TButton"
        )
        self.central_copy_btn.pack(side="left")
        self.central_copy_btn.configure(state="disabled")
        self.central_evidence = None
        self.central_running = False

        basicos = self._section(
            conteudo, "1. Testes gerais"
        )
        basicos.pack(fill="x", pady=(0, 10))

        ttk.Label(
            basicos,
            text="Verificações Qt e SQLite ou compilação "
                 "experimental de executável.",
            style="Sub.TLabel"
        ).pack(
            anchor="w", padx=16, pady=(0, 9)
        )

        comandos = ttk.Frame(basicos)
        comandos.pack(
            fill="x", padx=16, pady=(0, 13)
        )

        self.run_btn = ttk.Button(
            comandos, text="Testes Qt + SQLite",
            command=lambda: self._start("testes"),
            style="Primary.TButton"
        )
        self.run_btn.pack(
            side="left", fill="x", expand=True,
            padx=(0, 8)
        )

        self.build_btn = ttk.Button(
            comandos, text="Testes + compilar EXE",
            command=lambda: self._start("build"),
            style="Primary.TButton"
        )
        self.build_btn.pack(
            side="left", fill="x", expand=True
        )

        def linha_teste(painel, nome, descricao, comando):
            linha = ttk.Frame(painel)
            linha.pack(fill="x", padx=16, pady=(0, 10))

            botao = ttk.Button(
                linha, text=nome, command=comando,
                style="Secondary.TButton"
            )
            botao.pack(anchor="w")

            ttk.Label(
                linha, text=descricao,
                style="Sub.TLabel",
                wraplength=680
            ).pack(anchor="w", pady=(4, 0))

            return botao

        g5 = self._section(
            conteudo, "2. Isolamento e Windows Sandbox — G5"
        )
        g5.pack(fill="x", pady=(0, 10))

        self.g5a_btn = linha_teste(
            g5, "G5-A · Verificar isolamento",
            "Auditoria preliminar sem executar o EXE real.",
            self._start_g5a
        )
        self.g5b_btn = linha_teste(
            g5, "G5-B · Executar EXE no Sandbox",
            "Compilação e execução somente em ambiente restrito.",
            self._start_g5b
        )
        self.g5c_btn = linha_teste(
            g5, "G5-C · Validar interface e reinicialização",
            "Capturas, navegação e banco sintético no Sandbox.",
            self._start_g5c
        )

        g6 = self._section(
            conteudo, "3. Atualização e recuperação — G6"
        )
        g6.pack(fill="x", pady=(0, 10))

        self.g6a_btn = linha_teste(
            g6, "G6-A · Testar atualização sintética",
            "Aplicação, falha simulada e recuperação isolada.",
            self._start_g6a
        )
        self.g6b_btn = linha_teste(
            g6, "G6-B1 · Atualização com EXEs reais",
            "Fontes R1D/RC2 e transações no Windows Sandbox.",
            self._start_g6b
        )
        self.g6b2_btn = linha_teste(
            g6, "G6-B2 · Compilação original PyInstaller",
            "Compilação dentro do Sandbox e testes de restauração.",
            self._start_g6b2
        )

        execucao = self._section(
            conteudo, "4. Execução e evidências"
        )
        execucao.pack(fill="x", pady=(0, 10))

        linha = ttk.Frame(execucao)
        linha.pack(fill="x", padx=16, pady=(0, 7))

        ttk.Label(
            linha, text="Situação:",
            style="Section.TLabel"
        ).pack(side="left")

        ttk.Label(
            linha, textvariable=self.status,
            style="Sub.TLabel"
        ).pack(
            side="left", padx=9
        )

        self.progress = ttk.Progressbar(
            execucao, mode="indeterminate"
        )
        self.progress.pack(
            fill="x", padx=16, pady=(0, 11)
        )

        ttk.Label(
            execucao, text="Registro da execução",
            style="Section.TLabel"
        ).pack(
            anchor="w", padx=16, pady=(0, 6)
        )

        self.log = scrolledtext.ScrolledText(
            execucao,
            font=("Consolas", 9),
            bg="white", fg="#263447",
            height=9, wrap="word",
            state="disabled",
            relief="solid", bd=1
        )
        self.log.pack(
            fill="x", padx=16, pady=(0, 12)
        )

        for evento in (
            "<MouseWheel>",
            "<Button-4>",
            "<Button-5>"
        ):
            self.tests_canvas.bind_all(
                evento, self._scroll_tests_event,
                add="+"
            )

    def _build_updates(self):
        content, canvas = self._system_scroller(self.pages["atualizacoes"])
        self._heading(content, "Atualizações do painel",
                      "Atualização incremental e reversão exclusivamente do VighnaLab.")
        self._system_notice(
            content, "ESCOPO RESTRITO AO PAINEL",
            "Esta página não atualiza nem autoriza a instalação do VighnaStudy principal.",
            caution=True)

        version_card = self._section(content, "Versão identificada")
        version_card.pack(fill="x", pady=(0, 12))
        self.update_version = tk.StringVar(
            value="Versão do painel: " + painel_updater.panel_version(ROOT))
        tk.Label(version_card, textvariable=self.update_version,
                 font=("Segoe UI", 13, "bold"), fg="#264c70", bg="white",
                 anchor="w").pack(fill="x", padx=16, pady=(0, 8))
        self.update_status = tk.StringVar(value="Aguardando atualização incremental")
        status_label = tk.Label(version_card, textvariable=self.update_status,
                                bg="white", fg="#526e84", font=("Segoe UI", 9),
                                anchor="w", justify="left")
        status_label.pack(fill="x", padx=16, pady=(0, 14))
        version_card.bind("<Configure>", lambda e: status_label.configure(
            wraplength=max(180, e.width - 40)))

        actions = self._section(content, "Atualizar ou recuperar")
        actions.pack(fill="x", pady=(0, 12))
        controls = ttk.Frame(actions)
        controls.pack(fill="x", padx=16, pady=(0, 10))
        ttk.Button(controls, text="Selecionar atualização (.zip)",
                   command=self._select_panel_update,
                   style="Primary.TButton").pack(side="left")
        ttk.Button(controls, text="Reverter última atualização",
                   command=self._rollback_panel_update,
                   style="Secondary.TButton").pack(side="left", padx=(10, 0))
        tk.Label(actions, text="Após confirmação, o atualizador externo assume a operação e pode reabrir o painel.",
                 bg="white", fg="#61788e", font=("Segoe UI", 9),
                 wraplength=640, justify="left", anchor="w").pack(
                     fill="x", padx=16, pady=(0, 13))

        safeguards = self._section(content, "Verificações antes de substituir arquivos")
        safeguards.pack(fill="x", pady=(0, 12))
        for line in (
            "Versão de origem compatível e arquivos dentro da lista permitida.",
            "SHA-256 de origem e destino conferidos pelo atualizador.",
            "Backup verificado antes da aplicação e reversão disponível.",
            "Pacotes sem origem confiável, incompatíveis ou modificados são recusados.",
        ):
            tk.Label(safeguards, text="• " + line, bg="white", fg="#455e74",
                     font=("Segoe UI", 9), anchor="w", justify="left",
                     wraplength=620).pack(fill="x", padx=16, pady=(0, 7))
        tk.Frame(safeguards, bg="white", height=6).pack(fill="x")
        tk.Label(content,
                 text="Histórico e checkpoints são armazenados fora do pacote. "
                      "SHA-256 verifica integridade, mas não autentica autoria.",
                 bg="#f5f7fb", fg="#64798d", justify="left",
                 font=("Segoe UI", 9), wraplength=660).pack(
                     fill="x", anchor="w", pady=(0, 12))
        self._system_scroll_bind(content, canvas)

    def _refresh_update_info(self):
        if not hasattr(self,"update_version"):
            return
        try:
            self.update_version.set("Versão do painel: " + painel_updater.panel_version(ROOT))
        except (OSError,ValueError) as exc:
            self.update_version.set("Versão local não verificada: "+str(exc))
        report=ROOT/".painel_updates"/"ultima_execucao.json"
        if report.is_file():
            try:
                import json as _json
                obj=_json.loads(report.read_text(encoding="utf8"))
                self.update_status.set("Última operação: " + str(obj.get("status","indefinida"))
                                       + " — " + str(obj.get("detalhe",""))[:280])
            except (OSError,ValueError):
                self.update_status.set("Registro de atualização ilegível; verificar antes de prosseguir")

    def _start_external_update(self, action, package=None):
        """Fecha apenas o painel; atualizador externo espera este PID terminar."""
        # O atualizador por scripts não é um subcomando deste EXE de QA.
        # Recusar antes de abrir subprocesso ou fechar o painel.
        if getattr(sys, "frozen", False):
            messagebox.showwarning("Atualização indisponível no EXE de QA",
                "Atualização e rollback externos exigem a versão Python homologada do VighnaLab. "
                "O executável congelado não inicia painel_atualizador.py.", parent=self)
            return
        if self.running:
            messagebox.showwarning("Testes em andamento","Aguarde a bateria de testes terminar.",parent=self)
            return
        cmd=[sys.executable,"-B",str(ROOT/"painel_atualizador.py"),
             "--root",str(ROOT),"--wait-pid",str(os.getpid())]
        if action=="rollback":cmd.append("--rollback")
        else:cmd.extend(["--apply",str(package),"--gui-progress"])
        try:
            flags=(getattr(subprocess,"CREATE_NO_WINDOW",0)
                   if action=="apply" else getattr(subprocess,"CREATE_NEW_CONSOLE",0))
            subprocess.Popen(cmd,cwd=str(ROOT),creationflags=flags)
        except OSError as exc:
            messagebox.showerror("Falha ao iniciar atualização",str(exc),parent=self)
            return
        self.destroy()

    def _select_panel_update(self):
        file=filedialog.askopenfilename(parent=self,title="Atualizar somente o Painel V3",
                                       filetypes=[("Pacote de atualização (.zip)","*.zip")])
        if not file:return
        try:
            preview=painel_updater.inspect(Path(file),ROOT)
        except (OSError,ValueError) as exc:
            messagebox.showerror("Pacote rejeitado",str(exc),parent=self);return
        message=(f"Atualização do PAINEL: {preview['from_version']} → {preview['to_version']}\n"
                 f"Arquivos alterados: {len(preview['files'])}\n"
                 f"Descrição: {preview['description']}\n\n"
                 "O painel será fechado, a atualização mostrará progresso e, se aprovada, reabrirá automaticamente.\n"
                 "A instalação principal do VighnaStudy não será alterada.\n\n"
                 "Você confirma que obteve este ZIP nesta conversa?")
        if messagebox.askyesno("Confirmar atualização do painel",message,parent=self):
            self._start_external_update("apply",file)

    def _rollback_panel_update(self):
        if messagebox.askyesno("Reverter a última atualização",
             "A reversão restaurará apenas os arquivos do painel da última atualização íntegra.\n"
             "Fechar o painel e continuar?",parent=self):
            self._start_external_update("rollback")

    def _build_settings(self):
        content, canvas = self._system_scroller(self.pages["configuracoes"])
        self._heading(content, "Configurações",
                      "Ambientes Python e Qt utilizados somente na homologação.")
        self._system_notice(
            content, "CONFIGURAÇÃO LOCAL",
            "Selecione ou verifique o interpretador de testes. O Python e o VighnaStudy principais não são modificados.")

        python_card = self._section(content, "Interpretador Python com PySide6")
        python_card.pack(fill="x", pady=(0, 12))
        tk.Label(python_card, text="Caminho do python.exe do ambiente Qt de testes",
                 bg="white", fg="#526a80", font=("Segoe UI", 9),
                 anchor="w").pack(fill="x", padx=16, pady=(0, 7))
        row = ttk.Frame(python_card)
        row.pack(fill="x", padx=16)
        ttk.Entry(row, textvariable=self.python_path).pack(
            side="left", fill="x", expand=True)
        self.select_btn = ttk.Button(row, text="Selecionar...", command=self._choose_python,
                                     style="Secondary.TButton")
        self.select_btn.pack(side="left", padx=(8, 5))
        self.verify_btn = ttk.Button(row, text="Verificar", command=self._verify_python,
                                     style="Secondary.TButton")
        self.verify_btn.pack(side="left")
        tk.Label(python_card, text="A seleção é salva nas configurações locais do painel.",
                 bg="white", fg="#64788a", font=("Segoe UI", 9),
                 anchor="w").pack(fill="x", padx=16, pady=(9, 14))

        managed = self._section(content, "Ambiente Qt dedicado")
        managed.pack(fill="x", pady=(0, 12))
        target_label = tk.Label(managed,
                                text="Destino do ambiente de QA: " + str(ambiente_qt.destination()),
                                bg="white", fg="#465e74", font=("Segoe UI", 9),
                                justify="left", anchor="w")
        target_label.pack(fill="x", padx=16, pady=(0, 9))
        managed.bind("<Configure>", lambda e: target_label.configure(
            wraplength=max(180, e.width - 40)))
        row_env = ttk.Frame(managed)
        row_env.pack(fill="x", padx=16, pady=(0, 11))
        self.prepare_qt_btn = ttk.Button(row_env, text="Preparar ambiente Qt exclusivo",
                                        command=self._prepare_managed_qt,
                                        style="Secondary.TButton")
        self.prepare_qt_btn.pack(side="left")
        ttk.Button(row_env, text="Usar ambiente exclusivo existente",
                   command=self._select_managed_qt,
                   style="Secondary.TButton").pack(side="left", padx=(9, 0))
        self.qt_environment_status = tk.StringVar(
            value="Seu ambiente anterior será preservado até a verificação.")
        status = tk.Label(managed, textvariable=self.qt_environment_status,
                          bg="white", fg="#516f86", font=("Segoe UI", 9),
                          anchor="w", justify="left")
        status.pack(fill="x", padx=16, pady=(0, 14))
        managed.bind("<Configure>", lambda e: (
            target_label.configure(wraplength=max(180, e.width - 40)),
            status.configure(wraplength=max(180, e.width - 40))))

        safety = self._section(content, "Isolamento e limites")
        safety.pack(fill="x", pady=(0, 12))
        for item in (
            "Testes executados em fontes e bancos sintéticos isolados.",
            "O banco pessoal e a instalação principal do VighnaStudy são preservados.",
            "ZIPs de evidências são compartilhados apenas mediante ação manual.",
            "Resultado favorável de QA não autoriza a instalação do M2 ou M3.",
        ):
            tk.Label(safety, text="• " + item, bg="white", fg="#455e74",
                     font=("Segoe UI", 9), justify="left", anchor="w",
                     wraplength=620).pack(fill="x", padx=16, pady=(0, 7))
        tk.Frame(safety, bg="white", height=6).pack(fill="x")
        self._system_scroll_bind(content, canvas)

    def _select_managed_qt(self):
        """Ativa ambiente dedicado somente após validar todas as dependências."""
        try:
            qt_python = ambiente_qt.interpreter(ambiente_qt.destination())
            info = ambiente_qt.probe(qt_python)
        except ambiente_qt.EnvironmentError as exc:
            messagebox.showwarning("Ambiente Qt exclusivo", str(exc), parent=self)
            return
        self.python_path.set(str(qt_python))
        core.save_python_path(str(qt_python))
        self.qt_environment_status.set("Ambiente Qt exclusivo validado: PySide6 " + info["pyside6"])
        messagebox.showinfo("Python de homologação", "Ambiente exclusivo validado e selecionado.\n"
                            "O antigo qtvenv continua intacto.", parent=self)

    def _prepare_managed_qt(self):
        if getattr(sys, "frozen", False):
            messagebox.showwarning("Preparação Qt indisponível no EXE de QA",
                "Preparação do ambiente Qt exige interpretador Python externo. "
                "O executável congelado não executará painel_g5_ui.py.", parent=self)
            return
        if self.running or getattr(self, "_env_setup_process", None) is not None:
            messagebox.showwarning("Operação em andamento", "Aguarde a operação atual.", parent=self)
            return
        target = ambiente_qt.destination()
        try:
            ambiente_qt.verify_destination(target)
        except ambiente_qt.EnvironmentError as exc:
            messagebox.showerror("Ambiente bloqueado", str(exc), parent=self)
            return
        msg = ("Criar ambiente Python 3.13 exclusivamente para testes Qt?\n\n"
               "Destino: " + str(target) + "\n\n"
               "O Python virtual instalará PySide6, PyInstaller e qtawesome do índice de pacotes "
               "configurado no pip. Pode exigir Internet, vários minutos e centenas de MB.\n\n"
               "Seu Python atual e o VighnaStudy principal não serão alterados.\n"
               "A configuração só mudará após verificação completa.")
        if not messagebox.askyesno("Preparar ambiente Qt exclusivo", msg, parent=self):
            return
        log = ROOT / "ambiente_qt_preparacao.log"
        try:
            handle = log.open("w", encoding="utf8")
            try:
                flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
                proc = subprocess.Popen([sys.executable, "-B", str(ROOT / "painel_g5_ui.py"), "--prepare"],
                        cwd=str(ROOT), stdout=handle, stderr=subprocess.STDOUT,
                        env=ambiente_qt.clean_env(), creationflags=flags)
            finally:
                handle.close()
        except OSError as exc:
            messagebox.showerror("Falha ao iniciar preparação", str(exc), parent=self)
            return
        self._env_setup_process = proc
        self.prepare_qt_btn.configure(state="disabled")
        self.run_btn.configure(state="disabled")
        self.build_btn.configure(state="disabled")
        self.qt_environment_status.set("Preparando ambiente Qt em VighnaLab. Aguarde: pode demorar vários minutos.")
        self.after(1000, self._poll_managed_qt)

    def _poll_managed_qt(self):
        proc = getattr(self, "_env_setup_process", None)
        if proc is None:
            return
        code = proc.poll()
        if code is None:
            self.after(1000, self._poll_managed_qt)
            return
        self._env_setup_process = None
        self.prepare_qt_btn.configure(state="normal")
        self.run_btn.configure(state="normal")
        self.build_btn.configure(state="normal")
        if code == 0:
            try:
                self._select_managed_qt()
            except Exception as exc:
                self.qt_environment_status.set("Falha na validação final: " + str(exc))
        else:
            log = ROOT / "ambiente_qt_preparacao.log"
            try:
                details = log.read_text(encoding="utf8", errors="replace")[-950:]
            except OSError:
                details = "Log não disponível"
            self.qt_environment_status.set("Preparação não concluída; Python antigo preservado.")
            messagebox.showerror("Falha na preparação do Qt",
                 "O ambiente anterior permanece selecionado.\n\n"
                 + details + "\n\nLog: " + str(log), parent=self)

    def _build_history(self):
        self.history_view = HistoryView(self.pages["historico"], on_choose=self._remember_history_selection)
        self.history_view.pack(fill="both", expand=True)

    def _remember_history_selection(self, path):
        # A evidência selecionada é um ZIP arquivado pelo painel, não um instalador.
        self.new_zip = Path(path)

    def _refresh_history(self):
        if hasattr(self, "history_view"):
            self.history_view.refresh()

    def _choose_result_zip(self):
        if hasattr(self, "history_view"):
            self.history_view.import_dialog()

    def _display_result_zip(self, path):
        if hasattr(self, "history_view"):
            self.history_view.import_file(Path(path))

    def _append(self, line: str):
        self.lines.append(line)
        if len(self.lines) > 1800:
            self.lines = self.lines[-1400:]
        self.log.configure(state="normal")
        self.log.insert("end", line.rstrip("\n") + "\n")
        if int(self.log.index("end-1c").split(".")[0]) > 700:
            self.log.delete("1.0", "110.0")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _choose_python(self):
        path = filedialog.askopenfilename(
            parent=self, title="Selecione o python.exe que possui PySide6",
            initialdir=str(Path.home()), filetypes=[("Executável Python", "python.exe"),
                                                     ("Executáveis", "*.exe")])
        if path:
            self.python_path.set(path)
            core.save_python_path(path)
            self._verify_python()

    def _probe(self, path: str) -> tuple[bool, str]:
        p = Path(path.strip().strip('"'))
        if not p.is_file() or p.name.lower() not in ("python.exe", "pythonw.exe"):
            return False, "Selecione um arquivo python.exe existente."
        try:
            r = subprocess.run([str(p), "-B", "-c",
                "import sys, PySide6; from PySide6 import QtWidgets, QtTest; "
                "print('Python:',sys.version.split()[0],'PySide6:',PySide6.__version__)"],
                capture_output=True, text=True, timeout=20,
                encoding="utf-8", errors="replace")
            if r.returncode == 0:
                return True, r.stdout.strip()
            return False, (r.stderr or r.stdout)[-500:].strip()
        except (OSError, subprocess.TimeoutExpired) as exc:
            return False, str(exc)

    def _verify_python(self):
        if self.running:
            return
        path = self.python_path.get().strip()
        self.status.set("Verificando o Python...")
        self.update_idletasks()
        ok, info = self._probe(path)
        if ok:
            core.save_python_path(path)
            self.status.set("Python e PySide6 disponíveis")
            self._append("PYTHON CONFIRMADO: " + info)
        else:
            self.status.set("Python Qt ainda não localizado")
            messagebox.showwarning("Python com PySide6", info or "Selecione outro python.exe.", parent=self)

    def _block_frozen_external(self, label: str) -> bool:
        if not getattr(sys, "frozen", False):
            return False
        messagebox.showwarning("Operacao indisponivel no EXE de QA",
            label + " depende de arquivos Python externos e permanece PENDENTE no EXE. "
            "Use um laboratorio Python isolado; nenhum subprocesso foi iniciado.", parent=self)
        return True

    def _start(self, mode: str):
        if self._block_frozen_external("Bateria geral ou compilacao"):
            return
        if self.running or getattr(self, "central_running", False):
            return
        python = self.python_path.get().strip().strip('"')
        self.status.set("Verificando ambiente...")
        self.update_idletasks()
        ok, desc = self._probe(python)
        if not ok:
            self.status.set("Aguardando seleção de Python Qt")
            messagebox.showwarning("Selecione Python com PySide6",
                "Selecione o python.exe da pasta qtvenv\\Scripts.\n\n" + desc,
                parent=self)
            return
        if not RUNNER.is_file():
            messagebox.showerror("Arquivo ausente", "homologador_windows.py não encontrado.", parent=self)
            return
        core.save_python_path(python)
        self.running = True
        self.run_started = time.time()
        self.new_zip = None
        self.lines = []
        self.result_text.set("O ZIP será criado ao final dos testes.")
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        for b in (self.run_btn, self.build_btn, self.select_btn, self.verify_btn):
            b.configure(state="disabled")
        self.status.set("Executando testes" if mode=="testes" else "Testando build em laboratório")
        self.progress.start(13)
        self._append("Python: " + desc)
        self._append("Iniciando: " + ("testes Qt e atualização" if mode=="testes"
                                   else "testes e compilação PyInstaller"))
        threading.Thread(target=self._worker, args=(python,mode), daemon=True).start()

    def _start_g5a(self):
        if getattr(sys, "frozen", False):
            messagebox.showwarning("G5-A indisponível no EXE de QA",
                "O ensaio G5-A depende de um interpretador Python isolado. "
                "Não executaremos o próprio EXE com argumentos Python.", parent=self)
            return
        if self.running or getattr(self, "central_running", False):return
        self.running=True
        self.run_started=time.time()
        self.new_zip=None
        self.lines=[]
        self.result_text.set("Gerando diagnóstico isolado G5-A...")
        self.log.configure(state="normal")
        self.log.delete("1.0","end")
        self.log.configure(state="disabled")
        for b in (self.run_btn,self.build_btn,self.select_btn,self.verify_btn):
            b.configure(state="disabled")
        self.progress.start(13)
        self.status.set("G5-A: verificando isolamento sintético; EXE não será executado")
        threading.Thread(target=self._worker_g5a,daemon=True).start()

    def _start_g5b(self):
        if self._block_frozen_external("G5-B"):
            return
        if self.running or getattr(self, "central_running", False):
            return
        python=self.python_path.get().strip().strip('"')
        ok,description=self._probe(python)
        if not ok:
            messagebox.showwarning("Ambiente Qt necessário",description,parent=self)
            return
        if not messagebox.askyesno("Executar G5-B no Windows Sandbox",
            "Este teste COMPILA uma cópia do M2 RC2 e abre o executável real SOMENTE na Área Restrita do Windows.\n\n"
            "O Sandbox terá rede e área de transferência desativadas. "
            "Somente arquivos de QA e uma pasta descartável de resultados serão mapeados.\n\n"
            "A compilação pode levar vários minutos. G5 não será aprovado automaticamente.\n\n"
            "Deseja iniciar o laboratório G5-B agora?",parent=self):
            return
        core.save_python_path(python)
        self.running=True
        self.run_started=time.time()
        self.new_zip=None
        self.lines=[]
        self.result_text.set("Preparando laboratório G5-B; aguarde...")
        self.log.configure(state="normal")
        self.log.delete("1.0","end")
        self.log.configure(state="disabled")
        for btn in (self.run_btn,self.build_btn,self.select_btn,self.verify_btn,self.g5a_btn,self.g5b_btn):
            btn.configure(state="disabled")
        self.progress.start(13)
        self.status.set("G5-B: compilando e aguardando Sandbox isolado")
        self._append("Python de laboratório: "+description)
        self.g5b_btn.configure(state="disabled")
        threading.Thread(target=self._worker_g5b,args=(python,),daemon=True).start()
        self.after(700,self._g5b_monitor_button)

    def _g5b_monitor_button(self):
        if self.running:
            self.after(700,self._g5b_monitor_button)
        else:
            self.g5b_btn.configure(state="normal")

    def _worker_g5b(self, python):
        if getattr(sys, "frozen", False):
            self.events.put(("crash", "Operacao externa indisponivel no EXE de QA"))
            return
        try:
            env=os.environ.copy()
            env["PYTHONUNBUFFERED"]="1"
            env["PYTHONDONTWRITEBYTECODE"]="1"
            for key in ("PYTHONPATH","QT_PLUGIN_PATH","QT_QPA_PLATFORM_PLUGIN_PATH"):
                env.pop(key,None)
            flags=getattr(subprocess,"CREATE_NO_WINDOW",0)
            proc=subprocess.Popen([python,"-u","-B",str(ROOT/"painel_g5_ui.py"),"--g5b"],
                                  cwd=str(ROOT),env=env,stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,encoding="utf-8",errors="replace",
                                  text=True,bufsize=1,creationflags=flags)
            for line in proc.stdout:
                self.events.put(("line",line.rstrip("\n")))
            self.events.put(("done",proc.wait()))
        except Exception as exc:
            self.events.put(("crash",repr(exc)))

    def _start_g5c(self):
        if self._block_frozen_external("G5-C"):
            return
        if self.running or getattr(self, "central_running", False):return
        python=self.python_path.get().strip().strip('"')
        ok,description=self._probe(python)
        if not ok:
            messagebox.showwarning("Ambiente Qt necessário",description,parent=self)
            return
        if not messagebox.askyesno("Executar G5-C no Windows Sandbox",
            "O teste compilará SOMENTE as fontes RC2 de QA e abrirá o executável dentro do Sandbox.\n\n"
            "Serão realizadas duas inicializações, tentativa de navegação e verificações em um banco NOVO, "
            "criado dentro do ambiente descartável. Rede e clipboard ficarão desativados.\n\n"
            "Ao concluir, feche manualmente o Windows Sandbox pela janela X. "
            "A instalação principal NÃO será modificada. Deseja iniciar?",parent=self):
            return
        core.save_python_path(python)
        self.running=True;self.run_started=time.time();self.new_zip=None;self.lines=[]
        self.result_text.set("Preparando laboratório G5-C; aguarde...")
        self.log.configure(state="normal");self.log.delete("1.0","end");self.log.configure(state="disabled")
        for btn in (self.run_btn,self.build_btn,self.select_btn,self.verify_btn,
                    self.g5a_btn,self.g5b_btn,self.g5c_btn):btn.configure(state="disabled")
        self.progress.start(13)
        self.status.set("G5-C: compilação e duas inicializações dentro do Windows Sandbox")
        self._append("Ambiente QA verificado: "+description)
        threading.Thread(target=self._worker_g5c,args=(python,),daemon=True).start()
        self.after(700,self._g5c_monitor_button)

    def _g5c_monitor_button(self):
        if self.running:self.after(700,self._g5c_monitor_button)
        else:
            for b in (self.g5a_btn,self.g5b_btn,self.g5c_btn):b.configure(state="normal")

    def _worker_g5c(self,python):
        if getattr(sys, "frozen", False):
            self.events.put(("crash", "Operacao externa indisponivel no EXE de QA"))
            return
        try:
            env=os.environ.copy();env["PYTHONUNBUFFERED"]="1";env["PYTHONDONTWRITEBYTECODE"]="1"
            for key in ("PYTHONPATH","QT_PLUGIN_PATH","QT_QPA_PLATFORM_PLUGIN_PATH"):
                env.pop(key,None)
            flags=getattr(subprocess,"CREATE_NO_WINDOW",0)
            proc=subprocess.Popen([python,"-u","-B",str(ROOT/"painel_g5_ui.py"),"--g5c"],
                cwd=str(ROOT),env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                encoding="utf-8",errors="replace",text=True,bufsize=1,creationflags=flags)
            for line in proc.stdout:self.events.put(("line",line.rstrip("\n")))
            self.events.put(("done",proc.wait()))
        except Exception as exc:self.events.put(("crash",repr(exc)))


    def _start_g6a(self):
        if self._block_frozen_external("G6-A"):
            return
        if self.running or getattr(self, "central_running", False):return
        python=self.python_path.get().strip().strip('"')
        ok,description=self._probe(python)
        if not ok:
            messagebox.showwarning('Ambiente Qt necessário',description,parent=self);return
        if not messagebox.askyesno('G6-A — Atualizador real, instalação fictícia',
            'O G6-A executa o motor ORIGINAL de atualização R1D sobre uma instalação '
            'DESCARTÁVEL com banco SQLite sintético e EXEs fictícios.\n\n'
            'Testa aplicação, falha antecipada e falha pós-commit com rollback. '
            'Não instala o M2, não executa o EXE nem conclui o G6.\n\nExecutar?',parent=self):return
        core.save_python_path(python)
        self.running=True;self.run_started=time.time();self.new_zip=None;self.lines=[]
        self.result_text.set('G6-A: preparando instalações de QA...')
        self.log.configure(state='normal');self.log.delete('1.0','end');self.log.configure(state='disabled')
        for btn in (self.run_btn,self.build_btn,self.select_btn,self.verify_btn,
                    self.g5a_btn,self.g5b_btn,self.g5c_btn,self.g6a_btn,self.g6b_btn,self.g6b2_btn):btn.configure(state='disabled')
        self.progress.start(13)
        self.status.set('G6-A: aplicação e rollback sobre banco sintético')
        self._append('Python: '+description)
        threading.Thread(target=self._worker_g6a,args=(python,),daemon=True).start()
        self.after(700,self._g6a_monitor_button)

    def _g6a_monitor_button(self):
        if self.running:self.after(700,self._g6a_monitor_button)
        else:
            for btn in (self.g5a_btn,self.g5b_btn,self.g5c_btn,self.g6a_btn,self.g6b_btn,self.g6b2_btn):
                btn.configure(state='normal')

    def _start_g6b(self):
        if self._block_frozen_external("G6-B1"):
            return
        if self.running or getattr(self, "central_running", False):return
        python=self.python_path.get().strip().strip('"')
        ok,description=self._probe(python)
        if not ok:
            messagebox.showwarning('Ambiente QA necessário',description,parent=self);return
        if not messagebox.askyesno('G6-B1 — EXEs reais no Windows Sandbox',
            'Este teste compila DOIS executáveis reais a partir de fontes de QA '
            'e um executor descartável. Inicia o Windows Sandbox com rede e '
            'clipboard desabilitados e testa o motor original do atualizador '
            'com binários reais pré-compilados e SQLite sintético.\n\n'
            'A instalação principal não é alterada. O G6-B2 e o Gate G7 '
            'continuam pendentes. A compilação pode consumir espaço e tempo.\n\n'
            'Executar?',parent=self):return
        core.save_python_path(python)
        self.running=True;self.run_started=time.time();self.new_zip=None;self.lines=[]
        self.result_text.set('G6-B1: iniciando compilação QA...')
        self.log.configure(state='normal');self.log.delete('1.0','end');self.log.configure(state='disabled')
        for btn in (self.run_btn,self.build_btn,self.select_btn,self.verify_btn,
                    self.g5a_btn,self.g5b_btn,self.g5c_btn,self.g6a_btn,self.g6b_btn,self.g6b2_btn):
            btn.configure(state='disabled')
        self.progress.start(13)
        self.status.set('G6-B1: builds reais e transação isolada no Sandbox')
        self._append('Python QA: '+description)
        threading.Thread(target=self._worker_g6b,args=(python,),daemon=True).start()
        self.after(700,self._g6a_monitor_button)

    def _start_g6b2(self):
        if self._block_frozen_external("G6-B2"):
            return
        if self.running or getattr(self, "central_running", False):return
        python=self.python_path.get().strip().strip('"')
        ok,description=self._probe(python)
        if not ok:
            messagebox.showwarning('Ambiente QA necessario',description,parent=self);return
        if not messagebox.askyesno('G6-B2 — build ORIGINAL no Windows Sandbox',
            'Executa o PyInstaller pelo motor original dentro do Windows Sandbox. '
            'A instalacao Python QA e suas dependencias serao mapeadas como SOMENTE LEITURA. '
            'Usa bancos sinteticos e fontes de QA. Nenhuma instalacao principal sera acessada. '
            'O processo pode levar muitos minutos e ocupar espaco. '
            'G6 e G7 permanecem bloqueados mesmo que o G6-B2 passe.\n\nExecutar?',parent=self):return
        core.save_python_path(python)
        self.running=True;self.run_started=time.time();self.new_zip=None;self.lines=[]
        self.result_text.set('G6-B2: preparando PyInstaller original isolado...')
        self.log.configure(state='normal');self.log.delete('1.0','end');self.log.configure(state='disabled')
        for btn in (self.run_btn,self.build_btn,self.select_btn,self.verify_btn,
                    self.g5a_btn,self.g5b_btn,self.g5c_btn,self.g6a_btn,self.g6b_btn,self.g6b2_btn):
            btn.configure(state='disabled')
        self.progress.start(13)
        self.status.set('G6-B2: compilacao real no Sandbox; G6/G7 bloqueados')
        self._append('Python QA: '+description)
        threading.Thread(target=self._worker_g6b2,args=(python,),daemon=True).start()
        self.after(700,self._g6a_monitor_button)

    def _worker_g6b2(self,python):
        if getattr(sys, "frozen", False):
            self.events.put(("crash", "Operacao externa indisponivel no EXE de QA"))
            return
        try:
            env=os.environ.copy();env['PYTHONUNBUFFERED']='1';env['PYTHONDONTWRITEBYTECODE']='1'
            for key in ('PYTHONPATH','PYTHONHOME','QT_PLUGIN_PATH','QT_QPA_PLATFORM_PLUGIN_PATH'):
                env.pop(key,None)
            flags=getattr(subprocess,'CREATE_NO_WINDOW',0)
            proc=subprocess.Popen([python,'-u','-B',str(ROOT/'painel_g6b2.py')],
                cwd=str(ROOT),env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                encoding='utf-8',errors='replace',text=True,bufsize=1,creationflags=flags)
            for line in proc.stdout:self.events.put(('line',line.rstrip('\n')))
            self.events.put(('done',proc.wait()))
        except Exception as exc:self.events.put(('crash',repr(exc)))

    def _worker_g6b(self,python):
        if getattr(sys, "frozen", False):
            self.events.put(("crash", "Operacao externa indisponivel no EXE de QA"))
            return
        try:
            env=os.environ.copy();env['PYTHONUNBUFFERED']='1';env['PYTHONDONTWRITEBYTECODE']='1'
            for key in ('PYTHONPATH','PYTHONHOME','QT_PLUGIN_PATH','QT_QPA_PLATFORM_PLUGIN_PATH'):
                env.pop(key,None)
            flags=getattr(subprocess,'CREATE_NO_WINDOW',0)
            proc=subprocess.Popen([python,'-u','-B',str(ROOT/'painel_g6b.py')],
                cwd=str(ROOT),env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                encoding='utf-8',errors='replace',text=True,bufsize=1,creationflags=flags)
            for line in proc.stdout:self.events.put(('line',line.rstrip('\n')))
            self.events.put(('done',proc.wait()))
        except Exception as exc:self.events.put(('crash',repr(exc)))

    def _worker_g6a(self,python):
        if getattr(sys, "frozen", False):
            self.events.put(("crash", "Operacao externa indisponivel no EXE de QA"))
            return
        try:
            env=os.environ.copy();env['PYTHONUNBUFFERED']='1';env['PYTHONDONTWRITEBYTECODE']='1'
            for key in ('PYTHONPATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM_PLUGIN_PATH'):
                env.pop(key,None)
            flags=getattr(subprocess,'CREATE_NO_WINDOW',0)
            proc=subprocess.Popen([python,'-u','-B',str(ROOT/'painel_g5_ui.py'),'--g6a'],
                cwd=str(ROOT),env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                encoding='utf-8',errors='replace',text=True,bufsize=1,creationflags=flags)
            for line in proc.stdout:self.events.put(('line',line.rstrip('\n')))
            self.events.put(('done',proc.wait()))
        except Exception as exc:self.events.put(('crash',repr(exc)))

    def _worker(self, python: str, mode: str):
        if getattr(sys, "frozen", False):
            self.events.put(("crash", "Operacao externa indisponivel no EXE de QA"))
            return
        try:
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            env["PYTHONUTF8"] = "1"
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            # Evita que variáveis globais levem plugins Qt estranhos à cópia QA.
            for key in ("PYTHONPATH", "QT_PLUGIN_PATH", "QT_QPA_PLATFORM_PLUGIN_PATH"):
                env.pop(key, None)
            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            process = subprocess.Popen(
                [python, "-u", "-B", str(RUNNER), "--modo", mode],
                cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace", bufsize=1,
                env=env, creationflags=flags)
            assert process.stdout is not None
            for line in process.stdout:
                self.events.put(("line", line.rstrip("\n")))
            code = process.wait()
            self.events.put(("done", code))
        except Exception as exc:
            self.events.put(("crash", repr(exc)))

    def _worker_g5a(self):
        if getattr(sys, "frozen", False):
            self.events.put(("crash", "Operacao externa indisponivel no EXE de QA"))
            return
        try:
            env=os.environ.copy()
            env["PYTHONUNBUFFERED"]="1"
            flags=getattr(subprocess,"CREATE_NO_WINDOW",0)
            proc=subprocess.Popen([sys.executable,"-u","-B",str(ROOT/"painel_g5_preflight.py")],
                                  cwd=str(ROOT),env=env,stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,encoding="utf-8",errors="replace",
                                  text=True,bufsize=1,creationflags=flags)
            for line in proc.stdout:
                self.events.put(("line",line.rstrip("\n")))
            self.events.put(("done",proc.wait()))
        except Exception as exc:
            self.events.put(("crash",repr(exc)))

    def _poll_queue(self):
        for _ in range(100):
            try:
                kind, value = self.events.get_nowait()
            except queue.Empty:
                break
            if kind == "line":
                self._append(value)
                path = core.parse_result_path(value)
                if path:
                    self.new_zip = path
            elif kind == "done":
                self._end_run(int(value), None)
            elif kind == "crash":
                self._end_run(1, value)
        self.after(130, self._poll_queue)

    def _end_run(self, code: int, crash: str | None):
        self.running = False
        self.progress.stop()
        for b in (self.run_btn, self.build_btn, self.select_btn, self.verify_btn):
            b.configure(state="normal")
        result = self.new_zip if self.new_zip and self.new_zip.is_file() else core.latest_result(self.run_started)
        if result is None:
            error = crash or ("O processo finalizou com código " + str(code) +
                              ", mas não foi encontrado um ZIP novo.")
            try:
                result = core.emergency_report(error, self.lines)
                self._append("DIAGNÓSTICO DO PAINEL CRIADO: " + str(result))
            except OSError as exc:
                self.status.set("Falha ao salvar relatório")
                messagebox.showerror("Falha no diagnóstico", str(exc), parent=self)
                return
        self.new_zip = result
        self.result_text.set(str(result))
        try:
            result_status = core.inspect_result(result) if result.name.startswith("RESULTADOS_") else None
            if result_status is None:
                self.status.set("Encerrado com diagnóstico — envie o ZIP")
            elif result_status.get("falhas", 0) or code != 0:
                self.status.set("Concluído com falhas — envie o ZIP")
            elif result_status.get("bloqueados", 0):
                self.status.set("Concluído com etapas bloqueadas — envie o ZIP")
            else:
                self.status.set("Testes concluídos — ZIP pronto para enviar")
            if result_status:
                self._append("RESUMO: " + str(result_status))
        except Exception as exc:
            self.status.set("ZIP criado; leitura do resumo falhou — envie para análise")
            self._append("Não foi possível resumir: " + str(exc))
        self._append("RESULTADO PARA ENVIAR AO CHATGPT: " + str(result))
        if result.name.startswith("RESULTADOS_HOMOLOGACAO_WINDOWS_") and hasattr(self, "history_view"):
            try:
                _, novo = self.history_view.import_file(result)
                self._append("HISTÓRICO LOCAL: " + ("evidência registrada" if novo else "duplicata identificada"))
            except (OSError, ValueError, RuntimeError) as exc:
                self._append("HISTÓRICO NÃO REGISTRADO: " + str(exc))
                self.status.set("ZIP criado; histórico pendente de importação manual")
        messagebox.showinfo("Homologação finalizada",
            "O ZIP foi gerado.\n\nClique em 'Abrir pasta do resultado' e anexe-o à conversa do ChatGPT.\n\n"
            "Nenhuma atualização do VighnaStudy foi instalada.",
            parent=self)

    def _open_result_folder(self):
        folder = self.new_zip.parent if self.new_zip and self.new_zip.is_file() else core.diagnostics_folder()
        try:
            if sys.platform == "win32":
                os.startfile(str(folder))
            else:
                messagebox.showinfo("Pasta", str(folder), parent=self)
        except OSError as exc:
            messagebox.showerror("Não foi possível abrir a pasta", str(exc), parent=self)

    def _copy_result(self):
        if not self.new_zip:
            messagebox.showinfo("Ainda sem resultado", "Execute os testes primeiro.", parent=self)
            return
        self.clipboard_clear()
        self.clipboard_append(str(self.new_zip))
        self.update_idletasks()
        self.status.set("Caminho do ZIP copiado")

# V3.1.51: diagnósticos de leitura por contrato fechado, antes de criar Tkinter.
# Sem comandos, caminhos, arquivos arbitrários, rede, backups ou atualização.
QA_CHILD_MARKER = "--vighnalab-qa-child"
QA_PROTOCOL = "1"
QA_ALLOWED_OPS = frozenset(("ping", "ambiente", "identidade", "componentes", "central_leitura", "central_segura"))
QA_COMPONENTS = ("painel_core", "painel_atualizador", "painel_central_qa", "painel_g7")
# Atualizar este fingerprint somente ao versionar PAINEL_VERSAO.json.
QA_IDENTITY_VERSION = "3.1.53"
QA_IDENTITY_SHA256 = "91f0fbe8ed57f5d92330798e09605a1c0f2fd8d29332247cc33bc648785b8e56"



def _qa_identity():
    """Ler exclusivamente identidade fixa e validar hash; nunca consultar CWD."""
    import hashlib
    frozen = bool(getattr(sys, "frozen", False))
    if frozen and not getattr(sys, "_MEIPASS", None):
        raise RuntimeError("Identidade interna indisponível")
    folder = Path(sys._MEIPASS) if frozen else ROOT
    target = folder / "PAINEL_VERSAO.json"
    try:
        if folder.is_symlink() or (getattr(folder, "is_junction", lambda: False)()):
            raise ValueError("Raiz de recursos redirecionada")
        if target.is_symlink() or (getattr(target, "is_junction", lambda: False)()):
            raise ValueError("Recurso redirecionado")
        if not target.is_file() or target.stat().st_size > 4096:
            raise ValueError("Identidade ausente ou extensa")
        data = target.read_bytes()
        if len(data) > 4096 or hashlib.sha256(data).hexdigest() != QA_IDENTITY_SHA256:
            raise ValueError("Identidade divergente")
        doc = json.loads(data.decode("utf-8"))
        if doc != {"component": "vighna-panel", "version": QA_IDENTITY_VERSION}:
            raise ValueError("Versao do recurso divergente")
        return {"componente": "vighna-panel", "versao": QA_IDENTITY_VERSION}
    except (OSError, ValueError, UnicodeError, TypeError) as exc:
        raise RuntimeError("Identidade interna indisponível") from exc


def _qa_child_dispatch(args):
    """Contrato posicional fixo; não recebe caminhos nem comandos Python."""
    if (len(args) != 4 or args[0] != QA_CHILD_MARKER
            or args[1] != "--protocolo" or args[2] != QA_PROTOCOL
            or args[3] not in QA_ALLOWED_OPS):
        print(json.dumps({"status": "REJEITADO", "motivo": "Protocolo interno não autorizado"},
                         ensure_ascii=False), file=sys.stderr)
        return 2
    op = args[3]
    data = {"protocolo": 1, "operacao": op, "resultado": "OK",
            "frozen": bool(getattr(sys, "frozen", False))}
    if op in ("central_leitura", "central_segura"):
        # Escrita apenas do ZIP de evidências em pasta temporária fixa.
        # NÃO invoca a bateria inteira, não recebe caminhos do chamador.
        try:
            target = Path(__import__("tempfile").gettempdir()) / "VighnaLab_QA_Leitura_EXE"
            profiles = (("diagnosticos_exe", "integridade", "sqlite")
                        if op == "central_segura" else ("diagnosticos_exe",))
            res = central_qa.execute(ROOT, selected=profiles, output_dir=target)
            if res["resultado"] != "APROVADO_ESCOPO":
                raise RuntimeError("Diagnóstico isolado pendente")
            print(json.dumps({"protocolo": 1, "operacao": op, "resultado": "OK",
                              "frozen": bool(getattr(sys, "frozen", False)),
                              "arquivo": res["arquivo"]}, ensure_ascii=False))
            return 0
        except (OSError, RuntimeError, ValueError, central_qa.CentralQAError):
            print(json.dumps({"status": "FALHOU", "motivo": "Central de leitura indisponível"},
                             ensure_ascii=False), file=sys.stderr)
            return 3
    if op == "ambiente":
        data["plataforma"] = sys.platform
        data["python"] = f"{sys.version_info.major}.{sys.version_info.minor}"
    elif op == "identidade":
        try:
            data.update(_qa_identity())
        except RuntimeError:
            # Falha fechada, sem caminhos locais no erro.
            print(json.dumps({"status": "FALHOU", "motivo": "Identidade interna indisponível"},
                             ensure_ascii=False), file=sys.stderr)
            return 3
    elif op == "componentes":
        presentes = {name: (sys.modules.get(name) is not None) for name in QA_COMPONENTS}
        data["modulos_importados"] = presentes
        if not all(presentes.values()):
            data["resultado"] = "PENDENTE"
            print(json.dumps(data, ensure_ascii=False, sort_keys=True))
            return 3
    print(json.dumps(data, ensure_ascii=False, sort_keys=True))
    return 0


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    # Qualquer argumento recusa o fluxo GUI, inclusive -m, -c e scripts.
    if args:
        return _qa_child_dispatch(args)
    if sys.platform != "win32":
        print("Este painel destina-se ao Windows. Teste de GUI não executado neste ambiente.")
        return 77
    Painel().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
