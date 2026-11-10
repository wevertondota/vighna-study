"""VighnaStudy Histórico V2 — Etapa N: protótipo de preservação relacional.

Desenvolvido a partir do banco.py da coleta J (SHA256 registrado no relatório N).
NÃO EXECUTAR NA INSTALAÇÃO REAL até integração, backup e homologação.

Papel: preservar revisões comprovadas quando uma disciplina ou tópico é
removido administrativamente; guardar linhagens antes de excluir concurso.
A correção de revisões automáticas inválidas usa DELETE FROM revisoes
sem remoção de tópico, e não é arquivada por estes gatilhos.

Não bloqueia a exclusão administrativa; não escreve em banco externo; aplica
alterações SOMENTE à conexão SQLite fornecida pelo chamador.
"""
from __future__ import annotations

import re
import sqlite3

_REQUIRED = {
    "concursos": {"id", "nome"},
    "disciplinas": {"id", "nome"},
    "topicos": {"id", "disciplina_id", "nome"},
    "revisoes": {"id", "topico_id", "concurso_id", "data", "questoes", "acertos"},
    "tentativas_questoes": {"id", "concurso_id"},
}


def _fields(con: sqlite3.Connection, name: str) -> set[str]:
    return {str(r[1]) for r in con.execute(f'PRAGMA table_info("{name}")')}


def _json_revisao(con: sqlite3.Connection) -> str:
    # As colunas vêm apenas do próprio SQLite; nunca de entrada do usuário.
    fields = [str(row[1]) for row in con.execute('PRAGMA table_info("revisoes")')]
    if len(fields) > 55:
        raise RuntimeError('Número inesperado de colunas em revisoes; análise manual necessária')
    if any(not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', s) for s in fields):
        raise RuntimeError('Identificador de coluna não suportado no instantâneo')
    args = []
    for field in fields:
        args.append("'" + field + "'")
        args.append('r."' + field + '"')
    return 'json_object(' + ', '.join(args) + ')'


def garantir_schema_preservacao(con: sqlite3.Connection) -> dict:
    """Cria tabelas e gatilhos (idempotentes), na transação do chamador.

    O chamador deve fornecer conexão rw para um CLONE, com foreign_keys ON,
    depois que as tabelas e migrações de colunas do VighnaStudy existirem.
    """
    for table, required in _REQUIRED.items():
        absent = required - _fields(con, table)
        if absent:
            raise RuntimeError(f'Esquema incompatível em {table}: {sorted(absent)}')
    try:
        con.execute("SELECT json_object('probe', 1)").fetchone()
    except sqlite3.DatabaseError as ex:
        raise RuntimeError('Esta compilação SQLite não oferece json_object') from ex

    con.execute('''CREATE TABLE IF NOT EXISTS historico_v2_revisoes_arquivadas (
        revisao_id INTEGER PRIMARY KEY,
        concurso_id INTEGER,
        topico_id INTEGER NOT NULL,
        topico_nome TEXT,
        disciplina_id INTEGER,
        disciplina_nome TEXT,
        data TEXT NOT NULL,
        questoes INTEGER NOT NULL,
        acertos INTEGER NOT NULL,
        origem TEXT,
        dados_json TEXT NOT NULL,
        arquivada_em TEXT NOT NULL DEFAULT (datetime('now')),
        operacao TEXT NOT NULL
    )''')
    con.execute('''CREATE INDEX IF NOT EXISTS idx_hist_v2_revisoes_concurso_data
        ON historico_v2_revisoes_arquivadas(concurso_id, data)''')
    con.execute('''CREATE TABLE IF NOT EXISTS historico_v2_concursos_excluidos (
        concurso_id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL,
        excluido_em TEXT NOT NULL DEFAULT (datetime('now'))
    )''')
    con.execute('''CREATE TABLE IF NOT EXISTS historico_v2_vinculos_excluidos (
        tipo TEXT NOT NULL CHECK(tipo IN ('tentativa','revisao')),
        registro_id INTEGER NOT NULL,
        concurso_id INTEGER NOT NULL,
        PRIMARY KEY (tipo, registro_id)
    )''')
    con.execute('''CREATE INDEX IF NOT EXISTS idx_hist_v2_vinculos_concurso
        ON historico_v2_vinculos_excluidos(concurso_id, tipo)''')

    fields = _fields(con, 'revisoes')
    origem = 'r.origem' if 'origem' in fields else "'manual'"
    snap = _json_revisao(con)
    # BEFORE DELETE ON disciplinas grava nome de disciplina enquanto ela existe;
    # INSERT OR IGNORE evita duplicar quando a FK exclui os tópicos em cascata.
    con.execute(f'''CREATE TRIGGER IF NOT EXISTS trg_hist_v2_disciplina_archive
    BEFORE DELETE ON disciplinas BEGIN
      INSERT OR IGNORE INTO historico_v2_revisoes_arquivadas
      (revisao_id, concurso_id, topico_id, topico_nome, disciplina_id,
       disciplina_nome, data, questoes, acertos, origem, dados_json, operacao)
      SELECT r.id, COALESCE(r.concurso_id,(SELECT v.concurso_id FROM historico_v2_vinculos_excluidos v WHERE v.tipo='revisao' AND v.registro_id=r.id)), r.topico_id, t.nome, OLD.id, OLD.nome,
             r.data, r.questoes, r.acertos, {origem}, {snap}, 'exclusao_disciplina'
      FROM revisoes r JOIN topicos t ON t.id = r.topico_id
      WHERE t.disciplina_id = OLD.id;
    END''')
    con.execute(f'''CREATE TRIGGER IF NOT EXISTS trg_hist_v2_topico_archive
    BEFORE DELETE ON topicos BEGIN
      INSERT OR IGNORE INTO historico_v2_revisoes_arquivadas
      (revisao_id, concurso_id, topico_id, topico_nome, disciplina_id,
       disciplina_nome, data, questoes, acertos, origem, dados_json, operacao)
      SELECT r.id, COALESCE(r.concurso_id,(SELECT v.concurso_id FROM historico_v2_vinculos_excluidos v WHERE v.tipo='revisao' AND v.registro_id=r.id)), OLD.id, OLD.nome, OLD.disciplina_id,
             (SELECT d.nome FROM disciplinas d WHERE d.id=OLD.disciplina_id),
             r.data, r.questoes, r.acertos, {origem}, {snap}, 'exclusao_topico'
      FROM revisoes r WHERE r.topico_id = OLD.id;
    END''')
    # Quando um concurso é excluído, as FKs anulam o concurso_id de tentativas
    # e revisões. A ligação antiga é mantida separadamente, sem alterar os
    # registros nem interromper a exclusão do concurso.
    con.execute('''CREATE TRIGGER IF NOT EXISTS trg_hist_v2_concurso_linhagem
    BEFORE DELETE ON concursos BEGIN
      INSERT OR IGNORE INTO historico_v2_concursos_excluidos(concurso_id,nome)
      VALUES(OLD.id, OLD.nome);
      INSERT OR IGNORE INTO historico_v2_vinculos_excluidos(tipo,registro_id,concurso_id)
      SELECT 'tentativa',id,OLD.id FROM tentativas_questoes WHERE concurso_id=OLD.id;
      INSERT OR IGNORE INTO historico_v2_vinculos_excluidos(tipo,registro_id,concurso_id)
      SELECT 'revisao',id,OLD.id FROM revisoes WHERE concurso_id=OLD.id;
    END''')
    return {'schema': 'historico_preservacao_v2_n', 'triggers': 3, 'somente_clone': True}
