"""Lances do vídeo completo Vasco 2 x 1 Inter (Brasileirão 2026), 9:16.

Uso:
    python lances.py <lance> <pasta_saida> [amostras] [largura]
    lance: A (chance do Bruno Duarte), C (empate do Inter), D (gol do Coutinho),
           E (pressão final), F (tela final)
    QUADROS=10,40 python lances.py A pasta  -> só renderiza esses quadros (prévia)

Cada lance é sincronizado com um trecho do áudio original (ver montar_completo.py).
O 1º gol (bloco B) é o teste já renderizado em cena_gol_teste.py.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import personagens as P
import estadio as E

FPS = 12
CAB = 2.62 + 0.8 - 0.15  # altura da bola num cabeceio (personagem em pé)


def q(t):
    return int(round(t * FPS)) + 1


def rumo(de, para):
    dx, dy = para[0] - de[0], para[1] - de[1]
    return math.degrees(math.atan2(dx, -dy))


def junta(r, nome):
    return bpy.data.objects[r["juntas"][nome]]


def kf(obj, attr, frame, valor, idx=None):
    if idx is None:
        setattr(obj, attr, valor)
        obj.keyframe_insert(attr, frame=frame)
    else:
        getattr(obj, attr)[idx] = valor
        obj.keyframe_insert(attr, index=idx, frame=frame)


class Caminho:
    """Trajetória linear por partes: [(t, (x, y)), ...]."""

    def __init__(self, pontos):
        self.p = [(t, Vector((x, y))) for t, (x, y) in pontos]

    def pos(self, t):
        p = self.p
        if t <= p[0][0]:
            return p[0][1].copy()
        for (t0, a), (t1, b) in zip(p, p[1:]):
            if t <= t1:
                u = (t - t0) / (t1 - t0) if t1 > t0 else 1
                return a.lerp(b, u)
        return p[-1][1].copy()

    def vel(self, t, dt=0.05):
        return (self.pos(t + dt) - self.pos(t - dt)) / (2 * dt)

    def dir(self, t):
        v = self.vel(t)
        return v.normalized() if v.length > 1e-3 else Vector((1, 0))


_ang = {}


def mover(raiz, cam, t0, t1, olhar=None, freq=2.6, correndo=True):
    """Desloca o personagem pelo caminho, com pernas/braços de corrida."""
    qd, qe = junta(raiz, "quadril_d"), junta(raiz, "quadril_e")
    od, oe = junta(raiz, "ombro_d"), junta(raiz, "ombro_e")
    for f in range(q(t0), q(t1) + 1):
        t = (f - 1) / FPS
        p = cam.pos(t)
        v = cam.vel(t)
        kf(raiz, "location", f, p.x, 0)
        kf(raiz, "location", f, p.y, 1)
        if olhar is not None:
            alvo = olhar(t) if callable(olhar) else olhar
            ang = math.radians(rumo(p, alvo))
        elif v.length > 0.3:
            ang = math.radians(rumo(p, p + v))
        else:
            ang = _ang.get(raiz.name, raiz.rotation_euler[2])
        ant = _ang.get(raiz.name, ang)
        while ang - ant > math.pi:
            ang -= 2 * math.pi
        while ang - ant < -math.pi:
            ang += 2 * math.pi
        _ang[raiz.name] = ang
        kf(raiz, "rotation_euler", f, ang, 2)
        veloc = min(1.0, v.length / 5.0) if correndo else 0.0
        fase = math.sin(2 * math.pi * freq * t)
        a = 0.75 * veloc * fase
        kf(qd, "rotation_euler", f, a, 0)
        kf(qe, "rotation_euler", f, -a, 0)
        kf(od, "rotation_euler", f, -0.8 * a, 0)
        kf(oe, "rotation_euler", f, 0.8 * a, 0)
        kf(raiz, "location", f, 0.14 * veloc * abs(fase), 2)


def chute(raiz, t, perna="d"):
    qd = junta(raiz, "quadril_" + perna)
    qo = junta(raiz, "quadril_" + ("e" if perna == "d" else "d"))
    for dt, a, b in ((-0.35, 0, 0), (-0.15, 0.8, -0.15), (0, -1.15, 0.15), (0.25, -0.5, 0.05), (0.55, 0, 0)):
        kf(qd, "rotation_euler", q(t + dt), a, 0)
        kf(qo, "rotation_euler", q(t + dt), b, 0)
    oe = junta(raiz, "ombro_e" if perna == "d" else "ombro_d")
    for dt, a in ((-0.35, 0), (0, 0.9 if perna == "d" else -0.9), (0.55, 0)):
        kf(oe, "rotation_euler", q(t + dt), -a, 1)
    for dt, z in ((-0.15, 0), (0, 0.2), (0.25, 0)):
        kf(raiz, "location", q(t + dt), z, 2)


def pulo(raiz, t_pico, altura=1.5, dur=0.9, bracos=True):
    pts = ((t_pico - dur / 2, 0), (t_pico - dur / 4, altura * 0.8), (t_pico, altura),
           (t_pico + dur / 4, altura * 0.8), (t_pico + dur / 2, 0))
    for t, z in pts:
        kf(raiz, "location", q(t), z, 2)
    if bracos:
        od, oe = junta(raiz, "ombro_d"), junta(raiz, "ombro_e")
        for t, a in ((t_pico - dur / 2, 0), (t_pico, 1.1), (t_pico + dur / 2, 0.1)):
            kf(od, "rotation_euler", q(t), a, 1)
            kf(oe, "rotation_euler", q(t), -a, 1)

    def z(t):
        for (t0, z0), (t1, z1) in zip(pts, pts[1:]):
            if t0 <= t <= t1:
                return z0 + (z1 - z0) * (t - t0) / (t1 - t0)
        return 0.0
    return z


def mergulho(raiz, rot_z, base, t_ini, t_voo, dy, t_fim=None, cai=True):
    """Goleiro salta para o lado (dy > 0: para +y no mundo)."""
    s = 1 if dy * math.sin(math.radians(rot_z)) > 0 else -1
    pts = [(t_ini, 0, 0, 0), (t_ini + 0.3, 0.15 * s, dy * 0.15, 0.4),
           (t_voo, 1.35 * s, dy * 0.8, 1.5), (t_voo + 0.45, 1.5 * s, dy, 0.6),
           (t_voo + 0.85, 1.55 * s, dy * 1.05, 0.35)]
    if t_fim:
        pts.append((t_fim, 1.55 * s, dy * 1.05, 0.35))
    for t, rot, d, z in pts:
        kf(raiz, "rotation_euler", q(t), rot, 1)
        kf(raiz, "location", q(t), base[1] + d, 1)
        kf(raiz, "location", q(t), z, 2)


def arco(p1, p2, u, pico):
    p1, p2 = Vector(p1), Vector(p2)
    p = p1.lerp(p2, max(0.0, min(1.0, u)))
    p.z += 4 * pico * u * (1 - u)
    return p


def conduz(cam, t, freq=2.6):
    p = cam.pos(t)
    d = cam.dir(t)
    return Vector((p.x + d.x * 0.95, p.y + d.y * 0.95, 0.38 + 0.12 * abs(math.sin(2 * math.pi * freq * t))))


class Trajeto:
    """Bola: lista de (t_fim, função(t)) avaliada por trechos."""

    def __init__(self):
        self.trechos = []

    def add(self, t_fim, fn):
        self.trechos.append((t_fim, fn))

    def __call__(self, t):
        for t_fim, fn in self.trechos:
            if t <= t_fim:
                return fn(t)
        return self.trechos[-1][1](t)


def anima_bola(bola, traj, dur, giro=9.0):
    for f in range(1, q(dur) + 2):
        t = (f - 1) / FPS
        bola.location = traj(t)
        bola.keyframe_insert("location", frame=f)
        bola.rotation_euler.x = t * giro
        bola.keyframe_insert("rotation_euler", index=0, frame=f)


cams = []


def _aponta(cam, pos, alvo):
    cam.location = pos
    cam.rotation_quaternion = (Vector(alvo) - Vector(pos)).to_track_quat("-Z", "Y")


def plano(cena, nome, t0, t1, pos0, pos1, alvo0, alvo1, lente=32):
    cam = P.camera(pos0, alvo0, lente=lente)
    cam.name = nome
    for t, pos, alvo in ((t0, pos0, alvo0), (t1, pos1, alvo1)):
        _aponta(cam, pos, alvo)
        cam.keyframe_insert("location", frame=q(t))
        cam.keyframe_insert("rotation_quaternion", frame=q(t))
    cena.timeline_markers.new(nome, frame=q(t0)).camera = cam
    cams.append(cam)


def plano_segue(cena, nome, t0, t1, alvo_fn, offset, olhar_offset=(0, 0, 1.8), lente=30):
    """Câmera que acompanha um ponto móvel (corrida com a bola)."""
    cam = P.camera((0, 0, 0), (1, 0, 0), lente=lente)
    cam.name = nome
    for f in range(q(t0), q(t1) + 1, 2):
        t = (f - 1) / FPS
        a = alvo_fn(t)
        a = Vector((a.x, a.y, 0))
        _aponta(cam, a + Vector(offset), a + Vector(olhar_offset))
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_quaternion", frame=f)
    cena.timeline_markers.new(nome, frame=q(t0)).camera = cam
    cams.append(cam)


def novo(nome, x, y, preset, expr="neutro", olhar=None, rot_z=0.0, **kw):
    if olhar is not None:
        rot_z = rumo((x, y), olhar)
    r = P.criar_personagem(nome, x, y, preset=preset, expressao=expr, rot_z=rot_z, **kw)
    _ang[r.name] = math.radians(rot_z)
    return r


BRACOS_CIMA = dict(mao_d=(0.85, -0.1, 2.9), mao_e=(-0.85, -0.1, 2.9))
MAOS_CABECA = dict(mao_d=(0.72, -0.25, 3.05), mao_e=(-0.72, -0.25, 3.05))


def comemoracao(base, preset, jogadores, t0, t1):
    """3 jogadores pulando com braços para cima, de frente para a câmera (-y)."""
    rs = []
    for i, (dx, dy, rz, kw) in enumerate(jogadores):
        r = novo(f"cel_{preset}_{i}", base[0] + dx, base[1] + dy, preset, "feliz", rot_z=rz, **kw)
        rs.append(r)
        for f in range(q(t0), q(t1) + 1, 2):
            t = (f - 1) / FPS
            ph = i * 0.33
            kf(r, "location", f, 0.45 * abs(math.sin((t * 2.6 + ph) * math.pi)), 2)
            for nj, sg in (("ombro_d", 1), ("ombro_e", -1)):
                kf(junta(r, nj), "rotation_euler", f, sg * 0.22 * math.sin((t * 3 + ph) * 2 * math.pi), 1)
    return rs


def plano_placar(cena, est, nome, t0, t1):
    px, py, pz = est.placar_x, est.placar_y, est.placar_z
    plano(cena, nome, t0, t1, (px, py - 26, pz - 1), (px, py - 19, pz), (px, py, pz), (px, py, pz), lente=40)


def plano_close(cena, nome, base, t0, t1):
    plano(cena, nome, t0, t1, (base[0], base[1] - 7.5, 3.0), (base[0], base[1] - 5.3, 3.0),
          (base[0], base[1], 2.75), (base[0], base[1], 2.85), lente=32)


# ====================================================================== LANCE A
def lance_A(cena):
    """Chance do Bruno Duarte (áudio 0:11.5 a 0:30.0)."""
    DUR = 18.5
    est = E.construir(cena, FPS, DUR, placares=[(0, "VAS 0 x 0 INT")], relogio="1º T")
    CX = est.CX
    bruno_cam = Caminho([(0, (6, -7.5)), (7.4, (48.6, -3.4)), (10.9, (48.6, -3.4)),
                         (12.7, (53.2, 2.4)), (DUR, (53.2, 2.4))])
    bruno = novo("bruno", 6, -7.5, "vasco", "neutro", olhar=(20, -6), pele="parda", cabelo="topete",
                 cor_cabelo="preto")
    mover(bruno, bruno_cam, 0, 7.45)
    mover(bruno, bruno_cam, 7.45, 7.5, olhar=(CX, -1.5), correndo=False)
    chute(bruno, 7.75)
    mover(bruno, bruno_cam, 10.9, 12.75)
    mover(bruno, bruno_cam, 12.8, 12.9, olhar=(CX, 6.5), correndo=False)
    chute(bruno, 14.5)
    marc_cam = Caminho([(0, (2, -4.5)), (7.4, (45.0, -1.2)), (8.6, (46.5, -0.4)), (DUR, (46.5, -0.4))])
    marc = novo("marcador", 2, -4.5, "inter", "preocupado", olhar=(20, -4), pele="morena", cabelo="liso")
    mover(marc, marc_cam, 0, 8.6)
    for nome, x, y, pre, ex, kw in (("vasco_apoio", 30, 8, "vasco", "neutro", dict(pele="clara")),
                                    ("inter_lat", 38, -14, "inter", "chocado", dict(pele="parda", cabelo="careca"))):
        novo(nome, x, y, pre, ex, olhar=(45, 0), **kw)
    gol_cam = Caminho([(0, (CX - 1.6, 0)), (6.3, (CX - 1.6, 0)), (7.5, (CX - 5.2, -1.6)), (DUR, (CX - 5.2, -1.6))])
    gol = novo("goleiro", CX - 1.6, 0, "goleiro_inter", "preocupado", olhar=(40, 0),
               mao_d=(0.85, -0.2, 1.9), mao_e=(-0.85, -0.2, 1.9))
    mover(gol, gol_cam, 6.2, 7.55, olhar=(40, -3))
    rz = math.degrees(_ang[gol.name])
    mergulho(gol, rz, (CX - 5.2, -1.6), 7.55, 7.9, -1.4, t_fim=DUR)

    pe1 = conduz(bruno_cam, 7.45)
    p_def = Vector((CX - 5.6, -2.4, 0.7))
    p_reb = Vector((52.4, 3.6, 0.38))
    p_para = Vector((54.1, 2.6, 0.38))
    p_fora = Vector((CX + 1.5, 9.8, 1.6))
    p_fim = Vector((CX + 5.5, 12.5, 0.38))
    tr = Trajeto()
    tr.add(7.45, lambda t: conduz(bruno_cam, t))
    tr.add(7.75, lambda t: pe1)
    tr.add(7.98, lambda t: arco(pe1, p_def, (t - 7.75) / 0.23, 0.2))
    tr.add(9.2, lambda t: arco(p_def, p_reb, (t - 7.98) / 1.22, 2.6))
    tr.add(10.6, lambda t: p_reb.lerp(p_para, (t - 9.2) / 1.4))
    tr.add(14.5, lambda t: p_para)
    tr.add(15.25, lambda t: arco(p_para, p_fora, (t - 14.5) / 0.75, 1.0))
    tr.add(16.2, lambda t: arco(p_fora, p_fim, (t - 15.25) / 0.95, 0.4))
    tr.add(DUR + 1, lambda t: p_fim)
    anima_bola(est.bola, tr, DUR)

    BR = (20.0, 31.0)
    novo("bruno_close", *BR, "vasco", "chocado", rot_z=0, pele="parda", cabelo="topete", **MAOS_CABECA)

    plano(cena, "aereo", 0.0, 2.5, (-95, -120, 85), (-72, -95, 60), (0, 0, 0), (15, 0, 0), lente=28)
    plano_segue(cena, "corrida", 2.5, 5.0, bruno_cam.pos, (-3, -14, 4.5), (4, 0, 1.8))
    plano(cena, "cara_a_cara", 5.0, 8.6, (29, -13, 5.6), (33.5, -11.5, 5.0), (CX - 4, -1.5, 2.0), (CX - 4, -1, 1.8))
    plano(cena, "torcida", 8.6, 11.0, (-6, est.CY - 12, 3.5), (2, est.CY - 11, 4.0),
          (-6, est.CY + 12, 7.0), (2, est.CY + 12, 7.5), lente=30)
    plano(cena, "rebote", 11.0, 15.9, (45.5, -7.5, 3.4), (46.5, -6.5, 3.2), (53.5, 2.5, 2.0), (CX, 7.0, 2.0), lente=30)
    plano_close(cena, "lamento", BR, 15.9, DUR)
    return DUR


# ====================================================================== LANCE C
def lance_C(cena):
    """Empate do Inter (áudio 1:39.0-1:48.0 + 1:52.6-1:58.0)."""
    DUR = 14.1
    est = E.construir(cena, FPS, DUR, placares=[(0, "VAS 1 x 0 INT"), (8.4, "VAS 1 x 1 INT")], relogio="1º T")
    CX = est.CX
    alan_cam = Caminho([(0, (-33, -25)), (3.4, (-45, -30.5)), (DUR, (-45, -30.5))])
    alan = novo("alan", -33, -25, "inter", "neutro", olhar=(-45, -30), pele="clara", cabelo="topete",
                cor_cabelo="castanho")
    mover(alan, alan_cam, 0, 3.45)
    mover(alan, alan_cam, 3.45, 3.5, olhar=(-55, 2), correndo=False)
    chute(alan, 3.8)
    aj = novo("inter_ajeita", -55.5, 2.5, "inter", "neutro", olhar=(-50, -1), pele="negra", cabelo="cacheado")
    pulo(aj, 5.0, 1.0)
    fin = novo("inter_finaliza", -51.2, -1.4, "inter", "neutro", olhar=(-CX, -3.5), pele="morena", cabelo="liso")
    chute(fin, 7.4)
    for nome, x, y, ex, kw in (("vas_z1", -54.3, 4.2, "preocupado", dict(pele="clara")),
                               ("vas_z2", -52.6, -4.3, "chocado", dict(pele="negra", cabelo="careca"))):
        r = novo(nome, x, y, "vasco", ex, olhar=(-45, -20), **kw)
    pulo(bpy.data.objects["vas_z1"], 5.0, 0.8)
    gol = novo("goleiro_vasco", -CX + 1.6, 0.3, "goleiro_vasco", "preocupado", olhar=(-40, -10),
               mao_d=(0.85, -0.2, 1.9), mao_e=(-0.85, -0.2, 1.9))
    rz = math.degrees(_ang[gol.name])
    mergulho(gol, rz, (-CX + 1.6, 0.3), 7.45, 7.85, -3.0, t_fim=DUR)

    pe = conduz(alan_cam, 3.45)
    p_cab = Vector((-55.5, 2.5, CAB + 1.0))
    p_aj = Vector((-51.0, -1.0, 0.38))
    p_rede = Vector((-CX - 1.2, -4.0, 1.6))
    p_chao = Vector((-CX - 2.6, -4.4, 0.38))
    tr = Trajeto()
    tr.add(3.45, lambda t: conduz(alan_cam, t))
    tr.add(3.8, lambda t: pe)
    tr.add(5.0, lambda t: arco(pe, p_cab, (t - 3.8) / 1.2, 5.0))
    tr.add(5.9, lambda t: arco(p_cab, p_aj, (t - 5.0) / 0.9, 1.0))
    tr.add(7.4, lambda t: p_aj)
    tr.add(7.95, lambda t: arco(p_aj, p_rede, (t - 7.4) / 0.55, 0.5))
    tr.add(8.6, lambda t: arco(p_rede, p_chao, (t - 7.95) / 0.65, 0.2))
    tr.add(DUR + 1, lambda t: p_chao)
    anima_bola(est.bola, tr, DUR)

    CEL = (-10.0, 31.0)
    comemoracao(CEL, "inter", [(0, 0, 0, dict(pele="morena", **BRACOS_CIMA)),
                               (-2.1, 0.8, -15, dict(pele="negra", cabelo="cacheado", mao_d=(0.8, -0.3, 2.6), mao_e=(-0.95, 0, 1.4))),
                               (2.2, 0.9, 18, dict(pele="clara", cabelo="topete", mao_d=(0.95, 0, 1.4), mao_e=(-0.8, -0.3, 2.7)))],
                8.4, 11.6)

    plano_segue(cena, "ala_esquerda", 0.0, 2.3, alan_cam.pos, (4, -9, 4.0), (-3, 0, 1.8))
    plano(cena, "cruzamento", 2.3, 5.8, (-36, -38, 4.2), (-38, -36, 4.6), (-46, -29, 1.6), (-55, 1, 3.0), lente=28)
    plano(cena, "finalizacao", 5.8, 8.7, (-40, -9, 4.0), (-42, -8, 3.6), (-52, -1.5, 2.0), (-CX, -3, 2.0), lente=30)
    plano(cena, "comemoracao_inter", 8.7, 11.5, (CEL[0] + 0.5, CEL[1] - 10, 3.3), (CEL[0] + 0.3, CEL[1] - 8, 3.0),
          (CEL[0], CEL[1], 2.6), (CEL[0], CEL[1], 2.7))
    plano_placar(cena, est, "placar_1x1", 11.5, DUR)
    return DUR


# ====================================================================== LANCE D
def lance_D(cena):
    """Gol do Coutinho (áudio 2:27.6-2:46.0 + 3:00.6-3:04.4)."""
    DUR = 21.9
    est = E.construir(cena, FPS, DUR, placares=[(0, "VAS 1 x 1 INT"), (13.3, "VAS 2 x 1 INT")], relogio="2º T")
    CX = est.CX
    and_cam = Caminho([(0, (12, -28.5)), (2.0, (18.5, -29.5)), (6.0, (37, -29.5)), (8.0, (51.5, -27.5)),
                       (9.0, (55.5, -18.5)), (DUR, (55.5, -18.5))])
    andres = novo("andres", 12, -28.5, "vasco", "neutro", olhar=(20, -30), pele="negra", cabelo="cacheado")
    mover(andres, and_cam, 0, 9.0)
    mover(andres, and_cam, 9.0, 9.05, olhar=(41, -3.5), correndo=False)
    chute(andres, 9.15)
    agu_cam = Caminho([(0, (9, -25.5)), (2.0, (16, -27.6)), (6.0, (35.5, -27.9)), (7.6, (42, -27.2)),
                       (9.0, (44.5, -26.0)), (DUR, (44.5, -26.0))])
    aguirre = novo("aguirre", 9, -25.5, "inter", "preocupado", olhar=(20, -28), pele="clara", cabelo="liso",
                   cor_cabelo="preto")
    mover(aguirre, agu_cam, 0, 9.0, freq=2.4)
    cou_cam = Caminho([(0, (40.2, -3.0)), (10.6, (40.2, -3.0)), (11.1, (41.0, -3.3)), (DUR, (41.0, -3.3))])
    cout = novo("coutinho", 40.2, -3.0, "vasco", "neutro", olhar=(55, -18), pele="morena", cabelo="liso")
    mover(cout, cou_cam, 10.55, 11.15, olhar=(CX, -4.5), correndo=False)
    chute(cout, 12.5)
    novo("thiago", 50, 6, "vasco", "neutro", olhar=(45, -10), pele="clara", cabelo="longo")
    novo("zag_inter", 47, 1.5, "inter", "chocado", olhar=(42, -3), pele="parda", cabelo="careca")
    novo("vol_inter", 36.5, 1.0, "inter", "preocupado", olhar=(41, -3), pele="morena", cabelo="cacheado")
    gol = novo("goleiro", CX - 1.6, -1.0, "goleiro_inter", "preocupado", olhar=(40, -5),
               mao_d=(0.85, -0.2, 1.9), mao_e=(-0.85, -0.2, 1.9))
    rz = math.degrees(_ang[gol.name])
    mergulho(gol, rz, (CX - 1.6, -1.0), 12.55, 12.95, -3.6, t_fim=DUR)

    p_lanc = Vector((-4, -12, 0.38))
    p_rec = conduz(and_cam, 2.0)
    pe = conduz(and_cam, 9.0)
    p_cou = Vector((41.0, -3.1, 0.38))
    p_aj = Vector((41.9, -3.4, 0.38))
    p_rede = Vector((CX + 1.2, -5.6, 0.8))
    p_chao = Vector((CX + 2.6, -5.9, 0.38))
    tr = Trajeto()
    tr.add(2.0, lambda t: arco(p_lanc, p_rec, t / 2.0, 8.0))
    tr.add(9.0, lambda t: conduz(and_cam, t))
    tr.add(9.15, lambda t: pe)
    tr.add(10.5, lambda t: arco(pe, p_cou, (t - 9.15) / 1.35, 0.15))
    tr.add(11.1, lambda t: p_cou.lerp(p_aj, (t - 10.5) / 0.6))
    tr.add(12.5, lambda t: p_aj)
    tr.add(13.25, lambda t: arco(p_aj, p_rede, (t - 12.5) / 0.75, 0.8))
    tr.add(13.9, lambda t: arco(p_rede, p_chao, (t - 13.25) / 0.65, 0.2))
    tr.add(DUR + 1, lambda t: p_chao)
    anima_bola(est.bola, tr, DUR)

    CEL = (10.0, 31.0)
    comemoracao(CEL, "vasco", [(0, 0, 0, dict(pele="morena", **BRACOS_CIMA)),
                               (-2.1, 0.8, -15, dict(pele="negra", cabelo="cacheado", mao_d=(0.8, -0.3, 2.6), mao_e=(-0.95, 0, 1.4))),
                               (2.2, 0.9, 18, dict(pele="clara", cabelo="longo", mao_d=(0.95, 0, 1.4), mao_e=(-0.8, -0.3, 2.7)))],
                13.5, 16.8)
    CL = (-12.0, 31.0)
    r = novo("coutinho_close", *CL, "vasco", "feliz", rot_z=0, pele="morena", mao_d=(0.9, -0.3, 2.4), mao_e=(-0.6, -0.35, 1.25))
    for f in range(q(18.0), q(DUR) + 1, 2):
        t = (f - 1) / FPS
        kf(junta(r, "ombro_d"), "rotation_euler", f, 0.25 * math.sin(t * 2 * math.pi * 1.5), 1)

    plano(cena, "lancamento", 0.0, 2.4, (4, -40, 13), (8, -40, 11), (10, -24, 2), (18, -29, 1.5), lente=30)
    plano_segue(cena, "corrida_ala", 2.4, 5.2, and_cam.pos, (-2, -9.5, 3.6), (3, 1, 1.8))
    plano_segue(cena, "duelo", 5.2, 8.6, and_cam.pos, (5, -8, 3.0), (-1, 0.5, 1.9))
    plano(cena, "passe_atras", 8.6, 10.7, (CX + 1, -27, 5.0), (CX, -26, 4.6), (53, -19, 1.8), (42, -4, 1.8), lente=28)
    plano(cena, "chute_coutinho", 10.7, 14.4, (31, -10, 4.0), (33, -9, 3.8), (41, -3.2, 2.2), (CX, -4.5, 2.2), lente=30)
    plano(cena, "comemoracao_vasco", 14.4, 16.7, (CEL[0] + 0.5, CEL[1] - 10, 3.3), (CEL[0] + 0.3, CEL[1] - 8, 3.0),
          (CEL[0], CEL[1], 2.6), (CEL[0], CEL[1], 2.7))
    plano_placar(cena, est, "placar_2x1", 16.7, 18.1)
    plano_close(cena, "coutinho_fera", CL, 18.1, DUR)
    return DUR


# ====================================================================== LANCE E
def lance_E(cena):
    """Pressão final do Inter (áudio 4:19.0-4:28.3 + 4:31.9-4:38.4)."""
    DUR = 15.5
    est = E.construir(cena, FPS, DUR, placares=[(0, "VAS 2 x 1 INT")], relogio="48'")
    CX = est.CX
    BOLA0 = Vector((-40.0, 24.0, 0.38))
    alan_cam = Caminho([(0, (-38.6, 25.4)), (4.5, (-38.6, 25.4)), (5.0, (-39.4, 24.6)), (7.6, (-39.4, 24.6)),
                        (8.9, (-42.3, 24.8)), (DUR, (-42.3, 24.8))])
    alan = novo("alan", -38.6, 25.4, "inter", "neutro", olhar=(-55, 2), pele="clara", cabelo="topete",
                cor_cabelo="castanho")
    mover(alan, alan_cam, 4.4, 4.95, olhar=(-55, 2))
    chute(alan, 5.0)
    mover(alan, alan_cam, 7.6, 8.9, olhar=lambda t: (-43, 24))
    mover(alan, alan_cam, 8.9, 8.95, olhar=(-58.5, -5.5), correndo=False)
    chute(alan, 9.1)
    sald = novo("saldivia", -55.2, 1.6, "vasco", "bravo", olhar=(-40, 24), pele="clara", cabelo="liso")
    pulo(sald, 7.6, 1.5)
    for nome, x, y, pre, ex, kw in (("vas2", -53, -3, "vasco", "preocupado", dict(pele="negra")),
                                    ("vas3", -56.8, -5.0, "vasco", "neutro", dict(pele="parda", cabelo="cacheado")),
                                    ("int2", -54.0, 3.4, "inter", "neutro", dict(pele="morena")),
                                    ("int3", -52.4, -1.4, "inter", "neutro", dict(pele="clara", cabelo="careca"))):
        novo(nome, x, y, pre, ex, olhar=(-40, 20), **kw)
    cab = novo("inter_cabeceia", -58.5, -5.5, "inter", "bravo", olhar=(-CX, -1), pele="negra", cabelo="cacheado")
    pulo(cab, 10.75, 1.4)
    gk_cam = Caminho([(0, (-CX + 1.6, 0.5)), (10.6, (-CX + 1.6, 0.5)), (11.0, (-CX + 1.9, -0.9)), (DUR, (-CX + 1.9, -0.9))])
    gk = novo("goleiro_vasco", -CX + 1.6, 0.5, "goleiro_vasco", "bravo", olhar=(-40, 15), **BRACOS_CIMA)
    mover(gk, gk_cam, 10.5, 11.05, olhar=(-58, -5))
    zgk = pulo(gk, 11.4, 1.3, dur=1.0, bracos=False)
    mover(gk, gk_cam, 11.95, 12.0, olhar=(-40, 0), correndo=False)

    p_sald = Vector((-55.2, 1.6, CAB + 1.5))
    p_afast = Vector((-42.6, 24.3, 0.38))
    pe2 = Vector((-42.9, 24.1, 0.38))
    p_cab = Vector((-58.5, -5.5, CAB + 1.4))
    p_maos = lambda t: Vector((-CX + 1.9 + 0.55, -0.9, 3.2 + zgk(t)))
    tr = Trajeto()
    tr.add(5.0, lambda t: BOLA0)
    tr.add(7.6, lambda t: arco(BOLA0, p_sald, (t - 5.0) / 2.6, 6.0))
    tr.add(8.95, lambda t: arco(p_sald, p_afast, (t - 7.6) / 1.35, 5.0))
    tr.add(9.1, lambda t: pe2)
    tr.add(10.75, lambda t: arco(pe2, p_cab, (t - 9.1) / 1.65, 7.0))
    tr.add(11.4, lambda t: arco(p_cab, p_maos(11.4), (t - 10.75) / 0.65, 0.4))
    tr.add(DUR + 1, lambda t: p_maos(t) if t < 11.95 else Vector((-CX + 1.9 + 0.5, -0.9 - 0.05, 1.9)))
    anima_bola(est.bola, tr, DUR)

    plano_placar(cena, est, "placar_48", 0.0, 1.6)
    plano(cena, "area", 1.6, 4.3, (-44, 9, 4.5), (-45, 7.5, 4.2), (-55, 0, 2.5), (-55, 0, 2.5), lente=28)
    plano(cena, "cobranca", 4.3, 8.9, (-33, 31, 4.6), (-35, 30, 5.2), (-40, 24, 1.5), (-54, 3, 3.5), lente=28)
    plano(cena, "segunda_trave", 8.9, 12.0, (-47, -17, 5.0), (-48, -16, 4.8), (-52, -2, 3.0), (-CX + 2, -1.5, 3.5), lente=28)
    plano(cena, "goleiro_pegou", 12.0, DUR, (-CX + 7.5, 6.5, 3.4), (-CX + 6.5, 5.5, 3.1),
          (-CX + 1.9, -0.9, 2.6), (-CX + 1.9, -0.9, 2.6), lente=32)
    return DUR


# ====================================================================== LANCE F
def lance_F(cena):
    """Tela final: placar FIM DE JOGO + mascote do canal acenando."""
    DUR = 4.0
    est = E.construir(cena, FPS, DUR, placares=[(0, "VAS 2 x 1 INT")], relogio="FIM", torcida_pula=1.6)
    amarelo = P.mat_toon("titulo", P.hexcor("#FFD23F"), 0.3, emissao=3.0)
    est.texto("FIM DE JOGO", (est.placar_x, est.placar_y - 0.5, est.placar_z + 7.0), 4.2, amarelo, "fim")
    M = (0.0, 36.0)
    m = novo("mascote", *M, "narrador", "feliz", rot_z=0, mao_d=(0.9, -0.2, 2.9))
    for f in range(1, q(DUR) + 1, 2):
        t = (f - 1) / FPS
        kf(junta(m, "ombro_d"), "rotation_euler", f, 0.35 * math.sin(t * 2 * math.pi * 1.6), 1)
        kf(m, "location", f, 0.12 * abs(math.sin(t * math.pi * 1.6)), 2)
    anima_bola(est.bola, lambda t: Vector((0, 0, -5)), DUR)
    plano(cena, "fim", 0.0, DUR, (0, 26.0, 2.0), (0, 27.8, 2.3), (0, 45, 9.5), (0, 45, 9.5), lente=24)
    return DUR


LANCES = {"A": lance_A, "C": lance_C, "D": lance_D, "E": lance_E, "F": lance_F}

if __name__ == "__main__":
    lance = sys.argv[1]
    saida = os.path.abspath(sys.argv[2])
    amostras = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    larg = int(sys.argv[4]) if len(sys.argv) > 4 else 540
    cena = P.limpar_cena()
    cena.render.fps = FPS
    cena.render.use_persistent_data = True
    cena.cycles.samples = amostras
    dur = LANCES[lance](cena)
    cena.frame_start = 1
    cena.frame_end = q(dur) - 1
    cena.render.resolution_x = larg
    cena.render.resolution_y = int(larg * 16 / 9)
    cena.render.resolution_percentage = 100
    cena.render.image_settings.file_format = "PNG"
    os.makedirs(saida, exist_ok=True)
    if os.environ.get("QUADROS"):
        for f in [int(x) for x in os.environ["QUADROS"].split(",")]:
            cena.frame_set(f)
            cena.render.filepath = os.path.join(saida, f"previa_{lance}_{f:04d}.png")
            bpy.ops.render.render(write_still=True)
    else:
        cena.render.filepath = os.path.join(saida, "f_")
        bpy.ops.render.render(animation=True)
