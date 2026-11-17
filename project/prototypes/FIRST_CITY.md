# Primera ciudad — prototipo de recorrido 0.1

Encargo de Sam, 17 de noviembre de 2026. Este mapa no fija nombre de región, nombre de ciudad, iniciales ni historia. Leaf es la protagonista temporal solicitada para la prueba gráfica.

## Contenido

Mapa nuevo `PrototypeCity_Frlg`, 72 × 64 casillas. Tiene tres edificios altos de oficinas (OF.1–OF.3), dos complejos residenciales (APT.A y APT.B), un hotel rotulado HOTEL, parque con senderos, estanque, bancos, árboles y flores, gimnasio, Centro Pokémon y tienda de techo azul. Se reutiliza arquitectura de FRLG; el hotel se diferencia por su altura y letrero. Las calles conectan las nueve fachadas.

No tiene NPC, encuentros salvajes, conexiones con otros mapas, interiores ni eventos interactivos. Las puertas y edificios permanecen bloqueados. No hay Pokémon en el equipo inicial. La partida nueva entra directamente al mapa con Leaf; B permite correr.

## Implementación

- `include/config/prototype.h`: selector temporal `CITY_PROTOTYPE` y coordenadas de inicio.
- `src/new_game.c`: destino de la prueba, género femenino, nombre LEAF y zapatillas.
- `src/oak_speech.c`: omite la introducción original al elegir New Game en este prototipo.
- `data/maps/PrototypeCity_Frlg/`: mapa nuevo sin eventos.
- `data/layouts/PrototypeCity_Frlg/`: bloques y borde.
- `data/tilesets/secondary/prototype_city_frlg/`: recursos derivados de Saffron y rótulos simples. Usa las paletas de Saffron.
- `project/scripts/generate_first_city.py`: generador reproducible del mapa, necesita Pillow para regenerar los gráficos; los archivos generados están incluidos y compilar no requiere ejecutar este script.
- Se mantienen los mapas originales. El grupo nuevo se añade al final para conservar los identificadores previos.

## Cómo jugar

Descomprime el paquete de prueba y abre `Pokeproyecto_Ciudad_0.1.gba` con un emulador de GBA. En mGBA: File > Load ROM (Archivo > Cargar ROM). Pulsa Start/Enter para pasar la presentación y elige NEW GAME. Se inicia directamente con Leaf en la zona de prueba.

Usa la cruceta o flechas para caminar; mantén B para correr. Las teclas concretas de A/B dependen de la configuración de tu emulador y se pueden revisar en sus ajustes de controles. START abre el menú base del juego. Esta versión no tiene servicios interactivos.

Este archivo es una ROM de Game Boy Advance. Godot no la ejecuta como un proyecto propio. Para esta prueba usa el emulador de GBA. No hace falta compilar ni instalar WSL para jugar el archivo entregado.

Empieza con una partida nueva y un archivo de guardado propio de esta demo, no con una partida o estado rápido del juego original. Los estados rápidos dependen de la ROM y del emulador.

## Verificación de la entrega

Compiló con `make firered -j4` y se ejecutó en libmgba 0.10.5. La secuencia de 8,689 cuadros confirmó inicio en (27, 34), género femenino, recorrido a las nueve fachadas, bloqueo al intentar entrar y ausencia de eventos al pulsar A. Se comprobó además por conectividad que los accesos están unidos y el perímetro está cerrado. El hash y los resultados están en `first_city_verification.json`.

No se probaron combates, interiores ni guardado de partida en esta entrega. No hay ninguna versión de Godot ni pruebas en hardware GBA físico.

## Créditos de recursos

Motor: RHH pokeemerald-expansion 1.17.2; descompilaciones de pret y colaboradores de `CREDITS.md`. Arquitectura y personaje Leaf procedentes de los recursos FRLG incluidos en la base. Composición del mapa y rótulos preparados para el proyecto de Sam.
