from math import isclose
from unittest.mock import Mock

from baby_steps import given, then, when

from vedro.core import Report, ScenarioResult, VirtualScenario


def make_scenario_result() -> ScenarioResult:
    scenario_ = Mock(VirtualScenario)
    return ScenarioResult(scenario_)


def test_defaults():
    with when:
        report = Report()

    with then:
        assert report.total == 0
        assert report.passed == 0
        assert report.failed == 0
        assert report.skipped == 0

        assert report.started_at is None
        assert report.ended_at is None
        assert report.elapsed == 0.0


def test_passed():
    with given:
        report = Report()
        scenario_result = make_scenario_result().mark_passed()

    with when:
        res = report.add_result(scenario_result)

    with then:
        assert res is None
        assert report.total == 1
        assert report.passed == 1
        assert report.failed == 0
        assert report.skipped == 0


def test_failed():
    with given:
        report = Report()
        scenario_result = make_scenario_result().mark_failed()

    with when:
        res = report.add_result(scenario_result)

    with then:
        assert res is None
        assert report.total == 1
        assert report.passed == 0
        assert report.failed == 1
        assert report.skipped == 0


def test_skipped():
    with given:
        report = Report()
        scenario_result = make_scenario_result().mark_skipped()

    with when:
        res = report.add_result(scenario_result)

    with then:
        assert res is None
        assert report.total == 1
        assert report.passed == 0
        assert report.failed == 0
        assert report.skipped == 1


def test_elapsed():
    with given:
        report = Report()
        scenario_result = make_scenario_result()

        started_at = 1.0
        scenario_result.set_started_at(started_at)
        ended_at = 3.0
        scenario_result.set_ended_at(ended_at)

    with when:
        res = report.add_result(scenario_result)

    with then:
        assert res is None
        assert report.started_at == started_at
        assert report.ended_at == ended_at
        assert isclose(report.elapsed, ended_at - started_at)


def test_elapsed_min_max():
    with given:
        report = Report()

        scenario_result1 = make_scenario_result()
        scenario_result1.set_started_at(1.0)
        scenario_result1.set_ended_at(2.0)
        report.add_result(scenario_result1)

        scenario_result2 = make_scenario_result()
        scenario_result2.set_started_at(3.0)
        scenario_result2.set_ended_at(4.0)

    with when:
        res = report.add_result(scenario_result2)

    with then:
        assert res is None
        assert report.started_at == 1.0
        assert report.ended_at == 4.0
        assert isclose(report.elapsed, 3.0)


def test_eq():
    with given:
        report1 = Report()
        report2 = Report()

    with when:
        res = report1 == report2

    with then:
        assert res is True


def test_eq_with_same_results():
    with given:
        scenario_result1 = make_scenario_result().mark_passed()
        scenario_result2 = make_scenario_result().mark_failed()

        report1 = Report()
        report1.add_result(scenario_result1)
        report1.add_result(scenario_result2)

        report2 = Report()
        report2.add_result(scenario_result1)
        report2.add_result(scenario_result2)

    with when:
        res = report1 == report2

    with then:
        assert res is True


def test_eq_with_diff_results():
    with given:
        scenario_result1 = make_scenario_result().mark_passed()
        scenario_result2 = make_scenario_result().mark_failed()
        scenario_result3 = make_scenario_result().mark_failed()

        report1 = Report()
        report1.add_result(scenario_result1)
        report1.add_result(scenario_result2)

        report2 = Report()
        report2.add_result(scenario_result1)
        report2.add_result(scenario_result3)

    with when:
        res = report1 == report2

    with then:
        assert res is True


def test_summary_default():
    with given:
        report = Report()

    with when:
        res = report.summary

    with then:
        assert res == []


def test_add_summary():
    with given:
        report = Report()

    with when:
        res = report.add_summary("summary")

    with then:
        assert res is None


def test_get_summary():
    with given:
        report = Report()
        summary = "<summary>"
        report.add_summary(summary)

    with when:
        res = report.summary

    with then:
        assert res == [summary]
