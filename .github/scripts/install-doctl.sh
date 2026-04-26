#!/bin/bash
# install-doctl.sh — instala doctl en GitHub Actions runner Ubuntu.
# Idempotente.

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

cd /tmp
curl -sL "https://github.com/digitalocean/doctl/releases/download/v${DOCTL_VERSION}/doctl-${DOCTL_VERSION}-linux-${DOCTL_ARCH}.tar.gz" \
  | tar -xz
sudo mv doctl /usr/local/bin/
doctl version
echo "doctl installed"
