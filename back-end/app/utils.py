import secrets
import string

import bcrypt
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import SecretStr
import os

# 1. SMTP Configuration (Usually stored in .env)
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", "your_email@gmail.com"),
    MAIL_PASSWORD=SecretStr(os.getenv("MAIL_PASSWORD", "your_app_password")),
    MAIL_FROM="noreply@buet-ecouncil.ac.bd",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)


def hash_password(plain_password: str) -> str:
    """Hashes a plaintext password for storage."""
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks a plaintext password against a stored bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def generate_random_password(length: int = 12) -> str:
    """Generates a random password containing letters, digits, and punctuation."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


async def send_credentials_email(email_to: str, password: str):
    """Emails a newly created account's login credentials."""
    message = MessageSchema(
        subject="Your BUET e-Council Account",
        recipients=[email_to],  # type: ignore
        body=(
            "An account has been created for you on BUET e-Council.\n\n"
            f"Email: {email_to}\n"
            f"Password: {password}\n\n"
            "Please keep this password safe. You can change it after logging in."
        ),
        subtype=MessageType.plain,
    )
    fm = FastMail(conf)
    await fm.send_message(message)


def extract_plain_text(lexical_json: dict) -> str:
    """Helper to pull plain text out of the Lexical JSON structure"""
    try:
        # Navigates: root -> children (paragraphs) -> children (text nodes)
        nodes = lexical_json.get("root", {}).get("children", [])
        text_parts = []
        for p in nodes:
            for node in p.get("children", []):
                text_parts.append(node.get("text", ""))
        return "".join(text_parts).strip()
    except Exception:
        return "Untitled Meeting"
