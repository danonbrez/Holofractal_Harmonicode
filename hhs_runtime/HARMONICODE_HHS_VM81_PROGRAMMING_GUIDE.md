+    1 # HHS VM81 Programming Guide
+    2 ## Official Development Documentation v8.1
+    3 
+    4 **HARMONICODE / HHS Substrate Runtime**  
+    5 **Canonical Freeze: v7.2 with v8.1 Extensions**
+    6 
+    7 ---
+    8 
+    9 ## Table of Contents
+   10 
+   11 1. [Introduction](#introduction)
+   12 2. [Architecture Overview](#architecture-overview)
+   13 3. [Computational Model](#computational-model)
+   14 4. [Instruction Set Reference](#instruction-set-reference)
+   15 5. [Programming Model](#programming-model)
+   16 6. [Receipt and Ledger System](#receipt-and-ledger-system)
+   17 7. [Closure Conditions](#closure-conditions)
+   18 8. [Constraint Field System](#constraint-field-system)
+   19 9. [Advanced Topics](#advanced-topics)
+   20 10. [Example Programs](#example-programs)
+   21 11. [Best Practices](#best-practices)
+   22 12. [Appendices](#appendices)
+   23 
+   24 ---
+   25 
+   26 ## Introduction
+   27 
+   28 ### What is HHS VM81?
+   29 
+   30 HHS VM81 is a specialized virtual machine designed for harmonic computation over a 72-phase transport substrate with 81-cell state space. It implements a receipt-based ledger system with multiple closure detection mechanisms.
+   31 
+   32 ### Key Features
+   33 
+   34 - **81-cell grid** (72 visible + 9 hidden Lo Shu cells)
+   35 - **72-base hash projection** system
+   36 - **Receipt-chained execution** with witness bits
+   37 - **Three closure classes**: Transport, Orientation, Constraint
+   38 - **Non-commutative multiplication** with phase propagation
+   39 - **Quantum gate utilities** (QGU, APB, CLOSURE, IDENTITY)
+   40 - **Constraint field dynamics**
+   41 
+   42 ### Use Cases
+   43 
+   44 - Harmonic convergence detection
+   45 - Phase transport simulation
+   46 - Constraint satisfaction with field dynamics
+   47 - Receipt-auditable computation
+   48 - Multi-closure state space exploration
+   49 
+   50 ---
+   51 
+   52 ## Architecture Overview
+   53 
+   54 ### State Space
+   55 
+   56 ```
+   57 ┌─────────────────────────────────────────┐
+   58 │  72 Visible Cells (HASH72 projection)   │
+   59 │  [0..71] - mod-72 arithmetic            │
+   60 ├─────────────────────────────────────────┤
+   61 │  9 Hidden Cells (Lo Shu positions)      │
+   62 │  [72..80] - special closure positions   │
+   63 └─────────────────────────────────────────┘
+   64 ```
+   65 
+   66 ### Core Components
+   67 
+   68 #### 1. Grid Cells (`vm->cells[81]`)
+   69 - 81 uint8_t values (mod 72)
+   70 - Cells [0..71]: visible state space
+   71 - Cells [72..80]: hidden Lo Shu layer
+   72 
+   73 #### 2. XYZW Registers (`vm->xyzw[4]`)
+   74 - Track non-commutative operation state
+   75 - Used for orientation closure detection
+   76 - Balance: `(x + y - z - w) % 72`
+   77 
+   78 #### 3. Constraint Field (`vm->constraints[64]`)
+   79 - Up to 64 active constraints
+   80 - Each with: type, phase, strength, lineage
+   81 - Influences phase transport via bias field
+   82 
+   83 #### 4. Receipt Chain
+   84 - Cryptographic hash chain of execution
+   85 - Witness flags encode state transitions
+   86 - Ledger-advancing vs. ledger-freezing ops
+   87 
+   88 #### 5. Program Counter (PC)
+   89 - Points to current instruction
+   90 - Advances automatically (unless branched)
+   91 - Terminates at program_len or HALT
+   92 
+   93 ---
+   94 
+   95 ## Computational Model
+   96 
+   97 ### Execution Cycle
+   98 
+   99 ```
+  100 1. Fetch instruction at PC
+  101 2. Check if op advances ledger
+  102    ├─ YES: Execute → Hash state → Record receipt
+  103    └─ NO:  Execute → Annotate terminal receipt
+  104 3. Propagate phase transport
+  105 4. Constraint competition
+  106 5. Detect closures
+  107 6. Update PC
+  108 7. Repeat until HALT or orbit
+  109 ```
+  110 
+  111 ### Phase Arithmetic
+  112 
+  113 All cell values use **mod-72 arithmetic**:
+  114 
+  115 ```c
+  116 uint8_t wrap72(int v) {
+  117     int r = v % 72;
+  118     if (r < 0) r += 72;
+  119     return r;
+  120 }
+  121 ```
+  122 
+  123 **Reciprocal phase**: `(phase + 36) % 72`
+  124 
+  125 ### Hash72 Character Set
+  126 
+  127 ```
+  128 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?
+  129 ```
+  130 
+  131 72 characters for base-72 encoding.
+  132 
+  133 ---
+  134 
+  135 ## Instruction Set Reference
+  136 
+  137 ### Instruction Structure
+  138 
+  139 ```c
+  140 typedef struct {
+  141     Opcode op;        // Operation code
+  142     uint8_t a;        // First operand (cell index)
+  143     uint8_t b;        // Second operand (cell index)
+  144     uint8_t c;        // Result cell index
+  145     uint8_t cg_id;    // Closure group ID
+  146     uint8_t phase;    // Phase parameter
+  147     Edge81 next[4];   // Conditional edges (unused in most ops)
+  148 } Instruction;
+  149 ```
+  150 
+  151 ### Basic Arithmetic
+  152 
+  153 #### **ADD** - Addition
+  154 ```c
+  155 { OP_ADD, a, b, c, cg_id, phase }
+  156 ```
+  157 - `cells[c] = wrap72(cells[a] + cells[b])`
+  158 - Energy: `cells[c]`
+  159 - **Advances ledger**: YES
+  160 
+  161 #### **SUB** - Subtraction
+  162 ```c
+  163 { OP_SUB, a, b, c, cg_id, phase }
+  164 ```
+  165 - `cells[c] = wrap72(cells[a] - cells[b])`
+  166 - Energy: `cells[c]`
+  167 - **Advances ledger**: YES
+  168 
+  169 #### **ROT** - Phase Rotation
+  170 ```c
+  171 { OP_ROT, a, _, c, cg_id, phase }
+  172 ```
+  173 - `cells[c] = wrap72(cells[a] + phase)`
+  174 - Energy: `cells[c]`
+  175 - **Advances ledger**: YES
+  176 
+  177 ### Bitwise Operations
+  178 
+  179 #### **XOR** - Bitwise XOR
+  180 ```c
+  181 { OP_XOR, a, b, c, cg_id, phase }
+  182 ```
+  183 - `cells[c] = wrap72((cells[a] ^ cells[b]) + phase + cg_id)`
+  184 - Energy: `cells[c]`
+  185 - **Advances ledger**: YES
+  186 
+  187 #### **AND** - Bitwise AND
+  188 ```c
+  189 { OP_AND, a, b, c, cg_id, phase }
+  190 ```
+  191 - `cells[c] = wrap72((cells[a] & cells[b]) + phase)`
+  192 - Energy: `cells[c]`
+  193 - **Advances ledger**: YES
+  194 
+  195 #### **OR** - Bitwise OR
+  196 ```c
+  197 { OP_OR, a, b, c, cg_id, phase }
+  198 ```
+  199 - `cells[c] = wrap72((cells[a] | cells[b]) + phase)`
+  200 - Energy: `cells[c]`
+  201 - **Advances ledger**: YES
+  202 
+  203 ### Memory Operations
+  204 
+  205 #### **LOAD** - Load Immediate
+  206 ```c
+  207 { OP_LOAD, immediate, _, c, cg_id, phase }
+  208 ```
+  209 - `cells[c] = wrap72(immediate)`
+  210 - Energy: `cells[c]`
+  211 - **Advances ledger**: YES
+  212 
+  213 #### **STORE** - Store Value
+  214 ```c
+  215 { OP_STORE, a, _, c, cg_id, phase }
+  216 ```
+  217 - `cells[c] = cells[a]`
+  218 - Energy: `cells[c]`
+  219 - **Advances ledger**: YES
+  220 
+  221 ### Control Flow
+  222 
+  223 #### **BRANCH** - Unconditional Jump
+  224 ```c
+  225 { OP_BRANCH, target, _, _, cg_id, phase }
+  226 ```
+  227 - `PC = target`
+  228 - If `target >= program_len`: HALT
+  229 - Energy: `cg_id`
+  230 - **Advances ledger**: YES
+  231 
+  232 #### **BZ** - Branch if Zero
+  233 ```c
+  234 { OP_BZ, a, target, _, cg_id, phase }
+  235 ```
+  236 - If `cells[a] == 0`: `PC = target`
+  237 - Else: `PC++`
+  238 - Energy: `cg_id`
+  239 - **Advances ledger**: YES
+  240 
+  241 #### **BNZ** - Branch if Not Zero
+  242 ```c
+  243 { OP_BNZ, a, target, _, cg_id, phase }
+  244 ```
+  245 - If `cells[a] != 0`: `PC = target`
+  246 - Else: `PC++`
+  247 - Energy: `cg_id`
+  248 - **Advances ledger**: YES
+  249 
+  250 #### **QBRANCH** - Polarity Branch
+  251 ```c
+  252 { OP_QBRANCH, a, _, _, cg_id, phase }
+  253 ```
+  254 - Compute polarity: `pol = (cells[a] / 18) & 3`
+  255 - Branch to `next[pol].target` if enabled
+  256 - Else: HALT
+  257 - Energy: `wrap72(cg_id + pol * 9)`
+  258 - **Advances ledger**: YES
+  259 
+  260 #### **HALT** - Terminate Execution
+  261 ```c
+  262 { OP_HALT, _, _, _, _, _ }
+  263 ```
+  264 - Sets `vm->halted = 1`
+  265 - Witness: `W_HALT | W_LEDGER_FROZEN`
+  266 - **Advances ledger**: NO (freezes terminal receipt)
+  267 
+  268 ### Non-Commutative Multiplication
+  269 
+  270 #### **MULXY** - Multiply X·Y Order
+  271 ```c
+  272 { OP_MULXY, a, b, c, cg_id, phase }
+  273 ```
+  274 - `cells[c] = wrap72(cells[a] * cells[b])`
+  275 - Updates XYZW: `xyzw[0] += a; xyzw[1] += b`
+  276 - Phase transport from both operands
+  277 - Witness: `W_NONCOMMUTATIVE`
+  278 - Energy: `cells[c]`
+  279 - **Advances ledger**: YES
+  280 
+  281 **Phase Transport**:
+  282 ```
+  283 propagate_phase_transport(vm, cells[a], cells[c], cg_id);
+  284 propagate_phase_transport(vm, cells[b], cells[c], cg_id);
+  285 ```
+  286 
+  287 #### **MULYX** - Multiply Y·X Order
+  288 ```c
+  289 { OP_MULYX, a, b, c, cg_id, phase }
+  290 ```
+  291 - `cells[c] = wrap72(cells[b] * cells[a])`
+  292 - Updates XYZW: `xyzw[1] += a; xyzw[0] += b` (reversed!)
+  293 - Phase transport from both operands (reversed order)
+  294 - Witness: `W_NONCOMMUTATIVE`
+  295 - Energy: `cells[c]`
+  296 - **Advances ledger**: YES
+  297 
+  298 **Note**: MULXY and MULYX differ in XYZW update order and transport sequence.
+  299 
+  300 ### Quantum Gate Utilities
+  301 
+  302 #### **QGU** - Quantum Gate Update
+  303 ```c
+  304 { OP_QGU, q_cell, c_cell, result, d_cell_id, phase }
+  305 ```
+  306 - `delta = qgu_delta(cells[q_cell], cells[c_cell], cells[d_cell_id % 81])`
+  307 - `cells[result] += delta`
+  308 - Witness: `W_QGU_APPLIED`
+  309 - Energy: `cells[result]`
+  310 - **Advances ledger**: YES
+  311 
+  312 **QGU Formula**:
+  313 ```c
+  314 delta = (c · q² + d · q⁴) mod 72
+  315 ```
+  316 
+  317 ### Gate Verification
+  318 
+  319 #### **GATE_APB** - A=P=B Gate
+  320 ```c
+  321 { OP_GATE_APB, a, p, b, cg_id, phase }
+  322 ```
+  323 - Test: `cells[a] == cells[p] == cells[b]`
+  324 - Witness: `W_GATE_APB_PASS` or `W_GATE_APB_FAIL`
+  325 - Energy: `cg_id` (pass) or `cg_id + 36` (fail)
+  326 - **Advances ledger**: YES
+  327 
+  328 **Use case**: Verify three-way phase equality.
+  329 
+  330 #### **GATE_CLOSURE** - Closure Equation Gate
+  331 ```c
+  332 { OP_GATE_CLOSURE, Pc, pc, qc, nc_xc, yc }
+  333 ```
+  334 - Encoding:
+  335   - `nc = cg_id & 0x0F`
+  336   - `xc = (cg_id >> 4) & 0x0F`
+  337   - `yc = phase & 0x0F`
+  338 - Test equations:
+  339   - `P² - pq = n⁴`
+  340   - `n⁴ = xy`
+  341 - Witness: `W_GATE_CLOSURE_PASS` or `W_GATE_CLOSURE_FAIL`
+  342 - Energy: `cg_id` (pass) or `cg_id + 48` (fail)
+  343 - **Advances ledger**: YES
+  344 
+  345 **Mathematical invariant**:
+  346 ```
+  347 cells[Pc]² - cells[pc]·cells[qc] = cells[nc]⁴ = cells[xc]·cells[yc]
+  348 ```
+  349 
+  350 #### **GATE_IDENTITY** - Logarithmic Identity Gate
+  351 ```c
+  352 { OP_GATE_IDENTITY, x_cell, y_cell, u_cell, cg_id, phase }
+  353 ```
+  354 - Tests identity:
+  355   ```
+  356   A = (x/y)·(y/x)
+  357   B = (-xy)^((x²+y)(y²+x)/4)
+  358   C = e^(x·π - 144·ln|u|) · 4π
+  359   ```
+  360 - Verdict: `log(A) ≈ log(B) ≈ log(C)` within tolerance `1e-6`
+  361 - Witness:
+  362   - `W_GATE_IDENTITY_PASS`: All equal
+  363   - `W_GATE_IDENTITY_FAIL`: Not equal
+  364   - `W_IDENTITY_DEGENERATE`: Division by zero or invalid
+  365 - Energy: `cg_id` (pass) or `cg_id + 24` (fail/degenerate)
+  366 - **Advances ledger**: YES
+  367 
+  368 **Receipt contains**: `identity_residual` (worst log-space difference)
+  369 
+  370 ### Constraint Operations
+  371 
+  372 #### **CONSTRAIN** - Add Constraint
+  373 ```c
+  374 { OP_CONSTRAIN, type, phase_cell, strength, cg_id, phase }
+  375 ```
+  376 - Adds constraint:
+  377   - Type: `type`
+  378   - Phase: `cells[phase_cell]`
+  379   - Strength: `strength`
+  380   - Lineage: current step
+  381 - If table full: replaces weakest constraint
+  382 - Witness: `W_CONSTRAINT_FIRED`
+  383 - Energy: `wrap72(cg_id + strength)`
+  384 - **Advances ledger**: YES
+  385 
+  386 **Constraint effects**: Biases phase transport in 6-cell radius around constraint phase.
+  387 
+  388 #### **RELAX** - Weaken Constraints
+  389 ```c
+  390 { OP_RELAX, amount, _, _, cg_id, phase }
+  391 ```
+  392 - Reduces all constraint strengths by `amount`
+  393 - Deactivates constraints reaching strength 0
+  394 - Energy: `wrap72(cg_id + 1)`
+  395 - **Advances ledger**: YES
+  396 
+  397 ### Grid Operations
+  398 
+  399 #### **SWEEP81** - Conway-Like Sweep
+  400 ```c
+  401 { OP_SWEEP81, _, _, _, cg_id, phase }
+  402 ```
+  403 - For each cell in 9×9 grid:
+  404   ```c
+  405   next[r][c] = wrap72(
+  406       (cells[r][c] + 
+  407        cells[r-1][c] + cells[r+1][c] +
+  408        cells[r][c-1] + cells[r][c+1]) * 29
+  409   )
+  410   ```
+  411 - Wraps at edges (toroidal topology)
+  412 - Witness: `W_SWEEP`
+  413 - Energy: `cg_id`
+  414 - **Advances ledger**: YES
+  415 
+  416 #### **CLOSE81** - Lo Shu Closure
+  417 ```c
+  418 { OP_CLOSE81, _, _, _, cg_id, phase }
+  419 ```
+  420 - Applies Lo Shu values to hidden and boundary cells:
+  421   ```c
+  422   cells[72..80] += LOSHU[0..8]
+  423   cells[63..71] += LOSHU[0..8]
+  424   ```
+  425 - Lo Shu: `[4,9,2, 3,5,7, 8,1,6]`
+  426 - Energy: `cg_id`
+  427 - **Advances ledger**: YES
+  428 
+  429 ---
+  430 
+  431 ## Programming Model
+  432 
+  433 ### Basic Program Structure
+  434 
+  435 ```c
+  436 VM81 vm;
+  437 vm81_init(&vm, seed, SEED_LOSHU);
+  438 
+  439 vm.program_len = 0;
+  440 
+  441 // Initialize any special cell values
+  442 vm.cells[10] = 36;
+  443 vm.cells[11] = 54;
+  444 
+  445 // Add instructions
+  446 vm.program[vm.program_len++] = (Instruction){ OP_LOAD, 42, 0, 5, 10, 0 };
+  447 vm.program[vm.program_len++] = (Instruction){ OP_ADD, 5, 1, 2, 15, 3 };
+  448 vm.program[vm.program_len++] = (Instruction){ OP_HALT, 0, 0, 0, 0, 0 };
+  449 
+  450 // Execute
+  451 for (int i = 0; i < max_steps && !vm.halted; i++) {
+  452     vm81_step(&vm);
+  453 }
+  454 ```
+  455 
+  456 ### Seed Modes
+  457 
+  458 #### **SEED_PLAIN**
+  459 - Pseudorandom initialization from seed
+  460 - No special structure
+  461 
+  462 #### **SEED_LOSHU**
+  463 - Initializes hidden cells [72..80] with Lo Shu pattern
+  464 - Cells [63..71] include seed offset
+  465 - **Recommended for most programs**
+  466 
+  467 #### **SEED_PALINDROME**
+  468 - XORs seed with palindrome constant `179971179971`
+  469 - Affects genesis hash
+  470 - For specialized harmonic research
+  471 
+  472 ### Register Conventions
+  473 
+  474 While the VM has no formal registers, common cell usage patterns:
+  475 
+  476 - **Cells 0-9**: Working registers (scratch space)
+  477 - **Cells 10-20**: Input parameters
+  478 - **Cells 21-30**: Output results
+  479 - **Cells 31-62**: Algorithm workspace
+  480 - **Cells 63-71**: Boundary layer (affected by CLOSE81)
+  481 - **Cells 72-80**: Hidden Lo Shu layer (special closure)
+  482 
+  483 ### Closure Group IDs
+  484 
+  485 The `cg_id` field (0-255) serves multiple purposes:
+  486 
+  487 1. **Energy contribution** to phase transport
+  488 2. **Receipt differentiation** (affects hash chain)
+  489 3. **Semantic grouping** of related operations
+  490 
+  491 **Best practice**: Use consistent `cg_id` for logically related operations.
+  492 
+  493 ### Phase Parameters
+  494 
+  495 The `phase` field (0-255, interpreted mod 72):
+  496 
+  497 1. **Phase rotation** offset for transport
+  498 2. **Instruction-specific** parameters (e.g., GATE_CLOSURE yc encoding)
+  499 3. **Harmonic alignment** with constraint field
+  500 
+  501 ---
+  502 
+  503 ## Receipt and Ledger System
+  504 
+  505 ### Receipt Structure
+  506 
+  507 ```c
+  508 typedef struct {
+  509     char prev_h72[73];        // Previous receipt hash
+  510     char state_h72[73];       // Current state hash (Hash72 projection)
+  511     char receipt_h72[73];     // This receipt's hash
+  512     
+  513     uint8_t cg_id;            // Closure group ID
+  514     uint32_t witness;         // Witness flags
+  515     
+  516     uint64_t step;            // Step number
+  517     uint64_t orbit_period;    // Non-zero if orbit detected
+  518     
+  519     int ledger_advanced;      // 1=advanced, 0=frozen
+  520     
+  521     double identity_residual; // GATE_IDENTITY residual (if applicable)
+  522     int identity_has_data;    // 1 if identity gate executed
+  523 } VMReceipt;
+  524 ```
+  525 
+  526 ### Witness Flags
+  527 
+  528 | Flag | Value | Meaning |
+  529 |------|-------|---------|
+  530 | `W_GATE_APB_PASS` | 0x00001 | APB gate passed |
+  531 | `W_GATE_APB_FAIL` | 0x00002 | APB gate failed |
+  532 | `W_GATE_CLOSURE_PASS` | 0x00004 | Closure gate passed |
+  533 | `W_GATE_CLOSURE_FAIL` | 0x00008 | Closure gate failed |
+  534 | `W_QGU_APPLIED` | 0x00010 | QGU operation executed |
+  535 | `W_NONCOMMUTATIVE` | 0x00020 | MULXY or MULYX executed |
+  536 | `W_CONSTRAINT_FIRED` | 0x00040 | Constraint added |
+  537 | `W_ORBIT_DETECTED` | 0x00080 | State hash recurrence |
+  538 | `W_HALT` | 0x00100 | HALT instruction |
+  539 | `W_SWEEP` | 0x00200 | SWEEP81 executed |
+  540 | `W_CLOSE_TRANSPORT` | 0x00400 | Transport closure detected |
+  541 | `W_CLOSE_ORIENTATION` | 0x00800 | Orientation closure detected |
+  542 | `W_CLOSE_CONSTRAINT` | 0x01000 | Constraint closure detected |
+  543 | `W_CONVERGED` | 0x02000 | All three closures achieved |
+  544 | `W_LEDGER_FROZEN` | 0x04000 | Receipt did not advance ledger |
+  545 | `W_GATE_IDENTITY_PASS` | 0x08000 | Identity gate passed |
+  546 | `W_GATE_IDENTITY_FAIL` | 0x10000 | Identity gate failed |
+  547 | `W_IDENTITY_DEGENERATE` | 0x20000 | Identity gate degenerate input |
+  548 
+  549 ### Ledger-Advancing vs. Ledger-Freezing
+  550 
+  551 **Ledger-Advancing** (most ops):
+  552 - Extends receipt chain
+  553 - `prev_h72` ← previous `receipt_h72`
+  554 - New `state_h72` computed
+  555 - New `receipt_h72 = hash(prev, cg_id, witness, state)`
+  556 - `ledger_advanced = 1`
+  557 
+  558 **Ledger-Freezing** (OP_HALT only):
+  559 - Does NOT extend chain
+  560 - Annotates terminal receipt with witness bits
+  561 - `ledger_advanced = 0`
+  562 - `witness |= W_LEDGER_FROZEN`
+  563 
+  564 ### Hash72 Projection
+  565 
+  566 The `state_h72` is computed as:
+  567 
+  568 ```c
+  569 for (int i = 0; i < 72; i++) {
+  570     uint8_t g = hash72_index(genesis_hash[i]);
+  571     uint8_t h_contrib = 0;
+  572     
+  573     // Lo Shu hidden cells contribute at specific slots
+  574     if (LOSHU_SLOTS[k] == i) {
+  575         h_contrib = wrap72(cells[72+k] + k*7);
+  576     }
+  577     
+  578     uint8_t v = wrap72(cells[i] + g + h_contrib + i*3);
+  579     state_h72[i] = HASH72[v];
+  580 }
+  581 ```
+  582 
+  583 **Key properties**:
+  584 - Includes genesis hash (seed-dependent)
+  585 - Incorporates hidden cells at Lo Shu positions
+  586 - Deterministic given cell state + genesis
+  587 
+  588 ---
+  589 
+  590 ## Closure Conditions
+  591 
+  592 ### Three Closure Classes
+  593 
+  594 #### 1. **Transport Closure** (W_CLOSE_TRANSPORT)
+  595 
+  596 **Condition**: State hash recurrence (orbit detection)
+  597 
+  598 ```c
+  599 if (state_h72 seen before at step S) {
+  600     orbit_period = current_step - S;
+  601     W_CLOSE_TRANSPORT set;
+  602 }
+  603 ```
+  604 
+  605 **Meaning**: System has entered a periodic cycle in state space.
+  606 
+  607 **Orbit table**: Up to 8192 recent states tracked.
+  608 
+  609 #### 2. **Orientation Closure** (W_CLOSE_ORIENTATION)
+  610 
+  611 **Condition**: XYZW balance
+  612 
+  613 ```c
+  614 balance = (xyzw[0] + xyzw[1] - xyzw[2] - xyzw[3]) % 72;
+  615 if (balance == 0) {
+  616     W_CLOSE_ORIENTATION set;
+  617 }
+  618 ```
+  619 
+  620 **Meaning**: Non-commutative operations have balanced.
+  621 
+  622 **Influenced by**: MULXY, MULYX operations.
+  623 
+  624 #### 3. **Constraint Closure** (W_CLOSE_CONSTRAINT)
+  625 
+  626 **Condition**: All constraints below threshold
+  627 
+  628 ```c
+  629 for each active constraint:
+  630     if (strength > CONSTRAINT_CLOSURE_THRESHOLD) {
+  631         return false;
+  632     }
+  633 return true;
+  634 ```
+  635 
+  636 **Threshold**: `CONSTRAINT_CLOSURE_THRESHOLD = 4`
+  637 
+  638 **Meaning**: Constraint field has dissipated below critical energy.
+  639 
+  640 **Influenced by**: CONSTRAIN, RELAX, constraint competition.
+  641 
+  642 ### Joint Convergence (W_CONVERGED)
+  643 
+  644 When all three closures occur simultaneously:
+  645 
+  646 ```c
+  647 if ((witness & W_CLOSE_TRANSPORT) &&
+  648     (witness & W_CLOSE_ORIENTATION) &&
+  649     (witness & W_CLOSE_CONSTRAINT)) {
+  650     witness |= W_CONVERGED;
+  651 }
+  652 ```
+  653 
+  654 **Significance**: System has achieved harmonic equilibrium across all domains.
+  655 
+  656 ### Latched Closure State
+  657 
+  658 ```c
+  659 vm->ever_closed_transport
+  660 vm->ever_closed_orientation
+  661 vm->ever_closed_constraint
+  662 vm->converged
+  663 ```
+  664 
+  665 These flags latch `true` once closure achieved (never reset).
+  666 
+  667 **Use case**: Post-execution analysis to determine if closure was ever reached.
+  668 
+  669 ---
+  670 
+  671 ## Constraint Field System
+  672 
+  673 ### Constraint Structure
+  674 
+  675 ```c
+  676 typedef struct {
+  677     uint8_t type;       // Application-defined type
+  678     uint8_t phase;      // Phase position (0-71)
+  679     uint8_t strength;   // Constraint strength (0-255)
+  680     uint8_t active;     // 1=active, 0=deactivated
+  681     uint64_t lineage;   // Step number when created
+  682 } Constraint72;
+  683 ```
+  684 
+  685 ### Constraint Bias Field
+  686 
+  687 Constraints influence phase transport via a **bias field**:
+  688 
+  689 ```c
+  690 uint8_t constraint_bias_at(VM81 *vm, uint8_t phase) {
+  691     uint32_t acc = 0;
+  692     for each active constraint k:
+  693         dist = min_circular_distance(phase, k.phase);
+  694         if (dist < 6) {
+  695             acc += k.strength * (6 - dist);
+  696         }
+  697     return wrap72(acc);
+  698 }
+  699 ```
+  700 
+  701 **Effect**: Cells near constraint phase receive additional phase shift during transport.
+  702 
+  703 **Range**: 6-cell radius around constraint phase.
+  704 
+  705 ### Constraint Competition
+  706 
+  707 After each instruction, constraints with **reciprocal phases** compete:
+  708 
+  709 ```c
+  710 for each pair of constraints (A, B):
+  711     if (reciprocal_phase(A.phase) == B.phase) {
+  712         min_strength = min(A.strength, B.strength);
+  713         A.strength -= min_strength;
+  714         B.strength -= min_strength;
+  715         // Deactivate if strength reaches 0
+  716     }
+  717 ```
+  718 
+  719 **Result**: Opposing constraints cancel, driving toward constraint closure.
+  720 
+  721 ### Constraint Table Management
+  722 
+  723 - **Capacity**: 64 constraints
+  724 - **Overflow policy**: Replace weakest constraint
+  725 - **Deactivation**: Strength 0 → `active = 0`
+  726 
+  727 ---
+  728 
+  729 ## Advanced Topics
+  730 
+  731 ### Phase Transport Propagation
+  732 
+  733 When an instruction executes (except MULXY/MULYX which do custom transport):
+  734 
+  735 ```c
+  736 propagate_phase_transport(vm, origin, energy, cg_id)
+  737 ```
+  738 
+  739 **Algorithm**:
+  740 
+  741 1. **Origin cell and reciprocal**:
+  742    ```c
+  743    cells[origin] += energy + cg_id + constraint_bias_at(origin);
+  744    cells[reciprocal(origin)] = cells[origin] + 36;
+  745    ```
+  746 
+  747 2. **Radial propagation** (radius 1-5):
+  748    ```c
+  749    for radius = 1 to 5:
+  750        L = origin - radius;
+  751        R = origin + radius;
+  752        cells[L] += energy + cg_id + radius + bias_at(L);
+  753        cells[R] += energy + cg_id + radius + 1 + bias_at(R);
+  754        cells[reciprocal(L/R)] = cells[L/R] + 36;
+  755    ```
+  756 
+  757 3. **Full 72-cell diffusion**:
+  758    ```c
+  759    for i = 0 to 71:
+  760        delta = i - origin;
+  761        h = (energy + cg_id + delta) % 9;
+  762        cells[i] += h;
+  763    ```
+  764 
+  765 4. **Hidden cell perturbation**:
+  766    ```c
+  767    for i = 72 to 80:
+  768        t = (energy + cg_id + i + origin) % 72;
+  769        cells[i] += t % 5;
+  770    ```
+  771 
+  772 **Result**: Energy propagates non-uniformly across grid, influenced by constraint field.
+  773 
+  774 ### XYZW State Tracking
+  775 
+  776 XYZW tracks non-commutative operation history:
+  777 
+  778 #### **MULXY** update:
+  779 ```c
+  780 xyzw[0] = wrap72(xyzw[0] + a);
+  781 xyzw[1] = wrap72(xyzw[1] + b);
+  782 xyzw[2] = wrap72(xyzw[2] + (xyzw[0] ^ xyzw[1]));
+  783 xyzw[3] = wrap72(xyzw[0] + xyzw[1] - xyzw[2]);
+  784 ```
+  785 
+  786 #### **MULYX** update:
+  787 ```c
+  788 xyzw[1] = wrap72(xyzw[1] + a);  // Swapped!
+  789 xyzw[0] = wrap72(xyzw[0] + b);  // Swapped!
+  790 xyzw[2] = wrap72(xyzw[2] + (xyzw[0] ^ xyzw[1]));
+  791 xyzw[3] = wrap72(xyzw[0] + xyzw[1] - xyzw[2]);
+  792 ```
+  793 
+  794 **Orientation closure** requires: `xyzw[0] + xyzw[1] = xyzw[2] + xyzw[3] (mod 72)`
+  795 
+  796 ### Polarity Calculation
+  797 
+  798 Used by QBRANCH:
+  799 
+  800 ```c
+  801 uint8_t polarity = (cell_value / 18) & 3;
+  802 ```
+  803 
+  804 **Range**: 0-3 (4 polarities)
+  805 
+  806 **Mapping**:
+  807 - 0-17: polarity 0
+  808 - 18-35: polarity 1
+  809 - 36-53: polarity 2
+  810 - 54-71: polarity 3
+  811 
+  812 ### Genesis Hash
+  813 
+  814 The genesis hash is seed-dependent and influences all state projections:
+  815 
+  816 ```c
+  817 for (int i = 0; i < 72; i++) {
+  818     uint64_t x = (i * 11400714819323198485ULL) ^ (mixer + i * 0xC2B2AE3D27D4EB4FULL);
+  819     if (mode == SEED_PALINDROME) x ^= PALINDROME_SEED * (i + 1);
+  820     genesis_hash[i] = HASH72[x % 72];
+  821 }
+  822 ```
+  823 
+  824 **Immutable**: Set at initialization, never changes.
+  825 
+  826 **Purpose**: Ensures different seeds produce different hash chains even for identical cell states.
+  827 
+  828 ---
+  829 
+  830 ## Example Programs
+  831 
+  832 ### Example 1: Simple Arithmetic
+  833 
+  834 ```c
+  835 // Compute (5 + 7) * 3 and store in cell 10
+  836 
+  837 vm.program_len = 0;
+  838 
+  839 // Load 5 into cell 0
+  840 vm.program[vm.program_len++] = (Instruction){ OP_LOAD, 5, 0, 0, 10, 0 };
+  841 
+  842 // Load 7 into cell 1
+  843 vm.program[vm.program_len++] = (Instruction){ OP_LOAD, 7, 0, 1, 10, 0 };
+  844 
+  845 // Add: cell 2 = cell 0 + cell 1
+  846 vm.program[vm.program_len++] = (Instruction){ OP_ADD, 0, 1, 2, 15, 3 };
+  847 
+  848 // Load 3 into cell 3
+  849 vm.program[vm.program_len++] = (Instruction){ OP_LOAD, 3, 0, 3, 10, 0 };
+  850 
+  851 // Multiply: cell 10 = cell 2 * cell 3 (using MULXY)
+  852 vm.program[vm.program_len++] = (Instruction){ OP_MULXY, 2, 3, 10, 20, 5 };
+  853 
+  854 // Halt
+  855 vm.program[vm.program_len++] = (Instruction){ OP_HALT, 0, 0, 0, 0, 0 };
+  856 
+  857 // Result in vm.cells[10] after execution
+  858 ```
+  859 
+  860 ### Example 2: Constraint-Driven Convergence
+  861 
+  862 ```c
+  863 // Create constraints and relax to closure
+  864 
+  865 vm.program_len = 0;
+  866 
+  867 // Add strong constraint at phase 10
+  868 vm.program[vm.program_len++] = (Instruction){ OP_LOAD, 10, 0, 5, 5, 0 };
+  869 vm.program[vm.program_len++] = (Instruction){ OP_CONSTRAIN, 1, 5, 50, 19, 0 };
+  870 
+  871 // Add opposing constraint at phase 46 (reciprocal of 10)
+  872 vm.program[vm.program_len++] = (Instruction){ OP_LOAD, 46, 0, 6, 5, 0 };
+  873 vm.program[vm.program_len++] = (Instruction){ OP_CONSTRAIN, 1, 6, 50, 19, 0 };
+  874 
+  875 // Loop: relax, sweep, check
+  876 uint64_t loop_start = vm.program_len;
+  877 
+  878 vm.program[vm.program_len++] = (Instruction){ OP_RELAX, 5, 0, 0, 18, 0 };
+  879 vm.program[vm.program_len++] = (Instruction){ OP_SWEEP81, 0, 0, 0, 22, 0 };
+  880 
+  881 // Branch back to loop (will orbit, triggering transport closure)
+  882 vm.program[vm.program_len++] = (Instruction){ OP_BRANCH, loop_start, 0, 0, 10, 0 };
+  883 
+  884 // Run with --halt-on-orbit to stop at orbit detection
+  885 ```
+  886 
+  887 ### Example 3: Gate Verification Chain
+  888 
+  889 ```c
+  890 // Initialize test values
+  891 vm.cells[10] = 36;  // x
+  892 vm.cells[11] = 36;  // y (equal for APB gate)
+  893 vm.cells[12] = 36;  // z
+  894 vm.cells[20] = 40;  // u for identity gate
+  895 
+  896 vm.program_len = 0;
+  897 
+  898 // Test APB gate (should pass: 36 = 36 = 36)
+  899 vm.program[vm.program_len++] = (Instruction){ OP_GATE_APB, 10, 11, 12, 17, 0 };
+  900 
+  901 // Test Identity gate
+  902 vm.program[vm.program_len++] = (Instruction){ OP_GATE_IDENTITY, 10, 11, 20, 25, 0 };
+  903 
+  904 // Conditional branch based on polarity of result
+  905 vm.program[vm.program_len++] = (Instruction){ OP_QBRANCH, 10, 0, 0, 30, 0 };
+  906 
+  907 // ... program continues based on polarity
+  908 
+  909 vm.program[vm.program_len++] = (Instruction){ OP_HALT, 0, 0, 0, 0, 0 };
+  910 ```
+  911 
+  912 ### Example 4: Orbit Search
+  913 
+  914 ```c
+  915 // Search for orbit via random walk
+  916 
+  917 vm.program_len = 0;
+  918 
+  919 uint64_t loop = vm.program_len;
+  920 
+  921 // Add cells 0 and 1, store in 2
+  922 vm.program[vm.program_len++] = (Instruction){ OP_ADD, 0, 1, 2, 10, 3 };
+  923 
+  924 // XOR cells 2 and 3, store in 0
+  925 vm.program[vm.program_len++] = (Instruction){ OP_XOR, 2, 3, 0, 12, 7 };
+  926 
+  927 // Rotate cell 1 by phase 17
+  928 vm.program[vm.program_len++] = (Instruction){ OP_ROT, 1, 0, 1, 8, 17 };
+  929 
+  930 // Sweep the grid
+  931 vm.program[vm.program_len++] = (Instruction){ OP_SWEEP81, 0, 0, 0, 22, 0 };
+  932 
+  933 // Branch back
+  934 vm.program[vm.program_len++] = (Instruction){ OP_BRANCH, loop, 0, 0, 5, 0 };
+  935 
+  936 // Run until orbit detected (--halt-on-orbit)
+  937 // Orbit period will be in vm.last_receipt.orbit_period
+  938 ```
+  939 
+  940 ### Example 5: QGU Sequence
+  941 
+  942 ```c
+  943 // Apply QGU delta repeatedly
+  944 
+  945 vm.cells[0] = 10;  // q
+  946 vm.cells[1] = 5;   // c
+  947 vm.cells[2] = 3;   // d (via cg_id reference)
+  948 vm.cells[10] = 0;  // accumulator
+  949 
+  950 vm.program_len = 0;
+  951 
+  952 for (int i = 0; i < 10; i++) {
+  953     // QGU: cell[10] += delta(cells[0], cells[1], cells[2])
+  954     vm.program[vm.program_len++] = (Instruction){ OP_QGU, 0, 1, 10, 2, 11 };
+  955     
+  956     // Rotate q
+  957     vm.program[vm.program_len++] = (Instruction){ OP_ROT, 0, 0, 0, 5, 7 };
+  958 }
+  959 
+  960 vm.program[vm.program_len++] = (Instruction){ OP_HALT, 0, 0, 0, 0, 0 };
+  961 
+  962 // vm.cells[10] contains accumulated QGU deltas
+  963 ```
+  964 
+  965 ---
+  966 
+  967 ## Best Practices
+  968 
+  969 ### 1. Seed Selection
+  970 
+  971 - **Use SEED_LOSHU** for most applications (provides Lo Shu structure)
+  972 - **Use SEED_PALINDROME** for harmonic symmetry research
+  973 - **Document seed values** for reproducible results
+  974 
+  975 ### 2. Closure Group IDs
+  976 
+  977 - **Group related ops** with same `cg_id`
+  978 - **Use distinct ranges** for different algorithm phases:
+  979   - 0-9: Initialization
+  980   - 10-19: Main computation
+  981   - 20-29: Convergence testing
+  982   - 30-39: Cleanup
+  983 
+  984 ### 3. Phase Parameters
+  985 
+  986 - **Align phases** with constraint field for predictable behavior
+  987 - **Use reciprocal phases** (p and p+36) for symmetry
+  988 - **Avoid phase 0** when testing for special conditions
+  989 
+  990 ### 4. Memory Layout
+  991 
+  992 ```
+  993 Cells 0-9:    Scratch/working registers
+  994 Cells 10-20:  Input parameters
+  995 Cells 21-30:  Output results
+  996 Cells 31-62:  Algorithm workspace
+  997 Cells 63-71:  Boundary (CLOSE81 sensitive)
+  998 Cells 72-80:Hidden (Lo Shu, read-only in most contexts)
+  999 ```
+ 1000 
+ 1001 ### 5. Constraint Management
+ 1002 
+ 1003 - **Start with high strength** (50+) for significant constraints
+ 1004 - **Use RELAX strategically** to drive toward closure
+ 1005 - **Monitor constraint_count** to avoid table exhaustion
+ 1006 - **Reciprocal constraints** for balanced field dynamics
+ 1007 
+ 1008 ### 6. Loop Detection
+ 1009 
+ 1010 - **Backwards branches** increment sweep counter
+ 1011 - **Use --halt-on-orbit** to catch transport closure
+ 1012 - **Check orbit_period** in receipt for cycle length
+ 1013 
+ 1014 ### 7. Receipt Verification
+ 1015 
+ 1016 After execution:
+ 1017 
+ 1018 ```c
+ 1019 // Check closure achievement
+ 1020 if (vm.last_receipt.witness & W_CONVERGED) {
+ 1021     printf("CONVERGED: All closures achieved\n");
+ 1022 }
+ 1023 
+ 1024 // Check orbit
+ 1025 if (vm.last_receipt.orbit_period > 0) {
+ 1026     printf("ORBIT: Period %llu\n", vm.last_receipt.orbit_period);
+ 1027 }
+ 1028 
+ 1029 // Check identity gate
+ 1030 if (vm.last_receipt.identity_has_data) {
+ 1031     printf("IDENTITY residual: %.3e\n", vm.last_receipt.identity_residual);
+ 1032 }
+ 1033 ```
+ 1034 
+ 1035 ### 8. Debugging
+ 1036 
+ 1037 **Enable trace mode**:
+ 1038 ```bash
+ 1039 ./hhs_vm81 --trace
+ 1040 ```
+ 1041 
+ 1042 **Output per step**:
+ 1043 - Step number, PC, constraint count
+ 1044 - Closure group ID
+ 1045 - Previous/state/receipt hashes
+ 1046 - Witness flags
+ 1047 - XYZW balance
+ 1048 - Identity residual (if applicable)
+ 1049 - Orbit period (if detected)
+ 1050 
+ 1051 ### 9. Testing Gates
+ 1052 
+ 1053 **GATE_APB**:
+ 1054 - Initialize test cells to same value for pass
+ 1055 - Use for phase synchronization verification
+ 1056 
+ 1057 **GATE_CLOSURE**:
+ 1058 - Requires careful setup of P, p, q, n, x, y cells
+ 1059 - Test mathematical invariants
+ 1060 
+ 1061 **GATE_IDENTITY**:
+ 1062 - Avoid degenerate inputs (x=0, y=0, u=0)
+ 1063 - Expect identity_residual < 1e-6 for pass
+ 1064 - Check `identity_has_data` flag before reading residual
+ 1065 
+ 1066 ### 10. Performance Considerations
+ 1067 
+ 1068 - **MAX_STEPS**: Default 1M (2^20), adjust for long searches
+ 1069 - **Orbit table**: 8192 entries, older states evicted
+ 1070 - **Constraint competition**: O(n²) per step, minimize constraint count
+ 1071 - **Phase transport**: Full grid sweep, expensive for tight loops
+ 1072 
+ 1073 ---
+ 1074 
+ 1075 ## Appendices
+ 1076 
+ 1077 ### Appendix A: Complete Opcode Table
+ 1078 
+ 1079 | Opcode | Name | Params | Ledger | Energy | Notes |
+ 1080 |--------|------|--------|--------|--------|-------|
+ 1081 | 0 | NOP | - | YES | cg_id | No-op |
+ 1082 | 1 | ADD | a,b→c | YES | c | Arithmetic add |
+ 1083 | 2 | SUB | a,b→c | YES | c | Arithmetic sub |
+ 1084 | 3 | ROT | a→c | YES | c | Phase rotate |
+ 1085 | 4 | XOR | a,b→c | YES | c | Bitwise XOR |
+ 1086 | 5 | AND | a,b→c | YES | c | Bitwise AND |
+ 1087 | 6 | OR | a,b→c | YES | c | Bitwise OR |
+ 1088 | 7 | LOAD | imm→c | YES | c | Load immediate |
+ 1089 | 8 | STORE | a→c | YES | c | Store value |
+ 1090 | 9 | BRANCH | tgt | YES | cg_id | Unconditional jump |
+ 1091 | 10 | BZ | a,tgt | YES | cg_id | Branch if zero |
+ 1092 | 11 | BNZ | a,tgt | YES | cg_id | Branch if nonzero |
+ 1093 | 12 | MULXY | a,b→c | YES | c | Multiply XY order |
+ 1094 | 13 | MULYX | a,b→c | YES | c | Multiply YX order |
+ 1095 | 14 | QGU | q,c,d→r | YES | r | Quantum gate update |
+ 1096 | 15 | GATE_APB | a,p,b | YES | cg_id±36 | A=P=B test |
+ 1097 | 16 | GATE_CLOSURE | P,p,q,n,x,y | YES | cg_id±48 | Closure equation |
+ 1098 | 17 | GATE_IDENTITY | x,y,u | YES | cg_id±24 | Log identity test |
+ 1099 | 18 | QBRANCH | a | YES | cg_id+pol*9 | Polarity branch |
+ 1100 | 19 | CONSTRAIN | t,p,s | YES | cg_id+s | Add constraint |
+ 1101 | 20 | RELAX | amt | YES | cg_id+1 | Weaken constraints |
+ 1102 | 21 | SWEEP81 | - | YES | cg_id | Grid sweep |
+ 1103 | 22 | CLOSE81 | - | YES | cg_id | Lo Shu closure |
+ 1104 | 23 | HALT | - | NO | - | Freeze ledger |
+ 1105 
+ 1106 ### Appendix B: Lo Shu Magic Square
+ 1107 
+ 1108 ```
+ 1109 4  9  2
+ 1110 3  5  7
+ 1111 8  1  6
+ 1112 ```
+ 1113 
+ 1114 **Properties**:
+ 1115 - All rows sum to 15
+ 1116 - All columns sum to 15
+ 1117 - Both diagonals sum to 15
+ 1118 
+ 1119 **Slot mapping** (hidden cells 72-80):
+ 1120 ```
+ 1121 cells[72] = 4*8-1 = 31  (slot 31)
+ 1122 cells[73] = 9*8-1 = 71  (slot 71)
+ 1123 cells[74] = 2*8-1 = 15  (slot 15)
+ 1124 cells[75] = 3*8-1 = 23  (slot 23)
+ 1125 cells[76] = 5*8-1 = 39  (slot 39)
+ 1126 cells[77] = 7*8-1 = 55  (slot 55)
+ 1127 cells[78] = 8*8-1 = 63  (slot 63)
+ 1128 cells[79] = 1*8-1 = 7   (slot 7)
+ 1129 cells[80] = 6*8-1 = 47  (slot 47)
+ 1130 ```
+ 1131 
+ 1132 These cells contribute to state hash at their respective slots.
+ 1133 
+ 1134 ### Appendix C: Witness Flag Quick Reference
+ 1135 
+ 1136 ```c
+ 1137 W_GATE_APB_PASS        0x00001  // APB gate succeeded
+ 1138 W_GATE_APB_FAIL        0x00002  // APB gate failed
+ 1139 W_GATE_CLOSURE_PASS    0x00004  // Closure gate succeeded
+ 1140 W_GATE_CLOSURE_FAIL    0x00008  // Closure gate failed
+ 1141 W_QGU_APPLIED          0x00010  // QGU executed
+ 1142 W_NONCOMMUTATIVE       0x00020  // MULXY/MULYX executed
+ 1143 W_CONSTRAINT_FIRED     0x00040  // Constraint added
+ 1144 W_ORBIT_DETECTED       0x00080  // State recurrence
+ 1145 W_HALT                 0x00100  // Halt instruction
+ 1146 W_SWEEP                0x00200  // SWEEP81 executed
+ 1147 W_CLOSE_TRANSPORT      0x00400  // Transport closure
+ 1148 W_CLOSE_ORIENTATION    0x00800  // Orientation closure
+ 1149 W_CLOSE_CONSTRAINT     0x01000  // Constraint closure
+ 1150 W_CONVERGED            0x02000  // Joint closure
+ 1151 W_LEDGER_FROZEN        0x04000  // Receipt frozen
+ 1152 W_GATE_IDENTITY_PASS   0x08000  // Identity gate passed
+ 1153 W_GATE_IDENTITY_FAIL   0x10000  // Identity gate failed
+ 1154 W_IDENTITY_DEGENERATE  0x20000  // Identity degenerate
+ 1155 ```
+ 1156 
+ 1157 ### Appendix D: Command-Line Reference
+ 1158 
+ 1159 ```bash
+ 1160 # Basic execution
+ 1161 ./hhs_vm81
+ 1162 
+ 1163 # With trace output
+ 1164 ./hhs_vm81 --trace
+ 1165 
+ 1166 # Custom step limit
+ 1167 ./hhs_vm81 --steps 1000
+ 1168 
+ 1169 # Custom seed
+ 1170 ./hhs_vm81 --seed 12345
+ 1171 
+ 1172 # Palindrome mode
+ 1173 ./hhs_vm81 --palindrome
+ 1174 
+ 1175 # Halt on orbit detection
+ 1176 ./hhs_vm81 --halt-on-orbit
+ 1177 
+ 1178 # Verification mode (extended checks)
+ 1179 ./hhs_vm81 --verify
+ 1180 
+ 1181 # Disable trace
+ 1182 ./hhs_vm81 --no-trace
+ 1183 
+ 1184 # Combined
+ 1185 ./hhs_vm81 --seed 42 --palindrome --halt-on-orbit --verify --trace
+ 1186 ```
+ 1187 
+ 1188 ### Appendix E: Error Conditions
+ 1189 
+ 1190 | Condition | Behavior | Detection |
+ 1191 |-----------|----------|-----------|
+ 1192 | PC >= program_len | HALT (implicit terminal) | Auto |
+ 1193 | Branch target >= program_len | HALT | Auto |
+ 1194 | Division by zero (IR layer) | Return 0, halt frame | Runtime |
+ 1195 | Constraint table full | Replace weakest | Auto |
+ 1196 | Orbit table full | Evict old entries | Auto |
+ 1197 | Stack overflow (IR layer) | Return 0, halt frame | Runtime |
+ 1198 | Identity degenerate input | W_IDENTITY_DEGENERATE | Auto |
+ 1199 
+ 1200 ### Appendix F: Mathematical Foundations
+ 1201 
+ 1202 #### QGU Delta Function
+ 1203 
+ 1204 ```
+ 1205 δ(q, c, d) = (c·q² + d·q⁴) mod 72
+ 1206 ```
+ 1207 
+ 1208 **Use case**: Quantum-inspired phase perturbation.
+ 1209 
+ 1210 #### Closure Equation (GATE_CLOSURE)
+ 1211 
+ 1212 ```
+ 1213 P² - pq = n⁴ = xy  (all mod 72)
+ 1214 ```
+ 1215 
+ 1216 **Mathematical invariant** for harmonic closure.
+ 1217 
+ 1218 #### Identity Gate Equations
+ 1219 
+ 1220 ```
+ 1221 A = (x/y) · (y/x)                    // Multiplicative symmetry
+ 1222 B = (-xy)^((x²+y)(y²+x)/4)          // Exponential form
+ 1223 C = e^(xπ - 144·ln|u|) · 4π         // Transcendental form
+ 1224 ```
+ 1225 
+ 1226 **Test**: `|log A - log B| < ε` ∧ `|log B - log C| < ε` ∧ `|log A - log C| < ε`
+ 1227 
+ 1228 **Tolerance**: ε = 1×10⁻⁶
+ 1229 
+ 1230 #### Phase Transport Reciprocity
+ 1231 
+ 1232 For any phase p:
+ 1233 ```
+ 1234 reciprocal(p) = (p + 36) mod 72
+ 1235 ```
+ 1236 
+ 1237 **Property**: Forms antipodal pairs on 72-cycle.
+ 1238 
+ 1239 #### Constraint Bias Field
+ 1240 
+ 1241 For constraint at phase p₀ with strength s:
+ 1242 ```
+ 1243 bias(p) = s · max(0, 6 - distance(p, p₀))  where distance is circular
+ 1244 ```
+ 1245 
+ 1246 **Range**: 6-cell radius, linear falloff.
+ 1247 
+ 1248 #### XYZW Balance Invariant
+ 1249 
+ 1250 Orientation closure requires:
+ 1251 ```
+ 1252 x + y ≡ z + w  (mod 72)
+ 1253 ```
+ 1254 
+ 1255 Achieved through balanced MULXY/MULYX usage.
+ 1256 
+ 1257 ---
+ 1258 
+ 1259 ## Revision History
+ 1260 
+ 1261 | Version | Date | Changes |
+ 1262 |---------|------|---------|
+ 1263 | v7.2 | 2024 | Canonical freeze: receipt system, three closure classes |
+ 1264 | v8.0 | 2025 | Identity gate addition, layered tensor extensions |
+ 1265 | v8.1 | 2025 | IR bridge layer, Python integration stubs |
+ 1266 
+ 1267 ---
+ 1268 
+ 1269 ## License and Credits
+ 1270 
+ 1271 **HARMONICODE / HHS Substrate Runtime**  
+ 1272 Canonical Freeze Policy: v7.2 receipt/closure semantics locked.  
+ 1273 Extensions layered non-destructively.
+ 1274 
+ 1275 For technical support: [Contact development team]
+ 1276 
+ 1277 ---
+ 1278 
+ 1279 **END OF DOCUMENT**
