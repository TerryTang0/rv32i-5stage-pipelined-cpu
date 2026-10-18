addi s0, x0, 100        # s0 = 100

lui  s1, 0x12345
addi s1, s1, 0x678      # s1 = 0x12345678

sw   s1, 0(s0)          # store word at address 100
lw   t0, 0(s0)          # t0 = stored word

lb   t1, 0(s0)          # load byte at offset 0
lb   t2, 1(s0)          # load byte at offset 1
lh   a0, 0(s0)          # load halfword at offset 0

addi s2, x0, -1         # s2 = 0xffffffff
sb   s2, 7(s0)          # store s2 at address 107
lb   s1, 7(s0)          # s1 = 0xffffffff 

sh   s2, 8(s0)          # store half s2 at address 108
lh   s0, 8(s0)          # s0 = 0xffffffff