import random


# All numbers and letters in the latin alphabet without lookalikes.
ALPHABET = "346789ABCDEFGHJKLMNPQRTUVWXYabcdefghijkmnpqrtwxyz"
DEFAULT_SIZE = 8


def generate_shortid(size=DEFAULT_SIZE):
    return "".join(random.choice(ALPHABET) for _ in range(size))
