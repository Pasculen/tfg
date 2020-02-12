from OpenSSL.SSL import TLSv1_2_METHOD, FILETYPE_PEM, VERIFY_FAIL_IF_NO_PEER_CERT
import OpenSSL
import socket
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


HOST = '127.0.1.1'
PORT = 1234

# Create context for de TLS session
context = OpenSSL.SSL.Context(TLSv1_2_METHOD)

# Create connection
conn = OpenSSL.SSL.Connection(context, socket.socket(socket.AF_INET, socket.SOCK_STREAM))
conn.set_connect_state()
# Connect to server
conn.connect((HOST, PORT))

conn.write("Hello world")
data = conn.read(1024)
print("Received "+data.decode())
