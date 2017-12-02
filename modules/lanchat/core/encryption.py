import os
import binascii

# Locals
CAN_ENCRYPT = False

# Check if pycrypto is installed
try:
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP
    from Crypto.Signature import PKCS1_PSS
    from Crypto.Hash import SHA512
    CAN_ENCRYPT = True
except ModuleNotFoundError:
    pass

def bin2base64(bin_str):
    """ Convert bytes to base64 """
    return binascii.b2a_base64(bin_str)

def base642bin(base64_str):
    """ Convert base64 to bytes """
    return binascii.a2b_base64(base64_str)


class Encryption():
    def __init__(self, host):
        """ Constructor
        If a key exists, use that key.
        Otherwise create a new key, save it, then use it.

        Keyword arguments:
        host -- a Host object
        """
        # Check if pycrypto is installed
        global CAN_ENCRYPT
        if not CAN_ENCRYPT:
            raise ValueError

        self.host = host

        pubkey_path = os.path.join('.', 'security', 'pubkey.der')
        privkey_path = os.path.join('.', 'security', 'privkey.der')

        # Create directories if doesn't exist
        if not os.path.exists(os.path.dirname(pubkey_path)):
            try:
                os.makedirs(os.path.dirname(pubkey_path))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        try:
            with open(pubkey_path, 'r') as f:
                key = base642bin(f.read().encode())
                self.pubkey = RSA.importKey(key)
            with open(privkey_path, 'r') as f:
                key = base642bin(f.read().encode())
                self.privkey = RSA.importKey(key)
        except FileNotFoundError:
            self.privkey = RSA.generate(2048)
            self.pubkey = self.privkey.publickey()
            with open(pubkey_path, 'w') as f:
                key = self.pubkey.exportKey('DER')
                f.write(str(bin2base64(key), 'ascii'))
            with open(privkey_path, 'w') as f:
                key = self.privkey.exportKey('DER')
                f.write(str(bin2base64(key), 'ascii'))

    def get_pubk(self):
        """ Get the string representation of the public key """
        key = self.pubkey.exportKey('DER')
        return str(bin2base64(key), 'ascii')

    def encrypt(self, message, pubk):
        """ Encrypt a message using a given public key
        Returns ciphertext in base64 ascii string

        Keyword arguments:
        message -- a message in string
        pubk -- a public key in base64 ascii string
        """
        # Decode public key
        pubk = base642bin(bytes(pubk, 'ascii'))
        pubk = RSA.importKey(pubk)
        # Encrypt message
        cipher = PKCS1_OAEP.new(pubk)
        ciphertext = cipher.encrypt(bytes(message, 'utf-8'))
        return str(bin2base64(ciphertext), 'ascii')

    def decrypt(self, ciphertext):
        """ Decrypt a ciphertext using self's private key
        Returns original message in string

        Keyword arguments:
        ciphertext -- a ciphertext in base64 ascii string
        """
        # Decode ciphertext
        ciphertext = bytes(ciphertext, 'ascii')
        # Decryption
        ciphertext = base642bin(ciphertext)
        cipher = PKCS1_OAEP.new(self.privkey)
        return str(cipher.decrypt(ciphertext), 'utf-8')

    def sign(self, message):
        """ Sign a message and return a signature in base64

        Keyword arguments:
        message -- the message in utf-8 string
        """
        if not isinstance(message, str):
            raise ValueError("message not a string")
        h = SHA512.new(bytes(message, 'utf-8'))
        signer = PKCS1_PSS.new(self.privkey)
        signature = signer.sign(h)
        return str(bin2base64(signature), 'ascii')

    def verify(self, message, signature, pubkey):
        """ Verify a message, returns true if valid, else False

        Keyword arguments:
        message -- the message
        signature -- the signature in base64 ascii string
        pubkey -- sender's public key in base64 ascii string
        """
        if not isinstance(message, str):
            raise ValueError('message not a string')
        if not isinstance(signature, str):
            raise ValueError('signature not a string')
        if not isinstance(pubkey, str):
            raise ValueError('pubkey not a string')
        # Decode parameters
        signature = base642bin(bytes(signature, 'ascii'))
        pubkey = base642bin(bytes(pubkey, 'ascii'))
        # Verify
        key = RSA.importKey(pubkey)
        h = SHA512.new(bytes(message, 'utf-8'))
        verifier = PKCS1_PSS.new(key)
        if verifier.verify(h, signature):
            return True
        return False


    def msgs_protocol_send(self, message, pubk_str):
        """ Get the string protocol of msgs
        Returns a string representation of msgs protocol

        Keyword arguments:
        message -- the message
        pubk_str -- receiver's public key
        """
        protocol = 'msgs:{port}:{user}:{ciphertext}:{signature}'
        user = self.host.get_username()
        port = self.host.get_port()
        ciphertext = self.encrypt(message, pubk_str)
        signature = self.sign(ciphertext)
        return protocol.format(user=user, port=port,
                               ciphertext=ciphertext, signature=signature)


    def msgs_protocol_receive(self, ciphertext, certificate, pubk):
        """ Get the original message from the ciphertext, returns None
        if verification fails

        Keyword arguments:
        ciphertext -- the ciphertext
        certificate
        """
        if not isinstance(ciphertext, str):
            raise ValueError('ciphertext not a string')
        if not isinstance(certificate, str):
            raise ValueError('certificate not a string')
        if not isinstance(pubk, str):
            raise ValueError('pubkey not a string')
        if not self.verify(ciphertext, certificate, pubk):
            return None
        return self.decrypt(ciphertext)
