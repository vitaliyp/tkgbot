'''
    Represent dic as object.
    Implementation stolen from https://goodcode.io/articles/python-dict-object/
'''
class objectview(object):
    def __init__(self, d):
        self.__dict__ = d