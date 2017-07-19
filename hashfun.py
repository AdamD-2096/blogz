import hashlib
import random
import string

def make_salt():
    return ''.join([random.choice(string.hexdigits) for x in range(6)])

def make_pepper():
    return ''.join([random.choice(string.ascii_letters) for x in range(3)])

def make_pw_hash(password, salt=None, pepper=None):
    if not salt:
        salt = str(make_salt())
    if not pepper:
        pepper = str(make_pepper())
    pwhash = str(hashlib.sha256(str.encode(salt + str(password) + pepper)).hexdigest())
    return '{0}|{1}|{2}'.format(pwhash, salt, pepper)

def check_pw_hash(password, pwhash):
    salt = pwhash.split('|')[1]
    pepper = pwhash.split('|')[2]
    if make_pw_hash(password, salt, pepper) == pwhash:
        return True
    return False