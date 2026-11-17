# Windows 11 — preparación pendiente de ejecutar en la PC de Sam

La compilación de esta sesión se ejecuta en Linux remoto. No acredita instalación ni pruebas en la Lenovo de Sam.

1. En PowerShell como administrador: `wsl --install -d Ubuntu`. Reiniciar si Windows lo solicita. Si Ubuntu ya está instalado, comprobar `wsl -l -v` y usar versión 2.
2. En Ubuntu: `sudo apt update` y `sudo apt install build-essential binutils-arm-none-eabi gcc-arm-none-eabi libnewlib-arm-none-eabi git libpng-dev python3`.
3. Guardar el repositorio dentro de Linux, por ejemplo `~/projects/pokemon-original`, para evitar la lentitud de `/mnt/c`.
4. Descargar la rama del proyecto con `git clone --branch project/city-sketch https://github.com/samuelextremobeltran-cmyk/pokeproyecto.git ~/projects/pokemon-original` y entrar con `cd ~/projects/pokemon-original`. La carpeta de destino debe ser nueva; el ZIP inicial queda como respaldo de la fase 0.
5. En el repositorio restaurado, ejecutar `bash project/scripts/build.sh`. Resultado esperado: `pokefirered.gba`.
6. Abrir esa ROM local en mGBA. No renombrar ni reutilizar partidas de otras ROM como si su compatibilidad estuviera garantizada.

Fuentes oficiales: `INSTALL.md`, `docs/install/windows/WSL.md`, `docs/install/linux/DEBIAN.md`, `docs/tutorials/how_to_frlg.md` de Expansion 1.17.2. Los comandos de Windows son guía, no pruebas ya ejecutadas.
