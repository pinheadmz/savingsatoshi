'use strict';

// Import from standard nodejs library
const {randomBytes, Hash} = require('crypto');

// Import the local ECDSA and bech32 modules
const secp256k1 = require('./lib/secp256k1');
const bech32 = require('./lib/bech32');

function privatekey_to_address(private_key) {
  const publickey = privatekey_to_publickey(private_key);
  const compressed = compress_publickey(publickey);
  const pubkeyhash = hash_compressed(compressed);
  const address = hash_to_address(pubkeyhash);
  return address;
}

function privatekey_to_publickey(private_key) {
  // Multiply the private key by the ECDSA generator point G to
  // produce a new curve point which is the public key.
  // Return that curve point (also known as a group element)
  // which will be an instance of secp256k1.GE
  const G = secp256k1.G;

}

function compress_publickey(publickey) {
  // Determine if the y coordinate is even or odd and prepend the
  // corresponding header byte to the x coordinate.
  // Return 33-byte Buffer
  const header_byte = {
    'y_is_even': Buffer.from([2]),
    'y_is_odd':  Buffer.from([3])
  };

}

function hash_compressed(compressed) {
  // Get the sha256 digest of the compressed public key,
  // then get the ripemd160 digest of that sha256 hash.
  // Return 32-byte Buffer

}

function hash_to_address(pubkeyhash) {
  // Encode the compressed public key hash with bech32
  // to create a witness version 0 address.
  // Returns string

}

// MAIN
const private_key = BigInt(`0x${randomBytes(32).toString('hex')}`);
if (private_key >= secp256k1.ORDER)
  throw new Error('Invalid private key, start over.');
const address = privatekey_to_address(private_key);
console.log('Private key:', `0x${private_key.toString(16)}`);
console.log('Address:', address);
