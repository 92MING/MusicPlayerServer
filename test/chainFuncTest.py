from types import FunctionType

class ChainFunc:
    _FinalFuncs = {} # {className: func}
    _BeforeFuncs = {} # {className: {funcName: func}}

    _currentChainFuncs = []
    _currentObj = None
    _counter = 0

    class Chain:
        def __new__(cls, *args, **kwargs):
            obj = super().__new__(cls)
            ChainFunc._counter += 1
            obj.counter = ChainFunc._counter
            return obj
        def __call__(self, *args, **kwargs):
            lastFunc = ChainFunc._currentChainFuncs.pop()
            ChainFunc._currentChainFuncs.append(lambda: lastFunc(ChainFunc._currentObj, *args, **kwargs))
            return self
        def __getattr__(self, item):
            return getattr(ChainFunc._currentObj, item)
        def __del__(self):
            if self.counter == ChainFunc._counter: # end of chain func
                currentClsName = ChainFunc._currentObj.__class__.__qualname__
                if currentClsName in ChainFunc._BeforeFuncs:
                    ChainFunc._BeforeFuncs[currentClsName](ChainFunc._currentObj)
                for func in ChainFunc._currentChainFuncs:
                    func()
                if currentClsName in ChainFunc._FinalFuncs:
                    ChainFunc._FinalFuncs[currentClsName](ChainFunc._currentObj)
                ChainFunc._counter = 0
                ChainFunc._currentChainFuncs = []
                ChainFunc._currentObj = None

    def final(func):
        '''When registrating a function with ChainFunc, the class name and function name must be unique'''
        if not isinstance(func, FunctionType):
            raise Exception('ChainFunc.final can only be used on functions')
        names = func.__qualname__.split('.')
        if len(names) < 2:
            raise Exception('ChainFunc.final can only be used within a class')
        if len(func.__code__.co_varnames) != 1:
            raise Exception('ChainFunc.final can only be used on functions with "self" as the only argument')
        className, funcName = names[-2:]
        if className not in ChainFunc._FinalFuncs:
            ChainFunc._FinalFuncs[className] = func
        else:
            raise Exception('ChainFunc.final can only be used once in a class')
        return func
    def before(func):
        '''When registrating a function with ChainFunc, the class name and function name must be unique'''
        if not isinstance(func, FunctionType):
            raise Exception('ChainFunc.before can only be used on functions')
        names = func.__qualname__.split('.')
        if len(names) < 2:
            raise Exception('ChainFunc.before can only be used within a class')
        if len(func.__code__.co_varnames) != 1:
            raise Exception('ChainFunc.before can only be used on functions with "self" as the only argument')
        className, funcName = names[-2:]
        if className not in ChainFunc._BeforeFuncs:
            ChainFunc._BeforeFuncs[className] = func
        else:
            raise Exception('ChainFunc.before can only be used once in a class')
        return func
    def __new__(cls, func):
        obj= super().__new__(cls)
        names = func.__qualname__.split('.')
        if len(names) < 2:
            raise Exception('ChainFunc can only be used within a class')
        obj.func = func
        return obj
    def __get__(self, instance, owner):
        if instance is None:
            raise Exception('ChainFunc can only be used within the an instance')
        if ChainFunc._currentObj is None:
            ChainFunc._currentObj = instance
        else:
            if instance != ChainFunc._currentObj:
                raise Exception('ChainFunc can only be used within the same object')
        ChainFunc._currentChainFuncs += [self.func]
        return ChainFunc.Chain()

class A:
    @ChainFunc
    def test(self, x):
        print('test',self, x)
    @ChainFunc.final
    def f(self):
        print('final')
    @ChainFunc.before
    def g(self):
        print('before')

a=A()
a.f()