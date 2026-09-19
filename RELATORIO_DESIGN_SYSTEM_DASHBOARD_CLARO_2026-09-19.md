# RELATÓRIO — DESIGN SYSTEM DO DASHBOARD CLARO

Data: 2026-09-19  
Versão: 0.28.1  
Build: `dashboard-light-design-system`  
Schema: 19

## Objetivo
Incorporar a paleta visual sugerida ao VighnaStudy sem espalhar estilos locais pelo `main.py`, sem trocar PySide6 por PyQt6 e sem alterar os temas Escuro e Futurista.

## Estratégia adotada

### Paleta centralizada
Foi criada em `tema.py` a constante `PALETA_DASHBOARD_CLARO`, contendo os tokens principais do Dashboard:

- fundo: `#EBF2FA`
- superfície/card: `#FFFFFF`
- borda: `#E2E8F0`
- borda de controle: `#DCE3EE`
- azul principal: `#0F3989`
- hover do azul: `#1A4BA8`
- azul pressionado: `#0A3266`
- texto principal: `#1A202C`
- texto secundário: `#2D3748`
- texto suave: `#718096`
- hover claro: `#EDF2F7`

### Camada final específica do Dashboard
Foi criada `ESTILO_DESIGN_SYSTEM_DASHBOARD_CLARO`, aplicada por último no tema Claro. Ela usa `objectName` e seletores específicos, evitando um seletor global `QWidget` que poderia contaminar outras telas.

### Hierarquia dos botões
O azul forte foi reservado às ações principais:

- `Iniciar Foco`
- `COMEÇAR AGORA`

Ações de navegação ou secundárias permanecem vazadas/claras:

- Pausa
- Estatísticas
- Relatórios
- Calendário
- Central de Questões
- Ver conquistas
- Por que esta recomendação?

### Configurações
O botão de Configurações ficou sem fundo próprio no tema Claro. O ícone QtAwesome usa agora uma cor azul-marinho (`#0F3989`), permitindo que a engrenagem fique visível diretamente sobre o fundo do Dashboard.

### Remoção de estilo local
O badge circular de nível deixou de usar `setStyleSheet()` dentro de `main.py`. Agora possui `objectName="dashboardProgressBadge"` e recebe seu estilo pelo tema central.

## Arquivos alterados
- `tema.py`
- `main.py`
- `icones.py`
- `versao.py`

## Compatibilidade
- PySide6 mantido integralmente.
- QtAwesome mantido como infraestrutura opcional com fallback.
- Tema Escuro não alterado.
- Tema Futurista não alterado.
- Schema do banco permanece em 19.

## Validação
- `python -m py_compile tema.py main.py icones.py versao.py` — OK
- `python -m unittest discover -q` — 203 testes OK
- testes focados QtAwesome/Gamificação/Regularidade — 26 testes OK
- `testes_smoke.py` — OK
- SQLite `PRAGMA integrity_check` — `ok`
- SQLite `PRAGMA foreign_key_check` — sem violações

## Observação visual
A renderização final precisa ser conferida no Windows/PySide6 do usuário, pois o ambiente de trabalho atual não dispõe de renderização visual completa da aplicação.
