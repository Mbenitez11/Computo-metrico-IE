"""Shared contracts and fail-closed numeric helpers. No external dependencies."""
import hashlib
import json
import math
from pathlib import Path

SCHEMA = 'eqt/1'
UNITS_M = {'m': 1.0, 'mm': .001, 'cm': .01, 'ft': .3048, 'in': .0254}
SYSTEMS = ['iluminacion', 'tomacorrientes', 'alimentadores', 'tableros', 'bandejas',
           'tuberias', 'fuerza', 'respaldo', 'especiales', 'puesta_tierra', 'spda']


def uid(*parts):
    return hashlib.sha256(json.dumps(parts, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:24]


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def number(value, *, positive=False, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('Se requiere número finito, no texto ni booleano')
    if value < 0 or (positive and value == 0) or (integer and value != int(value)):
        raise ValueError('Valor fuera de dominio')
    return value


def meters(value, unit):
    if unit not in UNITS_M:
        raise ValueError(f'Unidad de longitud no soportada: {unit}')
    return number(value) * UNITS_M[unit]


def point(p):
    if not isinstance(p, (list, tuple)) or len(p) != 2:
        raise ValueError('Punto inválido')
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in p):
        raise ValueError('Coordenadas no finitas')
    return list(p)


def rect(r):
    if not isinstance(r, (list, tuple)) or len(r) != 4:
        raise ValueError('Región inválida')
    point(r[:2]); point(r[2:])
    if r[0] >= r[2] or r[1] >= r[3]:
        raise ValueError('Región sin área')
    return list(r)


def contains(region, box, tolerance=1e-6):
    return (region[0] - tolerance <= box[0] and region[1] - tolerance <= box[1]
            and region[2] + tolerance >= box[2] and region[3] + tolerance >= box[3])


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, data):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8')


def issue(code, severity, documents, detail, action, *, items=None, values=None):
    return {'id': uid(code, documents, detail, items), 'code': code, 'severity': severity,
            'documents': documents, 'items': items or [], 'values': values or [],
            'detail': detail, 'possible_cause': 'Requiere revisión de la documentación o configuración',
            'impact': 'No incorporar cantidades afectadas como comprobadas', 'action': action}


def require_approval(data):
    if data.get('status') != 'approved' or not str(data.get('evidence', '')).strip():
        raise ValueError('Falta aprobación con evidencia')


def geometry_length(commands):
    total = 0.0
    if not commands:
        raise ValueError('Geometría vacía')
    for cmd in commands:
        if cmd[0] == 'l':
            total += math.dist(point(cmd[1]), point(cmd[2]))
        elif cmd[0] == 're':
            x0, y0, x1, y1 = rect(cmd[1])
            total += 2 * ((x1 - x0) + (y1 - y0))
        elif cmd[0] == 'qu':
            ps = [point(p) for p in cmd[1:]]
            total += sum(math.dist(ps[i], ps[(i + 1) % 4]) for i in range(4))
        else:
            raise ValueError('Curva o geometría no soportada para longitud exacta')
    return total
