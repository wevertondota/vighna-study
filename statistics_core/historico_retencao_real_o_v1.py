"""Camada O: protege evidências de legado Excel e sessões, sobre a camada N.

NÃO INSTALAR até aprovação de esquema, backup e ensaio Windows.
Todas as operações são transacionais na conexão SQLite do chamador.

Revisões pré-existentes ao programa aparecem no banco como CONTADORES em
controle_topico; não se presume data, origem de sessão nem perfil específico.
Não faz nenhuma exclusão e não reclassifica uma revisão manual como erro.
"""
from __future__ import annotations

import sqlite3
from .historico_retencao_real_n_v1 import garantir_schema_preservacao as _garantir_n


def _criar_schema_preservacao(con: sqlite3.Connection) -> dict:
    """Estende a proteção N após as tabelas nativas estarem plenamente criadas.

    Retorna metadados para diagnóstico. Nunca executa commit ou rollback.
    Gatilhos BEFORE DELETE: snapshots anteriores às cascatas SQLite.
    """
    if con.execute('PRAGMA foreign_keys').fetchone()[0] != 1:
        raise RuntimeError('foreign_keys deve estar ativo para proteção das cascatas')
    for name, campos in {
        'controle_topico': {'topico_id', 'revisoes_iniciais', 'percentual_inicial'},
        'sessoes_questoes': {'id', 'concurso_id', 'iniciado_em', 'encerrado_em'},
        'simulados': {'id', 'sessao_id', 'concurso_id', 'criado_em'},
        'efetividade_sessoes': {'sessao_id', 'concurso_id', 'criado_em', 'respostas', 'acertos'},
        'tentativas_questoes': {'sessao_id', 'correta'},
    }.items():
        achados = {str(r[1]) for r in con.execute(f'PRAGMA table_info("{name}")')}
        if campos - achados:
            raise RuntimeError(f'Esquema incompatível em {name}: {sorted(campos-achados)}')

    _garantir_n(con)

    # NÃO atribuir revisões importadas a perfis por inferência: o mesmo tópico
    # pode pertencer a mais de um concurso. Também não fabricar datas.
    con.execute('''CREATE TABLE IF NOT EXISTS historico_v2_controles_legados (
        topico_id INTEGER PRIMARY KEY,
        topico_nome TEXT NOT NULL,
        disciplina_id INTEGER NOT NULL,
        disciplina_nome TEXT,
        revisoes_iniciais INTEGER NOT NULL DEFAULT 0,
        percentual_inicial REAL,
        observacao_inicial TEXT,
        texto_erros_inicial TEXT,
        continuacao_inicial TEXT,
        arquivado_em TEXT NOT NULL DEFAULT (datetime('now')),
        operacao TEXT NOT NULL
    )''')
    legado_campos = {str(r[1]) for r in con.execute(
        'PRAGMA table_info("historico_v2_controles_legados")')}
    legado_minimo = {'topico_id','disciplina_id','revisoes_iniciais',
                     'percentual_inicial','operacao'}
    if legado_minimo - legado_campos:
        raise RuntimeError('Arquivo de legado Excel incompatível; migração bloqueada')
    con.execute('''CREATE INDEX IF NOT EXISTS idx_hist_v2_legado_disciplina
        ON historico_v2_controles_legados(disciplina_id)''')
    for nome, tabela, select in (
        ('disciplina', 'disciplinas', '''SELECT c.topico_id, t.nome, OLD.id, OLD.nome,
            c.revisoes_iniciais,c.percentual_inicial,c.observacao_inicial,
            c.texto_erros_inicial,c.continuacao_inicial,'exclusao_disciplina'
            FROM controle_topico c JOIN topicos t ON t.id=c.topico_id
            WHERE t.disciplina_id=OLD.id'''),
        ('topico', 'topicos', '''SELECT c.topico_id, OLD.nome, OLD.disciplina_id,
            (SELECT nome FROM disciplinas WHERE id=OLD.disciplina_id),
            c.revisoes_iniciais,c.percentual_inicial,c.observacao_inicial,
            c.texto_erros_inicial,c.continuacao_inicial,'exclusao_topico'
            FROM controle_topico c WHERE c.topico_id=OLD.id'''),
    ):
        con.execute(f'''CREATE TRIGGER IF NOT EXISTS trg_hist_v2_o_legado_{nome}
            BEFORE DELETE ON {tabela} BEGIN
            INSERT OR IGNORE INTO historico_v2_controles_legados
            (topico_id,topico_nome,disciplina_id,disciplina_nome,
             revisoes_iniciais,percentual_inicial,observacao_inicial,
             texto_erros_inicial,continuacao_inicial,operacao)
            {select}; END''')

    # Trilha de concurso de sessão/simulado, evitando perda por SET NULL.
    con.execute('''CREATE TABLE IF NOT EXISTS historico_v2_linhagem_sessoes (
        tipo TEXT NOT NULL CHECK(tipo IN ('sessao','simulado','efetividade')),
        registro_id INTEGER NOT NULL,
        concurso_id INTEGER NOT NULL,
        PRIMARY KEY(tipo,registro_id)
    )''')
    con.execute('''CREATE TRIGGER IF NOT EXISTS trg_hist_v2_o_perfil_sessoes
      BEFORE DELETE ON concursos BEGIN
      INSERT OR IGNORE INTO historico_v2_linhagem_sessoes(tipo,registro_id,concurso_id)
        SELECT 'sessao',id,OLD.id FROM sessoes_questoes WHERE concurso_id=OLD.id;
      INSERT OR IGNORE INTO historico_v2_linhagem_sessoes(tipo,registro_id,concurso_id)
        SELECT 'simulado',id,OLD.id FROM simulados WHERE concurso_id=OLD.id;
      INSERT OR IGNORE INTO historico_v2_linhagem_sessoes(tipo,registro_id,concurso_id)
        SELECT 'efetividade',sessao_id,OLD.id FROM efetividade_sessoes WHERE concurso_id=OLD.id;
      END''')

    # Snapshots com totais no momento da exclusão, independentemente da
    # ordem em que as chaves estrangeiras propagam SET NULL e CASCADE.
    con.execute('''CREATE TABLE IF NOT EXISTS historico_v2_simulados_arquivados (
        simulado_id INTEGER PRIMARY KEY,
        sessao_id INTEGER NOT NULL,
        concurso_id INTEGER,
        criado_em TEXT NOT NULL,
        encerrado_em TEXT,
        respondidas INTEGER NOT NULL DEFAULT 0,
        acertos INTEGER NOT NULL DEFAULT 0,
        tipo TEXT,
        arquivado_em TEXT NOT NULL DEFAULT (datetime('now')),
        operacao TEXT NOT NULL
    )''')
    con.execute('''CREATE TABLE IF NOT EXISTS historico_v2_efetividade_arquivada (
        sessao_id INTEGER PRIMARY KEY,
        concurso_id INTEGER,
        criado_em TEXT NOT NULL,
        concluida INTEGER NOT NULL DEFAULT 0,
        respostas INTEGER NOT NULL DEFAULT 0,
        acertos INTEGER NOT NULL DEFAULT 0,
        dominio_medio_antes REAL,
        dominio_medio_depois REAL,
        cobertura_media_antes REAL,
        cobertura_media_depois REAL,
        arquivado_em TEXT NOT NULL DEFAULT (datetime('now')),
        operacao TEXT NOT NULL
    )''')

    con.execute('''CREATE INDEX IF NOT EXISTS idx_hist_v2_simulados_perfil_data
        ON historico_v2_simulados_arquivados(concurso_id, criado_em)''')
    con.execute('''CREATE INDEX IF NOT EXISTS idx_hist_v2_efetividade_perfil_data
        ON historico_v2_efetividade_arquivada(concurso_id, criado_em)''')

    # Trigger do pai é executado antes da propagação CASCADE. Protege ainda
    # contra mudança posterior dos vínculos sessao_id das tentativas.
    con.execute('''CREATE TRIGGER IF NOT EXISTS trg_hist_v2_o_sessao_snapshot
      BEFORE DELETE ON sessoes_questoes BEGIN
      INSERT OR IGNORE INTO historico_v2_simulados_arquivados
      (simulado_id,sessao_id,concurso_id,criado_em,encerrado_em,
       respondidas,acertos,tipo,operacao)
      SELECT s.id,s.sessao_id,COALESCE(s.concurso_id,
        (SELECT l.concurso_id FROM historico_v2_linhagem_sessoes l
         WHERE l.tipo='simulado' AND l.registro_id=s.id)),
        s.criado_em,OLD.encerrado_em,
        (SELECT COUNT(*) FROM tentativas_questoes tq
         WHERE tq.sessao_id=OLD.id AND tq.correta IN (0,1)),
        (SELECT COUNT(*) FROM tentativas_questoes tq
         WHERE tq.sessao_id=OLD.id AND tq.correta=1),
        s.tipo,'exclusao_sessao'
      FROM simulados s WHERE s.sessao_id=OLD.id;
      INSERT OR IGNORE INTO historico_v2_efetividade_arquivada
      (sessao_id,concurso_id,criado_em,concluida,respostas,acertos,
       dominio_medio_antes,dominio_medio_depois,
       cobertura_media_antes,cobertura_media_depois,operacao)
      SELECT e.sessao_id,COALESCE(e.concurso_id,
        (SELECT l.concurso_id FROM historico_v2_linhagem_sessoes l
         WHERE l.tipo='efetividade' AND l.registro_id=e.sessao_id)),
        e.criado_em,e.concluida,e.respostas,e.acertos,
        e.dominio_medio_antes,e.dominio_medio_depois,
        e.cobertura_media_antes,e.cobertura_media_depois,'exclusao_sessao'
      FROM efetividade_sessoes e WHERE e.sessao_id=OLD.id;
      END''')
    # Exclusões diretas de filhos também devem ser rastreadas. Não contabilizar
    # como concluídos os simulados sem data de encerramento/respostas.
    con.execute('''CREATE TRIGGER IF NOT EXISTS trg_hist_v2_o_simulado_snapshot
      BEFORE DELETE ON simulados BEGIN
      INSERT OR IGNORE INTO historico_v2_simulados_arquivados
      (simulado_id,sessao_id,concurso_id,criado_em,encerrado_em,
       respondidas,acertos,tipo,operacao)
      SELECT OLD.id,OLD.sessao_id,COALESCE(OLD.concurso_id,
        (SELECT l.concurso_id FROM historico_v2_linhagem_sessoes l
         WHERE l.tipo='simulado' AND l.registro_id=OLD.id)),
        OLD.criado_em,(SELECT encerrado_em FROM sessoes_questoes WHERE id=OLD.sessao_id),
        (SELECT COUNT(*) FROM tentativas_questoes tq
         WHERE tq.sessao_id=OLD.sessao_id AND tq.correta IN (0,1)),
        (SELECT COUNT(*) FROM tentativas_questoes tq
         WHERE tq.sessao_id=OLD.sessao_id AND tq.correta=1),
        OLD.tipo,'exclusao_simulado';
      END''')
    con.execute('''CREATE TRIGGER IF NOT EXISTS trg_hist_v2_o_efetividade_snapshot
      BEFORE DELETE ON efetividade_sessoes BEGIN
      INSERT OR IGNORE INTO historico_v2_efetividade_arquivada
      (sessao_id,concurso_id,criado_em,concluida,respostas,acertos,
       dominio_medio_antes,dominio_medio_depois,
       cobertura_media_antes,cobertura_media_depois,operacao)
      SELECT OLD.sessao_id,COALESCE(OLD.concurso_id,
        (SELECT l.concurso_id FROM historico_v2_linhagem_sessoes l
         WHERE l.tipo='efetividade' AND l.registro_id=OLD.sessao_id)),
        OLD.criado_em,OLD.concluida,OLD.respostas,OLD.acertos,
        OLD.dominio_medio_antes,OLD.dominio_medio_depois,
        OLD.cobertura_media_antes,OLD.cobertura_media_depois,'exclusao_efetividade';
      END''')
    # Bancos parcialmente migrados não podem receber gatilhos inválidos.
    # CREATE TABLE IF NOT EXISTS não repara uma tabela preexistente incompleta.
    required_archives = {
        'historico_v2_controles_legados': {'topico_id','revisoes_iniciais','percentual_inicial','operacao'},
        'historico_v2_linhagem_sessoes': {'tipo','registro_id','concurso_id'},
        'historico_v2_simulados_arquivados': {'simulado_id','sessao_id','concurso_id','criado_em','encerrado_em','respondidas','acertos'},
        'historico_v2_efetividade_arquivada': {'sessao_id','concurso_id','criado_em','concluida','respostas','acertos'},
    }
    for table, expected in required_archives.items():
        actual = {str(r[1]) for r in con.execute(f'PRAGMA table_info("{table}")')}
        if expected - actual:
            raise RuntimeError(f'Arquivo histórico incompatível em {table}: {sorted(expected-actual)}')

    return {'schema':'historico_preservacao_v2_o','triggers_n':3,'triggers_o':6,
            'legado_importado_sem_data':True,'somente_clone':True}


def garantir_schema_preservacao(con: sqlite3.Connection) -> dict:
    """Instala N+O atomicamente: erro não deixa DDL parcialmente aplicado.

    SAVEPOINT também preserva uma transação de inicialização preexistente.
    A função não muda a política de commit da conexão fornecida.
    """
    con.execute('SAVEPOINT historico_v2_o_instalacao')
    try:
        result = _criar_schema_preservacao(con)
    except Exception:
        con.execute('ROLLBACK TO SAVEPOINT historico_v2_o_instalacao')
        con.execute('RELEASE SAVEPOINT historico_v2_o_instalacao')
        raise
    con.execute('RELEASE SAVEPOINT historico_v2_o_instalacao')
    return result
