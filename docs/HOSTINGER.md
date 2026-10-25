# Publicación en Hostinger

Flujo: cambios en gis300765 → réplica al repositorio de la cuenta vinculada → despliegue de Hostinger → verificación de la web.

La réplica y el despliegue son dos automatizaciones distintas. Copiar el repositorio una vez no actualiza permanentemente el destino.

## Landing y sitio estático
Ejecutar `python scripts/package_web.py`. El ZIP generado contiene únicamente el contenido de `web/`, con la landing como `index.html`, la aplicación en `app/` y sus recursos.

No desplegar todo este repositorio dentro de public_html: contiene backend y documentación. Publicar solo `web/`, mediante una configuración de despliegue que seleccione esa carpeta, una rama de publicación estática o un artefacto preparado. La vía exacta depende del tipo de plan de Hostinger. Revisar primero en una carpeta de prueba o subdominio y hacer una copia de la web existente antes de sustituirla.

## Plataforma completa
Requiere un servicio compatible con Python/Flask y dependencias geoespaciales. En Hostinger, la documentación indica VPS para Python/Flask. Antes de desplegar: autenticación, permisos de proyectos, dominios permitidos, almacenamiento persistente de datos y un servidor de producción con HTTPS.

La configuración actual del backend es local y su restricción de localhost sigue activa. No se ha cambiado ni se ha publicado ningún servidor.

`web/config.js` permite definir la URL de API si se hospeda por separado. Cambiar la URL no basta: el backend también debe permitir el origen elegido y autenticar las solicitudes antes de exponerse.

Los TIFF, pesos y proyectos deben sobrevivir a las actualizaciones de código y quedar fuera de Git. En esta versión, parte del estado sigue en IndexedDB del navegador; hace falta persistencia de servidor para usuarios y equipos múltiples.

Documentación: https://www.hostinger.com/support/1583302-how-to-deploy-a-git-repository-in-hostinger/
Python: https://www.hostinger.com/support/which-programming-languages-and-frameworks-are-supported-at-hostinger/
