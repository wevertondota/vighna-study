"""M25 — ativação de produção do mérito com identidade e origem verificadas.

Nenhum dado acadêmico é alterado: M09 abre estudos.db por SQLite mode=ro;
M10 grava apenas o banco lateral em LOCALAPPDATA. Falha fechada.
O nome exibido no Perfil e o concurso ativo nunca definem a identidade.

Cópias de teste podem chamar a função com módulo backup sintético no ambiente
isolado; produção usa obrigatoriamente backup.ARQUIVO_BANCO e banco.py assinado
pelo hash de referência A–T, SEM variáveis de override de origem acadêmica.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import os
import sys

HASH_BANCO_HISTORICO_AT = "a6f122846530a2d50710f5d1a3f7cd5d4a21e6e353b68fb89fe6d91a388a633b"
SUBPASTAS_ESTADO = ("VighnaStudy", "MeritoGlobal")
NOME_BANCO_MERITO = "merito_global_vighna.sqlite3"


class ProducaoM25Bloqueada(RuntimeError):
    """Falha segura: não publicar brasões com fonte ou identidade duvidosa."""


@dataclass(frozen=True)
class LocalizacaoM25:
    raiz_instalacao: Path
    banco_academico: Path
    fonte_banco: Path
    pasta_persistente: Path
    banco_merito: Path


def _sem_symlink(arquivo: Path, *, incluir_pais: bool = False) -> None:
    cursor = arquivo
    while True:
        if cursor.is_symlink():
            raise ProducaoM25Bloqueada("Caminho indireto de identidade ou mérito não autorizado")
        if not incluir_pais or cursor == cursor.parent:
            break
        cursor = cursor.parent


def _sob(pasta: Path, origem: Path) -> bool:
    return pasta == origem or origem in pasta.parents


def _localizacao_segura() -> LocalizacaoM25:
    """Obtém exclusivamente a origem registrada pelo aplicativo existente.

    A instalação de fontes Histórico V2 A–T tem banco.py no mesmo diretório de estudos.db;
    qualquer divergência é NO-GO até nova auditoria, não fallback silencioso.
    """
    from backup import ARQUIVO_BANCO

    var = os.environ.get("LOCALAPPDATA")
    if not var or not Path(var).is_absolute():
        raise ProducaoM25Bloqueada("LOCALAPPDATA ausente ou não absoluto")
    raiz_dados = Path(var).expanduser()
    _sem_symlink(raiz_dados)
    try:
        banco = Path(ARQUIVO_BANCO).expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ProducaoM25Bloqueada("Banco acadêmico oficial indisponível") from exc
    if not banco.is_file() or banco.name.casefold() != "estudos.db":
        raise ProducaoM25Bloqueada("Origem acadêmica não é o estudos.db oficial")
    raiz = banco.parent
    fonte = raiz / "banco.py"
    if not fonte.is_file() or fonte.is_symlink():
        raise ProducaoM25Bloqueada("banco.py da instalação indisponível")
    if sha256(fonte.read_bytes()).hexdigest() != HASH_BANCO_HISTORICO_AT:
        raise ProducaoM25Bloqueada("banco.py divergente da referência auditada Histórico V2 A–T")
    if not (raiz / "main.py").is_file() or not (raiz / "versao.py").is_file():
        raise ProducaoM25Bloqueada("Raiz de fontes da instalação incompleta")
    pasta = raiz_dados.joinpath(*SUBPASTAS_ESTADO)
    banco_merito = pasta / NOME_BANCO_MERITO
    if _sob(pasta.resolve(strict=False), raiz) or _sob(raiz, pasta.resolve(strict=False)):
        raise ProducaoM25Bloqueada("Mérito e banco acadêmico precisam estar isolados")
    if _sob(pasta.resolve(strict=False), banco):
        raise ProducaoM25Bloqueada("Armazenamento lateral coincide com banco acadêmico")
    _sem_symlink(pasta, incluir_pais=False)
    _sem_symlink(pasta.parent, incluir_pais=False)
    _sem_symlink(banco_merito)
    if banco_merito.exists() and not banco_merito.is_file():
        raise ProducaoM25Bloqueada("Armazenamento lateral não é arquivo regular")
    return LocalizacaoM25(raiz, banco, fonte, pasta, banco_merito)


def validar_escopo_producao_m25(escopo, *, conferir_schema: bool = True) -> LocalizacaoM25:
    """Validação repetida dentro do worker ANTES de ler ou gravar qualquer banco."""
    if getattr(escopo, "modo", None) != "producao":
        raise ProducaoM25Bloqueada("Modo de produção não declarado")
    local = _localizacao_segura()
    if Path(escopo.banco_academico).resolve(strict=False) != local.banco_academico:
        raise ProducaoM25Bloqueada("Escopo aponta outro banco acadêmico")
    if Path(escopo.banco_merito).resolve(strict=False) != local.banco_merito.resolve(strict=False):
        raise ProducaoM25Bloqueada("Escopo aponta outro armazenamento de mérito")
    from .identidade_candidato_m12 import obter_identidade
    ident = obter_identidade(local.pasta_persistente)
    if escopo.perfil_id != ident.perfil_id:
        raise ProducaoM25Bloqueada("Identidade persistente diverge do escopo")
    if conferir_schema:
        from .inspecao_schema_m12 import inspecionar_schema
        if not inspecionar_schema(local.banco_academico).compativel:
            raise ProducaoM25Bloqueada("Schema acadêmico incompatível")
    return local


def preparar_escopo_producao_m25():
    """Executar na GUI após o layout, antes de iniciar o worker assíncrono.

    Pode criar APENAS identidade e pasta lateral em LOCALAPPDATA; nunca cria
    estudos.db nem escreve em diretórios do aplicativo. Nenhuma apuração na GUI.
    """
    local = _localizacao_segura()
    from .inspecao_schema_m12 import inspecionar_schema
    if not inspecionar_schema(local.banco_academico).compativel:
        raise ProducaoM25Bloqueada("Schema acadêmico não homologado")
    from .identidade_candidato_m12 import ARQUIVO as ARQUIVO_IDENTIDADE
    if (local.banco_merito.exists()
            and not (local.pasta_persistente / ARQUIVO_IDENTIDADE).is_file()):
        raise ProducaoM25Bloqueada(
            "Banco de mérito anterior sem identidade: recuperação manual necessária"
        )
    try:
        local.pasta_persistente.mkdir(parents=True, exist_ok=True)
        _sem_symlink(local.pasta_persistente)
        from .identidade_candidato_m12 import obter_identidade
        # Parâmetro histórico: o método M12 cria exclusivamente na pasta que
        # recebe. M25 garante, ANTES, que a pasta é o LOCALAPPDATA oficial.
        identidade = obter_identidade(local.pasta_persistente, criar_em_laboratorio=True)
        from .integracao_merito_m11 import EscopoM11
        escopo = EscopoM11(identidade.perfil_id,
                           local.banco_academico, local.banco_merito,
                           modo="producao")
        validar_escopo_producao_m25(escopo)
        return escopo
    except (OSError, ValueError, RuntimeError) as exc:
        raise ProducaoM25Bloqueada("Falha na preparação da identidade ou do mérito lateral") from exc


def backup_conquistas_m25(escopo, estado_anterior, persistido) -> bool:
    """Backup lateral no primeiro estado ou quando faltar snapshot dos marcos.

    Confere também após um COMMIT já efetuado: se uma tentativa anterior de
    backup falhou, a execução seguinte recupera a cópia sem duplicar o mérito.
    Não sobrescreve backups, não escreve no banco acadêmico, não roda na GUI.
    """
    validar_escopo_producao_m25(escopo, conferir_schema=False)
    novo = persistido.estado
    from .persistencia_merito_m10 import ler_estado_merito, criar_backup_merito
    pasta = Path(escopo.banco_merito).parent / 'backups_merito'
    _sem_symlink(pasta)
    # Uma cópia anterior que já contém todas as conquistas atuais é suficiente.
    # A primeira apuração de 0 pontos também precisa de snapshot inicial.
    atual = {c.marco for c in novo.conquistas}
    if pasta.exists():
        if not pasta.is_dir():
            raise ProducaoM25Bloqueada('Diretório de backup lateral inválido')
        for arquivo in sorted(pasta.glob('*.sqlite3'), reverse=True):
            _sem_symlink(arquivo)
            salvo = ler_estado_merito(arquivo, escopo.perfil_id)
            if (salvo is not None and salvo.origem_auditada == novo.origem_auditada
                    and atual.issubset({c.marco for c in salvo.conquistas})):
                return False
    from datetime import datetime, timezone
    from uuid import uuid4
    pasta.mkdir(parents=True, exist_ok=True)
    alvo = pasta / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
                    + '_' + uuid4().hex[:12] + '.sqlite3')
    criar_backup_merito(escopo.banco_merito, alvo)
    return True
