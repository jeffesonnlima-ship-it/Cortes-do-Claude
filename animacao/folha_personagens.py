"""Renderiza a folha de personagens (todos os presets lado a lado)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import personagens as P

saida = sys.argv[1] if len(sys.argv) > 1 else "folha.png"
amostras = int(sys.argv[2]) if len(sys.argv) > 2 else 48
larg = int(sys.argv[3]) if len(sys.argv) > 3 else 1920

P.limpar_cena()
P.luz_estudio()
lista = [("jogador_listrado", "neutro"), ("jogador_aros", "feliz"), ("jogador_liso", "preocupado"),
         ("arbitro", "bravo"), ("torcedor", "chocado"), ("dirigente", "desconfiado"),
         ("tecnico", "bravo"), ("narrador", "feliz")]
esp = 1.9
for i, (preset, expr) in enumerate(lista):
    P.criar_personagem(nome=preset, x=(i - (len(lista) - 1) / 2) * esp, preset=preset, expressao=expr)
P.camera((0, -22, 3.6), (0, 0, 1.6), lente=50)
P.renderizar(os.path.abspath(saida), larg, int(larg * 9 / 16), amostras)
