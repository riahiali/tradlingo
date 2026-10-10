from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import sqlite3
from contextlib import contextmanager
from pathlib import Path


DB_PATH = Path(__file__).with_name("users.db")
PASSWORD_ALGORITHM = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 260_000
PASSWORD_SALT_BYTES = 16


def _normalize_username(username: str) -> str:
    normalized = (username or "").strip().lower()
    if not normalized:
        raise ValueError("Le nom d'utilisateur est obligatoire.")
    if len(normalized) < 3:
        raise ValueError("Le nom d'utilisateur doit contenir au moins 3 caractères.")
    return normalized


def _validate_password(password: str) -> str:
    value = password or ""
    if len(value) < 8:
        raise ValueError("Le mot de passe doit contenir au moins 8 caractères.")
    return value


@contextmanager
def _connect(db_path: Path = DB_PATH):
    connection = sqlite3.connect(db_path)
    try:
        yield connection
    finally:
        connection.close()


def init_db(db_path: Path = DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with _connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                hashed_password TEXT NOT NULL
            )
            """
        )
        connection.commit()


def hash_password(password: str, *, salt: bytes | None = None, iterations: int = PASSWORD_ITERATIONS) -> str:
    secret = _validate_password(password)
    salt_bytes = salt or secrets.token_bytes(PASSWORD_SALT_BYTES)
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        secret.encode("utf-8"),
        salt_bytes,
        iterations,
    )
    return "$".join(
        [
            PASSWORD_ALGORITHM,
            str(iterations),
            base64.b64encode(salt_bytes).decode("ascii"),
            base64.b64encode(derived_key).decode("ascii"),
        ]
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations_text, salt_text, hash_text = stored_hash.split("$", 3)
        if algorithm != PASSWORD_ALGORITHM:
            return False
        iterations = int(iterations_text)
        salt = base64.b64decode(salt_text.encode("ascii"))
        expected_hash = base64.b64decode(hash_text.encode("ascii"))
    except (ValueError, TypeError, base64.binascii.Error):
        return False

    candidate = hashlib.pbkdf2_hmac(
        "sha256",
        (password or "").encode("utf-8"),
        salt,
        iterations,
    )
    return hmac.compare_digest(candidate, expected_hash)


def create_user(username: str, password: str, db_path: Path = DB_PATH) -> int:
    normalized_username = _normalize_username(username)
    secret = _validate_password(password)
    init_db(db_path)
    hashed_password = hash_password(secret)

    try:
        with _connect(db_path) as connection:
            cursor = connection.execute(
                "INSERT INTO users (username, hashed_password) VALUES (?, ?)",
                (normalized_username, hashed_password),
            )
            connection.commit()
            return int(cursor.lastrowid)
    except sqlite3.IntegrityError as exc:
        raise ValueError("Ce nom d'utilisateur existe déjà.") from exc


def authenticate_user(username: str, password: str, db_path: Path = DB_PATH) -> bool:
    normalized_username = _normalize_username(username)
    init_db(db_path)

    with _connect(db_path) as connection:
        row = connection.execute(
            "SELECT hashed_password FROM users WHERE username = ?",
            (normalized_username,),
        ).fetchone()

    if row is None:
        return False
    return verify_password(password, row[0])
