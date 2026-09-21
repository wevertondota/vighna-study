# Auditoria e recuperação do banco de questões — 20/09/2026

## Escopo

Foram comparados:

- os três bancos SQLite fornecidos pelo usuário;
- **58 bancos históricos com tabela de questões** extraídos de **73 checkpoints** disponíveis entre 15 e 20/09/2026;
- os conjuntos VPQ 1.1 disponíveis na Biblioteca do projeto;
- a estrutura atual de disciplinas, tópicos, capítulos, questões, sessões e tentativas.

## Conclusão principal

A auditoria encontrou **12 questões comprovadamente presentes em checkpoints anteriores e ausentes do banco atual**, todas em **Direito Penal**. Não foi encontrada perda histórica confirmada em CTB, Direito Administrativo, Direito Constitucional, Informática, Leis Complementares ou Português.

Além das 12 perdas comprovadas, existem **30 questões de Dignidade Sexual preservadas em VPQs finais** (7 de Liberdade Sexual, 5 de Exposição da Intimidade Sexual e 18 de Crimes Sexuais contra Vulnerável) que não aparecem em nenhum dos bancos/checkpoints auditados. Como o usuário informa que essas questões foram adicionadas, elas foram incluídas na base de recuperação como conteúdo recuperável de uma possível ramificação não persistida do banco.

## Perdas comprovadas por histórico

### Direito Penal — Dignidade Sexual — 6 questões

Questões históricas antigas 157 a 162, fonte `Código Penal - Arts. 233 e 234`:

- ato obsceno;
- escrito ou objeto obsceno;
- condutas equiparadas e hipóteses correlatas.

Essas questões existiam em checkpoints anteriores e os mesmos IDs passaram posteriormente a identificar questões de Crimes contra a Fé Pública. Isso é compatível com substituição por outra ramificação do banco, e não com exclusão comum pelo Vighna.

Na recuperação, foram vinculadas ao atual **Capítulo IV – Do Ultraje Público ao Pudor**.

### Direito Penal — Estado Democrático de Direito — 6 questões

Questões históricas antigas 237 a 242, fonte `Código Penal - Arts. 359-L a 359-M-B`:

- abolição violenta do Estado Democrático de Direito;
- golpe de Estado;
- regras correlatas aplicáveis aos crimes contra as instituições democráticas.

Os mesmos IDs passaram depois a identificar questões do Capítulo I — Soberania Nacional. Na recuperação, as seis foram vinculadas ao atual **Capítulo II – Dos Crimes Contra Instituições Democráticas**.

## Alterações históricas que NÃO são perda

A comparação encontrou outras 7 versões antigas de enunciados (IDs 114, 125, 126, 132, 153, 154 e 155). Os mesmos IDs continuam existentes no banco atual com enunciados revisados. Elas foram classificadas como **edições/reformulações**, não como questões perdidas, e não foram reinseridas.

## Conteúdo de Dignidade Sexual recuperado

Foram adicionadas à cópia de recuperação:

- 7 questões — Capítulo I – Dos Crimes Contra a Liberdade Sexual;
- 18 questões — Capítulo II – Dos Crimes Sexuais Contra Vulnerável;
- 5 questões — Exposição da Intimidade Sexual;
- 6 questões históricas — Capítulo IV – Do Ultraje Público ao Pudor;
- as 4 questões já existentes — Capítulo V – Disposições Gerais foram preservadas.

A estrutura atual do Vighna não contém `Capítulo I-A – Da Exposição da Intimidade Sexual`. Para não alterar silenciosamente a taxonomia, essas 5 questões foram recuperadas no **Título VI sem capítulo interno**. O conteúdo está preservado e poderá ser reclassificado caso o Capítulo I-A seja adicionado futuramente.

Resultado do Título VI após recuperação: **40 questões ativas**.

## Auditoria das demais disciplinas

A varredura dos checkpoints históricos encontrou **2.492 textos de questões historicamente distintos**. Apenas 19 textos históricos não aparecem literalmente na base atual, todos de Direito Penal; 7 eram versões antigas editadas e 12 eram perdas comprovadas.

Também foi feita comparação com os VPQs finais localizados. Nos conjuntos de Direito Administrativo, Direito Constitucional, Informática, Leis Complementares e nos conjuntos de CTB comparáveis, as questões esperadas estavam presentes no banco atual. Não apareceu evidência de perda em outra disciplina.

Há 9 questões antigas do CTB e 4 de Leis Complementares que permanecem fisicamente no banco com status de excluídas/lixeira. Elas **não foram perdidas** e não foram reativadas nesta recuperação.

## Contagem antes da recuperação

| Disciplina | Ativas | Na lixeira | Total físico |
|---|---:|---:|---:|
| Código de Trânsito Brasileiro | 763 | 9 | 772 |
| Direito Administrativo | 709 | 0 | 709 |
| Direito Constitucional | 314 | 0 | 314 |
| Direito Penal | 256 | 0 | 256 |
| Informática | 39 | 0 | 39 |
| Leis Complementares | 378 | 4 | 382 |
| Português | 36 | 0 | 36 |

## Contagem após a recuperação preparada

| Disciplina | Ativas | Na lixeira | Total físico |
|---|---:|---:|---:|
| Código de Trânsito Brasileiro | 763 | 9 | 772 |
| Direito Administrativo | 709 | 0 | 709 |
| Direito Constitucional | 314 | 0 | 314 |
| Direito Penal | 298 | 0 | 298 |
| Informática | 39 | 0 | 39 |
| Leis Complementares | 378 | 4 | 382 |
| Português | 36 | 0 | 36 |

O único acréscimo realizado foi em **Direito Penal: +42 questões**. Nenhuma outra disciplina foi modificada.

## Integridade do banco recuperado

- `PRAGMA integrity_check`: **ok**;
- `PRAGMA foreign_key_check`: **0 problemas**;
- questões físicas: **2.550**;
- questões ativas: **2.537**;
- questões em lixeira: **13**;
- Direito Penal: **298 ativas**;
- Dignidade Sexual: **40 ativas**;
- Estado Democrático de Direito: **29 ativas**.

As 12 questões historicamente recuperadas não possuíam tentativas nos checkpoints em que foram encontradas. Portanto, não havia histórico de respostas associado a restaurar.

## Causa técnica encontrada

A versão anterior mantinha dois caminhos de banco:

- execução por `python main.py` → banco da raiz do projeto;
- execução pelo `.exe` → banco dentro de `dist\SistemaEstudos`.

Além disso, `atualizar_exe.bat` podia escolher o banco de `dist` e copiá-lo por cima do banco da raiz. Isso permitia que uma ramificação antiga substituísse outra sem deixar registros de `DELETE` ou lacunas nos IDs.

## Correção estrutural 0.29.5

Foi preparada a versão **0.29.5 — single-database-integrity-recovery-v1**:

- Python e EXE passam a localizar a mesma fonte autoritativa `C:\SistemaEstudos\estudos.db`;
- `atualizar_exe.bat` não copia mais o banco de `dist` por cima da raiz;
- builds novos não criam uma segunda cópia operacional de `estudos.db` em `dist`;
- se uma cópia antiga de `dist` existir durante a transição, ela é arquivada em `backups` antes da substituição do executável;
- checkpoints passam a fotografar o banco único da raiz;
- script `aplicar_recuperacao_banco.bat` faz backup dos bancos atuais antes de instalar a base recuperada.

## Arquivos de recuperação

- `RECUPERACAO/estudos_recuperado.db` — banco recuperado;
- `RECUPERACAO/estudos_pre_recuperacao.db` — cópia do banco usado como base;
- `RECUPERACAO/QUESTOES_RECUPERADAS_42.txt` — relação das questões adicionadas;
- `RECUPERACAO/recuperacao_resumo.json` — resumo técnico;
- `aplicar_recuperacao_banco.bat` — aplicação segura com backup prévio.
