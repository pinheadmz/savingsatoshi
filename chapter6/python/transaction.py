import hashlib
import random
import struct
# Import the local ECDSA and bech32 modules
from lib import secp256k1, bech32

class Outpoint:
    def __init__(self, txid, index):
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
        r += struct.pack("<I", self.index)
        return r

class Input:
    def __init__(self):
        self.outpoint = None
        self.script = b""
        self.sequence = 0xffffffff
        self.value = 0
        self.scriptcode = b""

    @classmethod
    def from_output(cls, txid, vout, value, scriptcode):
        self = cls()
        self.outpoint = Outpoint(bytes.fromhex(txid)[::-1], vout)
        self.value = value
        self.scriptcode = bytes.fromhex(scriptcode)
        return self

    def serialize(self):
        r = b""
        r += self.outpoint.serialize()
        r += struct.pack("<B", len(self.script))
        r += struct.pack("<I", self.sequence)
        return r

class Output:
    def __init__(self):
        self.value = 0
        self.witness_version = 0
        self.witness_data = b""

    @classmethod
    def from_options(cls, addr, value):
        assert isinstance(value, int)
        self = cls()
        (ver, data) = bech32.decode("bc", addr)
        self.witness_version = ver
        self.witness_data = bytes(data)
        self.value = value
        return self

    def serialize(self):
        r = b""
        r += struct.pack("<q", self.value)
        r += struct.pack("<B", len(self.witness_data) + 2)
        r += struct.pack("<B", self.witness_version)
        r += struct.pack("<B", len(self.witness_data))
        r += self.witness_data
        return r

class Witness:
    def __init__(self):
        self.items = []

    def push_item(self, data):
        self.items.append(data)

    def serialize(self):
        r = b""
        r += struct.pack("<B", len(self.items))
        for item in self.items:
            r += struct.pack("<B", len(item))
            r += item
        return r

class Transaction:
    def __init__(self):
        self.version = 2
        self.flags = bytes.fromhex("0001")
        self.inputs = []
        self.outputs = []
        self.witnesses = []
        self.locktime = 0

    def serialize(self):
        r = b""
        r += struct.pack("<I", self.version)
        r += self.flags
        r += struct.pack("<B", len(self.inputs))
        for inp in self.inputs:
            r += inp.serialize()
        r += struct.pack("<B", len(self.outputs))
        for out in self.outputs:
            r += out.serialize()
        for wit in self.witnesses:
            r += wit.serialize()
        r += struct.pack("<I", self.locktime)
        return r

    def digest(self, input_index):
        def dsha256(data):
            return hashlib.new('sha256', hashlib.new('sha256', data).digest()).digest()

        sighash = 1

        s = b""
        s += struct.pack("<I", self.version)

        outpoints = b""
        for inp in self.inputs:
            outpoints += inp.outpoint.serialize()
        s += dsha256(outpoints)

        sequences = b""
        for inp in self.inputs:
            sequences += struct.pack("<I", inp.sequence)
        s += dsha256(sequences)

        s += self.inputs[input_index].outpoint.serialize()
        s += self.inputs[input_index].scriptcode
        s += struct.pack("<q", self.inputs[input_index].value)
        s += struct.pack("<I", self.inputs[input_index].sequence)

        outputs = b""
        for out in self.outputs:
            outputs += out.serialize()
        s += dsha256(outputs)

        s += struct.pack("<I", self.locktime)
        s += struct.pack("<I", sighash)
        return dsha256(s)

    def compute_input_signature(self, index, key):
        # k = random integer in [1, n-1]
        # R = G * k
        # r = x(R) mod n
        # s = (r * a + m) / k mod n
        # Extra Bitcoin rule from BIP 146
        # https://github.com/bitcoin/bips/blob/master/bip-0146.mediawiki#user-content-LOW_S
        #   s = -s mod n, if s > n / 2
        # return (r, s)
        assert isinstance(key, int)
        msg = self.digest(index)
        k = random.randrange(1, secp256k1.GE.ORDER)
        k_inverted = pow(k, -1, secp256k1.GE.ORDER)
        R = k * secp256k1.G
        r = int(R.x) % secp256k1.GE.ORDER
        s = ((r * key) + int.from_bytes(msg)) * k_inverted % secp256k1.GE.ORDER
        if s > secp256k1.GE.ORDER // 2:
            s = secp256k1.GE.ORDER - s
        return (r, s)

    def sign_input(self, index, priv, pub, sighash=1):
        def encode_der(r, s):
            # Represent in DER format. The byte representations of r and s have
            # length rounded up (255 bits becomes 32 bytes and 256 bits becomes 33 bytes).
            # See BIP 66
            # https://github.com/bitcoin/bips/blob/master/bip-0066.mediawiki
            rb = r.to_bytes((r.bit_length() + 8) // 8, 'big')
            sb = s.to_bytes((s.bit_length() + 8) // 8, 'big')
            return b'\x30' + bytes([4 + len(rb) + len(sb), 2, len(rb)]) + rb + bytes([2, len(sb)]) + sb
        (r, s) = self.compute_input_signature(0, priv)
        der_sig = encode_der(r, s)
        wit = Witness()
        wit.push_item(der_sig + bytes([sighash]))
        wit.push_item(pub)
        self.witnesses.append(wit)



if __name__ == "__main__":
    # From chapter 4 (we will reuse address for change)
    priv = 0x93485bbe0f0b2810937fc90e8145b2352b233fbd3dd7167525401dd30738503e
    compressed_pub = bytes.fromhex("038cd0455a2719bf72dc1414ef8f1675cd09dfd24442cb32ae6e8c8bbf18aaf5af")
    addr = "bc1qkg62ae0wwntkzhq8td87s87c4nj5zdlj2ga8j7"

    # UTXO from chapter 6 step 1 (mining pool payout)
    txid = "8a081631c920636ed71f9de5ca24cb9da316c2653f4dc87c9a1616451c53748e"
    vout = 1
    value = 650000000

    # User must compute this in step (TBA)
    scriptcode = "1976a914" + "b234aee5ee74d7615c075b4fe81fd8ace54137f2" + "88ac"

    # User's script for final step
    in0 = Input.from_output(txid, vout, value, scriptcode)
    out0 = Output.from_options("bc1qgghq08syehkym52ueu9nl5x8gth23vr8hurv9dyfcmhaqk4lrlgs28epwj", 100000000)
    out1 = Output.from_options(addr, 549999000)
    tx = Transaction()
    tx.inputs.append(in0)
    tx.outputs.append(out0)
    tx.outputs.append(out1)
    tx.sign_input(0, priv, compressed_pub)
    print(tx.serialize().hex())

    # The script output can be tested locally on regtest by sending 6.5 BTC
    # to the regtest version of the address (bcrt1qkg62ae0wwntkzhq8td87s87c4nj5zdljz8le7y)
    # and then entering the txid and vout of that funding TX into the script.
    # Then, `bitcoin-cli -regtest testmempoolaccept <hex>`
