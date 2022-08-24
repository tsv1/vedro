from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from .._scenario_finder import ScenarioFinder
from .._scenario_loader import ScenarioLoader
from .._virtual_scenario import VirtualScenario

__all__ = ("ScenarioDiscoverer",)


class ScenarioDiscoverer(ABC):
    def __init__(self, finder: ScenarioFinder, loader: ScenarioLoader) -> None:
        self._finder = finder
        self._loader = loader

    @abstractmethod
    async def discover(self, root: Path) -> List[VirtualScenario]:
        pass
