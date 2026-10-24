"""Arena F15: indicadores exclusivos de leitura para os cinco jogos.

Este módulo não cria/migra tabelas, não salva dados e não altera os
recordes utilizados pelos motores. Consultas parametrizadas a partir do
CAMINHO_BANCO oficial acessado por banco.conectar().
"""
from contextlib import closing
from datetime import datetime
from banco import conectar

_JOGOS = frozenset({"chimpanze", "memoria", "sequencia", "rotacao_visual", "quebra_cabeca"})


def _data(texto):
    if not texto:
        return None
    try:
        return datetime.fromisoformat(str(texto)).strftime("%d/%m/%Y")
    except (ValueError, TypeError, OverflowError):
        return None


def _tempo(segundos):
    segundos = int(segundos)
    minutos, resto = divmod(segundos, 60)
    horas, minutos = divmod(minutos, 60)
    return f"{horas:02d}:{minutos:02d}:{resto:02d}" if horas else f"{minutos:02d}:{resto:02d}"


def _linha(conexao, jogo, coluna, *, minimo=0, decrescente=True):
    """Somente colunas predefinidas, nunca nomes recebidos do usuário."""
    if coluna not in {"pontuacao", "nivel", "duracao_segundos", "movimentos"}:
        raise ValueError("Coluna não autorizada")
    sentido = "DESC" if decrescente else "ASC"
    return conexao.execute(
        f"SELECT {coluna}, criado_em FROM jogos_resultados "
        f"WHERE jogo = ? AND {coluna} IS NOT NULL AND {coluna} >= ? "
        f"ORDER BY {coluna} {sentido}, criado_em DESC, id DESC LIMIT 1",
        (jogo, minimo),
    ).fetchone()


def obter_indicadores_reais(jogo):
    """Retorna até quatro linhas (rótulo, valor, data) do jogo ativo.

    Sem resultados: retorna uma linha de ausência real de histórico.
    Queries são SELECT, não usam fetchall e cada jogo é parametrizado.
    """
    if jogo not in _JOGOS:
        raise ValueError("Jogo não reconhecido")
    with closing(conectar()) as conexao:
        total, ultimo = conexao.execute(
            "SELECT COUNT(*), MAX(criado_em) FROM jogos_resultados WHERE jogo = ?",
            (jogo,),
        ).fetchone()
        if not total:
            return [("Histórico do jogo", "Sem partidas registradas", None)]
        linhas = []
        if jogo == "chimpanze":
            # pontuacao = melhor nível COMPLETADO; nivel pode incluir tentativa falhada.
            concluido = _linha(conexao, jogo, "pontuacao")
            alcancado = _linha(conexao, jogo, "nivel")
            if concluido:
                linhas.append(("Maior nível concluído", str(concluido[0]), _data(concluido[1])))
            if alcancado:
                linhas.append(("Maior nível alcançado", str(alcancado[0]), _data(alcancado[1])))
        elif jogo in {"memoria", "quebra_cabeca"}:
            movimentos = _linha(conexao, jogo, "movimentos", minimo=1, decrescente=False)
            tempo = _linha(conexao, jogo, "duracao_segundos", minimo=1, decrescente=False)
            if movimentos:
                linhas.append(("Menor nº de movimentos", str(movimentos[0]), _data(movimentos[1])))
            if tempo:
                linhas.append(("Tempo mais rápido", _tempo(tempo[0]), _data(tempo[1])))
        elif jogo == "sequencia":
            recorde = _linha(conexao, jogo, "nivel")
            if recorde:
                linhas.append(("Maior sequência concluída", str(recorde[0]), _data(recorde[1])))
        elif jogo == "rotacao_visual":
            pontuacao = _linha(conexao, jogo, "pontuacao")
            nivel = _linha(conexao, jogo, "nivel")
            if pontuacao:
                linhas.append(("Maior pontuação", f"{pontuacao[0]} pts", _data(pontuacao[1])))
            if nivel:
                linhas.append(("Maior nível alcançado", str(nivel[0]), _data(nivel[1])))
        linhas.append(("Partidas registradas", str(total), None))
        linhas.append(("Último registro", _data(ultimo) or "Data indisponível", None))
        return linhas[:4]
