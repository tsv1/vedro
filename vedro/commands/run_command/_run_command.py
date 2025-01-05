import inspect
import os
import warnings
from argparse import Namespace
from collections.abc import Sequence
from inspect import isclass
from os import linesep
from pathlib import Path
from typing import Any, List, Set, Type

from vedro import Config
from vedro.core import Dispatcher, MonotonicScenarioRunner, Plugin, PluginConfig
from vedro.events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    ConfigLoadedEvent,
    StartupEvent,
)
from vedro.plugins.dry_runner import DryRunner

from .._cmd_arg_parser import CommandArgumentParser
from .._command import Command

__all__ = ("RunCommand",)


class RunCommand(Command):
    """
    Represents the "run" command for executing scenarios.

    This command handles the entire lifecycle of scenario execution, including:
    - Validating configuration parameters.
    - Registering plugins with the dispatcher.
    - Parsing command-line arguments.
    - Discovering scenarios.
    - Scheduling and executing scenarios.
    - Dispatching events before and after scenario execution.

    :param config: The global configuration instance.
    :param arg_parser: The argument parser for parsing command-line options.
    """

    def __init__(self, config: Type[Config], arg_parser: CommandArgumentParser) -> None:
        """
        Initialize the RunCommand instance.

        :param config: The global configuration instance.
        :param arg_parser: The argument parser for parsing command-line options.
        """
        super().__init__(config, arg_parser)

    def _validate_config(self) -> None:
        """
        Validate the configuration parameters.

        Ensures that the `default_scenarios_dir` is a valid directory within the
        project directory. Raises appropriate exceptions if validation fails.

        :raises TypeError: If `default_scenarios_dir` is not a `Path` or `str`.
        :raises FileNotFoundError: If `default_scenarios_dir` does not exist.
        :raises NotADirectoryError: If `default_scenarios_dir` is not a directory.
        :raises ValueError: If `default_scenarios_dir` is not inside the project directory.
        """
        default_scenarios_dir = self._config.default_scenarios_dir
        if default_scenarios_dir == Config.default_scenarios_dir:
            return

        if not isinstance(default_scenarios_dir, (Path, str)):
            raise TypeError(
                "Expected `default_scenarios_dir` to be a Path, "
                f"got {type(default_scenarios_dir)} ({default_scenarios_dir!r})"
            )

        scenarios_dir = Path(default_scenarios_dir).resolve()
        if not scenarios_dir.exists():
            raise FileNotFoundError(
                f"`default_scenarios_dir` ('{scenarios_dir}') does not exist"
            )

        if not scenarios_dir.is_dir():
            raise NotADirectoryError(
                f"`default_scenarios_dir` ('{scenarios_dir}') is not a directory"
            )

        try:
            scenarios_dir.relative_to(self._config.project_dir)
        except ValueError:
            raise ValueError(
                f"`default_scenarios_dir` ('{scenarios_dir}') must be inside project directory "
                f"('{self._config.project_dir}')"
            )

    async def _register_plugins(self, dispatcher: Dispatcher) -> None:
        for plugin_config in self._get_ordered_plugins():
            plugin = plugin_config.plugin(config=plugin_config)
            dispatcher.register(plugin)

    def _get_ordered_plugins(self) -> List[Type[PluginConfig]]:
        available_plugins = set(self._config.Plugins.values())

        plugins = []
        for plugin_config in self._config.Plugins.values():
            self._validate_plugin_config(plugin_config, available_plugins)
            if plugin_config.enabled:
                plugins.append(plugin_config)

        return self._order_plugins(plugins)

    def _order_plugins(self, plugins: List[Type[PluginConfig]]) -> List[Type[PluginConfig]]:
        for plugin in plugins:
            ...

        return plugins

    def _validate_plugin_config(self, plugin_config: Type[PluginConfig],
                                available_plugins: Set[Type[PluginConfig]]) -> None:
        if not self._is_subclass(plugin_config, PluginConfig):
            raise TypeError(
                f"PluginConfig '{plugin_config}' must be a subclass of 'vedro.core.PluginConfig'"
            )

        if not self._is_subclass(plugin_config.plugin, Plugin) or (plugin_config.plugin is Plugin):
            raise TypeError(
                f"Attribute 'plugin' in '{plugin_config.__name__}' must be a subclass of "
                "'vedro.core.Plugin'"
            )

        if not isinstance(plugin_config.depends_on, Sequence):
            raise TypeError(
                f"Attribute 'depends_on' in '{plugin_config.__name__}' plugin must be a list or"
                f"another sequence type ({type(plugin_config.depends_on)} provided). "
                + linesep.join([
                    "Example:",
                    "  @computed",
                    "  def depends_on(cls):",
                    "    return [Config.Plugins.Tagger]"
                ])
            )

        for dep in plugin_config.depends_on:
            if not self._is_subclass(dep, PluginConfig):
                raise TypeError(
                    f"Dependency '{dep}' in 'depends_on' of '{plugin_config.__name__}' "
                    "must be a subclass of 'vedro.core.PluginConfig'"
                )

            if dep not in available_plugins:
                raise ValueError(
                    f"Dependency '{dep.__name__}' in 'depends_on' of '{plugin_config.__name__}' "
                    "is not found among the configured plugins"
                )

            if plugin_config.enabled and not dep.enabled:
                raise ValueError(
                    f"Dependency '{dep.__name__}' in 'depends_on' of '{plugin_config.__name__}' "
                    "is not enabled"
                )

        if self._config.validate_plugins_configs:
            self._validate_plugin_config_attrs(plugin_config)

    def _validate_plugin_config_attrs(self, plugin_config: Type[PluginConfig]) -> None:
        unknown_attrs = self._get_attrs(plugin_config) - self._get_parent_attrs(plugin_config)
        if unknown_attrs:
            attrs = ", ".join(unknown_attrs)
            raise AttributeError(
                f"{plugin_config.__name__} configuration contains unknown attributes: {attrs}"
            )

    def _is_subclass(self, cls: Any, parent: Any) -> bool:
        return isclass(cls) and issubclass(cls, parent)

    def _get_attrs(self, cls: type) -> Set[str]:
        """
        Retrieve the set of attributes for a class.

        :param cls: The class to retrieve attributes for.
        :return: A set of attribute names for the class.
        """
        return set(vars(cls))

    def _get_parent_attrs(self, cls: type) -> Set[str]:
        """
        Recursively retrieve attributes from parent classes.

        :param cls: The class to retrieve parent attributes for.
        :return: A set of attribute names for the parent classes.
        """
        attrs = set()
        # `object` (the base for all classes) has no __bases__
        for base in cls.__bases__:
            attrs |= self._get_attrs(base)
            attrs |= self._get_parent_attrs(base)
        return attrs

    async def _parse_args(self, dispatcher: Dispatcher) -> Namespace:
        """
        Parse command-line arguments and fire corresponding dispatcher events.

        Adds the `--project-dir` argument, fires the `ArgParseEvent`, parses
        the arguments, and then fires the `ArgParsedEvent`.

        :param dispatcher: The dispatcher to fire events.
        :return: The parsed arguments as a `Namespace` object.
        """

        # Avoid unrecognized arguments error
        help_message = ("Specify the root directory of the project, used as a reference point for "
                        "relative paths and file operations. "
                        "Defaults to the directory from which the command is executed.")
        self._arg_parser.add_argument("--project-dir", type=Path,
                                      default=self._config.project_dir,
                                      help=help_message)

        # https://github.com/python/cpython/issues/95073
        self._arg_parser.remove_help_action()
        await dispatcher.fire(ArgParseEvent(self._arg_parser))
        self._arg_parser.add_help_action()

        args = self._arg_parser.parse_args()
        await dispatcher.fire(ArgParsedEvent(args))

        return args

    async def run(self) -> None:
        """
        Execute the command lifecycle.

        This method validates the configuration, registers plugins, parses arguments,
        discovers scenarios, schedules them, and executes them.

        :raises Exception: If scenario discovery raises a `SystemExit`.
        """
        # TODO: move config validation to somewhere else in v2
        self._validate_config()  # Must be before ConfigLoadedEvent

        dispatcher = self._config.Registry.Dispatcher()
        await self._register_plugins(dispatcher)

        await dispatcher.fire(ConfigLoadedEvent(self._config.path, self._config))

        args = await self._parse_args(dispatcher)
        start_dir = self._get_start_dir(args)

        discoverer = self._config.Registry.ScenarioDiscoverer()

        kwargs = {}
        # Backward compatibility (to be removed in v2):
        signature = inspect.signature(discoverer.discover)
        if "project_dir" in signature.parameters:
            kwargs["project_dir"] = self._config.project_dir

        try:
            scenarios = await discoverer.discover(start_dir, **kwargs)
        except SystemExit as e:
            raise Exception(f"SystemExit({e.code}) ⬆")

        scheduler = self._config.Registry.ScenarioScheduler(scenarios)
        await dispatcher.fire(StartupEvent(scheduler))

        runner = self._config.Registry.ScenarioRunner()
        if not isinstance(runner, (MonotonicScenarioRunner, DryRunner)):
            warnings.warn("Deprecated: custom runners will be removed in v2.0", DeprecationWarning)
        report = await runner.run(scheduler)

        await dispatcher.fire(CleanupEvent(report))

    def _get_start_dir(self, args: Namespace) -> Path:
        """
        Determine the starting directory for discovering scenarios.

        Resolves the starting directory based on the parsed arguments, ensuring
        it is a valid directory inside the project directory.

        :param args: Parsed command-line arguments.
        :return: The resolved starting directory.
        :raises ValueError: If the starting directory is outside the project directory.
        """
        file_or_dir = getattr(args, "file_or_dir", [])
        # Note: `args.file_or_dir` is an argument that is registered by the core Skipper plugin.
        # This introduces a dependency on the Skipper plugin's implementation,
        # violating best practices, as the higher-level RunCommand component directly relies
        # on a lower-level plugin.
        # TODO: Fix this in v2.0 by introducing a more generic mechanism for passing arguments
        if not file_or_dir:
            return Path(self._config.default_scenarios_dir).resolve()

        common_path = os.path.commonpath([self._normalize_path(x) for x in file_or_dir])
        start_dir = Path(common_path).resolve()
        if not start_dir.is_dir():
            start_dir = start_dir.parent

        try:
            start_dir.relative_to(self._config.project_dir)
        except ValueError:
            raise ValueError(
                f"The start directory '{start_dir}' must be inside the project directory "
                f"('{self._config.project_dir}')"
            )

        return start_dir

    def _normalize_path(self, file_or_dir: str) -> str:
        """
        Normalize the provided path and handle backward compatibility.

        Ensures the path is absolute and adjusts it based on legacy rules if necessary.

        :param file_or_dir: The path to normalize.
        :return: The normalized absolute path.
        """
        path = os.path.normpath(file_or_dir)
        if os.path.isabs(path):
            return path

        # Backward compatibility (to be removed in v2):
        # Only prepend "scenarios/" if:
        # 1) The default_scenarios_dir is exactly <project_dir>/scenarios
        # 2) The original path does not exist, but "scenarios/<path>" does
        scenarios_dir = Path(self._config.default_scenarios_dir).resolve()
        if scenarios_dir == self._config.project_dir / "scenarios":
            updated_path = os.path.join("scenarios/", path)
            if not os.path.exists(path) and os.path.exists(updated_path):
                return os.path.abspath(updated_path)

        return os.path.abspath(path)
