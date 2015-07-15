import pyDes
from django.conf import settings

_crypter = pyDes.triple_des(settings.SECRET_KEY[:24], padmode=pyDes.PAD_PKCS5)

def triple_des_encrypt(data):
    return _crypter.encrypt(data)

def triple_des_decrypt(data):
    return _crypter.decrypt(data)
