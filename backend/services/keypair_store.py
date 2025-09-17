import json
from pathlib import Path
from typing import Tuple
from solders.keypair import Keypair  # ed25519

try:
    from eth_account import Account
    _HAVE_ETH_ACCOUNT = True
except ImportError:
    _HAVE_ETH_ACCOUNT = False

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
SOLANA_KEYFILE = KEYS_DIR / "solana_keypair.json"
ETHEREUM_KEYFILE = KEYS_DIR / "ethereum_keypair.json"

def get_or_create_solana_keypair() -> Tuple[str, str]:
    KEYS_DIR.mkdir(exist_ok=True)
    if SOLANA_KEYFILE.exists():
        data = json.loads(SOLANA_KEYFILE.read_text(encoding="utf-8"))
        return data["public_key"], data["private_key"]
    kp = Keypair()  # generates new
    secret_bytes = bytes(kp)  # 64 bytes (ed25519 secret + public)
    pub = str(kp.pubkey())    # base58
    prv = b58encode(secret_bytes)
    data = {"public_key": pub, "private_key": prv}
    SOLANA_KEYFILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return pub, prv

def get_or_create_ethereum_keypair() -> Tuple[str, str]:
    if not _HAVE_ETH_ACCOUNT:
        raise RuntimeError("eth_account not available")
    KEYS_DIR.mkdir(exist_ok=True)
    if ETHEREUM_KEYFILE.exists():
        data = json.loads(ETHEREUM_KEYFILE.read_text(encoding="utf-8"))
        return data["public_key"], data["private_key"]
    acct = Account.create()  # generates new
    pub = acct.address
    prv = acct.key.hex()
    data = {"public_key": pub, "private_key": prv}
    ETHEREUM_KEYFILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return pub, prv

# Backward compatibility
def get_or_create_keypair() -> Tuple[str, str]:
    return get_or_create_solana_keypair()
