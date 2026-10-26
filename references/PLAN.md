# Plan técnico

Primera versión: núcleo documental PDF vectorial con selección revisada, indexación XLS/XLSX, reglas deterministas y entregables. Una skill con módulos evita duplicar contratos. No intentar detección universal, CAD y BIM simultáneamente.

| Fase | Aceptación medible | Alcance v1 |
|---|---|---|
| 1. Núcleo | Hash por archivo; texto/trazos con página/coordenadas; errores por documento; sin escala se bloquea longitud | PDF vectorial, Excel, TXT/DOCX; escaneo señalado |
| 2. Conteos | Unidad ligada a referencia revisada; etiqueta sin verificación queda candidata; fixture reproducible | Selección asistida y etiquetas exactas; CV pendiente |
| 3. Longitudes | Línea 3-4-5 calibrada; fuera de región/curva no soportada bloqueado | Segmentos rectos y rectángulos PDF; CAD y bajadas automáticas pendientes |
| 4. Derivados | Regla versionada aprobada; variables/unidades; sin supuestos implícitos | Conductores, soportes y reserva/desperdicio explícitos |
| 5. Entregables | Once hojas Excel; visor ligado a IDs; duplicados excluidos; contradicciones informadas | Base funcional; cotejo mediante relaciones explícitas |
| 6. Extensiones | Adaptador probado contra exportación y cómputo manual del mismo proyecto | DWG/DXF/IFC, OCR, CV, conectividad y costos pendientes |

## Secuencia

Investigar cuatro repositorios y documentación oficial leyendo licencias reales. Definir contratos. Implementar índice → evidencias → selección/calibración → cantidades → reglas → controles → salidas. Probar fixtures sintéticos rotulados y documentos reales. Registrar límites un proyecto de referencia sin convertir su Excel en cómputo manual validado. Forward-test independiente, corregir y guardar con commit/push.

## Dependencias y riesgos

Python 3.11+, PyMuPDF, openpyxl, xlrd. Sin servicios cloud. Revisar licencia AGPL/comercial de PyMuPDF antes de redistribuir aplicación integrada. No hay conversor CAD compatible instalado. No ejecutar software externo descargado durante investigación. Precios permanecen fuera del cómputo métrico.
