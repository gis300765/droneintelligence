# droneintelligence

Landing e interfaz geoespacial en negro y plomo, con backend local Python para GeoTIFF, teselas y conectores de análisis.

## Estructura
- `web/index.html`: landing.
- `web/app/index.html`: plataforma.
- `web/landing-assets/`: recursos optimizados de la landing y licencia de Inter.
- `web/config.js`: dirección pública de API cuando se sirve desde otro origen.
- `backend/`: servidor Python y dependencias.
- `scripts/package_web.py`: genera un paquete estático que no incluye el backend ni los datos.
- `docs/`: réplica entre cuentas y publicación.

## Ejecución local
Python 3.12 o compatible:

```sh
python -m venv .venv
# Windows:
.venv\Scripts\python -m pip install -r backend/requirements.txt
.venv\Scripts\python backend/server.py
```

En Linux/macOS usa `.venv/bin/python`.
Abre `http://127.0.0.1:8765/` para la landing y `/app/` para el software.

## Datos
Los TIFF, modelos y el manifiesto de los proyectos privados no se incluyen en Git. Copia por un canal privado las carpetas `data/` y `models/` del entorno local si necesitas esos proyectos en otro equipo. El servidor espera `data/library.json`, `data/source/` y las vistas previas. Las imágenes WebP incluidas son recursos derivados de los ejemplos utilizados en la landing: contienen vistas aéreas cuya publicación en este repositorio ha sido autorizada por su propietario.
La publicación del repositorio no concede por sí sola una licencia de redistribución del software ni de las imágenes; esa licencia se definirá por separado.

## Estado de publicación
El backend está preparado para uso local. Mantiene restricciones de localhost y no implementa autenticación multiusuario. No publicar el servidor de desarrollo ni exponer datos privados sin adaptar dominios, autenticación, permisos, almacenamiento y servidor de producción.
La landing estática sí puede empaquetarse por separado. Con un hosting sin Python, el HTML de la aplicación se visualizará, pero los servicios Python permanecerán desconectados hasta configurar una API compatible.
Consulta `docs/REPLICAR.md` y `docs/HOSTINGER.md`.

## Comprobaciones
```sh
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python scripts/package_web.py
```
