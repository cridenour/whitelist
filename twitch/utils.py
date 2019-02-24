import random
import string


def generate_access_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))