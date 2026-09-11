#!/bin/sh
set -eu
: "${RCTF_FLAG:?RCTF_FLAG must be supplied by the instancer}"
printf '%s\n' "$RCTF_FLAG" > /run/ctf/flag.txt
chmod 0444 /run/ctf/flag.txt
unset RCTF_FLAG RCTF_FLAGS
exec socat TCP-LISTEN:1337,reuseaddr,fork EXEC:/home/mirai/chall,stderr,su=mirai
