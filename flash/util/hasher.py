import bcrypt
from .bytes import Bytes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes


class Hasher:
    @staticmethod
    def hash_sha_256(ctx: str):
        """
        hashes string using sha256 algorithm

        @returns hash
        """
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(Bytes.str_to_bytes(ctx))
        return Bytes.encode_bytes(digest.finalize()).decode('utf-8')

    @staticmethod
    def hash(ctx: str) -> str:
        """
        hashes ctx

        @returns hash
        """
        return bcrypt.hashpw(
            ctx.encode('utf-8'),
            bcrypt.gensalt(12)
        ).decode('utf-8')

    @staticmethod
    def validate(ctx: str, hash: str) -> bool:
        """
        validates a ctx against a hash

        @returns: match
        """
        return bcrypt.checkpw(ctx.encode('utf-8'), hash.encode('utf-8'))
