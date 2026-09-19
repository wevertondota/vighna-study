# RELATÓRIO — AJUSTE DO CTB NA IMPORTAÇÃO VPQ 1.1

Data: 18/09/2026  
Versão: 0.25.1  
Build: `ctb-capitulos-importacao`  
Schema: 18 (inalterado)

## 1. Objetivo

Adequar o VighnaStudy à estrutura real do Código de Trânsito Brasileiro (CTB) durante a importação de questões. No CTB, a classificação principal usada pelo sistema é o capítulo legal; o campo Título não se aplica.

## 2. Nomenclatura do CTB

A disciplina passa a usar como nome canônico:

`Código de Trânsito Brasileiro`

A sigla oficial de uso no sistema permanece:

`CTB`

Para exibição contextual, o importador utiliza:

`Código de Trânsito Brasileiro (CTB)`

Foram preservados aliases estruturais para as três formas. Assim, arquivos e chamadas que utilizem `CTB`, `Código de Trânsito Brasileiro` ou `Código de Trânsito Brasileiro (CTB)` resolvem para a mesma disciplina.

O banco existente foi migrado sem troca de identidade: a disciplina permaneceu com ID 10 e seus relacionamentos foram preservados.

## 3. Estrutura do CTB

O banco real possui 22 conteúdos do CTB cadastrados no nível estrutural `topicos`, e esses conteúdos correspondem aos capítulos legais do Código.

Não existem capítulos aninhados (`capitulos_topico`) para essa disciplina. Portanto, na interface do CTB:

- o capítulo legal é tratado como a classificação principal;
- o nível Título é removido da experiência de importação;
- não é criado um segundo nível artificial apenas para adaptar o CTB ao modelo usado em outras disciplinas.

## 4. Importação VPQ 1.1

Quando a disciplina reconhecida é CTB:

- `CAPÍTULO` é usado para localizar o conteúdo estrutural;
- `TÍTULO` deixa de ser obrigatório e não é exibido como classificação do CTB;
- arquivos VPQ antigos com classificação em Título ainda possuem fallback de compatibilidade, sem tornar essa forma o padrão atual;
- o cabeçalho de auditoria mostra `Disciplina: Código de Trânsito Brasileiro (CTB)` e `Capítulo: ...`;
- mensagens de vínculo e erro falam em capítulo, e não em título;
- a ajuda do importador explica que o campo Título não se aplica ao CTB.

O protocolo VPQ e o modelo de importação também foram documentados com a regra específica do CTB.

## 5. Campo superior de classificação

Foi adicionado/adequado o controle de `Capítulo padrão` na área superior da importação.

Para CTB:

- o controle principal é rotulado `Capítulo padrão`;
- ele contém somente os capítulos do CTB disponíveis no perfil ativo;
- o controle de segundo nível fica oculto porque não se aplica;
- a seleção padrão é propagada para as questões da tabela.

Para as demais disciplinas, permanece a estrutura `Título padrão` + `Capítulo padrão`.

## 6. Tabela de questões

Para CTB:

- a coluna `Título` passa a ser `Capítulo`;
- a coluna de capítulo aninhado é ocultada;
- os combos apresentam apenas os capítulos do CTB;
- o rótulo da disciplina nesses combos usa `Código de Trânsito Brasileiro (CTB)`;
- questão sem classificação recebe status `Sem capítulo`;
- a importação exige capítulo, e não `título/capítulo`.

As regras de Título/Capítulo das demais disciplinas permanecem inalteradas.

## 7. Migração do banco existente

Antes do ajuste, o banco real possuía:

- disciplina ID 10: `CTB`;
- 22 tópicos associados;
- 0 capítulos aninhados para o CTB.

Após a migração:

- disciplina ID 10: `Código de Trânsito Brasileiro`;
- os mesmos 22 tópicos continuam associados;
- os relacionamentos de concurso permanecem preservados;
- `CTB` continua resolvendo para ID 10 como alias;
- `Código de Trânsito Brasileiro (CTB)` também resolve para ID 10.

Não houve migração destrutiva nem alteração de schema.

## 8. Compatibilidade

Foram atualizados scripts legados que dependiam do nome exato da disciplina.

Chamadas estruturais que ainda utilizam a sigla `CTB` continuam válidas por alias, permitindo compatibilidade com dados e rotinas anteriores.

## 9. Testes

Foi criado `test_ctb_importacao.py` cobrindo:

- banco novo com nome oficial;
- alias `CTB`;
- alias `Código de Trânsito Brasileiro (CTB)`;
- migração de banco legado sem mudança de ID;
- resolução de capítulo do CTB como conteúdo estrutural;
- VPQ do CTB sem Título;
- aviso específico quando o CTB não informa Capítulo.

Resultado final:

- 168 testes `unittest`: OK;
- `testes_smoke.py`: OK;
- `py_compile`: OK;
- `PRAGMA integrity_check`: `ok`;
- `PRAGMA foreign_key_check`: 0 violações.

Os `ResourceWarning` já existentes em alguns testes de fila/conexões não causaram falha e não foram introduzidos por este ajuste.

## 10. Limitação de validação visual

O ambiente de validação não possui PySide6 instalado, portanto a janela real não pôde ser aberta aqui. A lógica, parser, banco e regressões foram validados automaticamente. A conferência visual final deve ser feita no Windows do usuário.

## 11. Resultado esperado na tela

Em um VPQ do CTB, a interface deve apresentar conceitualmente:

`Disciplina: Código de Trânsito Brasileiro (CTB) • Capítulo: Capítulo I: Disposições Preliminares`

Na área superior:

`Capítulo padrão`

Na tabela:

`Capítulo`

Sem coluna funcional de Título para o CTB.
