from typing import Optional, Type

from ._config_loader import Section
from ._dispatcher import Dispatcher, Subscriber

__all__ = ("Plugin", "PluginConfig",)


class Plugin(Subscriber):
    def __init__(self, config: Optional[Type["PluginConfig"]] = None) -> None:
        self._config = config

    def subscribe(self, dispatcher: Dispatcher) -> None:
        pass


class PluginConfig(Section):
    plugin: Type[Plugin] = Plugin
    enabled: bool = True
