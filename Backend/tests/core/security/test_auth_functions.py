from Backend.core.security.auth import (
    create_access_token,
    get_password_hash,
    get_secret_key,
    verify_password,
)


def test_get_secret_key():
    secret_key1 = get_secret_key()
    secret_key2 = get_secret_key()

    assert secret_key1 == secret_key2
    assert isinstance(secret_key1, str)


def test_verify_password_hash():
    hashed_pw = get_password_hash("secret")
    assert isinstance(hashed_pw, str)

    result = verify_password("secret", hashed_pw)
    assert result

    result = verify_password("also_secret", hashed_pw)
    assert not result


def test_create_access_token():
    data1 = {"sub": "Tester"}
    token1 = create_access_token(data1)

    data2 = {"sub": "Tester2"}
    token2 = create_access_token(data2)

    assert not (token1 == token2)
