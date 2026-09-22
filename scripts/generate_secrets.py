"""Production Cryptographic Secrets Generator for VertexERP AI V2."""

import secrets
import string


def generate_alphanumeric_secret(length: int = 32) -> str:
    """Generates a secure password containing uppercase, lowercase, digits, and symbols."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    # Ensure at least one of each category
    password = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*()-_=+"),
    ]
    password += [secrets.choice(alphabet) for _ in range(length - 4)]
    secrets.SystemRandom().shuffle(password)
    return "".join(password)


def generate_production_secrets() -> dict[str, str]:
    """Generates a complete bundle of cryptographic tokens for production deployment."""
    return {
        "JWT_SECRET_KEY": secrets.token_urlsafe(48),
        "DATABASE_PASSWORD": generate_alphanumeric_secret(32),
        "REDIS_PASSWORD": generate_alphanumeric_secret(32),
        "STORAGE_SECRET_KEY": generate_alphanumeric_secret(32),
        "ENCRYPTION_MASTER_KEY": secrets.token_hex(32),
    }


def main() -> None:
    print("=" * 75)
    print(" VertexERP AI V2 - Production Cryptographic Secrets Generator")
    print("=" * 75)
    print(" Generated using Python `secrets` CSPRNG (SystemRandom / CryptGenRandom)")
    print("-" * 75)

    secrets_bundle = generate_production_secrets()
    for key, value in secrets_bundle.items():
        print(f"{key}={value}")

    print("-" * 75)
    print(" [!] CAUTION: Store these values in your secure secrets manager (AWS Secrets")
    print("     Manager, HashiCorp Vault, Kubernetes Secrets). Do NOT commit to git.")
    print("=" * 75)


if __name__ == "__main__":
    main()
