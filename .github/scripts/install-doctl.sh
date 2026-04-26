#!/bin/bash
# install-doctl.sh — instala doctl en GitHub Actions runner Ubuntu.
# Idempotente + retry en descargas (defensa contra transient network failures).

set -euo pipefail

if command -v doctl >/dev/null 2>&1; then
    echo "doctl already installed: $(doctl version | head -1)"
    exit 0
fi

DOCTL_VERSION="1.117.0"
ARCH=$(uname -m)
case "$ARCH" in
    x86_64) DOCTL_ARCH="amd64" ;;
    aarch64) DOCTL_ARCH="arm64" ;;
    *) echo "Unsupported arch: $ARCH"; exit 1 ;;
esac

URL="https://github.com/digitalocean/doctl/releases/download/v${DOCTL_VERSION}/doctl-${DOCTL_VERSION}-linux-${DOCTL_ARCH}.tar.gz"

cd /tmp
# Retry 3 veces con backoff exponencial — defense vs transient GitHub releases throttling
for attempt in 1 2 3; do
    if curl -sLf --max-time 60 "$URL" -o doctl.tar.gz; then
        echo "Download OK on attempt $attempt"
        break
    fi
    echo "Download attempt $attempt failed, retry in $((attempt * 5))s..."
    sleep $((attempt * 5))
done

[ ! -f /tmp/doctl.tar.gz ] && { echo "ERROR: failed to download doctl after 3 attempts"; exit 1; }

tar -xzf doctl.tar.gz
sudo mv doctl /usr/local/bin/
rm -f doctl.tar.gz
doctl version
echo "doctl installed"
