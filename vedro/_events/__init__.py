from argparse import ArgumentParser, Namespace
from typing import Any, List

from .._core._report import Report
from .._core._scenario_result import ScenarioResult
from .._core._step_result import StepResult
from .._core._virtual_scenario import VirtualScenario
from ._event import Event


class ArgParseEvent(Event):
    def __init__(self, arg_parser: ArgumentParser) -> None:
        self._arg_parser = arg_parser

    @property
    def arg_parser(self) -> ArgumentParser:
        return self._arg_parser


class ArgParsedEvent(Event):
    def __init__(self, args: Namespace) -> None:
        self._args = args

    @property
    def args(self) -> Namespace:
        return self._args


class StartupEvent(Event):
    def __init__(self, scenarios: List[VirtualScenario]) -> None:
        self._scenarios = scenarios

    @property
    def scenarios(self) -> List[VirtualScenario]:
        return self._scenarios


class _ScenarioEvent(Event):
    def __init__(self, scenario_result: ScenarioResult) -> None:
        self._scenario_result = scenario_result

    @property
    def scenario_result(self) -> ScenarioResult:
        return self._scenario_result

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self._scenario_result == other._scenario_result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._scenario_result!r})"


class ScenarioSkipEvent(_ScenarioEvent):
    pass


class ScenarioRunEvent(_ScenarioEvent):
    pass


class ScenarioFailEvent(_ScenarioEvent):
    pass


class ScenarioPassEvent(_ScenarioEvent):
    pass


class _StepEvent(Event):
    def __init__(self, step_result: StepResult) -> None:
        self._step_result = step_result

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self._step_result == other._step_result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._step_result!r})"


class StepRunEvent(_StepEvent):
    pass


class StepFailEvent(_StepEvent):
    pass


class StepPassEvent(_StepEvent):
    pass


class CleanupEvent(Event):
    def __init__(self, report: Report) -> None:
        self._report = report

    @property
    def report(self) -> Report:
        return self._report


__all__ = ("Event", "ArgParseEvent", "ArgParsedEvent", "StartupEvent",
           "ScenarioSkipEvent", "ScenarioRunEvent", "ScenarioFailEvent", "ScenarioPassEvent",
           "StepRunEvent", "StepFailEvent", "StepPassEvent", "CleanupEvent",)
