# VighnaStudy 0.29.58 — editor inline da explicação durante a bateria

## Objetivo
Permitir corrigir ou complementar a explicação de uma questão sem sair da bateria.

## Comportamento
1. A resposta é confirmada normalmente.
2. O card de feedback passa a exibir a seção **Explicação** com um ícone de lápis.
3. Ao acionar o lápis, a explicação vira um editor de texto dentro do próprio card.
4. O usuário pode corrigir qualquer trecho ou acrescentar uma anotação.
5. **Salvar** grava a nova explicação na própria questão e atualiza imediatamente o texto exibido.
6. **Cancelar** descarta a edição ainda não salva.
7. Enquanto o editor estiver aberto, **Próxima questão** fica desabilitado para impedir perda acidental do texto.

## Persistência
Foi criada uma operação específica `atualizar_explicacao_questao`, que altera apenas:
- `questoes.explicacao`;
- `questoes.atualizado_em`.

Não houve alteração de schema.

## Integração com teclado
Enquanto o editor inline está aberto, o filtro global do resolvedor deixa o teclado sob controle do campo de texto e dos botões de edição. Assim, Enter, setas e Espaço não executam comandos da bateria durante a edição. Ao salvar ou cancelar, o fluxo normal da bateria é retomado e o foco volta para **Próxima questão**.

## Temas
Foram incluídos estilos próprios para o editor, lápis, Salvar e Cancelar nos temas:
- Claro;
- Escuro;
- Futurista.

## Validação
- `py_compile`: aprovado para `main.py`, `banco.py`, `tema.py` e `versao.py`.
- Teste específico 0.29.58: **8/8** aprovado.
- Regressão do fluxo de teclado 0.29.56/0.29.57: **8/8** aprovado.
- Teste da função de persistência em cópia temporária do banco: aprovado.
- `PRAGMA integrity_check` do banco original: **ok**.
- `PRAGMA foreign_key_check`: **0 violações**.

## Versão
- Versão: **0.29.58**
- Build: `inline-explanation-editor-v1`
- Schema: **25**
