import importlib
import importlib.util
import inspect
import os
from importlib.abc import Loader
from importlib.machinery import ModuleSpec
from keyword import iskeyword
from pathlib import Path
from types import ModuleType
from typing import List, Type, cast

from ..._scenario import Scenario
from ._scenario_loader import ScenarioLoader

__all__ = ("ScenarioFileLoader",)


class ScenarioFileLoader(ScenarioLoader):
    def _path_to_module_name(self, path: Path) -> str:
        parts = path.with_suffix("").parts
        for part in parts:
            if not self._is_valid_identifier(part):
                raise ValueError(
                    f"The module name derived from the path '{path}' is invalid "
                    f"due to the segment '{part}'. A valid module name should "
                    "start with a letter or underscore, contain only letters, "
                    "digits, or underscores, and not be a Python keyword."
                )
        return ".".join(parts)

    def _is_valid_identifier(self, name: str) -> bool:
        return name.isidentifier() and not iskeyword(name)

    def _spec_from_path(self, path: Path) -> ModuleSpec:
        module_name = self._path_to_module_name(path)
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None:
            raise ModuleNotFoundError(module_name)
        return spec

    def _module_from_spec(self, spec: ModuleSpec) -> ModuleType:
        return importlib.util.module_from_spec(spec)

    def _exec_module(self, loader: Loader, module: ModuleType) -> None:
        loader.exec_module(module)

    async def load(self, path: Path) -> List[Type[Scenario]]:
        print("path", path)
        spec = self._spec_from_path(path)
        module = self._module_from_spec(spec)
        self._exec_module(cast(Loader, spec.loader), module)

        loaded = []
        # used module.__dict__ instead of dir(module) because __dict__ preserves order
        for name in module.__dict__:
            val = getattr(module, name)
            if inspect.isclass(val) and issubclass(val, Scenario) and val != Scenario:
                if not (val.__name__.startswith("Scenario") or val.__name__.endswith("Scenario")):
                    continue
                val.__file__ = os.path.abspath(module.__file__)  # type: ignore
                loaded.append(val)
        return loaded
