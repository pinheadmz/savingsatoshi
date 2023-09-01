# Chapter 5 challenge outline

1. Vanderpoole says he signed a message with Satoshi's keys:

```
-----BEGIN BITCOIN SIGNED MESSAGE-----

I am Vanderpoole and I have control of the private key Satoshi
used to sign the first-ever Bitcoin transaction confirmed in block #170.
The public key is:
0411db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6909a5cb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f999b8643f656b412a3

-----BEGIN BITCOIN SIGNATURE-----

IIXCUGj6YMEAIBlD5RCWJBTu6mKggy0LmtgPwATZIolecTE6JPrP0nEynAPDIPtLXZ1vWMUYBnRChCUXNT2nw3o=

-----END BITCOIN SIGNATURE----- 
```

What does this even mean?

Hal Finney claimed Satoshi sent him the block #170 transaction:
https://bitcointalk.org/index.php?topic=155054.0
Whoever sent that transaction mined block #9 so it seems very likely to have been Satoshi.

Block #9 generated 50 BTC to this public key
(this was in the days before hashed addresses or even compressed public keys were used!):
`0411db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6909a5cb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f999b8643f656b412a3`

That key can be seen in the `scriptPubKey` of ouput `0` in transaction `0437cd7f8525ceed2324359c2d0ba26006d92d856a9c20fa0241106ee5a597c9`,
which is the coinbase transaction of block 9. The complete output script there is just this public key followed by the opcode `OP_CHECKSIG`.

The output is spent (by Satoshi, probably) in transaction `f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16`
which was confirmed in block #170. That transaction obviously has a valid signature.

2. Verify Satoshi's signature from tx `f4184f...`

All the transaction details can be seen in [tx_f4184f.json](tx_f4184f.json).

We will summarize the process outlined in https://en.bitcoin.it/wiki/OP_CHECKSIG#How_it_works
which conviniently uses this exact transaction as an example: https://en.bitcoin.it/wiki/OP_CHECKSIG#Code_samples_and_raw_dumps

This is the raw transaction:
```
0100000001c997a5e56e104102fa209c6a852dd90660a20b2d9c352423edce25
857fcd3704000000004847304402204e45e16932b8af514961a1d3a1a25fdf3f
4f7732e9d624c6c61548ab5fb8cd410220181522ec8eca07de4860a4acdd1290
9d831cc56cbbac4622082221a8768d1d0901ffffffff0200ca9a3b0000000043
4104ae1a62fe09c5f51b13905f07f06b99a2f7159b2225f374cd378d71302fa2
8414e7aab37397f554a7df5f142c21c1b7303b8a0626f1baded5c72a704f7e6c
d84cac00286bee0000000043410411db93e1dcdb8a016b49840f8c53bc1eb68a
382e97b1482ecad7b148a6909a5cb2e0eaddfb84ccf9744464f82e160bfa9b8b
64f9d4c03f999b8643f656b412a3ac00000000
```

This is the raw transaction formatted for signing:
```
version:
 01000000
number of inputs:
 01
hash of tx being spent by input #0:
 c997a5e56e104102fa209c6a852dd90660a20b2d9c352423edce25857fcd3704
index of output of tx being spent by input #0:
 00000000
scriptPubKey of output being spent by input #0
(note that this comes from the block 9 coinbase transaction!):
 43410411db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6
 909a5cb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f999b8643f656
 b412a3ac
input #0 sequence:
 ffffffff
number of outputs:
 02
output #0 value (10 BTC or 1,000,000,000 satoshis):
 00ca9a3b00000000
output #0 scriptPubKey (Hal Finney's public key plus OP_CHECKSIG):
 434104ae1a62fe09c5f51b13905f07f06b99a2f7159b2225f374cd378d71302f
 a28414e7aab37397f554a7df5f142c21c1b7303b8a0626f1baded5c72a704f7e
 6cd84cac
outut #1 value (40 BTC or 4,000,000,000 satoshis):
 00286bee00000000
output #1 scriptPubKey (Satoshi's oen public key again, for change):
 43410411db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6
 909a5cb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f999b8643f656
 b412a3ac
locktime:
 00000000
hash type (from the input #0 signature):
 01000000
```

Which gives us this blob of serialized data:
```
0100000001c997a5e56e104102fa209c6a852dd90660a20b2d9c352423edce25
857fcd37040000000043410411db93e1dcdb8a016b49840f8c53bc1eb68a382e
97b1482ecad7b148a6909a5cb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9
d4c03f999b8643f656b412a3acffffffff0200ca9a3b00000000434104ae1a62
fe09c5f51b13905f07f06b99a2f7159b2225f374cd378d71302fa28414e7aab3
7397f554a7df5f142c21c1b7303b8a0626f1baded5c72a704f7e6cd84cac0028
6bee0000000043410411db93e1dcdb8a016b49840f8c53bc1eb68a382e97b148
2ecad7b148a6909a5cb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f
999b8643f656b412a3ac0000000001000000
```

Finally we can do some code.
See [python/verify_example.py](python/verify_example.py)







