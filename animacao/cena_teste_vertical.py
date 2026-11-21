"""Cena de teste 9:16: juiz dá vermelho, jogador e torcedor reagem, no estádio."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import personagens as P
saida, amostras, larg = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
P.limpar_cena()
P.luz_estudio(fundo=(0.45, 0.70, 0.98), cor_chao=(0.20, 0.62, 0.22))
# faixas do gramado e linhas
for i in range(-6, 7):
    if i % 2 == 0:
        P.para_cenario(P.caixa("faixa", (i * 3, 6, 0.005), (3, 60, 0.01),
                               P.mat_toon("grama2", P.lin((0.17, 0.55, 0.19)), 0.85), contorno=0))
P.para_cenario(P.caixa("linha", (0, 0.8, 0.012), (40, 0.12, 0.01), P.mat_toon("cal", (0.95, 0.95, 0.95)), contorno=0))
# arquibancada: degraus + torcida de bolinhas
rnd = random.Random(3)
cores = [P.hexcor(h) for h in ("#D62828", "#111111", "#F4F4F4", "#D62828", "#1E63B5")]
for d in range(7):
    y, z = 14 + d * 1.6, d * 1.2
    P.para_cenario(P.caixa("degrau", (0, y, z), (60, 1.6, 0.6), P.mat_toon("concreto", (0.55, 0.57, 0.6)), contorno=0))
    for k in range(46):
        x = -27 + k * 1.2 + rnd.uniform(-0.2, 0.2)
        c = cores[rnd.randrange(len(cores))]
        P.para_cenario(P.esfera("torc_corpo", (x, y, z + 0.75), 0.42, P.mat_toon("t%d" % cores.index(c), c), escala=(1, 0.8, 1.1), contorno=0, seg=12))
        P.para_cenario(P.esfera("torc_cab", (x, y, z + 1.45), 0.36, P.mat_toon("tp", P.lin((0.93, 0.78, 0.62))), contorno=0, seg=12))
# personagens
P.criar_personagem("juiz", x=-1.45, y=0, preset="arbitro", expressao="bravo", rot_z=8)
P.criar_personagem("jogador", x=1.25, y=-0.4, preset="jogador_listrado", expressao="chocado", rot_z=-18)
P.camera((0.6, -8.2, 2.6), (0.1, 0, 2.0), lente=32)
bpy.context.scene.render.film_transparent = False
P.renderizar(os.path.abspath(saida), larg, int(larg * 16 / 9), amostras)
