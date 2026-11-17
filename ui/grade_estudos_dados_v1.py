"""Grade de Estudos V1: leitura sincronizada, notas e edição auditada da agenda.

A tabela de tópicos e as datas são as mesmas utilizadas em Disciplinas.
Não cria segundo catálogo, revisão executada, nem altera ciclos de questões.
"""
from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
from datetime import date
import sqlite3

NOTA_MAX = 280


@dataclass(frozen=True)
class LinhaGrade:
    topico_id: int
    topico: str
    revisoes: int
    ultima_revisao: str | None
    proxima_revisao: str | None
    percentual: float | None
    respondidas: int
    questoes_ativas: int
    acertos: int
    tentativas: int
    nota: str
    importancia: int = 3


class RepositorioGrade:
    def __init__(self, banco_module=None):
        if banco_module is None:
            import banco as banco_module
        self.banco = banco_module

    def _conexao(self):
        return self.banco.conectar()

    @staticmethod
    def _garantir_tabelas(cx):
        # Aditivas: não sobrescrevem revisões, controle_topico ou tentativas.
        cx.execute('''
            CREATE TABLE IF NOT EXISTS grade_estudos_notas_v1 (
                concurso_id INTEGER NOT NULL,
                topico_id INTEGER NOT NULL,
                texto TEXT NOT NULL DEFAULT '',
                alterado_em TEXT NOT NULL DEFAULT (datetime('now','localtime')),
                PRIMARY KEY (concurso_id, topico_id),
                FOREIGN KEY (concurso_id) REFERENCES concursos(id) ON DELETE CASCADE,
                FOREIGN KEY (topico_id) REFERENCES topicos(id) ON DELETE CASCADE,
                CHECK (length(texto) <= 280)
            )
        ''')
        cx.execute('''
            CREATE TABLE IF NOT EXISTS grade_estudos_agenda_edicoes_v1 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concurso_id INTEGER NOT NULL,
                topico_id INTEGER NOT NULL,
                anterior TEXT,
                novo TEXT,
                alterado_em TEXT NOT NULL DEFAULT (datetime('now','localtime')),
                FOREIGN KEY (concurso_id) REFERENCES concursos(id) ON DELETE CASCADE,
                FOREIGN KEY (topico_id) REFERENCES topicos(id) ON DELETE CASCADE
            )
        ''')
        cx.execute('''
            CREATE INDEX IF NOT EXISTS idx_grade_agenda_perfil_topico_v1
            ON grade_estudos_agenda_edicoes_v1 (concurso_id, topico_id, id)
        ''')

    @staticmethod
    def _validar_topico_perfil(cx, concurso_id, topico_id):
        existe = cx.execute('''
            SELECT 1
            FROM topicos t
            JOIN disciplina_concurso_inclusao dc
              ON dc.disciplina_id=t.disciplina_id
             AND dc.concurso_id=? AND dc.incluido=1
            JOIN topico_concurso_importancia tc
              ON tc.topico_id=t.id
             AND tc.concurso_id=? AND tc.incluido=1
            WHERE t.id=?
        ''', (concurso_id, concurso_id, topico_id)).fetchone()
        if not existe:
            raise ValueError('Tópico não pertence ao perfil selecionado.')

    def disciplinas(self, concurso_id):
        return [(int(ident), str(nome)) for ident, nome in self.banco.listar_disciplinas(
            concurso_id=int(concurso_id), somente_incluidas=True,
        )]

    def topicos(self, nome_disciplina, concurso_id):
        concurso_id = int(concurso_id)
        registros = self.banco.listar_topicos(nome_disciplina, concurso_id=concurso_id)
        ids = [int(linha[0]) for linha in registros]
        if not ids:
            return []
        # Duas agregações por disciplina, não uma consulta por linha.
        placeholders = ','.join('?' for _ in ids)
        with closing(self._conexao()) as cx:
            with cx:
                self._garantir_tabelas(cx)
            questoes = cx.execute(f'''
                SELECT q.topico_id, COUNT(DISTINCT q.id) AS elegiveis,
                  COUNT(DISTINCT CASE WHEN tq.concurso_id=? THEN tq.questao_id END)
                    AS respondidas_distintas,
                  COUNT(CASE WHEN tq.concurso_id=? THEN tq.id END) AS tentativas,
                  SUM(CASE WHEN tq.concurso_id=? AND tq.correta=1 THEN 1 ELSE 0 END)
                    AS acertos
                FROM questoes q
                LEFT JOIN tentativas_questoes tq ON tq.questao_id=q.id
                WHERE q.topico_id IN ({placeholders})
                  AND COALESCE(q.ativa,1)=1 AND COALESCE(q.excluida,0)=0
                GROUP BY q.topico_id
            ''', (concurso_id, concurso_id, concurso_id, *ids)).fetchall()
            por_topico = {
                int(row[0]): tuple(int(v or 0) for v in row[1:])
                for row in questoes
            }
            # Uma agregação JOIN de tentativas multiplicaria q.id no COUNT(*).
            # A lista de questões elegíveis deve contar distintos.
            nota_rows = cx.execute(f'''
                SELECT topico_id, texto FROM grade_estudos_notas_v1
                WHERE concurso_id=? AND topico_id IN ({placeholders})
            ''', (concurso_id, *ids)).fetchall()
            notas = {int(id_): str(txt or '') for id_, txt in nota_rows}
        resultado = []
        for row in registros:
            ident, nome, revisoes, ultima, proxima, percentual, importancia = row[:7]
            q, respondidas, tentativas, acertos = por_topico.get(int(ident), (0,0,0,0))
            resultado.append(LinhaGrade(
                topico_id=int(ident), topico=str(nome), revisoes=int(revisoes or 0),
                ultima_revisao=ultima, proxima_revisao=proxima,
                percentual=(float(percentual) if percentual is not None else None),
                respondidas=respondidas, questoes_ativas=q, acertos=acertos,
                tentativas=tentativas, nota=notas.get(int(ident), ''),
                importancia=max(1, min(5, int(importancia or 3))),
            ))
        return resultado

    def ciclos_em_andamento(self, concurso_id):
        """Ciclos efetivamente ativos e com questões pendentes no perfil.

        Reutiliza o controle persistente do motor; leitura em lote sem writes.
        Questões concluídas no histórico não são inferidas como ciclo aberto.
        """
        try:
            with closing(self._conexao()) as cx:
                registros = cx.execute('''
                    SELECT c.topico_id,
                           SUM(CASE WHEN ci.estado='respondida' THEN 1 ELSE 0 END),
                           SUM(CASE WHEN ci.estado='pendente'
                                     AND q.id IS NOT NULL
                                     AND q.ativa=1
                                     AND COALESCE(q.excluida,0)=0
                                    THEN 1 ELSE 0 END),
                           COUNT(*)
                    FROM ciclos_questoes c
                    JOIN ciclo_questoes_itens ci ON ci.ciclo_id=c.id
                    LEFT JOIN questoes q ON q.id=ci.questao_id
                    WHERE c.concurso_id=? AND c.status='ativo'
                    GROUP BY c.id, c.topico_id
                ''', (int(concurso_id),)).fetchall()
        except sqlite3.OperationalError as exc:
            # Ausência de tabelas em instalações legadas pode significar
            # nenhum ciclo; outros problemas de SQLite não são ocultados.
            if 'no such table' in str(exc).lower():
                return {}
            raise
        return {int(topico_id): (int(respondidas or 0), int(pendentes or 0), int(total or 0))
                for topico_id, respondidas, pendentes, total in registros
                if int(pendentes or 0) > 0}

    def tendencias_recentes(self, concurso_id, topico_ids):
        '''Comparação descritiva das 10 últimas vs. 10 anteriores, por perfil.

        Fonte histórica de tentativas, inclusive snapshots de itens arquivados.
        Somente retorna tendência se houver 20 respostas com resultado 0/1;
        nunca trata saltos ou amostras insuficientes como desempenho zero.
        Não grava e não modifica o motor de domínio.
        '''
        ids = [int(i) for i in topico_ids]
        if not ids:
            return {}
        marcadores = ','.join('?' for _ in ids)
        with closing(self._conexao()) as cx:
            linhas = cx.execute(f'''
                WITH tentativas_ordenadas AS (
                    SELECT COALESCE(tq.topico_id_snapshot, q.topico_id) AS topico_id,
                           tq.correta AS correta,
                           ROW_NUMBER() OVER (
                               PARTITION BY COALESCE(tq.topico_id_snapshot, q.topico_id)
                               ORDER BY tq.respondida_em DESC, tq.id DESC
                           ) AS posicao
                    FROM tentativas_questoes tq
                    LEFT JOIN questoes q ON q.id = tq.questao_id
                    WHERE tq.concurso_id = ?
                      AND tq.correta IN (0, 1)
                      AND COALESCE(tq.topico_id_snapshot, q.topico_id)
                          IN ({marcadores})
                )
                SELECT topico_id,
                       SUM(CASE WHEN posicao <= 10 THEN correta ELSE 0 END) AS acertos_recentes,
                       SUM(CASE WHEN posicao BETWEEN 11 AND 20 THEN correta ELSE 0 END) AS acertos_anteriores,
                       COUNT(*) AS qtd
                FROM tentativas_ordenadas
                WHERE posicao <= 20
                GROUP BY topico_id
            ''', (int(concurso_id), *ids)).fetchall()
        resultados = {}
        for topico_id, recente, anterior, qtd in linhas:
            if int(qtd) >= 20:
                # Ambas as janelas contêm exatamente 10 respostas válidas.
                resultados[int(topico_id)] = (float(recente or 0) - float(anterior or 0)) * 10.0
        return resultados

    def edicoes_agenda(self, concurso_id, topico_ids):
        """Última edição manual por tópico, sem criar ou atualizar registros."""
        ids = [int(i) for i in topico_ids]
        if not ids:
            return {}
        placeholders = ','.join('?' for _ in ids)
        try:
            with closing(self._conexao()) as cx:
                registros = cx.execute(f'''
                    SELECT topico_id, novo
                    FROM grade_estudos_agenda_edicoes_v1
                    WHERE concurso_id=? AND topico_id IN ({placeholders})
                    ORDER BY id DESC
                ''', (int(concurso_id), *ids)).fetchall()
        except sqlite3.OperationalError:
            # Instalações legadas sem tabela de auditoria: origem desconhecida.
            return {}
        ultima = {}
        for topico_id, nova in registros:
            ultima.setdefault(int(topico_id), nova)
        return ultima

    def salvar_nota(self, concurso_id, topico_id, texto):
        cid, tid = int(concurso_id), int(topico_id)
        texto = str(texto).strip()
        if len(texto) > NOTA_MAX:
            raise ValueError(f'Anotação deve ter no máximo {NOTA_MAX} caracteres.')
        with closing(self._conexao()) as cx:
            with cx:
                self._validar_topico_perfil(cx, cid, tid)
                self._garantir_tabelas(cx)
                cx.execute('''
                    INSERT INTO grade_estudos_notas_v1(concurso_id,topico_id,texto)
                    VALUES (?,?,?)
                    ON CONFLICT(concurso_id,topico_id) DO UPDATE SET
                      texto=excluded.texto, alterado_em=datetime('now','localtime')
                ''', (cid, tid, texto))

    def atualizar_data_manual(self, concurso_id, topico_id, nova_data):
        """Modifica a agenda oficial e audita; NUNCA cria uma revisão."""
        cid, tid = int(concurso_id), int(topico_id)
        if nova_data is not None:
            nova_data = date.fromisoformat(str(nova_data)).isoformat()
        with closing(self._conexao()) as cx:
            with cx:
                self._validar_topico_perfil(cx, cid, tid)
                self._garantir_tabelas(cx)
                linha = cx.execute(
                    'SELECT proxima_revisao FROM controle_topico WHERE topico_id=?',
                    (tid,),
                ).fetchone()
                anterior = linha[0] if linha else None
                if anterior == nova_data:
                    return False
                # Mesma fonte de agenda que o motor de Disciplinas/Calendário.
                cx.execute('INSERT OR IGNORE INTO controle_topico(topico_id) VALUES (?)', (tid,))
                cx.execute('UPDATE controle_topico SET proxima_revisao=? WHERE topico_id=?',
                           (nova_data,tid))
                cx.execute('''
                    INSERT INTO grade_estudos_agenda_edicoes_v1
                    (concurso_id,topico_id,anterior,novo) VALUES (?,?,?,?)
                ''', (cid,tid,anterior,nova_data))
        return True
