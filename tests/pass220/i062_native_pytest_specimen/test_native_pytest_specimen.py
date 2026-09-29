from __future__ import annotations

import os
import pytest


@pytest.fixture
def base_value():
    return 2


@pytest.fixture
def doubled(base_value):
    yield base_value * 2


@pytest.mark.parametrize(
    "left,right",
    [
        (1, 2),
        pytest.param(2, 4, id="two"),
    ],
)
def test_parametrize_and_fixture(left, right, doubled):
    assert left * doubled == right * 2


def test_raises_and_approx():
    with pytest.raises(ValueError, match="native"):
        raise ValueError("native provider")
    assert 1.0000001 == pytest.approx(1.0)


@pytest.mark.skip(reason="compatibility skip")
def test_skip():
    raise AssertionError("must not execute")


@pytest.mark.xfail(reason="expected compatibility failure")
def test_xfail():
    assert False


@pytest.mark.asyncio
async def test_async_and_builtin_fixtures(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("HHS_I062_SPECIMEN", "1")
    assert os.environ["HHS_I062_SPECIMEN"] == "1"
    target = tmp_path / "value.txt"
    target.write_text("ok", encoding="utf-8")
    print(target.read_text(encoding="utf-8"))
    captured = capsys.readouterr()
    assert captured.out.strip() == "ok"
