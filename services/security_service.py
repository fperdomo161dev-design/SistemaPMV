import hashlib
import bcrypt


def hash_password(password: str) -> str:
    """Genera un hash seguro utilizando bcrypt con sal dinámica."""
    if not password:
        return ""

    bytes_password = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(bytes_password, salt)

    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara la contraseña ingresada con el hash de la BD.

    Soporta hashes bcrypt antiguos de SHA-256 y texto plano para evitar
    'Invalid salt'.
    """
    if not plain_password or not hashed_password:
        return False

    # 1. Verificar si es un hash valido de bcrypt (empieza por $2a$, $2b$ o $2y$)
    if hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            bytes_plain = plain_password.encode("utf-8")
            bytes_hashed = hashed_password.encode("utf-8")
            return bcrypt.checkpw(bytes_plain, bytes_hashed)
        except Exception as e:
            print(f"Error al verificar bcrypt: {e}")
            return False

    # 2. Si no es bcrypt, verificar si era un hash SHA-256 (compatibilidad previa)
    sha256_input = hashlib.sha256(
        plain_password.encode("utf-8")
    ).hexdigest()
    if sha256_input == hashed_password:
        return True

    # 3. Si era texto plano sin cifrar (ej. "1234")
    if plain_password == hashed_password:
        return True

    return False