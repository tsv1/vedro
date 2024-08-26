from asyncio import CancelledError

import vedro.core as core
import vedro.plugins.artifacted as artifacted
import vedro.plugins.assert_rewriter as assert_rewriter
import vedro.plugins.deferrer as deferrer
import vedro.plugins.director as director
import vedro.plugins.dry_runner as dry_runner
import vedro.plugins.interrupter as interrupter
import vedro.plugins.last_failed as last_failed
import vedro.plugins.orderer as orderer
import vedro.plugins.plugin_enforcer as plugin_enforcer
import vedro.plugins.repeater as repeater
import vedro.plugins.rerunner as rerunner
import vedro.plugins.seeder as seeder
import vedro.plugins.skipper as skipper
import vedro.plugins.slicer as slicer
import vedro.plugins.system_upgrade as system_upgrade
import vedro.plugins.tagger as tagger
import vedro.plugins.temp_keeper as temp_keeper
import vedro.plugins.terminator as terminator
from vedro.core import (
    Dispatcher,
    Factory,
    ModuleFileLoader,
    ModuleLoader,
    MonotonicScenarioRunner,
    MonotonicScenarioScheduler,
    MultiScenarioDiscoverer,
    ScenarioDiscoverer,
    ScenarioFileFinder,
    ScenarioFileLoader,
    ScenarioFinder,
    ScenarioLoader,
    ScenarioOrderer,
    ScenarioRunner,
    ScenarioScheduler,
    Singleton,
)
from vedro.core.scenario_finder.scenario_file_finder import (
    AnyFilter,
    DunderFilter,
    ExtFilter,
    HiddenFilter,
)
from vedro.core.scenario_orderer import StableScenarioOrderer

__all__ = ("Config",)


class Config(core.Config):

    # Validate each plugin's configuration, checking for unknown attributes to prevent errors
    validate_plugins_configs: bool = True

    class Registry(core.Config.Registry):
        Dispatcher = Singleton[Dispatcher](Dispatcher)

        ModuleLoader = Factory[ModuleLoader](ModuleFileLoader)

        ScenarioFinder = Factory[ScenarioFinder](lambda: ScenarioFileFinder(
            file_filter=AnyFilter([HiddenFilter(), DunderFilter(), ExtFilter(only=["py"])]),
            dir_filter=AnyFilter([HiddenFilter(), DunderFilter()])
        ))

        ScenarioLoader = Factory[ScenarioLoader](lambda: ScenarioFileLoader(
            module_loader=Config.Registry.ModuleLoader(),
        ))

        ScenarioOrderer = Factory[ScenarioOrderer](StableScenarioOrderer)

        ScenarioDiscoverer = Factory[ScenarioDiscoverer](lambda: MultiScenarioDiscoverer(
            finder=Config.Registry.ScenarioFinder(),
            loader=Config.Registry.ScenarioLoader(),
            orderer=Config.Registry.ScenarioOrderer(),
        ))

        ScenarioScheduler = Factory[ScenarioScheduler](MonotonicScenarioScheduler)

        # Note: The `ScenarioRunner` factory definition here should not be overridden
        # with a custom runner implementation because, starting from version 2.0,
        # custom runners will be deprecated and removed.
        ScenarioRunner = Factory[ScenarioRunner](lambda: MonotonicScenarioRunner(
            dispatcher=Config.Registry.Dispatcher(),
            interrupt_exceptions=(KeyboardInterrupt, SystemExit, CancelledError),
        ))

    class Plugins(core.Config.Plugins):
        class Director(director.Director):
            enabled = True

        class RichReporter(director.RichReporter):
            enabled = True

        class SilentReporter(director.SilentReporter):
            enabled = True

        class PyCharmReporter(director.PyCharmReporter):
            enabled = True

        class TempKeeper(temp_keeper.TempKeeper):
            enabled = True

        class Orderer(orderer.Orderer):
            enabled = True

        class LastFailed(last_failed.LastFailed):
            enabled = True

        class Deferrer(deferrer.Deferrer):
            enabled = True

        class Seeder(seeder.Seeder):
            enabled = True

        class Artifacted(artifacted.Artifacted):
            enabled = True

        class Skipper(skipper.Skipper):
            enabled = True

        class Slicer(slicer.Slicer):
            enabled = True

        class Tagger(tagger.Tagger):
            enabled = True

        class Repeater(repeater.Repeater):
            enabled = True

        class Rerunner(rerunner.Rerunner):
            enabled = True

        class AssertRewriter(assert_rewriter.AssertRewriter):
            enabled = True

        class DryRunner(dry_runner.DryRunner):
            enabled = True

        class Interrupter(interrupter.Interrupter):
            enabled = True

        class PluginEnforcer(plugin_enforcer.PluginEnforcer):
            enabled = True

        class SystemUpgrade(system_upgrade.SystemUpgrade):
            enabled = True

        class Terminator(terminator.Terminator):
            enabled = True
