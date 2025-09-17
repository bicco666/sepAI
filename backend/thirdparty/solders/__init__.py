# backend/thirdparty/solders/__init__.py

class PublicKey(str):
    pass

class Keypair:
    def __init__(self):
        self._pk = PublicKey("MockPublicKey")
    @classmethod
    def generate(cls):
        return cls()
    @property
    def pubkey(self):
        return self._pk

LAMPORTS_PER_SOL = 1_000_000_000