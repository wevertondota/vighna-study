# VighnaStudy 0.29.11 — Questões Certo/Errado (CESPE/Cebraspe)

## Objetivo

Adicionar `CERTO_ERRADO` como formato nativo de questão, preservando a arquitetura atual de questões, tentativas, cobertura, revisões e inteligência acadêmica.

## 1. Banco de dados

A tabela `questoes` passa a possuir o campo:

```text
tipo_questao
```

Valores canônicos:

```text
MULTIPLA_ESCOLHA
CERTO_ERRADO
```

A migração é automática. Questões antigas recebem `MULTIPLA_ESCOLHA`, sem alteração de enunciado, alternativas, gabarito, histórico ou IDs.

Questões C/E usam internamente duas respostas canônicas (`C` e `E`), com textos `Certo` e `Errado`. Isso permite reaproveitar o mesmo motor de tentativas e histórico sem criar um segundo sistema acadêmico.

## 2. VPQ 1.1

O importador aceita:

```text
FORMATO: CERTO-ERRADO
```

Modelo:

```text
QUESTÃO 1
Julgue o item a seguir.

GABARITO: CERTO
EXPLICAÇÃO: ...
```

Também aceita `C`, `E`, `CERTO` e `ERRADO` como gabarito de entrada e salva internamente de forma canônica.

Não são necessárias alternativas artificiais `A) Certo` / `B) Errado`.

## 3. Editor de questões

O editor ganhou o campo **Formato**:

- Múltipla escolha;
- Certo / Errado.

Em `CERTO_ERRADO`, os campos A–E são ocultados e o gabarito passa a ser escolhido diretamente entre **CERTO** e **ERRADO**.

## 4. Resolução e revisão

Ao resolver uma questão C/E:

- aparecem apenas os botões **CERTO** e **ERRADO**;
- não aparece representação artificial por letras;
- a ferramenta de eliminação de alternativas é ocultada;
- feedback, revisão pós-bateria e visualização histórica usam CERTO/ERRADO.

O registro acadêmico continua sendo `acertou`, `errou` ou `pulou`, como nas demais questões.

## 5. Central de Questões

Foi adicionado o filtro **Formato**:

- Todos os formatos;
- Múltipla escolha;
- Certo / Errado.

O tipo também participa da pesquisa e da edição.

## 6. Sessões e algoritmo

As sessões configuráveis podem filtrar:

- todos os formatos;
- somente múltipla escolha;
- somente Certo/Errado.

A seleção adaptativa e o algoritmo acadêmico tratam `CERTO_ERRADO` como questão normal para cobertura, domínio, erros recentes, revisões, dificuldade e prioridade.

## 7. Simulado

O Simulado ganhou dois controles independentes:

**Formato das questões**
- Todos os formatos;
- Múltipla escolha;
- Certo / Errado.

**Pontuação**
- Normal: `+1` acerto, `0` erro, `0` branco;
- Cebraspe: `+1` acerto, `-1` erro, `0` branco.

A pontuação do edital é calculada apenas para a nota do simulado. Ela não altera Domínio, cobertura ou a interpretação acadêmica de um erro.

O resumo também pode mostrar desempenho separado por formato.

## 8. Compatibilidade

- Não acompanha `estudos.db`.
- A migração de schema ocorre ao abrir o programa atualizado.
- Questões existentes permanecem múltipla escolha.
- O histórico existente é preservado.
- As regras de pulo e revisão da 0.29.10 permanecem ativas.

## 9. Validação realizada

- `python -m compileall -q .`: OK.
- `python testes_smoke.py`: OK.
- `python test_ciclo_estudo.py`: 3/3 OK.
- teste do parser VPQ C/E: OK.
- teste de migração/criação/leitura de questão C/E: OK.
- teste de filtro C/E no Simulado Equilibrado: OK.
- teste de filtro C/E no Simulado Personalizado: OK.
- teste de seleção adaptativa C/E: OK.
- teste de registro de tentativa/histórico C/E: OK.

O ambiente de validação não possui PyQt6 instalado, portanto a janela gráfica não pôde ser aberta aqui. O código da interface compila normalmente e os fluxos não gráficos acima foram executados sobre uma cópia do banco.

## Versão

- VighnaStudy: `0.29.11`
- Build: `question-format-certo-errado-v1`
- Schema: `21`
