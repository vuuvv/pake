import os
from imp import new_module
from functools import partial

from pake import PakeError
from pake.core import task, task_manager
from pake.local import LocalStack, LocalProxy

def has_pakefile_context():
	return _pakefile_ctx_stack.top is not None

class PakefileContext(object):
	def __init__(self, path):
		self.pakefile = self.load_module(path)
		self.path = path

	def load_module(self, path):
		"""
		Load module the path specified.
		"""
		d = new_module('pakefile')
		d.__file__ = path
		d.task = task
		#d.task_manager = task_manager
		try:
			execfile(path, d.__dict__)
		except IOError, e:
			raise PakeError('Unable to load configuration file (%s): %s' % (
				e.strerror, os.path.abspath(path)))
		return d

	def __enter__(self):
		_pakefile_ctx_stack.push(self)
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

