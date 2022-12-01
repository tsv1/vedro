from baby_steps import given, then, when

from vedro.commands._cmd_arg_parser import CommandArgumentParser
from vedro.commands._command import Command
from vedro.commands._run_command import RunCommand
from vedro.core import Config


def test_inheritance():
    with given:
        config = Config
        arg_parser = CommandArgumentParser()

    with when:
        command = RunCommand(config, arg_parser)

    with then:
        assert isinstance(command, Command)
