# RELATÓRIO — AJUSTE DO BOTÃO DE CONFIGURAÇÕES

Data: 2026-09-18
Versão: 0.27.6
Build: `config-gear-image`
Schema: 19

## Objetivo
Substituir a engrenagem tipográfica do botão de Configurações por uma imagem baseada na referência enviada pelo usuário, usando fundo transparente para que apareça apenas sobre o fundo do próprio programa.

## Alterações realizadas

### 1. Novo asset
Foi criado o arquivo:
- `assets/config_gear.png`

A imagem foi preparada com transparência para remover o fundo xadrez da referência.

### 2. Botão de Configurações
O botão do cabeçalho passou a:
- usar `QIcon` com o asset `assets/config_gear.png`;
- exibir apenas a imagem da engrenagem;
- manter fallback para o caractere `⚙` caso o asset não exista.

### 3. Tamanho e integração visual
O ícone foi configurado com tamanho compacto (`20x20`) para caber bem no botão existente sem acrescentar novo fundo além do próprio botão do tema.

## Arquivos alterados
- `main.py`
- `versao.py`
- `assets/config_gear.png`

## Validação local
- `python -m py_compile main.py versao.py` ✅
- `python -m unittest -q test_gamificacao.py test_regularidade.py` ✅

## Resultado esperado
No cabeçalho:
- o botão de Configurações deve mostrar a engrenagem azul da referência;
- sem fundo xadrez na imagem;
- usando apenas o fundo normal do programa/botão.
