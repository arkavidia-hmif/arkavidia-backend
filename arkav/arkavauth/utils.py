from string import ascii_letters
from string import digits
from django.utils.crypto import get_random_string


def generate_random_token(length=30):
    return get_random_string(length, allowed_chars=ascii_letters + digits)
