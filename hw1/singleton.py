# through class field and saving it there one time
class Singleton1:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

instance1 = Singleton1()
instance2 = Singleton1()
print(instance1 is instance2)

# though Singleton metaclass that makes any child singleton
class Singleton2(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton2, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class SomeClass1(metaclass=Singleton2):
    pass

instance1 = SomeClass1()
instance2 = SomeClass1()
print(instance1 is instance2)

# decorator that wraps class and returns function that creates+returns class instances
def Singleton3(cls):
    instance = None

    def get_instance(*args, **kwargs):
        nonlocal instance
        if instance is None:
            instance = cls(*args, **kwargs)
        return instance

    return get_instance

@Singleton3
class SomeClass2:
    pass

instance1 = SomeClass2()
instance2 = SomeClass2()
print(instance1 is instance2)

'''
First and second approaches are pretty similar
Second has a plus that it allows to make any class singleton without modifying its code, only adding inheritance from metaclass

Yet both first and second have a problem of having field with instance available from outside
If it is modified appropriately, calling class instance creating will make a new instance

Third approach of decorator is better in this regard
It creates inner function variable for storing value and so can't be accessed from outside
'''
