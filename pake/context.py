import os
import sys
import imp
import copy
import inspect
from functools import partial

from pake.exceptions import PakeError
from pake.core import Task
from pake.globals import _pakefile_ctx_stack, app, context_stack
from pake.invoke_chain import EmptyChain, InvokeChain

class PakefileContext(object):
	def __init__(self, app, path=None):
		self.app = app
		self.tasks = {}
		self.module = None
		self.default = None
		self.path = path

	def find_task(self, name):
		for ctx in reversed(context_stack):
			t = ctx.tasks.get(name, None)
			if t is not None:
				return t
		raise PakeError("Can't find target '%s'" % name)

	def add_task(self, task):
		self.tasks[task.target] = task
		if task.default:
			self.default = task.target

	def run_task(self, target):
		t = self.find_task(target)
		chain = InvokeChain(t)
		self._run_prerequisite(t, chain)
		t.execute(app.argv)

	def _invoke_task(self, target, invoke_chain):
		t = self.find_task(target)
		if not t.invoked:
			chain = invoke_chain.append(t)
			self._run_prerequisite(t, chain)
			t.execute()

	def _run_prerequisite(self, t, invoke_chain):
		for pre in t.prerequisites:
			self._invoke_task(pre, invoke_chain)

	def is_native(self):
		return context_stack.index(self) == 0

	def is_root(self):
		return context_stack.index(self) == 1

	def _load_module(self, path):
		"""
		Load module the path specified.
		"""
		# for native context
		if self.is_native():
			m = __import__("pake.builtins")
			# the m is not the pake.builtins module,(why), so get it from sys.modules
			return sys.modules['pake.builtins']

		module = imp.new_module('pakefile')
		self._init_module(module)
		try:
			execfile(path, module.__dict__)
		except IOError, e:
			raise PakeError('Unable to load configuration file (%s): %s' % (
				e.strerror, os.path.abspath(path)))
		return module

	def _init_module(self, module):
		for ctx in reversed(context_stack[:-1]):
			m = ctx.module
			for name in dir(m):
				if not name.startswith('__'):
					v = getattr(m, name)
					if inspect.ismodule(v) or isinstance(v, Task):
						continue
					setattr(module, name, v)

		return module

	def __enter__(self):
		_pakefile_ctx_stack.push(self)
		self.module = self._load_module(self.path)
		return self

	def __exit__(self, exc_type, exc_value, tb):
		_pakefile_ctx_stack.pop()

	def __repr__(self):
		return '<%s of %s>' % (self.__class__.__name__, self.path)

