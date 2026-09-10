#!/bin/sh
set -eu
exec socat TCP-LISTEN:1337,reuseaddr,fork EXEC:/home/mirai/chall,stderr,su=mirai
