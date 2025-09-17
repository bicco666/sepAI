import os
import shutil
import zipfile
import datetime
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]  # Projektwurzel
BACKUP_DIR = BASE_DIR / "backups"
CHANGELOG = BASE_DIR / "CHANGELOG.md"


def backup_project():
    """Legt ein Backup der aktuellen Projektstruktur an."""
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"sepAI_backup_{timestamp}.zip"
    shutil.make_archive(str(backup_path).replace(".zip", ""), "zip", BASE_DIR)
    return backup_path


def apply_update(zip_path: Path, version: str = None):
    """Entpackt ein Update-ZIP ins Projektverzeichnis und schreibt CHANGELOG."""
    if not zip_path.exists():
        raise FileNotFoundError(f"{zip_path} nicht gefunden.")

    # Backup machen
    backup_path = backup_project()
    print(f"Backup erstellt: {backup_path}")

    # ZIP entpacken
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(BASE_DIR)
    print(f"Update {zip_path} entpackt nach {BASE_DIR}")

    # CHANGELOG aktualisieren
    with open(CHANGELOG, "a", encoding="utf-8") as f:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"\n[{ts}] Update applied from {zip_path.name}\n")
        if version:
            f.write(f"- Version bump: {version}\n")
    print("CHANGELOG.md aktualisiert.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update Handler für sepAI")
    parser.add_argument("zipfile", type=str, help="Pfad zum Update-ZIP")
    parser.add_argument("--version", type=str, help="Neue Version (z.B. v0.2.0)")
    args = parser.parse_args()

    apply_update(Path(args.zipfile), args.version)
