"""Revisões independentes e opcionais por capítulo.

Os dados ficam num SQLite distinto do banco acadêmico. O tópico pai e o
motor de revisões original jamais são atualizados por este módulo.
"""
from __future__ import annotations

from datetime import date, datetime
from contextlib import contextmanager
from pathlib import Path
import sqlite3


def _iso_date(v, *, optional=False):
    if v in (None, '') and optional:
        return None
    return date.fromisoformat(str(v)[:10]).isoformat()


def _now():
    return datetime.now().astimezone().isoformat(timespec='seconds')


def _duracao_opcional(valor):
    if valor is None or valor == '':
        return None
    try:
        minutos = int(valor)
    except (TypeError, ValueError) as exc:
        raise ValueError('Tempo de estudo deve ser informado em minutos inteiros.') from exc
    if not 1 <= minutos <= 5999:
        raise ValueError('Tempo de estudo deve estar entre 1 minuto e 99h59min.')
    return minutos


class RepositorioRevisoesCapitulos:
    def __init__(self, caminho=None):
        if caminho is None:
            from caminhos import CAMINHO_BANCO
            caminho = Path(CAMINHO_BANCO).resolve().parent / 'revisoes_capitulos_v1.db'
        self.caminho = Path(caminho)
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        self._inicializar()

    @contextmanager
    def _conectar(self):
        c = sqlite3.connect(str(self.caminho), timeout=15)
        try:
            c.row_factory = sqlite3.Row
            c.execute('PRAGMA busy_timeout=15000')
            c.execute('PRAGMA foreign_keys=ON')
            yield c
            c.commit()
        except Exception:
            c.rollback()
            raise
        finally:
            c.close()

    def _inicializar(self):
        with self._conectar() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS unidades (
                    perfil_id INTEGER NOT NULL,
                    capitulo_id INTEGER NOT NULL,
                    topico_id INTEGER NOT NULL,
                    disciplina TEXT NOT NULL DEFAULT '',
                    topico TEXT NOT NULL DEFAULT '',
                    capitulo TEXT NOT NULL DEFAULT '',
                    ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0,1)),
                    proxima_revisao TEXT,
                    criado_em TEXT NOT NULL,
                    atualizado_em TEXT NOT NULL,
                    PRIMARY KEY(perfil_id, capitulo_id)
                );
                CREATE TABLE IF NOT EXISTS revisoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    perfil_id INTEGER NOT NULL,
                    capitulo_id INTEGER NOT NULL,
                    data TEXT NOT NULL,
                    questoes INTEGER NOT NULL CHECK(questoes>=1),
                    acertos INTEGER NOT NULL CHECK(acertos>=0 AND acertos<=questoes),
                    observacao TEXT NOT NULL DEFAULT '',
                    erros TEXT NOT NULL DEFAULT '',
                    continuacao TEXT NOT NULL DEFAULT '',
                    proxima_sugerida TEXT,
                    tempo_estudo_minutos INTEGER CHECK(tempo_estudo_minutos IS NULL OR tempo_estudo_minutos BETWEEN 1 AND 5999),
                    criado_em TEXT NOT NULL,
                    FOREIGN KEY(perfil_id,capitulo_id)
                        REFERENCES unidades(perfil_id,capitulo_id)
                );
                CREATE INDEX IF NOT EXISTS idx_rev_capitulo
                    ON revisoes(perfil_id,capitulo_id,data,id);
                CREATE INDEX IF NOT EXISTS idx_capitulo_agenda
                    ON unidades(perfil_id,ativo,proxima_revisao);
            ''')
            # Migração aditiva, segura para bancos existentes: não recria
            # a tabela nem reescreve qualquer revisão já registrada.
            colunas = {r['name'] for r in db.execute('PRAGMA table_info(revisoes)')}
            if 'tempo_estudo_minutos' not in colunas:
                db.execute('''ALTER TABLE revisoes ADD COLUMN tempo_estudo_minutos INTEGER
                    CHECK(tempo_estudo_minutos IS NULL OR tempo_estudo_minutos BETWEEN 1 AND 5999)''')
            if 'contabilizar_tempo' not in colunas:
                db.execute('ALTER TABLE revisoes ADD COLUMN contabilizar_tempo INTEGER NOT NULL DEFAULT 1 CHECK(contabilizar_tempo IN (0,1))')
            db.execute('PRAGMA user_version=3')

    def estado(self, perfil_id, capitulo_id):
        with self._conectar() as db:
            row = db.execute(
                'SELECT * FROM unidades WHERE perfil_id=? AND capitulo_id=?',
                (int(perfil_id), int(capitulo_id))).fetchone()
        return dict(row) if row else None

    def ativar(self, perfil_id, capitulo_id, topico_id, disciplina, topico, capitulo):
        pid, cid, tid = int(perfil_id), int(capitulo_id), int(topico_id)
        if min(pid,cid,tid) < 0 or cid == 0 or tid == 0:
            raise ValueError('Identificação de capítulo inválida.')
        with self._conectar() as db:
            anterior = db.execute(
                'SELECT topico_id FROM unidades WHERE perfil_id=? AND capitulo_id=?',
                (pid, cid)).fetchone()
            if anterior is not None and int(anterior['topico_id']) != tid:
                raise ValueError(
                    'Identificador de capítulo reutilizado em outro tópico; '
                    'as revisões antigas foram preservadas sem reassociação.')
            db.execute('''INSERT INTO unidades
                (perfil_id,capitulo_id,topico_id,disciplina,topico,capitulo,ativo,criado_em,atualizado_em)
                VALUES (?,?,?,?,?,?,1,?,?)
                ON CONFLICT(perfil_id,capitulo_id) DO UPDATE SET
                topico_id=excluded.topico_id,disciplina=excluded.disciplina,
                topico=excluded.topico,capitulo=excluded.capitulo,ativo=1,
                atualizado_em=excluded.atualizado_em''',
                (pid,cid,tid,str(disciplina)[:250],str(topico)[:500],str(capitulo)[:500],_now(),_now()))

    def desativar(self, perfil_id, capitulo_id):
        with self._conectar() as db:
            db.execute('UPDATE unidades SET ativo=0, atualizado_em=? WHERE perfil_id=? AND capitulo_id=?',
                       (_now(), int(perfil_id), int(capitulo_id)))

    def resumo(self, perfil_id, capitulo_id):
        estado = self.estado(perfil_id,capitulo_id)
        with self._conectar() as db:
            dados = db.execute('''SELECT COUNT(*) AS n, MAX(data) AS ultima
              FROM revisoes WHERE perfil_id=? AND capitulo_id=?''',
              (int(perfil_id),int(capitulo_id))).fetchone()
            ultimo = db.execute('''SELECT 100.0*acertos/questoes AS pct FROM revisoes
              WHERE perfil_id=? AND capitulo_id=? ORDER BY data DESC,id DESC LIMIT 1''',
              (int(perfil_id),int(capitulo_id))).fetchone()
        return {'revisoes_totais':int(dados['n']), 'ultima_revisao':dados['ultima'],
                'proxima_revisao':estado['proxima_revisao'] if estado else None,
                'percentual_atual':float(ultimo['pct']) if ultimo else None,
                'ativo':bool(estado and estado['ativo'])}

    def registrar(self, perfil_id, capitulo_id, data, questoes, acertos,
                  observacao='', erros='', continuacao='', proxima=None,
                  tempo_estudo_minutos=None, contabilizar_tempo=True):
        pid,cid=int(perfil_id),int(capitulo_id)
        q,a=int(questoes),int(acertos)
        if q < 1 or not (0 <= a <= q):
            raise ValueError('Quantidade de questões/acertos inválida.')
        data=_iso_date(data)
        proxima=_iso_date(proxima,optional=True)
        tempo_estudo_minutos=_duracao_opcional(tempo_estudo_minutos)
        with self._conectar() as db:
            modo = db.execute('SELECT ativo FROM unidades WHERE perfil_id=? AND capitulo_id=?', (pid,cid)).fetchone()
            if not modo or not modo['ativo']:
                raise ValueError('Ative a revisão independente do capítulo antes de registrar.')
            cur=db.execute('''INSERT INTO revisoes
                (perfil_id,capitulo_id,data,questoes,acertos,observacao,erros,continuacao,proxima_sugerida,tempo_estudo_minutos,contabilizar_tempo,criado_em)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',
                (pid,cid,data,q,a,str(observacao),str(erros),str(continuacao),proxima,tempo_estudo_minutos,int(bool(contabilizar_tempo)),_now()))
            db.execute('UPDATE unidades SET proxima_revisao=?, atualizado_em=? WHERE perfil_id=? AND capitulo_id=?',
                       (proxima,_now(),pid,cid))
            return cur.lastrowid

    def percentuais_ativos_por_topico(self, perfil_id, topicos_ids):
        """Último percentual das revisões de capítulos independentes ativos.

        Apenas leitura. O chamador verifica a existência e o estado atual dos
        capítulos no cadastro acadêmico, sem alterar o histórico de ninguém.
        """
        permitidos = {int(topico_id) for topico_id in topicos_ids}
        if not permitidos:
            return {}
        with self._conectar() as db:
            rows = db.execute('''SELECT u.topico_id, u.capitulo_id,
                    (SELECT 100.0 * r.acertos / r.questoes
                     FROM revisoes r
                     WHERE r.perfil_id = u.perfil_id
                       AND r.capitulo_id = u.capitulo_id
                     ORDER BY r.data DESC, r.id DESC LIMIT 1) AS percentual
                FROM unidades u
                WHERE u.perfil_id = ? AND u.ativo = 1
                ''', (int(perfil_id),)).fetchall()
        resultado = {}
        for row in rows:
            tid = int(row['topico_id'])
            if tid in permitidos and row['percentual'] is not None:
                resultado.setdefault(tid, []).append(
                    (int(row['capitulo_id']), float(row['percentual'])))
        return resultado

    def listar_historico(self, perfil_id, capitulo_id):
        with self._conectar() as db:
            dados=db.execute('''SELECT id,data,questoes,acertos,
                 100.0*acertos/questoes,observacao,erros,continuacao,proxima_sugerida,
                 tempo_estudo_minutos,contabilizar_tempo FROM revisoes WHERE perfil_id=? AND capitulo_id=?
                 ORDER BY data DESC,id DESC''',(int(perfil_id),int(capitulo_id))).fetchall()
        return [tuple(row) for row in dados]

    def editar(self, perfil_id, capitulo_id, revisao_id, data, questoes, acertos,
               observacao, erros, continuacao, tempo_estudo_minutos=None, contabilizar_tempo=True):
        q,a=int(questoes),int(acertos)
        if q<1 or not (0<=a<=q):
            raise ValueError('Quantidade de questões/acertos inválida.')
        tempo_estudo_minutos=_duracao_opcional(tempo_estudo_minutos)
        with self._conectar() as db:
            cur=db.execute('''UPDATE revisoes SET data=?,questoes=?,acertos=?,observacao=?,erros=?,continuacao=?,tempo_estudo_minutos=?,contabilizar_tempo=?
                WHERE id=? AND perfil_id=? AND capitulo_id=?''',
                (_iso_date(data),q,a,str(observacao),str(erros),str(continuacao),tempo_estudo_minutos,int(bool(contabilizar_tempo)),
                 int(revisao_id),int(perfil_id),int(capitulo_id)))
            if cur.rowcount!=1: raise ValueError('Revisão não encontrada.')

    def excluir(self, perfil_id, capitulo_id, revisao_id):
        with self._conectar() as db:
            db.execute('DELETE FROM revisoes WHERE id=? AND perfil_id=? AND capitulo_id=?',
                       (int(revisao_id),int(perfil_id),int(capitulo_id)))
            # Não recalcular prazos arbitrariamente após excluir um histórico;
            # o usuário mantém o controle manual da data futura.

    def atualizar_proxima(self, perfil_id, capitulo_id, proxima):
        proxima=_iso_date(proxima,optional=True)
        with self._conectar() as db:
            cur=db.execute('UPDATE unidades SET proxima_revisao=?, atualizado_em=? WHERE perfil_id=? AND capitulo_id=?',
                       (proxima,_now(),int(perfil_id),int(capitulo_id)))
            if cur.rowcount!=1:raise ValueError('Capítulo não cadastrado.')

    def agendadas(self, inicio, fim, perfil_id):
        inicio,fim=_iso_date(inicio),_iso_date(fim)
        with self._conectar() as db:
            rows=[dict(r) for r in db.execute('''SELECT * FROM unidades
              WHERE perfil_id=? AND ativo=1 AND proxima_revisao BETWEEN ? AND ?
              ORDER BY proxima_revisao,disciplina,capitulo''',(int(perfil_id),inicio,fim))]
        if not rows:return []
        # Estado e existência atuais do capítulo são a fonte da verdade;
        # capítulos removidos e desligados no cadastro não geram pendências.
        try:
            from banco import listar_capitulos_topico, topico_esta_pausado
        except ImportError:
            return []
        cache={}
        resultado=[]
        for r in rows:
            tid,cid=r['topico_id'],r['capitulo_id']
            if tid not in cache:
                cache[tid] = ({int(x[0]): bool(x[4]) for x in listar_capitulos_topico(tid)},
                              bool(topico_esta_pausado(tid)))
            cap, pai_pausado = cache[tid]
            if cid not in cap or cap[cid] or pai_pausado:
                continue
            resumo=self.resumo(perfil_id,cid)
            # ID negativo diferencia o capítulo dos tópicos no calendário.
            resultado.append((-cid, r['disciplina'],f"↳ {r['capitulo']}",
                              resumo['revisoes_totais'],r['proxima_revisao'],
                              resumo['percentual_atual'],3))
        return resultado

    def pendentes(self, referencia, perfil_id):
        return self.agendadas('1900-01-01',referencia,perfil_id)

    def topicos_pais_suspensos(self, perfil_id):
        """Tópicos cuja totalidade de capítulos cadastrados é independente.

        Suspensão virtual: não altera prazos, revisões ou o banco do tópico.
        Ao desativar a independência de qualquer capítulo, a agenda do pai
        volta a ser elegível, inclusive seu prazo anteriormente preservado.
        O cálculo usa os capítulos atualmente existentes, não registros órfãos.
        """
        from banco import listar_capitulos_topico

        with self._conectar() as db:
            rows = db.execute("SELECT topico_id,capitulo_id FROM unidades "
                "WHERE perfil_id=? AND ativo=1", (int(perfil_id),)).fetchall()
        por_topico = {}
        for r in rows:
            por_topico.setdefault(int(r['topico_id']), set()).add(int(r['capitulo_id']))

        suspensos = set()
        for topico_id, capitulos_ativos in por_topico.items():
            capitulos_existentes = listar_capitulos_topico(topico_id)
            ids_existentes = {int(cap[0]) for cap in capitulos_existentes}
            if ids_existentes and ids_existentes.issubset(capitulos_ativos):
                suspensos.add(topico_id)
        return suspensos
