from .runtime_base import RuntimeBaseMixin
from .runtime_commit import RuntimeCommitMixin
from .runtime_reduce import RuntimeReduceMixin


class GCMSLRuntime(RuntimeReduceMixin, RuntimeCommitMixin, RuntimeBaseMixin):
    pass
