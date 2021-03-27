import base64

import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5

from login.NCLogin import NCLogin

session = requests.session()


class NCPasswordLogin(NCLogin):
    rsa_public_key = """-----BEGIN PUBLIC KEY-----
    MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCsAiBmrht+wJFrQSMlMjppAYniUSvyek62PDJg
    g/+dWoODaPEkaGTXpGmSuRyn3RC2xWLPKZIxvYc9Pk+/QDnmsNxaY/3T3btZmgJsKPw4F7YCfRY/
    fKk/lahvumwnohr8cFY9lVgAz80caWcP9SZijQ9MaXgW3GkMkuWyhcoJpwIDAQAB
    -----END PUBLIC KEY-----"""

    def __init__(self, account, pwd):
        self.account = account
        self.pwd = pwd
        self.cipher_text = base64.b64encode(
            Cipher_pkcs1_v1_5.new(RSA.importKey(self.rsa_public_key)).encrypt(bytes(self.pwd, encoding="utf8")))

    def do(self, session=None) -> requests.Session:
        if not session:
            session = requests.session()

        session.get("https://www.nowcoder.com/login")
        session.post(url="https://www.nowcoder.com/nccommon/login/do?token=", data={
            "email": self.account,
            "remember": "true",
            "cipherPwd": self.cipher_text
        })

        return session

