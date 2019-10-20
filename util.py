import hashlib, binascii, os

# hash_password and verify_password functions courtesy of Vitosh Academy at https://www.vitoshacademy.com/hashing-passwords-in-python/
 
def hash_password(password):
    """Hash a password for storing."""

    # create salt with sha256hash of random bytes read from os.urandom
    # then extracts string representation of hashed salt as hexadecimal numbers
    # the salt will always be 64 characters long
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')

    # salt + password provided to pbkdf2_hmac (requires bytes as input)
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                salt, 100000)

    # convert the salted and hashed password into hexadecimal for storage
    pwdhash = binascii.hexlify(pwdhash)

    return (salt + pwdhash).decode('ascii')
 
def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""

    # pull the salt out of the stored password (it is always 64 characters long)
    salt = stored_password[:64]
    stored_password = stored_password[64:]

    # hash the provided password with the same salt
    pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                  provided_password.encode('utf-8'), 
                                  salt.encode('ascii'), 
                                  100000)

    # convert the salted and hash into hexadecimal and compare this hash to the stored_password
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password