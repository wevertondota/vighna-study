"""Núcleo de inteligência operacional do VighnaStudy.

Este módulo concentra cache analítico, recomendação explicável e preparação
para o Modo Foco. Ele não depende da interface gráfica e pode ser testado de
forma isolada.
"""

from __future__ import annotations

import math
import time
from datetime import date, datetime
from typing import Any, Callable


class CacheAnalitico:
    """Cache curto em memória para evitar recomputações repetidas na mesma tela."""

    def __init__(self, ttl_padrao: float = 12.0):
        self.ttl_padrao = float(ttl_padrao)
        self._dados: dict[str, tuple[float, Any]] = {}
        self.acertos = 0
        self.falhas = 0

    def obter(self, chave: str, carregador: Callable[[], Any], ttl: float | None = None):
        agora = time.monotonic()
        validade = self.ttl_padrao if ttl is None else max(0.0, float(ttl))
        registro = self._dados.get(str(chave))
        if registro is not None:
            criado, valor = registro
            if agora - criado <= validade:
                self.acertos += 1
                return valor
        self.falhas += 1
        valor = carregador()
        self._dados[str(chave)] = (agora, valor)
        return valor

    def definir(self, chave: str, valor: Any):
        self._dados[str(chave)] = (time.monotonic(), valor)
        return valor

    def invalidar(self, prefixo: str | None = None):
        if prefixo is None:
            self._dados.clear()
            return
        prefixo = str(prefixo)
        for chave in list(self._dados):
            if chave.startswith(prefixo):
                self._dados.pop(chave, None)

    def estatisticas(self) -> dict[str, int]:
        return {
            "itens": len(self._dados),
            "acertos": int(self.acertos),
            "falhas": int(self.falhas),
        }


def _limitar(valor: float, minimo: float, maximo: float) -> float:
    return max(minimo, min(maximo, valor))


def _arredondar_5(minutos: float) -> int:
    return max(5, int(round(float(minutos) / 5.0) * 5))


def _texto_nao_vazio(valor: Any) -> str:
    return str(valor or "").strip()


def montar_preparacao_foco(
    recomendacao: dict,
    minutos: int | None = None,
    atividade: str | None = None,
    rotulo: str | None = None,
) -> dict:
    """Transforma uma recomendação em contexto do Modo Foco sem iniciar o timer."""

    recomendacao = dict(recomendacao or {})
    minutos = int(minutos or recomendacao.get("minutos") or 25)
    atividade = _texto_nao_vazio(atividade or recomendacao.get("atividade") or "Estudo livre")
    rotulo = _texto_nao_vazio(rotulo or recomendacao.get("rotulo_sessao") or "sessão recomendada")
    meta_questoes = max(0, int(recomendacao.get("questoes_alvo") or 0))
    origem = _texto_nao_vazio(recomendacao.get("origem_texto") or "Estudar agora V5")

    if atividade in {"Questões", "Treino adaptativo", "Teste de retenção"} and meta_questoes > 0:
        # Impede que uma alternativa muito curta preserve uma meta incompatível.
        meta_questoes = min(meta_questoes, max(5, int(round(minutos / 2.0))))
    else:
        meta_questoes = 0

    observacoes = [origem, rotulo]
    if meta_questoes:
        observacoes.append(f"meta sugerida: {meta_questoes} questões")
    if recomendacao.get("calibracao_aplicada"):
        observacoes.append("duração calibrada pelo histórico real")

    return {
        "minutos": minutos,
        "atividade": atividade,
        "disciplina": recomendacao.get("disciplina"),
        "topico_id": recomendacao.get("topico_id"),
        "topico": recomendacao.get("topico"),
        "observacao": " • ".join(parte for parte in observacoes if parte),
        "questoes_alvo": meta_questoes,
        "origem": origem,
        "plano_chave": None,
        "abrir_questoes_ao_iniciar": bool(meta_questoes > 0),
    }


class MotorRecomendacaoV4:
    """Seleciona uma sessão usando urgência, domínio, rotação e histórico real.

    O motor é propositalmente explicável: cada ajuste relevante é devolvido em
    ``score_explicado`` para que a interface possa mostrar por que a sugestão
    apareceu. O motor não registra nada; persistência fica a cargo do banco.
    """

    def __init__(
        self,
        fila: list[dict] | None,
        adaptativas: list[dict] | None,
        contexto: dict | None,
        calibracao: dict | None = None,
        perfil_decisoes: dict | None = None,
        hoje: date | datetime | str | None = None,
        usar_calibracao: bool = True,
        usar_historico_decisoes: bool = True,
    ):
        self.fila = list(fila or [])
        self.adaptativas = list(adaptativas or [])
        self.contexto = dict(contexto or {})
        self.calibracao = dict(calibracao or {})
        self.perfil_decisoes = dict(perfil_decisoes or {})
        self.usar_calibracao = bool(usar_calibracao)
        self.usar_historico_decisoes = bool(usar_historico_decisoes)
        self.hoje = self._normalizar_data(hoje)

    @staticmethod
    def _normalizar_data(valor):
        if isinstance(valor, datetime):
            return valor.date()
        if isinstance(valor, date):
            return valor
        if valor:
            try:
                return date.fromisoformat(str(valor)[:10])
            except Exception:
                pass
        return date.today()

    def _ajuste_rotacao(self, disciplina: str, topico: str | None, atividade: str) -> tuple[float, list[dict], list[str]]:
        disciplina = _texto_nao_vazio(disciplina)
        topico = _texto_nao_vazio(topico)
        atividade = _texto_nao_vazio(atividade)
        ajuste = 0.0
        partes: list[dict] = []
        motivos: list[str] = []

        distribuicao = self.contexto.get("distribuicao") or {}
        dist = distribuicao.get(disciplina) or {}
        percentual = float(dist.get("percentual") or 0.0)
        semana_segundos = int((self.contexto.get("foco") or {}).get("semana_segundos") or 0)

        if disciplina:
            if percentual >= 55:
                ajuste -= 10
                partes.append({"rotulo": "concentração semanal", "pontos": -10.0})
                motivos.append(f"{disciplina} já concentrou {percentual:.0f}% do foco da semana")
            elif 0 < percentual <= 15:
                ajuste += 4
                partes.append({"rotulo": "matéria pouco trabalhada", "pontos": 4.0})
                motivos.append(f"{disciplina} recebeu pouco foco nesta semana")
            elif percentual == 0 and semana_segundos > 0:
                ajuste += 5
                partes.append({"rotulo": "matéria ainda sem foco na semana", "pontos": 5.0})
                motivos.append(f"{disciplina} ainda não recebeu foco nesta semana")

        recentes = list(self.contexto.get("recentes") or [])[:8]
        recentes_disc = [_texto_nao_vazio(item.get("disciplina")) for item in recentes]
        recentes_top = [_texto_nao_vazio(item.get("topico")) for item in recentes]
        recentes_atividade = [_texto_nao_vazio(item.get("tipo_atividade")) for item in recentes]

        consecutivas_disc = 0
        for nome in recentes_disc:
            if nome and nome == disciplina:
                consecutivas_disc += 1
            else:
                break
        if consecutivas_disc == 1:
            ajuste -= 4
            partes.append({"rotulo": "mesma disciplina na última sessão", "pontos": -4.0})
        elif consecutivas_disc >= 2:
            penalidade = min(18.0, 5.0 + 5.0 * (consecutivas_disc - 1))
            ajuste -= penalidade
            partes.append({"rotulo": "fadiga por repetição de disciplina", "pontos": -penalidade})
            motivos.append(f"rotação reduz repetição: {consecutivas_disc} sessões seguidas em {disciplina}")

        if topico and recentes:
            ultimo = recentes[0]
            ultimo_topico = _texto_nao_vazio(ultimo.get("topico"))
            if ultimo_topico == topico:
                if not bool(ultimo.get("concluida")):
                    ajuste += 7
                    partes.append({"rotulo": "continuidade de sessão interrompida", "pontos": 7.0})
                    motivos.append("há continuidade útil: a última sessão deste tópico foi interrompida")
                else:
                    ajuste -= 3
                    partes.append({"rotulo": "mesmo tópico na última sessão", "pontos": -3.0})

            repeticoes_topico = sum(1 for nome in recentes_top[:4] if nome and nome == topico)
            if repeticoes_topico >= 3:
                penalidade = 8.0 + 3.0 * (repeticoes_topico - 3)
                ajuste -= penalidade
                partes.append({"rotulo": "fadiga por repetição do tópico", "pontos": -penalidade})
                motivos.append("o mesmo tópico apareceu muitas vezes nas sessões recentes")

        repeticoes_atividade = 0
        for nome in recentes_atividade[:4]:
            if nome and nome.lower() == atividade.lower():
                repeticoes_atividade += 1
            else:
                break
        if atividade and repeticoes_atividade >= 3:
            ajuste -= 5
            partes.append({"rotulo": "variedade de atividade", "pontos": -5.0})
            motivos.append("o Vighna favoreceu variar o tipo de atividade")

        return ajuste, partes, motivos

    def _calibracao_disciplina(self, disciplina: str) -> dict:
        por_disc = self.calibracao.get("por_disciplina") or {}
        return dict(por_disc.get(_texto_nao_vazio(disciplina)) or {})

    def _calibrar_duracao(self, disciplina: str, atividade: str, questoes_alvo: int, base_minutos: int) -> tuple[int, str | None]:
        minutos = int(base_minutos)
        nota = None
        if not self.usar_calibracao:
            return minutos, nota

        dados_disc = self._calibracao_disciplina(disciplina)
        global_q = self.calibracao.get("questoes_global") or {}
        sec_por_q = None
        amostras_q = 0

        if questoes_alvo > 0:
            if int(dados_disc.get("amostras_questoes") or 0) >= 3:
                sec_por_q = float(dados_disc.get("segundos_por_questao") or 0)
                amostras_q = int(dados_disc.get("amostras_questoes") or 0)
            elif int(global_q.get("amostras") or 0) >= 5:
                sec_por_q = float(global_q.get("segundos_por_questao") or 0)
                amostras_q = int(global_q.get("amostras") or 0)

            if sec_por_q and sec_por_q > 0:
                estimado = questoes_alvo * sec_por_q / 60.0
                # A calibração personaliza sem permitir uma mudança extrema por uma amostra ruidosa.
                estimado = _limitar(estimado, max(15, base_minutos * 0.65), min(90, base_minutos * 1.65))
                minutos = _arredondar_5(estimado)
                nota = f"calibração pessoal: {amostras_q} sessão(ões), ~{sec_por_q/60.0:.1f} min por questão"
                return minutos, nota

        por_atividade = self.calibracao.get("por_atividade") or {}
        chave_atividade = _texto_nao_vazio(atividade)
        dados_atividade = por_atividade.get(chave_atividade) or {}
        if int(dados_atividade.get("amostras") or 0) >= 4:
            mediana = float(dados_atividade.get("mediana_minutos") or 0)
            if mediana > 0:
                combinada = 0.7 * base_minutos + 0.3 * mediana
                minutos = _arredondar_5(_limitar(combinada, 15, 90))
                nota = f"calibração pessoal: mediana de {mediana:.0f} min em {int(dados_atividade.get('amostras') or 0)} sessão(ões)"
        return minutos, nota

    def _ajustar_preferencia_duracao(self, minutos: int) -> tuple[int, str | None]:
        if not self.usar_historico_decisoes:
            return minutos, None
        amostras = int(self.perfil_decisoes.get("aceitas") or 0)
        preferida = self.perfil_decisoes.get("mediana_minutos_aceitos")
        if amostras < 5 or preferida in (None, 0):
            return minutos, None
        preferida = float(preferida)
        combinada = 0.8 * minutos + 0.2 * preferida
        ajustada = _arredondar_5(_limitar(combinada, 15, 90))
        if ajustada == int(minutos):
            return minutos, None
        return ajustada, f"seu histórico recente favorece sessões próximas de {int(round(preferida))} min"

    def _limitar_ao_ritmo_diario(self, minutos: int) -> tuple[int, str | None]:
        faltam = int(self.contexto.get("faltam_hoje") or 0)
        if faltam <= 0:
            return minutos, None
        faltam_min = max(1, int(round(faltam / 60.0)))
        if 15 <= faltam_min < minutos:
            return faltam_min, f"faltam cerca de {faltam_min} min para o ritmo diário de referência"
        return minutos, f"faltam cerca de {faltam_min} min para o ritmo diário de referência"

    def _finalizar_recomendacao(
        self,
        *,
        origem: str,
        selo: str,
        disciplina: str | None,
        topico_id: int | None,
        topico: str | None,
        motivos: list[str],
        score_total: float,
        score_partes: list[dict],
        atividade: str,
        minutos_base: int,
        questoes_alvo: int,
    ) -> dict:
        minutos, nota_calibracao = self._calibrar_duracao(
            disciplina or "", atividade, questoes_alvo, minutos_base
        )
        calibracao_aplicada = bool(nota_calibracao)
        if nota_calibracao:
            motivos.append(nota_calibracao)

        minutos, nota_preferencia = self._ajustar_preferencia_duracao(minutos)
        if nota_preferencia:
            motivos.append(nota_preferencia)

        minutos, nota_ritmo = self._limitar_ao_ritmo_diario(minutos)
        if nota_ritmo and nota_ritmo not in motivos:
            motivos.append(nota_ritmo)

        if questoes_alvo > 0:
            descricao = f"{atividade} • {questoes_alvo} questões • ~{minutos} min"
        else:
            descricao = f"{atividade} • ~{minutos} min"

        alternativas = [
            {"minutos": 15, "rotulo": "Revisão rápida", "atividade": "Revisão"},
            {"minutos": 25, "rotulo": "Teste de retenção", "atividade": "Teste de retenção" if questoes_alvo else "Leitura / teoria"},
            {"minutos": 50, "rotulo": "Sessão completa", "atividade": "Questões" if questoes_alvo else "Leitura / teoria"},
        ]

        return {
            "versao_motor": 4,
            "origem": origem,
            "origem_texto": f"Estudar agora V4 • {'revisão prioritária' if origem == 'revisao' else 'prioridade estratégica'}",
            "selo": selo,
            "disciplina": disciplina,
            "topico_id": topico_id,
            "topico": topico,
            "motivos": list(dict.fromkeys(motivos))[:6],
            "minutos": int(minutos),
            "atividade": atividade,
            "questoes_alvo": int(questoes_alvo),
            "descricao_sessao": descricao,
            "rotulo_sessao": "sessão adaptativa",
            "alternativas": alternativas,
            "score_total": round(float(score_total), 2),
            "score_explicado": score_partes,
            "calibracao_aplicada": calibracao_aplicada,
        }

    def montar(self) -> dict:
        adaptativas_por_topico = {
            int(item.get("topico_id")): item
            for item in self.adaptativas
            if item.get("topico_id") not in (None, "")
        }

        if self.fila:
            avaliadas = []
            for item in self.fila:
                adapt = adaptativas_por_topico.get(int(item.get("topico_id")), {}) if item.get("topico_id") not in (None, "") else {}
                questoes_disp = int(adapt.get("questoes_disponiveis") or 0)
                atividade_prevista = "Questões" if questoes_disp >= 5 else "Revisão"
                ajuste, partes_ajuste, motivos_rotacao = self._ajuste_rotacao(
                    item.get("disciplina"), item.get("topico"), atividade_prevista
                )
                base = float(item.get("score") or 0.0)
                avaliadas.append((base + ajuste, item, adapt, partes_ajuste, motivos_rotacao))

            score_total, prioridade, adaptativa, partes_ajuste, motivos_rotacao = max(
                avaliadas, key=lambda x: x[0]
            )
            score_base = float(prioridade.get("score") or 0.0)
            score_partes = [{"rotulo": "prioridade da fila de revisão", "pontos": round(score_base, 2)}] + partes_ajuste

            topico_id = int(prioridade["topico_id"])
            minutos_base = 40 if score_base >= 80 else 30 if score_base >= 60 else 25
            questoes_disponiveis = int(adaptativa.get("questoes_disponiveis") or 0)
            questoes_alvo = min(questoes_disponiveis, 20 if minutos_base >= 40 else 15 if minutos_base >= 30 else 10)
            atividade = "Questões" if questoes_alvo >= 5 else "Revisão"

            motivos: list[str] = []
            data_txt = _texto_nao_vazio(prioridade.get("proxima"))
            if data_txt:
                try:
                    data_revisao = date.fromisoformat(data_txt[:10])
                    atraso = (self.hoje - data_revisao).days
                    if atraso > 0:
                        motivos.append(f"revisão atrasada há {atraso} dia(s)")
                    elif atraso == 0:
                        motivos.append("revisão prevista para hoje")
                except Exception:
                    pass
            percentual = prioridade.get("percentual")
            if percentual is not None:
                motivos.append(f"último desempenho registrado: {float(percentual):.0f}%")
            revisoes = int(prioridade.get("revisoes") or 0)
            motivos.append(
                f"{revisoes} revisão(ões) registrada(s) • importância {int(prioridade.get('importancia', 3) or 3)}/5"
            )
            motivo_adaptativo = _texto_nao_vazio(adaptativa.get("motivo_principal"))
            if motivo_adaptativo:
                motivos.append(f"sinal adaptativo: {motivo_adaptativo}")
            motivos.extend(motivos_rotacao)

            return self._finalizar_recomendacao(
                origem="revisao",
                selo=f"PRIORIDADE {_texto_nao_vazio(prioridade.get('nivel')).upper() or 'ATUAL'}",
                disciplina=prioridade.get("disciplina"),
                topico_id=topico_id,
                topico=prioridade.get("topico"),
                motivos=motivos,
                score_total=score_total,
                score_partes=score_partes,
                atividade=atividade,
                minutos_base=minutos_base,
                questoes_alvo=questoes_alvo,
            )

        if self.adaptativas:
            avaliadas = []
            for item in self.adaptativas[:20]:
                questoes_disp = int(item.get("questoes_disponiveis") or 0)
                atividade_prevista = "Treino adaptativo" if questoes_disp else "Leitura / teoria"
                ajuste, partes_ajuste, motivos_rotacao = self._ajuste_rotacao(
                    item.get("disciplina"), item.get("topico"), atividade_prevista
                )
                base = float(item.get("score_adaptativo") or 0.0)
                avaliadas.append((base + ajuste, item, partes_ajuste, motivos_rotacao))

            score_total, prioridade, partes_ajuste, motivos_rotacao = max(avaliadas, key=lambda x: x[0])
            score_base = float(prioridade.get("score_adaptativo") or score_total)
            score_partes = [{"rotulo": "prioridade adaptativa", "pontos": round(score_base, 2)}] + partes_ajuste
            minutos_base = 40 if score_base >= 65 else 30
            questoes_disponiveis = int(prioridade.get("questoes_disponiveis") or 0)
            questoes_alvo = min(questoes_disponiveis, 20 if minutos_base >= 40 else 15)
            atividade = "Treino adaptativo" if questoes_alvo > 0 else "Leitura / teoria"

            motivos: list[str] = []
            detalhado = _texto_nao_vazio(prioridade.get("motivo_detalhado"))
            if detalhado:
                motivos.extend(parte.strip() for parte in detalhado.split("•") if parte.strip())
            if not motivos:
                motivos.append(_texto_nao_vazio(prioridade.get("motivo_principal")) or "prioridade estratégica")
            dominio = prioridade.get("dominio")
            if dominio is not None and not any("domínio" in m.lower() for m in motivos):
                motivos.append(f"Domínio V2 atual: {float(dominio):.0f}/100")
            importancia = int(prioridade.get("importancia", 3) or 3)
            if importancia >= 4:
                motivos.append(f"importância {importancia}/5 no edital")
            motivos.extend(motivos_rotacao)

            return self._finalizar_recomendacao(
                origem="adaptativa",
                selo="PRIORIDADE ESTRATÉGICA",
                disciplina=prioridade.get("disciplina"),
                topico_id=prioridade.get("topico_id"),
                topico=prioridade.get("topico"),
                motivos=motivos,
                score_total=score_total,
                score_partes=score_partes,
                atividade=atividade,
                minutos_base=minutos_base,
                questoes_alvo=questoes_alvo,
            )

        return {
            "versao_motor": 4,
            "origem": "livre",
            "origem_texto": "Estudar agora V4 • sessão livre",
            "selo": "SEM PRIORIDADE CRÍTICA",
            "disciplina": None,
            "topico_id": None,
            "topico": None,
            "motivos": [
                "não há revisão pendente nem evidência suficiente para uma prioridade estratégica",
                "uma sessão livre mantém continuidade sem inventar uma prioridade",
            ],
            "minutos": 25,
            "atividade": "Estudo livre",
            "questoes_alvo": 0,
            "descricao_sessao": "Estudo livre • ~25 min",
            "rotulo_sessao": "sessão livre",
            "alternativas": [
                {"minutos": 15, "rotulo": "Contato rápido", "atividade": "Estudo livre"},
                {"minutos": 25, "rotulo": "Estudo livre", "atividade": "Estudo livre"},
                {"minutos": 50, "rotulo": "Leitura / teoria", "atividade": "Leitura / teoria"},
            ],
            "score_total": 0.0,
            "score_explicado": [],
            "calibracao_aplicada": False,
        }


# ==========================================================
# MOTOR V5 — três eixos independentes e auditáveis
# ==========================================================

PESOS_PADRAO_V5 = {"urgencia": 45, "necessidade": 40, "momento": 15}


def normalizar_pesos_v5(pesos=None):
    base = dict(PESOS_PADRAO_V5)
    base.update({k: float(v) for k, v in dict(pesos or {}).items() if k in base})
    total = sum(max(0.0, float(v)) for v in base.values())
    if total <= 0:
        base = dict(PESOS_PADRAO_V5)
        total = 100.0
    return {k: 100.0 * max(0.0, float(v)) / total for k, v in base.items()}


class MotorRecomendacaoV5(MotorRecomendacaoV4):
    """Motor explicável em três dimensões.

    * urgência: vencimento/agenda temporal;
    * necessidade: fragilidade acadêmica e importância;
    * momento: rotação, fadiga, continuidade e ritmo.

    Revisões vencidas/para hoje podem formar uma faixa protegida. Nesse modo,
    o peso acadêmico e de momento escolhe *qual* revisão fazer primeiro, mas
    uma prioridade flexível não ultrapassa silenciosamente uma obrigação já
    vencida.
    """

    def __init__(self, *args, pesos=None, proteger_revisoes_vencidas=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.pesos_v5 = normalizar_pesos_v5(pesos)
        self.proteger_revisoes_vencidas = bool(proteger_revisoes_vencidas)

    def _urgencia_temporal(self, item, origem):
        proxima = _texto_nao_vazio(item.get("proxima") or item.get("proxima_revisao"))
        if proxima:
            try:
                alvo = date.fromisoformat(proxima[:10])
                dias = (self.hoje - alvo).days
                if dias > 0:
                    return min(100.0, 90.0 + min(10.0, dias * 1.2)), dias, f"revisão atrasada há {dias} dia(s)"
                if dias == 0:
                    return 88.0, 0, "revisão prevista para hoje"
                faltam = abs(dias)
                return max(18.0, 72.0 - faltam * 8.0), -faltam, f"revisão prevista em {faltam} dia(s)"
            except Exception:
                pass
        if origem == "revisao":
            return 72.0, None, "revisão na fila atual"
        try:
            urg = float(item.get("urgencia") or (item.get("componentes") or {}).get("urgencia") or 0.0)
        except Exception:
            urg = 0.0
        return _limitar(urg, 0.0, 100.0), None, _texto_nao_vazio(item.get("motivo_urgencia")) or "urgência adaptativa"

    def _necessidade_academica(self, item, adapt=None):
        base = dict(adapt or item or {})
        comp = dict(base.get("componentes") or {})
        if comp:
            # Exclui urgência do cálculo acadêmico; ela já possui eixo próprio.
            pesos = {
                "dominio": 26.0,
                "erros": 22.0,
                "evidencia": 13.0,
                "variedade": 8.0,
                "estabilidade": 8.0,
                "recencia": 10.0,
                "importancia": 13.0,
            }
            valor = sum(float(comp.get(k) or 0.0) * w / 100.0 for k, w in pesos.items())
            detalhes = []
            for k, rot in (("dominio","domínio"),("erros","erros"),("evidencia","evidência"),("importancia","importância")):
                if float(comp.get(k) or 0.0) >= 65:
                    detalhes.append(rot)
            return _limitar(valor, 0.0, 100.0), detalhes

        percentual = item.get("percentual")
        fragilidade = 50.0 if percentual is None else _limitar(100.0 - float(percentual), 0.0, 100.0)
        importancia = max(1, min(5, int(item.get("importancia", 3) or 3)))
        imp = (importancia - 1) / 4.0 * 100.0
        revisoes = int(item.get("revisoes") or item.get("revisoes_totais") or 0)
        evidencia = max(25.0, 70.0 - min(45.0, revisoes * 8.0))
        valor = 0.55 * fragilidade + 0.30 * imp + 0.15 * evidencia
        return _limitar(valor, 0.0, 100.0), ["desempenho", "importância"]

    def _adequacao_momento(self, item, adapt=None):
        base = dict(adapt or item or {})
        questoes = int(base.get("questoes_disponiveis") or 0)
        atividade = "Questões" if questoes >= 5 else ("Revisão" if item.get("origem_candidato") == "revisao" else "Leitura / teoria")
        ajuste, partes, motivos = self._ajuste_rotacao(
            item.get("disciplina") or base.get("disciplina"),
            item.get("topico") or base.get("topico"),
            atividade,
        )
        # 60 é neutro: ajustes positivos/negativos ficam legíveis sem dominar o score.
        valor = _limitar(60.0 + ajuste * 2.2, 0.0, 100.0)
        faltam = int(self.contexto.get("faltam_hoje") or 0)
        if 0 < faltam <= 20 * 60:
            valor = min(100.0, valor + 6.0)
            partes.append({"rotulo": "encaixe no tempo restante", "pontos": 6.0})
        return valor, partes, motivos

    def analisar_candidatos(self):
        adapt_por_topico = {
            int(x.get("topico_id")): x for x in self.adaptativas
            if x.get("topico_id") not in (None, "")
        }
        candidatos = []
        vistos = set()

        def adicionar(item, origem):
            item = dict(item or {})
            tid = item.get("topico_id")
            try:
                tid = int(tid) if tid not in (None, "") else None
            except Exception:
                tid = None
            chave = (tid, origem)
            if chave in vistos:
                return
            vistos.add(chave)
            adapt = adapt_por_topico.get(tid, {}) if tid is not None else {}
            urg, dias_atraso, motivo_urg = self._urgencia_temporal(item if origem == "revisao" else adapt, origem)
            nec, sinais = self._necessidade_academica(item, adapt)
            mom, partes_momento, motivos_momento = self._adequacao_momento({**item, "origem_candidato": origem}, adapt)
            p = self.pesos_v5
            score = urg*p["urgencia"]/100.0 + nec*p["necessidade"]/100.0 + mom*p["momento"]/100.0
            protegido = bool(origem == "revisao" and dias_atraso is not None and dias_atraso >= 0)
            candidatos.append({
                "origem_candidato": origem,
                "disciplina": item.get("disciplina") or adapt.get("disciplina"),
                "topico_id": tid,
                "topico": item.get("topico") or adapt.get("topico"),
                "item_fila": item if origem == "revisao" else None,
                "item_adaptativo": adapt or (item if origem == "adaptativa" else {}),
                "urgencia": round(urg, 1),
                "necessidade": round(nec, 1),
                "momento": round(mom, 1),
                "score_total": round(score, 2),
                "dias_atraso": dias_atraso,
                "faixa_temporal_protegida": protegido,
                "motivo_urgencia": motivo_urg,
                "sinais_academicos": sinais,
                "partes_momento": partes_momento,
                "motivos_momento": motivos_momento,
            })

        for item in self.fila:
            adicionar(item, "revisao")
        fila_ids = {int(x.get("topico_id")) for x in self.fila if x.get("topico_id") not in (None, "")}
        for item in self.adaptativas[:30]:
            # Um tópico já presente na fila fica representado pela versão temporal.
            if item.get("topico_id") not in (None, "") and int(item.get("topico_id")) in fila_ids:
                continue
            adicionar(item, "adaptativa")

        candidatos.sort(key=lambda x: (-x["score_total"], -x["urgencia"], -x["necessidade"], str(x.get("disciplina") or "").lower()))
        for pos, c in enumerate(candidatos, 1):
            c["posicao_global"] = pos
        return candidatos

    def _finalizar_v5(self, candidato, ranking):
        origem = candidato["origem_candidato"]
        fila = dict(candidato.get("item_fila") or {})
        adapt = dict(candidato.get("item_adaptativo") or {})
        disciplina = candidato.get("disciplina")
        topico = candidato.get("topico")
        tid = candidato.get("topico_id")
        questoes_disp = int(adapt.get("questoes_disponiveis") or 0)
        score = float(candidato["score_total"])
        minutos_base = 40 if score >= 78 else 30 if score >= 58 else 25
        questoes_alvo = min(questoes_disp, 20 if minutos_base >= 40 else 15 if minutos_base >= 30 else 10)
        atividade = "Questões" if origem == "revisao" and questoes_alvo >= 5 else ("Revisão" if origem == "revisao" else ("Treino adaptativo" if questoes_alvo else "Leitura / teoria"))
        motivos = [candidato.get("motivo_urgencia")]
        if candidato.get("sinais_academicos"):
            motivos.append("necessidade acadêmica: " + ", ".join(candidato["sinais_academicos"][:4]))
        motivos.extend(candidato.get("motivos_momento") or [])
        if origem == "revisao":
            perc = fila.get("percentual")
            if perc is not None:
                motivos.append(f"último desempenho registrado: {float(perc):.0f}%")
        else:
            detalhado = _texto_nao_vazio(adapt.get("motivo_detalhado"))
            if detalhado:
                motivos.extend([x.strip() for x in detalhado.split("•") if x.strip()][:2])

        score_partes = [
            {"rotulo": f"urgência ({self.pesos_v5['urgencia']:.0f}%)", "pontos": round(candidato['urgencia']*self.pesos_v5['urgencia']/100.0, 2)},
            {"rotulo": f"necessidade ({self.pesos_v5['necessidade']:.0f}%)", "pontos": round(candidato['necessidade']*self.pesos_v5['necessidade']/100.0, 2)},
            {"rotulo": f"momento ({self.pesos_v5['momento']:.0f}%)", "pontos": round(candidato['momento']*self.pesos_v5['momento']/100.0, 2)},
        ]
        base = self._finalizar_recomendacao(
            origem=origem,
            selo=(f"PRIORIDADE {_texto_nao_vazio(fila.get('nivel')).upper() or 'TEMPORAL'}" if origem == "revisao" else "PRIORIDADE ESTRATÉGICA"),
            disciplina=disciplina,
            topico_id=tid,
            topico=topico,
            motivos=[m for m in motivos if m],
            score_total=score,
            score_partes=score_partes,
            atividade=atividade,
            minutos_base=minutos_base,
            questoes_alvo=questoes_alvo,
        )
        base.update({
            "versao_motor": 5,
            "origem_texto": f"Estudar agora V5 • {'revisão prioritária' if origem == 'revisao' else 'prioridade estratégica'}",
            "eixos_v5": {"urgencia": candidato["urgencia"], "necessidade": candidato["necessidade"], "momento": candidato["momento"]},
            "pesos_v5": {k: round(v, 1) for k, v in self.pesos_v5.items()},
            "faixa_temporal_protegida": bool(candidato.get("faixa_temporal_protegida")),
            "dias_atraso": candidato.get("dias_atraso"),
            "ranking_resumo": [{k: c.get(k) for k in ("posicao_global","disciplina","topico_id","topico","urgencia","necessidade","momento","score_total","faixa_temporal_protegida","origem_candidato")} for c in ranking[:8]],
        })
        if self.proteger_revisoes_vencidas and any(c.get("faixa_temporal_protegida") for c in ranking):
            base["criterio_selecao_v5"] = "Há revisão vencida ou prevista para hoje; o Vighna protegeu essa faixa temporal e usou necessidade/momento para ordenar dentro dela."
        else:
            base["criterio_selecao_v5"] = "Seleção pelo equilíbrio entre urgência, necessidade acadêmica e adequação ao momento."
        return base

    def montar(self):
        ranking = self.analisar_candidatos()
        if not ranking:
            livre = super().montar()
            livre.update({
                "versao_motor": 5,
                "origem_texto": "Estudar agora V5 • sessão livre",
                "eixos_v5": {"urgencia": 0.0, "necessidade": 0.0, "momento": 50.0},
                "pesos_v5": {k: round(v, 1) for k, v in self.pesos_v5.items()},
                "faixa_temporal_protegida": False,
                "ranking_resumo": [],
                "criterio_selecao_v5": "Sem evidência suficiente para prioridade contextual.",
            })
            return livre
        protegidos = [c for c in ranking if c.get("faixa_temporal_protegida")]
        elegiveis = protegidos if (self.proteger_revisoes_vencidas and protegidos) else ranking
        escolhido = max(elegiveis, key=lambda c: (c["score_total"], c["necessidade"], c["momento"]))
        return self._finalizar_v5(escolhido, ranking)
