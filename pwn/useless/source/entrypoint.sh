#!/bin/sh
set -eu
: "${RCTF_FLAG:?RCTF_FLAG must be supplied by the instancer}"
flag_name="$(od -An -N16 -tx1 /dev/urandom | tr -d ' \n')"
flag_path="/run/ctf/$flag_name"
printf '%s\n' "$RCTF_FLAG" > "$flag_path"
chmod 0444 "$flag_path"
unset RCTF_FLAG RCTF_FLAGS
exec socat TCP-LISTEN:1337,reuseaddr,fork EXEC:/home/mirai/chall,stderr,su=mirai
