# Import from python standard library
import hashlib
import base64

# Import the local ECDSA and bech32 modules
from lib import secp256k1


def create_tx_message():
    msg = ""
    # version:
    msg += "01000000"
    # number of inputs:
    msg += "01"
    # hash of tx being spent by input #0:
    msg += "c997a5e56e104102fa209c6a852dd90660a20b2d9c352423edce25857fcd3704"
    # index of output of tx being spent by input #0:
    msg += "00000000"
    # scriptPubKey of output being spent by input #0:
    msg += "43410411db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6"
    msg += "909a5cb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f999b8643f656"
    msg += "b412a3ac"
    # input #0 sequence:
    msg += "ffffffff"
    # number of outputs:
    msg += "02"
    # output #0 value (10 BTC or 1,000,000,000 satoshis):
    msg += "00ca9a3b00000000"
    # output #0 scriptPubKey (Hal Finney's public key plus OP_CHECKSIG):
    msg += "434104ae1a62fe09c5f51b13905f07f06b99a2f7159b2225f374cd378d71302f"
    msg += "a28414e7aab37397f554a7df5f142c21c1b7303b8a0626f1baded5c72a704f7e"
    msg += "6cd84cac"
    # outut #1 value (40 BTC or 4,000,000,000 satoshis):
    msg += "00286bee00000000"
    # output #1 scriptPubKey (Satoshi's oen public key again, for change):
    msg += "43410411db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6"
    msg += "909a5cb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f999b8643f656"
    msg += "b412a3ac"
    # locktime:
    msg += "00000000"
    # SIGHASH type
    msg += "01000000"
    return msg


def msg_to_integer(msg):
    # Double-SHA256 the tx data
    single_hash = hashlib.new('sha256', bytes.fromhex(msg)).digest()
    double_hash = hashlib.new('sha256', single_hash).digest()
    # Convert the hash to a 32-byte integer
    return int.from_bytes(double_hash)


def verify(sig_r, sig_s, pubkey_x, pubkey_y, msg):
    key = secp256k1.GE(pubkey_x, pubkey_y)
    if sig_r == 0 or sig_r >= secp256k1.GE.ORDER:
        print("FALSE - invalid r value")
    if sig_s == 0 or sig_s >= secp256k1.GE.ORDER:
        print("FALSE - invalid s value")
    sig_s_inverted = pow(sig_s, -1, secp256k1.GE.ORDER)
    u1 = (msg * sig_s_inverted) % secp256k1.GE.ORDER
    u2 = (sig_r * sig_s_inverted) % secp256k1.GE.ORDER
    R = (u1 * secp256k1.G) + (u2 * key)
    return sig_r == int(R.x)


def encode_message(text):
    prefix = b"Bitcoin Signed Message:\n"
    vector = bytes([len(prefix)]) + prefix + bytes([len(text)]) + text
    return vector.hex()


def decode_sig(base64_sig):
    # decode base64 into raw bytes
    vp_sig_bytes = base64.b64decode(base64_sig)
    # throw away first byte for now, remaining bytes are r and s
    vp_sig_r = int.from_bytes(vp_sig_bytes[1:33])
    vp_sig_s = int.from_bytes(vp_sig_bytes[33:])
    return (vp_sig_r, vp_sig_s)


if __name__ == '__main__':
    # Public key values from step 7:
    pubkey_x = 0x11db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6909a5c
    pubkey_y = 0xb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f999b8643f656b412a3

    def verify_satoshi():
        # From step 5:
        msg_hex = create_tx_message()
        msg = msg_to_integer(msg_hex)
        # From step 6:
        sig_r = 0x4e45e16932b8af514961a1d3a1a25fdf3f4f7732e9d624c6c61548ab5fb8cd41
        sig_s = 0x181522ec8eca07de4860a4acdd12909d831cc56cbbac4622082221a8768d1d09
        # Satoshi's signature
        print(f"Satoshi: {verify(sig_r, sig_s, pubkey_x, pubkey_y, msg)}")

    def verify_vp():
        # Provided by Vanderpoole
        text =  b"I am Vanderpoole and I have control of the private key Satoshi\n"
        text += b"used to sign the first-ever Bitcoin transaction confirmed in block #170.\n"
        text += b"This message is signed with the same private key."
        sig = "H4vQbVD0pLK7pkzPto8BHourzsBrHMB3Qf5oYVmr741pPwdU2m6FaZZmxh4ScHxFoDelFC9qG0PnAUl5qMFth8k="

        msg_hex = encode_message(text)
        msg = msg_to_integer(msg_hex)

        (sig_r, sig_s) = decode_sig(sig)
        # Vanderpoole's signature
        print(f"Vanderpoole: {verify(sig_r, sig_s, pubkey_x, pubkey_y, msg)}")

        # Vanderpoole's actual key
        vp_pubkey_x = 0x9d57ded01d3a7652a957cf86fd4c3d2a76e76e83d3c965e1dca45f1ee0663063
        vp_pubkey_y = 0x6b8bcbc3df3fbc9669efa2ccd5d7fa5a89fe1c0045684189f01ea915b8a746a6
        print(f"Vanderpoole actual: {verify(sig_r, sig_s, vp_pubkey_x, vp_pubkey_y, msg)}")

    verify_satoshi()
    verify_vp()
