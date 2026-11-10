"""VighnaStudy: registro aditivo e idempotente de tempo líquido das baterias.

A fonte de verdade para sessões/tentativas acadêmicas permanece no banco legado.
Aqui ficam APENAS intervalos de baterias finalizadas e pausas medidas B21.
Não inventa pausas para sessões anteriores à instalação deste módulo.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
import json
import math
from pathlib import Path
import sqlite3


_SCHEMA = """
CREATE TABLE IF NOT EXISTS tempo_baterias_v1 (
    chave TEXT PRIMARY KEY,
    sessao_questoes_id INTEGER,
    concurso_id INTEGER,
    origem TEXT NOT NULL,
    inicio_local TEXT NOT NULL,
    fim_local TEXT NOT NULL,
    duracao_bruta_segundos INTEGER NOT NULL CHECK (duracao_bruta_segundos >= 0),
    pausa_total_segundos INTEGER NOT NULL CHECK (pausa_total_segundos >= 0),
    tempo_liquido_segundos INTEGER NOT NULL CHECK (tempo_liquido_segundos >= 0),
    pausas_json TEXT NOT NULL DEFAULT '[]',
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (tempo_liquido_segundos <= duracao_bruta_segundos)
);
CREATE TABLE IF NOT EXISTS tempo_baterias_dia_v1 (
    chave TEXT NOT NULL,
    dia_local TEXT NOT NULL,
    duracao_bruta_segundos INTEGER NOT NULL CHECK (duracao_bruta_segundos >= 0),
    pausa_segundos INTEGER NOT NULL CHECK (pausa_segundos >= 0),
    tempo_liquido_segundos INTEGER NOT NULL CHECK (tempo_liquido_segundos >= 0),
    PRIMARY KEY (chave, dia_local),
    FOREIGN KEY (chave) REFERENCES tempo_baterias_v1(chave) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_tempo_baterias_dia_v1_data
    ON tempo_baterias_dia_v1(dia_local);
"""


def _dt(value: str | datetime) -> datetime:
    resultado = value if isinstance(value, datetime) else datetime.fromisoformat(str(value))
    if not isinstance(resultado, datetime):
        raise ValueError("Data e hora inválidas")
    return resultado


def _partes_por_dia(inicio: datetime, fim: datetime) -> dict[str, float]:
    """Segundos de um intervalo por dia local; inclui a travessia de meia-noite."""
    if fim <= inicio:
        return {}
    if inicio.tzinfo != fim.tzinfo:
        # Converter ambas ao fuso de início evita comparar horários heterogêneos.
        if inicio.tzinfo is None or fim.tzinfo is None:
            raise ValueError("Datas devem usar o mesmo tipo de fuso")
        fim = fim.astimezone(inicio.tzinfo)
    cursor = inicio
    partes: dict[str, float] = {}
    while cursor < fim:
        seguinte = datetime.combine(cursor.date() + timedelta(days=1), time.min, tzinfo=cursor.tzinfo)
        limite = min(fim, seguinte)
        if limite <= cursor:
            raise ValueError("Intervalo temporal inconsistente")
        chave = cursor.date().isoformat()
        partes[chave] = partes.get(chave, 0.0) + (limite - cursor).total_seconds()
        cursor = limite
    return partes


def _inteiros_com_total(fracoes: dict[str, float], total: int) -> dict[str, int]:
    """Distribuição inteira conservando o total, sem perder segundos por arredondamento."""
    if not fracoes:
        return {}
    total = max(0, int(total))
    pesos = {k: max(0.0, float(v)) for k, v in fracoes.items()}
    divisor = sum(pesos.values())
    if divisor <= 0:
        return {k: total if k == list(pesos)[-1] else 0 for k in pesos}
    exatos = {k: total * v / divisor for k, v in pesos.items()}
    resultado = {k: int(math.floor(v)) for k, v in exatos.items()}
    restantes = total - sum(resultado.values())
    ordem = sorted(exatos, key=lambda k: (-(exatos[k] - resultado[k]), k))
    for k in ordem[:restantes]:
        resultado[k] += 1
    return resultado


def _segmentos(inicio: datetime, fim: datetime, bruto: int, pausa: int,
               pausas: list[dict]) -> list[tuple[str, int, int, int]]:
    """Divide tempo e pausas por data; soma da coluna líquida é sempre bruto-pausa."""
    bruto = max(0, int(bruto))
    pausa = min(bruto, max(0, int(pausa)))
    partes_brutas = _partes_por_dia(inicio, fim)
    if not partes_brutas:
        partes_brutas = {inicio.date().isoformat(): 1.0}
    brutos = _inteiros_com_total(partes_brutas, bruto)
    pesos_pausa = {k: 0.0 for k in brutos}
    for registro in pausas:
        try:
            p0 = _dt(registro["inicio_iso"])
            p1 = _dt(registro["fim_iso"])
            if p0 < inicio:
                p0 = inicio
            if p1 > fim:
                p1 = fim
            for dia, segundos in _partes_por_dia(p0, p1).items():
                if dia in pesos_pausa:
                    pesos_pausa[dia] += segundos
        except (KeyError, TypeError, ValueError):
            continue
    # Pausas registradas no B21 têm relógio monotônico; se for impossível
    # distribuí-las pelas datas, atribui-se o total ao fim da bateria.
    if sum(pesos_pausa.values()) <= 0:
        pesos_pausa[fim.date().isoformat()] = 1.0
    pausas_por_dia = {k: 0 for k in brutos}
    restante = pausa
    for k in sorted(pesos_pausa, key=lambda item: (-pesos_pausa[item], item)):
        quantidade = min(brutos[k], restante)
        if quantidade > 0:
            desejada = round(pausa * pesos_pausa[k] / max(1, sum(pesos_pausa.values())))
            quantidade = min(quantidade, desejada)
            pausas_por_dia[k] += quantidade
            restante -= quantidade
    for k in reversed(list(brutos)):
        if not restante:
            break
        quantidade = min(restante, brutos[k] - pausas_por_dia[k])
        pausas_por_dia[k] += quantidade
        restante -= quantidade
    if restante:
        raise ValueError("Pausa maior que a duração atribuída à bateria")
    return [(k, brutos[k], pausas_por_dia[k], brutos[k] - pausas_por_dia[k])
            for k in sorted(brutos)]


def registrar_bateria_finalizada(
    caminho_banco: str | Path, *, chave: str, inicio_local: str,
    fim_local: str, duracao_bruta_segundos: int, pausas: list[dict] | None,
    sessao_questoes_id: int | None = None, concurso_id: int | None = None,
    origem: str = "questoes",
) -> bool:
    """True se gravou; False se já existia. Nenhuma tabela acadêmica é alterada."""
    chave = str(chave).strip()
    if not chave:
        raise ValueError("Chave da bateria vazia")
    inicio, fim = _dt(inicio_local), _dt(fim_local)
    if fim < inicio:
        raise ValueError("Fim da bateria anterior ao início")
    bruto = max(0, int(duracao_bruta_segundos))
    pausas = [dict(p) for p in (pausas or [])]
    pausa = min(bruto, sum(max(0, int(p.get("duracao_segundos") or 0)) for p in pausas))
    partes = _segmentos(inicio, fim, bruto, pausa, pausas)
    banco = Path(caminho_banco)
    if not banco.is_file():
        raise FileNotFoundError(f"Banco acadêmico não encontrado: {banco}")
    with sqlite3.connect(str(banco), timeout=5.0) as con:
        con.execute("PRAGMA foreign_keys=ON")
        con.executescript(_SCHEMA)
        existente = con.execute("SELECT 1 FROM tempo_baterias_v1 WHERE chave=?", (chave,)).fetchone()
        if existente:
            return False
        con.execute("""INSERT INTO tempo_baterias_v1
            (chave,sessao_questoes_id,concurso_id,origem,inicio_local,fim_local,
             duracao_bruta_segundos,pausa_total_segundos,tempo_liquido_segundos,pausas_json)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (chave, sessao_questoes_id, concurso_id, str(origem), inicio.isoformat(),
             fim.isoformat(), bruto, pausa, bruto - pausa,
             json.dumps(pausas, ensure_ascii=False, default=str)))
        con.executemany("""INSERT INTO tempo_baterias_dia_v1
            (chave,dia_local,duracao_bruta_segundos,pausa_segundos,tempo_liquido_segundos)
            VALUES (?,?,?,?,?)""",
            [(chave, *p) for p in partes])
        return True


def obter_resumo_diario(caminho_banco: str | Path, dia: str | None = None) -> dict:
    """Leitura sem criação de tabela; não estima pausas de sessões legadas."""
    dia = dia or date.today().isoformat()
    date.fromisoformat(dia)
    resultado = {"dia": dia, "tempo_liquido_segundos": 0, "pausa_segundos": 0,
                 "tempo_bruto_segundos": 0, "baterias": 0, "respondidas": 0,
                 "acertos": 0, "erros": 0, "fonte_temporal": "a_partir_da_ativacao"}
    with sqlite3.connect(str(caminho_banco), timeout=5.0) as con:
        tabela = con.execute("""SELECT 1 FROM sqlite_master
                                  WHERE type='table' AND name='tempo_baterias_dia_v1'""").fetchone()
        if tabela:
            linha = con.execute("""SELECT COALESCE(SUM(tempo_liquido_segundos),0),
                COALESCE(SUM(pausa_segundos),0), COALESCE(SUM(duracao_bruta_segundos),0)
                FROM tempo_baterias_dia_v1 WHERE dia_local=?""", (dia,)).fetchone()
            resultado.update(zip(("tempo_liquido_segundos", "pausa_segundos",
                                  "tempo_bruto_segundos"), map(int, linha)))
            resultado["baterias"] = con.execute("""SELECT COUNT(*) FROM tempo_baterias_v1
                                                  WHERE substr(fim_local,1,10)=?""", (dia,)).fetchone()[0]
        tentativas = con.execute("""SELECT COUNT(*),
            COALESCE(SUM(CASE WHEN correta=1 THEN 1 ELSE 0 END),0),
            COALESCE(SUM(CASE WHEN correta=0 THEN 1 ELSE 0 END),0)
            FROM tentativas_questoes WHERE substr(respondida_em,1,10)=?""", (dia,)).fetchone()
        resultado["respondidas"], resultado["acertos"], resultado["erros"] = map(int, tentativas)
    return resultado


def formatar_duracao(segundos: int) -> str:
    total = max(0, int(segundos))
    horas, minutos = divmod(total // 60, 60)
    return f"{horas}h {minutos:02d}min" if horas else f"{minutos}min"
