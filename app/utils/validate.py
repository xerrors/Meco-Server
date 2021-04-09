import hashlib

from app.config import SERVER_TOKEN, ADMIN_NAME


def validate_server_token(username, password):
    client_md5 = hashlib.md5(password.encode('utf-8')).hexdigest()
    server_md5 = hashlib.md5(SERVER_TOKEN.encode('utf-8')).hexdigest()
    return username == ADMIN_NAME and client_md5 == server_md5