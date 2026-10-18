addi s1, x0, 5
addi t0, x0, 5
addi t1, x0, 7
addi t2, x0, -1

beq  s1, t0, beq_taken
addi a0, x0, 111          # should be skipped
beq_taken:
    addi s0, x0, 1

    bne  s1, t1, bne_taken
    addi a0, x0, 111      # should be skipped
bne_taken:
    addi s0, x0, 2

    blt  t2, s1, blt_taken
    addi a0, x0, 111      # should be skipped
blt_taken:
    addi s0, x0, 3

    bge  t1, s1, bge_taken
    addi a0, x0, 111      # should be skipped
bge_taken:
    addi s0, x0, 4

    bltu s1, t2, bltu_taken
    addi a0, x0, 111      # should be skipped
bltu_taken:
    addi s0, x0, 5

    bgeu t2, s1, bgeu_taken
    addi a0, x0, 111      # should be skipped
bgeu_taken:
    addi s0, x0, 6