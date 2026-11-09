"""Nabız Çemberi — geometrik neon düşmanlar (Python, bağımlılık yok; pygame varsa örnek gösterim).

    from geo_enemies import polygons, burst, step_burst, ENEMIES
    for pts, rgb in polygons('memur', x, y, size, t, beat=0.0):   # arkadan öne çiz
        pygame.draw.polygon(screen, rgb, pts)

    parts = burst('memur', x, y, size, t)       # ölüm parçaları
    step_burst(parts, dt)                       # her karede; her parça: pts, rgb, alpha (0..1)

    python geo_enemies.py                       # pygame ile sekiz düşmanı döndürür (tıkla: patlat)

Veri geo_enemies.json ile aynıdır (köşeler birim kürede, yüz köşeleri sıralı, n dış normal).
"""
import json, math, random, os

DATA = json.loads(r'''{"version": 1, "light": [-0.43554, 0.53233, 0.7259], "notes": "Koordinatlar birim küre içinde (en uzak köşe 1). Yüz köşeleri dışarıdan bakınca sıralı; n = dış normal. Dönüş: M = Rx(0.5+wob) · Ry(t) · Rz(0.6t), t = zaman × spin. Ton: renk × (0.62 + 0.7 × max(0, n·ışık)).", "shapes": {"kup": {"vertices": [[0.57735, 0.57735, 0.57735], [0.57735, 0.57735, -0.57735], [0.57735, -0.57735, 0.57735], [0.57735, -0.57735, -0.57735], [-0.57735, 0.57735, 0.57735], [-0.57735, 0.57735, -0.57735], [-0.57735, -0.57735, 0.57735], [-0.57735, -0.57735, -0.57735]], "faces": [{"v": [1, 0, 2, 3], "n": [1, 0, 0]}, {"v": [4, 0, 1, 5], "n": [0, 1, 0]}, {"v": [2, 0, 4, 6], "n": [0, 0, 1]}, {"v": [5, 1, 3, 7], "n": [-0.0, -0.0, -1]}, {"v": [3, 2, 6, 7], "n": [-0.0, -1, -0.0]}, {"v": [6, 4, 5, 7], "n": [-1, -0.0, -0.0]}]}, "tetra": {"vertices": [[0.57735, 0.57735, 0.57735], [0.57735, -0.57735, -0.57735], [-0.57735, 0.57735, -0.57735], [-0.57735, -0.57735, 0.57735]], "faces": [{"v": [2, 0, 1], "n": [0.57735, 0.57735, -0.57735]}, {"v": [1, 0, 3], "n": [0.57735, -0.57735, 0.57735]}, {"v": [3, 0, 2], "n": [-0.57735, 0.57735, 0.57735]}, {"v": [2, 1, 3], "n": [-0.57735, -0.57735, -0.57735]}]}, "okta": {"vertices": [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]], "faces": [{"v": [4, 0, 2], "n": [0.57735, 0.57735, 0.57735]}, {"v": [2, 0, 5], "n": [0.57735, 0.57735, -0.57735]}, {"v": [3, 0, 4], "n": [0.57735, -0.57735, 0.57735]}, {"v": [5, 0, 3], "n": [0.57735, -0.57735, -0.57735]}, {"v": [2, 1, 4], "n": [-0.57735, 0.57735, 0.57735]}, {"v": [5, 1, 2], "n": [-0.57735, 0.57735, -0.57735]}, {"v": [4, 1, 3], "n": [-0.57735, -0.57735, 0.57735]}, {"v": [3, 1, 5], "n": [-0.57735, -0.57735, -0.57735]}]}, "ikosa": {"vertices": [[0, 0.52573, 0.85065], [0.52573, 0.85065, 0], [0.85065, 0, 0.52573], [0, 0.52573, -0.85065], [0.52573, -0.85065, 0], [0.85065, 0, -0.52573], [0, -0.52573, 0.85065], [-0.52573, 0.85065, 0], [-0.85065, 0, 0.52573], [0, -0.52573, -0.85065], [-0.52573, -0.85065, 0], [-0.85065, 0, -0.52573]], "faces": [{"v": [1, 0, 2], "n": [0.57735, 0.57735, 0.57735]}, {"v": [7, 0, 1], "n": [0, 0.93417, 0.35682]}, {"v": [2, 0, 6], "n": [0.35682, 0, 0.93417]}, {"v": [6, 0, 8], "n": [-0.35682, -0.0, 0.93417]}, {"v": [8, 0, 7], "n": [-0.57735, 0.57735, 0.57735]}, {"v": [5, 1, 2], "n": [0.93417, 0.35682, 0]}, {"v": [3, 1, 5], "n": [0.57735, 0.57735, -0.57735]}, {"v": [7, 1, 3], "n": [0, 0.93417, -0.35682]}, {"v": [5, 2, 4], "n": [0.93417, -0.35682, 0]}, {"v": [4, 2, 6], "n": [0.57735, -0.57735, 0.57735]}, {"v": [9, 3, 5], "n": [0.35682, 0, -0.93417]}, {"v": [7, 3, 11], "n": [-0.57735, 0.57735, -0.57735]}, {"v": [11, 3, 9], "n": [-0.35682, -0.0, -0.93417]}, {"v": [5, 4, 9], "n": [0.57735, -0.57735, -0.57735]}, {"v": [10, 4, 6], "n": [0, -0.93417, 0.35682]}, {"v": [9, 4, 10], "n": [-0.0, -0.93417, -0.35682]}, {"v": [10, 6, 8], "n": [-0.57735, -0.57735, 0.57735]}, {"v": [8, 7, 11], "n": [-0.93417, 0.35682, -0.0]}, {"v": [10, 8, 11], "n": [-0.93417, -0.35682, -0.0]}, {"v": [11, 9, 10], "n": [-0.57735, -0.57735, -0.57735]}]}, "dodeka": {"vertices": [[0.57735, 0.57735, 0.57735], [0.57735, 0.57735, -0.57735], [0.57735, -0.57735, 0.57735], [0.57735, -0.57735, -0.57735], [-0.57735, 0.57735, 0.57735], [-0.57735, 0.57735, -0.57735], [-0.57735, -0.57735, 0.57735], [-0.57735, -0.57735, -0.57735], [0, 0.35682, 0.93417], [0.35682, 0.93417, 0], [0.93417, 0, 0.35682], [0, 0.35682, -0.93417], [0.35682, -0.93417, 0], [0.93417, 0, -0.35682], [0, -0.35682, 0.93417], [-0.35682, 0.93417, 0], [-0.93417, 0, 0.35682], [0, -0.35682, -0.93417], [-0.35682, -0.93417, 0], [-0.93417, 0, -0.35682]], "faces": [{"v": [1, 9, 0, 10, 13], "n": [0.85065, 0.52573, 0]}, {"v": [2, 10, 0, 8, 14], "n": [0.52573, 0, 0.85065]}, {"v": [4, 8, 0, 9, 15], "n": [0, 0.85065, 0.52573]}, {"v": [17, 11, 1, 13, 3], "n": [0.52573, 0, -0.85065]}, {"v": [15, 9, 1, 11, 5], "n": [0, 0.85065, -0.52573]}, {"v": [13, 10, 2, 12, 3], "n": [0.85065, -0.52573, 0]}, {"v": [18, 12, 2, 14, 6], "n": [0, -0.85065, 0.52573]}, {"v": [7, 17, 3, 12, 18], "n": [-0.0, -0.85065, -0.52573]}, {"v": [19, 16, 4, 15, 5], "n": [-0.85065, 0.52573, -0.0]}, {"v": [14, 8, 4, 16, 6], "n": [-0.52573, 0, 0.85065]}, {"v": [7, 19, 5, 11, 17], "n": [-0.52573, -0.0, -0.85065]}, {"v": [7, 18, 6, 16, 19], "n": [-0.85065, -0.52573, -0.0]}]}, "prizma": {"vertices": [[0.8, 0, 0.6], [0.8, 0, -0.6], [-0.4, 0.69282, 0.6], [-0.4, 0.69282, -0.6], [-0.4, -0.69282, 0.6], [-0.4, -0.69282, -0.6]], "faces": [{"v": [3, 2, 0, 1], "n": [0.5, 0.86603, 0]}, {"v": [1, 0, 4, 5], "n": [0.5, -0.86603, -0.0]}, {"v": [4, 0, 2], "n": [0, 0, 1]}, {"v": [3, 1, 5], "n": [-0.0, -0.0, -1]}, {"v": [4, 2, 3, 5], "n": [-1, 0, 0]}]}, "elmas": {"vertices": [[0, 0, 1], [0, 0, -0.8], [0.8, 0, 0.12], [0.4, 0.69282, 0.12], [-0.4, 0.69282, 0.12], [-0.8, 0, 0.12], [-0.4, -0.69282, 0.12], [0.4, -0.69282, 0.12]], "faces": [{"v": [3, 0, 2], "n": [0.68045, 0.39286, 0.61859]}, {"v": [2, 0, 7], "n": [0.68045, -0.39286, 0.61859]}, {"v": [4, 0, 3], "n": [0, 0.78571, 0.61859]}, {"v": [5, 0, 4], "n": [-0.68045, 0.39286, 0.61859]}, {"v": [6, 0, 5], "n": [-0.68045, -0.39286, 0.61859]}, {"v": [7, 0, 6], "n": [-0.0, -0.78571, 0.61859]}, {"v": [2, 1, 3], "n": [0.6918, 0.39941, -0.60157]}, {"v": [7, 1, 2], "n": [0.6918, -0.39941, -0.60157]}, {"v": [3, 1, 4], "n": [-0.0, 0.79882, -0.60157]}, {"v": [4, 1, 5], "n": [-0.6918, 0.39941, -0.60157]}, {"v": [5, 1, 6], "n": [-0.6918, -0.39941, -0.60157]}, {"v": [6, 1, 7], "n": [-0.0, -0.79882, -0.60157]}]}, "yildiz": {"vertices": [[0.57735, 0.57735, 0.57735], [0.57735, 0.57735, -0.57735], [0.57735, -0.57735, 0.57735], [0.57735, -0.57735, -0.57735], [-0.57735, 0.57735, 0.57735], [-0.57735, 0.57735, -0.57735], [-0.57735, -0.57735, 0.57735], [-0.57735, -0.57735, -0.57735], [0.57735, 0, 0], [-0.57735, 0, 0], [0, 0.57735, 0], [0, -0.57735, 0], [0, 0, 0.57735], [0, 0, -0.57735]], "faces": [{"v": [0, 8, 10], "n": [0.57735, 0.57735, -0.57735]}, {"v": [0, 10, 12], "n": [-0.57735, 0.57735, 0.57735]}, {"v": [0, 12, 8], "n": [0.57735, -0.57735, 0.57735]}, {"v": [10, 8, 1], "n": [0.57735, 0.57735, 0.57735]}, {"v": [13, 10, 1], "n": [-0.57735, 0.57735, -0.57735]}, {"v": [8, 13, 1], "n": [0.57735, -0.57735, -0.57735]}, {"v": [11, 8, 2], "n": [0.57735, -0.57735, -0.57735]}, {"v": [12, 11, 2], "n": [-0.57735, -0.57735, 0.57735]}, {"v": [8, 12, 2], "n": [0.57735, 0.57735, 0.57735]}, {"v": [3, 8, 11], "n": [0.57735, -0.57735, 0.57735]}, {"v": [3, 11, 13], "n": [-0.57735, -0.57735, -0.57735]}, {"v": [3, 13, 8], "n": [0.57735, 0.57735, -0.57735]}, {"v": [10, 9, 4], "n": [-0.57735, 0.57735, -0.57735]}, {"v": [12, 10, 4], "n": [0.57735, 0.57735, 0.57735]}, {"v": [9, 12, 4], "n": [-0.57735, -0.57735, 0.57735]}, {"v": [5, 9, 10], "n": [-0.57735, 0.57735, 0.57735]}, {"v": [5, 10, 13], "n": [0.57735, 0.57735, -0.57735]}, {"v": [5, 13, 9], "n": [-0.57735, -0.57735, -0.57735]}, {"v": [6, 9, 11], "n": [-0.57735, -0.57735, -0.57735]}, {"v": [6, 11, 12], "n": [0.57735, -0.57735, 0.57735]}, {"v": [6, 12, 9], "n": [-0.57735, 0.57735, 0.57735]}, {"v": [11, 9, 7], "n": [-0.57735, -0.57735, 0.57735]}, {"v": [13, 11, 7], "n": [0.57735, -0.57735, -0.57735]}, {"v": [9, 13, 7], "n": [-0.57735, 0.57735, -0.57735]}]}}, "enemies": [{"id": "memur", "name": "Memur", "shape": "kup", "color": "#3ff2d2", "spin": 1.1}, {"id": "kurye", "name": "Kurye", "shape": "tetra", "color": "#ffb054", "spin": 2.2}, {"id": "stajyer", "name": "Stajyer", "shape": "okta", "color": "#5ab0ff", "spin": 1.6}, {"id": "avukat", "name": "Avukat", "shape": "prizma", "color": "#b98bff", "spin": 0.9}, {"id": "sansurcu", "name": "Sansürcü", "shape": "ikosa", "color": "#ff3fb4", "spin": 1.1}, {"id": "denetci", "name": "Denetçi", "shape": "dodeka", "color": "#ffd166", "spin": 0.7}, {"id": "mudur", "name": "Müdür", "shape": "yildiz", "color": "#ff5468", "spin": 0.8}, {"id": "ceo", "name": "CEO", "shape": "elmas", "color": "#ff8ff0", "spin": 0.6}]}''')
SHAPES = DATA['shapes']
ENEMIES = {e['id']: e for e in DATA['enemies']}
LIGHT = DATA['light']


def _rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def tone(hex_color, k, white=0.0):
    out = []
    for v in _rgb(hex_color):
        x = v * k if k <= 1 else v + (255 - v) * (k - 1)
        x += (255 - x) * white
        out.append(max(0, min(255, round(x))))
    return tuple(out)


def _rot(ax, ay, az):
    cx, sx, cy, sy, cz, sz = math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay), math.cos(az), math.sin(az)
    return [[cy * cz, -cy * sz, sy],
            [sx * sy * cz + cx * sz, -sx * sy * sz + cx * cz, -sx * cy],
            [-cx * sy * cz + sx * sz, cx * sy * sz + sx * cz, cx * cy]]


def _mul(M, v):
    return [M[r][0] * v[0] + M[r][1] * v[1] + M[r][2] * v[2] for r in range(3)]


def polygons(kind, x, y, size, t, beat=0.0, wob=0.0, flash=0.0, rz=0.6):
    """Görünen yüzler arkadan öne: [(noktalar, (r,g,b)), ...]. t saniye, beat 0..1 vuruş evresi (zıplama), rz=0 tek eksenli döngü."""
    e = ENEMIES.get(kind, ENEMIES['memur'])
    sh = SHAPES[e['shape']]
    tt = t * e['spin'] + wob * 7
    M = _rot(0.5 + wob, tt, tt * rz)
    s = size * (1 + 0.18 * math.sin(math.pi * (beat % 1)))
    Q = [_mul(M, v) for v in sh['vertices']]
    P = [(x + q[0] * s, y + q[1] * s) for q in Q]
    faces = []
    for f in sh['faces']:
        n = _mul(M, f['n'])
        if n[2] <= 1e-3:
            continue
        cz = sum(Q[i][2] for i in f['v']) / len(f['v'])
        lit = max(0.0, n[0] * LIGHT[0] + n[1] * LIGHT[1] + n[2] * LIGHT[2])
        faces.append((cz, [P[i] for i in f['v']], tone(e['color'], 0.62 + 0.7 * lit, flash * 0.85), lit))
    faces.sort(key=lambda o: o[0])
    return [(pts, rgb) for _, pts, rgb, _ in faces]


def burst(kind, x, y, size, t, **kw):
    """Ölüm: görünen yüzler merkezden üçgenlere bölünür; her parça dönerek dağılır."""
    parts = []
    for pts, rgb in polygons(kind, x, y, size, t, **kw):
        cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
        for k in range(len(pts)):
            a, b = pts[k], pts[(k + 1) % len(pts)]
            tx, ty = (cx + a[0] + b[0]) / 3, (cy + a[1] + b[1]) / 3
            sp = 2.2 + random.random() * 2.5
            parts.append({'x': tx, 'y': ty, 'rel': [(cx - tx, cy - ty), (a[0] - tx, a[1] - ty), (b[0] - tx, b[1] - ty)],
                          'vx': (tx - x) * sp + (random.random() - 0.5) * 20, 'vy': (ty - y) * sp + (random.random() - 0.5) * 20,
                          'rot': 0.0, 'vr': (random.random() * 2 - 1) * 9, 'life': 1.0, 'rgb': rgb})
    return parts


def step_burst(parts, dt, gravity=0.0):
    """Parçaları ilerletir, ölenleri siler; her parça için 'pts' ve 'alpha' yazar."""
    for f in parts[:]:
        f['x'] += f['vx'] * dt; f['y'] += f['vy'] * dt; f['vy'] += gravity * dt; f['vx'] *= 0.98
        f['rot'] += f['vr'] * dt; f['life'] -= dt * 1.25
        if f['life'] <= 0:
            parts.remove(f); continue
        c, s, sc = math.cos(f['rot']), math.sin(f['rot']), 0.6 + 0.4 * f['life']
        f['pts'] = [(f['x'] + (px * c - py * s) * sc, f['y'] + (px * s + py * c) * sc) for px, py in f['rel']]
        f['alpha'] = min(1.0, f['life'] * 1.5)
    return parts


if __name__ == '__main__':
    import pygame
    pygame.init(); W, H = 900, 300
    screen = pygame.display.set_mode((W, H)); clock = pygame.time.Clock(); t = 0.0; parts = []
    kinds = list(ENEMIES)
    run = True
    while run:
        dt = clock.tick(60) / 1000; t += dt
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: run = False
            if ev.type == pygame.MOUSEBUTTONDOWN:
                i = min(len(kinds) - 1, ev.pos[0] * len(kinds) // W)
                parts += burst(kinds[i], (i + 0.5) * W / len(kinds), H / 2, 34, t)
        screen.fill((11, 10, 20))
        glow = pygame.Surface((W, H), pygame.SRCALPHA)
        for i, k in enumerate(kinds):
            x, y = (i + 0.5) * W / len(kinds), H / 2
            col = _rgb(ENEMIES[k]['color'])
            for r in range(78, 10, -8):
                pygame.draw.circle(glow, col + (int(10 * (1 - r / 78) ** 0.5 * 4),), (int(x), int(y)), r)
            for pts, rgb in polygons(k, x, y, 34, t, beat=(t * 2) % 1):
                pygame.draw.polygon(screen, rgb, pts); pygame.draw.polygon(screen, (255, 255, 255), pts, 1)
        screen.blit(glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        for f in step_burst(parts, dt):
            s = pygame.Surface((W, H), pygame.SRCALPHA); pygame.draw.polygon(s, f['rgb'] + (int(255 * f['alpha']),), f['pts']); screen.blit(s, (0, 0))
        pygame.display.flip()
