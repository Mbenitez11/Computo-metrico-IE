# Contratos de datos (eqt/1)

## Índice

`schema`, `project`, `documents[]`, `pages[]`, `references[]`, `cells[]`, `observations[]`, `quantities[]`, `rules[]`, `consolidated[]`. Los IDs de documentos derivan de SHA-256; un cambio de bytes cambia el ID. Las referencias derivan de documento/página/localizador. No editar índice manualmente para ocultar errores. Al computar desde CLI se vuelve a comprobar el hash de cada original.

Documentos: ID, nombre, ruta local, extensión, bytes, SHA-256, especialidad y revisión indicativas, revisión declarada, estado, hojas. Una fecha o RV del nombre es solo indicio. Páginas: ID, documento, número desde 1, dimensiones en pt, marco sin rotación, rotación original, texto, imagen y notas de escala. Referencias: ID, documento, página, tipo `word|path`, bbox `[x0,y0,x1,y1]` en puntos, texto o comandos. Celdas: ID, documento, hoja, address, fila/columna desde 1, valor, fórmula/cache cuando existen.

## Configuración

Usar `assets/config.example.json` como estructura. Los IDs de ejemplo son ilustrativos y deben sustituirse por IDs del índice real.

- `documents`: objeto por ID. Cada documento activo exige `sha256`, `family`, `revision`, `status: approved`, `evidence`. Una familia representa un plano/documento, no toda una disciplina. Dos revisiones activas de una familia se bloquean. Para cómputos parciales filtrar selecciones por nivel/sector/circuito y documentos por alcance; ejecutar salidas distintas si se necesitan revisiones concurrentes con alcance dividido.
- `calibrations`: ID único, page_id, source_sha256, p1/p2, real_distance, unit, region, status/evidence. Región explícita homogénea. Unidad `m|mm|cm|ft|in`. Distancia real positiva, puntos diferentes, región dentro de página, puntos dentro de región. Unidades PDF no se confunden con unidades reales.
- `selections`: una partida original por elemento físico o recorrido. ID único, sistema, sector/nivel/circuito, descripción, material_key, specification, unit, source_refs, kind, status/evidence. `count` representa exactamente un elemento; varias referencias pueden documentar el mismo elemento. Si se usa texto debe declararse `tag_is_element_verified: true`. `length` requiere `installation_route_verified: true` y calibration_id. `estimate` requiere value y justification, permanece estimada aunque su supuesto esté aprobado.
- `rules`: ID único, version, description, kind, formula declarada, variables, variable_units, conditions, source, status/evidence, basis_id, sistema/material/especificación/unidad. Las condiciones son coincidencias explícitas con campos de la base. No se ejecuta fórmula libre. Consultar las tres clases implementadas en operation.md.
- `identity_resolutions`: item_ids exactos, keep_id, status/evidence. No descartar por nombre similar. La cantidad autoritativa permanece; las otras quedan `excluded_duplicate` con evidencia.
- `comparisons`: quantity_id y cell_id conocidos, unidad, absolute_tolerance no negativa, status/evidence de equivalencia de alcance. Diferencia fuera de tolerancia produce conflicto y excluye la partida del consolidado. Conteos suelen requerir tolerancia cero. No comparar magnitudes incompatibles ni inferir unidad desde posición de columna.
- `system_reviews`: sistema, coverage_status (`partial|complete_reviewed|not_applicable_reviewed`), document_ids y status/evidence. Declarar ausencia requiere revisión documental; declarar completitud requiere partidas presentes sin pendientes. Sin revisión explícita, cobertura permanece parcial/no revisada. Agregar sistemas personalizados mediante este contrato sin tocar el extractor.
- Responsabilidades: `provision_by` e `installation_by` son campos por partida que se conservan en JSON y Trazabilidad. Nunca filtran cantidades. `kind: pending` y reason permiten conservar materiales/trabajos necesarios sin inventar cantidad, con source_refs si se conocen.

## Partidas

Campos: id, project, system, sector, level, circuit, material_key, specification, description, unit, quantity, method, formula, rule_id, source_refs, document_id, drawing, revision, page_id, geometry, evidence, confidence, review_status, notes, physical_id, calibration_id, basis_id.

Métodos: `measured`, `calculated`, `estimated`, `pending`. Estados: `confirmed`, `pending`, `estimated`, `duplicate_review`, `excluded_duplicate`, `conflict_review`, `basis_review`. Los conflictos conservan valores para auditoría pero no entran al consolidado. Las pendientes tienen cantidad null. Confianza es cualitativa y representa tipo de evidencia, no una probabilidad de exactitud.

Consolidado: agrupar por sistema, material, especificación, unidad y método; preservar todos los source_ids. No agrupar por descripciones iguales. No sumar entre métodos ni incorporar estimaciones. Hoja de precios futura será independiente, relacionada por material_key y versión.

## Observaciones

ID, criticidad (`info|warning|blocking`), código, documentos, partidas, valores, detalle, causa posible, impacto y acción. La causa es una hipótesis para revisión, no un diagnóstico automático. SCALE_UNVERIFIED se resuelve solo por región calibrada. Un documento indexado no significa cobertura completa.

## Completitud general

El inventario técnico incluye todo, independientemente de quién lo provea o monte. Las responsabilidades contractuales se conservan como notas sin filtrar partidas. La falta de datos produce partidas pendientes, nunca omisión silenciosa ni cantidad cero. `coverage` registra sistemas revisados y documentos bloqueados; una selección parcial no demuestra completitud del proyecto.
