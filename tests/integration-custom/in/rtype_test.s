
addi x1, x0, 5
addi x2, x0, 2

add x3, x1, x2      # x3 = 7
mul x4, x1, x2      # x4 = 10
sub x5, x2, x1      # x5 = -3
mulh x6, x1, x5     # x6 = 0
mulhu x7, x1, x5     
slt x8, x1, x2      # x8 = 0
xor x9, x1, x2      # x9 = 1
srl x10, x4, x2     # x10 = 2
mul x11, x1, x5     # x11 = -15
srl x12, x11, x2    # x12 = 0011 1111 1111 1111 1111 1111 1111 1100
sra x13, x11, x2    # x13 = -4
or x14, x3, x4      # x14 = 15
and x15, x3, x4     # x15 = 2