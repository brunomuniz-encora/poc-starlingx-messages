import random
import string
import socket
import numpy as np


def random_word(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def random_percentage_long_tail_distribution():
    return int((1 - np.random.power(10)) * 100)


def get_ip():
    return socket.gethostbyname(socket.gethostname())
