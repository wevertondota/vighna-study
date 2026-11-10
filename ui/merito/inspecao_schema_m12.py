"""M12 — inspeção somente leitura de schema SQLite em cópia de teste.

Não executa banco.py, não cria tabelas, não calcula conquistas, não grava dados.
Execute apenas com uma cópia do banco de um clone autorizado.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from contextlib import closing
import sqlite3

REQUISITOS = {
    "concursos": frozenset({"id"}),
    "tentativas_questoes": frozenset({"id","sessao_id","concurso_id","respondida_em","correta"}),
    "sessoes_questoes": frozenset({"id","origem","modo","encerrado_em","concluida"}),
    "simulados": frozenset({"sessao_id"}),
}

class EsquemaM12Invalido(RuntimeError):
    pass

@dataclass(frozen=True)
class DiagnosticoSchemaM12:
    compativel: bool
    tabelas_auditadas: tuple[str,...]
    pendencias: tuple[str,...]
    digest_estrutura: str


def inspecionar_schema(caminho: str | Path) -> DiagnosticoSchemaM12:
    p = Path(caminho).expanduser().resolve(strict=True)
    if not p.is_file():
        raise EsquemaM12Invalido("Somente arquivo SQLite explícito")
    pendencias = []
    descricoes = []
    try:
        with closing(sqlite3.connect(p.as_uri() + '?mode=ro', uri=True, timeout=5.0)) as cx:
            cx.execute('PRAGMA query_only=ON')
            cx.execute('BEGIN')
            for tabela,requeridas in sorted(REQUISITOS.items()):
                linha = cx.execute('SELECT type FROM sqlite_master WHERE name=?',(tabela,)).fetchone()
                if not linha or linha[0] != 'table':
                    pendencias.append(f'Tabela ausente: {tabela}')
                    continue
                cols = cx.execute(f'PRAGMA table_info({tabela})').fetchall()
                desc = tuple((str(x[1]),str(x[2]),int(x[3]),int(x[5])) for x in cols)
                descricoes.append((tabela,desc))
                presentes={x[0] for x in desc}
                if requeridas - presentes:
                    pendencias.append(f'Colunas ausentes em {tabela}: {sorted(requeridas-presentes)}')
                if tabela == 'tentativas_questoes' and next((x[3] for x in desc if x[0]=='id'),0) != 1:
                    pendencias.append('Identificador de tentativa sem chave primária')
            cx.execute('ROLLBACK')
    except sqlite3.Error as exc:
        raise EsquemaM12Invalido('Não foi possível auditar o schema em modo somente leitura') from exc
    import json
    digest=sha256(json.dumps(descricoes,sort_keys=True,ensure_ascii=True).encode()).hexdigest()
    return DiagnosticoSchemaM12(not pendencias, tuple(x[0] for x in descricoes),tuple(pendencias),digest)
