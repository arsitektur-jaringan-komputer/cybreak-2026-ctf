#!/bin/sh
set -e

if [ -n "${RCTF_FLAG:-}" ]; then
    printf '%s\n' "$RCTF_FLAG" > /root/flag.txt
fi
unset RCTF_FLAG RCTF_FLAGS

FLAG_NAME="$(tr -dc '0-9a-f' < /dev/urandom | head -c 12).txt"
FLAG_PATH="/${FLAG_NAME}"

rm -f /[0-9a-f]*.txt 2>/dev/null || true
cp /root/flag.txt "$FLAG_PATH"
chown root:root "$FLAG_PATH"
chmod 444 "$FLAG_PATH"

node /app/scripts/backup_watchdog.js &

exec setpriv --reuid=node --regid=node --init-groups "$@"
