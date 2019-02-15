import json
import os
from traceback import format_exception
from colorama import init, Fore, Style
from ..reporter import Reporter


class DefaultReporter(Reporter):

  def __get_representation(self, obj):
    try:
      representation = json.dumps(obj, ensure_ascii=False, indent=2, default=str)
    except Exception as e:
      return repr(obj)
    return representation

  def __print_dict(self, dictionary):
    for key, value in dictionary.items():
      print(Fore.BLUE + ' {}:'.format(key),
            Fore.RESET + '{}'.format(self.__get_representation(value)))
    print()

  def _on_setup(self, event):
    super()._on_setup(event)
    self._prev_namespace = None
    init(autoreset=True, strip=os.name == 'nt')
    print(Style.BRIGHT + self._target)

  def _on_scenario_run(self, event):
    super()._on_scenario_run(event)
    namespace = event.scenario.namespace
    namespace = namespace.replace('_', ' ').replace('/', ' / ')
    if (namespace is not None) and (namespace != self._prev_namespace):
      self._prev_namespace = namespace
      print(Style.BRIGHT + '* {}'.format(namespace))

  def _on_scenario_fail(self, event):
    super()._on_scenario_fail(event)
    print(Fore.RED + '  ✗ {}'.format(event.scenario.subject))

    if self._verbosity > 0:
      for step in event.scenario.steps:
        if step.failed:
          print(Fore.RED + '    ✗ {}'.format(step.name))
          break
        else:
          print(Fore.RED + '    ✔ {}'.format(step.name))

    if self._verbosity > 1:
      exception = ''.join(format_exception(*event.scenario.exception))
      if event.scenario.errors:
        print(Fore.YELLOW + exception + ' - ' + '\n - '.join(event.scenario.errors) + '\n')
      else:
        print(Fore.YELLOW + exception)

    if self._verbosity > 2 and 'scope' in event.scenario.scope:
      print(Style.BRIGHT + Fore.BLUE + 'Scope:')
      self.__print_dict(event.scenario.scope['scope'])

  def _on_scenario_pass(self, event):
    super()._on_scenario_pass(event)
    print(Fore.GREEN + '  ✔ {}'.format(event.scenario.subject))

  def _on_scenario_skip(self, event):
    super()._on_scenario_skip(event)

  def _on_cleanup(self, event):
    super()._on_cleanup(event)
    style = Style.BRIGHT
    color = Fore.GREEN if (self._failed == 0 and self._passed > 0) else Fore.RED
    print(style + color + '\n# {total} scenario{s}, {failed} failed, {skipped} skipped'.format(
      total=self._total,
      failed=self._failed,
      skipped=self._skipped,
      s='' if (self._total == 1) else 's'
    ))
