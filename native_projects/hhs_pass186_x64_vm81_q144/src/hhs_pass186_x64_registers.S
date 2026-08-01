.text
.globl hhs186_x64_capture_xyzw_registers
.type hhs186_x64_capture_xyzw_registers, @function
hhs186_x64_capture_xyzw_registers:
    /* SysV ingress: x=RDI, y=RSI, z=RDX, w=RCX, image=R8. */
    movq %r8, %rax
    movq %rdi, 0(%rax)
    movq %rsi, 8(%rax)
    movq %rdx, 16(%rax)
    movq %rcx, 24(%rax)

    /* Canonical internal noncommutative lanes. */
    movq %rdi, %r8
    movq %rsi, %r9
    movq %rdx, %r10
    movq %rcx, %r11

    movq %r8, 32(%rax)
    movq %r9, 40(%rax)
    movq %r10, 48(%rax)
    movq %r11, 56(%rax)
    ret
.size hhs186_x64_capture_xyzw_registers, .-hhs186_x64_capture_xyzw_registers
.section .note.GNU-stack,"",@progbits
