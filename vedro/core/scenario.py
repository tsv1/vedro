from enum import Enum


class Scenario:

  class Status(Enum):
    Passed, Failed, Skipped = range(3)

  def __init__(self, path, namespace, fn, scope, subject, steps, tags):
    self.priority = 0
    self.path = path
    self.namespace = namespace
    self.fn = fn
    self.subject = subject
    self.scope = scope
    self.steps = steps
    self.tags = set(map(str.upper, tags))
    self.status = None
    self.exception = None

  @property
  def unique_name(self):
    unique_name = self.subject if (self.namespace == '') else self.namespace + '/' + self.subject
    return unique_name.replace(' ', '_')

  @property
  def passed(self):
    return self.status == self.Status.Passed

  def mark_passed(self):
    self.status = self.Status.Passed

  @property
  def failed(self):
    return self.status == self.Status.Failed

  def mark_failed(self):
    self.status = self.Status.Failed
  
  @property
  def skipped(self):
    return self.status == self.Status.Skipped

  def mark_skipped(self):
    self.status = self.Status.Skipped
