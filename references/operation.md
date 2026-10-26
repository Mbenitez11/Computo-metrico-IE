# Operación e instalación

## Dependencias

Python 3.11 o superior. `scripts/requirements.txt`: PyMuPDF (PDF), openpyxl (XLSX), xlrd (XLS). El motor numérico usa biblioteca estándar. No requiere API keys, GPU, servicios cloud ni conversor CAD para su primera versión. Ejecutar `python scripts/takeoff.py doctor` para ver disponibilidad. No se instalan dependencias automáticamente.

En Windows, abrir PowerShell en la carpeta de la skill:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r scripts\requirements.txt
.\.venv\Scripts\python.exe scripts\takeoff.py doctor
.\.venv\Scripts\python.exe scripts\takeoff.py index "C:\MiObra\Originales" --out "C:\MiObra\Indice" --project MiObra
.\.venv\Scripts\python.exe scripts\takeoff.py compute "C:\MiObra\Indice\index.json" --config "C:\MiObra\config.json" --out "C:\MiObra\Resultado"
```

Linux/macOS: `python3 -m venv .venv`, instalar requirements con el Python del entorno y usar los mismos subcomandos. Instalar una copia de la carpeta en el directorio de skills que indique la versión de Codex utilizada, o usar la skill nativa de Work creada por este proyecto. No copiar datos de clientes al directorio de la skill. Reiniciar la sesión si la instalación local no se descubre inmediatamente.

## Uso por etapas

`index`: inventario, PDF, Excel y evidencia textual. `--no-excel` omite XLSX cuando solo interesa extracción. Errores por archivo quedan en observaciones y el resto continúa; revisar esos estados antes de interpretar cobertura.

`candidates index.json --mapping mapping.json --out candidates.json`: mapping es objeto de etiquetas exactas, por ejemplo `{"L1":"luminaria-tipo-1"}`. La salida tiene quantity null y no se mezcla con cómputo. No recorrer solo etiquetas para afirmar cantidad de artefactos: puede haber una etiqueta por recinto o símbolos sin etiqueta.

`compute`: comprobar originales, seleccionar revisión, validar calibraciones, medir selecciones, bloquear duplicados, derivar, cotejar y exportar. La carpeta de salida debe quedar fuera de las carpetas de originales. No sobrescribir el índice con resultados. Para alcance parcial, seleccionar únicamente referencias de los sistemas/sectores/niveles deseados y registrar esa limitación al entregar.

## Reglas deterministas

Cada regla necesita todas sus variables incluso cuando el valor documentado sea cero. No usar ceros como sustituto de un dato desconocido.

| kind | Variables y unidades | Fórmula ejecutada |
|---|---|---|
| conductor | count [u] entero positivo; vertical [m]; reserve [m]; waste [1] entre 0 y 1 | `(L+vertical+reserve)*count*(1+waste)` |
| supports | spacing [m] positivo; endpoints [u] entero 0/1/2; single_run_verified=true | `ceil(L/spacing)+endpoints` según criterio aprobado |
| allowance | fraction [1] entre 0 y 1 | `L*fraction`, cantidad adicional, no total con desperdicio |

Para alimentadores, crear reglas distintas por conductor/especificación (fases, neutro y PE) con cantidades de cables justificadas por documentación. count representa el total explícito de cables de ESA especificación, incluidos paralelos cuando consten. No calcular secciones, número de fases o PE por deducción. Documentar origen/destino en descripción/circuito y evidencia; extracción automática de topología queda pendiente.

La fórmula declarada es documentación; kind selecciona implementación limitada. No hay eval ni ejecución de código de documentos. Las reglas se evalúan secuencialmente: una regla puede usar el ID derivado de otra anterior; no se permiten dependencias hacia adelante ni ciclos. Las bases sin confirmar producen derivados pendientes.

## Salidas

Once hojas Excel: resumen, consolidado, sistema, sector/nivel, mediciones, derivados, alimentadores/conductores, observaciones, reglas/supuestos, trazabilidad e índice. No hay precios. Las variables de reglas están diferenciadas como entradas y las fórmulas derivadas se relacionan con la base. Las cantidades originales provienen de la ejecución; para cambiar geometría, identidad, revisión o aprobación editar configuración y recalcular.

El XLSX solicita recálculo completo al abrir. openpyxl escribe fórmulas pero no las evalúa: verificar con Excel/LibreOffice antes de usar resultados recalculados. Cambiar variables en Excel no modifica JSON/visor ni revalida condiciones del motor; para entregables coherentes cambiar config y ejecutar de nuevo. El visor es de lectura y muestra plano, símbolos seleccionados, recorridos, partidas y observaciones sin servidor ni conexión de red. Llevar imágenes y HTML juntos.

## Compatibilidad y límites

Probado en Python del entorno Linux. Comandos Windows documentados, no ejecutados en Windows. DWG AC1032 requiere conversión compatible; PDF de copia exportada y DXF/IFC no se identifican automáticamente como el mismo elemento original. Falta enlazar ese linaje y validar antes de combinar fuentes. No soporta PDF cifrado sin credenciales, detección universal de símbolos, OCR automático ni medidas exactas de Bézier. Un PDF mixto puede contener elementos raster aunque tenga vectores.
