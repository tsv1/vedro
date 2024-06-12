import os
from pathlib import Path
from textwrap import dedent

import pytest
from baby_steps import given, then, when
from niltype import Nil
from pytest import raises

from vedro.plugins.assert_rewriter import AssertRewriterLoader, CompareOperator, assert_


@pytest.fixture()
def tmp_scn_dir(tmp_path: Path) -> Path:
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        scn_dir = tmp_path / "scenarios/"
        scn_dir.mkdir(exist_ok=True)
        yield scn_dir.relative_to(tmp_path)
    finally:
        os.chdir(cwd)


async def test_load(tmp_scn_dir: Path):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent('''
            import vedro
            class Scenario(vedro.Scenario):
                def then(self):
                    assert 1 == 2
        '''))

        loader = AssertRewriterLoader()
        module = await loader.load(path)
        scenario = module.Scenario()

    with when, raises(BaseException) as exc:
        scenario.then()

    with then:
        assert exc.type is AssertionError
        assert str(exc.value) == ""

        assert assert_.get_left(exc.value) == 1
        assert assert_.get_right(exc.value) == 2
        assert assert_.get_operator(exc.value) == CompareOperator.EQUAL
        assert assert_.get_message(exc.value) == Nil
