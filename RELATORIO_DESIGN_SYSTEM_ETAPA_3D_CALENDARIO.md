# Relatório do Design System — Etapa 3D: Calendário

## Resultado

O domínio visual do Calendário foi conectado ao Design System sem mudança
intencional de aparência, comportamento, algoritmo, layout, versão, build,
schema ou banco. O escopo inclui o calendário mensal, seus formatos
programáticos via `QTextCharFormat`, e a Semana prevista.

Os hashes canônicos completos de QSS continuam idênticos à linha de base da
Etapa 3C:

| Tema | SHA-256 canônico |
| --- | --- |
| Claro | `139709f8c57e00f16848668f9226703c7f8ff391dd9aea2bba8b2eae20ac2c5f` |
| Escuro | `ebbc21363d0035058301d060eb099fb2d33b992e8537c20f9bf1e77f8a2b4f3e` |
| Futurista | `0e588bb372946b4a6f61ad406c817fd155cac8c3c4286e9f93b7a09d06dc8622` |

## Arquivos alterados

- `main.py`: somente a resolução de foreground/background do calendário mensal;
- `tema.py`: somente os blocos mensais e as três constantes da Semana prevista;
- `ui/design/tokens.py`: contrato dos papéis estáveis de calendário;
- `ui/design/themes.py`: valores literais caracterizados nos três temas;
- `ui/design/palette.py`: valores físicos exigidos pelos novos papéis;
- `test_design_system_calendario.py`: caracterização de QSS, estados, tokens e código-fonte;
- `test_design_system_controles_compartilhados.py`: deixa de considerar `calendar.*` fora de escopo e mantém a baseline integral;
- `DESIGN_SYSTEM.md`: registra o domínio conectado e sua nomenclatura.

## Blocos migrados

### Calendário mensal

- painéis `calendarPanel` e `calendarDayPanel`;
- título e contador;
- legendas de hoje, atraso e agendamento;
- `QCalendarWidget#reviewCalendar`, barra de navegação, botões, spinbox e view;
- seleção do `QAbstractItemView`;
- foreground/background programáticos de hoje, atraso e agendamento.

Não existe, no calendário mensal atual, um formato programático próprio para
“concluído”. Nenhum estado artificial foi criado.

### Semana prevista

- seletor Mensal/Semana em normal, hover e checked;
- painel, aviso, metadados e estado vazio;
- colunas de passado, hoje e futuro;
- cards, títulos, disciplina, carga e badges;
- revisão, realizado, recomendação e simulado;
- ação de abertura em normal e hover.

O código de projeção, a ordem dos cards, o recálculo, a abertura de tópico e a
invalidação por mudanças de estudo não foram alterados.

## Tokens

Foram reutilizados 10 tokens públicos já existentes:

- `calendar.surface`;
- `calendar.today_surface`, `calendar.today_border`, `calendar.today_text`;
- `calendar.selected_surface`, `calendar.selected_text`;
- `calendar.week_predicted_surface`, `calendar.week_predicted_border`, `calendar.week_predicted_text`;
- `action.ghost`.

Foram criados 51 tokens de componente. O contrato passou de 196 para 247
tokens: 102 semânticos e 145 de componente.

Os novos papéis mensais são:

- `calendar.border`, `calendar.text`, `calendar.title_text`;
- `calendar.badge_*`;
- `calendar.legend_today`, `calendar.legend_late`, `calendar.legend_scheduled`;
- `calendar.navigation_surface`, `calendar.navigation_hover_surface`;
- `calendar.input_surface`, `calendar.input_border`;
- `calendar.late_surface`, `calendar.late_text`;
- `calendar.scheduled_surface`, `calendar.scheduled_text`.

Os novos papéis semanais são:

- `calendar.forecast_toggle_*` para normal, hover e checked;
- `calendar.forecast_action_text`, `calendar.forecast_meta_text`;
- `calendar.forecast_panel_*`, `calendar.forecast_title_text`, `calendar.forecast_notice_text`;
- `calendar.forecast_today_surface`, `calendar.forecast_past_*`;
- `calendar.forecast_count_*`, `calendar.forecast_badge_*`;
- `calendar.forecast_card_surface`, `calendar.forecast_card_accent`;
- `calendar.forecast_review`, `calendar.forecast_completed`,
  `calendar.forecast_recommendation`, `calendar.forecast_simulation`;
- `calendar.forecast_discipline_text`, `calendar.forecast_card_text`;
- `calendar.forecast_open_text`, `calendar.forecast_open_hover_surface`,
  `calendar.forecast_open_hover_border`, `calendar.forecast_empty_text`.

A quantidade foi revisada após a primeira substituição. Título versus texto de
controle e contador versus badge foram mantidos separados porque a
caracterização demonstrou valores diferentes. Os tokens agrupam papéis que se
repetem em seletores/estados; não há um token por seletor.

## Valores antes e depois

Todos os valores abaixo eram hardcodes e agora são produzidos pelos tokens
indicados, sem aproximação.

### Formatos programáticos mensais

| Estado | Claro texto/fundo | Escuro texto/fundo | Futurista texto/fundo | Tokens |
| --- | --- | --- | --- | --- |
| Hoje | `#1D4ED8` / `#DBEAFE` | `#93C5FD` / `#1E3A8A` | `#BDF7FF` / `#124E68` | `today_text` / `today_surface` |
| Atrasada | `#B91C1C` / `#FEE2E2` | `#FCA5A5` / `#4C1D24` | `#FF9BAC` / `#4B1D2C` | `late_text` / `late_surface` |
| Agendada | `#15803D` / `#DCFCE7` | `#86EFAC` / `#163523` | `#74F1C5` / `#124334` | `scheduled_text` / `scheduled_surface` |

`main.py` continua criando `QTextCharFormat` e chamando `setForeground()` e
`setBackground()`. Apenas `QColor(hex)` foi substituído por
`qcolor(tema_atual, token)`.

### Calendário mensal em QSS

| Papel | Claro | Escuro e base herdada pelo Futurista |
| --- | --- | --- |
| superfície / borda | `#FFFFFF` / `#DBE3ED` | `#182235` / `#334155` |
| título / texto de controle | `#111827` / `#1F2937` | `#F8FAFC` / `#E5E7EB` |
| badge superfície/texto/borda | `#F1F5F9` / `#475569` / `#E2E8F0` | `#273449` / `#CBD5E1` / `#334155` |
| legendas hoje/atraso/agendado | `#2563EB` / `#DC2626` / `#16A34A` | `#93C5FD` / `#FCA5A5` / `#86EFAC` |
| navegação normal/hover | `#F8FAFC` / `#E2E8F0` | `#172033` / `#273449` |
| seleção fundo/texto | `#2563EB` / `#FFFFFF` | `#2563EB` / `#FFFFFF` |

A herança Futurista permaneceu `stylesheet_escuro() + overrides`; como antes,
o calendário mensal não ganhou override futurista de QSS.

### Semana prevista

| Papel | Claro | Escuro | Futurista |
| --- | --- | --- | --- |
| toggle normal (fundo/texto/borda) | `#FFFFFF/#64748B/#D7E0EA` | `#172033/#94A3B8/#334155` | `#0D1D2D/#84A9BD/#294B63` |
| toggle hover | `#F8FAFC/#334155/#CBD5E1` | `#273449/#E2E8F0/#475569` | `#123049/#D7F3FF/#39789A` |
| toggle checked | `#E8F1FF/#1D4ED8/#93C5FD` | `#172554/#93C5FD/#1E40AF` | `#143A55/#BDF7FF/#45BCE8` |
| coluna futura | `#F8FAFC/#E2E8F0` | `#172033/#334155` | `#0D1D2D/#294B63` |
| coluna hoje | `#F0F7FF/#93C5FD` | `#172554/#1E40AF` | `#10304A/#3D9BC5` |
| coluna passada | `#F8FAFC/#E2E8F0` | `#151E2E/#2B394B` | `#0B1824/#223D50` |
| card (fundo/borda/acento) | `#FFFFFF/#DBE3ED/#64748B` | `#1D293D/#334155/#64748B` | `#102334/#294B63/#5F8296` |
| revisão | `#2563EB` | `#60A5FA` | `#4BC9F2` |
| realizado | `#16A34A` | `#4ADE80` | `#74F1C5` |
| recomendação | `#7C3AED` | `#A78BFA` | `#8D7CFF` |
| simulado | `#D97706` | `#F59E0B` | `#E7B14B` |
| vazio | `#94A3B8` | `#64748B` | `#638397` |

## Hardcodes e gradientes

- `main.py`: 18 ocorrências hexadecimais removidas;
- `tema.py`: 166 ocorrências hexadecimais removidas dos blocos migrados;
- total: 184 ocorrências hexadecimais removidas;
- 25 usos de `transparent` nos mesmos blocos passaram a usar `action.ghost`;
- hardcodes hexadecimais remanescentes no domínio migrado: zero;
- gradientes encontrados/migrados no domínio Calendário: zero.

Declarações estruturais como `border: none`, dimensões, raios e tipografia
continuam literais por não serem decisões de cor e por estarem fora do contrato
atual.

## Caracterização e equivalência

`test_design_system_calendario.py` verifica:

- hashes completos dos três stylesheets;
- valores mensais de superfície, texto, bordas, legendas e seleção;
- normal, hover e checked do seletor de visualização;
- passado, hoje e futuro;
- revisão, realizado, recomendação e simulado;
- cards, badges, ação, metadados e estado vazio;
- os 18 valores mensais programáticos via tokens e `qcolor()`;
- ausência de hexadecimais nos trechos migrados;
- preservação textual da lógica de estados e vazios.

A suíte histórica `test_calendario_previsao_semanal_0_29_59.py` continua
caracterizando visualizações, lazy load, plano de sete dias, estudos reais,
revisões, cards, abertura de tópico e invalidação.

### Execuções finais

- `py_compile` de `main.py`, `tema.py`, `ui/design/*.py` e do teste 3D: passou;
- Design System + 3A + 3B + 3C + 3D + calendário 0.29.59 + QtAwesome:
  passou;
- transparência 0.29.49: quatro verificações visuais passaram; somente a
  asserção histórica que exige versão `0.29.49` falhou, como esperado na
  versão atual `0.29.59`;
- sete módulos históricos de Dashboard: 22 testes passaram e 10 asserções
  antigas falharam por versões/layouts 0.29.28–0.29.39 já substituídos; nenhuma
  delas aponta para os blocos do Calendário;
- `testes_smoke.py`: `VighnaStudy 0.29.59: testes smoke OK`;
- `git diff --check`: passou (apenas avisos informativos de conversão LF/CRLF).

## Banco, schema e versão

- VighnaStudy: `0.29.59`;
- build: `calendar-week-forecast-v1`;
- schema declarado: `25`;
- `PRAGMA integrity_check`: `ok`;
- `PRAGMA foreign_key_check`: zero violações;
- SHA-256 do schema SQLite: `240e65de128ff81959d6277489c03a5599c7fc404b08d5ace5b79596b00f43a9`;
- arquivos funcionais de banco/schema não foram alterados.

## Checklist visual manual

Não existe harness seguro de screenshots automatizados para essas telas neste
ambiente. A comparação posterior deve registrar cada item em Claro, Escuro e
Futurista:

- [ ] calendário mensal normal;
- [ ] dia atual;
- [ ] data selecionada;
- [ ] revisão atrasada;
- [ ] revisão agendada;
- [ ] troca de mês e atualização das marcações;
- [ ] Semana prevista completa;
- [ ] colunas de passado, hoje e futuro;
- [ ] card de revisão;
- [ ] card de recomendação;
- [ ] card de simulado;
- [ ] card realizado;
- [ ] hover do seletor e da ação de abrir;
- [ ] estado vazio;
- [ ] recálculo e abertura de tópico.

## Riscos e recomendações

- O Futurista ainda depende da cascata Escuro + overrides. A migração preserva
  deliberadamente essa precedência; separá-la pertence a etapa posterior.
- `calendar.weekend_text` e `calendar.outside_month_text` continuam no contrato,
  mas o calendário atual não os consome explicitamente.
- O estado mensal “concluído” não existe na implementação atual; adicioná-lo
  seria mudança funcional/visual.
- O próximo módulo deve continuar usando hashes integrais e caracterização
  antes de tocar em `tema.py`. Nenhuma migração de resolvedor, Modo Foco,
  Dashboard, gráficos ou controles avançados foi iniciada.
