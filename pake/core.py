"""
Python Makefile System
"""

import pake

class Task(object):
	"""
	A decorator make a function be a sub-command of pake.
	A task function should have 2 argument 'depends' and 'target' at least
	"""
	def __init__(self, depends=[], target=None, default=False, help=None):
		self.target = target
		self.depends = depends
		self.default = default
		self.help = help

	def __call__(self, func):
		if self.target is None:
			self.target = func.__name__

		helper = partial(func, self.depends, self.target)
		_task = wraps(func)(helper)
		tasks.add(self.target, _task, self.depends, 
				self.default, arg_func=self.arg_func)
		return self.target

	def arg_func(self, target, func, depends, default):
		help = self.help if self.help is not None else target
		parser = loader.subparser.add_parser(target, help=help)
		return func, depends, default

def task(*args, **kwargs):
	return Task(*args, **kwargs)

class TaskManager(object):
	def __init__(self):
		self.lookup = {}

task_manager = TaskManager()

class Loader(object):
	pass

