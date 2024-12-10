import hashlib

text = "insert_shop"

hashed = hashlib.sha256(text.encode('utf-8')).hexdigest()

print(hashed)