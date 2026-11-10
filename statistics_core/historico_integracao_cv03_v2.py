"""Adaptador de consulta histórico V2 para integração futura no VighnaStudy.

Somente leitura. Não importa o módulo banco.py, nem altera SQLite.
Inclui contrato estável para a janela Qt e avisos de origem das métricas.
"""
from __future__ import annotations

from datetime import date, datetime
from contextlib import closing
from pathlib import Path

from .historico_analitico_v1 import (
    analisar_tentativas, abrir_banco_somente_leitura, evolucao_mensal,
    janela_periodo,
)
from .historico_multifonte_v1 import analisar_fontes_historicas
from .historico_viewmodel_v1 import montar_modelo_relatorio
from .historico_consulta_legado_o_v1 import consultar_legado_global

PERIODOS_TELA = {
    '7 dias': 7,
    '30 dias': 30,
    '90 dias': 90,
    '180 dias': 180,
    '365 dias': 365,
    'Todo o histórico': 'completo',
    'Personalizado': 'personalizado',
}


def consultar_historico_v2(
    caminho_banco: str | Path, concurso_id: int, escolha: str = '30 dias', *,
    data_inicio: str | None = None, data_fim: str | None = None,
    hoje: date | None = None,
) -> dict:
    """Gera modelo de leitura sem modificar tabelas ou o arquivo de dados.

    Caso uma fonte de dados não exista, o núcleo multifonte expõe status de
    indisponibilidade. Se tentativas estiverem incompatíveis, não fabricamos
    números; exceção sinaliza falha para a interface.
    """
    if escolha not in PERIODOS_TELA:
        raise ValueError('Período de consulta desconhecido')
    if isinstance(concurso_id, bool) or not isinstance(concurso_id, int) or concurso_id < 1:
        raise ValueError('Concurso inválido')
    periodo = PERIODOS_TELA[escolha]
    # Fixar a data uma única vez evita discordância caso a consulta atravesse
    # a meia-noite local, especialmente com bases históricas extensas.
    referencia = hoje if hoje is not None else datetime.now().astimezone().date()
    janela = janela_periodo(periodo, inicio=data_inicio, fim=data_fim, hoje=referencia)
    if not Path(caminho_banco).is_file():
        raise FileNotFoundError('Arquivo do banco de estudos não encontrado')
    with closing(abrir_banco_somente_leitura(caminho_banco)) as conexao:
        # Uma transação de LEITURA preserva o mesmo snapshot SQLite entre
        # o período, o acumulado e as séries mensais. A aplicação pode gravar
        # novos estudos em outra conexão enquanto o relatório é calculado.
        # mode=ro + query_only impossibilitam escritas por esta conexão.
        conexao.execute('PRAGMA query_only = ON')
        conexao.execute('BEGIN')
        try:
            kwargs = {'hoje': referencia, 'inicio': data_inicio, 'fim': data_fim}
            tentativas = analisar_tentativas(conexao, concurso_id, periodo, **kwargs)
            fontes = analisar_fontes_historicas(conexao, concurso_id, periodo, **kwargs)
            meses = evolucao_mensal(conexao, concurso_id)
            legado_excel = consultar_legado_global(conexao)
        finally:
            # Finalizar explicitamente a transação libera o snapshot mesmo
            # quando há uma exceção; não há COMMIT porque não há gravações.
            conexao.rollback()
    modelo = montar_modelo_relatorio(tentativas, fontes, meses, legado_global=legado_excel)
    return {
        'periodo': {
            'nome': escolha,
            'inicio': janela.inicio.isoformat() if janela.inicio else None,
            'fim': janela.fim.isoformat() if janela.fim else None,
        },
        'concurso_id': concurso_id,
        'tentativas': tentativas,
        'fontes': fontes,
        'modelo': modelo,
        'meses': meses,
        'legado_excel_global': legado_excel,
        'somente_leitura': True,
    }


def numero(valor: object) -> str:
    if valor is None:
        return '—'
    if isinstance(valor, bool):
        return str(valor)
    if isinstance(valor, int):
        return f'{valor:,}'.replace(',', '.')
    if isinstance(valor, float):
        return f'{valor:.1f}'.replace('.', ',')
    return str(valor)


def percentual(valor: float | None) -> str:
    return '—' if valor is None else f'{valor:.1f}%'.replace('.', ',')


def pontos_percentuais(valor: float | None) -> str:
    if valor is None:
        return 'Sem base anterior'
    return f'{valor:+.1f} p.p.'.replace('.', ',')


def horas_de_foco(segundos: int | None) -> str:
    if segundos is None:
        return '—'
    return f'{int(segundos) // 3600}h {(int(segundos) % 3600) // 60:02d}min'


def linhas_fontes(modelo: dict) -> list[tuple[str, str, str, str]]:
    """Quatro fontes em unidades próprias; não somar tentativas e simulados."""
    perfil = modelo['indicadores_do_perfil']
    foco = modelo['indicadores_globais_nao_atribuiveis']['foco']
    return [
        ('Tentativas respondidas', numero(perfil['tentativas']['periodo']),
         numero(perfil['tentativas']['acumulado']), 'Perfil do concurso'),
        ('Revisões registradas', numero(perfil['revisoes']['periodo']),
         numero(perfil['revisoes']['acumulado']), 'Perfil do concurso'),
        ('Simulados concluídos', numero(perfil['simulados']['periodo']),
         numero(perfil['simulados']['acumulado']), 'Perfil do concurso'),
        ('Sessões com efetividade', numero(perfil['efetividade']['periodo']),
         numero(perfil['efetividade']['acumulado']), 'Perfil do concurso'),
        ('  dos quais simulados arquivados', numero(perfil['simulados'].get('arquivados_no_periodo')),
         numero(perfil['simulados'].get('arquivados_no_acumulado')), 'Já incluídos nos simulados'),
        ('  das quais medições arquivadas', numero(perfil['efetividade'].get('arquivadas_no_periodo')),
         numero(perfil['efetividade'].get('arquivadas_no_acumulado')), 'Já incluídas nas medições'),
        ('Revisões importadas do Excel', '—',
         numero((modelo['indicadores_globais_nao_atribuiveis'].get('revisoes_importadas_excel') or {}).get('revisoes_importadas_declaradas')),
         'Global; sem datas por revisão'),
        ('Tempo de foco efetivo', horas_de_foco(foco['tempo_periodo_segundos']),
         horas_de_foco(foco['tempo_acumulado_segundos']), 'Global; não atribuir ao perfil'),
    ]
