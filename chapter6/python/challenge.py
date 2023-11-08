# !!! Every step should have the same imports, these are hints

# For computing double-SHA256
import hashlib
# For generating entropy used in ECDSA signing
from random import randrange
# For converting integers to series of bytes
from struct import pack
# Import the local ECDSA and bech32 modules
from lib import secp256k1, bech32


# !!! Step 2
#     Entire Outpoint class is given, this is also a hint

class Outpoint:
    def __init__(self, txid: bytes, index: int):
        assert isinstance(txid, bytes)
        assert len(txid) == 32
        assert isinstance(index, int)
        self.txid = txid
        self.index = index

    def serialize(self):
        # https:#docs.python.org/3/library/struct.html#byte-order-size-and-alignment
        # Encode the index as little-endian unsigned integer
        r = b""
        r += self.txid
        r += pack("<I", self.index)
        return r

class Input:
    def __init__(self):
        self.outpoint = None
        self.scriptsig = b""
        self.sequence = 0xffffffff
        self.value = 0
        self.scriptcode = b""

    @classmethod
    def from_output(cls, txid: str, vout: int, value: int, scriptcode: bytes):
        self = cls()
        # YOUR CODE HERE
        return self

    def serialize(self):
        # YOUR CODE HERE



# !!! Step 3

class Output:
    def __init__(self):
        self.value = 0
        self.witness_version = 0
        self.witness_data = b""

    @classmethod
    def from_options(cls, addr: str, value: int):
        assert isinstance(value, int)
        self = cls()
        # YOUR CODE HERE
        return self

    def serialize(self):
        # YOUR CODE HERE



# !!! Step 4

class Witness:
    def __init__(self):
        self.items = []

    def push_item(self, data: bytes):
        # YOUR CODE HERE

    def serialize(self):
        # YOUR CODE HERE



# !!! Step 5

class Transaction:
    def __init__(self):
        self.version = 2
        self.flags = bytes.fromhex("0001")
        self.inputs = []
        self.outputs = []
        self.witnesses = []
        self.locktime = 0

    def serialize(self):
        # YOUR CODE HERE

# !!! Step 6

    def digest(self, input_index: int):
        sighash = 1
        # YOUR CODE HERE

# !!! Step 7

    def compute_input_signature(self, index: int, key: int):
        # k = random integer in [1, n-1]
        # R = G * k
        # r = x(R) mod n
        # s = (r * a + m) / k mod n
        # Extra Bitcoin rule from BIP 146
        # https://github.com/bitcoin/bips/blob/master/bip-0146.mediawiki#user-content-LOW_S
        #   s = -s mod n, if s > n / 2
        # return (r, s)
        assert isinstance(key, int)
        # YOUR CODE HERE
        return (r, s)

# !!! Step 8
#     The encode_der() helper function is given
#     (Unless we wanna make this even harder...)

    def sign_input(self, index, priv, pub, sighash=1):
        def encode_der(r, s):
            # Represent in DER format. The byte representations of r and s have
            # length rounded up (255 bits becomes 32 bytes and 256 bits becomes 33 bytes).
            # See BIP 66
            # https://github.com/bitcoin/bips/blob/master/bip-0066.mediawiki
            rb = r.to_bytes((r.bit_length() + 8) // 8, 'big')
            sb = s.to_bytes((s.bit_length() + 8) // 8, 'big')
            return b'\x30' + bytes([4 + len(rb) + len(sb), 2, len(rb)]) + rb + bytes([2, len(sb)]) + sb
        # YOUR CODE HERE


# !!! Step 9

# !!! These constants can be given to the user
# From chapter 4 (we will reuse address for change)
priv = 0x93485bbe0f0b2810937fc90e8145b2352b233fbd3dd7167525401dd30738503e
compressed_pub = bytes.fromhex("038cd0455a2719bf72dc1414ef8f1675cd09dfd24442cb32ae6e8c8bbf18aaf5af")
pubkey_hash = "b234aee5ee74d7615c075b4fe81fd8ace54137f2"
addr = "bc1qkg62ae0wwntkzhq8td87s87c4nj5zdlj2ga8j7"

# UTXO from chapter 6 step 1 (mining pool payout)
txid = "8a081631c920636ed71f9de5ca24cb9da316c2653f4dc87c9a1616451c53748e"
vout = 1
value = 650000000

# Explained in step 6
scriptcode = "1976a914" + pubkey_hash + "88ac"

tx = Transaction()
# YOUR CODE HERE
print(tx.serialize().hex())
