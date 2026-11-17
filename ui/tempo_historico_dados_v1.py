"""Consultas de tempo efetivo por dia/semana/mês/ano (SQLite somente leitura).

Fonte única: tempo_baterias_dia_v1 e tempo_baterias_v1. Não reconstrói
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
    tabelas = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('tempo_baterias_dia_v1','tempo_baterias_v1')")}
    if len(tabelas) != 2:
        con.close()
        raise FonteTempoIndisponivel('O contador de tempo ainda não possui registros persistentes nesta instalação.')
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
    where, args = _where(concurso_id, inicio, fim)
    return con.execute('''
        SELECT d.dia_local, SUM(d.tempo_liquido_segundos),
               SUM(d.pausa_segundos), SUM(d.duracao_bruta_segundos),
               COUNT(DISTINCT d.chave)
        FROM tempo_baterias_dia_v1 AS d
        INNER JOIN tempo_baterias_v1 AS b ON b.chave=d.chave
        ''' + where + ' GROUP BY d.dia_local ORDER BY d.dia_local', args).fetchall()


def _primeiro_dia(con, concurso_id=None):
    where, args = _where(concurso_id)
    linha = con.execute('''SELECT MIN(d.dia_local) FROM tempo_baterias_dia_v1 d
        INNER JOIN tempo_baterias_v1 b ON b.chave=d.chave''' + where, args).fetchone()
    return _data(linha[0]) if linha and linha[0] else None


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


def consultar_serie(caminho_banco, *, inicio, fim, agrupamento='dia', concurso_id=None):
    """Grupos de calendário com indicação explícita de ausência de dados.

    Os intervalos parciais são contabilizados apenas no intervalo solicitado.
    Nenhuma conexão pode inserir/atualizar dados no banco de produção.
    """
    a, b = _data(inicio), _data(fim)
    if a > b:
        raise ValueError('A data inicial deve ser anterior ou igual à final.')
    if (b-a).days > 36525:
        raise ValueError('Intervalo de consulta excessivo.')
    with closing(_abrir_ro(caminho_banco)) as con:
        registros = _linhas(con, concurso_id=concurso_id, inicio=a, fim=b)
        primeiro = _primeiro_dia(con, concurso_id)
    grupos = {}
    for data_str, liquido, pausa, bruto, baterias in registros:
        chave = _chave(_data(data_str), agrupamento)
        dados = grupos.setdefault(chave, [0, 0, 0, 0, 0])
        dados[0] += int(liquido or 0)
        dados[1] += int(pausa or 0)
        dados[2] += int(bruto or 0)
        dados[3] += int(baterias or 0)
        dados[4] += 1
    resultado = []
    cursor = _chave(a, agrupamento)
    while cursor <= b:
        valores = grupos.get(cursor, [0, 0, 0, 0, 0])
        resultado.append({
            'inicio': cursor.isoformat(), 'rotulo': _rotulo(cursor, agrupamento, b),
            'liquido': valores[0], 'pausa': valores[1], 'bruto': valores[2],
            'baterias': valores[3], 'dias_registrados': valores[4],
            'tem_registro': bool(valores[4]),
        })
        cursor = _seguinte(cursor, agrupamento)
    return {'inicio': a.isoformat(), 'fim': b.isoformat(), 'agrupamento': agrupamento,
            'primeiro_registro': primeiro.isoformat() if primeiro else None,
            'linhas': resultado, 'total_segundos': sum(i['liquido'] for i in resultado),
            'total_pausas': sum(i['pausa'] for i in resultado),
            'dias_registrados': sum(1 for _ in registros),
            'baterias_periodo': sum(int(r[4] or 0) for r in registros)}


def consultar_resumo(caminho_banco, *, hoje=None, concurso_id=None):
    hoje = _data(hoje or date.today())
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    mes_atual = _inicio_mes(hoje)
    mes_anterior = _inicio_mes(mes_atual - timedelta(days=1))
    semana_anterior = inicio_semana - timedelta(days=7)
    with closing(_abrir_ro(caminho_banco)) as con:
        registros = _linhas(con, concurso_id=concurso_id, fim=hoje)
        primeiro = _primeiro_dia(con, concurso_id)
    por_dia = {_data(r[0]): int(r[1] or 0) for r in registros}
    def soma(a, b):
        return sum(v for d, v in por_dia.items() if a <= d <= b)
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
            'media_dia_ativo': int(round(sum(por_dia.values())/dias_ativos)) if dias_ativos else 0}


def formatar_variacao(atual, anterior):
    if anterior == 0:
        return 'Sem base anterior' if atual else 'Sem registros'
    return f'{(atual-anterior)*100/anterior:+.1f}%'.replace('.', ',')
