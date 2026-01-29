"""Utilitários para hash e verificação de senhas."""

import bcrypt


def hash_password(password: str) -> str:
    """Gera hash da senha usando bcrypt.

    Args:
        password: Senha em texto plano.

    Returns:
        Hash da senha.
    """
    # Converte a senha para bytes e gera o hash
    password_bytes = password.encode('utf-8')
    # Bcrypt tem limite de 72 bytes, então truncamos se necessário
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha corresponde ao hash.

    Args:
        plain_password: Senha em texto plano.
        hashed_password: Hash da senha armazenado.

    Returns:
        True se a senha corresponde, False caso contrário.
    """
    try:
        plain_bytes = plain_password.encode('utf-8')
        # Bcrypt tem limite de 72 bytes, então truncamos se necessário
        if len(plain_bytes) > 72:
            plain_bytes = plain_bytes[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception:
        return False
