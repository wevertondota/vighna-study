# VighnaStudy 0.29.33 — alinhamento horizontal do splash

## Objetivo
Corrigir a sensação de composição "diagonal" do splash 0.29.32, em que o cabeçalho permanecia visualmente mais à esquerda que o card, enquanto o rodapé ficava centralizado na janela. O refinamento deveria preservar a barra viva, o progresso real e o processo externo do splash.

## Diagnóstico visual
A versão 0.29.32 já havia melhorado a distribuição vertical, mas ainda mantinha três centros visuais distintos:
1. cabeçalho (`logo + VighnaStudy`) puxado para a esquerda;
2. card de progresso ocupando outra massa visual;
3. assinatura centralizada na largura total da janela.

Isso gerava a percepção de que os elementos não pertenciam ao mesmo conjunto.

## Solução implementada
Foi adotado um **contêiner central único** para a composição do splash.

### Alterações aplicadas
- criado um widget central com largura fixa de **470 px**;
- esse contêiner passa a concentrar:
  - cabeçalho;
  - card de carregamento;
  - assinatura `motor de inteligência Vighna`;
- o contêiner completo é centralizado horizontalmente na janela;
- o card deixa de começar no eixo do título e passa a compartilhar o mesmo centro visual do cabeçalho e do rodapé;
- mantidos os espaçamentos gerais da versão anterior, com pequenos ajustes internos:
  - `20 px` entre cabeçalho e card;
  - `24 px` entre card e assinatura.

## Preservado
Nenhum comportamento funcional do splash foi removido. Permanecem:
- processo externo do splash;
- barra viva com shimmer;
- pulso suave;
- progresso real;
- suavização de avanço;
- fallback local em `JanelaInicializacao`.

## Arquivos alterados
- `startup_splash.py`
- `main.py`
- `versao.py`
- `test_startup_splash_alinhamento_0_29_33.py`

## Versão
- `VIGHNA_VERSION = "0.29.33"`
- `VIGHNA_BUILD = "startup-splash-alinhamento-horizontal-v1"`
- `VIGHNA_SCHEMA = 23`

## Banco de dados
Nenhuma alteração no banco.
- `estudos.db` SHA-256: `6e73df5942723106f9347b949a1b6cd41f655b58bada1d416b35028fd9a9d1fd`

## Validação executada
- `python -m py_compile main.py startup_splash.py versao.py test_startup_splash_alinhamento_0_29_33.py`: OK
- `python -m unittest test_startup_splash_alinhamento_0_29_33.py`: **7/7 OK**

## Observação
Este ambiente não possui PySide6 para inspeção visual direta. Portanto, a confirmação final da percepção estética deve ser feita no seu Windows, executando o projeto real.
