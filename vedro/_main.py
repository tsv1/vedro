import os
import sys
from argparse import ArgumentParser, HelpFormatter
from functools import partial
from pathlib import Path
from typing import Type, cast

from ._config import Config
from .commands import CommandArgumentParser
from .commands.plugin_command import PluginCommand
from .commands.run_command import RunCommand
from .commands.version_command import VersionCommand
from .core import ConfigFileLoader


async def main() -> None:
    formatter = partial(HelpFormatter, max_help_position=30)
    config_path = Path("vedro.cfg.py")

    arg_parser = ArgumentParser("vedro", formatter_class=formatter,
                                add_help=False, allow_abbrev=False,
                                description="documentation: vedro.io/docs")

    shadow_parser = ArgumentParser(add_help=False, allow_abbrev=False)
    shadow_parser.add_argument("--project-dir", type=Path, default=Path.cwd())
    shadow_args, _ = shadow_parser.parse_known_args()

    project_dir = shadow_args.project_dir.absolute()
    if (not project_dir.exists()) or (not project_dir.is_dir()):
        raise FileNotFoundError(
            f"Specified project directory '{project_dir}' does not exist or is not a directory")
    os.chdir(project_dir)

    config_loader = ConfigFileLoader(Config)
    config = cast(Type[Config], await config_loader.load(config_path))

    commands = {"run", "version", "plugin"}
    arg_parser.add_argument("command", nargs="?", help=f"Command to run {{{', '.join(commands)}}}")
    args, unknown_args = arg_parser.parse_known_args()

    # backward compatibility
    # vedro <args> -> vedro run <args>
    help_args = {"-h", "--help"}
    commands |= {"plugins"}  # alias for "plugin"
    if (args.command not in commands) and (not help_args.intersection(set(unknown_args))):
        default_command = "run"
        sys.argv.insert(1, default_command)
        args.command = default_command

    arg_parser_factory = partial(CommandArgumentParser, formatter_class=formatter,
                                 allow_abbrev=False, add_help=True)

    if args.command == "run":
        parser = arg_parser_factory("vedro run")
        await RunCommand(config, parser).run()

    elif args.command == "version":
        parser = arg_parser_factory("vedro version")
        await VersionCommand(config, parser).run()

    elif args.command in ("plugin", "plugins"):
        parser = arg_parser_factory("vedro plugin")
        await PluginCommand(config, parser).run()

    else:
        arg_parser.print_help()
        arg_parser.exit()
