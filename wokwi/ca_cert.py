"""Cole UM certificado CA PEM baixado do seu deployment EMQX.
Preserve as linhas BEGIN CERTIFICATE e END CERTIFICATE.
O certificado CA é público; não é senha nem chave privada.
"""
import binascii

CA_PEM = """
COLE_AQUI_O_CERTIFICADO_PEM_COMPLETO
"""

def ca_der():
    begin = "-----BEGIN CERTIFICATE-----"
    end = "-----END CERTIFICATE-----"
    if CA_PEM.count(begin) != 1 or CA_PEM.count(end) != 1:
        raise ValueError("CA pendente: cole um certificado PEM completo em ca_cert.py")
    encoded = CA_PEM.split(begin)[1].split(end)[0]
    encoded = "".join(encoded.split())
    return binascii.a2b_base64(encoded)
