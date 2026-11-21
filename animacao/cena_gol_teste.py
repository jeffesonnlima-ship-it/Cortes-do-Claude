"""Teste de animação (9:16): Vasco 1 x 0 Inter, gol de Thiago Mendes.

Uso:
    python cena_gol_teste.py <pasta_saida> [amostras] [largura] [quadro_ini] [quadro_fim]

Renderiza PNGs numerados a 12 quadros/s; a montagem (upscale, legendas,
narração) é feita depois com ffmpeg (ver montar_teste.sh).
"""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import bmesh
from mathutils import Vector
import personagens as P

saida = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "frames_teste")
AMOSTRAS = int(sys.argv[2]) if len(sys.argv) > 2 else 10
LARG = int(sys.argv[3]) if len(sys.argv) > 3 else 540
FPS = 12
DURACAO = 15.5


def q(t):
    """segundos -> número do quadro"""
    return int(round(t * FPS)) + 1


cena = P.limpar_cena()
cena.render.fps = FPS
cena.frame_start = 1
cena.frame_end = q(DURACAO) - 1
cena.render.use_persistent_data = True
cena.cycles.samples = AMOSTRAS

# ------------------------------------------------------------------ céu e luz (noite)
mundo = bpy.data.worlds.new("noite")
cena.world = mundo
mundo.use_nodes = True
bg = mundo.node_tree.nodes["Background"]
bg.inputs[0].default_value = (*P.lin((0.07, 0.10, 0.24)), 1)
bg.inputs[1].default_value = 1.8

bpy.ops.object.light_add(type="SUN", rotation=(math.radians(42), math.radians(8), math.radians(-25)))
sol = bpy.context.active_object
sol.data.energy = 3.4
sol.data.angle = math.radians(12)
sol.data.color = (1.0, 0.98, 0.94)
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(40), math.radians(20), math.radians(150)))
contra = bpy.context.active_object
contra.data.energy = 0.8
contra.data.color = (0.75, 0.82, 1.0)

cenario = []


def C(o):
    P.para_cenario(o)
    return o


# ------------------------------------------------------------------ gramado
CX, CY = 62, 40  # meio-comprimento e meia-largura do campo
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
gram = C(bpy.context.active_object)
gram.scale = (CX * 2 + 30, CY * 2 + 30, 1)
mg = bpy.data.materials.new("gramado")
mg.use_nodes = True
nt = mg.node_tree
bs = nt.nodes["Principled BSDF"]
bs.inputs["Roughness"].default_value = 0.85
tc = nt.nodes.new("ShaderNodeTexCoord")
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
nt.links.new(tc.outputs["Object"], sep.inputs[0])
mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 2 * math.pi * 9
nt.links.new(sep.outputs["X"], mul.inputs[0])
sen = nt.nodes.new("ShaderNodeMath"); sen.operation = "SINE"
nt.links.new(mul.outputs[0], sen.inputs[0])
gt = nt.nodes.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"
nt.links.new(sen.outputs[0], gt.inputs[0])
_, fac, a, b, out = P._mix_rgba(nt)
a.default_value = (*P.lin((0.20, 0.58, 0.22)), 1)
b.default_value = (*P.lin((0.16, 0.50, 0.19)), 1)
nt.links.new(gt.outputs[0], fac)
nt.links.new(out, bs.inputs["Base Color"])
gram.data.materials.append(mg)

cal = P.mat_toon("cal", (0.92, 0.92, 0.92), 0.6)


def linha(x1, y1, x2, y2, larg=0.25):
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    comp = math.hypot(x2 - x1, y2 - y1)
    ang = math.atan2(y2 - y1, x2 - x1)
    C(P.caixa("linha", (cx, cy, 0.01), (comp + larg, larg, 0.01), cal, rot=(0, 0, ang), contorno=0))


def retangulo(x1, y1, x2, y2):
    linha(x1, y1, x2, y1); linha(x2, y1, x2, y2); linha(x2, y2, x1, y2); linha(x1, y2, x1, y1)


retangulo(-CX, -CY, CX, CY)
linha(0, -CY, 0, CY)
for sx in (-1, 1):
    retangulo(sx * CX, -20, sx * (CX - 20), 20)
    retangulo(sx * CX, -9, sx * (CX - 7), 9)
bpy.ops.mesh.primitive_torus_add(major_radius=11, minor_radius=0.13, location=(0, 0, 0.01),
                                 major_segments=96, minor_segments=6)
t = C(bpy.context.active_object); t.scale = (1, 1, 0.05); t.data.materials.append(cal)

# ------------------------------------------------------------------ traves e rede
branco_trave = P.mat_toon("trave", (0.97, 0.97, 0.97), 0.3)
rede = bpy.data.materials.new("rede")
rede.use_nodes = True
rede.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.9, 0.9, 0.9, 1)
GX, GY, GZ, GP = CX, 7.2, 4.8, 3.2  # linha do gol, meia-largura, altura, profundidade
for sx in (1, -1):
    x = sx * GX
    for sy in (-1, 1):
        P.bastao("poste", (x, sy * GY, 0), (x, sy * GY, GZ), 0.14, branco_trave, pontas=False)
    P.bastao("travessao", (x, -GY, GZ), (x, GY, GZ), 0.14, branco_trave, pontas=False)
    # rede: caixa aberta com modificador wireframe
    bm = bmesh.new()
    xf = x + sx * GP
    vs = [bm.verts.new(v) for v in [(x, -GY, GZ), (xf, -GY, GZ * 0.8), (xf, GY, GZ * 0.8), (x, GY, GZ),
                                    (x, -GY, 0), (xf, -GY, 0), (xf, GY, 0), (x, GY, 0)]]
    bm.faces.new([vs[0], vs[1], vs[2], vs[3]])  # teto
    bm.faces.new([vs[1], vs[5], vs[6], vs[2]])  # fundo
    bm.faces.new([vs[0], vs[4], vs[5], vs[1]])  # lado
    bm.faces.new([vs[3], vs[2], vs[6], vs[7]])  # lado
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=14, use_grid_fill=True)
    me = bpy.data.meshes.new("rede"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("rede", me); bpy.context.collection.objects.link(o)
    w = o.modifiers.new("fio", "WIREFRAME"); w.thickness = 0.035
    o.data.materials.append(rede)
    C(o)

# ------------------------------------------------------------------ arquibancadas + torcida
concreto = P.mat_toon("concreto", P.lin((0.32, 0.34, 0.40)), 0.9)
rnd = random.Random(11)
cores_torcida = {
    "preto": P.hexcor("#161616"), "branco": P.hexcor("#EDEDED"), "cinza": P.hexcor("#6E6E73"),
    "vermelho": P.hexcor("#C8102E"),
}
pele_torcida = [P.lin(P.PELE[k]) for k in ("clara", "morena", "parda", "negra")]
bm_corpo = {k: bmesh.new() for k in cores_torcida}
bm_cabeca = [bmesh.new() for _ in pele_torcida]
bm_corpo_b = {k: bmesh.new() for k in cores_torcida}   # metade que pula fora de fase
bm_cabeca_b = [bmesh.new() for _ in pele_torcida]


def pessoa(x, y, z, cor, visitante=False):
    meta = rnd.random() < 0.5
    alvo_c = (bm_corpo_b if meta else bm_corpo)[cor]
    m = bmesh.ops.create_icosphere(alvo_c, subdivisions=1, radius=0.5)
    for v in m["verts"]:
        v.co = Vector((v.co.x * 0.95 + x, v.co.y * 0.8 + y, v.co.z * 1.1 + z + 0.6))
    i = rnd.randrange(len(pele_torcida))
    alvo_p = (bm_cabeca_b if meta else bm_cabeca)[i]
    m = bmesh.ops.create_icosphere(alvo_p, subdivisions=1, radius=0.42)
    for v in m["verts"]:
        v.co = v.co + Vector((x, y, z + 1.45))


FILEIRAS, PASSO_Y, PASSO_Z = 9, 1.7, 1.25


def arquibancada(eixo, sinal, inicio, comp, visitante_ini=None):
    """eixo 'y': lateral (ao longo de x); eixo 'x': fundo (ao longo de y)."""
    for f in range(FILEIRAS):
        d = inicio + f * PASSO_Y
        z = f * PASSO_Z
        if eixo == "y":
            C(P.caixa("degrau", (0, sinal * d, z / 2 + 0.3), (comp, PASSO_Y, z + 0.6), concreto, contorno=0))
        else:
            C(P.caixa("degrau", (sinal * d, 0, z / 2 + 0.3), (PASSO_Y, comp, z + 0.6), concreto, contorno=0))
        n = int(comp / 1.15)
        for k in range(n):
            if rnd.random() < 0.06:
                continue
            u = -comp / 2 + (k + 0.5) * comp / n + rnd.uniform(-0.15, 0.15)
            vis = visitante_ini is not None and u > visitante_ini
            if vis:
                cor = "vermelho" if rnd.random() < 0.85 else "branco"
            else:
                r = rnd.random()
                cor = "preto" if r < 0.55 else ("branco" if r < 0.88 else "cinza")
            if eixo == "y":
                pessoa(u, sinal * d, z + 0.6, cor)
            else:
                pessoa(sinal * d, u, z + 0.6, cor)


arquibancada("y", 1, CY + 6, 2 * CX + 16)
arquibancada("y", -1, CY + 6, 2 * CX + 16)
arquibancada("x", 1, CX + 9, 2 * CY + 10, visitante_ini=CY * 0.3)
arquibancada("x", -1, CX + 9, 2 * CY + 10)

torcida_a, torcida_b = [], []
for dic_c, dic_p, lista in ((bm_corpo, bm_cabeca, torcida_a), (bm_corpo_b, bm_cabeca_b, torcida_b)):
    for k, bmc in dic_c.items():
        me = bpy.data.meshes.new("torcida_" + k); bmc.to_mesh(me); bmc.free()
        o = bpy.data.objects.new("torcida_" + k, me); bpy.context.collection.objects.link(o)
        o.data.materials.append(P.mat_toon("torc_" + k, cores_torcida[k], 0.7))
        lista.append(C(o))
    for i, bmp in enumerate(dic_p):
        me = bpy.data.meshes.new("cabecas"); bmp.to_mesh(me); bmp.free()
        o = bpy.data.objects.new("cabecas", me); bpy.context.collection.objects.link(o)
        o.data.materials.append(P.mat_toon("pele_torc%d" % i, pele_torcida[i], 0.5))
        lista.append(C(o))

# torcida pulando: as duas metades alternam
for lista, fase in ((torcida_a, 0.0), (torcida_b, 0.5)):
    for o in lista:
        for f in range(1, cena.frame_end + 2, 3):
            o.location.z = 0.35 * max(0.0, math.sin((f / FPS) * 2 * math.pi * 1.6 + fase * 2 * math.pi))
            o.keyframe_insert("location", index=2, frame=f)

# refletores
luz_ref = P.mat_toon("refletor", (1.0, 0.97, 0.88), 0.2, emissao=12.0)
for sx in (-1, 1):
    for sy in (-1, 1):
        x, y = sx * (CX + 20), sy * (CY + 20)
        C(P.bastao("torre", (x, y, 0), (x, y, 30), 0.6, concreto, pontas=False))
        painel = C(P.caixa("painel", (x, y, 31), (7, 0.6, 3), luz_ref, contorno=0,
                           rot=(math.radians(-25 * sy), 0, math.radians(-25 * sx * sy))))

# ------------------------------------------------------------------ placar (LED)
placar_x, placar_y, placar_z = 0, CY + 6 + FILEIRAS * PASSO_Y + 3, FILEIRAS * PASSO_Z + 9
C(P.caixa("placar", (placar_x, placar_y, placar_z), (22, 0.8, 8), P.mat_toon("placar", (0.02, 0.02, 0.03), 0.5), contorno=0))
fonte = bpy.data.fonts.load("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf")
led = P.mat_toon("led", P.hexcor("#39E3F5"), 0.3, emissao=4.0)
led_amarelo = P.mat_toon("led_am", P.hexcor("#FFD23F"), 0.3, emissao=4.0)


def texto(corpo, loc, tam, mat, nome="texto"):
    cu = bpy.data.curves.new(nome, "FONT")
    cu.body = corpo
    cu.font = fonte
    cu.size = tam
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.extrude = 0.05
    o = bpy.data.objects.new(nome, cu)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (math.radians(90), 0, 0)
    o.data.materials.append(mat)
    return C(o)


txt_placar = texto("VAS 0 x 0 INT", (placar_x, placar_y - 0.5, placar_z + 1.4), 2.6, led, "placar_txt")
texto("25'", (placar_x, placar_y - 0.5, placar_z - 2.0), 2.4, led_amarelo, "relogio")
# o placar muda para 1 x 0 depois do gol
txt_placar2 = texto("VAS 1 x 0 INT", (placar_x, placar_y - 0.5, placar_z + 1.4), 2.6, led, "placar_txt2")
for o, vis_antes in ((txt_placar, True), (txt_placar2, False)):
    for f, vis in ((1, vis_antes), (q(10.4), not vis_antes)):
        o.hide_render = not vis
        o.keyframe_insert("hide_render", frame=f)

# ------------------------------------------------------------------ bola
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.38)
bola = bpy.context.active_object
bola.name = "bola"
mb = bpy.data.materials.new("bola")
mb.use_nodes = True
ntb = mb.node_tree
vor = ntb.nodes.new("ShaderNodeTexVoronoi"); vor.inputs["Scale"].default_value = 3.2
ntb.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.35
ramp = ntb.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = 0.18
ramp.color_ramp.elements[0].color = (0.03, 0.03, 0.03, 1)
ramp.color_ramp.elements[1].position = 0.2
ramp.color_ramp.elements[1].color = (0.95, 0.95, 0.95, 1)
ntb.links.new(vor.outputs["Distance"], ramp.inputs[0])
ntb.links.new(ramp.outputs[0], ntb.nodes["Principled BSDF"].inputs["Base Color"])
P._finalizar(bola, mb, 0, None)

# ------------------------------------------------------------------ personagens
TM_POS = (52.0, 3.0)      # Thiago Mendes
CO_POS = (49.5, -3.5)     # Coutinho
PU_POS = (CX - 1.2, -CY + 1.2)  # Puma no escanteio


def rumo(de, para):
    """rot_z para o personagem (frente = -Y) olhar de 'de' para 'para'."""
    dx, dy = para[0] - de[0], para[1] - de[1]
    return math.degrees(math.atan2(dx, -dy))


puma = P.criar_personagem("puma", *PU_POS, preset="vasco", expressao="neutro",
                          rot_z=rumo(PU_POS, (50, 0)), cabelo="cacheado", pele="parda")
cout = P.criar_personagem("coutinho", *CO_POS, preset="vasco", expressao="neutro",
                          rot_z=rumo(CO_POS, (CX - 6, 0)), pele="morena", cabelo="liso")
tm = P.criar_personagem("thiago", *TM_POS, preset="vasco", expressao="neutro",
                        rot_z=rumo(TM_POS, (CX, 0)), pele="clara", cabelo="longo", cor_cabelo="castanho")
zag1 = P.criar_personagem("zagueiro1", 51.0, -1.0, preset="inter", expressao="preocupado",
                          rot_z=rumo((51, -1), (40, 0)))
zag2 = P.criar_personagem("zagueiro2", 53.8, 6.8, preset="inter", expressao="chocado",
                          rot_z=rumo((53.8, 6.8), (45, 0)), pele="parda", cabelo="careca")
gol = P.criar_personagem("goleiro", CX - 1.6, 0.6, preset="goleiro_inter", expressao="preocupado",
                         rot_z=rumo((CX - 1.6, 0.6), (40, 0)), mao_d=(0.85, -0.2, 1.9), mao_e=(-0.85, -0.2, 1.9))

# comemoração (perto da lateral, com a torcida atrás)
CEL = (10.0, 31.0)
braco_cima_d, braco_cima_e = (0.85, -0.1, 2.9), (-0.85, -0.1, 2.9)
cel_tm = P.criar_personagem("cel_thiago", CEL[0], CEL[1], preset="vasco", expressao="feliz",
                            pele="clara", cabelo="longo", cor_cabelo="castanho",
                            mao_d=braco_cima_d, mao_e=braco_cima_e)
cel_co = P.criar_personagem("cel_coutinho", CEL[0] - 2.1, CEL[1] + 0.8, preset="vasco", expressao="feliz",
                            rot_z=-15, pele="morena", mao_d=(0.8, -0.3, 2.6), mao_e=(-0.95, 0, 1.4))
cel_pu = P.criar_personagem("cel_puma", CEL[0] + 2.2, CEL[1] + 0.9, preset="vasco", expressao="feliz",
                            rot_z=18, cabelo="cacheado", pele="parda", mao_d=(0.95, 0, 1.4), mao_e=(-0.8, -0.3, 2.7))
# jogador do Inter bravo (último plano)
BR = (-12.0, 31.0)
bravo = P.criar_personagem("inter_bravo", *BR, preset="inter", expressao="bravo", pele="morena",
                           cabelo="cacheado", mao_d=(0.6, -0.35, 1.25), mao_e=(-0.6, -0.35, 1.25))


def junta(raiz, nome_j):
    return bpy.data.objects[raiz["juntas"][nome_j]]


def kf(obj, attr, frame, valor, idx=None):
    if idx is None:
        setattr(obj, attr, valor)
        obj.keyframe_insert(attr, frame=frame)
    else:
        getattr(obj, attr)[idx] = valor
        obj.keyframe_insert(attr, index=idx, frame=frame)


# --- Puma: corre 2 passos e cruza (chute com a perna direita)
t_chute = 6.35
pd, pe = junta(puma, "quadril_d"), junta(puma, "quadril_e")
for t, ang_d, ang_e in ((5.7, 0, 0), (5.9, -0.4, 0.4), (6.05, 0.4, -0.4), (6.2, 0.75, -0.1),
                        (t_chute, -1.1, 0.15), (6.6, -0.5, 0.05), (6.9, 0, 0)):
    kf(pd, "rotation_euler", q(t), ang_d, 0)
    kf(pe, "rotation_euler", q(t), ang_e, 0)
for t, z in ((6.2, 0.0), (t_chute, 0.25), (6.6, 0.0)):
    kf(puma, "location", q(t), z, 2)
ob_d, ob_e = junta(puma, "ombro_d"), junta(puma, "ombro_e")
for t, a in ((6.2, 0), (t_chute, 0.9), (6.9, 0.2)):
    kf(ob_e, "rotation_euler", q(t), -a, 1)
    kf(ob_d, "rotation_euler", q(t), a * 0.5, 1)


# --- pulos de cabeceio
def pulo(raiz, t_pico, altura=1.5, dur=0.9):
    for t, z in ((t_pico - dur / 2, 0), (t_pico - dur / 4, altura * 0.8), (t_pico, altura),
                 (t_pico + dur / 4, altura * 0.8), (t_pico + dur / 2, 0)):
        kf(raiz, "location", q(t), z, 2)
    od, oe = junta(raiz, "ombro_d"), junta(raiz, "ombro_e")
    for t, a in ((t_pico - dur / 2, 0), (t_pico, 1.1), (t_pico + dur / 2, 0.1)):
        kf(od, "rotation_euler", q(t), a, 1)
        kf(oe, "rotation_euler", q(t), -a, 1)
    qd, qe = junta(raiz, "quadril_d"), junta(raiz, "quadril_e")
    for t, a in ((t_pico - dur / 2, 0), (t_pico, 0.45), (t_pico + dur / 2, 0)):
        kf(qd, "rotation_euler", q(t), a, 0)
        kf(qe, "rotation_euler", q(t), -0.3, 0)


T_CO = 7.75   # Coutinho escora
T_TM = 9.05   # Thiago cabeceia
T_REDE = 9.6  # bola na rede
pulo(cout, T_CO)
pulo(tm, T_TM, altura=1.6)
pulo(zag1, T_CO + 0.1, altura=1.0)
pulo(zag2, T_TM + 0.05, altura=0.9)

# --- goleiro: espera, salta tarde para o canto
for t, x_rot, dy, z in ((8.9, 0, 0, 0), (9.25, 0, 0.6, 0.4), (9.65, -1.35, 3.2, 1.6),
                        (10.1, -1.5, 4.0, 0.6), (10.5, -1.55, 4.2, 0.35)):
    kf(gol, "rotation_euler", q(t), x_rot, 1)
    kf(gol, "location", q(t), 0.6 + dy, 1)
    kf(gol, "location", q(t), z, 2)

# --- bola (posição calculada quadro a quadro)
CAB = 2.62 + 0.8  # topo da cabeça em pé
p_pe = Vector((PU_POS[0] - 0.4, PU_POS[1] + 0.6, 0.38))
p_co = Vector((CO_POS[0], CO_POS[1], CAB + 1.5 - 0.15))
p_tm = Vector((TM_POS[0], TM_POS[1], CAB + 1.6 - 0.15))
p_rede = Vector((CX + 1.2, 4.6, 2.4))
p_chao = Vector((CX + 2.6, 4.9, 0.38))


def arco(p1, p2, u, pico):
    p = p1.lerp(p2, u)
    p.z += 4 * pico * u * (1 - u)
    return p


for f in range(1, cena.frame_end + 2):
    t = (f - 1) / FPS
    if t <= t_chute:
        pos = p_pe
    elif t <= T_CO:
        pos = arco(p_pe, p_co, (t - t_chute) / (T_CO - t_chute), 9.0)
    elif t <= T_TM:
        pos = arco(p_co, p_tm, (t - T_CO) / (T_TM - T_CO), 1.6)
    elif t <= T_REDE:
        pos = arco(p_tm, p_rede, (t - T_TM) / (T_REDE - T_TM), 0.3)
    elif t <= T_REDE + 0.7:
        pos = arco(p_rede, p_chao, (t - T_REDE) / 0.7, 0.2)
    else:
        pos = p_chao
    bola.location = pos
    bola.keyframe_insert("location", frame=f)
    bola.rotation_euler.x = t * 9
    bola.keyframe_insert("rotation_euler", index=0, frame=f)

# --- comemoração: pulinhos e braços balançando
for i, (r, fase) in enumerate(((cel_tm, 0.0), (cel_co, 0.33), (cel_pu, 0.66))):
    for f in range(q(10.9), q(12.9) + 1, 2):
        t = (f - 1) / FPS
        kf(r, "location", f, 0.45 * abs(math.sin((t * 2.6 + fase) * math.pi)), 2)
        for nome_j, s in (("ombro_d", 1), ("ombro_e", -1)):
            kf(junta(r, nome_j), "rotation_euler", f, s * 0.22 * math.sin((t * 3 + fase) * 2 * math.pi), 1)

# --- jogador bravo: bufando (sobe e desce o corpo)
for f in range(q(12.6), q(DURACAO) + 1, 3):
    t = (f - 1) / FPS
    kf(bravo, "location", f, 0.06 * math.sin(t * 2 * math.pi * 1.2), 2)

# ------------------------------------------------------------------ câmeras e cortes
cams = []


def plano(nome, t_ini, t_fim, pos_ini, pos_fim, alvo_ini, alvo_fim, lente=35):
    cam = P.camera(pos_ini, alvo_ini, lente=lente)
    cam.name = nome
    for t, pos, alvo in ((t_ini, pos_ini, alvo_ini), (t_fim, pos_fim, alvo_fim)):
        cam.location = pos
        d = Vector(alvo) - Vector(pos)
        cam.rotation_quaternion = d.to_track_quat("-Z", "Y")
        cam.keyframe_insert("location", frame=q(t))
        cam.keyframe_insert("rotation_quaternion", frame=q(t))
    m = cena.timeline_markers.new(nome, frame=q(t_ini))
    m.camera = cam
    cams.append(cam)


# 1. aéreo do estádio
plano("aereo", 0.0, 3.0, (-95, -120, 85), (-70, -92, 58), (0, 0, 0), (5, 5, 0), lente=28)
# 2. torcida
plano("torcida", 3.0, 4.4, (-6, CY - 12, 3.5), (2, CY - 11, 4.0), (-6, CY + 12, 7.0), (2, CY + 12, 7.5), lente=30)
# 3. placar com o relógio
plano("placar", 4.4, 5.9, (placar_x, placar_y - 26, placar_z - 1), (placar_x, placar_y - 19, placar_z),
      (placar_x, placar_y, placar_z), (placar_x, placar_y, placar_z), lente=40)
# 4. escanteio: Puma cruza
plano("escanteio", 5.9, 7.4, (PU_POS[0] - 11, PU_POS[1] - 7, 3.6), (PU_POS[0] - 12, PU_POS[1] - 5, 5.5),
      (PU_POS[0], PU_POS[1] + 1, 2.2), (PU_POS[0] - 3, PU_POS[1] + 12, 6.5), lente=30)
# 5. Coutinho escora
plano("coutinho", 7.4, 8.5, (CO_POS[0] - 10, CO_POS[1] - 7, 4.2), (CO_POS[0] - 9, CO_POS[1] - 6, 4.6),
      (CO_POS[0], CO_POS[1], 3.8), (CO_POS[0] + 1.5, CO_POS[1] + 3, 4.4), lente=32)
# 6. Thiago cabeceia para o gol (câmera ao lado do gol, olhando para o campo)
plano("gol", 8.5, 11.1, (TM_POS[0] + 1.5, -15, 3.8), (TM_POS[0] + 4.5, -14, 3.4),
      (TM_POS[0] + 1, TM_POS[1], 4.0), (CX + 0.5, 3.0, 2.4), lente=26)
# 7. comemoração
plano("comemoracao", 11.1, 12.8, (CEL[0] + 0.5, CEL[1] - 10, 3.3), (CEL[0] + 0.3, CEL[1] - 8, 3.0),
      (CEL[0], CEL[1], 2.6), (CEL[0], CEL[1], 2.7), lente=32)
# 8. jogador do Inter bravo
plano("bravo", 12.8, DURACAO, (BR[0], BR[1] - 7.5, 3.0), (BR[0], BR[1] - 5.2, 3.0),
      (BR[0], BR[1], 2.75), (BR[0], BR[1], 2.85), lente=32)

# ------------------------------------------------------------------ render
cena.render.resolution_x = LARG
cena.render.resolution_y = int(LARG * 16 / 9)
cena.render.resolution_percentage = 100
cena.render.image_settings.file_format = "PNG"
cena.render.filepath = os.path.join(saida, "f_")
if os.environ.get("QUADROS"):
    # modo prévia: renderiza só alguns quadros soltos
    for f in [int(x) for x in os.environ["QUADROS"].split(",")]:
        cena.frame_set(f)
        cena.render.filepath = os.path.join(saida, "previa_%04d.png" % f)
        bpy.ops.render.render(write_still=True)
else:
    if len(sys.argv) > 5:
        cena.frame_start, cena.frame_end = int(sys.argv[4]), int(sys.argv[5])
    bpy.ops.render.render(animation=True)
