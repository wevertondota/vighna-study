# -*- coding: utf-8 -*-
"""Exibição V2-B: índice local, filtros, comparação e backup de evidências.

Apenas leitura de metadados dos ZIPs escolhidos. Não executa arquivos.
"""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from painel_historico import HistoryError, HistoryStore

CATEGORIES = ('Todas', 'Qt', 'SQLite / Atualização', 'Segurança', 'PyInstaller', 'Integridade', 'Outros')
STATES = ('Todos', 'Aprovados', 'Com falhas', 'Bloqueados')


class HistoryView(tk.Frame):
    def __init__(self, parent, *, on_choose=None):
        super().__init__(parent, bg='#f5f7fb')
        self.on_choose = on_choose
        self.store = HistoryStore()
        self.category = tk.StringVar(value='Todas')
        self.state = tk.StringVar(value='Todos')
        self.query = tk.StringVar(value='')
        self.summary = tk.StringVar(value='Histórico local pronto. Importe ZIPs antigos ou execute novos testes.')
        self.selected_text = tk.StringVar(value='Selecione uma execução para ver as etapas.')
        self._build()
        self.refresh()

    def _title(self, parent, text):
        tk.Label(parent,text=text,bg='#f5f7fb',fg='#193b59',font=('Segoe UI',19,'bold')).pack(anchor='w')


    def _build(self):
        fundo = "#f5f7fb"

        self._title(self, "Evidências e histórico")

        subtitulo = tk.Label(
            self,
            text="Consulte execuções, filtre resultados e compare evidências verificadas.",
            bg=fundo, fg="#607488",
            font=("Segoe UI", 9),
            anchor="w", justify="left"
        )
        subtitulo.pack(fill="x", pady=(3, 12))

        operacoes = tk.Frame(
            self, bg="white",
            highlightthickness=1,
            highlightbackground="#e1e8f0"
        )
        operacoes.pack(fill="x", pady=(0, 10))

        tk.Label(
            operacoes,
            text="OPERAÇÕES COM EVIDÊNCIAS",
            bg="white", fg="#536c83",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=14, pady=(12, 8))

        linha_principal = ttk.Frame(operacoes)
        linha_principal.pack(fill="x", padx=14, pady=(0, 7))

        ttk.Button(
            linha_principal,
            text="Importar ZIPs",
            command=self.import_dialog
        ).pack(side="left")

        ttk.Button(
            linha_principal,
            text="Exportar histórico",
            command=self.export_dialog
        ).pack(side="left", padx=(8, 0))

        ttk.Button(
            linha_principal,
            text="Atualizar lista",
            command=self.refresh
        ).pack(side="right")

        linha_comparacao = ttk.Frame(operacoes)
        linha_comparacao.pack(
            fill="x", padx=14, pady=(0, 12)
        )

        ttk.Button(
            linha_comparacao,
            text="Comparar duas execuções",
            command=self.compare_selected
        ).pack(side="left")

        ttk.Label(
            linha_comparacao,
            text="Selecione duas linhas com Ctrl + clique.",
            style="Sub.TLabel"
        ).pack(side="left", padx=(10, 0))

        filtros = tk.Frame(
            self, bg="white",
            highlightthickness=1,
            highlightbackground="#e1e8f0"
        )
        filtros.pack(fill="x", pady=(0, 10))

        tk.Label(
            filtros,
            text="FILTRAR EXECUÇÕES",
            bg="white", fg="#536c83",
            font=("Segoe UI", 9, "bold")
        ).grid(
            row=0, column=0,
            columnspan=4, sticky="w",
            padx=14, pady=(11, 7)
        )

        ttk.Label(
            filtros, text="Categoria"
        ).grid(
            row=1, column=0,
            sticky="w", padx=(14, 6)
        )

        ttk.Combobox(
            filtros,
            textvariable=self.category,
            values=CATEGORIES,
            state="readonly",
            width=20
        ).grid(
            row=1, column=1,
            sticky="ew", padx=(0, 12)
        )

        ttk.Label(
            filtros, text="Situação"
        ).grid(
            row=1, column=2,
            sticky="w", padx=(0, 6)
        )

        ttk.Combobox(
            filtros,
            textvariable=self.state,
            values=STATES,
            state="readonly",
            width=17
        ).grid(
            row=1, column=3,
            sticky="ew", padx=(0, 14)
        )

        ttk.Label(
            filtros, text="Pesquisar"
        ).grid(
            row=2, column=0,
            sticky="w", padx=(14, 6),
            pady=(9, 12)
        )

        busca = ttk.Entry(
            filtros, textvariable=self.query
        )
        busca.grid(
            row=2, column=1,
            columnspan=3, sticky="ew",
            padx=(0, 14), pady=(9, 12)
        )

        filtros.grid_columnconfigure(1, weight=2)
        filtros.grid_columnconfigure(3, weight=1)

        for variavel in (self.category, self.state):
            variavel.trace_add(
                "write", lambda *_: self.refresh()
            )
        busca.bind(
            "<KeyRelease>", lambda e: self.refresh()
        )

        resumo = tk.Label(
            self,
            textvariable=self.summary,
            bg="#e9f0f7",
            fg="#365a76",
            anchor="w",
            justify="left",
            font=("Segoe UI", 9),
            padx=12, pady=8
        )
        resumo.pack(fill="x", pady=(0, 9))

        area = tk.Frame(self, bg=fundo)
        area.pack(fill="both", expand=True)

        detalhes = ttk.LabelFrame(
            area,
            text="Detalhes da execução selecionada",
            padding=9
        )
        detalhes.pack(
            side="bottom", fill="x",
            pady=(9, 0)
        )

        texto_selecionado = ttk.Label(
            detalhes,
            textvariable=self.selected_text,
            style="Sub.TLabel"
        )
        texto_selecionado.pack(
            fill="x", pady=(0, 7)
        )

        quadro_etapas = ttk.Frame(detalhes)
        quadro_etapas.pack(fill="x")

        colunas_etapas = (
            "area", "etapa", "status", "testes"
        )
        self.steps = ttk.Treeview(
            quadro_etapas,
            columns=colunas_etapas,
            show="headings", height=4
        )

        for chave, titulo, largura in (
            ("area", "Área", 110),
            ("etapa", "Etapa", 245),
            ("status", "Situação", 105),
            ("testes", "Testes", 60)
        ):
            self.steps.heading(chave, text=titulo)
            self.steps.column(
                chave,
                width=largura,
                minwidth=55,
                stretch=(chave == "etapa"),
                anchor="w" if chave == "etapa"
                else "center"
            )

        barra_etapas = ttk.Scrollbar(
            quadro_etapas,
            orient="vertical",
            command=self.steps.yview
        )
        self.steps.configure(
            yscrollcommand=barra_etapas.set
        )
        barra_etapas.pack(
            side="right", fill="y"
        )
        self.steps.pack(
            side="left", fill="x", expand=True
        )

        tabela = tk.Frame(
            area, bg="white",
            highlightthickness=1,
            highlightbackground="#e1e8f0"
        )
        tabela.pack(
            side="top", fill="both", expand=True
        )

        tk.Label(
            tabela,
            text="EXECUÇÕES REGISTRADAS",
            bg="white", fg="#536c83",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=13, pady=(11, 7))

        quadro_tabela = ttk.Frame(tabela)
        quadro_tabela.pack(
            fill="both", expand=True,
            padx=10, pady=(0, 10)
        )

        colunas = (
            "data", "arquivo", "modo",
            "aprovados", "falhas", "bloqueados"
        )

        self.table = ttk.Treeview(
            quadro_tabela,
            columns=colunas,
            show="headings",
            selectmode="extended",
            height=7
        )

        for chave, titulo, largura in (
            ("data", "Importado em", 118),
            ("arquivo", "Arquivo", 190),
            ("modo", "Modo", 68),
            ("aprovados", "OK", 58),
            ("falhas", "Falhas", 60),
            ("bloqueados", "Bloqueios", 74)
        ):
            self.table.heading(
                chave, text=titulo
            )
            self.table.column(
                chave, width=largura,
                minwidth=48,
                stretch=(chave == "arquivo"),
                anchor="w" if chave == "arquivo"
                else "center"
            )

        self.table.tag_configure(
            "falhas", foreground="#a14336"
        )
        self.table.tag_configure(
            "bloqueados", foreground="#986a2b"
        )
        self.table.tag_configure(
            "aprovado", foreground="#21604e"
        )

        barra = ttk.Scrollbar(
            quadro_tabela,
            orient="vertical",
            command=self.table.yview
        )
        self.table.configure(
            yscrollcommand=barra.set
        )

        barra.pack(side="right", fill="y")
        self.table.pack(
            side="left",
            fill="both", expand=True
        )
        self.table.bind(
            "<<TreeviewSelect>>",
            self._on_select
        )

        self.bind(
            "<Configure>",
            lambda e: (
                subtitulo.configure(
                    wraplength=max(200, e.width - 24)
                ),
                resumo.configure(
                    wraplength=max(200, e.width - 30)
                ),
                texto_selecionado.configure(
                    wraplength=max(200, e.width - 50)
                )
            )
        )

    def refresh(self):
        selection=self.table.selection()
        rows=self.store.list_runs(category=self.category.get(),status=self.state.get(),query=self.query.get().strip())
        self.table.delete(*self.table.get_children())
        for row in rows:
            when=row['imported_at'][:16].replace('T',' ')
            tag='falhas' if row['falhas'] else 'bloqueados' if row['bloqueados'] else 'aprovado'
            self.table.insert('', 'end', iid=str(row['id']),values=(when,row['filename'],row['modo'],
                row['aprovados'],row['falhas'],row['bloqueados']),tags=(tag,))
        restore=[k for k in selection if self.table.exists(k)]
        if restore:
            self.table.selection_set(restore)
        self.summary.set(f'{len(rows)} execução(ões) visíveis · {len(self.store.list_runs())} no histórico total. '
                         'Use Ctrl + clique para selecionar duas execuções e compará-las.')
        self._on_select()

    def _on_select(self, _evt=None):
        selected=self.table.selection()
        self.steps.delete(*self.steps.get_children())
        if len(selected)==1:
            idx=int(selected[0])
            steps=self.store.steps_for(idx,self.category.get())
            for s in steps:
                self.steps.insert('','end',values=(s['category'],s['step_key'],s['status'],
                                                  s['checks'] if s['checks'] is not None else '—'))
            self.selected_text.set(f'Execução #{idx} · {len(steps)} etapa(s) na categoria selecionada')
            if self.on_choose:
                try:
                    self.on_choose(self.store.evidence_path(idx))
                except HistoryError:
                    pass
        elif len(selected)==2:
            self.selected_text.set('Duas execuções selecionadas. Clique em Comparar duas execuções.')
        else:
            self.selected_text.set('Selecione uma execução; ou duas com Ctrl + clique para comparar.')

    def import_file(self, source: Path, *, notify=False):
        """Usado após a execução e ao importar manualmente; retorna ID e inclusão."""
        idx, inserted=self.store.import_zip(Path(source))
        self.refresh()
        if self.table.exists(str(idx)):
            self.table.selection_set(str(idx))
            self.table.see(str(idx))
        if notify:
            messagebox.showinfo('Histórico',
                'Evidência registrada com SHA-256.' if inserted else 'Esse mesmo ZIP já consta no histórico.',parent=self)
        return idx,inserted

    def import_dialog(self):
        paths=filedialog.askopenfilenames(parent=self,title='Importar ZIPs de homologação',
                                          filetypes=[('Evidências de homologação','*.zip')])
        if not paths:
            return
        added=duplicate=0
        errors=[]
        for p in paths:
            try:
                _,ok=self.import_file(Path(p))
                if ok:added+=1
                else:duplicate+=1
            except (OSError,ValueError,RuntimeError) as exc:
                errors.append(Path(p).name+': '+str(exc))
        text=f'{added} arquivo(s) adicionado(s); {duplicate} duplicado(s).'
        if errors:
            text+='\n\nArquivos não importados:\n'+'\n'.join(errors[:8])
            messagebox.showwarning('Importação do histórico',text,parent=self)
        else:
            messagebox.showinfo('Importação do histórico',text,parent=self)

    def compare_selected(self):
        selected=self.table.selection()
        if len(selected)!=2:
            messagebox.showinfo('Comparação','Selecione exatamente duas linhas usando Ctrl + clique.',parent=self)
            return
        before,after=sorted(map(int,selected))
        try:
            comparison=self.store.compare(before,after)
        except (HistoryError,OSError) as exc:
            messagebox.showerror('Comparação',str(exc),parent=self)
            return
        popup=tk.Toplevel(self)
        popup.title('Comparação de homologações')
        popup.geometry('730x540')
        popup.transient(self.winfo_toplevel())
        area=scrolledtext.ScrolledText(popup,wrap='word',font=('Consolas',10))
        area.pack(fill='both',expand=True,padx=14,pady=14)
        a,b=comparison['antes'],comparison['depois']
        lines=[f'ANTES: #{a["id"]} {a["filename"]}',f'DEPOIS: #{b["id"]} {b["filename"]}',
               f'REGRESSÕES DE ESTADO: {len(comparison["regressoes"])}',
               f'MELHORIAS DE ESTADO: {len(comparison["melhorias"])}','',
               f'MUDANÇAS ENTRE ETAPAS ({len(comparison["mudancas"])}):']
        lines.extend(f'  {x["categoria"]} / {x["etapa"]}: {x["antes"]} → {x["depois"]}' for x in comparison['mudancas'])
        lines.append('\n'+comparison['observacao'])
        area.insert('1.0','\n'.join(lines))
        area.configure(state='disabled')

    def export_dialog(self):
        filename='VighnaStudy_HISTORICO_HOMOLOGACOES_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.zip'
        target=filedialog.asksaveasfilename(parent=self,title='Exportar histórico e evidências',
                                            initialfile=filename,defaultextension='.zip',
                                            filetypes=[('ZIP de backup','*.zip')])
        if not target:
            return
        try:
            out=self.store.export_backup(Path(target))
            messagebox.showinfo('Exportação concluída',f'Backup salvo em:\n{out}\n\nGuarde em lugar seguro.',parent=self)
        except (HistoryError,OSError,zipfile.BadZipFile) as exc:
            messagebox.showerror('Exportação não realizada',str(exc),parent=self)
