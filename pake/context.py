import os
import copy
import inspect
from imp import new_module
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
		d = self._create_module()
		try:
			execfile(path, d.__dict__)
		except IOError, e:
			raise PakeError('Unable to load configuration file (%s): %s' % (
				e.strerror, os.path.abspath(path)))
		return d

	def _create_module(self):
		parent = self.pakefile.parent
		m = new_module('pakefile')
		if parent is not None:
			module = parent.module
			for name in dir(module):
				if not name.startswith('__'):
					v = getattr(module, name)
					if inspect.ismodule(v) or isinstance(v, Task):
						continue
					setattr(m, name, v)
		if self.pakefile.is_root():
			m.task = task
			m.option = option
			m.cd = app.cd
		return m

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

