'use strict';

// Import from standard nodejs library
const {randomBytes, Hash} = require('crypto');

// Import the local ECDSA and bech32 modules
const secp256k1 = require('./lib/secp256k1');
const bech32 = require('./lib/bech32');

/**
 * Private key to public key
 */

// Generate a private key
const k = BigInt(`0x${randomBytes(32).toString('hex')}`);
if (k >= secp256k1.ORDER)
  throw new Error('Invalid private key, start over.');
console.log('Private key:', k.toString(16));

// Derive the public key by multiplying by generator point
const P = secp256k1.G.mul(k);
console.log('Public key: x:', P.x);
console.log('            y:', P.y);

/**
 * Compressed public key
 */

// Get header byte
const is_y_even = (P.y.val & 1n) === 0n;
const header_byte = is_y_even ? 2 : 3;

// Get public key X coordinate as bytes
const x_bytes = P.x.getBytes();

// Get 33-byte compressed public key
const compressed = Buffer.alloc(33);
compressed.writeUInt8(header_byte, 0);
x_bytes.copy(compressed, 1);
console.log("Compressed public key:", compressed.toString('hex'))

/**
 * Public key to pubkeyhash
 */

// Get 20-byte hash
const public_key_hash = Hash('ripemd160').update(Hash('sha256').update(compressed).digest()).digest();
console.log('Public key hash in hex: ', public_key_hash.toString('hex'));

/**
 * Pubkeyhash to address
 */

const address2 = bech32.encode('bc', 0, public_key_hash)
console.log('bech32 address:', address2)

