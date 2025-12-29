import unittest.mock
from collections import OrderedDict
from functools import wraps


def lru_cache_v1(*args, **kwargs):
	maxsize = kwargs.get('maxsize', None)
	cache = {}
	seen = {}
	counter = 0

	def get_key(xargs, xkwargs):
		return (xargs, tuple(xkwargs.items()))

	def deco(func):
		@wraps(func)
		def wrapper(*fun_args, **fun_kwargs):
			nonlocal counter
			key = get_key(fun_args, fun_kwargs)
			if maxsize:
				seen[key] = counter
				counter += 1
			if key in cache:
				return cache[key]
			value = func(*fun_args, **fun_kwargs)
			cache[key] = value
			if maxsize and len(seen) > maxsize:
				to_remove = min(seen.items(), key=lambda x: x[1])
				del cache[to_remove[0]]
			return value

		return wrapper

	if len(args) == 1 and callable(args[0]):
		return deco(args[0])
	else:
		return deco

def lru_cache_v2(*args, **kwargs):
	maxsize = kwargs.get('maxsize', None)
	cache = OrderedDict()

	def get_key(xargs, xkwargs):
		return (xargs, tuple(xkwargs.items()))

	def put(key, value):
		if key in cache:
			cache.pop(key)
		cache[key] = value

		if maxsize and len(cache) > maxsize:
			cache.popitem(last=False)

	def get(key):
		if key not in cache:
			return None
		val = cache.pop(key)
		cache[key] = val
		return val

	def deco(func):
		@wraps(func)
		def wrapper(*fun_args, **fun_kwargs):
			key = get_key(fun_args, fun_kwargs)

			val = get(key)
			if val is None:
				val = func(*fun_args, **fun_kwargs)
				put(key, val)
			return val
		return wrapper

	if len(args) == 1 and callable(args[0]):
		return deco(args[0])
	else:
		return deco




lru_cache = lru_cache_v2

@lru_cache
def sum(a: int, b: int) -> int:
    return a + b


@lru_cache
def sum_many(a: int, b: int, *, c: int, d: int) -> int:
    return a + b + c + d


@lru_cache(maxsize=3)
def multiply(a: int, b: int) -> int:
    return a * b


if __name__ == '__main__':
    
    assert sum(1, 2) == 3
    assert sum(3, 4) == 7

    assert multiply(1, 2) == 2
    assert multiply(3, 4) == 12

    assert sum_many(1, 2, c=3, d=4) == 10

    mocked_func = unittest.mock.Mock()
    mocked_func.side_effect = [1, 2, 3, 4]

    decorated = lru_cache(maxsize=2)(mocked_func)
    assert decorated(1, 2) == 1
    assert decorated(1, 2) == 1
    assert decorated(3, 4) == 2
    assert decorated(3, 4) == 2
    assert decorated(5, 6) == 3
    assert decorated(5, 6) == 3
    assert decorated(1, 2) == 4
    assert mocked_func.call_count == 4
