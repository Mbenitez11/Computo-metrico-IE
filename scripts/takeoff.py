#!/usr/bin/env python3
"""Local CLI. Run with --help; sources are never modified."""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

from eqt import __version__
from eqt.model import load, save, sha256
from eqt.extract import index_folder
from eqt.engine import run, tag_candidates
from eqt.export import export_all


def main(argv=None):
    parser = argparse.ArgumentParser(description='Cómputos eléctricos trazables, asistidos por revisión')
    parser.add_argument('--version', action='version', version=__version__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor', help='Comprobar dependencias sin instalarlas')
    p = sub.add_parser('index', help='Inventariar y extraer documentación')
    p.add_argument('input'); p.add_argument('--out', required=True); p.add_argument('--project', required=True)
    p.add_argument('--no-excel', action='store_true')
    p = sub.add_parser('compute', help='Computar selecciones explícitas y calibradas')
    p.add_argument('index'); p.add_argument('--config', required=True); p.add_argument('--out', required=True)
    p.add_argument('--no-excel', action='store_true')
    p = sub.add_parser('candidates', help='Buscar etiquetas exactas; no confirma cantidades')
    p.add_argument('index'); p.add_argument('--mapping', required=True); p.add_argument('--out', required=True)
    args = parser.parse_args(argv)
    if args.command == 'doctor':
        result = {'python': sys.version.split()[0], 'version': __version__,
                  'dependencies': {name: importlib.util.find_spec(name) is not None for name in ('fitz', 'openpyxl', 'xlrd')},
                  'pending_adapters': ['DWG', 'DXF', 'IFC', 'OCR', 'computer_vision']}
        print(json.dumps(result, ensure_ascii=False, indent=2)); return 0
    if args.command == 'index':
        data = index_folder(args.input, args.out, args.project)
        export_all(data, args.out, make_excel=not args.no_excel, filename='index.json')
    elif args.command == 'candidates':
        save(args.out, tag_candidates(load(args.index), load(args.mapping))); return 0
    else:
        data = load(args.index); config = load(args.config)
        # Bind computations to still-existing source bytes, not a stale index alone.
        for doc in data['documents']:
            if not Path(doc['path']).is_file() or sha256(doc['path']) != doc['sha256']:
                raise ValueError(f"Fuente cambió o no está disponible: {doc['name']}; volver a indexar")
        out = Path(args.out).resolve()
        sources = [Path(d['path']).resolve() for d in data['documents']]
        if any(out == p or out == p.parent or out.is_relative_to(p.parent) for p in sources):
            raise ValueError('Salida debe estar fuera de carpetas de originales')
        data = run(data, config)
        export_all(data, args.out, index_directory=Path(args.index).parent, make_excel=not args.no_excel)
    print(json.dumps({'project': data['project'], 'documents': len(data['documents']),
                      'references': len(data['references']), 'quantities': len(data['quantities']),
                      'confirmed': sum(q['review_status'] == 'confirmed' for q in data['quantities']),
                      'blocking_observations': sum(o['severity'] == 'blocking' for o in data['observations'])}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        raise SystemExit(2)
