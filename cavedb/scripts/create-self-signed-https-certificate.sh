#!/bin/bash -eu
# SPDX-License-Identifier: Apache-2.0

SSL_SELFSIGNED_CA_SUBJECT="/C=US/ST=Some State/L=Some Locality/O=Some Organization/CN=localhost"

cp /etc/ssl/private/ssl-cert-snakeoil.key "${SSL_KEY}"

SSL_BASE_DIR=$(dirname "${SSL_KEY}")

SSL_CERT="${SSL_BASE_DIR}"/ssl-cert-snakeoil-signed.pem
SSL_CA_CERT="${SSL_BASE_DIR}"/ssl-cert-snakeoil-cacert.pem

CA_DIR="${SSL_BASE_DIR}"/demoCA
CA_KEY="${CA_DIR}"/private/cakey.pem
CA_CERT="${CA_DIR}"/cacert.pem
NEWCERTS_DIR="${CA_DIR}"/newcerts
CSR="${SSL_BASE_DIR}"/ssl-cert-snakeoil.csr
DAYS=1095

cd "${SSL_BASE_DIR}"

# Generate CA
mkdir -p "${CA_DIR}"/private "${NEWCERTS_DIR}"
echo '01' > "${CA_DIR}"/serial
touch "${CA_DIR}"/index.txt
openssl req -new -x509 -extensions v3_ca -keyout "${CA_KEY}" -out "${CA_CERT}" -days "${DAYS}" -nodes -subj "${SSL_SELFSIGNED_CA_SUBJECT}"

# Generate CSR
openssl req -new -key "${SSL_KEY}" -out "${CSR}" -days "${DAYS}" -subj "${SSL_SELFSIGNED_CA_SUBJECT}"

# Sign certificate
openssl ca -days "${DAYS}" -batch -in "${CSR}" -config /etc/ssl/openssl.cnf

cp "${CA_DIR}"/newcerts/01.pem "${SSL_CERT}"
cp "${CA_CERT}" "${SSL_CA_CERT}"

cat "${SSL_CERT}" "${SSL_CA_CERT}" > "${SSL_COMBINED_CERTS}"
