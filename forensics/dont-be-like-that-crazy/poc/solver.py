import struct
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

core = open("memory.core", "rb").read()
enc = open("ciphertext.bin", "rb").read()


def fnv(data):
    h = 0x811C9DC5
    for byte in data:
        h = ((h ^ byte) * 0x01000193) & 0xFFFFFFFF
    return h


# read index mask R0OT2026, cobain semua candidate
root = core.index(b"R0OT2026")
count, mask = struct.unpack_from("<II", core, root + 24)
chunks, offset = {}, 0

while (offset := core.find(b"K3YNOD3!", offset)) >= 0:
    encoded_index, checksum = struct.unpack_from("<II", core, offset + 16)
    left, right = core[offset + 24:offset + 32], core[offset + 32:offset + 40]
    chunk = bytes(a ^ b for a, b in zip(left, right))
    index = encoded_index ^ mask
    if index < count and fnv(chunk) == checksum: # kalo decoy ga masuk
        chunks[index] = chunk
    offset += 8

assert len(chunks) == count and enc[:8] == b"PUJOW!1\0"
key = b"".join(chunks[i] for i in range(count))
flag = AESGCM(key).decrypt(enc[8:20], enc[20:], None)
print(flag.decode())
i