"""Reviewed selections, calibrated geometry and explicit, dimensioned rules."""
import copy
import math
from collections import defaultdict

from .model import (SCHEMA, uid, number, meters, rect, point, contains, require_approval,
                    geometry_length, issue)


def calibration_factor(calibration, page, doc):
    require_approval(calibration)
    if calibration['source_sha256'] != doc['sha256'] or calibration['page_id'] != page['id']:
        raise ValueError('Calibración de otra página o versión')
    region = rect(calibration['region'])
    if not contains([0, 0, page['width'], page['height']], region):
        raise ValueError('Región de calibración fuera de página')
    p1, p2 = point(calibration['p1']), point(calibration['p2'])
    if any(not contains(region, [p[0], p[1], p[0], p[1]]) for p in (p1, p2)):
        raise ValueError('Cota de calibración fuera de región')
    distance = number(math.dist(p1, p2), positive=True)
    real = number(meters(calibration['real_distance'], calibration['unit']), positive=True)
    return real / distance


def reviewed_document(setting, doc):
    require_approval(setting)
    if setting.get('sha256') != doc['sha256']:
        raise ValueError('Hash documental no coincide')
    if not setting.get('revision') or not setting.get('family'):
        raise ValueError('Declarar revisión y familia documental')
    if doc['status'] != 'indexed':
        raise ValueError('Documento pendiente de extracción')


def base_quantity(project, selection, n):
    return {'id': selection.get('id') or uid(project, 'selection', n), 'project': project,
            'system': selection.get('system', 'sin_clasificar'), 'sector': selection.get('sector', ''),
            'level': selection.get('level', ''), 'circuit': selection.get('circuit', ''),
            'material_key': selection.get('material_key', ''), 'specification': selection.get('specification', ''),
            'description': selection.get('description', ''), 'unit': selection.get('unit', 'u'),
            'quantity': None, 'method': 'pending', 'formula': '', 'rule_id': None,
            'source_refs': selection.get('source_refs', []), 'document_id': None, 'drawing': None,
            'revision': None, 'page_id': None, 'geometry': [], 'evidence': selection.get('evidence', ''),
            'confidence': 'unverified', 'review_status': 'pending', 'notes': [],
            'physical_id': selection.get('physical_id'), 'calibration_id': selection.get('calibration_id'),
            'basis_id': None, 'provision_by': selection.get('provision_by', ''),
            'installation_by': selection.get('installation_by', '')}


def run(index, config):
    if index.get('schema') != SCHEMA or config.get('schema') != SCHEMA:
        raise ValueError('Versión de contrato no soportada')
    out = copy.deepcopy(index)
    out['quantities'] = []; out['consolidated'] = []; out['rules'] = config.get('rules', [])
    docs = {d['id']: d for d in out['documents']}
    refs = {r['id']: r for r in out['references']}
    pages = {p['id']: p for p in out['pages']}
    settings = config.get('documents', {})
    observations = out['observations']
    approved_docs, families = set(), defaultdict(list)
    for did, setting in settings.items():
        try:
            if did not in docs:
                raise ValueError('Documento desconocido')
            reviewed_document(setting, docs[did])
            approved_docs.add(did); families[setting['family']].append(did)
            docs[did]['revision'] = setting['revision']
        except (ValueError, KeyError, TypeError) as exc:
            observations.append(issue('DOCUMENT_NOT_APPROVED', 'blocking', [did], str(exc), 'Revisar índice y selección de revisión.'))
    for family, ids in families.items():
        if len(ids) > 1:
            approved_docs.difference_update(ids)
            observations.append(issue('REVISION_CONFLICT', 'blocking', ids,
                                      f'Familia {family}: más de un documento activo.',
                                      'Seleccionar una revisión o separar alcance en ejecuciones distintas.'))
    calibrations = {}; calibration_ids = set(); invalid_calibration_ids = set()
    for cal in config.get('calibrations', []):
        try:
            cid = cal['id']
            if cid in calibration_ids:
                invalid_calibration_ids.add(cid); calibrations.pop(cid, None)
                raise ValueError('ID de calibración duplicado')
            calibration_ids.add(cid)
            page = pages[cal['page_id']]; doc = docs[page['document_id']]
            factor = calibration_factor(cal, page, doc)
            if cid not in invalid_calibration_ids:
                calibrations[cid] = (cal, factor)
        except (ValueError, KeyError, TypeError) as exc:
            observations.append(issue('CALIBRATION_INVALID', 'blocking', [], str(exc), 'Corregir calibración antes de medir.'))
    out['calibrations'] = [c for c, factor in calibrations.values()]
    # Retain scale findings for uncovered pages; resolve only pages with an approved calibration.
    covered = {c['page_id'] for c, factor in calibrations.values()}
    for obs in observations:
        if obs['code'] == 'SCALE_UNVERIFIED':
            candidates = [p for p in pages.values() if p['document_id'] in obs['documents']
                          and obs['detail'].startswith(f"Página {p['page']}: ")]
            if candidates and candidates[0]['id'] in covered:
                obs['resolution'] = 'Región calibrada; medir solo dentro de ella'
                obs['severity'] = 'info'
    used_ids = set()
    for n, s in enumerate(config.get('selections', [])):
        q = base_quantity(index['project'], s, n)
        if q['id'] in used_ids:
            raise ValueError('ID de partida duplicado')
        used_ids.add(q['id']); out['quantities'].append(q)
        try:
            if not q['description'] or not q['material_key'] or q['system'] == 'sin_clasificar':
                raise ValueError('Falta descripción, sistema o clave de material')
            if s.get('kind') == 'pending' and not q['source_refs']:
                raise ValueError(s.get('reason', 'Falta información para cuantificar esta partida necesaria'))
            if not isinstance(q['source_refs'], list) or not q['source_refs']:
                raise ValueError('Faltan referencias gráficas')
            selected = [refs[r] for r in q['source_refs']]
            if len({r['id'] for r in selected}) != len(selected):
                raise ValueError('Referencia repetida en la misma partida')
            if len({shape_key(r) for r in selected}) != len(selected):
                raise ValueError('Geometría coincidente repetida en la misma partida')
            dids = {r['document_id'] for r in selected}; pids = {r['page_id'] for r in selected}
            if len(dids) != 1 or len(pids) != 1:
                raise ValueError('Una partida original debe pertenecer a una página/documento')
            did, pid = next(iter(dids)), next(iter(pids))
            q.update(document_id=did, drawing=docs[did]['name'], page_id=pid,
                     revision=docs[did].get('revision'), geometry=[r['bbox'] for r in selected])
            if s.get('kind') == 'pending':
                raise ValueError(s.get('reason', 'Falta información para cuantificar esta partida necesaria'))
            if did not in approved_docs:
                raise ValueError('Revisión documental no aprobada o en conflicto')
            require_approval(s)
            kind = s['kind']
            if kind == 'count':
                if q['unit'] != 'u':
                    raise ValueError('Conteo requiere unidad u')
                if any(r['kind'] == 'word' for r in selected) and not s.get('tag_is_element_verified'):
                    raise ValueError('Texto no demuestra identidad de un elemento físico')
                q['quantity'] = 1
                q['formula'] = '1 elemento físico revisado (puede incluir varias referencias)'
                q['method'] = 'measured'
            elif kind == 'length':
                if q['unit'] != 'm' or any(r['kind'] != 'path' for r in selected):
                    raise ValueError('Longitud requiere paths y unidad m')
                if not s.get('installation_route_verified'):
                    raise ValueError('Trazo no verificado como recorrido real de instalación')
                if s.get('calibration_id') not in calibrations:
                    raise ValueError('Falta calibración válida y aprobada para medir este recorrido')
                cal, factor = calibrations[s['calibration_id']]
                if cal['page_id'] != pid or any(not contains(cal['region'], r['bbox']) for r in selected):
                    raise ValueError('Recorrido fuera de la región calibrada')
                q['quantity'] = sum(geometry_length(r['commands']) for r in selected) * factor
                q['formula'] = f'sum(longitud_geométrica_pt) * {factor:.15g} m/pt'
                q['method'] = 'measured'
            elif kind == 'estimate':
                q['quantity'] = number(s['value'])
                if q['unit'] not in ('u', 'm', 'm2', 'm3', 'kg'):
                    raise ValueError('Unidad de estimación inválida')
                q['method'] = 'estimated'; q['formula'] = s['justification']
                q['review_status'] = 'estimated'; q['confidence'] = 'assumption'
                continue
            else:
                raise ValueError('Tipo de selección no soportado')
            q['review_status'] = 'confirmed'; q['confidence'] = 'reviewed_evidence'
        except (ValueError, KeyError, TypeError) as exc:
            q['quantity'] = None; q['method'] = 'pending'; q['review_status'] = 'pending'
            q['notes'].append(str(exc))
            observations.append(issue('QUANTITY_BLOCKED', 'blocking', [q['document_id']] if q['document_id'] else [],
                                      str(exc), 'Completar evidencia o datos y recalcular.', items=[q['id']]))

    flag_duplicates(out, refs, config.get('identity_resolutions', []))
    apply_rules(out, config.get('rules', []))
    comparisons(out, config.get('comparisons', []))
    consolidate(out)
    coverage(out, config.get('system_reviews', []), approved_docs)
    return out


def shape_key(ref):
    commands = ref.get('commands')
    if commands and all(c[0] == 'l' for c in commands):
        commands = sorted(sorted([tuple(c[1]), tuple(c[2])]) for c in commands)
    return uid(ref['document_id'], ref['page_id'], ref['kind'], ref['bbox'], commands, ref.get('text'))


def flag_duplicates(out, refs, resolutions):
    by_ref, by_physical = defaultdict(list), defaultdict(list)
    for q in out['quantities']:
        if q['method'] not in ('measured', 'estimated'):
            continue
        for rid in q['source_refs']:
            by_ref[shape_key(refs[rid])].append(q)
        if q['physical_id']:
            by_physical[q['physical_id']].append(q)
    groups = list(by_ref.values()) + list(by_physical.values())
    seen = set()
    for group in groups:
        group = list({q['id']: q for q in group}.values())
        if len(group) < 2:
            continue
        ids = sorted(q['id'] for q in group)
        if tuple(ids) in seen:
            continue
        seen.add(tuple(ids))
        resolution = next((r for r in resolutions if sorted(r.get('item_ids', [])) == ids), None)
        keep = None
        if resolution:
            try:
                require_approval(resolution)
                if resolution['keep_id'] not in ids:
                    raise ValueError('Resolución no identifica partida autoritativa')
                keep = resolution['keep_id']
            except (ValueError, KeyError):
                pass
        for q in group:
            if q['id'] != keep:
                q['review_status'] = 'excluded_duplicate' if keep else 'duplicate_review'
                q['notes'].append('Duplicación resuelta por referencia autoritativa' if keep else 'Posible doble conteo')
        out['observations'].append(issue('DUPLICATE_ELEMENT', 'info' if keep else 'blocking',
                                         sorted({q['document_id'] for q in group}),
                                         'Referencias coincidentes o identidad física compartida.',
                                         f'Conservar {keep}' if keep else 'Resolver identidad con evidencia.', items=ids))


def rule_value(rule, base):
    """Return quantity, unit, auditable numeric formula; no eval or default ratios."""
    require_approval(rule)
    for field in ('id', 'description', 'formula', 'source', 'version', 'conditions'):
        if not rule.get(field):
            raise ValueError(f'Regla sin {field}')
    if base['unit'] != 'm' or base['quantity'] is None:
        raise ValueError('Regla requiere longitud base en m')
    if not isinstance(rule.get('conditions'), dict):
        raise ValueError('Condiciones deben ser objeto con coincidencias explícitas')
    if any(base.get(k) != v for k, v in rule['conditions'].items()):
        raise ValueError('Condiciones de regla no satisfechas')
    variables = rule['variables']; units = rule['variable_units']; L = base['quantity']
    def v(key, unit, positive=False, integer=False):
        if units.get(key) != unit:
            raise ValueError(f'Unidad incorrecta para {key}')
        return number(variables[key], positive=positive, integer=integer)
    kind = rule['kind']
    if kind == 'conductor':
        cables = v('count', 'u', positive=True, integer=True)
        vertical = v('vertical', 'm'); reserve = v('reserve', 'm'); waste = v('waste', '1')
        if waste > 1:
            raise ValueError('Desperdicio fuera de rango 0..1')
        result = (L + vertical + reserve) * cables * (1 + waste)
        formula = f'({L}+{vertical}+{reserve})*{cables}*(1+{waste})'
        return result, 'm', formula
    if kind == 'supports':
        spacing = v('spacing', 'm', positive=True)
        endpoints = v('endpoints', 'u', integer=True)
        if endpoints not in (0, 1, 2):
            raise ValueError('Extremos debe ser 0, 1 o 2')
        # Rule applies per explicitly reviewed physical run, never aggregate unrelated routes.
        if not rule.get('single_run_verified'):
            raise ValueError('Confirmar un único recorrido para espaciamiento de soportes')
        return math.ceil(L / spacing) + endpoints, 'u', f'CEILING({L}/{spacing},1)+{endpoints}'
    if kind == 'allowance':
        fraction = v('fraction', '1')
        if fraction > 1:
            raise ValueError('Factor fuera de rango 0..1')
        return L * fraction, 'm', f'{L}*{fraction}'
    raise ValueError('Regla no soportada')


def apply_rules(out, rules):
    by_id = {q['id']: q for q in out['quantities']}
    seen = set()
    for rule in rules:
        rid = rule.get('id')
        if not rid or rid in seen:
            raise ValueError('ID de regla ausente o repetido')
        seen.add(rid)
        base = by_id.get(rule.get('basis_id'))
        q = base_quantity(out['project'], rule, rid)
        q['id'] = uid('derived', rid, rule.get('basis_id')); q['basis_id'] = rule.get('basis_id')
        q['rule_id'] = rid
        if base:
            for key in ('document_id', 'drawing', 'revision', 'page_id', 'source_refs', 'geometry', 'sector', 'level', 'circuit'):
                q[key] = copy.deepcopy(base[key])
        try:
            if not base or base['review_status'] != 'confirmed':
                raise ValueError('Partida base no confirmada')
            if not q['material_key'] or not q['description'] or q['system'] == 'sin_clasificar':
                raise ValueError('Regla sin material, descripción o sistema')
            value, unit, formula = rule_value(rule, base)
            if q['unit'] != unit:
                raise ValueError('Unidad de salida de regla incompatible')
            q.update(quantity=number(value), formula=formula, method='calculated',
                     review_status='confirmed', confidence='rule_with_reviewed_inputs', evidence=rule['evidence'])
        except (ValueError, KeyError, TypeError) as exc:
            q['notes'].append(str(exc))
            out['observations'].append(issue('RULE_BLOCKED', 'blocking', [q['document_id']] if q['document_id'] else [],
                                             str(exc), 'Completar o aprobar regla y base.', items=[q['id']]))
        out['quantities'].append(q); by_id[q['id']] = q


def comparisons(out, config):
    qs = {q['id']: q for q in out['quantities']}; cells = {c['id']: c for c in out['cells']}
    for c in config:
        try:
            require_approval(c)  # explicit equivalence, never a name-based match
            q = qs[c['quantity_id']]; source = cells[c['cell_id']]
            if c['unit'] != q['unit'] or q['quantity'] is None:
                raise ValueError('Comparación sin cantidad o con unidades incompatibles')
            target = number(source['value']); tol = number(c['absolute_tolerance'])
            if abs(q['quantity'] - target) > tol:
                q['review_status'] = 'conflict_review'
                out['observations'].append(issue('DOCUMENT_CONTRADICTION', 'blocking',
                                                 [q['document_id'], source['document_id']],
                                                 f"{q['id']} frente a {source['sheet']}!{source['address']}",
                                                 'Revisar alcance, unidades, revisiones y criterio documental; no elegir silenciosamente.',
                                                 items=[q['id']], values=[q['quantity'], target]))
        except (ValueError, KeyError, TypeError) as exc:
            out['observations'].append(issue('COMPARISON_BLOCKED', 'blocking', [], str(exc), 'Completar relación de cotejo.'))
    # Derived quantities must lose confirmation if their input becomes disputed.
    changed = True
    while changed:
        changed = False
        for q in out['quantities']:
            if q['basis_id'] and qs[q['basis_id']]['review_status'] != 'confirmed' and q['review_status'] == 'confirmed':
                q['review_status'] = 'basis_review'; changed = True


def coverage(out, reviews, approved_docs):
    """A selected subset cannot silently imply a complete project takeoff."""
    from .model import SYSTEMS
    systems = sorted(set(SYSTEMS) | {q['system'] for q in out['quantities']} | {r['system'] for r in reviews})
    result = []
    for system in systems:
        items = [q for q in out['quantities'] if q['system'] == system]
        review = next((r for r in reviews if r['system'] == system), None)
        record = {'system': system, 'status': 'partial' if items else 'not_reviewed', 'evidence': '',
                  'items': [q['id'] for q in items]}
        if review:
            try:
                require_approval(review)
                if not review.get('document_ids') or not set(review['document_ids']).issubset(approved_docs):
                    raise ValueError('Cobertura sin documentos revisados')
                status = review['coverage_status']
                if status not in ('complete_reviewed', 'not_applicable_reviewed', 'partial'):
                    raise ValueError('Estado de cobertura inválido')
                if status == 'complete_reviewed' and (not items or any(q['review_status'] not in ('confirmed', 'excluded_duplicate') for q in items)):
                    raise ValueError('No declarar completo con partidas pendientes o sin partidas')
                if status == 'not_applicable_reviewed' and items:
                    raise ValueError('Sistema con partidas no puede declararse ausente')
                record.update(status=status, evidence=review['evidence'], document_ids=review['document_ids'])
            except (ValueError, KeyError, TypeError) as exc:
                out['observations'].append(issue('COVERAGE_NOT_CONFIRMED', 'blocking', review.get('document_ids', []),
                                                 f'{system}: {exc}', 'Revisar el sistema completo sin omitir provisiones de terceros.'))
        result.append(record)
    out['coverage'] = result


def consolidate(out):
    groups = defaultdict(list)
    for q in out['quantities']:
        if q['review_status'] == 'confirmed' and q['method'] in ('measured', 'calculated'):
            groups[(q['system'], q['material_key'], q['specification'], q['unit'], q['method'])].append(q)
    out['consolidated'] = [{'id': uid('consolidated', key), 'system': key[0], 'material_key': key[1],
                            'specification': key[2], 'unit': key[3], 'method': key[4],
                            'description': rows[0]['description'], 'quantity': sum(q['quantity'] for q in rows),
                            'source_ids': [q['id'] for q in rows]} for key, rows in sorted(groups.items())]


def tag_candidates(index, mapping):
    """Exact documentary hints only. A tag count is never a fixture count."""
    return [{'reference_id': r['id'], 'tag': r['text'], 'material_key': mapping[r['text']],
             'status': 'candidate', 'quantity': None}
            for r in index['references'] if r['kind'] == 'word' and r['text'] in mapping]
