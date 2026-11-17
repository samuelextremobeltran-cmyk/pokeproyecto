# Primera ciudad — barrios y recorrido 0.2

Revisión solicitada por Sam el 17 de noviembre de 2026, tras probar la versión 0.1. El mapa conserva el nombre provisional técnico `PrototypeCity_Frlg`. No fija nombres de ciudad o región ni añade historia. Leaf continúa como personaje temporal; los edificios no tienen interacciones ni interiores.

## Distribución aprobada por el encargo

Mapa de 106 × 96 casillas, dividido en barrios con calles de losa sobre césped, manzanas alineadas y zonas verdes, siguiendo la composición clásica de Rojo Fuego.

| Sector | Contenido |
| --- | --- |
| Noroeste residencial | Tres edificios de departamentos, siete casas, lago y parque de barrio |
| Noreste comercial | Hotel, centro comercial, museo, casino, Centro Pokémon, tienda azul y comisaría |
| Suroeste de negocios | Cinco edificios con una fuente en la plaza que rodean |
| Centro | Parque con segunda fuente, flores y senderos |
| Sur | Gimnasio rodeado de árboles, con un paseo de losa conectado al norte |

Total: 23 edificios y tres hitos (dos fuentes y un lago). Los caminos de losa conectan los accesos de todos los edificios. Hay césped entre las calles y las construcciones; el suelo no se rellena completamente con pavimento.

## Correcciones respecto a 0.1

- Coníferas completas: filas 14/15, 30/31 y 38/39 de FRLG. Se elimina la combinación incorrecta que dejaba dos copas superpuestas.
- Se eliminan los falsos bancos hechos con fragmentos de fachada.
- Casas completas con tejado, fachada y puerta; departamentos y oficinas con entrada visible.
- El lago tiene un borde cerrado y las flores se colocan en césped, sin cortar los senderos.
- Se combinan únicamente las piezas utilizadas de Celadon, Pallet, Pewter y Saffron. Se remapean índices de tiles y paletas, conservando las capas y volteos de cada metatile.
- Museo y viviendas adaptan algunos colores a paletas compartidas para respetar el presupuesto de paletas de GBA. No se sustituyen los recursos originales.
- El tileset propio usa sus propias paletas; ya no apunta a las de Saffron pese a contener piezas de otras ciudades.

## Implementación y regeneración

`project/scripts/generate_first_city.py` genera el plano, los bloques y los recursos gráficos de `data/tilesets/secondary/prototype_city_frlg/`. Requiere Pillow solo para regenerar; los archivos generados están incluidos y compilar no necesita ejecutar el generador.

El generador comprueba los 23 edificios exactos, que no se solapen, las colisiones de las fachadas, los límites gráficos de GBA, el perímetro cerrado y que todos los accesos tengan una conexión continua de losa desde el punto de inicio. `first_city.json` describe el plano y sus recursos.

Se amplía `MAX_MAP_DATA_SIZE` de 10,240 a 14,336 entradas para que el mapa de 106×96 y su borde de cámara (121×110) quepan en el búfer. El enlace final comprueba que la memoria EWRAM e IWRAM sigan dentro de los límites. No se aumenta el tamaño de ROM más allá de los 32 MiB del formato existente.

## Jugar

1. Descomprime `Pokeproyecto_Ciudad_0.2.zip`.
2. Abre `Pokeproyecto_Ciudad_0.2.gba` con tu emulador de GBA.
3. Pasa la presentación y elige `NEW GAME`. Leaf aparece en el cruce central.
4. Usa la cruceta para caminar y B para correr, según las teclas configuradas en tu emulador.

Empieza una partida nueva. No cargues un estado rápido ni un guardado de la versión 0.1: cambiaron el tamaño del mapa, el plano y las coordenadas de inicio. No hace falta compilar ni usar Godot para jugar el archivo entregado.

No hay NPC, encuentros, conexiones a la región original, servicios ni interiores. Las puertas son decorativas y permanecen bloqueadas. No hay Pokémon en el equipo inicial.

## Verificación

Los resultados y el SHA-256 de la ROM de esta entrega se registran en `first_city_verification.json`. La prueba en libmgba recorre los 23 accesos por losa, intenta entrar y pulsa A frente a cada fachada; comprueba además las dos fuentes y el lago. Las capturas se revisan visualmente para comprobar árboles, casas, museo, gimnasio y parque. No se atribuyen pruebas de combate o de guardado a esta demo de recorrido.

## Créditos

Motor RHH pokeemerald-expansion 1.17.2; descompilaciones de pret y colaboradores de `CREDITS.md`. Recursos gráficos FRLG incluidos en la base, recombinados para el mapa de Sam. No se utilizaron imágenes de las capturas del usuario como texturas del juego.
