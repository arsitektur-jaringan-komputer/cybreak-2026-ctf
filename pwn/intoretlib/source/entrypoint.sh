#!/bin/sh
set -eu
: "${RCTF_FLAG:?RCTF_FLAG must be supplied by the instancer}"
umask 077
mkdir -p /run/ctf
printf '%s\n' "$RCTF_FLAG" > /run/ctf/flag.txt
chmod 0400 /run/ctf/flag.txt
chown ctf:ctf /run/ctf/flag.txt
unset RCTF_FLAG RCTF_FLAGS
exec setpriv --reuid=ctf --regid=ctf --init-groups --no-new-privs "$@"
