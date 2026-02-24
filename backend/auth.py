from datetime import datetime, timedelta
import base64
import secrets
import hashlib
import hmac
import json

SECRET_KEY = "SUPER_SECRET_HACKATHON_KEY"
ALGORITHM = "HS256"

def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200000
    ).hex()
    return f"pbkdf2_sha256$200000${salt}${digest}"

def verify_password(plain, hashed):
    try:
        algo, rounds_str, salt, expected = hashed.split("$", 3)
        if algo != "pbkdf2_sha256":
            return False
        rounds = int(rounds_str)
        calc = hashlib.pbkdf2_hmac(
            "sha256",
            plain.encode("utf-8"),
            salt.encode("utf-8"),
            rounds
        ).hex()
        return hmac.compare_digest(calc, expected)
    except Exception:
        return False

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=2)
    to_encode.update({"exp": int(expire.timestamp())})
    payload = json.dumps(to_encode, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload).decode("utf-8").rstrip("=")
    sig = hmac.new(SECRET_KEY.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).decode("utf-8").rstrip("=")
    return f"{payload_b64}.{sig_b64}"


def decode_access_token(token: str):
    try:
        payload_b64, sig_b64 = token.split(".", 1)
        expected_sig = hmac.new(
            SECRET_KEY.encode("utf-8"),
            payload_b64.encode("utf-8"),
            hashlib.sha256
        ).digest()
        expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode("utf-8").rstrip("=")
        if not hmac.compare_digest(sig_b64, expected_sig_b64):
            return None

        padded = payload_b64 + "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8"))
        exp = payload.get("exp")
        if not isinstance(exp, int):
            return None
        if datetime.utcnow().timestamp() > exp:
            return None
        return payload
    except Exception:
        return None
