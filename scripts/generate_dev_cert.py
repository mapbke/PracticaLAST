from datetime import datetime, timedelta, timezone
from pathlib import Path
import ipaddress
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def generate():
    folder = Path(__file__).resolve().parents[1] / 'certs'
    folder.mkdir(exist_ok=True)
    cert_path, key_path = folder / 'dev-cert.pem', folder / 'dev-key.pem'
    if cert_path.exists() and key_path.exists():
        return str(cert_path), str(key_path)
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'localhost')])
    now = datetime.now(timezone.utc)
    cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
        .serial_number(x509.random_serial_number()).not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=30)).add_extension(x509.SubjectAlternativeName([
            x509.DNSName('localhost'), x509.IPAddress(ipaddress.ip_address('127.0.0.1'))]), critical=False)
        .sign(key, hashes.SHA256()))
    key_path.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    return str(cert_path), str(key_path)

if __name__ == '__main__':
    generate()
