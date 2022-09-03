import os
from pathlib import Path
from types import MethodType
from typing import Type
from unittest.mock import Mock

import pytest
from baby_steps import given, then, when

from vedro import Scenario
from vedro.core import VirtualScenario, VirtualStep


@pytest.fixture()
def scenario_():
    scenario = Mock(Scenario)
    scenario.__file__ = os.getcwd() + "/scenarios/scenario.py"
    scenario.__module__ = "scenarios.scenario"
    scenario.__name__ = "Scenario"
    return scenario


@pytest.fixture()
def template_():
    scenario = Mock(Scenario)
    scenario.__file__ = os.getcwd() + "/scenarios/scenario.py"
    scenario.__module__ = "scenarios.scenario"
    scenario.__name__ = "Scenario_0_VedroScenario"
    scenario.__vedro__template_index__ = 0
    scenario.__vedro__template_total__ = 1
    return scenario


@pytest.fixture()
def method_():
    return Mock(MethodType)


def test_virtual_scenario_steps(*, scenario_: Type[Scenario], method_: MethodType):
    with given:
        expected_steps = [VirtualStep(method_), VirtualStep(method_)]
        virtual_scenario = VirtualScenario(scenario_, expected_steps)

    with when:
        actual_steps = virtual_scenario.steps

    with then:
        assert actual_steps == expected_steps


def test_virtual_scenario_unique_id(*, scenario_: Type[Scenario]):
    with given:
        virtual_scenario = VirtualScenario(scenario_, [])

    with when:
        unique_id = virtual_scenario.unique_id

    with then:
        assert unique_id == "c2NlbmFyaW9zL3NjZW5hcmlvLnB5OjpTY2VuYXJpbw"


def test_virtual_scenario_unique_hash(*, scenario_: Type[Scenario]):
    with given:
        virtual_scenario = VirtualScenario(scenario_, [])

    with when:
        unique_hash = virtual_scenario.unique_hash

    with then:
        assert unique_hash == "c6b074186cf075e2044bed1088c30b9af5e6e2c2"


def test_virtual_template_unique_id(*, template_: Type[Scenario]):
    with given:
        virtual_scenario = VirtualScenario(template_, [])

    with when:
        unique_id = virtual_scenario.unique_id

    with then:
        assert unique_id == "c2NlbmFyaW9zL3NjZW5hcmlvLnB5OjpTY2VuYXJpb18wX1ZlZHJvU2NlbmFyaW8jMA"


def test_virtual_scenario_path(*, scenario_: Type[Scenario]):
    with given:
        virtual_scenario = VirtualScenario(scenario_, [])

    with when:
        path = virtual_scenario.path

    with then:
        assert path == Path(scenario_.__file__)


def test_virtual_scenario_rel_path(*, scenario_: Type[Scenario]):
    with given:
        virtual_scenario = VirtualScenario(scenario_, [])

    with when:
        path = virtual_scenario.rel_path

    with then:
        assert path == Path("scenarios/scenario.py")


def test_virtual_scenario_subject(*, scenario_: Type[Scenario]):
    with given:
        scenario_.subject = "<subject>"
        virtual_scenario = VirtualScenario(scenario_, [])

    with when:
        subject = virtual_scenario.subject

    with then:
        assert subject == scenario_.subject


def test_virtual_scenario_without_subject(*, scenario_: Type[Scenario]):
    with given:
        virtual_scenario = VirtualScenario(scenario_, [])

    with when:
        subject = virtual_scenario.subject

    with then:
        assert subject == Path(scenario_.__file__).stem


def test_virtual_scenario_namespace(*, scenario_: Type[Scenario]):
    with given:
        virtual_scenario = VirtualScenario(scenario_, [])

    with when:
        namespace = virtual_scenario.namespace

    with then:
        assert namespace == ""


def test_virtual_scenario_with_subject(*, scenario_: Type[Scenario]):
    with given:
        scenario_.subject = "<subject>"
        virtual_scenario = VirtualScenario(scenario_, [])

    with when:
        subject = virtual_scenario.subject

    with then:
        assert subject == scenario_.subject


def test_virtual_scenario_is_skipped(*, scenario_: Type[Scenario]):
    with given:
        virtual_scenario = VirtualScenario(scenario_, [])

    with when:
        is_skipped = virtual_scenario.is_skipped()

    with then:
        assert is_skipped is False


def test_virtual_scenario_skip(*, scenario_: Type[Scenario]):
    with given:
        virtual_scenario = VirtualScenario(scenario_, [])

    with when:
        res = virtual_scenario.skip()

    with then:
        assert res is None
        assert virtual_scenario.is_skipped() is True


def test_virtual_scenario_repr(*, scenario_: Type[Scenario], method_: MethodType):
    with given:
        steps = [VirtualStep(method_), VirtualStep(method_)]
        virtual_scenario = VirtualScenario(scenario_, steps)

    with when:
        res = repr(virtual_scenario)

    with then:
        assert res == f"<VirtualScenario {str(virtual_scenario.rel_path)!r}>"


def test_virtual_scenario_eq_without_steps(*, scenario_: Type[Scenario]):
    with given:
        virtual_scenario1 = VirtualScenario(scenario_, [])
        virtual_scenario2 = VirtualScenario(scenario_, [])

    with when:
        res = virtual_scenario1 == virtual_scenario2

    with then:
        assert res is True


def test_virtual_scenario_not_eq_without_steps(*, scenario_: Type[Scenario]):
    with given:
        another_scenario_ = Mock(Scenario)
        another_scenario_.__file__ = scenario_.__file__
        another_scenario_.__name__ = scenario_.__name__
        virtual_scenario1 = VirtualScenario(scenario_, [])
        virtual_scenario2 = VirtualScenario(another_scenario_, [])

    with when:
        res = virtual_scenario1 == virtual_scenario2

    with then:
        assert res is False


def test_virtual_scenario_eq_with_steps(*, scenario_: Type[Scenario], method_: MethodType):
    with given:
        steps = [VirtualStep(method_), VirtualStep(method_)]
        virtual_scenario1 = VirtualScenario(scenario_, steps)
        virtual_scenario2 = VirtualScenario(scenario_, steps)

    with when:
        res = virtual_scenario1 == virtual_scenario2

    with then:
        assert res is True


def test_virtual_scenario_not_eq_with_steps(*, scenario_: Type[Scenario], method_: MethodType):
    with given:
        steps = [VirtualStep(method_), VirtualStep(method_)]
        virtual_scenario1 = VirtualScenario(scenario_, steps)

        another_method_ = Mock(MethodType)
        another_steps = [VirtualStep(another_method_), VirtualStep(another_method_)]
        virtual_scenario2 = VirtualScenario(scenario_, another_steps)

    with when:
        res = virtual_scenario1 == virtual_scenario2

    with then:
        assert res is False
