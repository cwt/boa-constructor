class propertyRedirector:
    """ Class that implements properties or getter/setter attributes.

         Attributes starting with '_' can be accessed by declaring
         getter and setter functions for it.
         e.g. for attr _test:

         def get_test(self):
             return self._test

         def set_test(self, val):
             self._test = val

    """

    getter = 'get'
    setter = 'set'

    def __getattr__(self, attr):
        priv_attr = '_'+attr
        if self.__class__.__dict__.has_key(self.getter+priv_attr):
            return self.__class__.__dict__[self.getter+priv_attr](self)
        elif self.__dict__.has_key(priv_attr):
            return self.__dict__[priv_attr]
        elif attr == '':
            return self
        else:
            raise AttributeError, attr

    def __setattr__(self, attr, val):
        priv_attr = '_'+attr
        if self.__class__.__dict__.has_key(self.setter+priv_attr):
            self.__class__.__dict__[self.setter+priv_attr](self, val)
        elif self.__dict__.has_key(priv_attr):
            self.__dict__[priv_attr] = val
        else:
            self.__dict__[attr] = val

class propTst(propertyRedirector):
    def __init__(self):
        self._size = 10
    def get_size(self):
        return self._size
    def set_size(self, val):
        self._size = val

class simplePropTst(propertyRedirector):
    def __init__(self):
        self._size = 10
    def __repr__(self):
        return '<simple prop obj>'

def test():
    p1 = propTst()
    print p1.size
    p1.size = p1.size + 10
    print p1.size

    p2 = simplePropTst()
    print p2.size
    p2.size = p2.size + 10
    print p2.size

test()
