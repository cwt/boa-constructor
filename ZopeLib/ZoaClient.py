#from ZopeLib 
import Client

class ZClient:
    def __init__(self, url, user, passwd, timeout=None):
        self.__url = url
        self.__user = user
        self.__passwd = passwd
        self.__timeout = timeout
    def __request(self, methodname, *args, **kwargs):
        msg, res = apply(Client.Function(self.__url+'/'+methodname, 
                username=self.__user, password=self.__passwd, 
                timeout=self.__timeout), args, kwargs)
        return res
    def __getattr__(self, name):
        return _MethodDisp(self.__request, name)

class _MethodDisp:
    def __init__(self, request, name):
        self.__request = request
        self.__name = name
    def __getattr__(self, name):
        return _MethodDisp(self.__request, '%s/%s' % (self.__name, name))
    def __call__(self, *args, **kwargs):
        return apply(self.__request, (self.__name,) + args, kwargs)

if __name__ == '__main__':
    z = ZClient('http://localhost:8080', 'riaan', 'riaan', 10)
    print z.Projects.Boa.title_or_id()