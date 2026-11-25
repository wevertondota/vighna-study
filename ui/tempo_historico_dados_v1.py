"""Consultas de tempo efetivo por dia/semana/mês/ano (SQLite somente leitura).

Fontes: baterias finalizadas e revisões manuais com duração elegível. Não reconstrói
sessões anteriores à ativação nem confunde ausência de registro com 0 medido.
"""
from __future__ import annotations

from calendar import monthrange
from datetime import date, timedelta
from pathlib import Path
import sqlite3
from contextlib import closing


class FonteTempoIndisponivel(RuntimeError):
    """O contador não foi ativado ou a base não pode ser consultada."""


def _data(valor):
    if isinstance(valor, date):
        return valor
    return date.fromisoformat(str(valor))


def _abrir_ro(caminho):
    banco = Path(caminho).expanduser().resolve()
    if not banco.is_file():
        raise FonteTempoIndisponivel('Banco de estudos não localizado.')
    uri = banco.as_uri() + '?mode=ro'
    con = sqlite3.connect(uri, uri=True, timeout=5.0)
    con.execute('PRAGMA query_only=ON')
    return con


def _where(concurso_id, inicio=None, fim=None):
    partes = []
    parametros = []
    if concurso_id is not None:
        partes.append('b.concurso_id=?')
        parametros.append(int(concurso_id))
    if inicio is not None:
        partes.append('d.dia_local>=?')
        parametros.append(_data(inicio).isoformat())
    if fim is not None:
        partes.append('d.dia_local<=?')
        parametros.append(_data(fim).isoformat())
    return (' WHERE ' + ' AND '.join(partes)) if partes else '', parametros


def _linhas(con, *, concurso_id=None, inicio=None, fim=None):
    tabelas = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if not {'tempo_baterias_v1','tempo_baterias_dia_v1'}.issubset(tabelas):
        return []
    where, args = _where(concurso_id, inicio, fim)
    return con.execute('''
        SELECT d.dia_local, SUM(d.tempo_liquido_segundos),
               SUM(d.pausa_segundos), SUM(d.duracao_bruta_segundos),
               COUNT(DISTINCT d.chave)
        FROM tempo_baterias_dia_v1 AS d
        INNER JOIN tempo_baterias_v1 AS b ON b.chave=d.chave
        ''' + where + ' GROUP BY d.dia_local ORDER BY d.dia_local', args).fetchall()


def _linhas_manuais(caminho_banco, *, concurso_id=None, inicio=None, fim=None):
    """Histórico real, inclusive capítulos cuja autonomia foi desativada.
    Banco inexistente ou versão anterior sem duração: nenhuma medição.
    Erros de leitura não são confundidos com ausência de estudo.
    """
    caminho = Path(caminho_banco).expanduser().resolve().parent / 'revisoes_capitulos_v1.db'
    if not caminho.is_file():
        return []
    with closing(_abrir_ro(caminho)) as con:
        colunas = {r[1] for r in con.execute('PRAGMA table_info(revisoes)')}
        if 'tempo_estudo_minutos' not in colunas:
            return []
        partes = ['tempo_estudo_minutos BETWEEN 1 AND 5999']
        if 'contabilizar_tempo' in colunas:
            partes.append('contabilizar_tempo=1')
        args = []
        if concurso_id is not None:
            partes.append('perfil_id=?'); args.append(int(concurso_id))
        if inicio is not None:
            partes.append('data>=?'); args.append(_data(inicio).isoformat())
        if fim is not None:
            partes.append('data<=?'); args.append(_data(fim).isoformat())
        return con.execute('SELECT data, SUM(tempo_estudo_minutos)*60, COUNT(*) FROM revisoes WHERE '
            + ' AND '.join(partes) + ' GROUP BY data ORDER BY data', args).fetchall()


def _consolidar(caminho_banco, *, concurso_id=None, inicio=None, fim=None, origem='todos'):
    if origem not in ('todos','baterias','manual'):
        raise ValueError('Origem de tempo inválida.')
    por_dia = {}
    if origem != 'manual':
        with closing(_abrir_ro(caminho_banco)) as con:
            for dia, liquido, pausa, bruto, baterias in _linhas(con, concurso_id=concurso_id,inicio=inicio,fim=fim):
                por_dia[dia] = [int(liquido or 0), int(pausa or 0), int(bruto or 0), int(baterias or 0), 0, 0]
    if origem != 'baterias':
        for dia, segundos, quantidade in _linhas_manuais(caminho_banco, concurso_id=concurso_id,inicio=inicio,fim=fim):
            valores = por_dia.setdefault(dia,[0,0,0,0,0,0])
            valores[4] += int(segundos or 0); valores[5] += int(quantidade or 0)
    return [(dia,*v) for dia,v in sorted(por_dia.items())]


def _inicio_mes(dia):
    return dia.replace(day=1)


def _proximo_mes(dia):
    return (dia.replace(day=28) + timedelta(days=4)).replace(day=1)


def _chave(dia, agrupamento):
    if agrupamento == 'dia':
        return dia
    if agrupamento == 'semana':
        return dia - timedelta(days=dia.weekday())
    if agrupamento == 'mes':
        return _inicio_mes(dia)
    if agrupamento == 'ano':
        return dia.replace(month=1, day=1)
    raise ValueError('Agrupamento inválido.')


def _seguinte(chave, agrupamento):
    if agrupamento == 'dia':
        return chave + timedelta(days=1)
    if agrupamento == 'semana':
        return chave + timedelta(days=7)
    if agrupamento == 'mes':
        return _proximo_mes(chave)
    if agrupamento == 'ano':
        return chave.replace(year=chave.year+1)
    raise ValueError('Agrupamento inválido.')


def _rotulo(chave, agrupamento, fim):
    if agrupamento == 'dia':
        return chave.strftime('%d/%m/%Y')
    if agrupamento == 'semana':
        return f'{chave:%d/%m} – {min(chave+timedelta(days=6),fim):%d/%m/%Y}'
    if agrupamento == 'mes':
        return chave.strftime('%m/%Y')
    return str(chave.year)


def consultar_serie(caminho_banco, *, inicio, fim, agrupamento='dia', concurso_id=None, origem='todos'):
    """Grupos de calendário com indicação explícita de ausência de dados.

    Os intervalos parciais são contabilizados apenas no intervalo solicitado.
    Nenhuma conexão pode inserir/atualizar dados no banco de produção.
    """
    a, b = _data(inicio), _data(fim)
    if a > b:
        raise ValueError('A data inicial deve ser anterior ou igual à final.')
    if (b-a).days > 36525:
        raise ValueError('Intervalo de consulta excessivo.')
    todos = _consolidar(caminho_banco, concurso_id=concurso_id, fim=b, origem=origem)
    primeiro = _data(todos[0][0]) if todos else None
    registros = [r for r in todos if a.isoformat() <= r[0] <= b.isoformat()]
    grupos = {}
    for data_str, liquido, pausa, bruto, baterias, manual, revisoes in registros:
        chave = _chave(_data(data_str), agrupamento)
        dados = grupos.setdefault(chave, [0, 0, 0, 0, 0, 0, 0])
        dados[0] += liquido
        dados[1] += pausa
        dados[2] += bruto
        dados[3] += baterias
        dados[4] += 1
        dados[5] += manual
        dados[6] += revisoes
    resultado = []
    cursor = _chave(a, agrupamento)
    while cursor <= b:
        valores = grupos.get(cursor, [0, 0, 0, 0, 0, 0, 0])
        resultado.append({
            'inicio': cursor.isoformat(), 'rotulo': _rotulo(cursor, agrupamento, b),
            'liquido': valores[0]+valores[5], 'pausa': valores[1], 'bruto': valores[2],
            'liquido_baterias': valores[0], 'liquido_manual': valores[5], 'revisoes_manuais': valores[6],
            'baterias': valores[3], 'dias_registrados': valores[4],
            'tem_registro': bool(valores[4]),
        })
        cursor = _seguinte(cursor, agrupamento)
    return {'inicio': a.isoformat(), 'fim': b.isoformat(), 'agrupamento': agrupamento,
            'primeiro_registro': primeiro.isoformat() if primeiro else None,
            'linhas': resultado, 'total_segundos': sum(i['liquido'] for i in resultado),
            'total_pausas': sum(i['pausa'] for i in resultado),
            'dias_registrados': sum(1 for _ in registros),
            'baterias_periodo': sum(int(r[4] or 0) for r in registros),
            'total_baterias': sum(i['liquido_baterias'] for i in resultado),
            'total_manual': sum(i['liquido_manual'] for i in resultado),
            'revisoes_manuais': sum(i['revisoes_manuais'] for i in resultado)}


def consultar_resumo(caminho_banco, *, hoje=None, concurso_id=None, origem='todos'):
    hoje = _data(hoje or date.today())
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    mes_atual = _inicio_mes(hoje)
    mes_anterior = _inicio_mes(mes_atual - timedelta(days=1))
    semana_anterior = inicio_semana - timedelta(days=7)
    registros = _consolidar(caminho_banco, concurso_id=concurso_id, fim=hoje, origem=origem)
    primeiro = _data(registros[0][0]) if registros else None
    por_dia = {_data(r[0]): r[1]+r[5] for r in registros}
    def soma(a, b):
        return sum(v for d, v in por_dia.items() if a <= d <= b)
    def origens(a,b):
        linhas = [r for r in registros if a <= _data(r[0]) <= b]
        return {'baterias':sum(r[1] for r in linhas), 'manual':sum(r[5] for r in linhas), 'revisoes':sum(r[6] for r in linhas)}
    semana = soma(inicio_semana, hoje)
    sem_ant = soma(semana_anterior, inicio_semana-timedelta(days=1))
    mes = soma(mes_atual, hoje)
    mes_ant = soma(mes_anterior, mes_atual-timedelta(days=1))
    ano = soma(hoje.replace(month=1,day=1), hoje)
    dias_ativos = sum(1 for x in por_dia.values() if x > 0)
    return {'hoje': hoje.isoformat(), 'primeiro_registro': primeiro.isoformat() if primeiro else None,
            'semana': semana, 'semana_anterior': sem_ant, 'mes': mes,
            'mes_anterior': mes_ant, 'ano': ano, 'total': sum(por_dia.values()),
            'dias_ativos': dias_ativos,
            'origens_hoje': origens(hoje,hoje), 'origens_semana': origens(inicio_semana,hoje),
            'origens_mes': origens(mes_atual,hoje), 'origens_total': origens(date.min,hoje),
            'media_dia_ativo': int(round(sum(por_dia.values())/dias_ativos)) if dias_ativos else 0}


def formatar_variacao(atual, anterior):
    if anterior == 0:
        return 'Sem base anterior' if atual else 'Sem registros'
    return f'{(atual-anterior)*100/anterior:+.1f}%'.replace('.', ',')
