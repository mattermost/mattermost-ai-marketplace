Este es un recurso de apoyo genérico: úsalo cuando surja cualquier duda
concreta durante el triage que la documentación oficial de Mattermost pueda
resolver — no solo sobre un ajuste de configuración o una feature puntual,
sino sobre cualquier aspecto relevante del producto (configuración, roles y
permisos, seguridad, arquitectura, terminología, límites documentados,
comportamiento esperado de cualquier parte del producto, etc.).

Toda la documentación oficial vive ahora en UN solo sitio: el directorio
`docs/` del propio monorepo `mattermost/mattermost` — su checkout local, que
en este documento llamamos `<MM_REPO>` (si no tienes ninguno a mano, clónalo en
un directorio temporal con `gh repo clone mattermost/mattermost`). NO uses nunca el repo
`mattermost/docs` (archived, ya no se mantiene — puede tener contenido
desactualizado o directamente eliminado) ni lo cites como fuente, aunque
aparezca en un resultado de búsqueda o en tu memoria de otro momento.
Dentro de `docs/` hay dos subárboles:
- **End-user / admin docs** (lo que se despliega en docs.mattermost.com):
  `docs/main/` (p.ej. `docs/main/administration-guide/...`)
- **Developer docs** (lo que se despliega en developers.mattermost.com —
  arquitectura interna, plugins, APIs, convenciones de desarrollo):
  `docs/develop/`
Esto aplica igual si lo que estás investigando pertenece a otro repo (p.ej.
Playbooks): la documentación de TODO el ecosistema Mattermost vive aquí,
bajo `docs/` del monorepo — nunca en el repo de Playbooks/Boards/etc. ni en
`mattermost/docs`.

## Paso 1: usa el índice, no grep a ciegas sobre el repo entero

Existen dos índices pre-generados (`mattermost-docs-index.md` y
`mattermost-developer-docs-index.md`), optimizados para que un agente los recorra
rápido, pero NO se distribuyen con este plugin (son muy grandes); si no los
tienes, salta directamente al Paso 2 y navega `docs/main/` y `docs/develop/`.

AVISO — esos dos índices están desactualizados tras la migración: se
generaron cuando la documentación aún vivía en `mattermost/docs` (ficheros
`.rst` bajo `source/`) y en el repo de developer docs por separado. Los
ficheros reales ahora están bajo `docs/main/` y `docs/develop/` del monorepo,
en formato `.mdx`, con nombres/rutas que no coinciden uno a uno con lo que
listan estos índices. Trátalos como una pista de qué tema suele vivir en qué
subcarpeta, nunca como la ruta exacta del fichero — verifica siempre la ruta
real antes de leer (`ls`/`Glob` sobre `docs/main/<área>/` o `docs/develop/<área>/`),
y si no cuadra, cae directamente al Paso 2 (grep sobre el repo real) en vez
de insistir con la ruta que da el índice. Regenerar estos índices para que
reflejen `docs/main/`+`docs/develop/` es trabajo pendiente, no asumas que ya
está hecho.

## Paso 2: leer/actualizar el repo fuente

El checkout local del monorepo es compartido con el resto del pipeline de
triage y puede estar en cualquier estado — NO asumas que está en `master`,
puede estar en una rama de trabajo (p.ej. un worktree de reproducción TDD en
curso) o tener cambios sin commitear:
```bash
git -C <MM_REPO> branch --show-current
git -C <MM_REPO> status --short
```
- Si está en `master` Y el working tree está limpio: actualiza y lee del
  disco directamente:
  ```bash
  git -C <MM_REPO> pull origin master
  ```
- Si está en cualquier otra rama, o tiene cambios sin commitear: NO cambies
  de rama ni toques ese working tree (puede ser trabajo en curso, tuyo o de
  otra sesión). Lee el contenido de `master` sin afectar el checkout — esto
  es lo normal en la práctica, y también es lo que te garantiza que siempre
  estás viendo la última versión de la documentación aunque no puedas
  cambiar de rama:
  ```bash
  git -C <MM_REPO> fetch origin master
  git -C <MM_REPO> show origin/master:docs/main/<ruta-relativa>
  git -C <MM_REPO> show origin/master:docs/develop/<ruta-relativa>
  ```
En cualquier caso, la documentación que consultes debe ser siempre la de
`origin/master` — nunca la de una rama de feature/fix en curso, que puede
tener cambios sin mergear todavía.
Si el `pull`/`fetch` falla (sin red, etc.), sigue adelante con la copia local
que ya tengas y dilo explícitamente en tu respuesta — no lo trates como
bloqueante.
