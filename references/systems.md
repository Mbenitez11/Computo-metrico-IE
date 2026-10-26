# Especialidades y criterios

La extracción conserva datos sin imponer una especialidad. Mantener catálogos de materiales por proyecto y reglas explícitas. Ningún sistema se marca completo por la sola presencia de sus planos.

| Sistema | Elementos y atributos mínimos | Contraste y límites |
|---|---|---|
| Iluminación | Luminaria/tipo/potencia/montaje, interruptor, sensor, circuito, caja, canalización, conductores | Plantas/leyenda/cuadro. Una etiqueta puede identificar varias luminarias. Separar provisión y montaje. |
| Tomas | TUG/TUE/industrial/hospitalario, mecanismo, caja, circuito, sección/canalización documentada | Planta/cuadro/unifilar. No inferir aislamiento hospitalario por ubicación. |
| Alimentadores | Origen/destino, fases, neutro, PE, sección, material, aislamiento, paralelos y recorrido | Unifilar/cuadro/planta. Derivar cada conductor con regla independiente. Bajadas/reservas requieren datos. |
| Tableros | ID, gabinete, barras, protecciones y accesorios especificados | Cuadro/unifilar/detalle. Mismos nombres no prueban identidad. No dimensionar protecciones. |
| Bandejas | Tipo/ancho/alto/acabado, longitud, curvas/tes/reducciones, unión/tapa/soporte | Planta/detalle/EETT. Separar longitud útil de barras comerciales. No aplicar soportes a suma de rutas sin segmentación. |
| Tuberías | Material, diámetro, recorrido, curvas/uniones/cajas/soportes | Leyenda/detalle/recorrido. Cruce no prueba conexión. Geometría esquemática no prueba longitud instalada. |
| Fuerza | AA, motores, bombas, ascensores y equipos especiales | Plantas por sistema, cuadros y unifilares. Equipos pueden ser provisión de terceros. |
| Respaldo | Generador, transferencia, UPS y auxiliares | Especificación/unifilar/lista de provisiones. Separar equipo, montaje y accesorios. |
| Especiales | Detección, datos, CCTV, acceso, TV y otros | Incluir equipos, mecanismos, canalización, cajas y cableado; registrar responsabilidades por separado. |
| Tierra y SPDA | Conductor, jabalina, conector, caja, malla, equipotencialidad, pararrayos | Planta/detalle/EETT. Cómputo no implica cálculo ni conformidad de resistencia, sección o protección. |

## Reglas complementarias futuras

Curvas, uniones y derivaciones requieren topología y criterio de piezas comerciales; no derivarlas de un porcentaje. Gabinetes, barras y accesorios requieren detalle específico. Longitudes verticales se calculan por cotas de niveles y alturas de montaje; no por altura típica universal. Desperdicio/reserva se modelan como adiciones separadas o total explícito, sin aplicarlos dos veces.

## Completitud y responsabilidades

Incluir absolutamente todo lo necesario para ejecutar la instalación: materiales, equipos, accesorios y trabajos. Ninguna nota de provisión o montaje por terceros autoriza omitir una partida del cómputo técnico. Registrar esas responsabilidades como observaciones independientes, con fuente/celda o párrafo. Mantener provisión y montaje distinguibles para evitar duplicar el equipo físico. Si falta información para cuantificar, crear una partida pendiente sin inventar su cantidad.

No generalizar exclusiones de un proyecto de referencia a otros proyectos. Las exclusiones contractuales de ese ejemplo describen responsabilidades de su contrato; no son reglas para reducir el cómputo. Revisar cada sistema y marcar cobertura como no revisada, parcial, completa revisada o ausencia comprobada. Solo declarar completo un sistema tras contrastar plantas, detalles, leyendas, EETT y documentos complementarios disponibles.
