import random

def easy_pass(s):
    hash = random.sample('1234567890qwertyuiopasdfghjklzxcvbnm', s)
    return ''.join(hash)

def medium_pass(s):
    hash = random.sample('1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM', s)
    return ''.join(hash)


def hard_pass(s):
    hash = random.sample('1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM!?-_@#$%&<>', s)
    return ''.join(hash)
