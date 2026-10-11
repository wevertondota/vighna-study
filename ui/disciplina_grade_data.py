"""Projeção somente leitura para a grade de disciplinas do perfil.

Não consulta o banco: recebe linhas das APIs existentes. Evita confundir
revisões com sessões ou percentual registrado com domínio estatístico.
"""

from datetime import date, datetime


def _data(valor):
    if isinstance(valor, date):
        return valor if not isinstance(valor, datetime) else valor.date()
    texto = str(valor or '').strip()
    if not texto:
        return None
    try:
        return date.fromisoformat(texto[:10])
    except ValueError:
        pass
    try:
        return datetime.strptime(texto[:10], '%d/%m/%Y').date()
    except ValueError:
        return None


def _texto_data(valor):
    convertido = _data(valor)
    return convertido.strftime('%d/%m/%Y') if convertido else '—'


def construir_grade(disciplinas, listar_topicos, hoje=None):
    """Retorna registros estáveis respeitando a ordem oficial das disciplinas.

    ``listar_topicos`` deve receber nome e retornar os oito campos históricos
    de ``listar_topicos_gerenciamento``. Não cria, altera nem remove dados.
    """
    hoje = hoje or date.today()
    if isinstance(hoje, datetime):
        hoje = hoje.date()
    if not isinstance(hoje, date):
        raise TypeError('hoje precisa ser date')
    resultado = []
    for disciplina_id, nome, disciplina_pausada in disciplinas:
        topicos = list(listar_topicos(nome))
        if not topicos:
            resultado.append({
                'disciplina_id': int(disciplina_id), 'disciplina': str(nome),
                'topico_id': None, 'topico': '— Sem tópicos vinculados —',
                'revisoes': None, 'ultima': '—', 'proxima': '—',
                'ultima_ordem': None, 'proxima_ordem': None,
                'percentual': None,
                'situacao': 'Pausada' if disciplina_pausada else 'Sem tópicos',
                'pausado': bool(disciplina_pausada),
            })
            continue
        for linha in topicos:
            if len(linha) < 8:
                raise ValueError('listagem de tópicos precisa ter oito campos')
            id_topico, topico, revisoes, ultima, proxima, percentual, _importancia, topico_pausado = linha[:8]
            proxima_dt = _data(proxima)
            ultima_dt = _data(ultima)
            pausado = bool(disciplina_pausada or topico_pausado)
            if pausado:
                situacao = 'Pausada'
            elif proxima_dt is None:
                situacao = 'Sem data'
            elif proxima_dt < hoje:
                situacao = 'Atrasada'
            elif proxima_dt == hoje:
                situacao = 'Hoje'
            else:
                situacao = 'Agendada'
            try:
                percentual_num = float(percentual) if percentual is not None else None
            except (ValueError, TypeError):
                percentual_num = None
            resultado.append({
                'disciplina_id': int(disciplina_id),
                'disciplina': str(nome),
                'topico_id': int(id_topico), 'topico': str(topico),
                'revisoes': int(revisoes or 0),
                'ultima': _texto_data(ultima), 'proxima': _texto_data(proxima),
                'ultima_ordem': ultima_dt, 'proxima_ordem': proxima_dt,
                'percentual': percentual_num,
                'situacao': situacao,
                'pausado': pausado,
            })
    return resultado


def resumir_disciplinas(disciplinas, listar_topicos):
    """Uma linha por disciplina, sem expor tópicos na grade principal.

    A contagem utiliza a listagem histórica já disponível e não executa
    escrita nem interpreta revisões como sessões. O editor original permanece
    responsável por apresentar e modificar os conteúdos detalhados.
    """
    resultado = []
    for disciplina_id, nome, pausada in disciplinas:
        topicos = list(listar_topicos(nome))
        quantidade = len(topicos)
        resultado.append({
            'disciplina_id': int(disciplina_id),
            'disciplina': str(nome),
            'quantidade_topicos': quantidade,
            'situacao': 'Pausada' if pausada else ('Sem tópicos' if quantidade == 0 else 'Ativa'),
            'pausado': bool(pausada),
        })
    return resultado
