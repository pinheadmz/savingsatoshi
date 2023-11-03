# Chapter 6 challenge outline



1. Mike Ramen needs 2 BTC to book his flight to VPs private island. You two
already have 1 BTC in a shared "multisig" address. You decide to top that off with
1 BTC from your Chapter 3 mining rewards, which have been sent by the mining pool
to the address you created in Chapter 4.

You open you Bitcoin full node and execute a command to see where your money
is in the blockchain:

```
$ bitcoin-cli listunspent

[
  {
    "txid": "74149a689ce95562309cf4c404ef6ca91e76b6a19ef25e9625e9c13d93fac4e1",
    "vout": 0,
    "address": "bc1qm2dr49zrgf9wc74h5c58wlm3xrnujfuf5g80hs",
    "label": "",
    "scriptPubKey": "0014da9a3a9443424aec7ab7a628777f7130e7c92789",
    "amount": 6.50000000,
    "confirmations": 341
    "spendable": true,
    "solvable": true,
    "desc": "wpkh([a73804d3/0'/0'/0']02ab3d3cb82c1eb89168824b20f667224d868250dedec69177012e5a26c5221ae8)#5mf00k95",
    "parent_descs": [
    ],
    "safe": true
  }
]
```

This is an unspent transaction output (aka "UTXO"). You might recognize your
compressed public key hash and address from Chapter 4. The amount looks right, too:
6.5 BTC. Mike Ramen gives you an address to send your 1 BTC contribution to:

```
bc1qgghq08syehkym52ueu9nl5x8gth23vr8hurv9dyfcmhaqk4lrlgs28epwj
```

Hm, that address looks a lot longer than yours! I wonder why...

Anyway, we need to create and sign a transaction that sends one of our 6.5 BTC
to this address.