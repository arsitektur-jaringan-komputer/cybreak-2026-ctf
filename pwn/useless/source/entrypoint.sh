#!/bin/sh
set -eu
: "${RCTF_FLAG:?RCTF_FLAG must be supplied by the instancer}"
<<<<<<< HEAD
umask 077
mkdir -p /run/ctf
printf '%s\n' "$RCTF_FLAG" > /run/ctf/flag.txt
chmod 0444 /run/ctf/flag.txt
chown mirai:mirai /run/ctf/flag.txt
unset RCTF_FLAG RCTF_FLAGS
exec setpriv --reuid=mirai --regid=mirai --init-groups --no-new-privs "$@"
=======
printf '%s\n' "$RCTF_FLAG" > /run/ctf/flag.txt
chmod 0444 /run/ctf/flag.txt
unset RCTF_FLAG RCTF_FLAGS
exec socat TCP-LISTEN:1337,reuseaddr,fork EXEC:/home/mirai/chall,stderr,su=mirai
>>>>>>> db7fd10ed33b83e07d6cf930eaf9616df1fecafb
