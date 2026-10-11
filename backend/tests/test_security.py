from app.internal.security import hash_password, verify_password


def test_hash_is_not_plain_text():
    hashed = hash_password('secret')
    assert hashed != 'secret'
    assert hashed.startswith('$argon2id$')


def test_verify_password():
    hashed = hash_password('secret')
    assert verify_password('secret', hashed)
    assert not verify_password('wrong', hashed)


def test_same_password_produces_different_hashes():
    assert hash_password('secret') != hash_password('secret')
