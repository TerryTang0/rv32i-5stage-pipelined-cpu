addi s1, x0, 5          # PC 0x00: s1 = 5
addi t0, x0, 5          # PC 0x04: t0 = 5

beq  s1, t0, target     # PC 0x08: branch should be taken
addi a0, x0, 111        # PC 0x0C: MUST be flushed

target:
    addi s0, x0, 1      # PC 0x10: s0 = 1