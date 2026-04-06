import pyotp
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

def generate_otp_secret():
    """Generates a random secret for a user's OTP."""
    return pyotp.random_base32()

async def send_otp_email(email_to: str, otp_code: str):
    """Sends the 6-digit code to the user's email."""
    message = MessageSchema(
        subject="BUET e-Council Login Code",
        recipients=[email_to], # type: ignore
        body=f"Your secure login code is: {otp_code}. It expires in 5 minutes.",
        subtype=MessageType.plain
    )
    fm = FastMail(conf)
    await fm.send_message(message)

def verify_otp_code(secret: str, code: str):
    """Verifies the code using the user's secret."""
    totp = pyotp.TOTP(secret, interval=300) # Valid for 5 minutes
    return totp.verify(code)

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