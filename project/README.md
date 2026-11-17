# Pokémon original — preproducción

Proyecto de Sam. Título definitivo pendiente. La estética deseada es Pokémon GBA, especialmente Rojo Fuego/Verde Hoja. El juego tendrá una región moderna original y una aventura clásica con gimnasios, rivales, organización criminal, Alto Mando y campeona.

## Documentación

- `creative/MASTER.md`: decisiones del documento de transferencia v0.1 y propuestas abiertas.
- `technical/STATUS.md`: resultados reales de la fase 0 y limitaciones.
- `technical/WINDOWS.md`: preparación de Windows 11 con WSL2.
- `technical/MAPS.md`: rutas de trabajo y configuración de Porymap.
- `scripts/build.sh`: compilación FireRed con registro de salida.

El documento creativo organiza la transferencia; no redefine su canon. El texto original completo permanece en la conversación de origen. Toda ampliación debe indicar si es decisión de Sam o sugerencia.

## Base técnica

Repositorio propio: https://github.com/samuelextremobeltran-cmyk/pokeproyecto . Rama actual de la ciudad: `project/city-districts`, fijada en la base estable que ya compiló. La rama `master` conserva la copia upstream y puede tener cambios posteriores al release probado.

Para descargar la rama del proyecto:

```bash
git clone --branch project/city-districts https://github.com/samuelextremobeltran-cmyk/pokeproyecto.git
cd pokeproyecto
bash project/scripts/build.sh
```

Instala antes las dependencias de `technical/WINDOWS.md`. Con este repositorio ya no hace falta usar el script de restauración del ZIP inicial.

Based off RHH's pokeemerald-expansion 1.17.2 https://github.com/rh-hideout/pokeemerald-expansion/

Se conserva `CREDITS.md` del proyecto original. `pret/pokefirered` es una referencia, no otro motor que se mezcle automáticamente. Godot y Pokémon Essentials quedan fuera de la base principal.

## Hitos

0. Preparación y compilación sin cambiar contenido jugable.
1. Pueblo original, casa, introducción, entrega de inicial, primera ruta, encuentros, rival y guardado.
2. Primera ciudad, gimnasio y misión de Nunca Jamás.
3. Primera demo narrativa integrada y probada.
4. Expansión gradual de la región.
5. Campaña completa, legendario, hermanas y campeona.
6. Equilibrio, correcciones y parche de distribución.

Primer mapa original de prueba: `PrototypeCity_Frlg`. La versión 0.2 tiene barrios residencial, comercial y de negocios, parque central y gimnasio al sur. Mantiene los edificios sin interacciones y a Leaf temporalmente como personaje jugable. Véase `prototypes/FIRST_CITY.md`. No hay personajes originales definitivos ni historia implementada todavía.
