# Chapter 6 challenge outline



1. Mike Ramen needs 2 BTC to book his flight to Vanderpoole's private island. You two
already have 1 BTC in a shared "multisig" address. You decide to top that off with
1 BTC from your chapter 3 mining rewards, which have been sent by the mining pool
to the address you created in chapter 4.

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

Outpoint:

| Size | Name     | Description |
|------|----------|-------------|
|  32  | `txid`   | Hash of transaction being spent from |
|  4   | `index`  | Position of output being spent in the transaction's output array |


Input:

| Size | Name     | Description |
|------|----------|-------------|
|  36  | outpoint | txid and output index being spent from |
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
|  8   | value    | Little-endian integer number of satoshis being sent |
|  1   | length   | Total length of the following script (the "witness program") |
|  1   | version  | The segregated witness version. Derived from the bech32 address |
|  1   | length   | Length of the following witness program data. |
| (var)| program  | The data component derived from the bech32 address, between 2 and 40 bytes |



4. Witnesses: Finish the implementation of `Class Witness`. It should have a method `push_item(data)`
which accepts a byte array and adds that item to the witness stack. It will also need a `serialize()`
method that returns the serialized witness stack:

Witness stack:

| Size | Name     | Description |
|------|----------|-------------|
|  1   | count    | The number of items in the witness stack |
| (var)| items    | Serialized stack items |

Witness stack item:

| Size | Name     | Description |
|------|----------|-------------|
|  1   | length   | Total length of the following stack item |
| (var)| data     | The raw bytes of the stack item |



5. Transaction: Finish the implementation of `Class Transaction`. It should have
global properties `locktime` and `version` as well as an array of inputs, outputs,
and witness stacks. It will need a `serialize()` method that outputs the entire
transaction as bytes formatted for broadcast on the Bitcoin p2p network.


| Size | Name     | Description |
|------|----------|-------------|
|  4   | version  | Currently `2`, encoded as a little-endian integer |
|  2   | flags    | Must be exactly `0x0001` for segregated witness |
|  1   | in count | The number of inputs |
| (var)| inputs   | All transaction inputs, serialized |
|  1   | out count| The number of outputs |
| (var)| outputs  | All transaction outputs, serialized |
| (var)| witness  | All witness stacks, serialized |
|  4   | locktime | Setting to `0xffffffff` indicates finality |

Notice that there is no "count" value for witnesses. That is because the number
of witness stacks must always be exactly equal to the number of inputs.



6. Transaction digest: In chapter 5 we learned that to sign a transaction we
first need to rearrange and hash its data into a message, which becomes the
raw input to our signing algorithm. Since we are using segregated witness now,
we also need to implement the updated transaction digest algorithm which is specified
in [BIP 143](https://github.com/bitcoin/bips/blob/master/bip-0143.mediawiki#user-content-Specification).
Remember each transaction input needs its own signature, and so some components of
the digest algorithm can be cached and reused but others are different depending
on which input is being signed! Finish the transaction method `digest(input_index)` that
computes the 32 byte message for signing an input.

"Double SHA-256" or `dSHA256` = `sha256(sha256(data))`

`scriptcode` is the raw Bitcoin script being evaluated. We'll dive in to this
more in the next section, but to spend from your pay-to-witness-public-key-hash
address, you will you use this data:

`0x1976a914{20-byte-pubkey-hash}88ac`

This decodes to the following Bitcoin script:
```
OP_PUSHBYTES_25
OP_DUP
OP_HASH160
OP_PUSHBYTES_20
<20-byte public key hash>
OP_EQUALVERIFY
OP_CHECKSIG
```

The raw transaction hash preimage is the the serialization of:

| Size | Data |
|------|------|
|  4   | Version (little endian) |
|  32  | `dSHA256` of all outpoints from all inputs, serialized |
|  32  | `dSHA256` of all sequence values from all inputs, serialized |
|  36  | The serialized outpoint of the input being signed |
| (var)| `scriptcode` |
|  8   | Value in satoshis being spent by the input being signed (little endian) |
|  4   | Sequence value of the input being signed |
|  32  | `dSHA256` or all outputs, serialized |
|  4   | Locktime (little endian) |
|  4   | Sighash type, we will use `0x01000000` to indicate "ALL" |


Finally, the message we sign is the double SHA-256 of all this serialized data.



7. Signing! We wrote the ECDSA signature verification code in the last chapter,
now we need to rearrange that a bit to create a valid signature. Add a method
called `compute_input_signature(index, key)` to your `Transaction` class that accepts an input
index number and a 32-byte private key. It should compute the message digest for
the chosen input, and return an ECDSA signature in the form of two 32-byte
numbers `r` and `s`.



8. Populate the witness: Finish the method `sign_input(index, key)` that calls
our previous method `compute_input_signature(index, key)` and handles its return
value. The `r` and `s` values need to be encoded with an algorithm called DER
which we have implemented for you. Once we have that we need to create a `Witness`
object with two stack items: your public key, and this new signature. The witness
object can be appended to the witnesses array of the transaction object.




9. Put it all together: We know our input, we know our output. Are we ready to
build and sign a transaction? Not quite. We have a 6.5 BTC input and a 1 BTC
output... what happens to the other 5.5 BTC? Most of that will be "change" and
we need to send it back to our own address!

Write a script that creates and signs a `Transaction` object. It should have one input
(the UTXO we identified in step 1) and two outputs:

Mike Ramen gets 100,000,000 satoshis to `bc1qgghq08syehkym52ueu9nl5x8gth23vr8hurv9dyfcmhaqk4lrlgs28epwj`
You get 550,000,000 back to your address `bc1qm2dr49zrgf9wc74h5c58wlm3xrnujfuf5g80hs`

Oh wait! We need to include a "fee". We'll shave off a tiny piece of our change output
for the mining pools to incentivize them to include our transaction in a block.
Let's reduce our change from 550,000,000 to 549,999,000 satoshis.

Finally our work is done. Your script should end by returning the result of the
transaction `serialize()` method. This is a valid signed Bitcoin transaction and
we can broadcast it to the network to send Mike Ramen the money he needs!



