# Bounded Product Repair Execution — Pass 076

Pass 076 implements product-local repair as a constrained Runtime transaction.

## Admission requirements

- valid failed test evidence;
- valid bounded healing plan;
- product-local target under `native_projects/`;
- no frozen foundation path;
- exact pre-artifact root;
- bounded exact replacement operations;
- role contract, task assignment, and capability lease;
- post-freeze alignment admission;
- mandatory rollback capsule.

## Atomic postcondition

A candidate repair becomes a committed product artifact only when the repaired source:

```text
parses
AND validates
AND lowers
AND executes
AND closes required invariants
```

If any postcondition fails, the repair transaction is witnessed as rejected and the candidate source artifact is not admitted.

Rollback does not delete the repair. It creates a new source artifact whose parent is the repaired artifact and whose content reconstructs the pre-repair state.

```text
repair transaction root: 0000000000000000000000000000003tKbMA50KXgYg-0=MqGMhlhO9uuxJnYzg2ps/fbLda
rollback capsule root:   0000000000000000000000000000004JpwCqDT=Zo/Ic)hKbeHs/i3>xG-vfP(3lS/k=*6K3
```
