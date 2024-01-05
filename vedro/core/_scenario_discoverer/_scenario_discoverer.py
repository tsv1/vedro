from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from .._scenario_finder import ScenarioFinder
from .._scenario_loader import ScenarioLoader
from .._virtual_scenario import VirtualScenario
from ..scenario_orderer import ScenarioOrderer

__all__ = ("ScenarioDiscoverer",)


class ScenarioDiscoverer(ABC):
    """
    An abstract base class for discovering scenarios.

    This class defines the basic framework for discovering scenarios from a source
    (like a directory). It uses a finder to locate scenarios, a loader to load them,
    and an orderer to sort them into the desired sequence.

    :param finder: An instance of ScenarioFinder for finding scenario files.
    :param loader: An instance of ScenarioLoader for loading scenarios from files.
    :param orderer: An instance of ScenarioOrderer for ordering the loaded scenarios.
    """

    def __init__(self, finder: ScenarioFinder, loader: ScenarioLoader,
                 orderer: ScenarioOrderer) -> None:
        self._finder = finder
        self._loader = loader
        self._orderer = orderer

    @abstractmethod
    async def discover(self, root: Path) -> List[VirtualScenario]:
        """
        An abstract method for discovering scenarios.

        Subclasses should implement this method to define how scenarios are discovered from the
        given root path. The method should asynchronously return a list of
        discovered VirtualScenarios.

        :param root: The root path to start discovering scenarios.
        :return: A list of discovered VirtualScenario instances.
        """
        pass
