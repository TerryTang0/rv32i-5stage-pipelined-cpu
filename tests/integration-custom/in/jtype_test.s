addi s0, x0, 5          # 1,  0x00, s0 = 5

jal  ra, jal_target     # 2,  0x04, ra = 0x0
addi t0, x0, 110        # skip if jal works

jal_target:
    addi s1, x0, 6      # 3,  0x0C, s1 = 6

    addi t1, x0, 28     # 4,  0x10, t1 = 0x1C
    jalr ra, t1, 0      # 5,  0x14, ra = 0x18
    addi t2, x0, 220    # skip if jalr works

jalr_target:
    addi a0, x0, 9      # 6,  0x1C, a0 = 9