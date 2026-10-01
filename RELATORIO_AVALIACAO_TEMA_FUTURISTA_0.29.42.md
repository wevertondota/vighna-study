# Avaliação do tema Futurista — VighnaStudy 0.29.42

Checkpoint analisado: `VighnaStudy_checkpoint_2026-10-01_00-33-45.zip`

## Conclusão preliminar

O tema Futurista é um fator plausível de custo no startup, mas ainda não há evidência suficiente para classificá-lo como gargalo principal. A atualização 0.29.42 não alterou `main.py` nem `tema.py` em relação ao checkpoint 0.29.41; portanto, o comportamento de aplicação do tema permaneceu igual.

A atualização adicionou/refinou a infraestrutura de microtemas e elevou o schema de 23 para 24. O banco passou de aproximadamente 35,7 MB para 37,7 MB, mas `criar_banco()` continuou barato no ambiente de análise (mediana próxima de 12 ms). Isso não indica que a nova atualização, por si só, tenha criado um novo gargalo de abertura.

## Tamanho dos stylesheets

| Tema | Caracteres | Linhas | Blocos de regras | Seletores aproximados |
|---|---:|---:|---:|---:|
| Claro | 210.696 | 8.380 | 1.366 | 1.801 |
| Escuro | 182.243 | 7.281 | 1.205 | 1.542 |
| Futurista | 308.665 | 11.789 | 1.950 | 2.591 |

O Futurista é formado pelo stylesheet Escuro mais uma camada adicional de aproximadamente 126 mil caracteres.

Foram contados aproximadamente 556 seletores descendentes no Futurista, contra 292 no Escuro e 425 no Claro. Seletores descendentes e uma grande quantidade de regras aumentam o trabalho potencial de correspondência/polimento do Qt quando muitos widgets são criados.

## O que NÃO é o problema

A geração da string do stylesheet em Python é praticamente irrelevante:

- Claro: ~0,07 ms de mediana;
- Escuro: ~0,05 ms;
- Futurista: ~0,17 ms.

Portanto, se o tema estiver afetando a abertura, o custo não está em `stylesheet_futurista()` montar o texto. O custo estará em `QApplication.setStyleSheet()` e, principalmente, no trabalho do Qt ao estilizar os widgets criados posteriormente.

## Ordem de aplicação no startup

O fluxo atual faz o seguinte:

1. cria `QApplication`;
2. constrói `SistemaEstudos`;
3. cria inicialmente o Dashboard;
4. aplica o stylesheet global;
5. inicia o pré-carregamento completo;
6. constrói Central, Estatísticas, Relatórios e demais telas já com o QSS global ativo;
7. só então exibe a janela principal.

O código já evita um problema importante: o stylesheet é aplicado uma única vez depois que o Dashboard inicial foi montado. Porém, como todo o restante é pré-carregado depois dessa aplicação, o Futurista ainda pode aumentar o custo de construção das telas secundárias.

Isso é especialmente relevante na Central, que contém milhares de linhas e dezenas de milhares de itens gráficos.

## Comparação com 0.29.41

`main.py` e `tema.py` são idênticos entre os checkpoints 0.29.41 e 0.29.42. Assim, qualquer diferença de startup entre essas versões não deve ser atribuída a uma mudança do tema.

## Teste decisivo

Para decidir com dados reais, o benchmark deve executar o mesmo pré-carregamento completo nas mesmas condições em três modos:

- Futurista;
- Claro;
- sem QSS global.

O teste deve medir separadamente:

- imports/bootstrap;
- criação de `QApplication`;
- construtor inicial + Dashboard + aplicação do tema;
- Dashboard;
- Disciplinas;
- Central;
- Resumo;
- Calendário;
- Sessão;
- Estatísticas;
- Relatórios;
- primeiro paint da janela;
- total até a interface pronta.

Foi preparado `benchmark_startup_temas.py` para fazer esse teste no Windows usando uma cópia temporária do projeto. O banco original não é alterado. O script restaura uma cópia limpa do `estudos.db` antes de cada rodada e gera CSV/JSON com as medições.

## Critério de decisão sugerido

A interpretação deve usar a diferença entre as medianas, não uma única execução.

- diferença pequena entre Futurista e Claro/sem QSS: tema não merece prioridade;
- diferença relevante concentrada no construtor ou nas telas com muitos widgets: otimizar QSS/construção visual;
- tempos semelhantes nos três modos: priorizar SQL, N+1, duplicidades, Central e relatórios;
- Futurista muito mais lento e sem QSS muito mais rápido: há justificativa técnica para refatorar o stylesheet mantendo o mesmo visual.

## Observação sobre o ambiente de análise

O runtime PySide6 não está disponível no ambiente usado para inspecionar o checkpoint e a rede está indisponível para instalá-lo. Por isso, foi possível medir banco, estrutura e geração de QSS, mas não executar aqui o `QApplication.setStyleSheet()` real. Essa parte precisa ser medida no Windows onde o Vighna roda.
