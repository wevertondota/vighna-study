"""Infraestrutura de microtemas, versionamento e refinamento do VighnaStudy.

A unidade persistente de aprendizado é o microtema. Questões e alternativas são
instrumentos mutáveis que podem ser reformulados, arquivados ou excluídos sem
apagar a evidência histórica do estudante.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from difflib import SequenceMatcher
import hashlib
import json
import math
import re
import unicodedata
from pathlib import Path
from typing import Iterable

CATALOGO_ARQUIVO = "microtemas_crimes_pessoa.json"
TOPICO_CRIMES_PESSOA_ID = 22
LIMIAR_REFINAMENTO_PADRAO = 90.0
VERSAO_MOTOR_MICROTEMAS = "microtemas_v1"
VERSAO_REFINAMENTO = "refino_microtemas_v1"


def _agora_sql() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _texto(valor) -> str:
    return str(valor or "").strip()


def _normalizar(valor: str) -> str:
    txt = unicodedata.normalize("NFKD", _texto(valor))
    txt = "".join(c for c in txt if not unicodedata.combining(c)).lower()
    txt = re.sub(r"[^a-z0-9]+", " ", txt)
    return re.sub(r"\s+", " ", txt).strip()


def _familia(nome: str) -> str:
    nome = _texto(nome)
    if " — " in nome:
        return nome.split(" — ", 1)[0].strip()
    if ":" in nome:
        return nome.split(":", 1)[0].strip()
    return nome


def _fingerprint(enunciado: str, alternativas: Iterable[dict], gabarito: str | None, tipo: str = "") -> str:
    payload = {
        "enunciado": _texto(enunciado),
        "alternativas": [
            {
                "letra": _texto(item.get("letra")).upper(),
                "texto": _texto(item.get("texto")),
                "correta": bool(item.get("correta")),
                "ordem": int(item.get("ordem") or 0),
            }
            for item in alternativas
        ],
        "gabarito": _texto(gabarito).upper(),
        "tipo": _texto(tipo),
    }
    bruto = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(bruto.encode("utf-8")).hexdigest()


def garantir_schema(conexao) -> None:
    conexao.executescript(
        """
        CREATE TABLE IF NOT EXISTS microtemas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chave_estavel TEXT NOT NULL UNIQUE,
            disciplina_id INTEGER NOT NULL,
            topico_id INTEGER NOT NULL,
            capitulo_id INTEGER,
            familia TEXT,
            nome TEXT NOT NULL,
            descricao TEXT,
            tipo TEXT NOT NULL DEFAULT 'regra_normativa',
            status TEXT NOT NULL DEFAULT 'ativo',
            ordem INTEGER NOT NULL DEFAULT 0,
            criado_em TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            atualizado_em TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (disciplina_id) REFERENCES disciplinas(id) ON DELETE CASCADE,
            FOREIGN KEY (topico_id) REFERENCES topicos(id) ON DELETE CASCADE,
            FOREIGN KEY (capitulo_id) REFERENCES capitulos_topico(id) ON DELETE SET NULL
        );

        CREATE INDEX IF NOT EXISTS idx_microtemas_topico
            ON microtemas(topico_id, status, ordem);
        CREATE INDEX IF NOT EXISTS idx_microtemas_capitulo
            ON microtemas(capitulo_id, status, ordem);
        CREATE INDEX IF NOT EXISTS idx_microtemas_familia
            ON microtemas(topico_id, familia);

        CREATE TABLE IF NOT EXISTS questao_versoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            questao_id INTEGER,
            versao INTEGER NOT NULL,
            fingerprint TEXT NOT NULL,
            topico_id_snapshot INTEGER,
            capitulo_id_snapshot INTEGER,
            enunciado_snapshot TEXT NOT NULL,
            alternativas_snapshot TEXT NOT NULL,
            gabarito_snapshot TEXT,
            explicacao_snapshot TEXT,
            tipo_questao_snapshot TEXT,
            motivo TEXT,
            atual INTEGER NOT NULL DEFAULT 1,
            criado_em TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            UNIQUE (questao_id, versao),
            FOREIGN KEY (questao_id) REFERENCES questoes(id) ON DELETE SET NULL
        );

        CREATE INDEX IF NOT EXISTS idx_questao_versoes_atual
            ON questao_versoes(questao_id, atual);
        CREATE INDEX IF NOT EXISTS idx_questao_versoes_fingerprint
            ON questao_versoes(fingerprint);

        CREATE TABLE IF NOT EXISTS alternativa_microtemas (
            questao_id INTEGER NOT NULL,
            letra TEXT NOT NULL,
            microtema_id INTEGER NOT NULL,
            confianca REAL NOT NULL DEFAULT 1.0,
            origem TEXT NOT NULL DEFAULT 'manual',
            requer_revisao INTEGER NOT NULL DEFAULT 0,
            atualizado_em TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            PRIMARY KEY (questao_id, letra, microtema_id),
            FOREIGN KEY (questao_id) REFERENCES questoes(id) ON DELETE CASCADE,
            FOREIGN KEY (microtema_id) REFERENCES microtemas(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_alt_microtema_microtema
            ON alternativa_microtemas(microtema_id, questao_id);

        CREATE TABLE IF NOT EXISTS questao_microtemas (
            questao_id INTEGER NOT NULL,
            microtema_id INTEGER NOT NULL,
            papel TEXT NOT NULL DEFAULT 'cobertura',
            confianca REAL NOT NULL DEFAULT 1.0,
            origem TEXT NOT NULL DEFAULT 'derivado_alternativas',
            requer_revisao INTEGER NOT NULL DEFAULT 0,
            atualizado_em TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            PRIMARY KEY (questao_id, microtema_id),
            FOREIGN KEY (questao_id) REFERENCES questoes(id) ON DELETE CASCADE,
            FOREIGN KEY (microtema_id) REFERENCES microtemas(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_questao_microtemas_microtema
            ON questao_microtemas(microtema_id, questao_id);

        CREATE TABLE IF NOT EXISTS questao_versao_microtemas (
            versao_id INTEGER NOT NULL,
            letra TEXT NOT NULL,
            microtema_id INTEGER NOT NULL,
            papel TEXT NOT NULL DEFAULT 'alternativa',
            confianca REAL NOT NULL DEFAULT 1.0,
            PRIMARY KEY (versao_id, letra, microtema_id),
            FOREIGN KEY (versao_id) REFERENCES questao_versoes(id) ON DELETE CASCADE,
            FOREIGN KEY (microtema_id) REFERENCES microtemas(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS microtema_mapeamento_pendencias (
            questao_id INTEGER NOT NULL,
            letra TEXT NOT NULL,
            motivo TEXT NOT NULL,
            criado_em TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            resolvida INTEGER NOT NULL DEFAULT 0,
            resolvida_em TEXT,
            PRIMARY KEY (questao_id, letra),
            FOREIGN KEY (questao_id) REFERENCES questoes(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS tentativa_microtemas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tentativa_id INTEGER NOT NULL,
            microtema_id INTEGER NOT NULL,
            questao_versao_id INTEGER,
            letra_relacionada TEXT,
            tipo_sinal TEXT NOT NULL,
            valor REAL NOT NULL,
            peso REAL NOT NULL DEFAULT 1.0,
            criado_em TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            UNIQUE (tentativa_id, microtema_id, letra_relacionada, tipo_sinal),
            FOREIGN KEY (tentativa_id) REFERENCES tentativas_questoes(id) ON DELETE CASCADE,
            FOREIGN KEY (microtema_id) REFERENCES microtemas(id) ON DELETE CASCADE,
            FOREIGN KEY (questao_versao_id) REFERENCES questao_versoes(id) ON DELETE SET NULL
        );

        CREATE INDEX IF NOT EXISTS idx_tentativa_microtemas_microtema
            ON tentativa_microtemas(microtema_id, tentativa_id);

        CREATE TABLE IF NOT EXISTS microtema_estado (
            concurso_id INTEGER NOT NULL,
            microtema_id INTEGER NOT NULL,
            evidencias INTEGER NOT NULL DEFAULT 0,
            peso_positivo REAL NOT NULL DEFAULT 0,
            peso_negativo REAL NOT NULL DEFAULT 0,
            dominio_atual REAL,
            fragilidade REAL NOT NULL DEFAULT 0,
            confianca REAL NOT NULL DEFAULT 0,
            ultima_evidencia TEXT,
            ultimo_erro TEXT,
            proxima_revisao TEXT,
            estado TEXT NOT NULL DEFAULT 'sem_evidencia',
            atualizado_em TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            PRIMARY KEY (concurso_id, microtema_id),
            FOREIGN KEY (concurso_id) REFERENCES concursos(id) ON DELETE CASCADE,
            FOREIGN KEY (microtema_id) REFERENCES microtemas(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_microtema_estado_refino
            ON microtema_estado(concurso_id, fragilidade DESC, proxima_revisao);
        """
    )


def _carregar_catalogo(base_dir: Path | None = None) -> dict | None:
    raiz = Path(base_dir or Path(__file__).resolve().parent)
    caminho = raiz / CATALOGO_ARQUIVO
    if not caminho.is_file():
        return None
    return json.loads(caminho.read_text(encoding="utf-8"))


def _resolver_disciplina_topico(conexao):
    linha = conexao.execute(
        """
        SELECT t.id, d.id
        FROM topicos t
        JOIN disciplinas d ON d.id = t.disciplina_id
        WHERE lower(d.nome) = lower('Direito Penal')
          AND (
            t.id = ?
            OR lower(t.nome) LIKE '%crimes contra a pessoa%'
          )
        ORDER BY CASE WHEN t.id = ? THEN 0 ELSE 1 END
        LIMIT 1
        """,
        (TOPICO_CRIMES_PESSOA_ID, TOPICO_CRIMES_PESSOA_ID),
    ).fetchone()
    if linha is None:
        return None, None
    return int(linha[1]), int(linha[0])


def sincronizar_questao_microtemas(conexao, questao_id: int) -> None:
    questao_id = int(questao_id)
    conexao.execute("DELETE FROM questao_microtemas WHERE questao_id = ?", (questao_id,))
    conexao.execute(
        """
        INSERT INTO questao_microtemas (
            questao_id, microtema_id, papel, confianca, origem, requer_revisao, atualizado_em
        )
        SELECT
            questao_id,
            microtema_id,
            'cobertura',
            MAX(confianca),
            'derivado_alternativas',
            MAX(requer_revisao),
            datetime('now','localtime')
        FROM alternativa_microtemas
        WHERE questao_id = ?
        GROUP BY questao_id, microtema_id
        """,
        (questao_id,),
    )


def _snapshot_questao(conexao, questao_id: int):
    q = conexao.execute(
        """
        SELECT id, topico_id, capitulo_id, enunciado, explicacao, tipo_questao
        FROM questoes WHERE id = ?
        """,
        (int(questao_id),),
    ).fetchone()
    if q is None:
        return None
    alts_linhas = conexao.execute(
        """
        SELECT letra, texto, correta, ordem
        FROM alternativas_questoes WHERE questao_id = ?
        ORDER BY ordem, letra
        """,
        (int(questao_id),),
    ).fetchall()
    alternativas = [
        {"letra": str(a[0]).upper(), "texto": a[1], "correta": bool(a[2]), "ordem": int(a[3])}
        for a in alts_linhas
    ]
    gabarito = next((a["letra"] for a in alternativas if a["correta"]), None)
    fp = _fingerprint(q[3], alternativas, gabarito, q[5] or "")
    return {
        "questao_id": int(q[0]),
        "topico_id": int(q[1]) if q[1] is not None else None,
        "capitulo_id": int(q[2]) if q[2] is not None else None,
        "enunciado": q[3] or "",
        "explicacao": q[4] or "",
        "tipo_questao": q[5] or "MULTIPLA_ESCOLHA",
        "alternativas": alternativas,
        "gabarito": gabarito,
        "fingerprint": fp,
    }


def garantir_versao_atual(conexao, questao_id: int, motivo: str = "sincronizacao") -> int | None:
    snapshot = _snapshot_questao(conexao, questao_id)
    if snapshot is None:
        return None
    atual = conexao.execute(
        """
        SELECT id, versao, fingerprint
        FROM questao_versoes
        WHERE questao_id = ? AND atual = 1
        ORDER BY versao DESC LIMIT 1
        """,
        (int(questao_id),),
    ).fetchone()
    if atual is not None and str(atual[2]) == snapshot["fingerprint"]:
        return int(atual[0])

    if atual is not None:
        conexao.execute("UPDATE questao_versoes SET atual = 0 WHERE questao_id = ?", (int(questao_id),))
        # Pode haver versões históricas criadas a partir dos snapshots de
        # tentativas com número maior que a versão atualmente ativa. Nunca
        # reutilize esses números ao criar a próxima versão corrente.
        maxv = conexao.execute(
            "SELECT COALESCE(MAX(versao), 0) FROM questao_versoes WHERE questao_id = ?",
            (int(questao_id),),
        ).fetchone()[0]
        versao = int(maxv or 0) + 1
    else:
        maxv = conexao.execute(
            "SELECT COALESCE(MAX(versao), 0) FROM questao_versoes WHERE questao_id = ?",
            (int(questao_id),),
        ).fetchone()[0]
        versao = int(maxv or 0) + 1

    cur = conexao.execute(
        """
        INSERT INTO questao_versoes (
            questao_id, versao, fingerprint, topico_id_snapshot, capitulo_id_snapshot,
            enunciado_snapshot, alternativas_snapshot, gabarito_snapshot,
            explicacao_snapshot, tipo_questao_snapshot, motivo, atual
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            int(questao_id), versao, snapshot["fingerprint"], snapshot["topico_id"],
            snapshot["capitulo_id"], snapshot["enunciado"],
            json.dumps(snapshot["alternativas"], ensure_ascii=False), snapshot["gabarito"],
            snapshot["explicacao"], snapshot["tipo_questao"], _texto(motivo) or "sincronizacao",
        ),
    )
    versao_id = int(cur.lastrowid)
    conexao.execute("DELETE FROM questao_versao_microtemas WHERE versao_id = ?", (versao_id,))
    conexao.execute(
        """
        INSERT OR IGNORE INTO questao_versao_microtemas (
            versao_id, letra, microtema_id, papel, confianca
        )
        SELECT ?, letra, microtema_id, 'alternativa', confianca
        FROM alternativa_microtemas WHERE questao_id = ?
        """,
        (versao_id, int(questao_id)),
    )
    return versao_id


def registrar_questao_nova(conexao, questao_id: int, motivo: str = "criacao") -> dict:
    """Versiona a nova questão e sinaliza mapeamento apenas em tópicos taxonomizados."""
    snapshot = _snapshot_questao(conexao, questao_id)
    if snapshot is None:
        return {"versao_id": None, "pendentes": 0}
    versao_id = garantir_versao_atual(conexao, questao_id, motivo=motivo)
    existe_taxonomia = conexao.execute(
        "SELECT 1 FROM microtemas WHERE topico_id=? AND status='ativo' LIMIT 1",
        (int(snapshot["topico_id"]),),
    ).fetchone()
    pendentes = 0
    if existe_taxonomia is not None:
        for alt in snapshot["alternativas"]:
            conexao.execute(
                """
                INSERT OR IGNORE INTO microtema_mapeamento_pendencias
                    (questao_id, letra, motivo, resolvida)
                VALUES (?, ?, 'questao_nova_sem_microtema', 0)
                """,
                (int(questao_id), alt["letra"]),
            )
            pendentes += 1
    return {"versao_id": versao_id, "pendentes": pendentes}


def capturar_estado_pre_edicao(conexao, questao_id: int) -> dict | None:
    snapshot = _snapshot_questao(conexao, questao_id)
    if snapshot is None:
        return None
    versao_id = garantir_versao_atual(conexao, questao_id, motivo="pre_edicao")
    mapeamentos = conexao.execute(
        """
        SELECT letra, microtema_id, confianca, origem
        FROM alternativa_microtemas WHERE questao_id = ?
        ORDER BY letra, microtema_id
        """,
        (int(questao_id),),
    ).fetchall()
    por_letra = {}
    for letra, mid, conf, origem in mapeamentos:
        por_letra.setdefault(str(letra).upper(), []).append(
            {"microtema_id": int(mid), "confianca": float(conf or 1.0), "origem": origem or "legado"}
        )
    textos = {a["letra"]: a["texto"] for a in snapshot["alternativas"]}
    return {"snapshot": snapshot, "versao_id": versao_id, "mapeamentos": por_letra, "textos": textos}


def finalizar_edicao_questao(conexao, questao_id: int, estado_anterior: dict | None, motivo: str = "edicao") -> dict:
    questao_id = int(questao_id)
    novo = _snapshot_questao(conexao, questao_id)
    if novo is None:
        return {"preservados": 0, "pendentes": 0, "versao_id": None}

    antigos = (estado_anterior or {}).get("mapeamentos", {})
    textos_antigos = (estado_anterior or {}).get("textos", {})
    snapshot_antigo = (estado_anterior or {}).get("snapshot") or {}
    novos_textos = {a["letra"]: a["texto"] for a in novo["alternativas"]}
    mesmo_topico = snapshot_antigo.get("topico_id") == novo.get("topico_id")
    novo_topico_taxonomizado = conexao.execute(
        "SELECT 1 FROM microtemas WHERE topico_id=? AND status='ativo' LIMIT 1",
        (int(novo["topico_id"]),),
    ).fetchone() is not None

    conexao.execute("DELETE FROM alternativa_microtemas WHERE questao_id = ?", (questao_id,))
    conexao.execute("DELETE FROM microtema_mapeamento_pendencias WHERE questao_id = ?", (questao_id,))
    preservados = 0
    pendentes = 0

    for letra, texto_novo in novos_textos.items():
        refs = antigos.get(letra) or []
        texto_antigo = textos_antigos.get(letra)
        if mesmo_topico and refs and texto_antigo is not None:
            similaridade = SequenceMatcher(None, _normalizar(texto_antigo), _normalizar(texto_novo)).ratio()
            if similaridade >= 0.72:
                for ref in refs:
                    conexao.execute(
                        """
                        INSERT OR IGNORE INTO alternativa_microtemas (
                            questao_id, letra, microtema_id, confianca, origem, requer_revisao
                        ) VALUES (?, ?, ?, ?, ?, 0)
                        """,
                        (
                            questao_id, letra, ref["microtema_id"],
                            min(float(ref.get("confianca", 1.0)), 0.98), "preservado_edicao",
                        ),
                    )
                    preservados += 1
                continue
        if novo_topico_taxonomizado:
            motivo_pendencia = (
                "questao_reclassificada_sem_correspondencia_segura"
                if not mesmo_topico
                else "conteudo_alterado_sem_correspondencia_segura"
            )
            conexao.execute(
                """
                INSERT OR REPLACE INTO microtema_mapeamento_pendencias (
                    questao_id, letra, motivo, criado_em, resolvida, resolvida_em
                ) VALUES (?, ?, ?, datetime('now','localtime'), 0, NULL)
                """,
                (questao_id, letra, motivo_pendencia),
            )
            pendentes += 1

    sincronizar_questao_microtemas(conexao, questao_id)
    versao_id = garantir_versao_atual(conexao, questao_id, motivo=motivo)
    # garantir_versao_atual já copia o novo mapeamento para a versão criada.
    return {"preservados": preservados, "pendentes": pendentes, "versao_id": versao_id}


def aplicar_catalogo_crimes_pessoa(conexao, base_dir: Path | None = None) -> dict:
    garantir_schema(conexao)
    catalogo = _carregar_catalogo(base_dir)
    if not catalogo:
        return {"aplicado": False, "motivo": "catalogo_ausente"}

    disciplina_id, topico_id = _resolver_disciplina_topico(conexao)
    if not disciplina_id or not topico_id:
        return {"aplicado": False, "motivo": "topico_ausente"}

    micro_ids = {}
    inseridos = atualizados = 0
    for item in catalogo.get("catalog", []):
        capitulo_id = item.get("capitulo_id")
        if capitulo_id is not None:
            existe_cap = conexao.execute(
                "SELECT 1 FROM capitulos_topico WHERE id = ? AND topico_id = ?",
                (int(capitulo_id), int(topico_id)),
            ).fetchone()
            if existe_cap is None:
                capitulo_id = None
        existente = conexao.execute(
            "SELECT id FROM microtemas WHERE chave_estavel = ?", (item["key"],)
        ).fetchone()
        if existente is None:
            cur = conexao.execute(
                """
                INSERT INTO microtemas (
                    chave_estavel, disciplina_id, topico_id, capitulo_id, familia,
                    nome, descricao, tipo, status, ordem
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["key"], disciplina_id, topico_id, capitulo_id,
                    _familia(item.get("nome")), item.get("nome"), item.get("descricao"),
                    item.get("tipo") or "regra_normativa", item.get("status") or "ativo",
                    int(item.get("ordem") or 0),
                ),
            )
            mid = int(cur.lastrowid); inseridos += 1
        else:
            mid = int(existente[0])
            conexao.execute(
                """
                UPDATE microtemas SET disciplina_id=?, topico_id=?, capitulo_id=?, familia=?,
                    nome=?, descricao=?, tipo=?, status=?, ordem=?,
                    atualizado_em=datetime('now','localtime') WHERE id=?
                """,
                (
                    disciplina_id, topico_id, capitulo_id, _familia(item.get("nome")),
                    item.get("nome"), item.get("descricao"), item.get("tipo") or "regra_normativa",
                    item.get("status") or "ativo", int(item.get("ordem") or 0), mid,
                ),
            )
            atualizados += 1
        micro_ids[item["key"]] = mid

    mapeados = 0
    questoes_afetadas = set()
    for ref in catalogo.get("mapping", []):
        qid = int(ref["question_id"])
        existe = conexao.execute(
            "SELECT 1 FROM questoes WHERE id=? AND topico_id=?", (qid, topico_id)
        ).fetchone()
        if existe is None:
            continue
        mid = micro_ids.get(ref["microtheme_key"])
        if not mid:
            continue
        letra = str(ref["letter"]).upper()
        conexao.execute(
            """
            INSERT OR REPLACE INTO alternativa_microtemas (
                questao_id, letra, microtema_id, confianca, origem, requer_revisao, atualizado_em
            ) VALUES (?, ?, ?, 1.0, 'auditoria_final_2026_09', 0, datetime('now','localtime'))
            """,
            (qid, letra, mid),
        )
        conexao.execute(
            "DELETE FROM microtema_mapeamento_pendencias WHERE questao_id=? AND letra=?",
            (qid, letra),
        )
        mapeados += 1
        questoes_afetadas.add(qid)

    for qid in sorted(questoes_afetadas):
        sincronizar_questao_microtemas(conexao, qid)
        garantir_versao_atual(conexao, qid, motivo="catalogo_piloto_crimes_pessoa")

    return {
        "aplicado": True,
        "microtemas_inseridos": inseridos,
        "microtemas_atualizados": atualizados,
        "alternativas_mapeadas": mapeados,
        "questoes_mapeadas": len(questoes_afetadas),
        "topico_id": topico_id,
    }


def _versao_atual_id(conexao, questao_id: int) -> int | None:
    row = conexao.execute(
        "SELECT id FROM questao_versoes WHERE questao_id=? AND atual=1 ORDER BY versao DESC LIMIT 1",
        (int(questao_id),),
    ).fetchone()
    if row is not None:
        return int(row[0])
    return garantir_versao_atual(conexao, questao_id, motivo="tentativa")


def _versao_snapshot_tentativa(conexao, tentativa_id: int, questao_id: int) -> int | None:
    """Resolve a versão realmente respondida usando o snapshot da tentativa.

    Tentativas antigas podem ter sido feitas antes de uma reformulação textual.
    Nesses casos criamos uma versão histórica (atual=0) com o texto congelado na
    própria tentativa, em vez de atribuir retroativamente a evidência à redação
    atual da questão.
    """
    row = conexao.execute(
        """
        SELECT tq.enunciado_snapshot, tq.alternativas_snapshot, tq.gabarito_snapshot,
               tq.explicacao_snapshot, tq.topico_id_snapshot,
               q.capitulo_id, q.tipo_questao
        FROM tentativas_questoes tq
        LEFT JOIN questoes q ON q.id = tq.questao_id
        WHERE tq.id = ?
        """,
        (int(tentativa_id),),
    ).fetchone()
    if row is None or not row[0] or not row[1]:
        return _versao_atual_id(conexao, questao_id)

    try:
        alternativas = json.loads(row[1]) if isinstance(row[1], str) else row[1]
    except Exception:
        return _versao_atual_id(conexao, questao_id)
    if not isinstance(alternativas, list):
        return _versao_atual_id(conexao, questao_id)

    tipo = row[6] or "MULTIPLA_ESCOLHA"
    fp = _fingerprint(row[0] or "", alternativas, row[2], tipo)
    existente = conexao.execute(
        "SELECT id FROM questao_versoes WHERE questao_id=? AND fingerprint=? LIMIT 1",
        (int(questao_id), fp),
    ).fetchone()
    if existente is not None:
        return int(existente[0])

    # Garante que exista uma versão atual antes de inserir uma versão histórica.
    atual_id = _versao_atual_id(conexao, questao_id)
    maxv = conexao.execute(
        "SELECT COALESCE(MAX(versao), 0) FROM questao_versoes WHERE questao_id=?",
        (int(questao_id),),
    ).fetchone()[0]
    cur = conexao.execute(
        """
        INSERT INTO questao_versoes (
            questao_id, versao, fingerprint, topico_id_snapshot, capitulo_id_snapshot,
            enunciado_snapshot, alternativas_snapshot, gabarito_snapshot,
            explicacao_snapshot, tipo_questao_snapshot, motivo, atual
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'snapshot_tentativa_historica', 0)
        """,
        (
            int(questao_id), int(maxv or 0) + 1, fp,
            int(row[4]) if row[4] is not None else None,
            int(row[5]) if row[5] is not None else None,
            row[0] or "", json.dumps(alternativas, ensure_ascii=False),
            _texto(row[2]).upper() or None, row[3] or "", tipo,
        ),
    )
    versao_id = int(cur.lastrowid)

    # No piloto, as reformas anteriores foram textuais/referenciais e mantiveram
    # a semântica de cada letra. Copiar o mapeamento atual para a versão histórica
    # é, portanto, a associação mais fiel disponível para o backfill inicial.
    conexao.execute(
        """
        INSERT OR IGNORE INTO questao_versao_microtemas
            (versao_id, letra, microtema_id, papel, confianca)
        SELECT ?, letra, microtema_id, 'alternativa', confianca
        FROM alternativa_microtemas
        WHERE questao_id=?
        """,
        (versao_id, int(questao_id)),
    )
    # Por segurança, não permita que a inserção histórica altere a versão atual.
    if atual_id is not None:
        conexao.execute(
            "UPDATE questao_versoes SET atual=CASE WHEN id=? THEN 1 ELSE 0 END WHERE questao_id=?",
            (int(atual_id), int(questao_id)),
        )
    return versao_id


def registrar_evidencia_tentativa(
    conexao,
    tentativa_id: int,
    questao_id: int,
    concurso_id: int,
    alternativa_marcada: str | None,
    gabarito: str | None,
    correta: bool | None,
    marcada_duvida: bool = False,
    usar_snapshot_historico: bool = False,
    tempo_segundos: int | None = None,
) -> dict:
    garantir_schema(conexao)
    tentativa_id = int(tentativa_id)
    questao_id = int(questao_id)
    concurso_id = int(concurso_id)
    if correta is None:
        return {"registradas": 0, "microtemas": []}
    existe = conexao.execute(
        "SELECT 1 FROM tentativa_microtemas WHERE tentativa_id=? LIMIT 1", (tentativa_id,)
    ).fetchone()
    if existe is not None:
        mids = [int(r[0]) for r in conexao.execute(
            "SELECT DISTINCT microtema_id FROM tentativa_microtemas WHERE tentativa_id=?", (tentativa_id,)
        ).fetchall()]
        return {"registradas": 0, "microtemas": mids, "ja_existia": True}

    mapa = {}
    for letra, mid in conexao.execute(
        "SELECT letra, microtema_id FROM alternativa_microtemas WHERE questao_id=?", (questao_id,)
    ).fetchall():
        mapa.setdefault(str(letra).upper(), []).append(int(mid))
    if not mapa:
        return {"registradas": 0, "microtemas": []}

    marcada = _texto(alternativa_marcada).upper() or None
    gab = _texto(gabarito).upper() or None
    versao_id = (
        _versao_snapshot_tentativa(conexao, tentativa_id, questao_id)
        if usar_snapshot_historico
        else _versao_atual_id(conexao, questao_id)
    )
    eventos = []

    def add(letra, tipo, valor, peso):
        for mid in mapa.get(letra, []):
            eventos.append((mid, letra, tipo, float(valor), float(peso)))

    if bool(correta):
        if gab:
            add(gab, "reconheceu_correta", 1.0, 1.0 if not marcada_duvida else 0.70)
        # Rejeitar distratores é evidência fraca, não domínio pleno.
        for letra in mapa:
            if letra != gab:
                add(letra, "rejeitou_distrator", 0.25, 0.15 if not marcada_duvida else 0.08)
    else:
        if marcada:
            add(marcada, "aceitou_distrator", -1.0, 1.0)
        if gab:
            add(gab, "nao_reconheceu_correta", -0.85, 0.85)

    if marcada_duvida:
        alvo = marcada or gab
        if alvo:
            add(alvo, "duvida", -0.25, 0.20)

    # Acerto muito mais lento que o padrão pessoal é um sinal fraco de
    # hesitação, nunca equivalente a erro. Só é calculado com uma base mínima
    # de tempos corretos do mesmo tópico para evitar falsos positivos.
    if bool(correta) and tempo_segundos is not None and int(tempo_segundos) > 0:
        topico_row = conexao.execute(
            "SELECT topico_id_snapshot FROM tentativas_questoes WHERE id=?",
            (tentativa_id,),
        ).fetchone()
        topico_id = int(topico_row[0]) if topico_row and topico_row[0] is not None else None
        if topico_id is not None:
            tempos = [int(r[0]) for r in conexao.execute(
                """
                SELECT tempo_segundos
                FROM tentativas_questoes
                WHERE concurso_id=? AND topico_id_snapshot=? AND correta=1
                  AND tempo_segundos IS NOT NULL AND tempo_segundos > 0 AND id<>?
                ORDER BY respondida_em DESC, id DESC
                LIMIT 100
                """,
                (concurso_id, topico_id, tentativa_id),
            ).fetchall()]
            if len(tempos) >= 8:
                tempos_ordenados = sorted(tempos)
                n = len(tempos_ordenados)
                mediana = (
                    float(tempos_ordenados[n // 2])
                    if n % 2
                    else (tempos_ordenados[n // 2 - 1] + tempos_ordenados[n // 2]) / 2.0
                )
                limite = max(45.0, mediana * 1.8, mediana + 15.0)
                if float(tempo_segundos) >= limite:
                    alvo = marcada or gab
                    if alvo:
                        add(alvo, "hesitacao", -0.60, 0.30)

    registrados = 0
    mids = set()
    for mid, letra, tipo, valor, peso in eventos:
        cur = conexao.execute(
            """
            INSERT OR IGNORE INTO tentativa_microtemas (
                tentativa_id, microtema_id, questao_versao_id, letra_relacionada,
                tipo_sinal, valor, peso
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (tentativa_id, mid, versao_id, letra, tipo, valor, peso),
        )
        if cur.rowcount:
            registrados += 1
            mids.add(mid)

    if mids:
        recalcular_estados(conexao, concurso_id, mids)
    return {"registradas": registrados, "microtemas": sorted(mids)}


def _parse_dt(valor):
    if not valor:
        return None
    try:
        return datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
    except Exception:
        try:
            return datetime.strptime(str(valor)[:19], "%Y-%m-%d %H:%M:%S")
        except Exception:
            return None


def recalcular_estados(conexao, concurso_id: int, microtema_ids: Iterable[int] | None = None) -> int:
    concurso_id = int(concurso_id)
    params = [concurso_id]
    filtro = ""
    if microtema_ids is not None:
        mids = sorted({int(x) for x in microtema_ids})
        if not mids:
            return 0
        filtro = " AND tm.microtema_id IN (%s)" % ",".join("?" * len(mids))
        params.extend(mids)
    linhas = conexao.execute(
        f"""
        SELECT tm.microtema_id, tm.valor, tm.peso, tq.respondida_em, tm.tipo_sinal
        FROM tentativa_microtemas tm
        JOIN tentativas_questoes tq ON tq.id = tm.tentativa_id
        WHERE tq.concurso_id = ? {filtro}
        ORDER BY tm.microtema_id, tq.respondida_em, tm.id
        """,
        params,
    ).fetchall()
    por = {}
    for mid, valor, peso, respondida, tipo_sinal in linhas:
        por.setdefault(int(mid), []).append(
            (float(valor), float(peso or 1.0), respondida, str(tipo_sinal or ""))
        )

    hoje = date.today()
    for mid, eventos in por.items():
        pos = sum(peso * max(valor, 0.0) for valor, peso, _, _ in eventos)
        neg = sum(peso * abs(min(valor, 0.0)) for valor, peso, _, _ in eventos)
        total = pos + neg
        if total <= 0:
            continue
        taxa = pos / total
        confianca = min(1.0, total / 2.5)
        dominio = 100.0 * taxa * (0.55 + 0.45 * confianca)
        tipos_erro = {"aceitou_distrator", "nao_reconheceu_correta"}
        erros = [(valor, peso, dt, tipo) for valor, peso, dt, tipo in eventos if tipo in tipos_erro]
        ultimo = max((_parse_dt(dt) for _, _, dt, _ in eventos if _parse_dt(dt)), default=None)
        ultimo_erro = max((_parse_dt(dt) for _, _, dt, _ in erros if _parse_dt(dt)), default=None)
        recente = 0.0
        if ultimo_erro is not None:
            dias = max(0, (hoje - ultimo_erro.date()).days)
            recente = 1.0 if dias <= 2 else 0.8 if dias <= 7 else 0.55 if dias <= 30 else 0.25
        erro_ratio = neg / total
        sinais = [
            1 if v > 0 else -1
            for v, p, _, tipo in eventos
            if p >= 0.5 and tipo not in {"duvida", "hesitacao", "rejeitou_distrator"}
        ]
        alternancias = sum(1 for a, b in zip(sinais, sinais[1:]) if a != b)
        instabilidade = min(1.0, alternancias / max(1, len(sinais) - 1)) if len(sinais) > 1 else 0.0
        fragilidade = 100.0 * min(1.0, 0.65 * erro_ratio + 0.25 * recente + 0.10 * instabilidade)

        if fragilidade >= 70:
            prox = hoje + timedelta(days=1); estado = "fragil"
        elif fragilidade >= 45:
            prox = hoje + timedelta(days=3); estado = "atencao"
        elif fragilidade >= 25:
            prox = hoje + timedelta(days=7); estado = "observacao"
        elif dominio >= 85 and confianca >= 0.65:
            prox = hoje + timedelta(days=21); estado = "consolidado"
        elif dominio >= 70:
            prox = hoje + timedelta(days=14); estado = "em_consolidacao"
        else:
            prox = hoje + timedelta(days=7); estado = "evidencia_baixa"

        conexao.execute(
            """
            INSERT INTO microtema_estado (
                concurso_id, microtema_id, evidencias, peso_positivo, peso_negativo,
                dominio_atual, fragilidade, confianca, ultima_evidencia, ultimo_erro,
                proxima_revisao, estado, atualizado_em
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now','localtime'))
            ON CONFLICT(concurso_id, microtema_id) DO UPDATE SET
                evidencias=excluded.evidencias,
                peso_positivo=excluded.peso_positivo,
                peso_negativo=excluded.peso_negativo,
                dominio_atual=excluded.dominio_atual,
                fragilidade=excluded.fragilidade,
                confianca=excluded.confianca,
                ultima_evidencia=excluded.ultima_evidencia,
                ultimo_erro=excluded.ultimo_erro,
                proxima_revisao=excluded.proxima_revisao,
                estado=excluded.estado,
                atualizado_em=excluded.atualizado_em
            """,
            (
                concurso_id, mid, len(eventos), round(pos, 4), round(neg, 4),
                round(dominio, 2), round(fragilidade, 2), round(100.0 * confianca, 2),
                ultimo.strftime("%Y-%m-%d %H:%M:%S") if ultimo else None,
                ultimo_erro.strftime("%Y-%m-%d %H:%M:%S") if ultimo_erro else None,
                prox.isoformat(), estado,
            ),
        )
    return len(por)


def backfill_tentativas(conexao, topico_id: int = TOPICO_CRIMES_PESSOA_ID) -> dict:
    garantir_schema(conexao)
    linhas = conexao.execute(
        """
        SELECT tq.id, tq.questao_id, tq.concurso_id, tq.alternativa_marcada,
               tq.gabarito_snapshot, tq.correta, tq.marcada_duvida, tq.tempo_segundos
        FROM tentativas_questoes tq
        LEFT JOIN questoes q ON q.id = tq.questao_id
        WHERE COALESCE(tq.topico_id_snapshot, q.topico_id) = ?
          AND tq.correta IS NOT NULL
        ORDER BY tq.id
        """,
        (int(topico_id),),
    ).fetchall()
    total_eventos = 0; tentativas = 0; concursos = set()
    for row in linhas:
        if row[1] is None or row[2] is None:
            continue
        res = registrar_evidencia_tentativa(
            conexao, int(row[0]), int(row[1]), int(row[2]), row[3], row[4], bool(row[5]), bool(row[6]),
            usar_snapshot_historico=True, tempo_segundos=row[7],
        )
        if res.get("registradas"):
            tentativas += 1; total_eventos += int(res["registradas"]); concursos.add(int(row[2]))
    for concurso_id in concursos:
        recalcular_estados(conexao, concurso_id)
    return {"tentativas_processadas": tentativas, "eventos_criados": total_eventos, "concursos": sorted(concursos)}


def backfill_hesitacoes(conexao, topico_id: int = TOPICO_CRIMES_PESSOA_ID) -> dict:
    """Enriquece tentativas históricas com hesitação relativa ao próprio aluno.

    O cálculo é cronológico: cada resposta só é comparada com tempos corretos
    anteriores do mesmo concurso/tópico, sem usar informação futura.
    """
    garantir_schema(conexao)
    existe_taxonomia = conexao.execute(
        "SELECT 1 FROM microtemas WHERE topico_id=? AND status='ativo' LIMIT 1",
        (int(topico_id),),
    ).fetchone()
    if existe_taxonomia is None:
        return {"aplicado": False, "eventos_criados": 0, "concursos": []}

    rows = conexao.execute(
        """
        SELECT tq.id, tq.questao_id, tq.concurso_id, tq.topico_id_snapshot,
               tq.alternativa_marcada, tq.gabarito_snapshot, tq.tempo_segundos,
               tq.respondida_em
        FROM tentativas_questoes tq
        LEFT JOIN questoes q ON q.id=tq.questao_id
        WHERE COALESCE(tq.topico_id_snapshot,q.topico_id)=?
          AND tq.correta=1 AND tq.tempo_segundos IS NOT NULL AND tq.tempo_segundos>0
        ORDER BY tq.concurso_id, tq.respondida_em, tq.id
        """,
        (int(topico_id),),
    ).fetchall()

    historico = {}
    criados = 0
    concursos = set()
    mids_afetados = set()
    for tentativa_id, questao_id, concurso_id, top_snapshot, marcada, gab, tempo, _ in rows:
        chave = (int(concurso_id), int(top_snapshot or topico_id))
        anteriores = historico.setdefault(chave, [])
        tempo = int(tempo)
        if len(anteriores) >= 8:
            ordenados = sorted(anteriores[-100:])
            n = len(ordenados)
            mediana = (
                float(ordenados[n // 2])
                if n % 2
                else (ordenados[n // 2 - 1] + ordenados[n // 2]) / 2.0
            )
            limite = max(45.0, mediana * 1.8, mediana + 15.0)
            if float(tempo) >= limite:
                letra = _texto(marcada).upper() or _texto(gab).upper() or None
                versao_row = conexao.execute(
                    """
                    SELECT questao_versao_id
                    FROM tentativa_microtemas
                    WHERE tentativa_id=? AND questao_versao_id IS NOT NULL
                    ORDER BY id LIMIT 1
                    """,
                    (int(tentativa_id),),
                ).fetchone()
                versao_id = int(versao_row[0]) if versao_row else _versao_snapshot_tentativa(
                    conexao, int(tentativa_id), int(questao_id)
                )
                if letra and versao_id is not None:
                    mids = [int(r[0]) for r in conexao.execute(
                        """
                        SELECT microtema_id FROM questao_versao_microtemas
                        WHERE versao_id=? AND letra=?
                        """,
                        (int(versao_id), letra),
                    ).fetchall()]
                    for mid in mids:
                        cur = conexao.execute(
                            """
                            INSERT OR IGNORE INTO tentativa_microtemas(
                                tentativa_id,microtema_id,questao_versao_id,letra_relacionada,
                                tipo_sinal,valor,peso
                            ) VALUES(?,?,?,?,'hesitacao',-0.60,0.30)
                            """,
                            (int(tentativa_id), mid, int(versao_id), letra),
                        )
                        if cur.rowcount:
                            criados += 1
                            mids_afetados.add(mid)
                            concursos.add(int(concurso_id))
        anteriores.append(tempo)

    for concurso_id in concursos:
        recalcular_estados(conexao, concurso_id, mids_afetados)
    return {
        "aplicado": True,
        "eventos_criados": criados,
        "concursos": sorted(concursos),
    }


def listar_microtemas(conexao, topico_id: int, concurso_id: int | None = None) -> list[dict]:
    params = [int(topico_id)]
    join = ""
    campos_estado = "NULL, NULL, NULL, NULL, NULL, NULL"
    if concurso_id is not None:
        join = "LEFT JOIN microtema_estado me ON me.microtema_id=m.id AND me.concurso_id=?"
        params = [int(concurso_id), int(topico_id)]
        campos_estado = "me.dominio_atual, me.fragilidade, me.confianca, me.ultima_evidencia, me.proxima_revisao, me.estado"
    rows = conexao.execute(
        f"""
        SELECT m.id,m.chave_estavel,m.capitulo_id,m.familia,m.nome,m.descricao,m.status,m.ordem,
               {campos_estado},
               COUNT(DISTINCT qm.questao_id) AS questoes_ativas
        FROM microtemas m
        {join}
        LEFT JOIN questao_microtemas qm ON qm.microtema_id=m.id
        LEFT JOIN questoes q ON q.id=qm.questao_id AND q.ativa=1 AND COALESCE(q.excluida,0)=0
        WHERE m.topico_id=? AND m.status='ativo'
        GROUP BY m.id
        ORDER BY m.capitulo_id,m.ordem,m.id
        """,
        params,
    ).fetchall()
    return [
        {
            "id":int(r[0]),"chave_estavel":r[1],"capitulo_id":r[2],"familia":r[3],"nome":r[4],
            "descricao":r[5],"status":r[6],"ordem":int(r[7] or 0),"dominio_atual":r[8],
            "fragilidade":r[9],"confianca":r[10],"ultima_evidencia":r[11],"proxima_revisao":r[12],
            "estado":r[13] or "sem_evidencia","questoes_ativas":int(r[14] or 0),
        }
        for r in rows
    ]


def selecionar_refinamento(
    conexao,
    concurso_id: int,
    topico_id: int,
    dominio_topico: float | None,
    quantidade: int = 10,
    limiar_dominio: float = LIMIAR_REFINAMENTO_PADRAO,
) -> dict:
    garantir_schema(conexao)
    dominio = None if dominio_topico is None else float(dominio_topico)
    if dominio is None or dominio < float(limiar_dominio):
        return {
            "elegivel": False, "motivo": "dominio_abaixo_limiar", "dominio_topico": dominio,
            "limiar": float(limiar_dominio), "fila": [], "microtemas_prioritarios": [],
            "versao": VERSAO_REFINAMENTO,
        }

    quantidade = max(1, int(quantidade or 1))
    hoje = date.today().isoformat()
    micros = conexao.execute(
        """
        SELECT m.id,m.chave_estavel,m.nome,m.familia,m.capitulo_id,
               me.dominio_atual,me.fragilidade,me.confianca,me.ultima_evidencia,
               me.ultimo_erro,me.proxima_revisao,me.estado
        FROM microtemas m
        JOIN microtema_estado me ON me.microtema_id=m.id AND me.concurso_id=?
        WHERE m.topico_id=? AND m.status='ativo'
          AND (
            me.fragilidade >= 20
            OR (me.proxima_revisao IS NOT NULL AND me.proxima_revisao <= ?)
          )
        ORDER BY me.fragilidade DESC,
                 CASE WHEN me.proxima_revisao <= ? THEN 0 ELSE 1 END,
                 me.ultimo_erro DESC,
                 m.ordem
        """,
        (int(concurso_id), int(topico_id), hoje, hoje),
    ).fetchall()
    if not micros:
        return {
            "elegivel": True,"motivo":"sem_fragilidade_relevante","dominio_topico":dominio,
            "limiar":float(limiar_dominio),"fila":[],"microtemas_prioritarios":[],"versao":VERSAO_REFINAMENTO,
        }

    micro_info = {int(r[0]): {
        "id":int(r[0]),"chave_estavel":r[1],"nome":r[2],"familia":r[3],"capitulo_id":r[4],
        "dominio_atual":r[5],"fragilidade":float(r[6] or 0),"confianca":float(r[7] or 0),
        "ultima_evidencia":r[8],"ultimo_erro":r[9],"proxima_revisao":r[10],"estado":r[11],
    } for r in micros}
    mids = list(micro_info)
    marcas = ",".join("?" * len(mids))
    rows = conexao.execute(
        f"""
        SELECT q.id,q.capitulo_id,q.enunciado,qm.microtema_id,
               MAX(tq.respondida_em) AS ultima_resposta,
               COUNT(CASE WHEN tq.correta IS NOT NULL THEN 1 END) AS tentativas
        FROM questoes q
        JOIN questao_microtemas qm ON qm.questao_id=q.id
        LEFT JOIN tentativas_questoes tq
          ON tq.concurso_id=? AND COALESCE(tq.questao_id_snapshot,tq.questao_id)=q.id
        WHERE q.topico_id=? AND q.ativa=1 AND COALESCE(q.excluida,0)=0
          AND qm.microtema_id IN ({marcas})
        GROUP BY q.id,qm.microtema_id
        """,
        [int(concurso_id),int(topico_id),*mids],
    ).fetchall()
    por_q = {}
    for qid, capid, enun, mid, ultima, tentativas in rows:
        item = por_q.setdefault(int(qid), {"id":int(qid),"capitulo_id":capid,"enunciado":enun,
            "microtemas":[],"ultima_resposta":ultima,"tentativas":int(tentativas or 0)})
        item["microtemas"].append(micro_info[int(mid)])
        if ultima and (not item["ultima_resposta"] or str(ultima)>str(item["ultima_resposta"])):
            item["ultima_resposta"] = ultima

    for item in por_q.values():
        frags = sorted((m["fragilidade"] for m in item["microtemas"]), reverse=True)
        score = (frags[0] if frags else 0) + 0.25 * sum(frags[1:3])
        if item["tentativas"] == 0:
            score += 18.0
        else:
            dt = _parse_dt(item["ultima_resposta"])
            if dt:
                dias = max(0,(date.today()-dt.date()).days)
                score += min(12.0, dias * 0.7)
                if dias <= 1 and (frags[0] if frags else 0) < 70:
                    score -= 10.0
        item["score_refino"] = round(score,2)
        item["motivo_inteligente"] = "Refinamento de microtema frágil."
        item["categoria_inteligente"] = "refino_microtema"
        item["categoria_rotulo"] = "Refinamento de microtema"
        item["prioridade_base"] = round(score,2)
        item["microtemas_alvo"] = [m["nome"] for m in sorted(item["microtemas"], key=lambda x:-x["fragilidade"])[:3]]

    candidatos = sorted(por_q.values(), key=lambda x:(-x["score_refino"], x["tentativas"], x["id"]))
    escolhidas=[]; cobertos=set()
    while candidatos and len(escolhidas)<quantidade:
        melhor=max(candidatos,key=lambda q:(
            sum(m["fragilidade"] for m in q["microtemas"] if m["id"] not in cobertos),
            q["score_refino"], -q["tentativas"], -q["id"]
        ))
        candidatos.remove(melhor); escolhidas.append(melhor)
        cobertos.update(m["id"] for m in melhor["microtemas"])

    return {
        "elegivel":True,"motivo":"refinamento_pontos_fracos","dominio_topico":dominio,
        "limiar":float(limiar_dominio),"fila":escolhidas,
        "microtemas_prioritarios":[micro_info[mid] for mid in mids[:max(10,quantidade*2)]],
        "versao":VERSAO_REFINAMENTO,
    }


def diagnostico_piloto(conexao, topico_id: int = TOPICO_CRIMES_PESSOA_ID) -> dict:
    garantir_schema(conexao)
    q_ativas = int(conexao.execute(
        "SELECT COUNT(*) FROM questoes WHERE topico_id=? AND ativa=1 AND COALESCE(excluida,0)=0", (int(topico_id),)
    ).fetchone()[0])
    a_ativas = int(conexao.execute(
        """SELECT COUNT(*) FROM alternativas_questoes a JOIN questoes q ON q.id=a.questao_id
           WHERE q.topico_id=? AND q.ativa=1 AND COALESCE(q.excluida,0)=0""", (int(topico_id),)
    ).fetchone()[0])
    m_ativos = int(conexao.execute(
        "SELECT COUNT(*) FROM microtemas WHERE topico_id=? AND status='ativo'", (int(topico_id),)
    ).fetchone()[0])
    alt_map = int(conexao.execute(
        """SELECT COUNT(*) FROM alternativa_microtemas am JOIN questoes q ON q.id=am.questao_id
           WHERE q.topico_id=? AND q.ativa=1 AND COALESCE(q.excluida,0)=0""", (int(topico_id),)
    ).fetchone()[0])
    gaps = int(conexao.execute(
        """SELECT COUNT(*) FROM alternativas_questoes a JOIN questoes q ON q.id=a.questao_id
           WHERE q.topico_id=? AND q.ativa=1 AND COALESCE(q.excluida,0)=0
             AND NOT EXISTS (SELECT 1 FROM alternativa_microtemas am WHERE am.questao_id=q.id AND am.letra=a.letra)""", (int(topico_id),)
    ).fetchone()[0])
    versoes = int(conexao.execute(
        """SELECT COUNT(*) FROM questao_versoes v JOIN questoes q ON q.id=v.questao_id
           WHERE q.topico_id=?""", (int(topico_id),)
    ).fetchone()[0])
    pend = int(conexao.execute(
        """SELECT COUNT(*) FROM microtema_mapeamento_pendencias p JOIN questoes q ON q.id=p.questao_id
           WHERE q.topico_id=? AND p.resolvida=0""", (int(topico_id),)
    ).fetchone()[0])
    ev = int(conexao.execute(
        """SELECT COUNT(*) FROM tentativa_microtemas tm JOIN tentativas_questoes tq ON tq.id=tm.tentativa_id
           LEFT JOIN questoes q ON q.id=tq.questao_id WHERE COALESCE(tq.topico_id_snapshot,q.topico_id)=?""", (int(topico_id),)
    ).fetchone()[0])
    estados = int(conexao.execute(
        """SELECT COUNT(*) FROM microtema_estado me JOIN microtemas m ON m.id=me.microtema_id WHERE m.topico_id=?""", (int(topico_id),)
    ).fetchone()[0])
    return {
        "topico_id":int(topico_id),"questoes_ativas":q_ativas,"alternativas_ativas":a_ativas,
        "microtemas_ativos":m_ativos,"mapeamentos_alternativas":alt_map,"lacunas_mapeamento":gaps,
        "versoes_questoes":versoes,"pendencias_mapeamento":pend,"eventos_evidencia":ev,"estados_microtema":estados,
    }
