import hashlib
import json
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

    @classmethod
    def from_json(cls, json_string):
        self = cls()
        utxo = json.loads(json_string)
        self.outpoint = Outpoint(bytes.fromhex(utxo["txid"]), utxo["vout"])
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
        for wit in self.witnessess:
            r += wit.serialize()
        r += struct.pack("<I", self.locktime)
        return r

    def digest(self, input_index, scriptcode, value, sighash=1):
        assert isinstance(scriptcode, bytes)
        assert isinstance(value, int)

        def dsha256(data):
            return hashlib.new('sha256', hashlib.new('sha256', data).digest()).digest()

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
        s += scriptcode
        s += struct.pack("<q", value)
        s += struct.pack("<I", self.inputs[input_index].sequence)
        outputs = b""
        for out in self.outputs:
            outputs += out.serialize()
        s += dsha256(outputs)
        s += struct.pack("<I", self.locktime)
        s += struct.pack("<I", sighash)
        return dsha256(s)

    def compute_input_signature(self, index, scriptcode, value, key):
        # k = random integer in [1,n-1]
        # R = G * k
        # r = x(R) mod n
        # s = (r * a + m) / k mod n
        # s = -s mod n, if s > n / 2
        # S = (r, s)
        assert isinstance(key, int)
        msg = self.digest(index, scriptcode, value)
        k = random.randrange(1, secp256k1.GE.ORDER)
        k_inverted = pow(k, -1, secp256k1.GE.ORDER)
        R = k * secp256k1.G
        r = int(R.x) % secp256k1.GE.ORDER
        s = ((r * key) + int.from_bytes(msg)) * k_inverted % secp256k1.GE.ORDER
        return (r, s)


if __name__ == "__main__":
    utxo = '''{
        "txid": "74149a689ce95562309cf4c404ef6ca91e76b6a19ef25e9625e9c13d93fac4e1",
        "vout": 0,
        "address": "bc1qm2dr49zrgf9wc74h5c58wlm3xrnujfuf5g80hs",
        "label": "",
        "scriptPubKey": "0014da9a3a9443424aec7ab7a628777f7130e7c92789",
        "amount": 6.50000000,
        "confirmations": 341,
        "spendable": true,
        "solvable": true,
        "desc": "wpkh([a73804d3/0'/0'/0']02ab3d3cb82c1eb89168824b20f667224d868250dedec69177012e5a26c5221ae8)#5mf00k95",
        "parent_descs": [
        ],
        "safe": true
    }'''
    in0 = Input.from_json(utxo)
    out0 = Output.from_options("bc1qgghq08syehkym52ueu9nl5x8gth23vr8hurv9dyfcmhaqk4lrlgs28epwj", 100000000)
    out1 = Output.from_options("bc1qm2dr49zrgf9wc74h5c58wlm3xrnujfuf5g80hs", 550000000)
