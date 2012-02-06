import os
import sys
import imp
import copy
import inspect
from functools import partial

from pake import PakeError
from pake.core import task, option, Task, PakefileNode
from pake.local import LocalStack, LocalProxy

def has_pakefile_context():
	return _pakefile_ctx_stack.top is not None

class PakefileContext(object):
	def __init__(self, app, path, parent=None):
		self.pakefile = PakefileNode(path, parent)
		self.app = app

	def _load_module(self, path):
		"""
		Load module the path specified.
		"""
		# for native context
		if self.pakefile.parent is None:
			m = __import__("pake.builtins")
			# the m is not the pake.builtins module, so get it from sys.modules
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
		parent = self.pakefile.parent
		if parent is not None:
			p = parent.module
			for name in dir(p):
				if not name.startswith('__'):
					v = getattr(p, name)
					if inspect.ismodule(v) or isinstance(v, Task):
						continue
					setattr(module, name, v)
		return module

	def __enter__(self):
		_pakefile_ctx_stack.push(self)
		self.pakefile.module = self._load_module(self.pakefile.path)
		return self

	def __exit__(self, exc_type, exc_value, tb):
		_pakefile_ctx_stack.pop()

	def __repr__(self):
		return '<%s of %s>' % (self.__class__.__name__, self.path)

def _lookup_object(name):
	top = _pakefile_ctx_stack.top
	if top is None:
		raise RuntimeError('working outside of request context')
	return getattr(top, name)

_pakefile_ctx_stack = LocalStack()
pakefile = LocalProxy(partial(_lookup_object, 'pakefile'))
app = LocalProxy(partial(_lookup_object, 'app'))

