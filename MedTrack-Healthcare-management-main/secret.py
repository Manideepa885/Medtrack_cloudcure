import os
import binascii

# Generate a random secret key
secret_key = binascii.hexlify(os.urandom(24)).decode()
print(secret_key)
