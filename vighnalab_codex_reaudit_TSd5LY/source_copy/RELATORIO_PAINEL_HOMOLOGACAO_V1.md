# VighnaStudy — Painel Gráfico de Homologação V1

Data: 12/10/2026
Entrega: ferramenta portátil de testes; **NÃO INSTALAR NO VIGHNASTUDY**.

## Objetivo
Executar o homologador V1.1 existente pelo Windows, com interface Tkinter
e sem necessidade de comandos CMD, salvo o duplo clique no iniciador.

## Operação
- `ABRIR_PAINEL_HOMOLOGACAO.cmd` inicia `painel_homologacao.py` com Python 3.13.
- O painel sugere o ambiente Qt já verificado pelo usuário ou permite escolher outro.
- Grava o caminho selecionado em `painel_configuracao_local.json` na própria
  pasta. Essa configuração pessoal NÃO está incluída no ZIP de distribuição.
- `Executar testes Qt + SQLite` chama o motor V1.1 em subprocesso isolado.
- `Testes + compilar EXE` tenta também PyInstaller com o `.spec` R1D,
  sem abrir o executável ou atualizar o programa principal.
- Registro de etapas é apresentado ao vivo. Quando há resultados, mostra
  o caminho exato e oferece botão `Abrir pasta do resultado`.
- Em caso de saída antecipada do motor sem ZIP, cria ZIP de diagnóstico
  do painel, usando somente log resumido e caminho do perfil substituído.

## Integridade e escopo
- Os arquivos do homologador V1.1 foram preservados sem alterações;
  o verificador original de hashes continua funcional.
- O programa não executa nem carrega o banco pessoal.
- O programa não tenta transmitir dados diretamente ao ChatGPT.
- O usuário deve anexar manualmente o ZIP resultante.
- M2 RC2 permanece sem autorização de instalação.
- M3 permanece experimental e não integrado.

## Testes realmente executados no Linux
- 13/13 testes do painel, incluindo descoberta do Python, seleção de
  resultado, geração de ZIP emergencial e leitura do resumo.
- 19/19 testes de guardas do homologador V1.1.
- 82/82 testes do atualizador e do Gate 6, com dados sintéticos.
- Selftest do pacote de fontes V1.1 aprovado.
- Compilação sintática dos módulos Python do kit.

## Testes ainda não executados
A interface Tkinter com backend Windows e os botões reais dependem
da primeira execução no Windows. Tampouco foi compilado o EXE nativo
com PyInstaller nesta entrega. Nunca declarar conclusão dessas etapas
sem um relatório Windows produzido pelo usuário.

## Como retomar
Baixar e extrair o ZIP, dar duplo clique em
`ABRIR_PAINEL_HOMOLOGACAO.cmd`, executar testes e enviar o ZIP
`RESULTADOS_HOMOLOGACAO_WINDOWS_*.zip` ou o diagnóstico criado.
