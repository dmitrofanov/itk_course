import datetime

class CreatedAtMeta(type):
	# def __new__(cls, name, bases, dict):
	# 	dict['created_at'] = datetime.datetime.now()
	# 	return super().__new__(cls, name, bases, dict)
	def __call__(cls, *args, **kwargs):
		instance = super().__call__(*args, **kwargs)
		instance.created_at = datetime.datetime.now()
		return instance

class A(metaclass=CreatedAtMeta):
	pass


a1 = A()
a2 = A()

print(A().created_at)
print(a1.created_at)
print(a2.created_at)