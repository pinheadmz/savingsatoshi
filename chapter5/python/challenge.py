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
    # https://blockstream.info/tx/0437cd7f8525ceed2324359c2d0ba26006d92d856a9c20fa0241106ee5a597c9?output:0&expand
    # FILL THIS IN!
    msg +=
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
    # FILL THIS IN!
    msg +=
    return msg


def msg_to_integer(msg):
    # Given a hex string to sign, convert that string to bytes,
    # double-SHA256 the bytes and then return an integer from the 32-byte digest.



def verify(sig_r, sig_s, pubkey_x, pubkey_y, msg):
    # Verify an ECDSA signature given a public key and a message.
    # All input values will be 32-byte integers.
    # Start by creating a curve point representation of the public key
    key = secp256k1.GE(pubkey_x, pubkey_y)
    # Next, check the range limits of the signature values
    if sig_r == 0 or sig_r >= secp256k1.GE.ORDER:
        print("invalid r value")
        return False
    if sig_s == 0 or sig_s >= secp256k1.GE.ORDER:
        print("invalid s value")
        return False
    # Implement ECDSA and return a boolean
    #   u1 = m / s mod n
    #   u2 = r / s mod n
    #   R = G * u1 + A * u2
    #   r == x(R) mod n


def encode_message(text):
    # Given an ascii-encoded text message, serialize a byte array
    # with the Bitcoin protocol prefix string followed by the text
    # and both components preceded by a length byte.
    # Returns a hex string.
    prefix = b"Bitcoin Signed Message:\n"


def decode_sig(base64_sig):
    # Decode a base64-encoded signature string into its ECDSA
    # signature elements r and s, returned as a tuple of integers.
    # Remember to throw away the first byte of metadata from the signature string!


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
