'use strict';

// Import from standard nodejs library
const {Hash} = require('crypto');

// Import the local ECDSA and bech32 modules
const secp256k1 = require('./lib/secp256k1');


function create_tx_message() {
  let msg = '';
  // version:
  msg += '01000000';
  // number of inputs:
  msg += '01';
  // hash of tx being spent by input #0:
  msg += 'c997a5e56e104102fa209c6a852dd90660a20b2d9c352423edce25857fcd3704';
  // index of output of tx being spent by input #0:
  msg += '00000000';
  // scriptPubKey of output being spent by input #0:
  // https://blockstream.info/tx/0437cd7f8525ceed2324359c2d0ba26006d92d856a9c20fa0241106ee5a597c9?output:0&expand
  // FILL THIS IN!
  msg +=
  // input #0 sequence:
  msg += 'ffffffff';
  // number of outputs:
  msg += '02';
  // output #0 value (10 BTC or 1,000,000,000 satoshis):
  msg += '00ca9a3b00000000';
  // output #0 scriptPubKey (Hal Finney's public key plus OP_CHECKSIG):
  msg += '434104ae1a62fe09c5f51b13905f07f06b99a2f7159b2225f374cd378d71302f';
  msg += 'a28414e7aab37397f554a7df5f142c21c1b7303b8a0626f1baded5c72a704f7e';
  msg += '6cd84cac';
  // outut #1 value (40 BTC or 4,000,000,000 satoshis):
  msg += '00286bee00000000';
  // output #1 scriptPubKey (Satoshi's oen public key again, for change):
  msg += '43410411db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6';
  msg += '909a5cb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f999b8643f656';
  msg += 'b412a3ac';
  // locktime:
  msg += '00000000';
  // SIGHASH type
  // FILL THIS IN!
  msg += 
  return msg
}


function msg_to_integer(msg) {
  // Given a hex string to sign, convert that string to bytes,
  // double-SHA256 the bytes and then return a BigInt() from the 32-byte digest.
  const bytes = Buffer.from(msg, 'hex');
  const single_hash = Hash('sha256').update(bytes).digest();
  const double_hash = Hash('sha256').update(single_hash).digest();
  return BigInt('0x' + double_hash.toString('hex'));
}


function verify(sig_r, sig_s, pubkey_x, pubkey_y, msg) {
  // Verify an ECDSA signature given a public key and a message.
  // All input values will be 32-byte BigInt()'s.
  // Start by creating a curve point representation of the public key
  const key = new secp256k1.GE(new secp256k1.FE(pubkey_x), new secp256k1.FE(pubkey_y));
  // Next, check the range limits of the signature values
  if (sig_r == 0n || sig_r >= secp256k1.ORDER) {
    console.log('invalid r value');
    return false;
  }
  if (sig_s == 0n || sig_s >= secp256k1.ORDER) {
    console.log('invalid s value');
    return false;
  }
  // Helper function:
  // Find modular multiplicative inverse using Extended Euclidean Algorithm
  function invert(value, modulus = secp256k1.ORDER) {
    let x0 = 0n;
    let x1 = 1n;
    let a = value;
    let m = modulus;

    while (a > 1n) {
      const q = a / m;
      let t = m;
      m = a % m;
      a = t;
      t = x0;
      x0 = x1 - q * x0;
      x1 = t;
    }

    if (x1 < 0n)
      x1 += modulus;

    return x1;
  }
  // Implement ECDSA!
  //   u1 = m / s mod n
  //   u2 = r / s mod n
  //   R = G * u1 + A * u2
  //   r == x(R) mod n

}


function encode_message(text) {
  // Given an ascii-encoded text message, serialize a byte array
  // with the Bitcoin protocol prefix string followed by the text.
  // Both components must be preceded by a length byte.
  // Returns a hex string.
  const prefix = Buffer.from('Bitcoin Signed Message:\n', 'ascii');

}


function decode_sig(base64_sig) {
  // Decode a base64-encoded signature string into its ECDSA
  // signature elements r and s, returned as an array of two BigInt()'s.
  // Remember to throw away the first byte of metadata from the signature string!

}


// MAIN
// Public key values from step 7:
const pubkey_x = 0x11db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6909a5cn
const pubkey_y = 0xb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f999b8643f656b412a3n

function verify_satoshi() {
  // From step 5:
  const msg_hex = create_tx_message()
  const msg = msg_to_integer(msg_hex)
  // From step 6:
  const sig_r = 0x4e45e16932b8af514961a1d3a1a25fdf3f4f7732e9d624c6c61548ab5fb8cd41n
  const sig_s = 0x181522ec8eca07de4860a4acdd12909d831cc56cbbac4622082221a8768d1d09n
  // Satoshi's signature
  console.log(`Satoshi: ${verify(sig_r, sig_s, pubkey_x, pubkey_y, msg)}`)
}

function verify_vp() {
  // Provided by Vanderpoole
  let text =  'I am Vanderpoole and I have control of the private key Satoshi\n';
      text += 'used to sign the first-ever Bitcoin transaction confirmed in block #170.\n';
      text += 'This message is signed with the same private key.';
  const sig = 'H4vQbVD0pLK7pkzPto8BHourzsBrHMB3Qf5oYVmr741pPwdU2m6FaZZmxh4ScHxFoDelFC9qG0PnAUl5qMFth8k=';

  const msg_hex = encode_message(text);
  const msg = msg_to_integer(msg_hex);

  const [sig_r, sig_s] = decode_sig(sig);
  // Vanderpoole's signature
  console.log(`Vanderpoole: ${verify(sig_r, sig_s, pubkey_x, pubkey_y, msg)}`);

  // Vanderpoole's actual key
  const vp_pubkey_x = 0x9d57ded01d3a7652a957cf86fd4c3d2a76e76e83d3c965e1dca45f1ee0663063n;
  const vp_pubkey_y = 0x6b8bcbc3df3fbc9669efa2ccd5d7fa5a89fe1c0045684189f01ea915b8a746a6n;
  console.log(`Vanderpoole actual: ${verify(sig_r, sig_s, vp_pubkey_x, vp_pubkey_y, msg)}`);
}

verify_satoshi()
verify_vp()
