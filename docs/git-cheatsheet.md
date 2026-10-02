# Cheatsheet de Git: el flujo profesional

## 0 · Configuración (una vez por máquina)
```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu@correo.com"
git config --global init.defaultBranch main
gh auth login       # conecta esta máquina con tu cuenta de GitHub
```
## 1 · Empezar un proyecto (una vez por proyecto)

### Caso A: el proyecto nace en tu máquina
```bash
mkdir proyecto && cd proyecto
git init                                   # crea el repositorio local
# ...creas .gitignore, README, código...
git add .
git commit -m "Inicializa el proyecto"
gh repo create proyecto --private --source=. --push   # crea el repo en GitHub, lo conecta y sube main
```

### Caso B: el proyecto ya existe en GitHub
```bash
git clone https://github.com/usuario/proyecto.git     # descarga el repo, ya conectado
cd proyecto
```
`origin` es el nombre que Git le da al repositorio remoto. `git remote -v` muestra a dónde apunta.

## 2 · El ciclo de cada funcionalidad (se repite siempre)
```bash
# 1. Parte siempre de un main actualizado
git switch main
git pull

# 2. Crea una rama para ESTA tarea
git switch -c feature/nombre-corto

# 3. Trabaja en ciclos pequeños
git status                         # ¿qué cambió?
git diff                           # ¿qué cambió exactamente?
git add archivo1 archivo2          # elige qué entra en la foto
git commit -m "Agrega validación de k"
#    ...repite el paso 3 las veces que haga falta...

# 4. Sube la rama a GitHub
git push -u origin feature/nombre-corto    # -u solo la primera vez; después basta "git push"

# 5. Abre el pull request: de tu rama HACIA main
gh pr create --base main --fill

# 6. Revisa el PR en GitHub y haz el merge ahí (o con el comando)
gh pr merge --merge --delete-branch

# 7. Actualiza tu máquina y limpia
git switch main
git pull
git branch -d feature/nombre-corto         # borra la rama local ya integrada
```
## 3 · Si aparece un conflicto
```bash
git status                         # lista los archivos "both modified"
# Abre cada archivo: deja el código final y BORRA las líneas <<<<<<<, ======= y >>>>>>>
python -m pytest                   # verifica que todo funciona
git add archivo_resuelto
git commit                         # termina el merge
```
Antes de cualquier commit, esto no debe devolver nada: `git grep -n "<<<<<<<"`.

## 4 · Consultar
| Comando                           | Para qué                                      |
| --------------------------------- | --------------------------------------------- |
| `git status`                      | Estado actual. Úsalo todo el tiempo           |
| `git log --oneline --graph --all` | El historial con sus ramas                    |
| `git diff · git diff --staged`    | Cambios sin preparar · cambios ya en staging  |
| `git branch -a`                   | Todas las ramas, locales y remotas            |

## 5 · Deshacer
| Situación                                                 | Comando                                 |
|-----------------------------------------------------------|-----------------------------------------|
| Quitar un archivo del staging (sin perder los cambios)    | `git restore --staged archivo`          |
| Descartar los cambios de un archivo (se pierden)          | `git restore archivo`                   |
| Corregir el mensaje del último commit (aún sin subir)     | `git commit --amend -m "Mensaje nuevo"` |
| Deshacer un commit ya subido, sin reescribir el historial | `git revert <id-del-commit>`            |
| Guardar cambios a medias para cambiar de rama             | `git stash` · luego `git stash pop`     |

## 6 · Reglas de oro
1. **Nunca hagas commits directos en `main`.** Todo entra por una rama y un PR.
2. **Una rama = una tarea.** Ramas cortas, de horas o un par de días.
3. **El PR va de tu rama hacia `main`**, nunca al revés.
4. **`git pull` en `main` antes de crear una rama.**
5. **Ejecuta los tests antes de cada commit.**
6. **Commits pequeños, con mensajes en imperativo** que digan qué hace el cambio.
7. **Nunca subas datos, modelos, secretos ni entornos virtuales.**