# RELATÓRIO — IMPORTAÇÃO DE QUESTÕES POR TXT

Data: 2026-09-19  
Versão: **0.28.2**  
Build: `txt-question-import`  
Schema: **19**

## Objetivo
Adicionar à Central de Importação do VighnaStudy uma quarta origem de questões: **arquivo TXT (.txt)**, mantendo a mesma conferência e as mesmas proteções já utilizadas nas importações por PDF e texto colado.

## Fluxo implementado
A Central de Importação passa a oferecer quatro opções em uma grade 2x2:

1. PDF
2. Arquivo TXT
3. Texto colado
4. CSV

Ao selecionar **Arquivo TXT**, o Vighna:

1. abre o seletor de arquivos limitado a `.txt`;
2. lê o conteúdo sem dependências externas;
3. identifica codificações comuns do Windows;
4. envia o texto ao mesmo analisador estrutural usado pelo VPQ/PDF/texto colado;
5. abre a tela comum de conferência;
6. verifica gabarito, classificação e duplicidade;
7. cria backup antes da gravação definitiva;
8. atualiza a Central de Questões após uma importação bem-sucedida.

## Codificações suportadas
O novo leitor reconhece:

- UTF-8;
- UTF-8 com BOM;
- UTF-16 com BOM;
- UTF-16 LE/BE sem BOM em arquivos compatíveis;
- Windows-1252 (ANSI comum no Windows);
- ISO-8859-1 como fallback.

A codificação detectada é mostrada na tela de conferência do TXT.

## Compatibilidade com VPQ 1.1
O TXT reutiliza o analisador já existente. Portanto, um arquivo `.txt` contendo o protocolo:

`VIGHNA PDF — VPQ 1.1`

segue a mesma validação estrutural dos VPQs já importados por PDF ou texto colado, incluindo disciplina, título/capítulo quando aplicável, fonte, quantidade, gabaritos e bloqueios de estrutura.

## Segurança
- Nenhuma questão é gravada assim que o TXT é selecionado.
- A conferência permanece obrigatória.
- Duplicidades continuam sendo verificadas.
- Antes da gravação é criado backup com o motivo `antes_importar_questoes_txt`.
- Arquivos vazios ou incompatíveis com texto puro são rejeitados.

## Arquivos alterados
- `main.py`
- `versao.py`

## Arquivos novos
- `importador_txt.py`
- `test_importador_txt.py`
- `test_importacao_txt_integracao.py`
- `RELATORIO_IMPORTACAO_TXT_2026-09-19.md`

## Validação
- `python -m py_compile ...` ✅
- testes específicos do TXT: **9/9** ✅
- suíte completa: **212 testes** ✅
- `testes_smoke.py`: **VighnaStudy 0.28.2: testes smoke OK** ✅
- SQLite `PRAGMA integrity_check`: **ok** ✅
- SQLite `PRAGMA foreign_key_check`: **sem violações** ✅

## Observação de interface
O ambiente de validação não possui PySide6 instalado, portanto a renderização gráfica da nova grade 2x2 não pôde ser aberta localmente. A integração foi validada por sintaxe, testes automatizados e inspeção estrutural. A conferência visual deve ser feita no Windows do usuário.
