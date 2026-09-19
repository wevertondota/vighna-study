# VighnaStudy — Otimização de responsividade da área Estatísticas

Data: 18/09/2026

Versão resultante: `0.24.1`
Build: `responsividade-estatisticas-lazy`
Schema: `18` (sem alteração)

## Problema observado

A abertura da área Estatísticas chamava `atualizar_estatisticas()` antes de trocar a tela visível. Esse método recalculava e redesenhava, em uma única ação, conteúdo de todas as abas: Algoritmo, Disciplinas, Pontos fracos, Revisões recentes, Histórico, Tendências e Progresso.

No banco do checkpoint do Passo 8, uma medição isolada das principais fontes de dados apresentou aproximadamente:

- disciplinas: 7 ms;
- métricas globais: 6 ms;
- pontos fracos: 19 ms;
- revisões recentes: 1 ms;
- histórico de 30 dias: 124 ms em média;
- tendências de 30 dias: 103 ms em média;
- progresso: 30 ms em média.

Somadas, apenas essas consultas/análises representam cerca de 290 ms em média, sem contar o Laboratório, construção de tabelas, gráficos, estilos e repaint do Qt.

## Alterações realizadas

### 1. Navegação antes do cálculo

`abrir_estatisticas()` agora mostra a tela primeiro e agenda a atualização para o ciclo seguinte do Qt. Foi usado um atraso curto de 15 ms para permitir o repaint da navegação antes das consultas mais pesadas.

### 2. Carregamento preguiçoso por aba

A área Estatísticas deixou de recalcular todas as abas ao mesmo tempo. Somente a aba atualmente visível é atualizada.

Abas controladas:

- Histórico;
- Algoritmo;
- Disciplinas;
- Pontos fracos;
- Revisões recentes;
- Tendências;
- Progresso.

Ao trocar de aba, somente a aba selecionada é carregada se estiver marcada como desatualizada.

### 3. Estado sujo/limpo

Foi criado `estatisticas_lazy.py`, independente de Qt, para controlar:

- abas que precisam de atualização;
- resumo geral desatualizado;
- troca de concurso;
- tempos locais de atualização para diagnóstico.

Uma aba já carregada não é recalculada ao voltar para ela sem alteração de dados.

### 4. Invalidação por evento

Alterações acadêmicas agora marcam as estatísticas como desatualizadas sem executar cálculos pesados imediatamente em outra tela.

Tratamento específico:

- foco: invalida Histórico e Tendências;
- recomendações/decisões: invalida Algoritmo;
- questões, revisões e alterações gerais: invalidam o conjunto estatístico pertinente.

Também são invalidados os caches temporários associados a Histórico, Tendências e Progresso.

### 5. Cache curto de análises caras

Foram adicionados caches curtos para:

- resumo estatístico;
- Histórico;
- Tendências;
- Pontos fracos;
- Revisões recentes.

O cache é invalidado quando os dados relevantes mudam. O cache de Progresso já existente foi integrado à nova política de invalidação.

### 6. Atualização manual

O botão `Atualizar dados` continua disponível, mas agora força apenas:

- resumo;
- aba atualmente selecionada.

Ele não recalcula abas invisíveis.

### 7. Acessos diretos ao Progresso

Atalhos do Dashboard que abrem:

- Progresso do edital;
- previsão;
- alertas;

agora selecionam primeiro a aba Progresso e usam o mesmo mecanismo preguiçoso, em vez de recalcular todas as Estatísticas antes da navegação.

### 8. Redução de repaint de tabelas

Durante preenchimentos maiores, updates e sinais das tabelas são temporariamente suspensos em pontos críticos, incluindo tabelas de Progresso, Disciplinas, Pontos fracos e Revisões recentes.

### 9. Mudança de dia/perfil

A troca do concurso ativo ou a mudança do dia civil invalida automaticamente as estatísticas para impedir reutilização indevida de dados antigos.

## Resultado esperado

Antes:

`clique → recalcula praticamente toda Estatística → monta tabelas/gráficos → mostra a tela`

Agora:

`clique → mostra a tela → atualiza apenas resumo + aba visível`

Ao alternar para uma aba ainda não visitada, somente aquela aba é calculada. Ao retornar a uma aba já atualizada e sem mudança de dados, não há recálculo pesado.

## Testes

Foram adicionados:

- `test_estatisticas_lazy.py` — 5 testes;
- `test_responsividade_estatisticas.py` — 5 testes de regressão estrutural.

Resultado da suíte completa após as alterações:

- `126/126` testes `unittest`: OK;
- `testes_smoke.py`: OK;
- `py_compile`: OK;
- `PRAGMA integrity_check`: `ok`;
- `PRAGMA foreign_key_check`: 0 violações.

## Limitação do ambiente de validação

O ambiente usado para a alteração não possui `PySide6`, portanto não foi possível executar a janela gráfica real aqui. A lógica sem Qt, compilação, regressões e banco foram validados. O teste perceptivo final deve ser feito no Windows do usuário executando o programa normalmente.

## Próximo critério

Antes de adicionar o Mapa de Domínio, testar no Windows:

1. abertura de Estatísticas;
2. troca entre Histórico, Disciplinas, Tendências e Progresso;
3. retorno para uma aba já aberta;
4. abertura do Progresso a partir do Dashboard.

Se ainda houver travamento perceptível em uma aba específica, medir essa aba isoladamente antes de introduzir threads ou processamento assíncrono mais complexo.
