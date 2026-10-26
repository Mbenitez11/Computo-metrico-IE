# Validación y confiabilidad

## Comandos reproducibles

Desde la carpeta de la skill:

```sh
python -m unittest discover -s scripts/tests -v
node scripts/tests/test_viewer.js
python scripts/takeoff.py doctor
```

Node es opcional y solo necesario para las pruebas DOM del visor. Las pruebas Python no requieren pytest. Los fixtures se generan dentro de directorios temporales y están rotulados como sintéticos; no representan mediciones de un proyecto de referencia.

## Resultados de desarrollo (26-10-2026)

43 pruebas Python aprobadas: unidades, números no válidos, escala y calibración/hash/región, curvas bloqueadas, revisión documental, conteos, candidatos por etiqueta, duplicados y resolución, estimaciones separadas, fórmulas de conductores/soportes, aprobación y dimensiones de reglas, consolidación, contradicciones, cobertura parcial, pendientes conservados, responsabilidades por terceros, PDF rotado, fuentes inalteradas, exportación de once hojas, referencias de fórmula, serialización segura y cambio de fuente detectado por CLI.

Pruebas DOM ejecutan el JavaScript real del visor en Node con un DOM mínimo. Comprueban selección de referencias, filtros, búsqueda y pendientes sin página. No sustituyen una revisión visual en navegador.

Se abrió un XLSX sintético con LibreOffice headless y se guardó recalculado: conductor esperado `(5+2+1)*3*1,1 = 26,4 m`, obtenido 26,4 en derivados y trazabilidad, sin celdas de error. Se exportaron las once hojas a PDF para inspección de formato. Excel de escritorio y Windows no se ejecutaron. El motor solicita recálculo al abrir; openpyxl por sí solo no evalúa fórmulas.

Se intentó renderizar el visor con Playwright; el paquete existe pero falta el ejecutable de Chromium. No se instaló un navegador ni se declaró completada la revisión visual/interactiva real. Queda pendiente esa comprobación de interfaz, aunque la lógica DOM y la sintaxis JavaScript sí se probaron.

## Forward-test independiente

Otro agente recibió solo la skill y una tarea de cómputo sintético. Creó un PDF propio y configuración con una luminaria provista por terceros, recorrido, regla de conductor y materiales/trabajos pendientes. Resultados: 1 luminaria, 20,5 m de tubería, 61,5 m de conductor y 12 partidas pendientes null. La base confirmó tres partidas; sin escala quedó una; sin revisión documental, ninguna. También probó falta de evidencia y calibración no aprobada.

Detectó tres defectos: procedencia gráfica de pendientes perdida, responsabilidades estructuradas no preservadas y mensaje de escala poco claro. Se corrigieron y se verificaron por regresión y nueva ejecución independiente. Los filtros devolvieron 15 partidas totales, 12 pendientes y 3 confirmadas. No usar estas cantidades como evidencia de exactitud en planos reales.

## Comparación contra cómputo manual

1. Seleccionar hojas y revisiones idénticas, y definir alcance técnico completo. No excluir equipos/materiales por provisión de terceros.
2. Obtener anotación manual independiente por elemento físico y por recorrido, conservando localizador gráfico, sistema, material, unidad y cantidad. Revisar también zonas sin detecciones para identificar falsos negativos.
3. Establecer correspondencias físicas con evidencia; no emparejar solo por nombre.
4. Exportar dos CSV con columnas `physical_id,system,material_key,unit,quantity`. Resolver IDs duplicados antes de comparar.
5. Ejecutar:

```sh
python scripts/benchmark.py predicted.csv truth.csv --ground-truth-reviewed --out benchmark.json
```

6. Revisar verdaderas correspondencias, falsos positivos/negativos, diferencias de cantidades y error absoluto/relativo de cada longitud. El denominador cero deja error relativo null. Los IDs emparejados no garantizan igualdad de cantidades: se reporta discrepancia aparte.
7. Registrar tipo de PDF, calidad del escaneo, reglas y versiones, hojas, fuentes, hashes, tamaño de muestra y revisión del anotador. Definir tolerancia por unidad y proceso antes de evaluar. No informar precisión global a partir de una sola muestra favorable.

## Límites de evidencia

La validación documental no demuestra detección ni longitudes desde DWG. Un Excel suministrado es referencia documental, no verdad manual validada. No se han probado CAD/BIM, OCR, CV o conectividad automática. Distinguir las capacidades pendientes de las funciones ejecutadas.
