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

Anyway, we need to create and sign a transaction that sends one of your 6.5 BTC
to this address. We looked at Satoshi's transaction structure in Chapter 5 but your
transaction will be a bit different. Technology has improved a lot since block 170,
and Bitcoin transactions are now version 2, and follow a new protocol called Segregated
Witness.

Segregated Witness transactions work just like their legacy predecessors. There are a few
global values like `version` and `locktime`. There is an array of Inputs (UTXOs we want to spend)
and an array of Outputs (new UTXOs we want to create, for other people to spend in the future).
There will also be an array of witnesses for each input. That is where signatures and scripts
will go instead of the `scriptSig`.

The message serializations for all these components is documented here:
https://en.bitcoin.it/wiki/Protocol_documentation#tx
and here:
https://github.com/bitcoinbook/bitcoinbook/blob/develop/ch06.asciidoc




2. Inputs: Finish the implementation of `Class Input`. It should have a method `from_json()` which
can parse a UTXO in JSON format like the one you got above from `listunspent`. It also must have a
`serialize()` method that returns a byte array according to the specification:

| Size | Name     | Description |
|------|----------|-------------|
|  32  | `txid`   | Hash of transaction being spent from |
|  4   | `index`  | Position of output being spent in the transaction's output array |
|  1   | length   | `ScriptSig` length (always `0` for Segregated Witness) |
|  0   | script   | Always empty for Segregated Witness |
|  4   | sequence | Default value is `0xffffffff` but can be used for relative timelocks |



3. Outputs: Finish the implementation of `Class Output`. It should have a method `from_options(addr, value)`
which accepts a Bitcoin address as a string (like the address from Mike Ramen) and a value as an integer
number of satoshis! Remember, 1 BTC = 100000000 satoshis. You will need to use our bech32 library
again to decode the address into `version` and `data` components. The class also needs a `serialize()`
method method that returns a byte array according to the specification:

| Size | Name     | Description |
|------|----------|-------------|
|  8   | Value    | Little-endian integer number of satoshis being sent |
|  1   | length   | Total length of the following script (the "witness program") |
|  1   | version  | The segregated witness version. Derived from the bech32 address |
|  1   | length   | Length of the following witness program data. |
| (var)| program  | The data component derived from the bech32 address, between 2 and 40 bytes |