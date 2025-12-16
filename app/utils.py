# This file contains any utility functions
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

# Create a utility function to hash a password coming from the user.
def get_password_hash(password: str)-> str:
    return password_hash.hash(password)

# And another utility to verify if a received password matches the hash stored.
def verify_password(plain_password: str, hashed_password: str)-> bool:
    return password_hash.verify(plain_password, hashed_password)