from django.conf import settings
from email.header import Header
from email.utils import parseaddr
import smtplib

def get_smtp_server():
    if not settings.MAIL_FROM_EMAIL:
        raise Exception("No MAIL_FROM_EMAIL configured")

    if settings.MAIL_SMTP_SERVER is None:
        raise Exception("No SMTP server configured")

    smtp = smtplib.SMTP(
        settings.MAIL_SMTP_SERVER,
        settings.MAIL_SMTP_SERVER_PORT or 0
    )

    if settings.MAIL_SMTP_USE_TLS:
        smtp.starttls()

    if settings.MAIL_SMTP_SERVER_LOGIN and settings.MAIL_SMTP_SERVER_PASSWORD:
        smtp.login(
            settings.MAIL_SMTP_SERVER_LOGIN,
            settings.MAIL_SMTP_SERVER_PASSWORD
        )

    return smtp

def make_email_header(email, name=None):
    if name is None:
        (n, e) = parseaddr(email)
        name = n
        email = e
    if name is None or name == "":
        return Header(email).encode()
    return Header(name, "utf-8").encode() + " <" + email + ">"

def mimeencode_header(header_string):
    return Header(header_string, "utf-8").encode()
