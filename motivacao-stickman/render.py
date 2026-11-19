"""Vídeo motivacional 2D com stickman — 25s, 16:9 (1920x1080), 30fps.
Uso: python3 render.py [saida.mp4]
"""
import math, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, DUR = 1920, 1080, 30, 25.0
S = 2  # supersampling para a camada do stickman/texto
OUT = sys.argv[1] if len(sys.argv) > 1 else "motivacao_stickman.mp4"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
WHITE = (240, 240, 240)
ACCENT = (255, 154, 60)
GROUND_Y = 800
random.seed(7)

# ---------------- utilidades ----------------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x):
    x = clamp(x); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
def lerp_pose(p, q, t): return {k: lerp(p[k], q[k], t) for k in p}

# ---------------- poses ----------------
# ângulos dos membros: 0 = apontando para baixo, positivo = para frente (direita)
# torso: 0 = vertical, positivo = inclinado para frente; head = inclinação extra
def pose(**kw):
    base = dict(torso=0.0, head=0.0, lua=0.12, lla=0.25, rua=-0.12, rla=0.05,
                lth=0.08, lsh=0.05, rth=-0.08, rsh=-0.1)
    base.update(kw); return base

STAND = pose()
SIT = pose(torso=0.3, head=0.95, lua=0.75, lla=2.1, rua=0.6, rla=2.0,
           lth=2.45, lsh=0.72, rth=2.35, rsh=0.62)
CROUCH = pose(torso=0.7, head=0.2, lua=0.4, lla=0.6, rua=0.2, rla=0.5,
              lth=1.5, lsh=-0.2, rth=1.3, rsh=-0.3)
FALLEN = pose(torso=1.1, head=0.55, lua=-0.05, lla=0.0, rua=0.05, rla=0.05,
              lth=0.1, lsh=-1.5, rth=-0.05, rsh=-1.55)
KNEEL = pose(torso=0.25, head=0.0, lua=0.3, lla=1.9, rua=-0.2, rla=0.3,
             lth=1.45, lsh=0.0, rth=0.0, rsh=-1.45)
VICTORY = pose(torso=-0.05, head=-0.3, lua=2.7, lla=2.9, rua=-2.7, rla=-2.9,
               lth=0.18, lsh=0.12, rth=-0.18, rsh=-0.22)
PUSH = pose(torso=0.75, head=-0.35, lua=1.45, lla=1.6, rua=1.35, rla=1.55)

def walk(phase, amp=0.45, lean=0.08, run=False):
    p = dict(STAND)
    a = amp * (1.5 if run else 1.0)
    for side, off in (("l", 0.0), ("r", math.pi)):
        ph = phase + off
        th = a * math.sin(ph)
        bend = (0.9 if run else 0.6) * max(0.0, math.cos(ph))
        p[side + "th"] = th
        p[side + "sh"] = th - 0.12 - bend
    arm = (0.9 if run else 0.45)
    p["lua"] = -arm * math.sin(phase)
    p["rua"] = arm * math.sin(phase)
    p["lla"] = p["lua"] + (1.3 if run else 0.4)
    p["rla"] = p["rua"] + (1.3 if run else 0.4)
    p["torso"] = lean + (0.25 if run else 0.0)
    return p

U = 300  # escala do corpo (px)
L = dict(torso=0.5, neck=0.07, r=0.115, ua=0.26, la=0.25, th=0.31, sh=0.31)

def joints(p, hx, hy, u=U):
    d = lambda ang, ln: (math.sin(ang) * ln * u, math.cos(ang) * ln * u)
    J = {"hip": (hx, hy)}
    t = p["torso"]
    nk = (hx + math.sin(t) * L["torso"] * u, hy - math.cos(t) * L["torso"] * u)
    J["neck"] = nk
    ha = t + p["head"]
    hd = (L["neck"] + L["r"]) * u
    J["head"] = (nk[0] + math.sin(ha) * hd, nk[1] - math.cos(ha) * hd)
    for s in "lr":
        e = d(p[s + "ua"], L["ua"]); J[s + "elb"] = (nk[0] + e[0], nk[1] + e[1])
        h = d(p[s + "la"], L["la"]); J[s + "hand"] = (J[s + "elb"][0] + h[0], J[s + "elb"][1] + h[1])
        k = d(p[s + "th"], L["th"]); J[s + "knee"] = (hx + k[0], hy + k[1])
        f = d(p[s + "sh"], L["sh"]); J[s + "foot"] = (J[s + "knee"][0] + f[0], J[s + "knee"][1] + f[1])
    return J

def grounded(p, hx, ground=lambda x: GROUND_Y, u=U, pad=6):
    """Calcula a altura do quadril para que o ponto mais baixo toque o chão."""
    J = joints(p, hx, 0, u)
    best = 1e9
    for k, (x, y) in J.items():
        if k == "head":
            y += L["r"] * u
        best = min(best, ground(x) - y - pad)
    return best

def draw_stick(d, J, color=WHITE, lw=12, u=U):
    c = tuple(color) + (255,)
    sc = lambda pt: (pt[0] * S, pt[1] * S)
    def seg(a, b):
        d.line([sc(J[a]), sc(J[b])], fill=c, width=lw * S)
        for q in (a, b):
            x, y = sc(J[q]); r = lw * S / 2
            d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    # membros de trás primeiro (um pouco mais escuros)
    back = tuple(int(v * 0.62) for v in color) + (255,)
    def seg_c(a, b, col):
        d.line([sc(J[a]), sc(J[b])], fill=col, width=lw * S)
        for q in (a, b):
            x, y = sc(J[q]); r = lw * S / 2
            d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    for a, b in (("neck", "relb"), ("relb", "rhand"), ("hip", "rknee"), ("rknee", "rfoot")):
        seg_c(a, b, back)
    seg("hip", "neck")
    for a, b in (("hip", "lknee"), ("lknee", "lfoot"), ("neck", "lelb"), ("lelb", "lhand")):
        seg(a, b)
    x, y = sc(J["head"]); r = L["r"] * u * S
    d.ellipse([x - r, y - r, x + r, y + r], fill=c)

# ---------------- fundo ----------------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
grad = (np.linspace(14, 2, H, dtype=np.float32)[:, None, None] * np.array([0.8, 0.85, 1.1], np.float32))
BG = np.broadcast_to(grad, (H, W, 3)).copy()
vig = 1.0 - 0.75 * np.clip((((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2), 0, 1)
VIG = vig[..., None]

def glow_map(cx, cy, rad):
    dd = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 1.15) ** 2) / rad
    return (np.exp(-dd ** 2 * 2.2) * 0.85 + np.exp(-dd * 3.0) * 0.6)[..., None]

GLOW2 = glow_map(1820, GROUND_Y, 700)
GLOW5 = glow_map(960, 740, 900)
WARM = np.array([255, 140, 50], np.float32)

def mountains(seed, base, amp, n=14, width=W * 2):
    rnd = random.Random(seed)
    pts = []
    for i in range(n + 1):
        pts.append((i * width / n, base - rnd.uniform(0.3, 1.0) * amp))
    return pts

MTN_FAR = mountains(3, 700, 260)
MTN_NEAR = mountains(11, 760, 150, n=10)

def draw_mtn(d, pts, off, color, bottom=GROUND_Y):
    width = pts[-1][0]
    off = off % width
    for k in (-1, 0, 1):
        poly = [((x - off + k * width) * S, y * S) for x, y in pts]
        poly += [(poly[-1][0], bottom * S), (poly[0][0], bottom * S)]
        d.polygon(poly, fill=color)

# partículas
DUST = [(random.uniform(0, W), random.uniform(0, H), random.uniform(1.5, 4), random.uniform(5, 25),
         random.uniform(0, 6.28)) for _ in range(70)]
RAIN = [(random.uniform(0, W + 300), random.uniform(0, H), random.uniform(900, 1400)) for _ in range(140)]
EMBERS = [(random.uniform(300, 1620), random.uniform(0, H), random.uniform(2, 5), random.uniform(40, 110),
           random.uniform(0, 6.28)) for _ in range(60)]

def draw_dust(d, t, alpha=60):
    for x, y, r, sp, ph in DUST:
        px = (x + math.sin(t * 0.6 + ph) * 20) % W
        py = (y - t * sp) % H
        a = int(alpha * (0.5 + 0.5 * math.sin(t * 1.3 + ph)))
        d.ellipse([(px - r) * S, (py - r) * S, (px + r) * S, (py + r) * S], fill=(200, 200, 210, a))

# ---------------- texto ----------------
FONTS = {}
def font(sz):
    if sz not in FONTS: FONTS[sz] = ImageFont.truetype(FONT, sz * S)
    return FONTS[sz]

def draw_caption(d, parts, t, t0, t1, y=190, size=74):
    """parts: lista de (texto, destaque?) — aparece palavra por palavra."""
    if t < t0 or t > t1: return
    fin = ease((t1 - t) / 0.45)
    f = font(size)
    words = []
    for txt, hl in parts:
        for w in txt.split():
            words.append((w, hl))
    space = f.getlength(" ")
    widths = [f.getlength(w) for w, _ in words]
    total = sum(widths) + space * (len(words) - 1)
    x = W * S / 2 - total / 2
    for i, ((w, hl), ww) in enumerate(zip(words, widths)):
        a = ease((t - t0 - i * 0.12) / 0.35) * fin
        if a <= 0:
            x += ww + space; continue
        dy = (1 - a) * 28 * S
        col = ACCENT if hl else WHITE
        # sombra suave
        d.text((x + 4 * S, y * S + dy + 4 * S), w, font=f, fill=(0, 0, 0, int(200 * a)))
        d.text((x, y * S + dy), w, font=f, fill=col + (int(255 * a),))
        x += ww + space
    # sublinhado laranja que cresce
    ul = ease((t - t0 - 0.4) / 0.8) * fin
    if ul > 0:
        lw = 140 * S * ul
        cy = (y + size + 30) * S
        d.rounded_rectangle([W * S / 2 - lw / 2, cy, W * S / 2 + lw / 2, cy + 6 * S], radius=3 * S,
                            fill=ACCENT + (int(255 * fin),))

CAPTIONS = [
    (0.4, 4.7, [("Todo mundo já se sentiu", False), ("sem forças.", True)]),
    (5.4, 9.7, [("Mas o que importa é se", False), ("levantar.", True)]),
    (10.4, 14.7, [("Cada passo te deixa mais", False), ("forte.", True)]),
    (15.4, 19.7, [("Cair faz parte.", False), ("Desistir, não.", True)]),
    (20.6, 24.6, [("Continue.", False), ("O topo é seu.", True)]),
]

# ---------------- cenas ----------------
def scene(t):
    """Retorna (layer RGBA supersampled, glow_map, glow_intensity, shake)."""
    layer = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    glow, gi, shake = None, 0.0, (0, 0)
    flat = lambda x: GROUND_Y

    def ground_line(off=0.0, col=(48, 48, 56, 255)):
        d.rectangle([0, GROUND_Y * S, W * S, GROUND_Y * S + 4 * S], fill=col)
        for i in range(-1, 26):
            gx = (i * 90 - off) % (W + 180) - 90
            d.rectangle([gx * S, (GROUND_Y + 14) * S, (gx + 30) * S, (GROUND_Y + 17) * S], fill=(30, 30, 36, 255))

    if t < 5:  # 1 — sentado no escuro, chuva
        lt = t
        draw_mtn(d, MTN_FAR, 0, (12, 12, 17, 255))
        for x, y, sp in RAIN:
            py = (y + lt * sp) % (H + 100) - 50
            px = x - (py * 0.15)
            d.line([(px * S, py * S), ((px - 6) * S, (py + 34) * S)], fill=(120, 125, 140, 70), width=2 * S)
        ground_line()
        p = dict(SIT); p["torso"] += 0.03 * math.sin(lt * 2.2)
        p["head"] += 0.04 * math.sin(lt * 2.2)
        hx = 820
        J = joints(p, hx, grounded(p, hx))
        draw_stick(d, J, color=(175, 175, 185))
    elif t < 10:  # 2 — levanta e caminha em direção à luz
        lt = t - 5
        draw_mtn(d, MTN_FAR, 0, (12, 12, 17, 255))
        ground_line()
        glow, gi = GLOW2, ease((lt - 1.0) / 2.0) * (0.85 + 0.08 * math.sin(lt * 3))
        hx = 820
        if lt < 0.6:
            p = dict(SIT)
        elif lt < 1.5:
            p = lerp_pose(SIT, CROUCH, ease((lt - 0.6) / 0.9))
        elif lt < 2.4:
            p = lerp_pose(CROUCH, STAND, ease((lt - 1.5) / 0.9))
        elif lt < 3.0:
            p = dict(STAND); p["head"] = -0.15 * ease((lt - 2.4) / 0.4)
        else:
            k = ease((lt - 3.0) / 0.5)
            ph = (lt - 3.0) * 7.0
            p = lerp_pose(STAND, walk(ph), k)
            hx = 820 + (lt - 3.0) * 120
        J = joints(p, hx, grounded(p, hx))
        col = tuple(int(lerp(175, 245, ease((lt - 1.0) / 2.0))) for _ in range(3))
        draw_stick(d, J, color=col)
    elif t < 15:  # 3 — empurrando a pedra morro acima
        lt = t - 10
        slope = 0.28
        gy = lambda x: 860 - (x - 800) * slope
        off = lt * 110
        draw_mtn(d, MTN_FAR, off * 0.15, (12, 12, 17, 255), bottom=H)
        draw_mtn(d, MTN_NEAR, off * 0.35, (17, 17, 23, 255), bottom=H)
        poly = [(0, gy(0) * S), (W * S, gy(W) * S), (W * S, H * S), (0, H * S)]
        d.polygon(poly, fill=(6, 6, 9, 255))
        d.line([(0, gy(0) * S), (W * S, gy(W) * S)], fill=(52, 52, 60, 255), width=5 * S)
        for i in range(-2, 24):
            gx = (i * 100 - off) % (W + 200) - 100
            d.ellipse([(gx - 6) * S, (gy(gx) + 16) * S, (gx + 6) * S, (gy(gx) + 22) * S], fill=(34, 34, 40, 255))
        ph = lt * 5.2
        p = lerp_pose(walk(ph, amp=0.4), PUSH, 1.0)
        for s, o in (("l", 0), ("r", math.pi)):
            th = 0.42 * math.sin(ph + o)
            p[s + "th"] = th + 0.35
            p[s + "sh"] = th - 0.25 - 0.55 * max(0, math.cos(ph + o))
        p["lua"] += 0.06 * math.sin(ph * 2); p["rua"] += 0.06 * math.sin(ph * 2 + 1)
        hx = 760
        J = joints(p, hx, grounded(p, hx, gy))
        hand = J["lhand"] if J["lhand"][0] > J["rhand"][0] else J["rhand"]
        R = 120
        cx = hand[0] + R * 0.92 + 8
        cy = gy(cx) - R - 2
        d.ellipse([(cx - R) * S, (cy - R) * S, (cx + R) * S, (cy + R) * S], fill=(26, 26, 32, 255),
                  outline=(110, 110, 120, 255), width=6 * S)
        rot = -off / R
        for k in range(3):
            a = rot + k * 2.1
            x1, y1 = cx + math.cos(a) * R * 0.25, cy + math.sin(a) * R * 0.25
            x2, y2 = cx + math.cos(a + 0.5) * R * 0.75, cy + math.sin(a + 0.5) * R * 0.75
            d.line([(x1 * S, y1 * S), (x2 * S, y2 * S)], fill=(70, 70, 80, 255), width=4 * S)
        draw_stick(d, J)
        # gotas de suor/esforço
        for k in range(3):
            st = (lt * 1.4 + k / 3) % 1
            hx2, hy2 = J["head"]
            sx = hx2 - 30 - st * 50
            sy = hy2 - 20 + st * st * 90
            a = int(200 * (1 - st))
            d.ellipse([(sx - 5) * S, (sy - 7) * S, (sx + 5) * S, (sy + 7) * S], fill=(150, 190, 255, a))
    elif t < 20:  # 4 — corre, cai e levanta
        lt = t - 15
        if lt < 1.0:
            spd = 1.0
        elif lt < 1.5:
            spd = 1.0 - ease((lt - 1.0) / 0.5)
        elif lt < 3.6:
            spd = 0.0
        else:
            spd = ease((lt - 3.6) / 0.8)
        # integra deslocamento
        def dist(tt):
            n = 60; acc = 0.0
            for i in range(n):
                x = tt * i / n
                if x < 1.0: v = 1.0
                elif x < 1.5: v = 1.0 - ease((x - 1.0) / 0.5)
                elif x < 3.6: v = 0.0
                else: v = ease((x - 3.6) / 0.8)
                acc += v * tt / n
            return acc * 650
        off = dist(lt)
        draw_mtn(d, MTN_FAR, off * 0.15, (12, 12, 17, 255))
        draw_mtn(d, MTN_NEAR, off * 0.35, (17, 17, 23, 255))
        ground_line(off)
        run = walk(lt * 11, run=True)
        hx = 820
        if lt < 1.0:
            p = run
        elif lt < 1.5:
            p = lerp_pose(run, FALLEN, ease((lt - 1.0) / 0.5))
            hx = 820 + ease((lt - 1.0) / 0.5) * 60
        elif lt < 2.5:
            p = dict(FALLEN); p["head"] += 0.05 * math.sin(lt * 3); hx = 880
        elif lt < 3.0:
            p = lerp_pose(FALLEN, KNEEL, ease((lt - 2.5) / 0.5)); hx = 880
        elif lt < 3.6:
            p = lerp_pose(KNEEL, STAND, ease((lt - 3.0) / 0.6)); hx = 880
            p["head"] = -0.2
        else:
            k = ease((lt - 3.6) / 0.6)
            p = lerp_pose(STAND, run, k); hx = 880 - (k * 60)
        if 1.45 < lt < 1.95:
            amt = (1 - (lt - 1.45) / 0.5) * 14
            shake = (random.uniform(-amt, amt), random.uniform(-amt, amt))
        J = joints(p, hx, grounded(p, hx))
        # poeira do impacto
        if 1.4 < lt < 2.4:
            st = (lt - 1.4) / 1.0
            for k in range(10):
                ang = math.pi + k * math.pi / 9
                rr = 30 + st * 140
                px = hx + 40 + math.cos(ang) * rr
                py = GROUND_Y - abs(math.sin(ang)) * rr * 0.35
                r = 10 * (1 - st) + 3
                d.ellipse([(px - r) * S, (py - r) * S, (px + r) * S, (py + r) * S],
                          fill=(120, 120, 130, int(150 * (1 - st))))
        # linhas de velocidade
        if spd > 0.05:
            for k in range(6):
                ly = 420 + k * 55
                lx = (W - ((lt * 1900 + k * 370) % (W + 400)))
                d.line([(lx * S, ly * S), ((lx + 160) * S, ly * S)], fill=(90, 90, 100, int(110 * spd)), width=3 * S)
        draw_stick(d, J)
    else:  # 5 — topo da montanha, nascer do sol
        lt = t - 20
        glow, gi = GLOW5, ease(lt / 2.5) * (1.0 + 0.06 * math.sin(lt * 2.5))
        peak = (960, 800)
        # raios de luz
        rays = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        rd = ImageDraw.Draw(rays)
        for k in range(14):
            a = k * (math.pi * 2 / 14) + lt * 0.08
            a2 = a + 0.07
            R = 1600
            pts = [(peak[0] * S, (peak[1] - 60) * S),
                   ((peak[0] + math.cos(a) * R) * S, (peak[1] - 60 + math.sin(a) * R) * S),
                   ((peak[0] + math.cos(a2) * R) * S, (peak[1] - 60 + math.sin(a2) * R) * S)]
            rd.polygon(pts, fill=(255, 170, 90, int(22 * ease(lt / 2.5))))
        layer.alpha_composite(rays); d = ImageDraw.Draw(layer)
        for x, y, r, sp, ph in EMBERS:
            py = (y - lt * sp) % H
            px = x + math.sin(lt + ph) * 25
            a = int(180 * ease(lt / 2) * (0.5 + 0.5 * math.sin(lt * 2 + ph)))
            d.ellipse([(px - r) * S, (py - r) * S, (px + r) * S, (py + r) * S], fill=ACCENT + (a,))
        mt = [(-100, H + 10), (300, 1010), (600, 920), (peak[0] - 70, peak[1] + 8), (peak[0] + 70, peak[1] + 8),
              (1300, 930), (1600, 1000), (2020, H + 10)]
        d.polygon([(x * S, y * S) for x, y in mt], fill=(4, 4, 6, 255))
        d.line([(x * S, y * S) for x, y in mt], fill=(90, 60, 40, 255), width=4 * S)
        top = lambda x: peak[1] + 6 if abs(x - peak[0]) < 70 else peak[1] + 6 + (abs(x - peak[0]) - 70) * 0.5
        hx = 960
        if lt < 1.3:
            p = dict(STAND); p["head"] = -0.2
            p["torso"] = 0.02 * math.sin(lt * 4)
        elif lt < 2.1:
            p = lerp_pose(STAND, VICTORY, ease((lt - 1.3) / 0.8))
        else:
            p = dict(VICTORY)
            b = math.sin((lt - 2.1) * 4) * 0.06
            p["lua"] += b; p["rua"] -= b; p["lla"] += b; p["rla"] -= b
        J = joints(p, hx, grounded(p, hx, top))
        draw_stick(d, J, color=(10, 10, 12))  # silhueta contra o sol
    # legenda
    for t0, t1, parts in CAPTIONS:
        draw_caption(d, parts, t, t0, t1, y=170 if t < 20 else 110, size=74 if t < 20 else 84)
    return layer, glow, gi, shake

def fade(t):
    edges = [0, 5, 10, 15, 20, 25]
    m = min(abs(t - e) for e in edges)
    f = clamp(m / 0.3)
    if t > 23.8: f = min(f, clamp((25 - t) / 1.2))
    return f

def frame(i):
    t = i / FPS
    layer, glow, gi, shake = scene(t)
    img = BG.copy()
    if glow is not None and gi > 0:
        img = img + glow * gi * WARM
    small = layer.resize((W, H), Image.LANCZOS)
    if shake != (0, 0):
        small = small.transform(small.size, Image.AFFINE, (1, 0, shake[0], 0, 1, shake[1]))
    arr = np.asarray(small, np.float32)
    a = arr[..., 3:4] / 255.0
    img = img * (1 - a) + arr[..., :3] * a
    img = img * VIG * fade(t)
    # grão de filme
    img += np.random.normal(0, 3.0, (H, W, 1)).astype(np.float32)
    return np.clip(img, 0, 255).astype(np.uint8)

if __name__ == "__main__":
    n = int(DUR * FPS)
    if len(sys.argv) > 2:  # modo preview: render.py out.png tempo
        Image.fromarray(frame(int(float(sys.argv[2]) * FPS))).save(OUT); sys.exit()
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    for i in range(n):
        ff.stdin.write(frame(i).tobytes())
        if i % 75 == 0: print(f"{i}/{n}", flush=True)
    ff.stdin.close(); ff.wait()
    print("ok", OUT)
