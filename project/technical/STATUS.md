# Fase 0 — informe de verificación

Fecha local de Sam: 16 de noviembre de 2026. Sesión de ejecución Linux remoto; no es la PC Windows del usuario.

## Resultado

Compilación FireRed completada y arranque comprobado con mGBA 0.10.5 mediante su biblioteca oficial, sin ventana gráfica. Se observaron presentación, menú, instrucciones interactivas y diálogo de Oak. No hay contenido original jugable incorporado.

## Versión fijada

- Repositorio: https://github.com/rh-hideout/pokeemerald-expansion
- Último release estable indicado por GitHub al consultar: `expansion/1.17.2`, publicado el 31 de octubre de 2026, no prerelease.
- Commit exacto: `79dd436920845ebc145577649de624f65298c209`.
- Repositorio propio conectado el 17 de noviembre de 2026: https://github.com/samuelextremobeltran-cmyk/pokeproyecto . Se verificaron permisos de lectura y escritura.
- Rama del proyecto: `project/phase-0`, creada desde el release 1.17.2. La rama `master` del fork conserva la revisión upstream copiada al crear el fork; no es la base verificada de este informe.
- Referencia FireRed: https://github.com/pret/pokefirered . No se mezcló su código por separado.

## Dependencias y compilación realmente ejecutadas

Debian 13 x86_64. GCC/G++ y GNU Make del entorno. Compilador ARM GCC 14.2.1 (`15:14.2.rel1-1`), binutils ARM `2.44-3+23+b1`, newlib `4.5.0.20241231-1`, cabeceras libpng `1.6.48-1+deb13u5`. mGBA `0.10.5+dfsg-1`.

No había sudo ni compilador ARM. Se descargaron paquetes Debian oficiales y se extrajeron en una carpeta de herramientas local. Se añadieron enlaces relativos de newlib que normalmente gestiona la instalación Debian. Se configuró pkg-config para libpng. Estas adaptaciones solo afectan al entorno, no al código del juego.

Comando del motor: `make firered -j4`. Tras completar la primera compilación se probó también `bash project/scripts/build.sh`; terminó con éxito y el SHA-256 de la ROM fue idéntico. Esta segunda ejecución es una reconstrucción incremental, no una segunda compilación limpia.

- Salida: `pokefirered.gba`, 33,554,432 bytes (32 MiB con relleno).
- SHA-256: `e271717c658b7a3bc7c02fd714410f8dcda1efdfe8415dfc1adcf13830e98c5a`.
- EWRAM: 226,704 B de 256 KiB, 86.48%.
- IWRAM: 28,648 B de 32 KiB, 87.43%.
- Contenido ROM enlazado: 26,963,028 B de 32 MiB, 80.36%.
- Primera compilación: 209 avisos libpng `bKGD: invalid index` en recursos originales; no impidieron generar la ROM. No se modificaron gráficos para ocultarlos.

## Comprobación en emulador

Se construyó un pequeño programa C que carga la ROM con libmgba, ejecuta cuadros de GBA y envía entradas mediante `setKeys`. No se utilizó una ROM BIOS externa; se empleó la emulación de BIOS de mGBA.

La secuencia reproducible está en `evidence/boot-input.txt`; el código del programa, en `evidence/mgba_probe.c` del paquete. Los nombres iniciales de algunas capturas describen la intención de la entrada y no una aserción automática sobre su contenido. Se inspeccionaron visualmente los resultados:

| Prueba | Resultado observado |
| --- | --- |
| Carga y ejecución de ROM | Correcta, el proceso completó la secuencia |
| Presentación FireRed | Charizard visible |
| Menú principal | NEW GAME y OPTION visibles |
| Elegir nueva partida | Aparece la introducción de controles |
| Respuesta al botón A | Avanza de una página de controles a otra |
| Introducción narrativa base | Oak visible con texto del Pokémon Professor |

Se ejecutaron 3,137 cuadros en la secuencia final. Esto acredita arranque y respuesta inicial, no una prueba completa del juego. Audio, combates, guardado/carga dentro del juego, crianza, conexión, todos los mapas y rendimiento en GBA física no se probaron. La primera zona original tendrá su propia prueba de recorrido y guardado.

## Compatibilidad FireRed confirmada por código y documentación

El Makefile configura FIRERED, título POKEMON FIRE, código BPRE, nombre `pokefirered` y MAP_VERSION=firered. Hay mapas `_Frlg`, pantalla de título FRLG, diálogos de Oak y guía oficial `docs/tutorials/how_to_frlg.md`. No es solo cambiar el nombre del archivo de Emerald. Sigue siendo el motor de Expansion, con sus cambios y limitaciones; no una reconstrucción binariamente idéntica al FireRed comercial.

La guía pide `make clean` al alternar Emerald y FRLG. Porymap requiere ajustes y mapas/layouts con selectores compatibles; véase `MAPS.md`. No se probó Porymap ni Poryscript en esta sesión.

## Configuración por decidir o aplicar

- Generaciones I–IX están habilitadas en `include/config/species_enabled.h`; esto no define una Pokédex regional ni encuentros originales.
- `I_REUSABLE_TMS` está en FALSE en `include/config/item.h`. El requisito de Sam es activarlas; queda registrado para la primera configuración de jugabilidad tras esta referencia sin cambios.
- Megaformas y otras formas especiales figuran habilitadas en la base. Su presencia técnica no significa que Sam haya decidido usarlas en su campaña.
- La configuración de combate usa numerosas reglas `GEN_LATEST`. Habrá que revisar y fijar las reglas deseadas antes de equilibrar equipos; no asumir equivalencia exacta con una generación por el nombre de la base.
- No se han cambiado iniciales, nombres, personajes, mapas, texto, medallas ni eventos de la ROM.

## Fuentes oficiales consultadas

- https://github.com/rh-hideout/pokeemerald-expansion/releases/tag/expansion/1.17.2
- `README.md`, `INSTALL.md`, `docs/install/linux/DEBIAN.md`, `docs/install/windows/WSL.md` en ese tag.
- `docs/tutorials/how_to_frlg.md`, `Makefile`, configuración y código de esa copia.
- Cabeceras de libmgba 0.10.5 y `tools/mgba/README.md` de Expansion.

## Próximo trabajo

Conservar esta base compilable en el repositorio propio; ejecutar la guía WSL2 en su PC; decidir nombres e iniciales y diseñar un pueblo pequeño con prólogo. Toda decisión importante de historia se consulta con Sam.
