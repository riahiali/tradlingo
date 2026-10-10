from pathlib import Path

import pytest

import auth


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "users.db"


def test_hash_password_and_verify_round_trip():
    hashed = auth.hash_password("MotDePasseSecurise123!")
    assert hashed != "MotDePasseSecurise123!"
    assert auth.verify_password("MotDePasseSecurise123!", hashed)
    assert not auth.verify_password("motdepasse", hashed)


def test_create_user_and_authenticate(db_path: Path):
    user_id = auth.create_user("alice", "MotDePasseSecurise123!", db_path=db_path)
    assert user_id > 0
    assert auth.authenticate_user("alice", "MotDePasseSecurise123!", db_path=db_path)
    assert not auth.authenticate_user("alice", "wrong-password", db_path=db_path)


def test_duplicate_username_is_rejected(db_path: Path):
    auth.create_user("alice", "MotDePasseSecurise123!", db_path=db_path)

    with pytest.raises(ValueError, match="existe déjà"):
        auth.create_user("alice", "AutreMotDePasse123!", db_path=db_path)
