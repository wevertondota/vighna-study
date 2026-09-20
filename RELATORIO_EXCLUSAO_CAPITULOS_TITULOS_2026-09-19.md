# VighnaStudy — Exclusão contextual de títulos e capítulos

**Versão:** 0.28.9  
**Build:** `chapter-title-delete-actions`  
**Schema:** 20  
**Base utilizada:** checkpoint 0.28.8 enviado em 19/09/2026 às 16:51.

## Objetivo
Permitir que o botão **Excluir** da tela da disciplina funcione conforme a linha selecionada, tanto para títulos/tópicos quanto para capítulos internos.

## Comportamento implementado

### Quando um título/tópico está selecionado
O comportamento destrutivo existente foi mantido e explicitado. A confirmação informa que o título/tópico e seus dados associados serão removidos.

### Quando um capítulo está selecionado
O botão **Excluir** passa a ficar habilitado. A confirmação mostra quantas questões estão classificadas naquele capítulo.

A exclusão do capítulo **não apaga as questões**. As questões permanecem vinculadas ao título/tópico pai e passam a ficar sem capítulo (`capitulo_id = NULL`) até eventual reclassificação.

Após a exclusão, a tela retorna ao título/tópico pai para manter o contexto do usuário.

## Capítulos padrão automáticos
Direito Penal possui capítulos padrão que podem ser materializados automaticamente. Para impedir que um capítulo explicitamente excluído pelo usuário reapareça na próxima atualização da tela, foi adicionada a tabela:

`capitulos_padrao_excluidos`

Ela registra somente a decisão de exclusão de capítulos padrão. Se o usuário recriar manualmente o mesmo capítulo, o bloqueio é removido.

## Compatibilidade
A rotina de exclusão zera explicitamente `questoes.capitulo_id` antes de remover o capítulo. Isso preserva as questões inclusive em bancos legados cuja coluna de capítulo tenha sido adicionada por migração sem a FK `ON DELETE SET NULL` original.

## Validação
- `python -m py_compile main.py banco.py versao.py` — OK
- 6 testes direcionados de exclusão — OK
- suíte completa: **231 testes** — OK
- smoke tests — OK
- migração do banco atual em cópia — OK
- `PRAGMA integrity_check` — `ok`
- `PRAGMA foreign_key_check` — vazio

## Banco de dados
O pacote de atualização não inclui `estudos.db`, para não substituir os dados atuais do usuário. A nova tabela do schema 20 é criada automaticamente na próxima inicialização do VighnaStudy.
