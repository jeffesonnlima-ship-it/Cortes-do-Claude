"""Estádio noturno reaproveitável (gramado, traves, torcida, refletores, placar, bola).

    import estadio as E
    est = E.construir(cena, fps=12, duracao=15.5,
                      placares=[(0, "VAS 0 x 0 INT"), (10.4, "VAS 1 x 0 INT")], relogio="25'")
    est.bola, est.CX, est.CY, est.placar_x ...
"""
import math, random
from types import SimpleNamespace
import bpy
import bmesh
from mathutils import Vector
import personagens as P


def construir(cena, fps=12, duracao=15.5, placares=((0, "VAS 0 x 0 INT"),), relogio="25'", torcida_pula=1.0):
    FPS = fps
    n_quadros = int(round(duracao * fps)) + 1

    def q(t):
        return int(round(t * FPS)) + 1
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
            for f in range(1, n_quadros + 2, 3):
                o.location.z = 0.35 * torcida_pula * max(0.0, math.sin((f / FPS) * 2 * math.pi * 1.6 + fase * 2 * math.pi))
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
    C(P.caixa("placar", (placar_x, placar_y, placar_z), (22, 0.8, 8),
              P.mat_toon("placar", (0.02, 0.02, 0.03), 0.5), contorno=0))
    fonte = bpy.data.fonts.load("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf")
    led = P.mat_toon("led", P.hexcor("#39E3F5"), 0.3, emissao=4.0)
    led_amarelo = P.mat_toon("led_am", P.hexcor("#FFD23F"), 0.3, emissao=4.0)

    def texto(corpo, loc, tam, mat, nome="texto", rot_x=90, rot_z=0):
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
        o.rotation_euler = (math.radians(rot_x), 0, math.radians(rot_z))
        o.data.materials.append(mat)
        return C(o)

    txts = []
    for i, (t_ini, corpo) in enumerate(placares):
        o = texto(corpo, (placar_x, placar_y - 0.5, placar_z + 1.4), 2.6, led, "placar_txt%d" % i)
        t_fim = placares[i + 1][0] if i + 1 < len(placares) else 1e9
        o.hide_render = True
        o.keyframe_insert("hide_render", frame=1)
        if t_ini > 0:
            o.keyframe_insert("hide_render", frame=q(t_ini) - 1)
        o.hide_render = False
        o.keyframe_insert("hide_render", frame=max(1, q(t_ini)))
        if t_fim < 1e8:
            o.hide_render = True
            o.keyframe_insert("hide_render", frame=q(t_fim))
        txts.append(o)
    texto(relogio, (placar_x, placar_y - 0.5, placar_z - 2.0), 2.4, led_amarelo, "relogio")

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

    return SimpleNamespace(**{k: v for k, v in locals().items()})
