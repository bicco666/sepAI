import json
from pathlib import Path
from typing import Tuple
from solders.keypair import Keypair  # ed25519

_ALPHABET = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
def b58encode(data: bytes) -> str:
    n_zeros = len(data) - len(data.lstrip(b"\0"))
    num = int.from_bytes(data, "big")
    enc = bytearray()
    while num > 0:
        num, rem = divmod(num, 58)
        enc.append(_ALPHABET[rem])
    enc.extend(b"1" * n_zeros)
    enc.reverse()
    return enc.decode("ascii")

BASE_DIR = Path(__file__).resolve().parents[2]
KEYS_DIR = BASE_DIR / "keys"
KEYFILE = KEYS_DIR / "solana_keypair.json"

def get_or_create_keypair() -> Tuple[str, str]:
    KEYS_DIR.mkdir(exist_ok=True)
    if KEYFILE.exists():
        data = json.loads(KEYFILE.read_text(encoding="utf-8"))
        return data["public_key"], data["private_key"]
    kp = Keypair()  # generates new
    secret_bytes = bytes(kp)  # 64 bytes (ed25519 secret + public)
    pub = str(kp.pubkey())    # base58
    prv = b58encode(secret_bytes)
    data = {"public_key": pub, "private_key": prv}
    KEYFILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return pub, prv
