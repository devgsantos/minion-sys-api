import hmac

from werkzeug.security import check_password_hash, generate_password_hash


HASH_PREFIXES = ('scrypt:', 'pbkdf2:')


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(stored_password: str, provided_password: str) -> tuple[bool, bool]:
    if stored_password.startswith(HASH_PREFIXES):
        return check_password_hash(stored_password, provided_password), False

    is_valid = hmac.compare_digest(stored_password, provided_password)
    return is_valid, is_valid
