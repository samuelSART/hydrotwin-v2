#!/bin/sh

echo -e "\033[0;32mCertificates for \033[1;32m\`${CERT_DOMAIN}\`\033[0m domain name(s) successfully renewed.\033[0m"
echo -e "\033[1;37mReloading Nginx\033[0m"
nginx -s reload > /proc/1/fd/1 2>/proc/1/fd/2
