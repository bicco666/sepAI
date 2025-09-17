import json
from pathlib import Path
from typing import Tuple
from solders.keypair import Keypair  # ed25519

# Local Base58 (Bitcoin alphabet)
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
KEYS_DIR.mkdir(exist_ok=True)
KEYFILE = KEYS_DIR / "solana_keypair.json"

def get_or_create_keypair() -> Tuple[str, str]:
    # Ensure directory exists even if KEYS_DIR/KEYFILE were monkeypatched
    try:
        KEYFILE.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        # Last-resort: attempt KEYS_DIR too
        try:
            KEYS_DIR.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    if KEYFILE.exists():
        data = json.loads(KEYFILE.read_text(encoding="utf-8"))
        return data["public_key"], data["private_key"]
    kp = Keypair()  # generates new
    secret_bytes = bytes(kp)  # 64 bytes
    pub = str(kp.pubkey())    # base58
    prv = b58encode(secret_bytes)
    data = {"public_key": pub, "private_key": prv}
    KEYFILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return pub, prv
