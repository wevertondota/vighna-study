# Relatório da pasta atual

**Caminho analisado:** `C:\SistemaEstudos`  
**Data da análise:** 16/09/2026

A pasta contém o projeto desktop **VighnaStudy**, versão **0.23.4**, escrito em Python com PySide6 e SQLite.

## Visão geral

- **Tamanho total:** aproximadamente 1,06 GB
- **Arquivos:** 8.848
- **Código Python:** 36 arquivos, cerca de 2,72 MB
- **Interface:** PySide6/Qt
- **Persistência:** SQLite
- **Distribuição:** PyInstaller
- **Sistema-alvo:** Windows
- **Executável atual:** `dist\SistemaEstudos\VighnaStudy.exe`

## Estrutura principal

| Pasta | Tamanho | Função |
|---|---:|---|
| `.venv` | 665,88 MB | Ambiente virtual Python e dependências |
| `dist` | 167,31 MB | Distribuições executáveis atual e antiga |
| `SistemaEstudos Reserva Final` | 160,03 MB | Reserva de versões executáveis anteriores |
| `.git` | 60,08 MB | Histórico Git |
| `backups` | 13,33 MB | Backups automáticos do banco |
| `checkpoints` | 7,89 MB | 14 checkpoints completos em ZIP |
| `build` | 6,22 MB | Arquivos intermediários do PyInstaller |
| `__pycache__` | 2,47 MB | Bytecode Python |
| `recuperacao_banco` | 0,45 MB | Banco e arquivos WAL/SHM preservados após recuperação |
| `Recuperação Chat` | 0,37 MB | Documento e ZIP usados para retomar o projeto |

## Código-fonte

Os três arquivos centrais são:

- `main.py`: aplicação principal e quase toda a interface. Tem 1,46 MB e dezenas de janelas para dashboard, questões, simulados, planejamento, concursos, backups, configurações e revisões.
- `banco.py`: camada SQLite e regras de negócio. Gerencia concursos, disciplinas, tópicos, revisões, questões, sessões, simulados, índices de domínio, recomendações, foco e relatórios.
- `tema.py`: estilos Qt dos temas claro, escuro e futurista.

### Módulos especializados

- `backup.py`: criação, validação, limpeza e restauração de backups.
- `checkpoint.py`: checkpoints ZIP do projeto com inventário e hashes SHA-256.
- `inteligencia.py`: motores de recomendação V4 e V5.
- `importador_pdf.py`: extração e interpretação de questões em PDF, incluindo formato VPQ.
- `foco.py`: temporizador, modo foco e tela pós-foco.
- `jogos.py`: jogos de memória, sequência visual, quebra-cabeça e chimpanzé.
- `jornada.py`: geração e acompanhamento da jornada diária.
- `espacamento.py`: cálculo de revisões espaçadas.
- `evolucao.py`: histórico e indicadores de evolução.
- `laboratorio.py`: comparação e ajuste do motor de recomendação.
- `diagnostico.py`: diagnóstico da instalação e manutenção segura do banco.
- `navegacao.py`: busca global.
- `testes_smoke.py`: testes integrados básicos.
- `versao.py`: versão `0.23.4`, build `central-questoes-organizacao-v2` e schema 14.

## Banco de dados

O banco ativo é `estudos.db`, com 434 KB. A verificação `PRAGMA integrity_check` retornou **ok**.

### Principais dados

| Entidade | Registros |
|---|---:|
| Concursos | 3 |
| Disciplinas | 7 |
| Tópicos | 105 |
| Questões | 29 |
| Alternativas | 136 |
| Revisões | 3 |
| Sessões de questões | 3 |
| Tentativas | 6 |
| Simulados | 1 |
| Recomendações de estudo | 11 |
| Configurações | 21 |

Existem 21 tabelas no total.

## Empacotamento

Os arquivos `VighnaStudy.spec` e `SistemaEstudos.spec` geram aplicações Windows sem console a partir de `main.py`, usando o ícone `vighnastudy.ico`.

### Dependências instaladas

- Python 3.13
- PySide6 6.11.2
- PyInstaller 6.22.3
- pypdf 6.18.1
- Shiboken6 e componentes auxiliares do Qt

## Backups e recuperação

A pasta `backups` possui 90 arquivos, organizados em 30 conjuntos SQLite com:

- arquivo `.db`;
- arquivo `.db-wal`;
- arquivo `.db-shm`.

Os scripts `recuperar_banco.py`, `copiar_banco_consistente.py` e os arquivos `.bat` auxiliam na recuperação, cópia consistente, criação do executável e atalhos.

## Git e organização

O repositório está na branch `master`, sem alterações pendentes no momento da análise, com dois commits:

- `79b4c77` — `chore: backup arquivos`
- `abddc40` — `chore: adiciona os arquivos base`

Há 627 arquivos versionados. O repositório não possui `.gitignore`, `README` nem arquivo explícito de dependências. Atualmente também estão versionados:

- 209 arquivos de `dist`;
- 212 arquivos da reserva final;
- 90 backups;
- 18 arquivos de `__pycache__`;
- 16 artefatos de `build`;
- 14 checkpoints.

## Avaliação estrutural

A principal questão estrutural é a concentração de grande parte da aplicação em `main.py` e `banco.py`, junto com executáveis, bancos e backups no mesmo repositório. Isso explica o tamanho elevado e torna manutenção, revisão e histórico Git mais difíceis.
