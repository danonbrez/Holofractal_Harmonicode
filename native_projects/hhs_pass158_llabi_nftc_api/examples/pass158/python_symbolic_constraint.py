from hhs_pass158 import Context, ExactRational, HHS158_OP_BIND_EQ

with Context() as context:
    definition, _ = context.register_definition(
        name="PYTHON_SYMBOLIC_EXAMPLE",
        constraints="A==B;O!=Pi;Delta=P^2-pq",
        symbols="A,B,O,Pi,Delta,P,p,q,x",
        shape=(9, 9),
    )
    instance, _ = definition.instantiate(b"python-symbolic-example")
    instance.bind_rational("x", ExactRational(1, 3))
    print(instance.validate())
    capability = instance.capability(commit=True)
    result, receipt = instance.execute(capability, [(HHS158_OP_BIND_EQ, "A,B")])
    print(result)
    print(receipt.replay())
