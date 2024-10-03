#!/bin/bash

SCRIPT_CWD=$(dirname "$0")
PROJECT_ROOT_PATH=$(readlink -f "${SCRIPT_CWD}/../..")

EXT_DOMAIN="local.bit4id.click"
INT_DOMAIN="ara-sd.intranet.bit4id.com"
PRJECT_SLUG="questionnaires_compiler"
PARENT="${PRJECT_SLUG}.${EXT_DOMAIN}"
OUTPUT_PATH="${PROJECT_ROOT_PATH}/nginx/configs/certs/${PARENT}"
mkdir -p "${OUTPUT_PATH}"

openssl req \
    -x509 \
    -newkey rsa:2048 \
    -sha256 \
    -days 365 \
    -nodes \
    -keyout "${OUTPUT_PATH}/privkey.pem" \
    -out "${OUTPUT_PATH}/fullchain.cert" \
    -subj "/CN=${PARENT}" \
    -extensions v3_ca \
    -extensions v3_req \
    -config <( \
        echo '[req]'; \
        echo 'default_bits=2048'; \
        echo 'distinguished_name=req'; \
        echo 'x509_extension = v3_ca'; \
        echo 'req_extensions = v3_req'; \
        echo '[v3_req]'; \
        echo 'basicConstraints = CA:FALSE'; \
        echo 'keyUsage = nonRepudiation, digitalSignature, keyEncipherment'; \
        echo 'subjectAltName = @alt_names'; \
        echo '[ alt_names ]'; \
        echo "DNS.1 = ${PARENT}"; \
        echo "DNS.2 = ${PRJECT_SLUG}.${INT_DOMAIN}"; \
        echo "DNS.3 = localhost"; \
        echo '[ v3_ca ]'; \
        echo 'subjectKeyIdentifier=hash'; \
        echo 'authorityKeyIdentifier=keyid:always,issuer'; \
        echo 'basicConstraints = critical, CA:TRUE, pathlen:0'; \
        echo 'keyUsage = critical, cRLSign, keyCertSign'; \
        echo 'extendedKeyUsage = serverAuth, clientAuth')

# openssl pkcs12 -export -out certificate.pfx -inkey $PARENT.key -in $PARENT.crt
# openssl x509 -outform der -in "${OUTPUT_PATH}/fullchain.pem" -out "${PROJECT_ROOT_PATH}/keycloak/fullchain.crt"