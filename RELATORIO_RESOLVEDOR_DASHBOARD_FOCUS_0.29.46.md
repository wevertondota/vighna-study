# VighnaStudy 0.29.46 — Resolvedor em modo concentração

Build: `resolvedor-dashboard-focus-v1`
Schema: `25` (sem migração de banco)

## Objetivo

Modernizar a tela **Resolver questões** para que ela pertença visualmente à mesma família do Dashboard atual, especialmente no tema Futurista, sem transformar a bateria em uma tela excessivamente ornamentada. A prioridade é manter leitura, concentração e operação rápida durante baterias longas.

## Alterações implementadas

### 1. Painel único de progresso da sessão

O progresso, o estado do ciclo e as métricas deixaram de aparecer como blocos horizontais soltos. Agora ficam reunidos em `questionSessionOverviewCard`, com:

- identificação `PROGRESSO DA SESSÃO`;
- `Questão X de Y`;
- ciclo e pendências em campo próprio;
- barra de progresso integrada;
- Respondidas, Acertos, Erros e Puladas como mini indicadores internos.

Os valores de acerto, erro e pulo receberam distinção cromática discreta, sem transformar o painel em um placar chamativo.

### 2. Modo Foco mais compacto

A faixa do Foco deixou de reutilizar o estilo dos cartões de métrica. Agora possui identidade própria (`questionSessionFocusBar`) e menor saliência visual. Os comandos **Retomar/Pausar** e **Abrir foco** continuam disponíveis e toda a lógica de janela independente da versão 0.29.45 foi preservada.

### 3. Hierarquia pedagógica mais limpa

A classificação da questão foi reorganizada em duas linhas:

- disciplina, como eyebrow discreto;
- tópico/título, como caminho principal.

Informações secundárias — inédita/já respondida, categoria inteligente, banca, ano, dificuldade, tipo Certo/Errado e motivos do motor — continuam acessíveis pelo tooltip. Repetições como `Inédita • Inédita` são eliminadas no tooltip.

### 4. Card de enunciado com identidade própria

O enunciado passou a exibir `QUESTÃO N` dentro do card. Quando a questão é um retorno de pulo, o marcador informa `RETORNO`. Isso separa visualmente contexto, comando e alternativas.

### 5. Alternativas em modo concentração

As alternativas receberam acabamento mais neutro e menos bordas luminosas. Antes da confirmação, a opção marcada passa a possuir `selectionState="selected"`, fornecendo feedback visual do card inteiro, além do radio button.

Após a confirmação, o estado de seleção é limpo e os estados `correta`/`errada` continuam assumindo a prioridade visual normal.

### 6. Barra de ações fixa

`Marcar como dúvida`, `Analisar depois`, `Pular questão`, `Confirmar resposta` e `Próxima questão` foram retirados do conteúdo rolável e passaram para um rodapé operacional fixo. Assim, perguntas ou explicações longas não fazem o botão principal desaparecer abaixo do scroll.

### 7. Integração com o Dashboard Futurista

O tema Futurista ganhou uma camada final específica para o resolvedor, baseada na linguagem do Dashboard Neo:

- fundo principal `#0B111D`;
- cards em cinza-azulado neutro;
- bordas menos luminosas;
- ação principal em azul-violeta;
- progresso na mesma família cromática;
- verde/vermelho reservados para feedback acadêmico;
- botão **Encerrar sessão** tratado como ação secundária de cautela, não como ação principal.

Os temas Claro e Escuro também receberam regras compatíveis para a nova estrutura.

## Compatibilidade preservada

Foram mantidos os comportamentos introduzidos na 0.29.45:

- bateria como janela top-level não modal;
- retorno ao Dashboard sem encerrar a sessão;
- restauração da bateria pelo Dashboard e `Ctrl+Shift+Q`;
- pausa do tempo da questão comum quando a janela é minimizada;
- simulado continua com seu cronômetro próprio;
- Modo Foco permanece independente e restaurável;
- fechamento da janela principal continua tratando a bateria top-level corretamente.

## Validação

- `python -m py_compile main.py tema.py versao.py`: OK.
- `python -m compileall -q .`: OK.
- 7 testes novos de estrutura/tema da versão 0.29.46: OK.
- 7 testes de regressão da arquitetura de janelas da 0.29.45: OK.
- `PRAGMA integrity_check`: `ok`.
- `PRAGMA foreign_key_check`: 0 violações.
- `estudos.db` manteve o mesmo SHA-256 do pacote 0.29.45: `649fd003e44bbeab21c3be8218ae9853d2fd7d4081d628b7e7bdf95a661fdb07`.
- Nenhuma alteração de schema.

## Validação visual pendente

O ambiente possui PySide6 6.11.2 e permitiu validar código, estrutura, regressão e banco. A conferência visual final ainda deve ser feita manualmente no Windows após executar `atualizar_exe.bat`.
