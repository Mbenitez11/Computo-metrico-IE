# Arquitectura

## Elección

Una skill principal con núcleo Python y adaptadores independientes. Múltiples skills multiplicarían índices, revisiones y reglas. Separar especialidades cuando tengan contratos y validación propios.

```
scripts/takeoff.py        CLI index / compute / doctor
scripts/eqt/model.py      IDs, hashes, números y unidades
scripts/eqt/extract.py    PDF / Excel / TXT / DOCX
scripts/eqt/engine.py     revisión, calibración, reglas, conflictos
scripts/eqt/export.py     Excel, informe y visor
scripts/tests/           pruebas y fixtures sintéticos
assets/                  configuración y visor locales
references/              contratos y criterios de aceptación
```

## Flujos y límites

Documentos no confiables: leer datos, nunca ejecutar fórmulas/macros. xlrd expone valores almacenados de XLS, sin reconstruir fórmulas originales. XLSX conserva fórmula y caché separados; fórmulas sin caché se señalan.

PDF: `get_text` y `get_drawings`, coordenadas sin rotación en puntos PDF, render en idéntico marco y rotación original en metadatos. Dibujar Bézier en visor pero bloquear longitud. No inferir conexiones, fases, secciones o bajadas por cruces gráficos.

Escala: dos puntos y distancia real dentro de región explícita; validar positividad, hash y aprobación. Factor metros/punto solo para referencias totalmente contenidas en región homogénea. Regiones múltiples por página. Nota 1:N es indicio, no medición validada.

DWG: registrar firma ACxxxx y bloquear geometría. Convertir copia mediante AutoCAD o herramienta local compatible autorizada; registrar versión/hash y relación original→convertido. Verificar layouts, xrefs, bloques dinámicos, unidades y cotas. No abrir DWG con ezdxf. DXF/IFC son extensiones previstas, no adaptadores de cantidades v1.

Escaneos: imagen y OCR/calibración pendientes. OCR/OpenCV futuros generarán candidatos con localización y métricas. EETT DOCX/TXT: evidencia textual e interpretación asistida.

## Modelo

`index.json`: documentos, páginas, geometría y celdas con IDs por contenido/localizador. `config.json`: alcance, revisiones, selección, calibración y reglas. `quantities.json`: originales, derivados, observaciones y consolidado con IDs de origen. Visor serializa estos datos, sin lógica de cómputo.

Especialidad representada por `system`, sin cambiar extractor. `material_key`/`specification` separan materiales. Futuras cotizaciones/mano de obra se relacionan por claves en tablas económicas independientes.

## Duplicación

Hash repetido: señalar archivo. Referencia seleccionada dos veces: bloquear ambas. Geometría coincidente: señalar y bloquear hasta resolución. Identidad física explícita entre fuentes: bloquear ambas salvo resolución documentada con partida autoritativa. Nombres no prueban identidad. Dos revisiones de una familia declarada no pueden estar activas simultáneamente para el mismo alcance en v1.

## Tecnologías

PyMuPDF reúne texto, geometría y render; atender licencia. openpyxl exporta XLSX con fórmulas; xlrd lee BIFF. Shapely puede aportar topología futura; no se necesita para segmentos. ezdxf sirve para DXF, no DWG. OpenCV necesita corpus etiquetado. IfcOpenShell puede aportar GlobalId/relaciones/QTO; no sustituir longitud real por bounding box.
