# VighnaStudy 0.29.34 — Futurista Neo

## Objetivo
Consolidar o tema Futurista como a principal direção visual do Dashboard, modernizando cores, superfícies, botões e hierarquia sem alterar o módulo Foco, que foi mantido como estava.

## Direção visual
A revisão segue uma linha de **futurismo limpo / cockpit premium**:
- fundo navy mais profundo;
- menos sensação de "grade de caixas";
- bordas mais discretas;
- contraste por superfície, não por contorno em excesso;
- azul/ciano reservado para estrutura, inteligência e ações principais;
- verde somente para estados positivos/concluídos;
- laranja somente para atenção;
- tipografia branca e azul-acinzentada com hierarquia mais clara.

## Alterações implementadas

### Topo do Dashboard
- `dashboardTopBar` recebeu gradiente navy discreto e borda menos agressiva;
- barra de busca ficou mais escura em repouso e acende apenas no hover;
- `Central de Questões` ganhou tratamento de ação forte em azul-petróleo/ciano;
- botão de configurações passou a ter superfície própria, mais compacta e coerente com o topo;
- módulo `PERFIL ATIVO` ganhou fundo mais profundo, borda suave e combo mais limpo;
- botões secundários (`subtleButton`) receberam um padrão único de controle secundário.

### Planejamento de hoje
- card principal ganhou gradiente escuro suave e borda reduzida;
- ícone, título, data e métrica principal tiveram hierarquia reforçada;
- barra de progresso passou a usar gradiente azul-ciano;
- bloco operacional interno ficou menos "encaixotado";
- chips semanais passaram a seguir semântica consistente:
  - azul/ciano = andamento;
  - verde = concluído;
  - laranja = atenção;
- botão `VER PLANEJAMENTO COMPLETO` foi convertido para um secundário premium.

### Recomendação do algoritmo
- card principal ganhou superfície mais profunda e tecnológica;
- borda menos pesada e mais coerente com o restante do Dashboard;
- ícone e cabeçalho ficaram mais limpos;
- bloco interno `algorithmRecommendationBody` perdeu peso visual;
- CTA `COMEÇAR AGORA` recebeu gradiente azul mais moderno;
- hover do CTA ganhou maior luminosidade sem mudar a identidade;
- botão de ajuda e link explicativo foram refinados.

### Seu progresso
- o card recebeu `cardRole="progress"` para permitir estilização própria sem afetar os cards do Foco;
- superfície, ícone, badge de nível e barra de XP foram modernizados;
- barra de XP passou a usar gradiente azul-ciano;
- botão `Ver conquistas` foi harmonizado com o padrão secundário.

### Cards inferiores e acessos rápidos
- superfícies principais foram uniformizadas;
- bordas ficaram menos dominantes;
- acessos rápidos receberam gradiente leve para reforçar profundidade sem poluição visual.

## Foco preservado
A nova camada `ESTILO_DASHBOARD_NEO_FUTURISTA` não possui seletores para:
- `dashboardFocusPanel`;
- `focusDashboardMainCard`;
- `dashboardFocusPrimaryButton`.

Assim, o módulo Foco permanece visualmente como estava na versão anterior.

## Implementação
Foi criada uma camada final de override:
- `ESTILO_DASHBOARD_NEO_FUTURISTA`

Ela é anexada por último ao stylesheet futurista para assumir prioridade sem reescrever as outras duas famílias de tema (Claro e Escuro).

## Arquivos alterados
- `tema.py`
- `main.py`
- `versao.py`
- `test_dashboard_futurista_neo_0_29_34.py`

## Versão
- `VIGHNA_VERSION = "0.29.34"`
- `VIGHNA_BUILD = "dashboard-futurista-neo-v1"`
- `VIGHNA_SCHEMA = 23`

## Banco
Nenhuma alteração de dados ou schema.

SHA-256 de `estudos.db`:
`6e73df5942723106f9347b949a1b6cd41f655b58bada1d416b35028fd9a9d1fd`

O hash é idêntico ao checkpoint 0.29.33.

## Validação
- `python -m py_compile main.py tema.py versao.py test_dashboard_futurista_neo_0_29_34.py`: OK
- `python -m unittest test_dashboard_futurista_neo_0_29_34.py test_dashboard_inteligencia.py`: **14/14 OK**

Os testes históricos 0.29.28/0.29.29 possuem assertivas de versão e contagem textual específicas das versões antigas e, por isso, não são usados como critério de regressão da 0.29.34.

## Observação de renderização
O ambiente de execução desta edição não possui PySide6 para abrir visualmente a interface. A validação estética final deve ser feita no Windows executando o projeto real.
