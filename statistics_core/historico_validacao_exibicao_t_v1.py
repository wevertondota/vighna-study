"""Histórico V2 / Etapa T: invariantes de apresentação, sem E/S nem Qt.

Não transforma dados: rejeita resultados inconsistentes para impedir que a
janela mostre números plausíveis mas incompatíveis entre si. Esta camada NÃO
faz consultas e NÃO altera registros acadêmicos.
"""
from __future__ import annotations

from datetime import date
from math import isfinite
from re import fullmatch


def _inteiro(valor, nome: str) -> int:
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
        raise ValueError(f'Contagem historica invalida: {nome}')
    return valor


def _taxa(valor, nome: str, *, minimo: float = 0.0, maximo: float = 100.0):
    if valor is None:
        return None
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f'Taxa historica invalida: {nome}')
    valor = float(valor)
    if not isfinite(valor) or not minimo <= valor <= maximo:
        raise ValueError(f'Taxa historica fora do intervalo: {nome}')
    return valor


def _coerencia_taxa(contagem: int, acertos: int | None, taxa: float | None, campo: str):
    if taxa is None:
        if contagem > 0:
            raise ValueError('Taxa ausente em periodo com respostas: ' + campo)
        return
    if not contagem:
        raise ValueError('Taxa sem respostas: ' + campo)
    if acertos is not None and abs(taxa - 100 * acertos / contagem) > 0.06:
        raise ValueError('Desempenho incompativel com respostas e acertos: ' + campo)


def validar_exibicao_historica(dados: dict, *, escolha: str | None = None,
                                concurso_id: int | None = None) -> None:
    """Verifica a coerência dos indicadores ANTES de preencher os widgets.

    Campos opcionais antigos são aceitos quando ausentes (testes de contratos
    legados), mas, se fornecidos, devem ser consistentes. Em dados reais, o
    adaptador apresenta contrato completo.
    """
    if not isinstance(dados, dict):
        raise ValueError('Resultado historico nao e mapa')
    modelo = dados.get('modelo')
    if not isinstance(modelo, dict):
        raise ValueError('Modelo historico ausente')
    if dados.get('somente_leitura', True) is not True:
        raise ValueError('Consulta analitica nao declarada somente leitura')
    if concurso_id is not None:
        for candidato in (dados.get('concurso_id'), modelo.get('perfil')):
            if candidato is not None and (type(candidato) is not int or candidato != concurso_id):
                raise ValueError('Resultado de outro perfil de concurso')
    periodo = dados.get('periodo')
    if periodo is not None:
        if not isinstance(periodo, dict) or not isinstance(periodo.get('nome'), str):
            raise ValueError('Periodo de consulta invalido')
        if escolha is not None and periodo['nome'] != escolha:
            raise ValueError('Resultado pertencente a outro periodo')
        ini, fim = periodo.get('inicio'), periodo.get('fim')
        if (ini is None) != (fim is None):
            raise ValueError('Limites da janela incompletos')
        if ini is not None:
            a, b = date.fromisoformat(ini), date.fromisoformat(fim)
            if a > b:
                raise ValueError('Janela temporal invertida')
    t = modelo['indicadores_do_perfil']['tentativas']
    resp = _inteiro(t['periodo'], 'periodo')
    if 'acumulado' in t and t['acumulado'] is not None:
        acum = _inteiro(t['acumulado'], 'acumulado')
        if resp > acum:
            raise ValueError('Periodo supera o total acumulado')
    else:
        acum = None
    acertos = _inteiro(t['acertos_periodo'], 'acertos_periodo') if 'acertos_periodo' in t else None
    if acertos is not None and acertos > resp:
        raise ValueError('Acertos maiores que respostas')
    _coerencia_taxa(resp, acertos, _taxa(t['taxa_periodo_pct'], 'taxa_periodo_pct'), 'periodo')
    _taxa(t['taxa_acumulada_pct'], 'taxa_acumulada_pct')
    _taxa(t['variacao_pp'], 'variacao_pp', minimo=-100.0, maximo=100.0)

    meses = dados['meses']
    if not isinstance(meses, (tuple, list)):
        raise ValueError('Serie mensal invalida')
    ultimo = None
    total_mensal = 0
    for registro in meses:
        if not isinstance(registro, dict):
            raise ValueError('Item mensal invalido')
        mes = registro.get('mes')
        if not isinstance(mes, str) or not fullmatch(r'\d{4}-(0[1-9]|1[0-2])', mes):
            raise ValueError('Mes nao reconhecido')
        if ultimo is not None and mes <= ultimo:
            raise ValueError('Serie mensal duplicada ou fora da ordem')
        ultimo = mes
        n = _inteiro(registro['respondidas'], f'respondidas/{mes}')
        a = _inteiro(registro['acertos'], f'acertos/{mes}')
        if a > n:
            raise ValueError('Acertos do mes excedem respondidas')
        _coerencia_taxa(n, a, _taxa(registro['desempenho'], f'desempenho/{mes}'), f'mes/{mes}')
        total_mensal += n
    if acum is not None and total_mensal > acum:
        raise ValueError('Somatorio mensal ultrapassa historico acumulado')
