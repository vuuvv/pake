import os
from imp import new_module
from functools import partial

from pake import PakeError
from pake.core import task, option, PakefileNode
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
		d = new_module('pakefile')
		d.__file__ = path
		d.task = task
		d.option = option
		d.cd = app.cd
		#d.task_manager = task_manager
		try:
			execfile(path, d.__dict__)
		except IOError, e:
			raise PakeError('Unable to load configuration file (%s): %s' % (
				e.strerror, os.path.abspath(path)))
		return d

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

