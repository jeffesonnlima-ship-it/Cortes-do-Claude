# Animação: personagens 3D "cabeça de bolinha"

Personagens próprios do Cortes do Claude, montados no Blender por código
(cabeça redonda, olhos de ponto, corpo em cápsula, membros de palito, contorno preto).

## Como rodar

```bash
python3 -m venv venv && venv/bin/pip install bpy   # Blender como módulo Python (Python 3.13)
venv/bin/python folha_personagens.py renders/folha_personagens.png 64 1920
venv/bin/python expressoes.py renders/folha_expressoes.png 64 1920
venv/bin/python cena_teste_vertical.py renders/cena_teste_9x16.png 64 1080
```

Argumentos: arquivo de saída, amostras do Cycles, largura em pixels.

## Personagens (`PRESETS` em `personagens.py`)

`jogador_listrado`, `jogador_aros`, `jogador_liso`, `arbitro`, `torcedor`,
`dirigente`, `tecnico`, `narrador` (mascote do canal: fone e cachecol laranja).

Expressões: `neutro`, `feliz`, `bravo`, `preocupado`, `chocado`, `desconfiado`.

Qualquer preset aceita sobrescrever `pele`, `cabelo` (`liso`, `topete`, `cacheado`, `careca`),
`cor_cabelo` e `uniforme` (`cor1`, `cor2`, `padrao` = `liso`/`vertical`/`horizontal`, `cor_calcao`).
