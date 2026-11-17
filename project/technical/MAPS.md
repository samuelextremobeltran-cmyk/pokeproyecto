# Mapas, personajes y eventos — preparación

No se añaden mapas originales en fase 0. Se respeta la estructura upstream.

| Área | Ubicación |
| --- | --- |
| Mapas y eventos | `data/maps/<Mapa>/map.json`, `scripts.inc` |
| Diseños y bloques | `data/layouts/`, `data/layouts/layouts.json` |
| Tilesets | `data/tilesets/`, `graphics/tilesets/` |
| Sprites y gráficos | `graphics/`, datos en `src/data/` |
| Mecánicas configurables | `include/config/` |
| Entrenadores | `src/data/trainers_frlg.party` (fuente FRLG); `trainers_frlg.h` se genera durante la compilación |
| Texto narrativo propio | primero `project/creative/`, después scripts del juego |

## Porymap con FireRed

Seguir `docs/tutorials/how_to_frlg.md` de esta versión:

- Options > Project Settings > General: base `pokefirered`.
- Identifiers: `define_tiles_primary=NUM_TILES_IN_PRIMARY_FRLG`, `define_metatiles_primary=NUM_METATILES_IN_PRIMARY_FRLG`, `define_pals_primary=NUM_PALS_IN_PRIMARY_FRLG`, `define_mask_behavior=METATILE_ATTR_BEHAVIOR_MASK_FRLG`, `define_mask_layer=METATILE_ATTR_LAYER_MASK_FRLG`.
- Para inclusión explícita en FireRed, mapa con `region: REGION_KANTO`, layout con `layout_version: frlg`. Aquí REGION_KANTO es un selector técnico; no decide el nombre de la región original.
- Usar grupos compatibles con FRLG o nuevos grupos; no asumir conexiones válidas entre grupos vanilla de Hoenn y Kanto.
- Si se alterna compilación Emerald/FRLG, ejecutar `make clean`.

No se ha abierto Porymap ni validado su instalación en Windows. Poryscript sigue como herramienta prevista; no hay scripts propios compilados con él todavía.

## Criterios de primera zona — propuesta técnica

Una partida nueva debe recorrer introducción, obtener un inicial, salir a ruta, combatir con la hermana y guardar/cargar sin bloqueos. Antes de implementar hacen falta las decisiones de Sam sobre nombres, iniciales y escena de apertura. La geografía inicial puede prototiparse sin fijar toda la región.
