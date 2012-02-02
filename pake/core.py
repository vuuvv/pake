"""
Python Makefile System
"""

import pake

class Task(object):
	"""
	A decorator make a function be a sub-command of pake.
	A task function should have 2 argument 'depends' and 'target' at least.
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
		self.func = wraps(func)(helper)
		task_manager.add(func)
		return self.target

	def arg_func(self, target, func, depends, default):
		help = self.help if self.help is not None else target
		parser = loader.subparser.add_parser(target, help=help)
		return func, depends, default

def task(*args, **kwargs):
	return Task(*args, **kwargs)

class TasksNode(object):
	def __init__(self, parent=None):
		self.parent = parent
		self.children = []
		self.tasks = {}

	def add_task(self, task):
		self.tasks[task.target] = task

	def add_child(self, node):
		self.children.append(node)

class TaskManager(object):
	def __init__(self):
		self.node = TaskNode()

task_manager = TaskManager()

class Loader(object):
	pass

