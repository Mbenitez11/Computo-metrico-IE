#!/usr/bin/env python3
"""Compare independently reviewed element annotations, never names alone."""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

from eqt.model import number, sha256, save


def read_annotations(path):
    rows = {}
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        required = {'physical_id', 'system', 'material_key', 'unit', 'quantity'}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError('Faltan columnas de anotación')
        for row in reader:
            key = (row['physical_id'], row['system'], row['material_key'], row['unit'])
            if not row['physical_id'] or key in rows:
                raise ValueError('Identidad física ausente o duplicada')
            rows[key] = number(float(row['quantity']))
    return rows


def compare(predicted, truth):
    result = {}
    for system in sorted({k[1] for k in predicted} | {k[1] for k in truth}):
        p = {k: v for k, v in predicted.items() if k[1] == system}
        t = {k: v for k, v in truth.items() if k[1] == system}
        matched = set(p) & set(t); fp = set(p) - set(t); fn = set(t) - set(p)
        lengths = [{'physical_id': k[0], 'predicted_m': p[k], 'truth_m': t[k],
                    'absolute_error_m': abs(p[k] - t[k]),
                    'relative_error': abs(p[k] - t[k]) / t[k] if t[k] else None}
                   for k in sorted(matched) if k[3] == 'm']
        result[system] = {'matched_identities': len(matched), 'false_positive_identities': len(fp),
                          'false_negative_identities': len(fn),
                          'precision_on_annotated_sample': len(matched) / len(p) if p else None,
                          'recall_on_annotated_sample': len(matched) / len(t) if t else None,
                          'false_positive_ids': [k[0] for k in sorted(fp)],
                          'false_negative_ids': [k[0] for k in sorted(fn)],
                          'length_errors': lengths,
                          'quantity_discrepancies': [{'physical_id': k[0], 'unit': k[3], 'predicted': p[k], 'truth': t[k]}
                                                      for k in sorted(matched) if p[k] != t[k]]}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('predicted'); parser.add_argument('truth'); parser.add_argument('--out', required=True)
    parser.add_argument('--ground-truth-reviewed', action='store_true', required=True,
                        help='Confirmar revisión independiente de verdad manual y correspondencias físicas')
    args = parser.parse_args()
    data = {'notice': 'Métricas de la muestra anotada; no generalizar precisión a otros proyectos.',
            'predicted_sha256': sha256(args.predicted), 'truth_sha256': sha256(args.truth),
            'results': compare(read_annotations(args.predicted), read_annotations(args.truth))}
    save(args.out, data); print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
