from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
import datetime

ROOT_PASS = b"hola"
SERVER_PASS = b"director"

def root_certificate():
	# Creating new private key
	key = rsa.generate_private_key(
		public_exponent=65537,
		key_size=2048,
		backend=default_backend()
		)

	# Wrinting private key to disk for safe keeping
	with open("key.pem", "wb") as f:
		f.write(key.private_bytes(
			encoding=serialization.Encoding.PEM,
			format=serialization.PrivateFormat.TraditionalOpenSSL,
			encryption_algorithm=serialization.BestAvailableEncryption(ROOT_PASS),
		))

	# Details for the certificate. Subject and issuer are always the same.
	subject = issuer = x509.Name([
		x509.NameAttribute(NameOID.COUNTRY_NAME, u"ES"),
		x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Madrid"),
		x509.NameAttribute(NameOID.LOCALITY_NAME, U"Madrid"),
		x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Simple Deception"),
		x509.NameAttribute(NameOID.COMMON_NAME, u"simple.deception"),
	])

	cert = x509.CertificateBuilder().subject_name(
	    subject
	).issuer_name(
	    issuer
	).public_key(
	    key.public_key()
	).serial_number(
	    x509.random_serial_number()
	).not_valid_before(
	    datetime.datetime.utcnow()
	).not_valid_after(
	    # Our certificate will be valid for 1 year
	    datetime.datetime.utcnow() + datetime.timedelta(days=365)
	).add_extension(
	    x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
	    critical=False,
	# Sign our certificate with our private key
	).sign(key, hashes.SHA256(), default_backend())

	with open("certificate.pem", "wb") as f:
	    f.write(cert.public_bytes(serialization.Encoding.PEM))

def server_certificate():

	ca_cert = x509.load_pem_x509_certificate(
		open("certificate.pem", "rb").read(),
		default_backend()
	)
	
	ca_rootkey = serialization.load_pem_private_key(
		open("key.pem", "rb").read(),
		password=ROOT_PASS,
		backend=default_backend()
	)

	# Creating new private key
	key = rsa.generate_private_key(
		public_exponent=65537,
		key_size=2048,
		backend=default_backend()
		)

	# Wrinting private key to disk for safe keeping
	with open("server_key.pem", "wb") as f:
		f.write(key.private_bytes(
			encoding=serialization.Encoding.PEM,
			format=serialization.PrivateFormat.TraditionalOpenSSL,
			encryption_algorithm=serialization.NoEncryption(),
		))

	# Details for the certificate. 
	subject = x509.Name([
		x509.NameAttribute(NameOID.COUNTRY_NAME, u"ES"),
		x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Madrid"),
		x509.NameAttribute(NameOID.LOCALITY_NAME, U"Madrid"),
		x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"JSPC"),
		x509.NameAttribute(NameOID.COMMON_NAME, u"javier.sanchez"),
	])


	server_cert = x509.CertificateBuilder().subject_name(
	    subject
	).issuer_name(
	    ca_cert.issuer
	).public_key(
	    key.public_key()
	).serial_number(
	    x509.random_serial_number()
	).not_valid_before(
	    datetime.datetime.utcnow()
	).not_valid_after(
	    # Our certificate will be valid for 1 year
	    datetime.datetime.utcnow() + datetime.timedelta(days=365)
	).add_extension(
	    x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
	    critical=False,
	# Sign our certificate with our ca private key
	).sign(ca_rootkey, hashes.SHA256(), default_backend())

	with open("server_cert.pem", "wb") as f:
		f.write(server_cert.public_bytes(serialization.Encoding.PEM))

print("Making root certificate...")
root_certificate()
print("Done")
print("Making server certificate...")
server_certificate()
print("Done")