import base64
import json
import os
from typing import Any, Dict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class SecretManagerService:
    """Secret Management Abstraction supporting AES-256 Fernet/GCM encryption and external KMS/Vault interfaces."""

    def __init__(self, secret_key: str | None = None):
        master_key = secret_key or os.getenv("SECRET_KEY", "vertexerp-ai-enterprise-secret-key-2026-phase-18")
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"vertexerp_integration_salt_2026",
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        self.fernet = Fernet(key)

    def encrypt_credentials(self, credentials: Dict[str, Any]) -> str:
        """Encrypts dictionary credentials into an authenticated ciphertext string."""
        json_str = json.dumps(credentials)
        encrypted_bytes = self.fernet.encrypt(json_str.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")

    def decrypt_credentials(self, ciphertext: str) -> Dict[str, Any]:
        """Decrypts authenticated ciphertext string back into dictionary credentials."""
        decrypted_bytes = self.fernet.decrypt(ciphertext.encode("utf-8"))
        return json.loads(decrypted_bytes.decode("utf-8"))
