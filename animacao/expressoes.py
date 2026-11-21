"""Folha de expressões: o mesmo personagem com 6 expressões."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import personagens as P
saida, amostras, larg = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
P.limpar_cena()
P.luz_estudio(fundo=(0.98, 0.84, 0.55), cor_chao=(0.95, 0.78, 0.45))
ex = ["neutro", "feliz", "bravo", "preocupado", "chocado", "desconfiado"]
for i, e in enumerate(ex):
    P.criar_personagem(nome=e, x=(i - 2.5) * 2.1, preset="jogador_liso", expressao=e)
P.camera((0, -19, 3.4), (0, 0, 2.2), lente=50)
P.renderizar(os.path.abspath(saida), larg, int(larg * 9 / 16), amostras)
