import os
import shutil

# Carpeta a organizar (cámbiala si quieres otra: "~/Desktop", "~/Documents", etc.)
downloads_path = os.path.expanduser("~/Downloads")

file_types = {
    "Documentos": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".xls", ".pptx", ".ppt", ".csv", ".odt"],
    "Imagenes": [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".heic", ".bmp"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".webm"],
    "Musica": [".mp3", ".wav", ".flac", ".m4a", ".aac"],
    "Instaladores": [".dmg", ".pkg", ".exe", ".msi"],
    "Comprimidos": [".zip", ".rar", ".7z", ".tar", ".tar.gz", ".tgz", ".gz"],
    "Codigo": [".py", ".js", ".ts", ".html", ".css", ".json", ".java", ".sql", ".sh"]
}

def get_extension(filename):
    """Detecta extensiones compuestas como .tar.gz."""
    lower = filename.lower()
    if lower.endswith(".tar.gz"):
        return ".tar.gz"
    return os.path.splitext(lower)[1]

def get_unique_path(target_folder, filename):
    """Si ya existe el archivo, le añade (1), (2), etc."""
    destination = os.path.join(target_folder, filename)
    if not os.path.exists(destination):
        return destination

    name, ext = os.path.splitext(filename)
    counter = 1
    while True:
        new_name = f"{name} ({counter}){ext}"
        new_path = os.path.join(target_folder, new_name)
        if not os.path.exists(new_path):
            return new_path
        counter += 1

def organize_downloads():
    if not os.path.exists(downloads_path):
        print(f"No se encontró la carpeta: {downloads_path}")
        return

    moved = 0
    skipped = 0

    for filename in os.listdir(downloads_path):
        filepath = os.path.join(downloads_path, filename)

        # Saltar carpetas, el propio script y archivos ocultos del sistema
        if os.path.isdir(filepath):
            continue
        if filename == "organizador.py" or filename.startswith("."):
            skipped += 1
            continue

        extension = get_extension(filename)

        # Buscar categoría
        folder_assigned = "Otros"
        for folder, extensions in file_types.items():
            if extension in extensions:
                folder_assigned = folder
                break

        # Crear carpeta destino
        target_folder = os.path.join(downloads_path, folder_assigned)
        os.makedirs(target_folder, exist_ok=True)

        # Mover sin sobrescribir
        destination = get_unique_path(target_folder, filename)
        try:
            shutil.move(filepath, destination)
            print(f"✓ {filename} → {folder_assigned}/")
            moved += 1
        except Exception as e:
            print(f"✗ Error con {filename}: {e}")

    print(f"\n¡Listo! Movidos: {moved} | Ignorados: {skipped}")

if __name__ == "__main__":
    organize_downloads()