"""Gerador de personagens 3D estilo "cabeça de bolinha" para o Cortes do Claude.

Uso (dentro do Python com o módulo bpy):
    import personagens as P
    P.limpar_cena()
    P.criar_personagem(nome="juiz", x=0, preset="arbitro", expressao="bravo")

Cada personagem é montado a partir de primitivas (esferas, cilindros, curvas)
com contorno preto feito pela técnica "inverted hull" (Solidify invertido).
"""
import math
import bpy
import bmesh
from mathutils import Vector

# ---------------------------------------------------------------- cores

PELE = {
    "clara": (0.97, 0.84, 0.70),
    "morena": (0.88, 0.64, 0.45),
    "parda": (0.70, 0.45, 0.28),
    "negra": (0.45, 0.27, 0.16),
    "branca": (0.96, 0.95, 0.93),
}
PRETO = (0.02, 0.02, 0.025)
CABELO = {
    "preto": (0.05, 0.04, 0.04),
    "castanho": (0.22, 0.12, 0.06),
    "grisalho": (0.62, 0.62, 0.64),
    "loiro": (0.85, 0.66, 0.30),
}


def hexcor(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    # sRGB -> linear
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)


def lin(c):
    """Converte cor sRGB (0-1) para linear."""
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)


# ---------------------------------------------------------------- cena

def limpar_cena():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    cena = bpy.context.scene
    cena.render.engine = "CYCLES"
    cena.cycles.device = "CPU"
    cena.cycles.samples = 48
    cena.cycles.use_denoising = True
    cena.cycles.max_bounces = 4
    cena.cycles.transparent_max_bounces = 16
    cena.view_settings.view_transform = "Standard"
    cena.view_settings.look = "None"
    # contorno preto de desenho animado (silhueta + bordas)
    cena.render.use_freestyle = True
    cena.render.line_thickness_mode = "RELATIVE"
    cena.render.line_thickness = 1.6
    fs = cena.view_layers[0].freestyle_settings
    ls = fs.linesets[0] if len(fs.linesets) else fs.linesets.new("contorno")
    if ls.linestyle is None:
        ls.linestyle = bpy.data.linestyles.new("contorno")
    ls.select_silhouette = True
    ls.select_border = True
    ls.select_crease = False
    ls.select_external_contour = True
    # cenário (chão, arquibancada) fica fora do contorno
    cen = bpy.data.collections.get("cenario") or bpy.data.collections.new("cenario")
    if cen.name not in cena.collection.children:
        cena.collection.children.link(cen)
    ls.select_by_collection = True
    ls.collection = cen
    ls.collection_negation = "EXCLUSIVE"
    ls.linestyle.color = PRETO
    ls.linestyle.thickness = 3.0
    return cena


_mats = {}


def _mix_rgba(nt):
    m = nt.nodes.new("ShaderNodeMix")
    m.data_type = "RGBA"
    fac = m.inputs[0]
    a = [i for i in m.inputs if i.name == "A" and i.type == "RGBA"][0]
    b = [i for i in m.inputs if i.name == "B" and i.type == "RGBA"][0]
    out = [o for o in m.outputs if o.type == "RGBA"][0]
    return m, fac, a, b, out


def mat_toon(nome, cor, rough=0.55, emissao=0.0):
    """Material liso, levemente 'plástico', como nos vídeos de referência."""
    chave = (nome, cor, rough, emissao)
    if chave in _mats:
        return _mats[chave]
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*cor, 1)
    bsdf.inputs["Roughness"].default_value = rough
    if emissao:
        bsdf.inputs["Emission Color"].default_value = (*cor, 1)
        bsdf.inputs["Emission Strength"].default_value = emissao
    _mats[chave] = m
    return m


def mat_contorno():
    if "contorno" in _mats:
        return _mats["contorno"]
    m = bpy.data.materials.new("contorno")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*PRETO, 1)
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(geo.outputs["Backfacing"], mix.inputs[0])
    # frente da casca (normais invertidas) = transparente; só a borda aparece preta
    nt.links.new(em.outputs[0], mix.inputs[1])
    nt.links.new(tr.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    _mats["contorno"] = m
    return m


def mat_uniforme(nome, cor1, cor2=None, padrao="liso", freq=9.0,
                 cor_calcao=None, corte_calcao=-0.42):
    """Camisa com listras verticais/horizontais + calção na parte de baixo.

    Usa coordenadas de objeto da cápsula do corpo (raio 1 antes da escala).
    """
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.6
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])

    cor_atual = None
    if padrao == "liso" or cor2 is None:
        rgb = nt.nodes.new("ShaderNodeRGB")
        rgb.outputs[0].default_value = (*cor1, 1)
        cor_atual = rgb.outputs[0]
    elif padrao == "faixa":
        # faixa diagonal do ombro direito ao quadril esquerdo
        mx = nt.nodes.new("ShaderNodeMath"); mx.operation = "MULTIPLY"
        mx.inputs[1].default_value = 0.85
        nt.links.new(sep.outputs["X"], mx.inputs[0])
        mz = nt.nodes.new("ShaderNodeMath"); mz.operation = "MULTIPLY"
        mz.inputs[1].default_value = -0.75
        nt.links.new(sep.outputs["Z"], mz.inputs[0])
        soma = nt.nodes.new("ShaderNodeMath"); soma.operation = "ADD"
        nt.links.new(mx.outputs[0], soma.inputs[0]); nt.links.new(mz.outputs[0], soma.inputs[1])
        ab = nt.nodes.new("ShaderNodeMath"); ab.operation = "ABSOLUTE"
        nt.links.new(soma.outputs[0], ab.inputs[0])
        lt = nt.nodes.new("ShaderNodeMath"); lt.operation = "LESS_THAN"
        lt.inputs[1].default_value = 0.2
        nt.links.new(ab.outputs[0], lt.inputs[0])
        _, fac, a, b, out = _mix_rgba(nt)
        a.default_value = (*cor1, 1)
        b.default_value = (*cor2, 1)
        nt.links.new(lt.outputs[0], fac)
        cor_atual = out
    else:
        eixo = sep.outputs["X"] if padrao == "vertical" else sep.outputs["Z"]
        mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = freq
        nt.links.new(eixo, mul.inputs[0])
        sen = nt.nodes.new("ShaderNodeMath"); sen.operation = "SINE"
        nt.links.new(mul.outputs[0], sen.inputs[0])
        gt = nt.nodes.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"
        gt.inputs[1].default_value = 0.0
        nt.links.new(sen.outputs[0], gt.inputs[0])
        _, fac, a, b, out = _mix_rgba(nt)
        a.default_value = (*cor1, 1)
        b.default_value = (*cor2, 1)
        nt.links.new(gt.outputs[0], fac)
        cor_atual = out

    if cor_calcao is not None:
        lt = nt.nodes.new("ShaderNodeMath"); lt.operation = "LESS_THAN"
        lt.inputs[1].default_value = corte_calcao
        nt.links.new(sep.outputs["Z"], lt.inputs[0])
        _, fac, a, b, out = _mix_rgba(nt)
        nt.links.new(cor_atual, a)
        b.default_value = (*cor_calcao, 1)
        nt.links.new(lt.outputs[0], fac)
        cor_atual = out

    nt.links.new(cor_atual, bsdf.inputs["Base Color"])
    return m


# ---------------------------------------------------------------- primitivas

# Contorno por casca invertida escurecia o shading no Cycles; o contorno agora
# é feito pelo Freestyle (ver limpar_cena). Defina CASCA=1 para testar a casca.
SEM_CONTORNO = __import__("os").environ.get("CASCA") != "1"


def _finalizar(obj, mat, contorno=0.018, pai=None, suave=True):
    if SEM_CONTORNO:
        contorno = 0
    obj.data.materials.append(mat)
    if contorno:
        obj.data.materials.append(mat_contorno())
        sol = obj.modifiers.new("contorno", "SOLIDIFY")
        sol.thickness = contorno
        sol.offset = 1.0
        sol.use_flip_normals = True
        sol.use_rim = False
        sol.material_offset = 1
        sol.use_even_offset = False
    if suave and hasattr(obj.data, "polygons"):
        for p in obj.data.polygons:
            p.use_smooth = True
    if pai is not None:
        _parentear(obj, pai)
    return obj


def _parentear(obj, pai):
    obj.parent = pai
    obj.matrix_parent_inverse = pai.matrix_world.inverted()


def esfera(nome, loc, raio, mat, escala=(1, 1, 1), contorno=0.018, pai=None, seg=48):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2,
                                         radius=raio, location=loc)
    o = bpy.context.active_object
    o.name = nome
    o.scale = escala
    return _finalizar(o, mat, contorno, pai)


def bastao(nome, p1, p2, raio, mat, contorno=0.0, pai=None, pontas=True):
    """Cilindro entre dois pontos (braços e pernas de palito)."""
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=raio, depth=d.length,
                                        location=(p1 + p2) / 2)
    o = bpy.context.active_object
    o.name = nome
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = d.to_track_quat("Z", "Y")
    _finalizar(o, mat, contorno, pai)
    if pontas:
        for i, p in enumerate((p1, p2)):
            esfera(f"{nome}_ponta{i}", p, raio, mat, contorno=0, pai=pai, seg=12)
    return o


def caixa(nome, loc, dims, mat, rot=(0, 0, 0), contorno=0.012, pai=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = nome
    o.scale = dims
    return _finalizar(o, mat, contorno, pai, suave=False)


def tubo_curva(nome, pontos, raio, mat, pai=None):
    """Curva com espessura (boca, sobrancelhas, alça do fone)."""
    cd = bpy.data.curves.new(nome, "CURVE")
    cd.dimensions = "3D"
    cd.bevel_depth = raio
    cd.bevel_resolution = 4
    cd.use_fill_caps = True
    sp = cd.splines.new("POLY")
    sp.points.add(len(pontos) - 1)
    for p, c in zip(sp.points, pontos):
        p.co = (*c, 1)
    o = bpy.data.objects.new(nome, cd)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    if pai is not None:
        _parentear(o, pai)
    return o


# ---------------------------------------------------------------- partes do rosto

def ponto_cabeca(c, r, ang_x, ang_z, fora=0.0):
    """Ponto na superfície frontal da cabeça.

    ang_x: ângulo horizontal (graus, + = direita do personagem para a câmera)
    ang_z: ângulo vertical (graus, + = para cima)
    A frente do personagem aponta para -Y.
    """
    ax, az = math.radians(ang_x), math.radians(ang_z)
    v = Vector((math.sin(ax) * math.cos(az), -math.cos(ax) * math.cos(az), math.sin(az)))
    return Vector(c) + v * (r + fora)


def rosto(c, r, expr, pai, olhos_grandes=False):
    preto = mat_toon("preto", PRETO, 0.3)
    branco = mat_toon("branco_olho", (1, 1, 1), 0.2)
    sep = 20
    ry = 0.085 * r
    alt_olho = 8
    olhos = []
    for lado in (-1, 1):
        p = ponto_cabeca(c, r, lado * sep, alt_olho, fora=-0.01 * r)
        if olhos_grandes or expr == "chocado":
            # olho arregalado: esclera branca + pupila
            esfera("olho_branco", p, 0.16 * r, branco, escala=(1, 0.45, 1.15),
                   contorno=0.012, pai=pai)
            pp = ponto_cabeca(c, r, lado * sep, alt_olho, fora=0.05 * r)
            esfera("pupila", pp, 0.06 * r, preto, escala=(1, 0.5, 1), contorno=0, pai=pai)
        else:
            alt = 1.25 if expr != "feliz" else 1.0
            esfera("olho", p, ry, preto, escala=(1, 0.5, alt), contorno=0, pai=pai)
        olhos.append(p)

    # sobrancelhas
    if expr in ("bravo", "preocupado", "desconfiado"):
        for lado in (-1, 1):
            if expr == "bravo":
                a = ponto_cabeca(c, r, lado * (sep + 10), alt_olho + 17, 0.01 * r)
                b = ponto_cabeca(c, r, lado * (sep - 9), alt_olho + 11, 0.01 * r)
            elif expr == "preocupado":
                a = ponto_cabeca(c, r, lado * (sep + 10), alt_olho + 12, 0.01 * r)
                b = ponto_cabeca(c, r, lado * (sep - 9), alt_olho + 18, 0.01 * r)
            else:  # desconfiado: uma levantada, outra reta
                h = 21 if lado > 0 else 14
                a = ponto_cabeca(c, r, lado * (sep + 10), alt_olho + h, 0.01 * r)
                b = ponto_cabeca(c, r, lado * (sep - 9), alt_olho + h - (3 if lado > 0 else 0), 0.01 * r)
            tubo_curva("sobrancelha", [a, b], 0.022 * r, preto, pai=pai)

    # boca
    boca_z = -18
    if expr in ("neutro", "bravo", "preocupado"):
        curva = {"neutro": 0, "bravo": -4, "preocupado": -3}[expr]
        pts = [ponto_cabeca(c, r, ax, boca_z + curva * (1 - (ax / 10) ** 2) * -1 + 0, 0.005 * r)
               for ax in (-10, -5, 0, 5, 10)]
        if expr != "neutro":
            pts = [ponto_cabeca(c, r, ax, boca_z - 2 + 4 * (1 - (ax / 10) ** 2), 0.005 * r)
                   for ax in (-10, -5, 0, 5, 10)]
        tubo_curva("boca", pts, 0.02 * r, preto, pai=pai)
    elif expr == "desconfiado":
        pts = [ponto_cabeca(c, r, ax, boca_z + (ax + 12) * 0.12 + (2 if ax > 6 else 0), 0.005 * r)
               for ax in (-12, -6, 0, 6, 12)]
        tubo_curva("boca", pts, 0.02 * r, preto, pai=pai)
    elif expr == "feliz":
        # sorriso aberto: meia-lua escura com língua
        boca = ponto_cabeca(c, r, 0, boca_z - 1, -0.02 * r)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.2 * r,
                                             location=boca)
        o = bpy.context.active_object
        o.name = "boca"
        bm = bmesh.new(); bm.from_mesh(o.data)
        apagar = [v for v in bm.verts if v.co.z > 0.0]
        bmesh.ops.delete(bm, geom=apagar, context="VERTS")
        bm.to_mesh(o.data); bm.free()
        o.scale = (1.15, 0.45, 0.9)
        _finalizar(o, mat_toon("boca_escura", (0.25, 0.04, 0.04), 0.4), 0.012, pai)
    elif expr == "chocado":
        boca = ponto_cabeca(c, r, 0, boca_z - 3, -0.01 * r)
        esfera("boca", boca, 0.09 * r, mat_toon("boca_escura", (0.25, 0.04, 0.04), 0.4),
               escala=(0.9, 0.5, 1.2), contorno=0.01, pai=pai)

    if expr == "preocupado":
        gota = ponto_cabeca(c, r, 48, 22, 0.04 * r)
        esfera("gota_suor", gota, 0.07 * r, mat_toon("suor", lin((0.55, 0.82, 1.0)), 0.1),
               escala=(0.8, 0.5, 1.3), contorno=0.01, pai=pai)


def cabelo(c, r, estilo, cor, pai):
    if estilo in (None, "careca"):
        return
    mat = mat_toon("cabelo_" + estilo, cor, 0.7)
    if estilo == "cacheado":
        import random
        rnd = random.Random(7)
        for i in range(70):
            ax = rnd.uniform(-110, 110)
            az = rnd.uniform(25, 88)
            if abs(ax) < 35 and az < 40:
                continue
            p = ponto_cabeca(c, r, ax, az, 0.02 * r)
            # parte de trás da cabeça também
            if rnd.random() < 0.5:
                p = Vector(c) + (p - Vector(c)).reflect(Vector((0, 1, 0))) * 1.0
            esfera("cacho", p, rnd.uniform(0.17, 0.23) * r, mat, contorno=0.012, pai=pai, seg=16)
        return
    # cabelo liso: casca esférica recortada (franja na frente, nuca atrás)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=r * 1.06,
                                         location=c)
    o = bpy.context.active_object
    o.name = "cabelo"
    bm = bmesh.new(); bm.from_mesh(o.data)
    R = r * 1.06
    apagar = []
    for v in bm.verts:
        dy = v.co.y / R  # -1 = frente
        dz = v.co.z / R
        franja = 0.38 if estilo != "topete" else 0.48
        limite = franja * max(0.0, -dy) - 0.35 * max(0.0, dy) + 0.05
        if estilo == "longo":
            # desce até a altura do queixo nas laterais e atrás
            limite = 0.42 * max(0.0, -dy) - 0.75 * max(0.0, dy) - 0.35 * abs(v.co.x / R)
        # franja recortada em "dentinhos" na frente
        if dy < -0.3:
            ang = math.atan2(v.co.x, -v.co.y)
            limite += 0.05 * math.sin(ang * 14)
        if dz < limite:
            apagar.append(v)
    bmesh.ops.delete(bm, geom=apagar, context="VERTS")
    bm.to_mesh(o.data); bm.free()
    o.scale = (1.0, 1.0, 1.02 if estilo != "topete" else 1.12)
    if estilo == "longo":
        o.scale = (1.07, 1.07, 1.03)
    sol = o.modifiers.new("espessura", "SOLIDIFY")
    sol.thickness = 0.06 * r
    _finalizar(o, mat, 0.016, pai)


# ---------------------------------------------------------------- personagem

PRESETS = {
    "jogador_listrado": dict(pele="morena", cabelo="liso", cor_cabelo="preto",
                             uniforme=dict(cor1=hexcor("#1E63B5"), cor2=hexcor("#111111"),
                                           padrao="vertical", freq=10,
                                           cor_calcao=hexcor("#111111"))),
    "jogador_aros": dict(pele="parda", cabelo="cacheado", cor_cabelo="preto",
                         uniforme=dict(cor1=hexcor("#C8102E"), cor2=hexcor("#111111"),
                                       padrao="horizontal", freq=9,
                                       cor_calcao=hexcor("#F2F2F2"))),
    "jogador_liso": dict(pele="clara", cabelo="topete", cor_cabelo="castanho",
                         uniforme=dict(cor1=hexcor("#F4F4F4"), padrao="liso",
                                       cor_calcao=hexcor("#111111"))),
    "vasco": dict(pele="morena", cabelo="liso", cor_cabelo="preto",
                  uniforme=dict(cor1=hexcor("#141414"), cor2=hexcor("#F4F4F4"), padrao="faixa",
                                cor_calcao=hexcor("#141414"))),
    "inter": dict(pele="clara", cabelo="liso", cor_cabelo="castanho",
                  uniforme=dict(cor1=hexcor("#D0102A"), padrao="liso",
                                cor_calcao=hexcor("#F4F4F4"))),
    "goleiro_vasco": dict(pele="parda", cabelo="liso", cor_cabelo="preto",
                          uniforme=dict(cor1=hexcor("#27A844"), padrao="liso",
                                        cor_calcao=hexcor("#1B6E2E"))),
    "goleiro_inter": dict(pele="clara", cabelo="liso", cor_cabelo="castanho",
                          uniforme=dict(cor1=hexcor("#F2D21B"), padrao="liso",
                                        cor_calcao=hexcor("#F2D21B"))),
    "arbitro": dict(pele="clara", cabelo="liso", cor_cabelo="preto",
                    uniforme=dict(cor1=hexcor("#1A1A1A"), padrao="liso",
                                  cor_calcao=hexcor("#1A1A1A")),
                    acessorios=["apito", "cartao_vermelho"]),
    "torcedor": dict(pele="negra", cabelo="cacheado", cor_cabelo="preto",
                     uniforme=dict(cor1=hexcor("#D62828"), padrao="liso",
                                   cor_calcao=hexcor("#2B3A55"), corte_calcao=-0.55),
                     acessorios=["radinho"]),
    "dirigente": dict(pele="clara", cabelo="liso", cor_cabelo="grisalho",
                      uniforme=dict(cor1=hexcor("#3D4350"), padrao="liso",
                                    cor_calcao=hexcor("#2E323C"), corte_calcao=-0.55),
                      acessorios=["gravata", "oculos"]),
    "tecnico": dict(pele="parda", cabelo="liso", cor_cabelo="grisalho",
                    uniforme=dict(cor1=hexcor("#22314F"), padrao="liso",
                                  cor_calcao=hexcor("#22314F")),
                    acessorios=["prancheta"]),
    "narrador": dict(pele="branca", cabelo="topete", cor_cabelo="castanho",
                     uniforme=dict(cor1=hexcor("#2B2D42"), padrao="liso",
                                   cor_calcao=hexcor("#2B2D42"), corte_calcao=-0.6),
                     acessorios=["fone", "cachecol"]),
}


def criar_personagem(nome="p", x=0.0, y=0.0, preset="jogador_liso", expressao="neutro",
                     rot_z=0.0, escala=1.0, **sobrescrever):
    cfg = dict(PRESETS[preset])
    cfg.update(sobrescrever)
    raiz = bpy.data.objects.new(nome, None)
    bpy.context.collection.objects.link(raiz)

    pele = mat_toon("pele_" + cfg["pele"], lin(PELE[cfg["pele"]]), 0.45)
    preto = mat_toon("preto", PRETO, 0.3)
    uni = cfg["uniforme"]
    mat_corpo = mat_uniforme(f"uniforme_{nome}", uni["cor1"], uni.get("cor2"),
                             uni.get("padrao", "liso"), uni.get("freq", 9),
                             uni.get("cor_calcao"), uni.get("corte_calcao", -0.42))

    def junta(nome_j, loc):
        e = bpy.data.objects.new(f"{nome}_{nome_j}", None)
        bpy.context.collection.objects.link(e)
        e.location = loc
        e.parent = raiz
        bpy.context.view_layer.update()
        return e

    quadril = {1: junta("quadril_d", (0.17, 0, 0.95)), -1: junta("quadril_e", (-0.17, 0, 0.95))}
    ombro = {1: junta("ombro_d", (0.45, 0, 1.62)), -1: junta("ombro_e", (-0.45, 0, 1.62))}
    raiz["juntas"] = {"quadril_d": quadril[1].name, "quadril_e": quadril[-1].name,
                      "ombro_d": ombro[1].name, "ombro_e": ombro[-1].name}

    # pernas de palito + chuteiras
    for lado in (-1, 1):
        bastao("perna", (lado * 0.17, 0, 0.12), (lado * 0.17, 0, 0.95), 0.045, preto, pai=quadril[lado])
        esfera("chuteira", (lado * 0.19, -0.06, 0.08), 0.1, preto,
               escala=(0.85, 1.4, 0.6), contorno=0, pai=quadril[lado], seg=16)
    # corpo em cápsula
    corpo = esfera("corpo", (0, 0, 1.4), 1.0, mat_corpo, escala=(0.52, 0.42, 0.62),
                   contorno=0.025, pai=raiz)
    # braços
    acess = cfg.get("acessorios", [])
    mao_d = (0.78, -0.05, 1.05)
    mao_e = (-0.78, -0.05, 1.05)
    if "cartao_vermelho" in acess:
        mao_d = (1.05, -0.3, 2.75)  # braço erguido
    if "radinho" in acess:
        mao_e = (-0.72, -0.25, 2.5)  # rádio no ouvido
    if "prancheta" in acess:
        mao_d = (0.35, -0.55, 1.35)
        mao_e = (-0.25, -0.55, 1.45)
    mao_d = cfg.get("mao_d", mao_d)
    mao_e = cfg.get("mao_e", mao_e)
    bastao("braco_d", (0.45, 0, 1.62), mao_d, 0.04, preto, pai=ombro[1])
    bastao("braco_e", (-0.45, 0, 1.62), mao_e, 0.04, preto, pai=ombro[-1])

    # cabeça
    rc = 0.8
    cc = (0, 0, 2.62)
    esfera("cabeca", cc, rc, pele, contorno=0.025, pai=raiz, seg=64)
    rosto(cc, rc, expressao, raiz)
    cabelo(cc, rc, cfg.get("cabelo"), lin(CABELO[cfg.get("cor_cabelo", "preto")]), raiz)

    # acessórios
    if "apito" in acess:
        amarelo = mat_toon("apito", hexcor("#E8B10A"), 0.25)
        tubo_curva("cordao", [(-0.2, -0.37, 1.95), (0, -0.43, 1.7), (0.2, -0.37, 1.95)],
                   0.012, preto, pai=raiz)
        esfera("apito", (0.02, -0.45, 1.62), 0.07, amarelo, escala=(1.2, 0.8, 0.8),
               contorno=0.01, pai=raiz)
    if "cartao_vermelho" in acess:
        caixa("cartao", (mao_d[0] + 0.05, mao_d[1] - 0.02, mao_d[2] + 0.22),
              (0.2, 0.02, 0.3), mat_toon("cartao", hexcor("#E01E1E"), 0.3), pai=ombro[1])
    if "radinho" in acess:
        caixa("radinho", (mao_e[0] + 0.02, mao_e[1], mao_e[2]), (0.14, 0.3, 0.42),
              mat_toon("radio", hexcor("#C9C1A8"), 0.5), pai=raiz)
        bastao("antena", (mao_e[0] + 0.03, mao_e[1] + 0.08, mao_e[2] + 0.2),
               (mao_e[0] - 0.05, mao_e[1] + 0.1, mao_e[2] + 0.65), 0.012,
               mat_toon("metal", (0.6, 0.6, 0.62), 0.2), pai=raiz)
    if "gravata" in acess:
        caixa("camisa_v", (0, -0.39, 1.72), (0.2, 0.02, 0.38), mat_toon("camisa", (0.95, 0.95, 0.95)),
              contorno=0, pai=raiz)
        caixa("gravata", (0, -0.415, 1.66), (0.07, 0.02, 0.42), mat_toon("gravata", hexcor("#B3202A")),
              contorno=0.008, pai=raiz)
    if "oculos" in acess:
        for lado in (-1, 1):
            p = ponto_cabeca(cc, rc, lado * 20, 8, 0.03)
            bpy.ops.mesh.primitive_torus_add(major_radius=0.15, minor_radius=0.018,
                                             location=p, rotation=(math.radians(90), 0, 0))
            o = bpy.context.active_object; o.name = "lente"
            _finalizar(o, preto, 0, raiz)
        tubo_curva("ponte", [ponto_cabeca(cc, rc, -8, 9, 0.04), ponto_cabeca(cc, rc, 8, 9, 0.04)],
                   0.016, preto, pai=raiz)
    if "prancheta" in acess:
        caixa("prancheta", (0.05, -0.62, 1.5), (0.55, 0.04, 0.7), mat_toon("prancheta", hexcor("#8A5A2B")),
              rot=(math.radians(-15), 0, 0), pai=raiz)
        caixa("papel", (0.05, -0.65, 1.47), (0.45, 0.02, 0.55), mat_toon("papel", (0.97, 0.97, 0.95)),
              rot=(math.radians(-15), 0, 0), contorno=0, pai=raiz)
    if "fone" in acess:
        verde = mat_toon("fone", hexcor("#D9773A"), 0.35)  # laranja Claude
        arco = [Vector(cc) + Vector((math.cos(a) * rc * 1.1, 0.02, math.sin(a) * rc * 1.12))
                for a in [math.radians(t) for t in range(0, 181, 15)]]
        tubo_curva("arco_fone", arco, 0.035, preto, pai=raiz)
        for lado in (-1, 1):
            esfera("concha", (lado * rc * 1.05, 0.0, cc[2] - 0.02), 0.17, verde,
                   escala=(0.6, 1, 1), contorno=0.015, pai=raiz)
        tubo_curva("haste_mic", [(-rc * 1.05, -0.05, cc[2] - 0.1), (-0.55, -0.45, cc[2] - 0.3),
                                 (-0.25, -0.66, cc[2] - 0.32)], 0.018, preto, pai=raiz)
        esfera("mic", (-0.22, -0.68, cc[2] - 0.32), 0.06, preto, contorno=0, pai=raiz)
    if "cachecol" in acess:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.36, minor_radius=0.1,
                                         location=(0, 0, 1.92))
        o = bpy.context.active_object; o.name = "cachecol"; o.scale = (1, 0.85, 1)
        _finalizar(o, mat_toon("cachecol", hexcor("#D9773A"), 0.7), 0.02, raiz)
        caixa("ponta_cachecol", (0.18, -0.36, 1.68), (0.16, 0.06, 0.45),
              mat_toon("cachecol", hexcor("#D9773A"), 0.7), rot=(0, math.radians(-10), 0), pai=raiz)

    raiz.location = (x, y, 0)
    raiz.rotation_euler = (0, 0, math.radians(rot_z))
    raiz.scale = (escala,) * 3
    return raiz


# ---------------------------------------------------------------- luz e câmera

def luz_estudio(fundo=(0.80, 0.86, 0.93), chao=True, cor_chao=(0.72, 0.76, 0.82)):
    mundo = bpy.data.worlds.new("mundo")
    bpy.context.scene.world = mundo
    mundo.use_nodes = True
    mundo.node_tree.nodes["Background"].inputs[0].default_value = (*lin(fundo), 1)
    mundo.node_tree.nodes["Background"].inputs[1].default_value = 0.9
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(-50), math.radians(-15), math.radians(-20)))
    sol = bpy.context.active_object; sol.data.energy = 3.2; sol.data.angle = math.radians(8)
    bpy.ops.object.light_add(type="AREA", location=(-4, -6, 6))
    pre = bpy.context.active_object; pre.data.energy = 900; pre.data.size = 6
    pre.rotation_euler = (math.radians(55), 0, math.radians(-35))
    if chao:
        bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
        c = bpy.context.active_object
        c.data.materials.append(mat_toon("chao", lin(cor_chao), 0.8))
        para_cenario(c)


def para_cenario(obj):
    """Move o objeto para a coleção 'cenario' (sem contorno do Freestyle)."""
    cen = bpy.data.collections["cenario"]
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    cen.objects.link(obj)
    return obj


def camera(loc, alvo, lente=50, ortho=None):
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.active_object
    d = Vector(alvo) - Vector(loc)
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = d.to_track_quat("-Z", "Y")
    cam.data.lens = lente
    if ortho:
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = ortho
    bpy.context.scene.camera = cam
    return cam


def renderizar(caminho, larg=1920, alt=1080, amostras=48):
    cena = bpy.context.scene
    cena.render.resolution_x = larg
    cena.render.resolution_y = alt
    cena.render.resolution_percentage = 100
    cena.cycles.samples = amostras
    cena.render.filepath = caminho
    cena.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
