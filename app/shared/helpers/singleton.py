class Singleton(type):
    def __init__(cls, name, bases, mmbs):
        super().__init__(name, bases, mmbs)
        cls._instance = super(Singleton, cls).__call__()

    def __call__(cls, *args, **kwargs):
        return cls._instance
