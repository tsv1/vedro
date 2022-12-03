import sys
from typing import Dict, List, cast

if sys.version_info >= (3, 8):
    from importlib.metadata import PackageNotFoundError, metadata
else:
    def metadata(name: str) -> Dict[str, str]:
        raise PackageNotFoundError(name)
    PackageNotFoundError = Exception

import json
import platform
import urllib.request
from dataclasses import dataclass
from typing import Callable, Type

from rich.console import Console
from rich.table import Table

import vedro
from vedro import Config
from vedro.core import PluginConfig

from ._cmd_arg_parser import CommandArgumentParser
from ._command import Command

__all__ = ("PluginCommand", "PluginInfo",)


def make_console() -> Console:
    return Console(highlight=False, force_terminal=True, markup=False, soft_wrap=True)


@dataclass
class PluginInfo:
    name: str
    enabled: bool
    package: str = "Unknown"
    version: str = "0.0.0"
    summary: str = "No data"
    is_default: bool = False


class PluginCommand(Command):
    def __init__(self, config: Type[Config], arg_parser: CommandArgumentParser, *,
                 console_factory: Callable[[], Console] = make_console) -> None:
        super().__init__(config, arg_parser)
        self._console = console_factory()

    def _get_plugin_info(self, plugin_config: PluginConfig) -> PluginInfo:
        plugin_name = getattr(plugin_config, "__name__", "Plugin")
        plugin_info = PluginInfo(plugin_name, plugin_config.enabled)

        plugin = plugin_config.plugin
        module = plugin.__module__
        package = module.split(".")[0]

        # plugin declared in vedro.cfg.py
        if module == self._config.__module__:
            return plugin_info

        # default plugin
        if package == "vedro":
            plugin_info.package = ".".join(module.split(".")[:-1])
            plugin_info.version = vedro.__version__
            plugin_info.summary = "Core plugin"
            plugin_info.is_default = True
            return plugin_info

        try:
            meta = metadata(package)
        except PackageNotFoundError:
            return plugin_info

        plugin_info.package = package
        if "Version" in meta:
            plugin_info.version = meta["Version"]
        if "Summary" in meta:
            plugin_info.summary = meta["Summary"]
        return plugin_info

    async def _show_installed_plugins(self) -> None:
        table = Table(expand=True, border_style="grey50")
        for column in ("Name", "Package", "Description", "Version", "Enabled"):
            table.add_column(column)

        for plugin_config in self._config.Plugins.values():
            plugin_info = self._get_plugin_info(plugin_config)

            color = "blue" if plugin_config.enabled else "grey70"
            table.add_row(plugin_info.name, plugin_info.package, plugin_info.summary,
                          plugin_info.version, str(plugin_info.enabled), style=color)

        self._console.print(table)

    def _get_user_agent(self) -> str:
        python_version = platform.python_version()
        platform_info = platform.platform(terse=True)
        return f"Vedro/{vedro.__version__} (Python/{python_version}; {platform_info})"

    def _send_request(self, url: str, *,
                      headers: Dict[str, str], timeout: float) -> List[Dict[str, str]]:
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result = json.loads(response.read())
        return cast(List[Dict[str, str]], result)

    async def _show_top_plugins(self) -> None:
        url = "https://api.vedro.io/v1/plugins/top?limit=10"
        headers = {"User-Agent": self._get_user_agent()}

        with self._console.status("Fetching plugins..."):
            try:
                plugins = self._send_request(url, headers=headers, timeout=10.0)
            except Exception as e:
                self._console.print(f"Failed to fetch popular plugins ({e})", style="red")
                return

        table = Table(expand=True, border_style="grey50")
        table.add_column("Package", overflow="fold", style="blue")
        table.add_column("Description", overflow="fold")
        table.add_column("URL", overflow="fold")
        table.add_column("Popularity", justify="right")

        for plugin in plugins:
            table.add_row(plugin["name"], plugin["description"],
                          plugin["url"], str(plugin["popularity"]))

        self._console.print(table)

    async def run(self) -> None:
        subparsers = self._arg_parser.add_subparsers(dest="subparser")

        subparsers.add_parser("list", help="Show installed plugins")
        subparsers.add_parser("top", help="Show popular plugins")

        args = self._arg_parser.parse_args()
        if args.subparser == "top":
            await self._show_top_plugins()
        elif args.subparser == "list":
            await self._show_installed_plugins()
        else:
            self._arg_parser.print_help()
            self._arg_parser.exit()
