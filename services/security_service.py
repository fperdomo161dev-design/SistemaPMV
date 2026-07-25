import hashlib

def hash_password(password: str) -> str:
    """Convierte la contraseña ingresada en un hash SHA-256 no reversible."""
    if not password:
        return ""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara la contraseña en texto plano ingresada en el Login 
    con el hash guardado en la base de datos."""
    return hash_password(plain_password) == hashed_password