# Dos cuentas de GitHub

Cuenta de trabajo comprobada: `gis300765`. El correo de la otra cuenta no permite deducir su nombre de usuario.

## Repositorio de trabajo
Origen: https://github.com/gis300765/droneintelligence
Rama de trabajo principal: main. El repositorio es público; se ha autorizado publicar el código y los recursos de la landing. Los TIFF originales, modelos y datos de los proyectos quedan fuera de Git.

## Copia inicial a la cuenta vinculada a Hostinger
Crear un repositorio privado vacío en la cuenta de destino. Se puede duplicar el código mediante Git o utilizar un fork cuando el propietario, los permisos y el plan lo permitan. Nunca introducir contraseñas ni tokens dentro de los archivos del proyecto.

Para una copia inicial de solo main, sin reescribir otras ramas:
```sh
git clone https://github.com/gis300765/droneintelligence.git
cd droneintelligence
git remote add hostinger-account https://github.com/USUARIO_DESTINO/droneintelligence.git
git push hostinger-account main
```
`USUARIO_DESTINO` es un marcador que debes reemplazar por el login real de la otra cuenta. La autenticación se hace mediante el gestor de credenciales o el inicio de sesión de Git de esa cuenta.

## Actualizaciones posteriores
Si el destino se mantiene como copia y no se modifica de forma independiente:
```sh
git pull --ff-only origin main
git push hostinger-account main
```
El push normal se detendrá si existen cambios divergentes. No usar force para resolverlos automáticamente.

Con un fork compatible, también se puede usar Sync fork → Update branch desde GitHub. La sincronización de la copia es un paso distinto del despliegue en Hostinger.

GitHub Importer importa repositorios y su historial, pero no mantiene por sí solo una sincronización permanente. Para automatizar el paso entre cuentas hará falta configurar una identidad con permiso de escritura en el destino. Esa configuración todavía no se ha realizado.

Alternativa que evita duplicados: invitar a `gis300765` como colaborador del repositorio de la cuenta de destino y dar al conector acceso específico a ese repositorio. El usuario decide y realiza la invitación.

Documentación:
- https://docs.github.com/es/migrations/importing-source-code/using-github-importer/about-github-importer
- https://docs.github.com/en/repositories/creating-and-managing-repositories/duplicating-a-repository
- https://docs.github.com/en/pull-requests/how-tos/work-with-forks/syncing-a-fork
