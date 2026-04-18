# 🧹 Script Python — Organizador de Descargas para macOS

Conjunto de scripts en Python para **analizar, organizar y limpiar** la carpeta `~/Downloads` (o cualquier otra) en macOS de forma segura.

Pensado para esos casos en los que la carpeta de descargas se ha convertido en un cementerio de instaladores `.dmg`, vídeos de clase, ZIPs de prácticas duplicados y descargas a medias.

---

## 📦 Contenido del proyecto

```
script_python/
├── organizador.py      # Organizador básico por tipo de archivo
├── analizar.py         # Analizador read-only (no toca nada)
├── organizar_v2.py     # Organizador avanzado con detección de duplicados
└── README.md
```

### 1. `analizar.py` — Modo lectura

Genera un informe completo de la carpeta sin modificar nada:

- Total de archivos y tamaño
- Distribución por tipo de extensión
- **Duplicados reales** detectados por hash MD5 (mismo contenido aunque tengan distinto nombre)
- Archivos basura (`.DS_Store`, `.crdownload`, `.tmp`...)
- Archivos grandes (>100 MB)
- Archivos antiguos (sin tocar >6 meses)

### 2. `organizar_v2.py` — Organizador inteligente

Organiza la carpeta separando duplicados, basura y archivos antiguos en carpetas de revisión:

- **Modo `DRY_RUN`** — previsualiza qué se movería sin tocar nada
- Detecta duplicados por hash y conserva el más antiguo como original
- Separa basura y archivos antiguos para que el usuario decida qué borrar
- Categoriza el resto por tipo (Documentos, Vídeos, Imágenes, etc.)
- Maneja extensiones compuestas como `.tar.gz`
- Evita sobrescritura añadiendo `(1)`, `(2)` si ya existe el archivo

### 3. `organizador.py` — Organizador básico

Versión inicial más sencilla. Solo categoriza por tipo de archivo, sin detección de duplicados ni separación de basura.

---

## 🚀 Uso

### Requisitos

- macOS (probado en Apple Silicon)
- Python 3.8+ (sin dependencias externas — solo librería estándar)

```bash
python3 --version
```

### Flujo recomendado

**Paso 1 — Analizar el estado actual:**

```bash
python3 analizar.py
```

Esto **no modifica nada**. Solo imprime un informe en terminal.

**Paso 2 — Simular la organización:**

```bash
python3 organizar_v2.py
```

Por defecto se ejecuta con `DRY_RUN = True`, que muestra qué movería sin hacerlo de verdad.

**Paso 3 — Ejecutar de verdad:**

Edita `organizar_v2.py` y cambia:

```python
DRY_RUN = False
```

Vuelve a ejecutar:

```bash
python3 organizar_v2.py
```

**Paso 4 — Revisar y limpiar manualmente:**

Tras la ejecución, revisa estas carpetas en `~/Downloads/` y borra lo que no necesites:

- `_BASURA_REVISAR/` — descargas rotas y archivos del sistema
- `_DUPLICADOS_REVISAR/` — copias (el original sigue en su categoría)
- `_ANTIGUOS_REVISAR/` — archivos sin tocar en más de 6 meses

Las carpetas empiezan con `_` para que aparezcan al principio en Finder.

---

## 🗂️ Estructura resultante

Después de ejecutar `organizar_v2.py`, la carpeta queda así:

```
~/Downloads/
├── _BASURA_REVISAR/
├── _DUPLICADOS_REVISAR/
├── _ANTIGUOS_REVISAR/
├── Documentos/         # .pdf, .docx, .xlsx, .pptx, .txt, .csv...
├── Imagenes/           # .jpg, .png, .gif, .svg, .webp, .heic...
├── Videos/             # .mp4, .mov, .avi, .mkv, .webm
├── Musica/             # .mp3, .wav, .flac, .m4a, .aac
├── Instaladores/       # .dmg, .pkg, .exe, .msi
├── Comprimidos/        # .zip, .rar, .7z, .tar, .tar.gz, .gz, .bz2
├── Codigo/             # .py, .js, .ts, .html, .css, .json, .java, .sql, .sh, .jar
└── Otros/              # cualquier otra extensión
```

---

## ⚙️ Configuración

Las constantes principales se editan en cabecera de cada script:

```python
DOWNLOADS = os.path.expanduser("~/Downloads")  # Carpeta a organizar
DRY_RUN = True                                  # Modo simulación
DAYS_OLD = 180                                  # Umbral de "antiguo" en días
```

Para usarlo en otra carpeta (por ejemplo el Escritorio):

```python
DOWNLOADS = os.path.expanduser("~/Desktop")
```

---

## 🛡️ Seguridad

El proyecto está diseñado priorizando **no perder archivos**:

| Mecanismo | Para qué sirve |
|-----------|---------------|
| `analizar.py` | Inspección sin modificar |
| `DRY_RUN` | Previsualizar antes de ejecutar |
| Hash MD5 | Detección de duplicados por contenido real |
| Conservar el más antiguo | El original nunca se mueve a `_DUPLICADOS_REVISAR` |
| Renombrado automático | Si ya existe el archivo, añade `(1)`, `(2)`... en vez de sobrescribir |
| Carpetas `_REVISAR` | El script nunca borra: el usuario decide |

---

## 🐛 Problemas comunes

**`xcode-select: Failed to locate 'python'`**

En macOS no existe el comando `python`, solo `python3`. Usa siempre:

```bash
python3 organizar_v2.py
```

**El script tarda mucho**

El cálculo de hashes para detectar duplicados se salta archivos mayores de 500 MB para no eternizarse. Si tienes muchos vídeos grandes, es normal que tarde unos segundos.

**No detecta `.tar.gz` como comprimido**

Está cubierto: la función `get_extension()` reconoce extensiones compuestas.

---

## 📝 Notas

Proyecto personal de aprendizaje en Python — formación DAW.

Sin licencia explícita: uso personal y educativo.
