import warnings
from enum import Enum
from typing import Any, Dict, List, Union

from ._artifacts import Artifact
from ._step_result import StepResult
from ._virtual_scenario import VirtualScenario

__all__ = ("ScenarioResult", "ScenarioStatus", "AggregatedResult",)


class ScenarioStatus(Enum):
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class ScenarioResult:
    def __init__(self, scenario: VirtualScenario, *, rerun: int = 0) -> None:
        self._scenario = scenario
        self._status: ScenarioStatus = ScenarioStatus.PENDING
        self._started_at: Union[float, None] = None
        self._ended_at: Union[float, None] = None
        self._step_results: List[StepResult] = []
        self._scope: Union[Dict[Any, Any], None] = None
        self._artifacts: List[Artifact] = []
        if rerun > 0:
            warnings.warn("Deprecated", DeprecationWarning)

    @property
    def scenario(self) -> VirtualScenario:
        return self._scenario

    @property
    def scenario_subject(self) -> str:
        warnings.warn("Deprecated: use scenario.subject instead", DeprecationWarning)
        return self._scenario.subject

    @property
    def scenario_namespace(self) -> str:
        warnings.warn("Deprecated: use scenario.namespace instead", DeprecationWarning)
        return self.scenario.namespace

    @property
    def status(self) -> ScenarioStatus:
        return self._status

    @property
    def rerun(self) -> int:
        warnings.warn("Deprecated: always returns 0", DeprecationWarning)
        return 0

    def mark_passed(self) -> "ScenarioResult":
        self._status = ScenarioStatus.PASSED
        return self

    def is_passed(self) -> bool:
        return self._status == ScenarioStatus.PASSED

    def mark_failed(self) -> "ScenarioResult":
        self._status = ScenarioStatus.FAILED
        return self

    def is_failed(self) -> bool:
        return self._status == ScenarioStatus.FAILED

    def mark_skipped(self) -> "ScenarioResult":
        self._status = ScenarioStatus.SKIPPED
        return self

    def is_skipped(self) -> bool:
        return self._status == ScenarioStatus.SKIPPED

    @property
    def started_at(self) -> Union[float, None]:
        return self._started_at

    def set_started_at(self, started_at: float) -> "ScenarioResult":
        self._started_at = started_at
        return self

    @property
    def ended_at(self) -> Union[float, None]:
        return self._ended_at

    def set_ended_at(self, ended_at: float) -> "ScenarioResult":
        self._ended_at = ended_at
        return self

    @property
    def elapsed(self) -> float:
        if (self._started_at is None) or (self._ended_at is None):
            return 0.0
        return self._ended_at - self._started_at

    def add_step_result(self, step_result: StepResult) -> None:
        self._step_results.append(step_result)

    @property
    def step_results(self) -> List[StepResult]:
        return self._step_results[:]

    def set_scope(self, scope: Dict[Any, Any]) -> None:
        self._scope = scope

    @property
    def scope(self) -> Dict[Any, Any]:
        if self._scope is None:
            return {}
        return self._scope

    def attach(self, artifact: Artifact) -> None:
        assert isinstance(artifact, Artifact)
        self._artifacts.append(artifact)

    @property
    def artifacts(self) -> List[Artifact]:
        return self._artifacts[:]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self._scenario!r} {self._status.value}>"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and (self.__dict__ == other.__dict__)


class AggregatedResult(ScenarioResult):
    def __init__(self, scenario: VirtualScenario) -> None:
        super().__init__(scenario)
        self._scenario_results: List[ScenarioResult] = []

    @property
    def scenario_results(self) -> List[ScenarioResult]:
        return self._scenario_results[:]

    def add_scenario_result(self, scenario_result: ScenarioResult) -> None:
        self._scenario_results.append(scenario_result)

    @staticmethod
    def from_existing(main_scenario_result: ScenarioResult,
                      scenario_results: List[ScenarioResult]) -> "AggregatedResult":
        result = AggregatedResult(main_scenario_result.scenario)

        if main_scenario_result.is_passed():
            result.mark_passed()
        elif main_scenario_result.is_failed():
            result.mark_failed()
        elif main_scenario_result.is_skipped():
            result.mark_skipped()

        if main_scenario_result.started_at is not None:
            result.set_started_at(main_scenario_result.started_at)
        if main_scenario_result.ended_at is not None:
            result.set_ended_at(main_scenario_result.ended_at)

        result.set_scope(main_scenario_result.scope)

        for step_result in main_scenario_result.step_results:
            result.add_step_result(step_result)

        for artifact in main_scenario_result.artifacts:
            result.attach(artifact)

        assert len(scenario_results) > 0
        for scenario_result in scenario_results:
            result.add_scenario_result(scenario_result)

        return result
