# Segunda reauditoria independente — VighnaLab 3.1.53-R1

Data: 15/10/2026  
Escopo: somente `VighnaLab_V3153_R1_CODIGO` e `MANIFESTO_CODEX_V3153_R1.json`.  
Decisão: **NÃO HOMOLOGADO PARA INSTALAÇÃO**. G7 formal, backups reais, rollback sobre dados pessoais, nuvem e instalação principal permaneceram fora de escopo.

## Conclusão executiva

A base recebida é internamente íntegra em relação ao manifesto externo: 60 de 60 arquivos, sem diferenças de tamanho ou SHA-256. Os hashes da fonte original antes e depois da reauditoria são idênticos. Nenhum arquivo do pacote foi editado e nenhuma dependência foi instalada.

Os controles novos de identidade frozen, falha fechada sem `_MEIPASS`, bloqueio de ações externas e persistência fora do bundle funcionaram nos testes executáveis. O resultado focal foi 14 aprovados e 2 não testados por falta de privilégio para symlink real. A bateria geral executou 413 testes: 370 aprovados, 27 erros de ambiente/entradas, 16 pulados, 0 falhas de asserção e 0 timeouts reais.

A entrega não pode ser considerada completa ou homologada. O manifesto interno de entradas declara 21 arquivos, mas apenas 8 estão presentes e 13 estão ausentes. Isso diverge da expectativa de “11 insumos ausentes” dada na ordem de trabalho. Dos 27 erros da bateria, 26 decorrem desses recursos ausentes e 1 decorre da indisponibilidade de uma sessão gráfica Tk apropriada. Não foi inventada aprovação para essas etapas.

## Ambiente e isolamento

- Windows, Python 3.13.15 64-bit.
- Testes executados em cópia descartável sob `%TEMP%`, com `USERPROFILE`, `HOME`, `LOCALAPPDATA`, `TEMP` e `TMP` apontados para perfil isolado.
- `PYTHONDONTWRITEBYTECODE=1` e `PYTHONNOUSERSITE=1`.
- Pacote original usado somente para leitura e hashes.
- VighnaStudy/VighnaLab principal, banco pessoal, backups reais, nuvem e instaladores não foram abertos.

## Integridade da entrega

`MANIFESTO_CODEX_V3153_R1.json` foi reproduzido integralmente:

- arquivos declarados: 60;
- arquivos encontrados: 60;
- ausentes ou extras: 0;
- hashes divergentes: 0;
- tamanhos divergentes: 0;
- fonte original antes/depois: idêntica;
- cópia de laboratório antes/depois: idêntica.

SHA-256 comprova identidade de bytes em relação ao valor de referência. Ele **não é assinatura digital do EXE**, não autentica o publicador e não substitui Authenticode ou cadeia de confiança.

## Reconciliação V3.1.53-R1

Comando reproduzido: `python -m unittest -v test_reconciliacao_v3153_r1`.

Resultado: 16 testes, 14 aprovados, 2 pulados, 0 falhas, 0 erros.

Foram confirmados:

- vínculo entre `PAINEL_VERSAO.json`, versão `3.1.53` e SHA-256 fixo;
- rejeição de adulteração para `3.1.99`;
- rejeição do mesmo JSON reordenado, pois o contrato é de bytes exatos;
- rejeição de recurso ausente;
- falha fechada quando frozen não possui `_MEIPASS`;
- integridade dos três recursos embutidos;
- configuração fora do bundle;
- diagnósticos fora de `APP_ROOT`;
- dossiê G7 no estado persistente;
- guardas de interface e de workers;
- presença dos três recursos no `.spec`;
- rejeição de argumentos extras pelo protocolo filho.

Os dois casos pulados foram os de symlink real, indisponível por `WinError 1314`. Junction real foi exercitada separadamente e rejeitada corretamente.

## Regressões gerais

Resultado: 413 testes em 24,001 s; 370 aprovados, 27 erros, 16 pulados e nenhuma falha de asserção.

Classificação dos 27 erros:

- 26: entradas/evidências auxiliares ausentes;
- 1: `test_gui_v3_smoke`, sem servidor de tela Tk adequado;
- 0: timeout real de subprocesso;
- 0: regressão demonstrada por falha de asserção.

Os testes que injetam `subprocess.TimeoutExpired` passaram e confirmam que timeout não é promovido a aprovação. Isso não equivale a executar os fluxos operacionais bloqueados pelos arquivos ausentes.

Os 16 pulos abrangem symlinks reais sem privilégio, widgets sem Xvfb/sessão adequada, evidência real deliberadamente fora do laboratório e casos condicionais de plataforma. Eles permanecem não testados; não foram contabilizados como aprovação.

## Entradas ausentes

O manifesto interno declara 21 entradas e somente 8 existem. Estão ausentes 13:

1. `EVIDENCIAS_PREPARACAO/TESTES_ATUALIZADOR_82_82.txt`
2. `EVIDENCIAS_PREPARACAO/TESTES_ATUALIZADOR_V1_1_82_82.txt`
3. `EVIDENCIAS_PREPARACAO/TESTES_INTERNOS_18_18.txt`
4. `EVIDENCIAS_PREPARACAO/TESTES_INTERNOS_V1_1_19_19.txt`
5. `insumos/BASE_R1D_SOMENTE_FONTES_QA.zip`
6. `insumos/CANDIDATO_QA_R1D_PARA_M2_RC2_NAO_INSTALAR.zip`
7. `insumos/M2_RC2_FONTE_REFERENCIA_NAO_INSTALAR.zip`
8. `qt/validador_qt_rc2_isolado.py`
9. `testes/test_gate6_casos_borda.py`
10. `testes/test_gate6_spec_compat_estatica.py`
11. `testes/test_gate_direto_r1d_rc2.py`
12. `testes/test_vighna_atualizador.py`
13. `testes/vighna_update_engine.py`

É necessário fornecer exatamente esses arquivos com os hashes declarados antes de considerar G5/G6, as regressões dependentes ou o build como executados.

## Modo frozen e arquivos externos

As entradas de interface para bateria geral, G5-B, G5-C, G6-A, G6-B1 e G6-B2 foram invocadas dinamicamente com `sys.frozen=True`; todas retornaram antes de subprocesso. Os workers `_worker`, `_worker_g5a`, `_worker_g5b`, `_worker_g5c`, `_worker_g6a`, `_worker_g6b` e `_worker_g6b2` também foram chamados diretamente e falharam fechados antes de `Popen`.

Portanto, esses caminhos estão **mitigados por bloqueio** no EXE frozen. Isso não prova execução funcional dos respectivos gates; eles continuam pendentes.

## Persistência e proteção de escrita

Passaram os seguintes ensaios:

- configuração nova em estado persistente equivalente a `%LOCALAPPDATA%\VighnaLab`;
- leitura de configuração antiga e preservação byte a byte quando marcada somente leitura;
- simulação de pasta sem escrita por `PermissionError`, sem sobrescrever destino;
- diagnósticos sob `%TEMP%\VighnaLab_Diagnosticos`;
- dossiê sob estado persistente `VighnaLab\G7_Dossies`;
- junction real detectada e recusada, preservando o alvo;
- nenhum arquivo novo ou alterado no bundle simulado `_MEIPASS`.

Symlink real não foi criado pelo token do teste (`WinError 1314`); as guardas sintéticas passaram, mas esse cenário real continua não testado.

## Spec e recursos do bundle

A inspeção estática do `VighnaLab_QA_V3153_R1.spec` passou e confirmou os três recursos:

- `PAINEL_VERSAO.json` — componente `vighna-panel`, versão `3.1.53`;
- `estado_planejamento_v3.json` — instalação não autorizada e build ainda pendente;
- `estado_planejamento_v2a.json` — instalação não autorizada e build ainda pendente.

O build PyInstaller ficou **PENDENTE**: o Python disponível não está em venv isolado e não possui PyInstaller. Nenhuma dependência foi instalada. Não houve execução ou assinatura de EXE.

## Disposição dos achados

A matriz detalhada está em `MATRIZ_ACHADOS_V3153_R1.md`. Resumo:

- corrigidos: F-01, F-02, F-04, F-08;
- mitigados por bloqueio: F-05, F-06;
- parciais: F-03, F-07;
- não resolvido: F-09 (completude operacional/build);
- não testado: symlink real e build PyInstaller, registrados como subitens sem aprovação.

## Decisão

**NÃO HOMOLOGADO / NÃO INSTALAR.** A integridade das fontes e vários controles defensivos estão confirmados, mas faltam 13 arquivos referenciados, o smoke gráfico não foi executado em ambiente apropriado, symlink real permaneceu não testado e o `.spec` não foi compilado em venv isolado. G5, G6, G7 e instalação continuam pendentes ou bloqueados conforme seu escopo próprio.
