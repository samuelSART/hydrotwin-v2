#!/bin/sh
set -e

# CONTAINER START-UP SCRIPT #

echo && echo "Running with DEBUG=${DEBUG:-False} in ENVIRONMENT=${ENVIRONMENT:-not set}"

case "$DEBUG" in
    TRUE|True|true|YES|yes ) DEBUG=TRUE;;
    * ) DEBUG="";
esac

case "$ENVIRONMENT" in
    PRODUCTION|Production|production|PROD|prod ) ENVIRONMENT=PRODUCTION;;
    * ) ENVIRONMENT="";
esac

MAX_RETRIES=5

gen_certs() {
    echo -e "Generating certificates for \033[1;32m\`${CERT_DOMAIN}\`\033[0m domain name(s)..."
    # !! --test-cert: REMOVE FOR PRODUCTION, use the staging server for the certificate !!
    [[ "$DEBUG" ]] && debug_param=--debug
    [[ "$ENVIRONMENT" != "PRODUCTION" ]] && staging=--test-cert
    i=1; while [ "$i" -le "$MAX_RETRIES" ]; do
        certbot certonly $staging $debug_param --cert-name NGINX --webroot --webroot-path /usr/share/nginx/ --non-interactive --agree-tos \
            --no-eff-email --email "${CERT_EMAIL:-'default@email.com'}" --domains "$CERT_DOMAIN" --keep-until-expiring
        [[ $? -eq 0 ]] && return 0
        sleep 60
        i=$(( i + 1 ))
    done
    return 1
}

gen_selfsigned_certs() {
    if [ ! -f /run/secrets/ssl_key ]; then
        HOST=$([[ -n "$CERT_DOMAIN" ]] && echo "$CERT_DOMAIN" | cut -d, -f1 || echo "$HOSTNAME")
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -reqexts v3_req -subj "/CN=$HOST" \
            -keyout /etc/nginx/certs/ssl_key -out /etc/nginx/certs/ssl_cert
        cp /etc/nginx/certs/ssl_key /etc/nginx/certs/ssl_chain
    else
        # if external certificates have been provided, use them instead
        ln -sf /run/secrets/ssl_cert /etc/nginx/certs/ssl_cert
        ln -sf /run/secrets/ssl_key /etc/nginx/certs/ssl_key
        [[ -f /run/secrets/ssl_chain ]] && ln -sf /run/secrets/ssl_chain /etc/nginx/certs/ssl_chain || \
            ln -sf /run/secrets/ssl_cert /etc/nginx/certs/ssl_chain
    fi
}

case "$SSL_ENABLED" in
    TRUE|True|true|YES|yes ) SSL_ENABLED=TRUE ;;
    * ) SSL_ENABLED="" ;;
esac

# Replace MAPBOX_TOKEN label with actual env var value
find /usr/share/nginx/html/ -type f -name "*.js" -exec sed -i -e "s|{{ MAPBOX_TOKEN }}|$MAPBOX_TOKEN|g" {} \;

# Replace AEMET_KEY label with actual env var value
find /usr/share/nginx/html/ -type f -name "*.js" -exec sed -i -e "s|{{ AEMET_KEY }}|$AEMET_KEY|g" {} \;

# Generate Diffie-Hellman parameters
[[ ! -d /etc/nginx/certs/ ]] && mkdir -p /etc/nginx/certs/
openssl dhparam -out /etc/nginx/certs/dhparam.pem 2048

# Launch Nginx
echo -e "\033[4;37mLaunching Nginx...\033[0m"
nginx -g 'daemon off;' > /proc/1/fd/1 2>/proc/1/fd/2 &
sleep 2

if [ "$SSL_ENABLED" ]; then
    echo -e "\033[0;32m## SSL enabled. ##\033[0m"
    rm -f /etc/nginx/templates/nginx.conf.template || true
    # Generate certificates for specified domain names @ CERT_DOMAIN, or selfsign new ones.
    if [ -n "$CERT_DOMAIN" ]; then
        if gen_certs; then
            # if successful, link cert files to configured path in Nginx template conf & run cron for check & renew
            echo -e "\033[0;32mCertificates successfully generated.\033[0m"
            [[ -e /etc/letsencrypt/live/NGINX/cert.pem ]] && ln -sf /etc/letsencrypt/live/NGINX/cert.pem /etc/nginx/certs/ssl_cert
            [[ -e /etc/letsencrypt/live/NGINX/privkey.pem ]] && ln -sf /etc/letsencrypt/live/NGINX/privkey.pem /etc/nginx/certs/ssl_key
            [[ -e /etc/letsencrypt/live/NGINX/chain.pem ]] && ln -sf /etc/letsencrypt/live/NGINX/chain.pem /etc/nginx/certs/ssl_chain
            [[ -e /etc/letsencrypt/live/NGINX/fullchain.pem ]] && ln -sf /etc/letsencrypt/live/NGINX/fullchain.pem /etc/nginx/certs/ssl_fullchain
            crond
        else
            echo -e "\033[0;31m[ERROR] Certificates could not be obtained\033[0m"
            gen_selfsigned_certs
        fi
    else
        gen_selfsigned_certs
    fi
else
    echo -e "\033[0;33m## SSL disabled. ##\033[0m"
    rm -f /etc/nginx/templates/nginx_ssl.conf.template || true
fi

# Link externally provided Nginx configuration template for use
if [ -f /run/secrets/web_conf ]; then
    rm -f /etc/nginx/templates/* || true
    ln -sf /run/secrets/web_conf /etc/nginx/templates/nginx.conf.template
fi

# Perform Nginx start-up configuration & templates processing
[[ -n "$DNS_RESOLVER" ]] || export DNS_RESOLVER=127.0.0.11
[[ -n "$SRVC_NAMESPACE" ]] || export SRVC_NAMESPACE=""
find "/docker-entrypoint.d/" -follow -type f -print | sort -V | while read -r f; do "$f"; done
rm -f /etc/nginx/conf.d/default.conf || true

echo -e "\033[1;37mReloading Nginx\033[0m"
nginx -s reload > /proc/1/fd/1 2>/proc/1/fd/2 &
sleep infinity
