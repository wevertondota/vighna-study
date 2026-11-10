"""Cobertura integral persistente das revisões por questões (R1).

Não executa reparações no carregamento do módulo: somente operações
expressamente iniciadas pelo usuário criam ciclos e ajustam a agenda.
A reconciliação retrospectiva é restrita ao primeiro contato recente e
nunca apaga revisões nem tentativas históricas.
"""
from __future__ import annotations

import json
from datetime import date, timedelta


def _base():
    import banco
    return banco


def _avaliar(concurso_id: int, topico_id: int) -> dict | None:
    banco = _base()
    concurso_id, topico_id = int(concurso_id), int(topico_id)
    with banco.conectar() as cx:
        total, = cx.execute(
            """SELECT COUNT(*) FROM questoes WHERE topico_id=? AND ativa=1
               AND COALESCE(excluida,0)=0""", (topico_id,),
        ).fetchone()
        if not total:
            return None
        existente = cx.execute(
            "SELECT id,origem FROM ciclos_questoes WHERE concurso_id=? AND topico_id=? AND status='ativo' LIMIT 1",
            (concurso_id, topico_id),
        ).fetchone()
        if existente:
            if existente[1] != 'revisao_topico_integral':
                return None  # ciclo personalizado existente: não substituir
            estado = banco.obter_estado_ciclo_questoes(existente[0])
            return {**estado, 'recuperavel': False, 'ciclo_existente': True}

        ja_houve_ciclo = cx.execute(
            "SELECT 1 FROM ciclos_questoes WHERE concurso_id=? AND topico_id=? LIMIT 1",
            (concurso_id, topico_id),
        ).fetchone() is not None
        iniciais = cx.execute(
            'SELECT COALESCE(revisoes_iniciais,0),proxima_revisao FROM controle_topico WHERE topico_id=?',
            (topico_id,),
        ).fetchone()
        inicial_revisoes = int(iniciais[0] or 0) if iniciais else 0
        agenda = str(iniciais[1])[:10] if iniciais and iniciais[1] else None
        # Nunca reconstruir historicamente um ciclo se houver revisão manual.
        manual = cx.execute(
            "SELECT 1 FROM revisoes WHERE topico_id=? AND (concurso_id=? OR concurso_id IS NULL) "
            "AND COALESCE(origem,'manual')!='questoes_internas' LIMIT 1",
            (topico_id, concurso_id),
        ).fetchone() is not None
        linhas = cx.execute(
            """SELECT tq.questao_id, tq.id, tq.respondida_em, s.origem
               FROM tentativas_questoes tq
               JOIN sessoes_questoes s ON s.id=tq.sessao_id
               JOIN questoes q ON q.id=tq.questao_id
               WHERE tq.concurso_id=? AND q.topico_id=? AND tq.correta IS NOT NULL
                 AND q.ativa=1 AND COALESCE(q.excluida,0)=0
               ORDER BY tq.respondida_em, tq.id""",
            (concurso_id, topico_id),
        ).fetchall()
        reutilizar = False
        ref = None
        ultima_por_questao = {}
        if linhas and not ja_houve_ciclo and not inicial_revisoes and not manual:
            primeira = str(linhas[0][2])[:10]
            recente = ((date.today() - timedelta(days=14)).isoformat() <= primeira <= date.today().isoformat())
            todas_revisoes = all(str(linha[3] or '').lower() in {'topico_revisao', 'revisao_inteligente'} for linha in linhas)
            if recente and todas_revisoes:
                reutilizar, ref = True, primeira
                for qid, tid, when, _ in linhas:
                    ultima_por_questao[int(qid)] = (int(tid), str(when))
        total_cobertas = len(ultima_por_questao)
        return {
            'concurso_id': concurso_id, 'topico_id': topico_id,
            'total': int(total), 'respondidas': total_cobertas,
            'pendentes': int(total) - total_cobertas,
            'recuperavel': reutilizar and bool(total_cobertas),
            'ciclo_existente': False, 'referencia_tentativas': ref,
            'agenda_anterior': agenda,
            '_ultima_por_questao': ultima_por_questao,
        }


def previa_ciclo_revisao_integral(concurso_id: int, topico_id: int) -> dict | None:
    """Somente leitura: permite a UI indicar a continuação recuperável."""
    estado = _avaliar(concurso_id, topico_id)
    if not estado:
        return None
    return {k: v for k, v in estado.items() if not k.startswith('_')}


def iniciar_ou_recuperar_ciclo_revisao_integral(concurso_id: int, topico_id: int) -> dict:
    """Cria snapshot integral; incorpora tentativas recentes apenas se inequívocas."""
    banco = _base()
    estado = _avaliar(concurso_id, topico_id)
    if not estado:
        raise ValueError('Não é possível criar o ciclo: há outro ciclo ativo ou não há questões.')
    if estado.get('ciclo_existente'):
        return estado
    concurso_id, topico_id = int(concurso_id), int(topico_id)
    with banco.conectar() as cx:
        ids = [int(r[0]) for r in cx.execute(
            "SELECT id FROM questoes WHERE topico_id=? AND ativa=1 AND COALESCE(excluida,0)=0 ORDER BY id",
            (topico_id,),
        )]
    recuperadas = estado.get('_ultima_por_questao') or {}
    referencia = estado.get('referencia_tentativas') or date.today().isoformat()
    filtros = {
        'tipo_cobertura': 'revisao_integral',
        'referencia_tentativas': referencia,
        'recuperadas_previamente': len(recuperadas),
        'agenda_antes_da_recuperacao': estado.get('agenda_anterior'),
    }
    if recuperadas:
        with banco.conectar() as cx:
            legadas = cx.execute(
                """SELECT id FROM revisoes WHERE concurso_id=? AND topico_id=?
                   AND origem='questoes_internas' AND data>=? AND data<=?""",
                (concurso_id, topico_id, referencia, date.today().isoformat()),
            ).fetchall()
        filtros['revisoes_parciais_legadas_id'] = [int(r[0]) for r in legadas]
    ciclo = banco.criar_ciclo_questoes(
        concurso_id, topico_id, ids, origem='revisao_topico_integral', filtros=filtros,
    )
    try:
        if recuperadas:
            with banco.conectar() as cx:
                cx.executemany(
                    """UPDATE ciclo_questoes_itens
                       SET estado='respondida', respondida_em=?, tentativa_id=?
                       WHERE ciclo_id=? AND questao_id=? AND estado='pendente'""",
                    [(when, tid, int(ciclo['id']), qid) for qid, (tid, when) in recuperadas.items()],
                )
                # O ciclo inicial incompleto não tem próxima data válida.
                # Remover APENAS o agendamento automático prematuro, sem apagar
                # nenhuma revisão ou tentativa e sem estabelecer data retroativa.
                anterior = estado.get('agenda_anterior')
                if anterior and anterior > date.today().isoformat():
                    cx.execute(
                        'UPDATE controle_topico SET proxima_revisao=NULL WHERE topico_id=? AND proxima_revisao=?',
                        (topico_id, anterior),
                    )
    except Exception:
        # Conservador: cancelar o ciclo criado se não foi possível recuperar o estado.
        banco.encerrar_ciclo_questoes(int(ciclo['id']), 'falha_reconciliacao')
        raise
    return banco.obter_estado_ciclo_questoes(int(ciclo['id']))


def resultado_cobertura_revisao_integral(sessao_id: int, topico_id: int, concurso_id: int | None) -> dict | None:
    """Lê a cobertura persistente da sessão, inclusive se o ciclo acabou de fechar."""
    banco = _base()
    with banco.conectar() as cx:
        linha = cx.execute('SELECT concurso_id,contexto_json FROM sessoes_questoes WHERE id=?', (int(sessao_id),)).fetchone()
    if not linha:
        return None
    try:
        contexto = json.loads(linha[1] or '{}')
        cid = int(contexto.get('ciclo_questoes_id') or 0)
    except (ValueError, TypeError, json.JSONDecodeError):
        contexto, cid = {}, 0
    if not cid:
        # Uma bateria avulsa do MESMO tópico também pode contribuir para
        # a cobertura em curso. Não incluir simulados nem outros módulos.
        with banco.conectar() as cx:
            origem = cx.execute('SELECT origem FROM sessoes_questoes WHERE id=?',
                                (int(sessao_id),)).fetchone()
        if origem and str(origem[0]) in {'topico_estudo', 'topico_revisao', 'revisao_inteligente'}:
            ativo = banco.obter_ciclo_questoes_ativo(int(linha[0]), int(topico_id))
            if ativo and ativo.get('origem') == 'revisao_topico_integral':
                cid = int(ativo['id'])
                with banco.conectar() as cx:
                    respostas = cx.execute(
                        """SELECT tq.questao_id,tq.id FROM tentativas_questoes tq
                           JOIN questoes q ON q.id=tq.questao_id
                           WHERE tq.sessao_id=? AND tq.correta IS NOT NULL
                             AND tq.concurso_id=? AND q.topico_id=?
                           ORDER BY tq.id""",
                        (int(sessao_id), int(linha[0]), int(topico_id)),
                    ).fetchall()
                for qid, tid in respostas:
                    banco.marcar_questao_ciclo_respondida(cid, qid, tid)
    if not cid:
        return None
    estado = banco.obter_estado_ciclo_questoes(cid)
    if not estado or estado['origem'] != 'revisao_topico_integral':
        return None
    if estado['topico_id'] != int(topico_id) or estado['concurso_id'] != int(linha[0]):
        return None
    if concurso_id is not None and int(concurso_id) != int(linha[0]):
        return None
    referencia = estado['filtros'].get('referencia_tentativas') or str(estado['criado_em'])[:10]
    ids = set(int(x) for x in estado.get('ids_respondidas', []))
    # Atribuir uma única observação (a mais recente) a cada questão coberta.
    with banco.conectar() as cx:
        linhas = cx.execute(
            """SELECT tq.questao_id,tq.correta,tq.id
               FROM tentativas_questoes tq JOIN questoes q ON q.id=tq.questao_id
               WHERE tq.concurso_id=? AND q.topico_id=? AND tq.correta IS NOT NULL
                 AND SUBSTR(tq.respondida_em,1,10)>=?
               ORDER BY tq.respondida_em DESC, tq.id DESC""",
            (int(linha[0]), int(topico_id), str(referencia)[:10]),
        ).fetchall()
    ultimas = {}
    for qid, correta, tid in linhas:
        if int(qid) in ids and int(qid) not in ultimas:
            ultimas[int(qid)] = (int(correta), int(tid))
    acertos = sum(1 for correta, _ in ultimas.values() if correta)
    # Reconhece revisões prematuras de um primeiro contato recuperado como
    # eventos históricos preservados, mas não como ciclos integrais concluídos.
    with banco.conectar() as cx:
        linhas_ciclos = cx.execute(
            "SELECT filtros_json FROM ciclos_questoes WHERE concurso_id=? AND topico_id=?",
            (int(linha[0]), int(topico_id)),
        ).fetchall()
        ids_parciais = set()
        for (json_filtros,) in linhas_ciclos:
            try:
                ids_parciais.update(int(v) for v in json.loads(json_filtros or '{}').get('revisoes_parciais_legadas_id', []))
            except (TypeError, ValueError, json.JSONDecodeError):
                pass
        revisoes_validas = cx.execute(
            'SELECT id,data,questoes,acertos FROM revisoes WHERE topico_id=? AND concurso_id=? AND data<? ORDER BY data DESC,id DESC',
            (int(topico_id), int(linha[0]), str(referencia)[:10]),
        ).fetchall()
        # Para a primeira conclusão, o intervalo desde o início do ciclo
        # também inclui antigas revisões prematuras; elas ficam fora do cálculo.
        if ids_parciais:
            revisoes_validas = [r for r in revisoes_validas if int(r[0]) not in ids_parciais]
        inicial = cx.execute(
            'SELECT COALESCE(revisoes_iniciais,0),percentual_inicial FROM controle_topico WHERE topico_id=?',
            (int(topico_id),),
        ).fetchone()
        anterior = (100.0 * revisoes_validas[0][3] / revisoes_validas[0][2]
                    if revisoes_validas and revisoes_validas[0][2] else
                    (inicial[1] if inicial else None))
        numero_revisao_real = 1 + len(revisoes_validas) + int(inicial[0] or 0 if inicial else 0)
    cobertas = len(ids)
    total = int(estado['total']) - int(estado['indisponiveis'])
    restantes = int(estado['pendentes'])
    return {
        'ativa': True, 'tipo': 'ciclo_integral', 'ciclo_id': cid,
        'referencia': referencia, 'total': total, 'cobertas': cobertas,
        'restantes': restantes, 'questoes': total,
        'respondidas_unicas': len(ultimas), 'acertos': acertos,
        'percentual_resultado': (100.0 * acertos / len(ultimas) if ultimas else None),
        'ids_cobertas': list(ids), 'ids_restantes': estado['ids_pendentes'],
        'ja_consolidado': bool(estado['filtros'].get('revisao_consolidada_id')),
        'numero_revisao_real': numero_revisao_real,
        'percentual_anterior_real': anterior,
    }


def marcar_ciclo_revisao_consolidado(ciclo_id: int, revisao_id: int) -> None:
    banco = _base()
    with banco.conectar() as cx:
        linha = cx.execute('SELECT filtros_json FROM ciclos_questoes WHERE id=?', (int(ciclo_id),)).fetchone()
        if not linha:
            raise ValueError('Ciclo não encontrado na consolidação.')
        filtros = json.loads(linha[0] or '{}')
        if not filtros.get('revisao_consolidada_id'):
            filtros['revisao_consolidada_id'] = int(revisao_id)
            cx.execute('UPDATE ciclos_questoes SET filtros_json=? WHERE id=?',
                       (json.dumps(filtros, ensure_ascii=False), int(ciclo_id)))
