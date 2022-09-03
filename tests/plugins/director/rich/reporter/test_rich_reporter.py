from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher
from vedro.core import MonotonicScenarioScheduler as ScenarioScheduler
from vedro.core import Report
from vedro.events import CleanupEvent, ScenarioReportedEvent, ScenarioRunEvent, StartupEvent
from vedro.plugins.director import (
    DirectorInitEvent,
    DirectorPlugin,
    RichReporter,
    RichReporterPlugin,
)

from ._utils import (
    director,
    dispatcher,
    fire_arg_parsed_event,
    make_aggregated_result,
    make_scenario_result,
    printer_,
    rich_reporter,
)

__all__ = ("dispatcher", "rich_reporter", "director", "printer_")  # fixtures


@pytest.mark.asyncio
async def test_subscribe(*, dispatcher: Dispatcher):
    with given:
        director_ = Mock(DirectorPlugin)

        reporter = RichReporterPlugin(RichReporter)
        reporter.subscribe(dispatcher)

    with when:
        await dispatcher.fire(DirectorInitEvent(director_))

    with then:
        assert director_.mock_calls == [
            call.register("rich", reporter)
        ]


@pytest.mark.asyncio
@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_startup(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scheduler = ScenarioScheduler([])
        event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.mock_calls == [
            call.print_header()
        ]


@pytest.mark.asyncio
@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_run(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scenario_result = make_scenario_result()
        event = ScenarioRunEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.print_namespace.assert_called() is None
        assert len(printer_.mock_calls) == 1


@pytest.mark.asyncio
@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_run_same_namespace(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scenario_result1 = make_scenario_result()
        await dispatcher.fire(ScenarioRunEvent(scenario_result1))
        printer_.reset_mock()

        scenario_result2 = make_scenario_result()
        event = ScenarioRunEvent(scenario_result2)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.print_namespace.assert_not_called() is None
        assert len(printer_.mock_calls) == 0


@pytest.mark.asyncio
@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_unknown_status(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scenario_result = make_scenario_result()
        aggregated_result = make_aggregated_result(scenario_result)
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.mock_calls == []


@pytest.mark.asyncio
@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_cleanup(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        report = Report()
        event = CleanupEvent(report)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.mock_calls == [
            call.print_empty_line(),
            call.print_report_summary(report.summary),
            call.print_report_stats(total=report.total,
                                    passed=report.passed,
                                    failed=report.failed,
                                    skipped=report.skipped,
                                    elapsed=report.elapsed)
        ]
