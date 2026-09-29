"""HHS-native pytest-compatible provider.

This module implements the authoritative HHS test-provider path without importing
or spawning upstream pytest.  It preserves a practical pytest-compatible ingress
surface for repository tests while producing deterministic proof/replay receipts.

Upstream pytest may still be used as a differential oracle outside the
authoritative provider path.
"""
from __future__ import annotations

import argparse
import asyncio
import contextlib
import dataclasses
import hashlib
import importlib
import importlib.util
import inspect
import io
import itertools
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
import traceback
import types
from typing import Any, Callable, Iterable, Iterator, Mapping, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72

VERSION = "HHS-P220-I062-NATIVE-PYTEST-PROVIDER-V1"
SCHEMA = "HHS_PASS_220_I062_NATIVE_PYTEST_PROVIDER_V1"
PROVIDER_ID = "provider:hhs.native.pytest"
OUTCOMES = ("PASS", "FAIL", "ERROR", "SKIP", "XFAIL", "XPASS")
EXIT_OK = 0
EXIT_TESTS_FAILED = 1
EXIT_COLLECTION_ERROR = 2
EXIT_INTERNAL_ERROR = 3
EXIT_USAGE_ERROR = 4
EXIT_NO_TESTS = 5


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _hash72(label: str, value: Any) -> str:
    digest = hash72_digest({"domain": VERSION, "label": label}, _canonical(value))
    if not validate_hash72(digest):
        raise RuntimeError(f"I062_INVALID_HASH72:{label}")
    return digest


class NativePytestError(RuntimeError):
    pass


class NativePytestUsageError(NativePytestError):
    pass


class _SkipSignal(Exception):
    pass


class _XFailSignal(Exception):
    pass


@dataclasses.dataclass(frozen=True)
class _MarkSpec:
    name: str
    args: tuple[Any, ...] = ()
    kwargs: Mapping[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True)
class _ParamValue:
    values: tuple[Any, ...]
    marks: tuple[_MarkSpec, ...] = ()
    id: str | None = None


@dataclasses.dataclass(frozen=True)
class _ParametrizeSpec:
    argnames: tuple[str, ...]
    values: tuple[_ParamValue, ...]


@dataclasses.dataclass(frozen=True)
class _FixtureMeta:
    scope: str = "function"
    autouse: bool = False
    name: str | None = None


@dataclasses.dataclass
class NativeTestCase:
    path: Path
    module: types.ModuleType
    function: Callable[..., Any]
    nodeid: str
    class_type: type[Any] | None = None
    method_name: str | None = None
    params: dict[str, Any] = dataclasses.field(default_factory=dict)
    marks: tuple[_MarkSpec, ...] = ()
    fixture_defs: Mapping[str, Callable[..., Any]] = dataclasses.field(default_factory=dict)
    source_sha256: str = ""


@dataclasses.dataclass(frozen=True)
class NativeTestResult:
    nodeid: str
    outcome: str
    duration_ns: int
    error_type: str | None = None
    error_message: str | None = None
    traceback: str | None = None
    stdout: str = ""
    stderr: str = ""
    xfail_strict: bool = False

    def identity_dict(self) -> dict[str, Any]:
        return {
            "nodeid": self.nodeid,
            "outcome": self.outcome,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "xfail_strict": self.xfail_strict,
        }


@dataclasses.dataclass(frozen=True)
class NativePytestRun:
    schema: str
    provider_id: str
    version: str
    root: str
    collected: int
    selected: int
    results: tuple[NativeTestResult, ...]
    collection_errors: tuple[str, ...]
    config_hash72: str
    collection_hash72: str
    result_hash72: str
    receipt_hash216: str
    exit_code: int
    authority: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "provider_id": self.provider_id,
            "version": self.version,
            "root": self.root,
            "collected": self.collected,
            "selected": self.selected,
            "results": [dataclasses.asdict(item) for item in self.results],
            "collection_errors": list(self.collection_errors),
            "config_hash72": self.config_hash72,
            "collection_hash72": self.collection_hash72,
            "result_hash72": self.result_hash72,
            "receipt_hash216": self.receipt_hash216,
            "exit_code": self.exit_code,
            "authority": dict(self.authority),
        }


def _attach_mark(obj: Any, mark: _MarkSpec) -> Any:
    marks = list(getattr(obj, "__hhs_pytest_marks__", ()))
    marks.append(mark)
    setattr(obj, "__hhs_pytest_marks__", tuple(marks))
    return obj


class _MarkDecorator:
    def __init__(
        self,
        name: str,
        args: tuple[Any, ...] = (),
        kwargs: Mapping[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.args = args
        self.kwargs = dict(kwargs or {})

    @property
    def spec(self) -> _MarkSpec:
        return _MarkSpec(self.name, self.args, self.kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if (
            len(args) == 1
            and callable(args[0])
            and not kwargs
            and not self.args
            and not self.kwargs
        ):
            return _attach_mark(args[0], self.spec)
        return _MarkDecorator(self.name, tuple(args), kwargs)

    def decorate(self, obj: Any) -> Any:
        return _attach_mark(obj, self.spec)


class _ParametrizeDecorator:
    def __init__(
        self,
        argnames: str | Sequence[str],
        argvalues: Sequence[Any],
        ids: Sequence[str] | Callable[[Any], str] | None = None,
    ) -> None:
        if isinstance(argnames, str):
            names = tuple(part.strip() for part in argnames.split(",") if part.strip())
        else:
            names = tuple(str(part).strip() for part in argnames)
        if not names:
            raise NativePytestUsageError("I062_PARAMETRIZE_EMPTY_ARGNAMES")
        values: list[_ParamValue] = []
        for index, raw in enumerate(argvalues):
            if isinstance(raw, _ParamValue):
                item = raw
            else:
                if len(names) == 1:
                    tuple_values = (raw,)
                elif isinstance(raw, (tuple, list)):
                    tuple_values = tuple(raw)
                else:
                    raise NativePytestUsageError(
                        f"I062_PARAMETRIZE_ARITY:{','.join(names)}:{index}"
                    )
                item = _ParamValue(tuple_values)
            if len(item.values) != len(names):
                raise NativePytestUsageError(
                    f"I062_PARAMETRIZE_ARITY:{','.join(names)}:{index}"
                )
            if item.id is None and ids is not None:
                if callable(ids):
                    generated = ids(item.values[0] if len(item.values) == 1 else item.values)
                else:
                    generated = ids[index]
                item = dataclasses.replace(item, id=str(generated))
            values.append(item)
        self.spec = _ParametrizeSpec(names, tuple(values))

    def __call__(self, obj: Any) -> Any:
        specs = list(getattr(obj, "__hhs_pytest_parametrize__", ()))
        specs.append(self.spec)
        setattr(obj, "__hhs_pytest_parametrize__", tuple(specs))
        return obj


class _MarkFactory:
    def __getattr__(self, name: str) -> Any:
        if name == "parametrize":
            def parametrize(
                argnames: str | Sequence[str],
                argvalues: Sequence[Any],
                *,
                ids: Sequence[str] | Callable[[Any], str] | None = None,
                **kwargs: Any,
            ) -> _ParametrizeDecorator:
                unsupported = set(kwargs) - {"scope", "indirect"}
                if unsupported:
                    raise NativePytestUsageError(
                        "I062_PARAMETRIZE_UNSUPPORTED:" + ",".join(sorted(unsupported))
                    )
                if kwargs.get("indirect"):
                    raise NativePytestUsageError("I062_INDIRECT_PARAMETRIZE_NOT_ADMITTED")
                return _ParametrizeDecorator(argnames, argvalues, ids=ids)
            return parametrize
        return _MarkDecorator(name)


def _fixture(
    function: Callable[..., Any] | None = None,
    *,
    scope: str = "function",
    autouse: bool = False,
    name: str | None = None,
    params: Sequence[Any] | None = None,
    ids: Sequence[str] | None = None,
) -> Any:
    if params is not None or ids is not None:
        raise NativePytestUsageError("I062_PARAMETRIZED_FIXTURE_NOT_ADMITTED")
    if scope not in {"function", "class", "module", "session"}:
        raise NativePytestUsageError(f"I062_FIXTURE_SCOPE:{scope}")

    def decorate(func: Callable[..., Any]) -> Callable[..., Any]:
        setattr(func, "__hhs_pytest_fixture__", _FixtureMeta(scope, bool(autouse), name))
        return func

    return decorate(function) if function is not None else decorate


def _param(*values: Any, marks: Any = (), id: str | None = None) -> _ParamValue:
    if marks is None:
        normalized: tuple[_MarkSpec, ...] = ()
    else:
        raw_marks = marks if isinstance(marks, (tuple, list)) else (marks,)
        converted: list[_MarkSpec] = []
        for mark in raw_marks:
            if isinstance(mark, _MarkSpec):
                converted.append(mark)
            elif isinstance(mark, _MarkDecorator):
                converted.append(mark.spec)
            else:
                raise NativePytestUsageError("I062_PARAM_MARK_INVALID")
        normalized = tuple(converted)
    return _ParamValue(tuple(values), normalized, id)


class _RaisesContext:
    def __init__(
        self,
        expected: type[BaseException] | tuple[type[BaseException], ...],
        *,
        match: str | None = None,
    ) -> None:
        self.expected = expected
        self.match = match
        self.value: BaseException | None = None
        self.type: type[BaseException] | None = None

    def __enter__(self) -> "_RaisesContext":
        return self

    def __exit__(self, typ: Any, value: Any, tb: Any) -> bool:
        if typ is None:
            raise AssertionError(f"DID_NOT_RAISE:{self.expected}")
        if not issubclass(typ, self.expected):
            return False
        if self.match is not None and re.search(self.match, str(value)) is None:
            raise AssertionError(
                f"RAISES_MATCH_FAILED:{self.match!r}:{str(value)!r}"
            )
        self.value = value
        self.type = typ
        return True


def _raises(
    expected: type[BaseException] | tuple[type[BaseException], ...],
    *args: Any,
    match: str | None = None,
    **kwargs: Any,
) -> Any:
    if args:
        func, *rest = args
        with _RaisesContext(expected, match=match):
            return func(*rest, **kwargs)
    if kwargs:
        raise NativePytestUsageError("I062_RAISES_CALL_KWARGS_WITHOUT_FUNCTION")
    return _RaisesContext(expected, match=match)


class _Approx:
    def __init__(
        self,
        expected: Any,
        *,
        rel: float | None = 1e-6,
        abs: float | None = 1e-12,
        nan_ok: bool = False,
    ) -> None:
        self.expected = expected
        self.rel = rel
        self.abs = abs
        self.nan_ok = nan_ok

    def _scalar(self, actual: Any, expected: Any) -> bool:
        if actual == expected:
            return True
        try:
            a = float(actual)
            e = float(expected)
        except (TypeError, ValueError):
            return False
        if self.nan_ok and a != a and e != e:
            return True
        delta = builtins_abs(a - e)
        absolute = 0.0 if self.abs is None else float(self.abs)
        relative = 0.0 if self.rel is None else float(self.rel) * builtins_abs(e)
        return delta <= max(absolute, relative)

    def __eq__(self, actual: Any) -> bool:
        if isinstance(self.expected, Mapping) and isinstance(actual, Mapping):
            return (
                self.expected.keys() == actual.keys()
                and all(self._scalar(actual[key], value) for key, value in self.expected.items())
            )
        if isinstance(self.expected, (tuple, list)) and isinstance(actual, (tuple, list)):
            return len(self.expected) == len(actual) and all(
                self._scalar(a, e) for a, e in zip(actual, self.expected)
            )
        return self._scalar(actual, self.expected)


builtins_abs = abs


def _approx(
    expected: Any,
    rel: float | None = 1e-6,
    abs: float | None = 1e-12,
    nan_ok: bool = False,
) -> _Approx:
    return _Approx(expected, rel=rel, abs=abs, nan_ok=nan_ok)


class MonkeyPatch:
    def __init__(self) -> None:
        self._undo: list[Callable[[], None]] = []

    def setattr(
        self,
        target: Any,
        name: str | Any,
        value: Any = dataclasses.MISSING,
        raising: bool = True,
    ) -> None:
        if isinstance(target, str):
            module_name, attr = target.rsplit(".", 1)
            object_target = importlib.import_module(module_name)
            new_value = name
            name = attr
        else:
            object_target = target
            if value is dataclasses.MISSING:
                raise TypeError("setattr target/name/value required")
            new_value = value
        existed = hasattr(object_target, str(name))
        if raising and not existed:
            raise AttributeError(str(name))
        old = getattr(object_target, str(name), dataclasses.MISSING)
        setattr(object_target, str(name), new_value)

        def undo() -> None:
            if old is dataclasses.MISSING:
                try:
                    delattr(object_target, str(name))
                except AttributeError:
                    pass
            else:
                setattr(object_target, str(name), old)
        self._undo.append(undo)

    def delattr(self, target: Any, name: str, raising: bool = True) -> None:
        existed = hasattr(target, name)
        if raising and not existed:
            raise AttributeError(name)
        old = getattr(target, name, dataclasses.MISSING)
        if existed:
            delattr(target, name)

        def undo() -> None:
            if old is not dataclasses.MISSING:
                setattr(target, name, old)
        self._undo.append(undo)

    def setenv(self, name: str, value: str, prepend: str | None = None) -> None:
        old = os.environ.get(name)
        new_value = str(value)
        if prepend is not None and old is not None:
            new_value = new_value + prepend + old
        os.environ[name] = new_value

        def undo() -> None:
            if old is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = old
        self._undo.append(undo)

    def delenv(self, name: str, raising: bool = True) -> None:
        old = os.environ.get(name)
        if raising and old is None:
            raise KeyError(name)
        os.environ.pop(name, None)

        def undo() -> None:
            if old is not None:
                os.environ[name] = old
        self._undo.append(undo)

    def chdir(self, path: str | os.PathLike[str]) -> None:
        old = Path.cwd()
        os.chdir(path)
        self._undo.append(lambda: os.chdir(old))

    def syspath_prepend(self, path: str | os.PathLike[str]) -> None:
        value = str(path)
        sys.path.insert(0, value)

        def undo() -> None:
            try:
                sys.path.remove(value)
            except ValueError:
                pass
        self._undo.append(undo)

    def undo(self) -> None:
        while self._undo:
            self._undo.pop()()


class _CaptureFixture:
    def __init__(self, stdout: io.StringIO, stderr: io.StringIO) -> None:
        self._stdout = stdout
        self._stderr = stderr
        self._out_pos = 0
        self._err_pos = 0

    def readouterr(self) -> Any:
        out = self._stdout.getvalue()[self._out_pos :]
        err = self._stderr.getvalue()[self._err_pos :]
        self._out_pos = len(self._stdout.getvalue())
        self._err_pos = len(self._stderr.getvalue())
        return types.SimpleNamespace(out=out, err=err)


class _TempPathFactory:
    def __init__(self) -> None:
        self._roots: list[tempfile.TemporaryDirectory[str]] = []

    def mktemp(self, basename: str, numbered: bool = True) -> Path:
        root = tempfile.TemporaryDirectory(prefix=f"{basename}-")
        self._roots.append(root)
        return Path(root.name)

    def close(self) -> None:
        while self._roots:
            self._roots.pop().cleanup()


@dataclasses.dataclass
class _Request:
    node: Any
    param: Any = dataclasses.MISSING
    _finalizers: list[Callable[[], None]] = dataclasses.field(default_factory=list)

    def addfinalizer(self, function: Callable[[], None]) -> None:
        self._finalizers.append(function)


def _skip(reason: str = "", *, allow_module_level: bool = False) -> None:
    raise _SkipSignal(reason or "skipped")


def _xfail(reason: str = "") -> None:
    raise _XFailSignal(reason or "xfail")


def _fail(reason: str = "", pytrace: bool = True) -> None:
    raise AssertionError(reason or "pytest.fail")


def _importorskip(
    modname: str,
    minversion: str | None = None,
    reason: str | None = None,
) -> Any:
    try:
        return importlib.import_module(modname)
    except ImportError as exc:
        raise _SkipSignal(reason or f"could not import {modname}") from exc


def _make_pytest_shim() -> types.ModuleType:
    shim = types.ModuleType("pytest")
    shim.__dict__.update(
        {
            "__version__": "hhs-native-i062",
            "mark": _MarkFactory(),
            "fixture": _fixture,
            "param": _param,
            "raises": _raises,
            "approx": _approx,
            "skip": _skip,
            "xfail": _xfail,
            "fail": _fail,
            "importorskip": _importorskip,
            "MonkeyPatch": MonkeyPatch,
        }
    )
    return shim


@contextlib.contextmanager
def _pytest_shim_installed() -> Iterator[None]:
    previous = sys.modules.get("pytest", dataclasses.MISSING)
    sys.modules["pytest"] = _make_pytest_shim()
    try:
        yield
    finally:
        if previous is dataclasses.MISSING:
            sys.modules.pop("pytest", None)
        else:
            sys.modules["pytest"] = previous


def _call_maybe_async(function: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    result = function(*args, **kwargs)
    if inspect.isawaitable(result):
        return asyncio.run(result)
    return result


def _parameter_id(value: Any) -> str:
    if isinstance(value, (str, int, bool)):
        return str(value)
    if value is None:
        return "None"
    return type(value).__name__


def _parameter_sets(function: Callable[..., Any]) -> list[tuple[dict[str, Any], tuple[_MarkSpec, ...], str | None]]:
    specs: tuple[_ParametrizeSpec, ...] = getattr(function, "__hhs_pytest_parametrize__", ())
    combinations: list[tuple[dict[str, Any], tuple[_MarkSpec, ...], list[str]]] = [({}, (), [])]
    for spec in specs:
        expanded: list[tuple[dict[str, Any], tuple[_MarkSpec, ...], list[str]]] = []
        for current, current_marks, current_ids in combinations:
            for item in spec.values:
                values = dict(current)
                values.update(dict(zip(spec.argnames, item.values)))
                pid = item.id or "-".join(_parameter_id(value) for value in item.values)
                expanded.append(
                    (values, current_marks + item.marks, current_ids + [pid])
                )
        combinations = expanded
    return [
        (params, marks, "-".join(ids) if ids else None)
        for params, marks, ids in combinations
    ]


def _path_node(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _iter_test_paths(root: Path, selectors: Sequence[str]) -> list[Path]:
    candidates: set[Path] = set()
    raw = selectors or (".",)
    for selector in raw:
        base = selector.split("::", 1)[0]
        path = Path(base)
        if not path.is_absolute():
            path = root / path
        if path.is_dir():
            for pattern in ("test_*.py", "*_test.py"):
                candidates.update(item for item in path.rglob(pattern) if item.is_file())
        elif path.is_file():
            candidates.add(path)
        else:
            raise NativePytestUsageError(f"I062_SELECTOR_NOT_FOUND:{selector}")
    return sorted(candidates, key=lambda item: item.as_posix())


def _selector_matches(nodeid: str, selectors: Sequence[str], root: Path) -> bool:
    if not selectors:
        return True
    for selector in selectors:
        if "::" not in selector:
            path = Path(selector)
            if not path.is_absolute():
                path = root / path
            if path.is_dir():
                try:
                    Path(root / nodeid.split("::", 1)[0]).resolve().relative_to(path.resolve())
                    return True
                except ValueError:
                    continue
            if nodeid.split("::", 1)[0] == _path_node(root, path):
                return True
        else:
            base, suffix = selector.split("::", 1)
            path = Path(base)
            if not path.is_absolute():
                path = root / path
            prefix = _path_node(root, path) + "::" + suffix
            if nodeid == prefix or nodeid.startswith(prefix + "[") or nodeid.startswith(prefix + "::"):
                return True
    return False


_TOKEN_RE = re.compile(r"\(|\)|\band\b|\bor\b|\bnot\b|[A-Za-z0-9_.:\-/]+")


def _boolean_match(expression: str | None, predicate: Callable[[str], bool]) -> bool:
    if not expression:
        return True
    tokens = _TOKEN_RE.findall(expression)
    if not tokens:
        return True
    position = 0

    def atom() -> bool:
        nonlocal position
        if position >= len(tokens):
            raise NativePytestUsageError("I062_BOOLEAN_EXPR_EOF")
        token = tokens[position]
        if token == "(":
            position += 1
            value = parse_or()
            if position >= len(tokens) or tokens[position] != ")":
                raise NativePytestUsageError("I062_BOOLEAN_EXPR_PAREN")
            position += 1
            return value
        if token == "not":
            position += 1
            return not atom()
        position += 1
        return predicate(token)

    def parse_and() -> bool:
        nonlocal position
        value = atom()
        while position < len(tokens) and tokens[position] == "and":
            position += 1
            rhs = atom()
            value = value and rhs
        return value

    def parse_or() -> bool:
        nonlocal position
        value = parse_and()
        while position < len(tokens) and tokens[position] == "or":
            position += 1
            rhs = parse_and()
            value = value or rhs
        return value

    result = parse_or()
    if position != len(tokens):
        raise NativePytestUsageError("I062_BOOLEAN_EXPR_TRAILING")
    return result


def _effective_marks(case: NativeTestCase) -> tuple[_MarkSpec, ...]:
    return case.marks


def _skip_reason(marks: Sequence[_MarkSpec]) -> str | None:
    for mark in marks:
        if mark.name == "skip":
            return str(mark.kwargs.get("reason") or (mark.args[0] if mark.args else "skipped"))
        if mark.name == "skipif":
            condition = bool(mark.args[0]) if mark.args else bool(mark.kwargs.get("condition"))
            if condition:
                return str(mark.kwargs.get("reason") or "skipif")
    return None


def _xfail_mark(marks: Sequence[_MarkSpec]) -> _MarkSpec | None:
    return next((mark for mark in marks if mark.name == "xfail"), None)


class NativePytestProvider:
    """Repository-native pytest-compatible collector and executor."""

    def __init__(self, root: str | os.PathLike[str] = ".") -> None:
        self.root = Path(root).resolve()
        self._module_cache: dict[Path, types.ModuleType] = {}
        self._scope_cache: dict[tuple[Any, ...], Any] = {}
        self._scope_finalizers: dict[tuple[Any, ...], list[Callable[[], None]]] = {}
        self._session_tmp = _TempPathFactory()

    def _load_module(self, path: Path) -> types.ModuleType:
        path = path.resolve()
        if path in self._module_cache:
            return self._module_cache[path]
        name = "hhs_i062_" + hashlib.sha256(str(path).encode()).hexdigest()[:20]
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise NativePytestError(f"I062_IMPORT_SPEC_FAILED:{path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        with _pytest_shim_installed():
            spec.loader.exec_module(module)
        self._module_cache[path] = module
        return module

    def _fixtures(self, module: types.ModuleType) -> dict[str, Callable[..., Any]]:
        fixtures: dict[str, Callable[..., Any]] = {}
        for name, value in vars(module).items():
            meta = getattr(value, "__hhs_pytest_fixture__", None)
            if meta is None:
                continue
            fixture_name = meta.name or name
            fixtures[fixture_name] = value
        return fixtures

    def collect(
        self,
        selectors: Sequence[str] = (),
        *,
        keyword: str | None = None,
        mark_expression: str | None = None,
    ) -> tuple[list[NativeTestCase], list[str], int]:
        cases: list[NativeTestCase] = []
        errors: list[str] = []
        total = 0
        paths = _iter_test_paths(self.root, selectors)
        for path in paths:
            try:
                module = self._load_module(path)
            except _SkipSignal:
                continue
            except BaseException as exc:
                errors.append(f"{_path_node(self.root, path)}:{type(exc).__name__}:{exc}")
                continue
            fixtures = self._fixtures(module)
            module_marks = tuple(getattr(module, "pytestmark", ()))
            normalized_module_marks: tuple[_MarkSpec, ...] = tuple(
                mark.spec if isinstance(mark, _MarkDecorator) else mark
                for mark in module_marks
                if isinstance(mark, (_MarkDecorator, _MarkSpec))
            )
            for name, value in vars(module).items():
                if inspect.isfunction(value) and name.startswith("test_"):
                    total += self._collect_function(
                        cases,
                        path,
                        module,
                        value,
                        name,
                        fixtures,
                        normalized_module_marks,
                        selectors,
                        keyword,
                        mark_expression,
                    )
                elif inspect.isclass(value) and name.startswith("Test"):
                    if "__init__" in value.__dict__:
                        continue
                    class_marks = normalized_module_marks + tuple(
                        getattr(value, "__hhs_pytest_marks__", ())
                    )
                    for method_name, method in vars(value).items():
                        if inspect.isfunction(method) and method_name.startswith("test_"):
                            total += self._collect_function(
                                cases,
                                path,
                                module,
                                method,
                                method_name,
                                fixtures,
                                class_marks,
                                selectors,
                                keyword,
                                mark_expression,
                                class_type=value,
                            )
        return cases, errors, total

    def _collect_function(
        self,
        output: list[NativeTestCase],
        path: Path,
        module: types.ModuleType,
        function: Callable[..., Any],
        name: str,
        fixtures: Mapping[str, Callable[..., Any]],
        inherited_marks: tuple[_MarkSpec, ...],
        selectors: Sequence[str],
        keyword: str | None,
        mark_expression: str | None,
        class_type: type[Any] | None = None,
    ) -> int:
        relative = _path_node(self.root, path)
        base_node = relative
        if class_type is not None:
            base_node += f"::{class_type.__name__}"
        base_node += f"::{name}"
        function_marks = inherited_marks + tuple(
            getattr(function, "__hhs_pytest_marks__", ())
        )
        parameter_sets = _parameter_sets(function)
        total = max(1, len(parameter_sets))
        for params, param_marks, param_id in parameter_sets:
            nodeid = base_node + (f"[{param_id}]" if param_id else "")
            marks = function_marks + param_marks
            marker_names = {mark.name for mark in marks}
            if not _selector_matches(nodeid, selectors, self.root):
                continue
            if not _boolean_match(keyword, lambda term: term.casefold() in nodeid.casefold()):
                continue
            if not _boolean_match(mark_expression, lambda term: term in marker_names):
                continue
            output.append(
                NativeTestCase(
                    path=path.resolve(),
                    module=module,
                    function=function,
                    nodeid=nodeid,
                    class_type=class_type,
                    method_name=name if class_type is not None else None,
                    params=params,
                    marks=marks,
                    fixture_defs=fixtures,
                    source_sha256=_source_sha256(path),
                )
            )
        return total

    def _scope_key(self, case: NativeTestCase, fixture_name: str, scope: str) -> tuple[Any, ...]:
        if scope == "session":
            return ("session", fixture_name)
        if scope == "module":
            return ("module", str(case.path), fixture_name)
        if scope == "class":
            return ("class", str(case.path), case.class_type.__name__ if case.class_type else "", fixture_name)
        return ("function", case.nodeid, fixture_name)

    def _register_finalizer(
        self,
        scope_key: tuple[Any, ...],
        finalizer: Callable[[], None],
    ) -> None:
        self._scope_finalizers.setdefault(scope_key, []).append(finalizer)

    def _resolve_fixture(
        self,
        name: str,
        case: NativeTestCase,
        local_cache: dict[str, Any],
        stdout: io.StringIO,
        stderr: io.StringIO,
        stack: tuple[str, ...] = (),
    ) -> Any:
        if name in case.params:
            return case.params[name]
        if name in local_cache:
            return local_cache[name]
        if name in stack:
            raise NativePytestError("I062_FIXTURE_CYCLE:" + "->".join(stack + (name,)))
        if name == "tmp_path":
            holder = tempfile.TemporaryDirectory(prefix="hhs-i062-tmp-")
            value = Path(holder.name)
            local_cache[name] = value
            self._register_finalizer(("function", case.nodeid, name), holder.cleanup)
            return value
        if name == "tmp_path_factory":
            return self._session_tmp
        if name == "monkeypatch":
            value = MonkeyPatch()
            local_cache[name] = value
            self._register_finalizer(("function", case.nodeid, name), value.undo)
            return value
        if name == "capsys":
            value = _CaptureFixture(stdout, stderr)
            local_cache[name] = value
            return value
        if name == "request":
            request = _Request(types.SimpleNamespace(nodeid=case.nodeid))
            local_cache[name] = request
            return request

        fixture = case.fixture_defs.get(name)
        if fixture is None:
            raise NativePytestError(f"I062_FIXTURE_NOT_FOUND:{name}:{case.nodeid}")
        meta: _FixtureMeta = getattr(fixture, "__hhs_pytest_fixture__")
        key = self._scope_key(case, name, meta.scope)
        if meta.scope != "function" and key in self._scope_cache:
            return self._scope_cache[key]

        kwargs: dict[str, Any] = {}
        for parameter in inspect.signature(fixture).parameters.values():
            if parameter.kind in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD):
                continue
            try:
                kwargs[parameter.name] = self._resolve_fixture(
                    parameter.name,
                    case,
                    local_cache,
                    stdout,
                    stderr,
                    stack + (name,),
                )
            except NativePytestError:
                if parameter.default is not inspect.Parameter.empty:
                    kwargs[parameter.name] = parameter.default
                else:
                    raise

        value = _call_maybe_async(fixture, **kwargs)
        finalizers: list[Callable[[], None]] = []
        if inspect.isgenerator(value):
            generator = value
            try:
                value = next(generator)
            except StopIteration as exc:
                raise NativePytestError(f"I062_FIXTURE_NO_YIELD:{name}") from exc

            def finalize_generator(generator: Iterator[Any] = generator, fixture_name: str = name) -> None:
                try:
                    next(generator)
                except StopIteration:
                    return
                raise NativePytestError(f"I062_FIXTURE_MULTIPLE_YIELD:{fixture_name}")
            finalizers.append(finalize_generator)

        request = local_cache.get("request")
        if isinstance(request, _Request):
            finalizers.extend(request._finalizers)
            request._finalizers.clear()

        target_key = key
        for finalizer in finalizers:
            self._register_finalizer(target_key, finalizer)
        if meta.scope == "function":
            local_cache[name] = value
        else:
            self._scope_cache[key] = value
        return value

    def _resolve_arguments(
        self,
        callable_obj: Callable[..., Any],
        case: NativeTestCase,
        local_cache: dict[str, Any],
        stdout: io.StringIO,
        stderr: io.StringIO,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {}
        signature = inspect.signature(callable_obj)
        for parameter in signature.parameters.values():
            if parameter.name in {"self", "cls"}:
                continue
            if parameter.kind in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD):
                continue
            if parameter.name in case.params:
                kwargs[parameter.name] = case.params[parameter.name]
                continue
            try:
                kwargs[parameter.name] = self._resolve_fixture(
                    parameter.name, case, local_cache, stdout, stderr
                )
            except NativePytestError:
                if parameter.default is not inspect.Parameter.empty:
                    kwargs[parameter.name] = parameter.default
                else:
                    raise
        for fixture_name, fixture in case.fixture_defs.items():
            meta: _FixtureMeta = getattr(fixture, "__hhs_pytest_fixture__")
            if meta.autouse:
                self._resolve_fixture(
                    fixture_name, case, local_cache, stdout, stderr
                )
        for mark in case.marks:
            if mark.name == "usefixtures":
                for fixture_name in mark.args:
                    self._resolve_fixture(
                        str(fixture_name), case, local_cache, stdout, stderr
                    )
        return kwargs

    def _cleanup_scope_prefix(self, prefix: tuple[Any, ...]) -> list[str]:
        errors: list[str] = []
        keys = [key for key in self._scope_finalizers if key[: len(prefix)] == prefix]
        for key in reversed(keys):
            finalizers = self._scope_finalizers.pop(key, [])
            while finalizers:
                finalizer = finalizers.pop()
                try:
                    finalizer()
                except BaseException as exc:
                    errors.append(f"{type(exc).__name__}:{exc}")
            self._scope_cache.pop(key, None)
        return errors

    def _run_case(self, case: NativeTestCase) -> NativeTestResult:
        stdout = io.StringIO()
        stderr = io.StringIO()
        local_cache: dict[str, Any] = {}
        started = time.perf_counter_ns()
        outcome = "PASS"
        error_type: str | None = None
        error_message: str | None = None
        tb_text: str | None = None
        strict = False
        xmark = _xfail_mark(case.marks)
        skip_reason = _skip_reason(case.marks)
        if skip_reason is not None:
            return NativeTestResult(case.nodeid, "SKIP", 0, error_message=skip_reason)

        instance: Any = None
        callable_obj: Callable[..., Any] = case.function
        setup_teardown: list[Callable[[], Any]] = []
        try:
            if case.class_type is not None:
                instance = case.class_type()
                callable_obj = getattr(instance, str(case.method_name))
                setup_method = getattr(instance, "setup_method", None)
                teardown_method = getattr(instance, "teardown_method", None)
                if callable(setup_method):
                    _call_maybe_async(setup_method, callable_obj)
                if callable(teardown_method):
                    setup_teardown.append(lambda: _call_maybe_async(teardown_method, callable_obj))
            else:
                setup_function = getattr(case.module, "setup_function", None)
                teardown_function = getattr(case.module, "teardown_function", None)
                if callable(setup_function):
                    _call_maybe_async(setup_function, callable_obj)
                if callable(teardown_function):
                    setup_teardown.append(lambda: _call_maybe_async(teardown_function, callable_obj))

            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                kwargs = self._resolve_arguments(
                    callable_obj, case, local_cache, stdout, stderr
                )
                _call_maybe_async(callable_obj, **kwargs)
            if xmark is not None:
                strict = bool(xmark.kwargs.get("strict", False))
                outcome = "XPASS"
        except _SkipSignal as exc:
            outcome = "SKIP"
            error_message = str(exc)
        except _XFailSignal as exc:
            outcome = "XFAIL"
            error_message = str(exc)
        except BaseException as exc:
            if xmark is not None:
                expected = xmark.kwargs.get("raises")
                if expected is None or isinstance(exc, expected):
                    outcome = "XFAIL"
                else:
                    outcome = "FAIL"
            elif isinstance(exc, AssertionError):
                outcome = "FAIL"
            else:
                outcome = "ERROR"
            error_type = type(exc).__name__
            error_message = str(exc)
            tb_text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        finally:
            for finalizer in reversed(setup_teardown):
                try:
                    finalizer()
                except BaseException as exc:
                    if outcome in {"PASS", "XPASS", "SKIP", "XFAIL"}:
                        outcome = "ERROR"
                        error_type = type(exc).__name__
                        error_message = str(exc)
                        tb_text = "".join(
                            traceback.format_exception(type(exc), exc, exc.__traceback__)
                        )
            cleanup_errors = self._cleanup_scope_prefix(("function", case.nodeid))
            if cleanup_errors and outcome in {"PASS", "XPASS", "SKIP", "XFAIL"}:
                outcome = "ERROR"
                error_type = "FixtureTeardownError"
                error_message = ";".join(cleanup_errors)

        return NativeTestResult(
            nodeid=case.nodeid,
            outcome=outcome,
            duration_ns=time.perf_counter_ns() - started,
            error_type=error_type,
            error_message=error_message,
            traceback=tb_text,
            stdout=stdout.getvalue(),
            stderr=stderr.getvalue(),
            xfail_strict=strict,
        )

    def run(
        self,
        selectors: Sequence[str] = (),
        *,
        keyword: str | None = None,
        mark_expression: str | None = None,
        collect_only: bool = False,
        maxfail: int | None = None,
    ) -> NativePytestRun:
        normalized_selectors = [
            self._normalize_selector(selector) for selector in (selectors or (".",))
        ]
        try:
            cases, collection_errors, collected = self.collect(
                selectors,
                keyword=keyword,
                mark_expression=mark_expression,
            )
        except NativePytestUsageError:
            raise
        config = {
            "selectors": normalized_selectors,
            "keyword": keyword,
            "mark_expression": mark_expression,
            "collect_only": bool(collect_only),
            "maxfail": maxfail,
        }
        config_hash72 = _hash72("config", config)
        collection_identity = [
            {
                "nodeid": case.nodeid,
                "source_sha256": case.source_sha256,
                "marks": [mark.name for mark in case.marks],
            }
            for case in cases
        ]
        collection_hash72 = _hash72("collection", collection_identity)

        results: list[NativeTestResult] = []
        if not collect_only and not collection_errors:
            active_module: Path | None = None
            active_class: type[Any] | None = None
            module_obj: types.ModuleType | None = None
            for case in cases:
                if active_module != case.path:
                    if active_class is not None:
                        self._teardown_class(active_class)
                        self._cleanup_scope_prefix(("class", str(active_module), active_class.__name__))
                        active_class = None
                    if active_module is not None and module_obj is not None:
                        self._teardown_module(module_obj)
                        self._cleanup_scope_prefix(("module", str(active_module)))
                    active_module = case.path
                    module_obj = case.module
                    self._setup_module(module_obj)
                if case.class_type is not active_class:
                    if active_class is not None:
                        self._teardown_class(active_class)
                        self._cleanup_scope_prefix(("class", str(case.path), active_class.__name__))
                    active_class = case.class_type
                    if active_class is not None:
                        self._setup_class(active_class)

                result = self._run_case(case)
                results.append(result)
                failed = result.outcome in {"FAIL", "ERROR"} or (
                    result.outcome == "XPASS" and result.xfail_strict
                )
                if failed and maxfail is not None:
                    if sum(
                        1
                        for item in results
                        if item.outcome in {"FAIL", "ERROR"}
                        or (item.outcome == "XPASS" and item.xfail_strict)
                    ) >= maxfail:
                        break

            if active_class is not None:
                self._teardown_class(active_class)
                self._cleanup_scope_prefix(("class", str(active_module), active_class.__name__))
            if active_module is not None and module_obj is not None:
                self._teardown_module(module_obj)
                self._cleanup_scope_prefix(("module", str(active_module)))

        self._cleanup_scope_prefix(("session",))
        self._session_tmp.close()

        result_identity = [item.identity_dict() for item in results]
        if collect_only:
            result_identity = [{"nodeid": case.nodeid, "outcome": "COLLECTED"} for case in cases]
        result_hash72 = _hash72(
            "results",
            {"results": result_identity, "collection_errors": collection_errors},
        )
        receipt_hash216 = config_hash72 + collection_hash72 + result_hash72
        if len(receipt_hash216) != 216:
            raise RuntimeError("I062_HASH216_WIDTH")

        if collection_errors:
            exit_code = EXIT_COLLECTION_ERROR
        elif not cases:
            exit_code = EXIT_NO_TESTS
        elif collect_only:
            exit_code = EXIT_OK
        elif any(
            item.outcome in {"FAIL", "ERROR"}
            or (item.outcome == "XPASS" and item.xfail_strict)
            for item in results
        ):
            exit_code = EXIT_TESTS_FAILED
        else:
            exit_code = EXIT_OK

        return NativePytestRun(
            schema=SCHEMA,
            provider_id=PROVIDER_ID,
            version=VERSION,
            root=str(self.root),
            collected=collected,
            selected=len(cases),
            results=tuple(results),
            collection_errors=tuple(collection_errors),
            config_hash72=config_hash72,
            collection_hash72=collection_hash72,
            result_hash72=result_hash72,
            receipt_hash216=receipt_hash216,
            exit_code=exit_code,
            authority={
                "execution": "HHS_NATIVE_PYTEST_PROVIDER",
                "external_pytest_execution": False,
                "vm81_mutation": False,
                "hash72_commit": False,
                "hash216_persistence": False,
                "receipt_role": "REPLAYABLE_TEST_EVIDENCE_CANDIDATE",
            },
        )

    def _normalize_selector(self, selector: str) -> str:
        base, *rest = selector.split("::")
        path = Path(base)
        if not path.is_absolute():
            path = self.root / path
        normalized = _path_node(self.root, path)
        return "::".join([normalized, *rest]) if rest else normalized

    @staticmethod
    def _setup_module(module: types.ModuleType) -> None:
        function = getattr(module, "setup_module", None)
        if callable(function):
            _call_maybe_async(function, module)

    @staticmethod
    def _teardown_module(module: types.ModuleType) -> None:
        function = getattr(module, "teardown_module", None)
        if callable(function):
            _call_maybe_async(function, module)

    @staticmethod
    def _setup_class(class_type: type[Any]) -> None:
        function = getattr(class_type, "setup_class", None)
        if callable(function):
            _call_maybe_async(function)

    @staticmethod
    def _teardown_class(class_type: type[Any]) -> None:
        function = getattr(class_type, "teardown_class", None)
        if callable(function):
            _call_maybe_async(function)


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise NativePytestUsageError(message)


def _parser() -> argparse.ArgumentParser:
    parser = _ArgumentParser(prog="hhs-native-pytest", add_help=True)
    parser.add_argument("selectors", nargs="*")
    parser.add_argument("-q", "--quiet", action="count", default=0)
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("-k", dest="keyword")
    parser.add_argument("-m", dest="mark_expression")
    parser.add_argument("--collect-only", action="store_true")
    parser.add_argument("--maxfail", type=int)
    parser.add_argument("-x", action="store_true")
    parser.add_argument("-s", action="store_true", dest="no_capture")
    parser.add_argument("--tb", default="short")
    parser.add_argument("--disable-warnings", action="store_true")
    parser.add_argument("--json-report")
    parser.add_argument("--rootdir", default=".")
    parser.add_argument("--version", action="store_true")
    return parser


_SYMBOL = {
    "PASS": ".",
    "FAIL": "F",
    "ERROR": "E",
    "SKIP": "s",
    "XFAIL": "x",
    "XPASS": "X",
}


def _print_run(run: NativePytestRun, *, quiet: int, verbose: int, collect_only: bool) -> None:
    if collect_only:
        for result in run.results:
            print(result.nodeid)
        if not run.results:
            print(f"collected {run.selected} item(s)")
        return
    if verbose:
        for result in run.results:
            print(f"{result.nodeid} {result.outcome}")
    elif quiet:
        print("".join(_SYMBOL.get(result.outcome, "?") for result in run.results))
    else:
        for result in run.results:
            print(f"{_SYMBOL.get(result.outcome, '?')} {result.nodeid}")
    counts = {outcome: 0 for outcome in OUTCOMES}
    for result in run.results:
        counts[result.outcome] += 1
    summary = ", ".join(f"{value} {key.lower()}" for key, value in counts.items() if value)
    if run.collection_errors:
        summary = (summary + ", " if summary else "") + f"{len(run.collection_errors)} collection error(s)"
    print(summary or "no tests ran")
    print(f"receipt_hash216={run.receipt_hash216}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    try:
        args = parser.parse_args(list(argv) if argv is not None else None)
        if args.version:
            print(VERSION)
            return EXIT_OK
        maxfail = 1 if args.x else args.maxfail
        if maxfail is not None and maxfail < 1:
            raise NativePytestUsageError("--maxfail must be >= 1")
        provider = NativePytestProvider(args.rootdir)
        run = provider.run(
            args.selectors,
            keyword=args.keyword,
            mark_expression=args.mark_expression,
            collect_only=args.collect_only,
            maxfail=maxfail,
        )
        if args.collect_only:
            for case, _, _ in [provider.collect(args.selectors, keyword=args.keyword, mark_expression=args.mark_expression)]:
                for item in case:
                    print(item.nodeid)
        else:
            _print_run(run, quiet=args.quiet, verbose=args.verbose, collect_only=False)
        if args.json_report:
            Path(args.json_report).write_text(
                json.dumps(run.to_dict(), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        return run.exit_code
    except NativePytestUsageError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_USAGE_ERROR
    except KeyboardInterrupt:
        return EXIT_COLLECTION_ERROR
    except BaseException as exc:
        print(f"INTERNAL ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_INTERNAL_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
