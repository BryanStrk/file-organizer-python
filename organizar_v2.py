import os
import shutil
import hashlib
from collections import defaultdict
from datetime import datetime, timedelta

# ============ CONFIG ============
DOWNLOADS = os.path.expanduser("~/Downloads")
DRY_RUN = False   # ⚠️ Cambia a False cuando quieras ejecutar de verdad
DAYS_OLD = 180   # Considerar "antiguo" si no se ha tocado en X días
# ================================

# Carpetas especiales (empiezan con _ para que salgan arriba en Finder)
DUPES_FOLDER = "_DUPLICADOS_REVISAR"
JUNK_FOLDER = "_BASURA_REVISAR"
OLD_FOLDER = "_ANTIGUOS_REVISAR"

JUNK_EXTENSIONS = {".crdownload", ".part", ".tmp", ".download"}
JUNK_NAMES = {".DS_Store", ".localized"}

FILE_TYPES = {
    "Documentos": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".xls", ".pptx", ".ppt", ".csv", ".odt"],
    "Imagenes": [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".heic", ".bmp"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".webm"],
    "Musica": [".mp3", ".wav", ".flac", ".m4a", ".aac"],
    "Instaladores": [".dmg", ".pkg", ".exe", ".msi"],
    "Comprimidos": [".zip", ".rar", ".7z", ".tar", ".tar.gz", ".tgz", ".gz", ".bz2"],
    "Codigo": [".py", ".js", ".ts", ".html", ".css", ".json", ".java", ".sql", ".sh", ".jar"]
}

# Carpetas que el script crea — no procesarlas si ya existen
PROTECTED_FOLDERS = {DUPES_FOLDER, JUNK_FOLDER, OLD_FOLDER, "Otros"} | set(FILE_TYPES.keys())


def get_file_hash(filepath, chunk_size=8192):
    h = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(chunk_size):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def get_extension(filename):
    lower = filename.lower()
    if lower.endswith(".tar.gz"):
        return ".tar.gz"
    return os.path.splitext(lower)[1]


def get_category(filename):
    ext = get_extension(filename)
    for folder, exts in FILE_TYPES.items():
        if ext in exts:
            return folder
    return "Otros"


def get_unique_path(target_folder, filename):
    destination = os.path.join(target_folder, filename)
    if not os.path.exists(destination):
        return destination
    name, ext = os.path.splitext(filename)
    counter = 1
    while True:
        new_path = os.path.join(target_folder, f"{name} ({counter}){ext}")
        if not os.path.exists(new_path):
            return new_path
        counter += 1


def move_file(filepath, target_folder, reason):
    """Mueve un archivo (o lo simula si DRY_RUN)."""
    filename = os.path.basename(filepath)
    if DRY_RUN:
        print(f"   [SIMULADO] {filename}  →  {os.path.basename(target_folder)}/  ({reason})")
        return True
    os.makedirs(target_folder, exist_ok=True)
    destination = get_unique_path(target_folder, filename)
    try:
        shutil.move(filepath, destination)
        print(f"   ✓ {filename}  →  {os.path.basename(target_folder)}/")
        return True
    except Exception as e:
        print(f"   ✗ Error con {filename}: {e}")
        return False


def main():
    if not os.path.exists(DOWNLOADS):
        print("No existe la carpeta")
        return

    print(f"\n{'='*60}")
    print(f"{'🔍 MODO SIMULACIÓN (DRY_RUN)' if DRY_RUN else '⚡ EJECUCIÓN REAL'}")
    print(f"{'='*60}\n")

    # ===== PASO 1: Recolectar info de todos los archivos =====
    files_info = []  # [(filepath, size, mtime, ext, category)]
    six_months_ago = datetime.now() - timedelta(days=DAYS_OLD)

    for filename in os.listdir(DOWNLOADS):
        filepath = os.path.join(DOWNLOADS, filename)
        # Saltar carpetas (incluyendo las que el propio script crea)
        if os.path.isdir(filepath):
            continue
        size = os.path.getsize(filepath)
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        files_info.append((filepath, filename, size, mtime))

    # ===== PASO 2: Detectar duplicados por hash =====
    print("⏳ Calculando hashes para detectar duplicados...")
    hashes = defaultdict(list)
    for filepath, filename, size, mtime in files_info:
        if size < 500 * 1024 * 1024:  # solo <500MB
            h = get_file_hash(filepath)
            if h:
                hashes[h].append((filepath, filename, size, mtime))

    # Para cada grupo de duplicados: el más antiguo se queda, el resto a _DUPLICADOS_REVISAR
    duplicates_to_move = set()
    for h, group in hashes.items():
        if len(group) > 1:
            # Ordenar por mtime ascendente: el primero (más viejo) es el "original"
            group_sorted = sorted(group, key=lambda x: x[3])
            for filepath, _, _, _ in group_sorted[1:]:
                duplicates_to_move.add(filepath)

    # ===== PASO 3: Procesar cada archivo =====
    stats = defaultdict(int)
    print(f"\n📦 Procesando {len(files_info)} archivos...\n")

    for filepath, filename, size, mtime in files_info:
        ext = get_extension(filename)

        # Saltar el propio script
        if filename in {"organizar_v2.py", "analizar.py", "organizador.py"}:
            continue

        # PRIORIDAD 1: Basura
        if ext in JUNK_EXTENSIONS or filename in JUNK_NAMES or filename.startswith("."):
            target = os.path.join(DOWNLOADS, JUNK_FOLDER)
            if move_file(filepath, target, "basura"):
                stats["basura"] += 1
            continue

        # PRIORIDAD 2: Duplicado (no el original)
        if filepath in duplicates_to_move:
            target = os.path.join(DOWNLOADS, DUPES_FOLDER)
            if move_file(filepath, target, "duplicado"):
                stats["duplicados"] += 1
            continue

        # PRIORIDAD 3: Antiguo (>6 meses)
        if mtime < six_months_ago:
            target = os.path.join(DOWNLOADS, OLD_FOLDER)
            if move_file(filepath, target, "antiguo"):
                stats["antiguos"] += 1
            continue

        # PRIORIDAD 4: Categorizar por tipo
        category = get_category(filename)
        target = os.path.join(DOWNLOADS, category)
        if move_file(filepath, target, category):
            stats[category] += 1

    # ===== RESUMEN =====
    print(f"\n{'='*60}")
    print("📊 RESUMEN")
    print(f"{'='*60}")
    for key, count in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"   {key:25} {count:>4} archivos")

    if DRY_RUN:
        print(f"\n⚠️  Esto fue una SIMULACIÓN. Nada se movió.")
        print(f"   Si te convence, cambia DRY_RUN = False y vuelve a ejecutar.\n")
    else:
        print(f"\n✅ Listo. Revisa estas carpetas antes de borrar nada:")
        print(f"   ~/Downloads/{JUNK_FOLDER}/    (basura — probablemente borrable)")
        print(f"   ~/Downloads/{DUPES_FOLDER}/   (duplicados — copias del original)")
        print(f"   ~/Downloads/{OLD_FOLDER}/     (antiguos — revisa cuáles ya no necesitas)\n")


if __name__ == "__main__":
    main()