# Electrical Quantity Takeoff

Skill para Codex que asiste en cómputos métricos de instalaciones eléctricas con evidencia y trazabilidad. Primera versión funcional 0.1.0.

## Alcance

- Inventario de archivos con SHA-256 y revisión documental.
- Extracción de texto y geometría de PDF vectorial; lectura de XLS/XLSX y EETT TXT/DOCX.
- Conteos asistidos por selección revisada y longitudes con calibración explícita.
- Reglas configurables para conductores, soportes y cantidades adicionales.
- Excel de once hojas, JSON, visor HTML local e informe de observaciones.
- Cantidades medidas, calculadas, estimadas y pendientes diferenciadas.

El cómputo técnico incluye todos los materiales, equipos, accesorios y trabajos necesarios, aunque sean provistos o ejecutados por terceros. Las responsabilidades se anotan sin excluir partidas.

## Límites actuales

DWG, DXF e IFC quedan pendientes de un adaptador validado. OCR y detección visual automática no están implementados. El cómputo PDF requiere revisión de elementos y calibración; no se presupone una escala. No incluye precios ni dimensionamiento eléctrico.

## Instalación y uso

Copiar esta carpeta completa al directorio de skills configurado en Codex. Consultar `SKILL.md` y `references/operation.md`.

Requiere Python 3.11 o superior:

```sh
python -m pip install -r scripts/requirements.txt
python scripts/takeoff.py doctor
python scripts/takeoff.py index /ruta/originales --out /ruta/indice --project MiObra
python scripts/takeoff.py compute /ruta/indice/index.json --config /ruta/config.json --out /ruta/resultado
```

La salida debe estar fuera de la carpeta de originales. `assets/config.example.json` es un ejemplo sintético que requiere sustituir IDs y hashes con los del índice.

Invocación: `Usa $electrical-quantity-takeoff para preparar el cómputo completo de estos planos, manteniendo identificadas las partidas pendientes`.

## Pruebas

```sh
python -m unittest discover -s scripts/tests -v
node scripts/tests/test_viewer.js
```

Se verificaron 43 pruebas Python, lógica DOM del visor y recálculo de fórmulas con LibreOffice. La revisión visual del visor en navegador real sigue pendiente. Los fixtures sintéticos no representan cantidades de un proyecto de referencia.

## Documentación

- `references/PLAN.md`: fases y criterios de aceptación.
- `references/ARCHITECTURE.md`: arquitectura y adaptadores.
- `references/contracts.md`: configuración y modelos de datos.
- `references/research.md`: investigación, fuentes y licencias consultadas.
- `references/systems.md`: criterios por especialidad.
- `references/validation.md`: validación y límites de evidencia.

Dependencias: PyMuPDF, openpyxl y xlrd. Revisar los términos AGPL/comerciales de PyMuPDF antes de redistribuir una aplicación integrada. No se incorporó código de los repositorios AutoConst consultados.
