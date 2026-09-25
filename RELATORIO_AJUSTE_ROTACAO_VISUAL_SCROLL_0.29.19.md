# VighnaStudy 0.29.19 — Rotação visual sem corte das alternativas

## Objetivo
Eliminar o recorte vertical das alternativas do minijogo **Rotação visual** em **Pausa & Desafios**, preservando o tamanho dos cartões e das figuras em janelas com menor altura útil.

## Diagnóstico
O problema não estava apenas no desenho vetorial. A grade possuía duas linhas de alternativas, mas o conteúdo da aba podia ser comprimido pelo `QTabWidget`. Nessa situação, a segunda linha continuava existindo, porém ficava parcialmente fora da área visível.

## Ajustes realizados
- O conteúdo inteiro de **Rotação & Espelho** foi colocado em um `QScrollArea` exclusivo.
- A rolagem horizontal foi desativada e a vertical aparece somente quando necessária.
- O conteúdo rolável recebeu altura mínima de `520 px`, impedindo compressão destrutiva pela aba.
- A grade das seis alternativas passou a ter um contêiner próprio (`rotationOptionsContainer`).
- Cada linha da grade reserva `112 px` de altura, com duas linhas completas e `10 px` de espaçamento vertical.
- Cada cartão de alternativa possui mínimo de `150 × 112 px`.
- O canvas interno de cada alternativa passou a ter mínimo de `110 × 88 px` e continua escalando a matriz proporcionalmente para caber integralmente.
- A forma original recebeu mínimo de `180 × 96 px`, mantendo centralização e melhor legibilidade.
- Os temas claro, escuro e futurista foram atualizados para preservar `112 px` de altura nos cartões e manter os contêineres de rolagem transparentes.
- Em telas altas, as seis alternativas aparecem integralmente sem necessidade de rolagem. Em telas com menor altura útil, os cartões mantêm o tamanho e o usuário rola a aba verticalmente, sem corte.

## Persistência
Nenhuma tabela, dado de estudo ou regra do motor foi alterada. `VIGHNA_SCHEMA` permanece em `22`.

## Versão
- `VIGHNA_VERSION = 0.29.19`
- `VIGHNA_BUILD = pausa-rotacao-visual-scroll-v3`
- `VIGHNA_SCHEMA = 22`

## Validação
- Teste estrutural: `test_rotacao_visual_layout_0_29_19.py`.
- Compilação estática de todos os fontes Python do checkpoint.
- A validação visual final deve ser feita no runtime Windows/PySide6 do projeto.
