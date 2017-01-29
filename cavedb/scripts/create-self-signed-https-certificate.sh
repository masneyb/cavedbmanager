#!/bin/bash -eu

# Copyright 2016-2017 Brian Masney <masneyb@onstation.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

cd "${SSL_BASE_DIR}"

# Generate CA
mkdir -p "${CA_DIR}"/private "${NEWCERTS_DIR}"
echo '01' > "${CA_DIR}"/serial
touch "${CA_DIR}"/index.txt
openssl req -new -x509 -extensions v3_ca -keyout "${CA_KEY}" -out "${CA_CERT}" -days 3650 -nodes -subj "${SSL_SELFSIGNED_CA_SUBJECT}"

# Generate CSR
openssl req -new -key "${SSL_KEY}" -out "${CSR}" -subj "${SSL_SELFSIGNED_CA_SUBJECT}"

# Sign certificate
openssl ca -batch -in "${CSR}" -config /etc/ssl/openssl.cnf

cp "${CA_DIR}"/newcerts/01.pem "${SSL_CERT}"
cp "${CA_CERT}" "${SSL_CA_CERT}"

cat "${SSL_CERT}" "${SSL_CA_CERT}" > "${SSL_COMBINED_CERTS}"
