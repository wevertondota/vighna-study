# Nova execução do G6-B1 — Painel V3.1.16

## Antes de executar

1. Use uma pasta exclusiva do Painel V3.1.16, fora da instalação principal.
2. Não copie `estudos.db`, executáveis ou arquivos pessoais para o VighnaLab.
3. Confirme que o Windows Sandbox está instalado e que não existe outra instância aberta.
4. Em **Configurações**, selecione somente o Python do `Ambiente_Qt_Homologador`.
5. Mantenha G6-B2, G7 e a instalação do M2 RC2 como pendentes/proibidos.

## Execução pela interface

1. Abra `ABRIR_PAINEL_HOMOLOGACAO.cmd`.
2. Confirme que a interface mostra `PAINEL V3.1.16`.
3. Acesse **Executar testes**.
4. Execute **G6-B1** e aguarde as compilações R1D, RC2 e GUEST.
5. Não feche o Windows Sandbox enquanto os cenários estiverem em andamento.
6. Aguarde o painel informar o caminho do ZIP de diagnóstico.

## Resultado esperado

O resultado somente é satisfatório se o relatório autenticado contiver:

- status geral `PASSOU_B1_EXECUTAVEIS_REAIS`;
- três cenários completos;
- sucesso: `PASSOU_B1_TRANSACAO_REAL`, checkpoint `installed`;
- falha de compilação: `PASSOU_B1_ROLLBACK_REAL`, sem checkpoint de commit;
- falha pós-commit: `PASSOU_B1_ROLLBACK_REAL`, checkpoint `recovered`;
- `banco_qa_preservado=true` nos três cenários;
- smokes R1D e final estáveis;
- transação sem alteração lógica ou física do banco;
- `instalacao_autorizada=false` e `gate_g6_aprovado=false`.

O ZIP deve incluir `RESULTADO_G6B1.json`, `DIAGNOSTICO_SQLITE_G6B1.json` e os
manifestos SHA-256. Se qualquer cenário falhar, a evidência parcial indicará
`operacao_falhou` e `primeira_divergencia`; preserve o laboratório e o ZIP.

## Limites

Passar no G6-B1 não aprova o Gate G6 e não autoriza instalar o RC2. G6-B2 e G7
continuam obrigatórios. Nunca execute esses testes sobre o banco pessoal ou a
instalação principal do VighnaStudy.
