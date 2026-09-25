# VighnaStudy 0.29.17 — Rotação Visual em Pausa & Desafios

## Objetivo
Adicionar um minijogo leve de raciocínio visuoespacial ao setor **Pausa & Desafios**, sem imagens externas e sem impacto relevante no tamanho do projeto.

## Implementação
- Novo jogo **Rotação & Espelho** (`rotacao_visual`).
- Figuras geradas em tempo real como pequenas matrizes de células conectadas.
- Renderização vetorial com `QPainter`; nenhum PNG/SVG é necessário para as questões.
- Seis alternativas por rodada, todas derivadas de rotações/espelhamentos reais da mesma figura.
- Formas assimétricas são escolhidas para garantir oito orientações distintas e evitar alternativas duplicadas.
- Operações disponíveis:
  - rotação de 90°, 180° e 270°;
  - espelhamento esquerda ↔ direita;
  - espelhamento cima ↔ baixo;
  - combinações de duas ou três operações nos níveis superiores.
- Progressão de dificuldade em 5 níveis:
  - menos tempo conforme o nível aumenta;
  - combinações de transformações;
  - figuras 5×5 a partir dos níveis avançados.
- Pontuação considera nível e tempo restante.
- Erro ou tempo esgotado encerra a partida e revela a alternativa correta.
- Recorde integrado ao painel de recordes de Pausa & Desafios.

## Persistência
O identificador `rotacao_visual` foi incluído em `_JOGOS_VALIDOS`. O jogo reutiliza a tabela `jogos_resultados`; não houve alteração de schema (`VIGHNA_SCHEMA = 22`).

## Interface
- Nova aba **Rotação visual** em Pausa & Desafios.
- Novo cartão de recorde.
- Estilos adicionados aos temas claro, escuro e futurista para as alternativas e para os estados de acerto/erro.

## Validação realizada
- `py_compile` dos arquivos modificados: OK.
- Parse AST dos arquivos centrais: OK.
- Testes isolados da matemática de rotação/espelhamento e geração de formas: OK, incluindo 200 gerações para cada tamanho 4×4 e 5×5, sempre com 8 orientações distintas.
- Teste de interface PySide6 foi adicionado (`test_rotacao_visual_0_29_17.py`), mas não pôde ser executado neste ambiente porque o runtime local não possui PySide6 instalado. O projeto declara `PySide6==6.11.2` em `requirements.txt`.

## Versão
- `VIGHNA_VERSION = 0.29.17`
- `VIGHNA_BUILD = pausa-rotacao-visual-v1`
- Schema permanece `22`.
