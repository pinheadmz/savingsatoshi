# Chapter 6 challenge outline



1. Mike Ramen needs 1 BTC to book his flight to Vanderpoole's private island. You
decide to send him 1 BTC from your chapter 3 mining rewards, which have been sent
by the mining pool to the address you created in chapter 4.

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
    "confirmations": 341,
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
compressed public key hash and address from chapter 4. The amount looks right, too:
6.5 BTC. Mike Ramen gives you an address to send your 1 BTC contribution to:

```
bc1qgghq08syehkym52ueu9nl5x8gth23vr8hurv9dyfcmhaqk4lrlgs28epwj
```

Hm, that address looks a lot longer than yours! I wonder why...

Anyway, we need to create and sign a transaction that sends one of your 6.5 BTC
to this address. We looked at Satoshi's transaction structure in chapter 5 but your
transaction will be a bit different. Technology has improved a lot since block 170,
and Bitcoin transactions are now version 2, and follow a new protocol called Segregated
Witness.

Segregated Witness transactions work just like their legacy predecessors. There are a few
global values like `version` and `locktime`. There is an array of inputs (UTXOs we want to spend)
and an array of outputs (new UTXOs we want to create, for other people to spend in the future).
There will also be an array of witnesses, one for each input. That is where signatures and scripts
will go instead of the `scriptSig`.

The message serializations for all these components is documented here:
https://en.bitcoin.it/wiki/Protocol_documentation#tx
and here:
https://github.com/bitcoinbook/bitcoinbook/blob/develop/ch06.asciidoc


And remember: integers in Bitcoin are serialized little-endian!


2. Finish the implementation of `Class Input`:

It should have a method `from_output(txid: str, vout: int, value: int, scriptcode: bytes)`.

The first two arguments are the transaction ID and the index of the output of that
transaction you want to spend from. Eventually we will pass in the `txid` and `vout`
values you got above from `listunspent`. Note that hashes in Bitcoin are little-endian,
which means that you will need to *reverse the byte order* of the `txid` string!

The second two arguments are the value of the output we want to spend (in satoshis)
and something called a `scriptcode`. For now, just store these data as properties
of the `Input` class, we won't need them until step 6.

We also need a `serialize()` method that returns a byte array according to the specification:

Outpoint:

| Size | Name     | Type  | Description |
|------|----------|-------|-------------|
|  32  | `txid`   | bytes | Hash of transaction being spent from |
|  4   | `index`  | int   | Position of output being spent in the transaction's output array |


Input:

| Size | Name     | Type  | Description |
|------|----------|-------|-------------|
|  36  | outpoint | bytes | `txid` and output index being spent from |
|  1   | length   | int   | `ScriptSig` length (always `0` for Segregated Witness) |
|  0   | script   | bytes | Always empty for Segregated Witness |
|  4   | sequence | int   | Default value is `0xffffffff` but can be used for relative timelocks |



3. Finish the implementation of `Class Output`:

It should have a method `from_options(addr: str, value: int)` which accepts a Bitcoin
address as a string (like the address from Mike Ramen) and a value as an integer.
The value is expressed as a number of satoshis! Remember, 1 BTC = 100000000 satoshis.
You will need to use our bech32 library again to decode the address into `version`
and `data` components.

The class also needs a `serialize()` method method that returns a byte array according to the specification:

Output:

| Size | Name     | Type  | Description |
|------|----------|-------|-------------|
|  8   | value    | int   | Number of satoshis being sent |
|  1   | length   | int   | Total length of the following script (the "witness program") |
|  1   | version  | int   | The segregated witness version. Derived from the bech32 address |
|  1   | length   | int   | Length of the following witness program data |
| (var)| program  | bytes | The data component derived from the bech32 address |



4. Finish the implementation of `Class Witness`:

It should have a method `push_item(data: bytes)` which accepts a byte array and adds
that item to the witness stack.

It will also need a `serialize()` method that returns the serialized witness stack:

Witness stack:

| Size | Name     | Type    | Description |
|------|----------|---------|-------------|
|  1   | count    | int     | The number of items in the witness stack |
| (var)| items    | items[] | Serialized stack items |

Witness stack item:

| Size | Name     | Type  | Description |
|------|----------|-------|-------------|
|  1   | length   | int   | Total length of the following stack item |
| (var)| data     | bytes | The raw bytes of the stack item |



5. Finish the implementation of `Class Transaction`:

It should have global properties `locktime` and `version` as well as an array of
inputs, outputs, and witness stacks.

It will need a `serialize()` method that outputs the entire
transaction as bytes formatted for broadcast on the Bitcoin p2p network.


| Size | Name     | Type        | Description |
|------|----------|-------------|-------------|
|  4   | version  | int         | Currently `2` |
|  2   | flags    | bytes       | Must be exactly `0x0001` for segregated witness |
|  1   | in count | int         | The number of inputs |
| (var)| inputs   | Inputs[]    | All transaction inputs, serialized |
|  1   | out count| int         | The number of outputs |
| (var)| outputs  | Outputs[]   | All transaction outputs, serialized |
| (var)| witness  | Witnesses[] | All witness stacks, serialized |
|  4   | locktime | int         | Setting to `0` indicates finality |

Notice that there is no "count" value for witnesses. That is because the number
of witness stacks must always be exactly equal to the number of inputs.



6. Transaction digest:

In chapter 5 we learned that to sign a transaction we first need to rearrange
and hash its data into a message, which becomes one of the raw inputs to our signing
algorithm. Since we are using segregated witness now, we also need to implement
the updated transaction digest algorithm which is specified in
[BIP 143](https://github.com/bitcoin/bips/blob/master/bip-0143.mediawiki#user-content-Specification).

Remember each transaction input needs its own signature, and so some components of
the digest algorithm can be cached and reused but others will be different depending
on which input is being signed! Finish the transaction method `digest(input_index)` that
computes the 32-byte message for signing an input.

Some notes:

- "Double SHA-256" or `dSHA256` = `sha256(sha256(data))`

- `value` is the amount of the satoshis in the output being spent from. We added
it to our `Input` class back in step 2, and just saved it there inside the class
until now.

- `scriptcode` is the raw Bitcoin script being evaluated. We also added this to our `Input`
class back in step 2. We'll dive in to this more in the next section, but to spend
from your pay-to-witness-public-key-hash address, your `scriptcode` would be:

`0x1976a914{20-byte-pubkey-hash}88ac`

...which decodes to the following Bitcoin script:
```
OP_PUSHBYTES_25
OP_DUP
OP_HASH160
OP_PUSHBYTES_20
<20-byte public key hash>
OP_EQUALVERIFY
OP_CHECKSIG
```

For more information about `scriptcode` see
[BIP 143](https://github.com/bitcoin/bips/blob/master/bip-0143.mediawiki)

The raw transaction hash preimage is the the serialization of:

| Size | Name     | Type  | Description |
|------|----------|-------|-------------|
|  4   | version  | int   | Transaction version, default `2` |
|  32  | outpoints| bytes | The `dSHA256` of all outpoints from all inputs, serialized |
|  32  | sequences| bytes | The `dSHA256` of all sequence values from all inputs, serialized |
|  36  | outpoint | bytes | The serialized outpoint of the single input being signed |
| (var)| scriptcode | bytes | The output script being spent from |
|  8   | value    | int   | The value in satoshis being spent by the single input being signed |
|  4   | sequence | int   | The sequence value of the single input being signed |
|  32  | outputs  | bytes | The `dSHA256` of all outputs, serialized |
|  4   | locktime | int   | Transaction locktime, default `0` |
|  4   | sighash  | int   | Signature hash type, we will use `1` to indicate "ALL" |


Finally, the message we sign is the double SHA-256 of all this serialized data.



7. Signing!

We wrote the ECDSA signature verification code in the last chapter,
now we need to rearrange that a bit to create a valid signature. Add a method
called `compute_input_signature(index: int, key: int)` to your `Transaction`
class that accepts an input index number and a private key (a 32-byte integer!).
It should compute the message digest for the chosen input using the `digest()`
method from step 6, and return an ECDSA signature in the form of two 32-byte
integers `r` and `s`.

See https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm
for the ECDSA signing algorithm.
Also https://www.secg.org/sec1-v2.pdf Page 44, Section 4.1.3.

The Bitcoin protocol requires one extra step to the signing algorithm, which
requires that the `s` value is "low", meaning less than the order of the curve
divided by 2. Learn more about this in BIP 146:
https://github.com/bitcoin/bips/blob/master/bip-0146.mediawiki#user-content-LOW_S



8. Populate the witness:

Finish the method `sign_input(index: int, key: int)` that calls
our step 7 method `compute_input_signature(index, key)` and handles its return
value. The `r` and `s` numbers need to be encoded with an algorithm called DER
which we have implemented for you.

Bitcoin requires one extra byte appended to the DER-signature which represents
the "sighash type". For now we'll always use the byte `0x01` for this indicating
"SIGHASH ALL".

Once we have that signature blob we need to create a `Witness`
object with two stack items: the signature blob, and your compressed public key.
Push the signature first, followed by the public key.

The witness stack object can then be appended to the witnesses array of the
transaction object.



9. Put it all together:

We know our input, we know our output. Are we ready to build and sign a transaction?
Not quite. We have a 6.5 BTC input and a 1 BTC output... what happens to the other 5.5 BTC?
Most of that will be "change" and we need to send it back to our own address!

Write a script that creates and signs a `Transaction` object. It should have one input
(the UTXO we identified in step 1) and two outputs:

- Mike Ramen gets 100,000,000 satoshis to `bc1qgghq08syehkym52ueu9nl5x8gth23vr8hurv9dyfcmhaqk4lrlgs28epwj`
- You get 550,000,000 back to your address `bc1qm2dr49zrgf9wc74h5c58wlm3xrnujfuf5g80hs`

But wait! We need to include a "fee". We'll shave off a tiny piece of our change output
for the mining pools to incentivize them to include our transaction in a block.
Let's reduce our change from 550,000,000 to 549,999,000 satoshis.

Finally our work is done. Your script should end by returning the result of the
transaction `serialize()` method. This is a valid signed Bitcoin transaction and
we can broadcast it to the network to send Mike Ramen the money he needs!



