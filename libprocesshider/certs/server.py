#!/usr/bin/python3

from OpenSSL.SSL import TLSv1_2_METHOD, FILETYPE_PEM, VERIFY_FAIL_IF_NO_PEER_CERT
import OpenSSL
import socket
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


HOST = '127.0.1.1'
PORT = 1234
def hola():
	pass

# Create context for de TLS session
context = OpenSSL.SSL.Context(TLSv1_2_METHOD)

# Load server private key and cert
context.use_privatekey_file("server_key.pem")
context.use_certificate_file("server_cert.pem")

# Add verify mode
context.set_verify(VERIFY_FAIL_IF_NO_PEER_CERT, hola)

# Load root certificate
context.load_verify_locations(cafile="certificate.pem")

# Create the initial connection with the above context and a socket
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.setblocking(1)
soc.bind((HOST, PORT))
soc.listen(1)
conn_ini = OpenSSL.SSL.Connection(context, soc)

# Accept client onnection
while 1:
	conn, addr = conn_ini.accept()
	conn.set_accept_state()
	print("Connected by "+str(addr))

	while 1:
		try:
			data = conn.read(1024)
			print(data.decode())
		except OpenSSL.SSL.SysCallError as e:
			#if e[0] == -1 or e[1] == 'Unexpected EOF':
			conn.shutdown()
			break