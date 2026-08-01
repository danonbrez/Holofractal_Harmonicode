#if defined(__x86_64__)
    .text
    .globl hhs188_bott_step_x86_64
    .type hhs188_bott_step_x86_64, @function
hhs188_bott_step_x86_64:
    movl %edi, %eax
    andl $7, %eax
    movl %eax, %edx
    shrl $1, %edx
    xorl %eax, %edx
    shrl $1, %edx
    andl $1, %edx
    subl $1, %edx
    xorl $1, %eax
    andl %edx, %eax
    ret
    .size hhs188_bott_step_x86_64, .-hhs188_bott_step_x86_64
    .section .note.GNU-stack,"",@progbits
#endif
