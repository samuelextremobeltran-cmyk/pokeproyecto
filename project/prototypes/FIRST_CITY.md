# Primera ciudad — plano de Sam, versión 0.3

Reorganización solicitada el 17 de noviembre de 2026 a partir del croquis `project/references/city_layout_sam_20261117.png`. Esta distribución sustituye la organización por cuadrantes de 0.2. La ciudad y región siguen sin nombre definitivo. Leaf continúa como personaje temporal y los edificios siguen sin interacciones ni interiores.

## Distribución según el dibujo

Mapa de 118 × 92 casillas, con proporción cercana a la del plano de referencia.

| Ubicación | Contenido |
| --- | --- |
| Noroeste | E1 a la izquierda, E2 arriba del parque, E3 a la derecha, E5 abajo a la izquierda y E4 abajo a la derecha |
| Parque entre los cinco edificios | Primera fuente y flores |
| Franja norte comercial | Hotel y casino |
| Debajo del hotel y casino | Centro Pokémon a la izquierda, centro comercial en medio y tienda azul a la derecha |
| Debajo de ese bloque | Museo horizontal |
| Cruce central, al oeste de la avenida | Comisaría, entre el lago y el bloque comercial |
| Oeste central | Lago dentro de su parque |
| Suroeste | Gimnasio dentro de un arbolado, con sendero en L hacia la avenida central |
| Este, debajo del museo | Parque grande con la segunda fuente y flores |
| Sureste | Cuatro casas en la fila superior y tres en la inferior; parque residencial entre ambas, con departamentos a los lados |

Se mantienen las cantidades del encargo anterior: siete casas y tres departamentos, además de los cinco edificios de negocios y los servicios. El croquis se interpreta como referencia de posiciones; el tercer departamento queda junto al bloque oriental del parque residencial. Esta interpretación se comunicó antes de trabajar. Total: 23 edificios, dos fuentes y un lago.

Las vías del plano se representan con losa de Rojo Fuego. Una avenida vertical separa la mitad occidental de la zona comercial y residencial. Todos los accesos están conectados mediante pavimento, sin necesidad de atravesar césped. Las puertas permanecen bloqueadas.

## Recursos y límites

Se conservan los recursos corregidos en 0.2: coníferas completas, casas y puertas, bordes de lago cerrados y paletas propias del tileset combinado. E1 y E3 tienen más altura mediante repetición de filas completas de ventanas. Los cinco edificios no tienen nombres narrativos; E1–E5 son identificadores del plano.

`project/scripts/generate_first_city.py` regenera mapa y recursos, y valida cantidades, solapamientos, colisiones, acceso por losa, límites gráficos y perímetro. Requiere Pillow solo para regenerar; los archivos generados están incluidos.

El búfer de mapa sigue siendo de 14,336 entradas. El plano de 118×92, incluyendo el margen de cámara de 133×106, necesita 14,098 entradas. No se amplió respecto a 0.2. El enlace verifica el uso de memoria de GBA.

## Probar la ROM

1. Descomprime `Pokeproyecto_Ciudad_0.3.zip`.
2. Abre `Pokeproyecto_Ciudad_0.3.gba` en tu emulador de GBA.
3. Pasa la presentación y selecciona `NEW GAME`.
4. Leaf aparece en el cruce de la avenida central; usa la cruceta para caminar y B para correr.

No cargues estados rápidos ni una partida anterior: han cambiado las posiciones de los edificios y el punto de inicio. No hace falta usar Godot ni herramientas de compilación para jugar el archivo entregado.

La prueba es de recorrido: no hay NPC, encuentros, interiores ni servicios interactivos. No hay Pokémon en el equipo inicial.

## Verificación

`first_city_verification.json` registra el hash de la ROM y la prueba con libmgba 0.10.5: inicio con Leaf, acceso a los 23 edificios por losa, colisiones frente a cada fachada, pulsación de A sin activar eventos y visita de las dos fuentes y del lago. El mapa completo se compara visualmente con el croquis. No se atribuyen pruebas de combate o de guardado a esta versión.

## Créditos

Distribución: croquis de Sam. Motor: RHH pokeemerald-expansion 1.17.2, descompilaciones de pret y contribuyentes de `CREDITS.md`. Arquitectura y Leaf: recursos FRLG de la base. El croquis es una referencia de diseño y no se usa como textura del juego.
