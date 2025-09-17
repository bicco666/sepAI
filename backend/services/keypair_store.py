from pathlib import Path
import json, os, base64, secrets

KEYS_DIR = Path(os.getenv("KEYS_DIR", "keys")); KEYS_DIR.mkdir(exist_ok=True, parents=True)
KEY_FILE = KEYS_DIR / "solana_keypair.json"

def _rand32():
    return secrets.token_bytes(32)

def generate_keypair_bytes():
    sk = _rand32(); pk = _rand32()
    return sk + pk  # 64 bytes mock

def save_keypair_file(path: Path = KEY_FILE):
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    raw = generate_keypair_bytes()
    payload = {"raw": base64.b64encode(raw).decode("ascii")}
    path.write_text(json.dumps(payload))
    return str(path)

def load_keypair_file(path: Path = KEY_FILE):
    if not path.exists():
        raise FileNotFoundError(str(path))
    data = json.loads(path.read_text())
    raw = base64.b64decode(data["raw"])
    return raw

def ensure_keypair(path: Path = KEY_FILE):
    if not path.exists():
        save_keypair_file(path)
    return load_keypair_file(path)
