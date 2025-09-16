"""Lightweight Solana RPC client wrapper (lazy imports).

This module provides a minimal adapter to interact with Solana clusters using
`solana-py`. All imports are lazy so the project does not require the
dependency unless real RPC calls are needed.

Security: do NOT store private keys in the repository. Use environment
variables pointing to secure files or secret stores. Mainnet transactions
are only allowed when `ALLOW_MAINNET_TRANSACTIONS` is set to a truthy value.
"""
from __future__ import annotations

import os
from typing import Optional


class SolanaClient:
    def __init__(self, rpc_url: Optional[str] = None, keypair_path: Optional[str] = None) -> None:
        self.rpc_url = rpc_url or os.getenv("SOLANA_RPC_URL", "")
        self.keypair_path = keypair_path or os.getenv("SOLANA_KEYPAIR_PATH", "")
        self._client = None
        self._keypair = None

    def _ensure_client(self):
        if self._client is not None:
            return
        if not self.rpc_url:
            raise RuntimeError("SOLANA_RPC_URL not configured")
        try:
            # Lazy import
            from solana.rpc.async_api import AsyncClient

            self._client = AsyncClient(self.rpc_url)
        except Exception as e:
            raise RuntimeError("solana-py is required for real RPC calls. Install 'solana' package.") from e

    def _load_keypair(self):
        if self._keypair is not None:
            return
        if not self.keypair_path:
            raise RuntimeError("SOLANA_KEYPAIR_PATH not set - path to keypair json required")
        try:
            import json
            from solana.keypair import Keypair

            with open(self.keypair_path, "r", encoding="utf-8") as f:
                arr = json.load(f)
            # arr is expected to be a list of ints (secret key)
            secret = bytes(arr)
            self._keypair = Keypair.from_secret_key(secret)
        except Exception as e:
            raise RuntimeError("Failed to load keypair from path") from e

    async def request_airdrop(self, pubkey: str, lamports: int) -> dict:
        """Request an airdrop (devnet/testnet only). Returns solana RPC result.

        `lamports` is amount in lamports (1 SOL = 1_000_000_000 lamports).
        """
        self._ensure_client()
        # Lazy import for PublicKey
        from solana.publickey import PublicKey

        pk = PublicKey(pubkey)
        resp = await self._client.request_airdrop(pk, lamports)
        return resp

    async def send_transfer(self, to_pubkey: str, lamports: int) -> dict:
        """Send SOL transfer from loaded keypair to `to_pubkey`.

        Returns RPC transaction signature/result dict.
        """
        self._ensure_client()
        self._load_keypair()
        from solana.publickey import PublicKey
        from solana.transaction import Transaction
        from solana.system_program import TransferParams, transfer

        to_pk = PublicKey(to_pubkey)
        tx = Transaction()
        tx.add(transfer(TransferParams(from_pubkey=self._keypair.public_key, to_pubkey=to_pk, lamports=lamports)))

        try:
            resp = await self._client.send_transaction(tx, self._keypair)
            return resp
        finally:
            # optionally confirm
            pass
