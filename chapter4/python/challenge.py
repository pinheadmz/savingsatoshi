# Import from python standard library
import hashlib
import random

# Import the local ECDSA and bech32 modules
from lib import secp256k1, bech32

def privatekey_to_address(private_key):
    publickey = privatekey_to_publickey(private_key)
    compressed = compress_publickey(publickey)
    pubkeyhash = hash_compressed(compressed)
    address = hash_to_address(pubkeyhash)
    return address


def privatekey_to_publickey(private_key):
    # Multiply the private key by the ECDSA generator point G to
    # produce a new curve point which is the public key.
    # Return that curve point (also known as a group element)
    # which will be an instance of secp256k1.GE
    G = secp256k1.G


def compress_publickey(publickey):
    # Determine if the y coordinate is even or odd and prepend the
    # corresponding header byte to the x coordinate.
    # Return 33-byte array
    header_byte = {
        "y_is_even": bytes([2]),
        "y_is_odd":  bytes([3])
    }


def hash_compressed(compressed):
    # Get the sha256 digest of the compressed public key,
    # then get the ripemd160 digest of that sha256 hash.
    # Return 32-byte array


def hash_to_address(pubkeyhash):
    # Encode the compressed public key hash with bech32
    # to create a witness version 0 address.
    # Returns string


if __name__ == '__main__':
    private_key = random.randrange(1, secp256k1.GE.ORDER)
    address = privatekey_to_address(private_key)
    print("Private key:", hex(private_key))
    print("Address:", address)
