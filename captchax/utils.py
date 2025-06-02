import uuid


def generate_captcha_id():
    return str(uuid.uuid4())
