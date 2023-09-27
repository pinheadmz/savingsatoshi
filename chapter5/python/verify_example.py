import base64
import hashlib
from lib.secp256k1 import GE, G

def verify(r, s, P, msg):
  # ECDSA VERIFY!
  # https://www.secg.org/sec1-v2.pdf (Page 46, Section 4.1.4)
  if r == 0 or r >= GE.ORDER:
    print("FALSE - invalid r value")

  if s == 0 or s >= GE.ORDER:
    print("FALSE - invalid s value")

  sig_s_inverted = pow(s, -1, GE.ORDER)
  u1 = (msg * sig_s_inverted) % GE.ORDER
  u2 = (r * sig_s_inverted) % GE.ORDER
  R = (u1 * G) + (u2 * P)

  if r == int(R.x):
    print("TRUE - valid signature")
  else:
    print("FALSE - invalid signature")

# Serialized tx data
data = """0100000001c997a5e56e104102fa209c6a852dd90660a20b2d9c352423edce25
          857fcd37040000000043410411db93e1dcdb8a016b49840f8c53bc1eb68a382e
          97b1482ecad7b148a6909a5cb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9
          d4c03f999b8643f656b412a3acffffffff0200ca9a3b00000000434104ae1a62
          fe09c5f51b13905f07f06b99a2f7159b2225f374cd378d71302fa28414e7aab3
          7397f554a7df5f142c21c1b7303b8a0626f1baded5c72a704f7e6cd84cac0028
          6bee0000000043410411db93e1dcdb8a016b49840f8c53bc1eb68a382e97b148
          2ecad7b148a6909a5cb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f
          999b8643f656b412a3ac0000000001000000"""

# Double-SHA256 the tx data
single_hash = hashlib.new('sha256', bytes.fromhex(data)).digest()
double_hash = hashlib.new('sha256', single_hash).digest()

# Convert the hash to a 32-byte integer
msg = int.from_bytes(double_hash)

# Satoshi's signature, from the input scriptSig of the tx to Hal Finney
sig_der = """304402204e45e16932b8af514961a1d3a1a25fdf3f4f7732e9d624c6c61548ab
             5fb8cd410220181522ec8eca07de4860a4acdd12909d831cc56cbbac4622082
             221a8768d1d09"""

# Extract the two 32-byte values (r, s) from the DER-encoded signature
sig_r = 0x4e45e16932b8af514961a1d3a1a25fdf3f4f7732e9d624c6c61548ab5fb8cd41
sig_s = 0x181522ec8eca07de4860a4acdd12909d831cc56cbbac4622082221a8768d1d09

# Satoshi's public key, from the block 9 coinbase output scriptPubKey
pubkey = """0411db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6909a
            5cb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f999b8643f656b412
            a3"""

# Extract the two 32-byte values (x, y) from the key and create a ECDSA point
key_ge = GE(0x11db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6909a5c,
            0xb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f999b8643f656b412a3)

print("\nVerifying Satoshi's transaction signature...")
verify(sig_r, sig_s, key_ge, msg)



# Vanderpoole's message
prefix = b"Bitcoin Signed Message:\n"
text =  b"I am Vanderpoole and I have control of the private key Satoshi\n"
text += b"used to sign the first-ever Bitcoin transaction confirmed in block #170.\n"
text += b"This message is signed with the same private key."

vector = bytes([len(prefix)]) + prefix + bytes([len(text)]) + text
vector_hash = hashlib.new('sha256', hashlib.new('sha256', vector).digest()).digest()
vp_msg = int.from_bytes(vector_hash)
print(hex(vp_msg))
# Vanderpoole's signature
vp_sig = "H4vQbVD0pLK7pkzPto8BHourzsBrHMB3Qf5oYVmr741pPwdU2m6FaZZmxh4ScHxFoDelFC9qG0PnAUl5qMFth8k="
# decode base64 into raw bytes
vp_sig_bytes = base64.b64decode(vp_sig)
vp_sig_bytes = bytes([4]) + vp_sig_bytes[1:]
# throw away first byte for now, remaining bytes are r and s
vp_sig_r = int.from_bytes(vp_sig_bytes[1:33])
vp_sig_s = int.from_bytes(vp_sig_bytes[33:])
print(hex(vp_sig_r), hex(vp_sig_s))
print("\nVerifying Vanderpoole's message signature...")
verify(vp_sig_r, vp_sig_s, key_ge, vp_msg)



# This is the actual key used to sign the message
# Address: mvG1WcMQV4cFq1aEN6uijg8FSCfcxtMEqS
vp_key_ge = GE(0x9d57ded01d3a7652a957cf86fd4c3d2a76e76e83d3c965e1dca45f1ee0663063,
               0x6b8bcbc3df3fbc9669efa2ccd5d7fa5a89fe1c0045684189f01ea915b8a746a6)

print("\nVerifying Vanderpoole's message signature with actual key...")
verify(vp_sig_r, vp_sig_s, vp_key_ge, vp_msg)
