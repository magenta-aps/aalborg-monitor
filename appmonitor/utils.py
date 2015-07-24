from django.conf import settings
from email.header import Header
from email.utils import parseaddr
import smtplib, md5, pyDes

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

# Implementation of windows CryptoAPI DeriveKey using MD5 algoritm.
def derive_md5_key(key):
    hash_val = bytearray(md5.new(key).digest())
    buf1 = bytearray(b'\x36' * 64)
    buf2 = bytearray(b'\x5c' * 64)
    for x in range(len(hash_val)):
        buf1[x] ^= hash_val[x]
        buf2[x] ^= hash_val[x]
    hash1 = md5.new(bytes(buf1)).digest()
    hash2 = md5.new(bytes(buf2)).digest()
    derived_key = hash1 + hash2

    return derived_key[:24]

# Provide a TripleDES object that uses the projects SECRET_KEY as encryption
# key and encrypts/decrypts in the same ways as the windows CryptAPI used
# by AutoIT.
def make_tripleDES():
    return pyDes.triple_des(
        derive_md5_key(settings.SECRET_KEY),
        pyDes.CBC,
        IV="\0\0\0\0\0\0\0\0",
        padmode=pyDes.PAD_PKCS5
    )

def encrypt_and_hex(data):
    return make_tripleDES().encrypt(data).encode("hex")

def decrypt_from_hex(data):
    return make_tripleDES().decrypt(data.decode("hex"))