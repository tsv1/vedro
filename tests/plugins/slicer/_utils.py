import os
from argparse import ArgumentParser, Namespace
from time import monotonic_ns
from typing import Union
from unittest.mock import Mock

import pytest

from vedro import Scenario
from vedro.core import Dispatcher, VirtualScenario
from vedro.events import ArgParsedEvent, ArgParseEvent
from vedro.plugins.slicer import Slicer, SlicerPlugin


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def slicer(dispatcher: Dispatcher) -> SlicerPlugin:
    slicer = SlicerPlugin(Slicer)
    slicer.subscribe(dispatcher)
    return slicer


def make_vscenario(*, is_skipped: bool = False) -> VirtualScenario:
    scenario_ = Mock(spec=Scenario)
    scenario_.__file__ = os.getcwd() + f"/scenarios/scenario_{monotonic_ns()}.py"
    scenario_.__name__ = "Scenario"

    vsenario = VirtualScenario(scenario_, steps=[])
    if is_skipped:
        vsenario.skip()
    return vsenario


async def fire_arg_parsed_event(dispatcher: Dispatcher, *,
                                total: Union[int, None] = None,
                                index: Union[int, None] = None) -> None:
    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)

    arg_parsed_event = ArgParsedEvent(Namespace(slicer_total=total, slicer_index=index))
    await dispatcher.fire(arg_parsed_event)
