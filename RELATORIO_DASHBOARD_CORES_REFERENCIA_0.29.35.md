# VighnaStudy 0.29.35 — Ajuste de paleta do Dashboard futurista

## Objetivo
Aproximar o Dashboard futurista da referência enviada pelo usuário, priorizando a mesma família cromática:
- fundo geral azul-marinho quase preto;
- superfícies em cinza-azulado escuro;
- CTAs principais em azul-violeta;
- card de progresso em verde-esmeralda;
- selo de atenção em âmbar suave.

## Arquivos alterados
- `tema.py`
- `versao.py`
- `test_dashboard_palette_reference_0_29_35.py`

## Ajustes visuais principais
### 1) Topo
- barra superior escurecida para um navy neutro;
- busca global em cinza-azulado escuro;
- botão `Central de Questões` convertido para o mesmo conjunto cromático escuro da referência;
- botão de engrenagem alinhado à mesma linguagem.

### 2) Card `Foco`
- fundo ajustado para cinza-azulado escuro;
- selo `PROTAGONISTA` mantido em rosa queimado suave;
- CTA `Iniciar Foco` convertido para azul-violeta, aproximando-se da referência.

### 3) Card `Planejamento de hoje`
- fundo e bordas aproximados ao cinza-azulado escuro da referência;
- chips e selos reequilibrados, preservando o âmbar de atenção.

### 4) Card `Recomendação do algoritmo`
- superfície escura neutra;
- botão principal `COMEÇAR AGORA` migrado para azul-violeta, em sintonia com a imagem de referência.

### 5) Card `Seu progresso`
- card migrado para gradiente verde-esmeralda;
- badge, barra de progresso e botão secundário harmonizados com esse novo bloco verde.

### 6) Busca global
- popup e campo de busca global harmonizados com a nova paleta do Dashboard futurista.

## Validação executada
- `python -m py_compile tema.py versao.py main.py`
- `python -m unittest -v test_dashboard_palette_reference_0_29_35.py`

## Versão
- `0.29.35`
- build: `dashboard-futurista-palette-reference-v1`
