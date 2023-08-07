# Import from python standard library
import random
import hashlib

# Import the local ECDSA and bech32 modules
from lib import secp256k1, bech32

##
# Private key to public key
##

# Generate a private key
k = random.randrange(1, secp256k1.GE.ORDER)
print("Private key:", hex(k))

# Derive the public key by multiplying by generator point
P = k * secp256k1.G
print("Public key: x:", P.x)
print("            y:", P.y)

# NOTE: even though we use the * symbol here which implies multiplication,
# what's really happening is elliptic curve operations which are defined
# by a custom __rmul__() function. Python kindly redirects "*" to that function.
# This next block is just a demonstration to show the outputs are equal.
P2 = secp256k1.G.__rmul__(k)
print("Public key: x:", P2.x)
print("            y:", P2.y)

##
# Compressed public key
##

# Get header byte
is_y_even = int(P.y) & 1 == 0
header_byte = bytes([2]) if is_y_even else bytes([3])

# Get public key X coordinate as bytes
x_bytes = int(P.x).to_bytes(32, 'big')

# Get 33-byte compressed public key
compressed = header_byte + x_bytes
print("Compressed public key:", compressed.hex())

# NOTE: the last 3 steps are also implemented in a single library function
compressed2 = P.to_bytes_compressed()
print("Compressed public key:", compressed2.hex())

##
# Public key to pubkeyhash
##

# Get 20-byte hash
public_key_hash = hashlib.new('ripemd160', hashlib.new('sha256', compressed).digest()).digest()
print("Public key hash in hex: ", public_key_hash.hex())

##
# Pubkeyhash to address
##

# Convert 8-bit bytes to 5-bit integers (base32)
base32_ints = bech32.convertbits(public_key_hash, 8, 5)
print("Public key hash in 5-bit integers:", base32_ints)

# Prepend the witness version
base32_ints = [0] + base32_ints

# Create checksum for MAINNET ("bc1...")
checksum = bech32.bech32_create_checksum('bc', base32_ints, bech32.Encoding.BECH32)
print("Checksum in 5-bit integers:", checksum)

# Put it all together and encode in bech32 format with witness version 0
combined = base32_ints + checksum
address = 'bc1' + ''.join(bech32.CHARSET[d] for d in combined)
print("bech32 address:", address)

# NOTE: The last 4 steps are also implemented in a single library function
address2 = bech32.encode('bc', 0, public_key_hash)
print("bech32 address:", address2)

